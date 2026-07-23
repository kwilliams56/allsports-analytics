"""Unit tests for the external sports API reliability boundary."""

from unittest.mock import Mock

import pytest
import requests

from app.services.base_client import SportsAPIClient
from app.services.cache import MemoryTTLCache
from app.services.exceptions import (
    SportsAPIAuthenticationError,
    SportsAPIConfigurationError,
    SportsAPIConnectionError,
    SportsAPIMalformedResponseError,
    SportsAPIRateLimitError,
    SportsAPIResponseError,
    SportsAPITimeoutError,
    SportsAPIValidationError,
)


def response(status: int = 200, payload=None, headers=None) -> Mock:
    result = Mock(spec=requests.Response)
    result.status_code = status
    result.headers = headers or {}
    result.json.return_value = {"data": []} if payload is None else payload
    return result


def client(session=None, sleep=None, **overrides) -> SportsAPIClient:
    settings = {
        "api_key": "test-key",
        "base_url": "https://api.example.test",
        "timeout_seconds": 4,
        "max_retries": 2,
        "backoff_seconds": 0.25,
        "cache_ttl_seconds": 60,
        "session": session or Mock(spec=requests.Session),
        "sleep": sleep or Mock(),
    }
    settings.update(overrides)
    return SportsAPIClient(**settings)


def test_success_uses_documented_auth_header_timeout_and_validation():
    session = Mock(spec=requests.Session)
    session.request.return_value = response(payload={"data": [{"id": 1}]})
    api = client(session=session)

    payload = api.get_json("league/v1/resources", required_fields=("data",))

    assert payload["data"][0]["id"] == 1
    session.request.assert_called_once_with(
        "GET",
        "https://api.example.test/league/v1/resources",
        params=None,
        headers={"Authorization": "test-key", "Accept": "application/json"},
        timeout=4,
    )


def test_cache_prevents_an_immediate_duplicate_request():
    session = Mock(spec=requests.Session)
    session.request.return_value = response(payload={"data": [1]})
    api = client(session=session)

    first = api.get_json("league/v1/resources", params={"page": 1})
    second = api.get_json("league/v1/resources", params={"page": 1})

    assert first == second
    session.request.assert_called_once()


def test_shared_cache_is_partitioned_by_credential_without_storing_raw_key():
    cache = MemoryTTLCache()
    first_session = Mock(spec=requests.Session)
    second_session = Mock(spec=requests.Session)
    first_session.request.return_value = response(payload={"data": [1]})
    second_session.request.return_value = response(payload={"data": [2]})
    first = client(session=first_session, cache=cache, api_key="first-test-key")
    second = client(session=second_session, cache=cache, api_key="second-test-key")

    assert first.get_json("league/v1/resources") == {"data": [1]}
    assert second.get_json("league/v1/resources") == {"data": [2]}
    assert not hasattr(first, "api_key")
    assert all("first-test-key" not in key for key in cache._entries)
    assert all("second-test-key" not in key for key in cache._entries)
    first_session.request.assert_called_once()
    second_session.request.assert_called_once()


def test_retries_server_error_with_exponential_backoff():
    session = Mock(spec=requests.Session)
    session.request.side_effect = [
        response(status=503),
        response(status=500),
        response(payload={"data": []}),
    ]
    sleep = Mock()

    client(session=session, sleep=sleep).get_json("league/v1/resources")

    assert session.request.call_count == 3
    assert [call.args[0] for call in sleep.call_args_list] == [0.25, 0.5]


def test_every_5xx_status_is_treated_as_temporary():
    session = Mock(spec=requests.Session)
    session.request.side_effect = [
        response(status=501),
        response(payload={"data": []}),
    ]

    client(session=session, max_retries=1).get_json("league/v1/resources")

    assert session.request.call_count == 2


def test_rate_limit_respects_retry_after_then_raises():
    session = Mock(spec=requests.Session)
    session.request.return_value = response(
        status=429, headers={"Retry-After": "2"}
    )
    sleep = Mock()

    with pytest.raises(SportsAPIRateLimitError) as error:
        client(session=session, sleep=sleep, max_retries=1).get_json(
            "league/v1/resources"
        )

    sleep.assert_called_once_with(2.0)
    assert error.value.retry_after == 2.0


@pytest.mark.parametrize("status", [401, 403])
def test_unauthorized_response_is_not_retried_or_cached(status):
    session = Mock(spec=requests.Session)
    session.request.return_value = response(status=status)

    api = client(session=session)
    for _ in range(2):
        with pytest.raises(SportsAPIAuthenticationError):
            api.get_json("league/v1/resources")

    assert session.request.call_count == 2


def test_exhausted_server_error_preserves_status():
    session = Mock(spec=requests.Session)
    session.request.return_value = response(status=503)

    with pytest.raises(SportsAPIResponseError) as error:
        client(session=session, max_retries=1).get_json("league/v1/resources")

    assert error.value.status_code == 503
    assert session.request.call_count == 2


@pytest.mark.parametrize(
    ("failure", "expected"),
    [
        (requests.Timeout("slow"), SportsAPITimeoutError),
        (requests.ConnectionError("offline"), SportsAPIConnectionError),
    ],
)
def test_network_failures_are_retried_and_translated(failure, expected):
    session = Mock(spec=requests.Session)
    session.request.side_effect = failure

    with pytest.raises(expected):
        client(session=session, max_retries=1).get_json("league/v1/resources")

    assert session.request.call_count == 2


def test_malformed_json_is_rejected():
    session = Mock(spec=requests.Session)
    bad_response = response()
    bad_response.json.side_effect = ValueError("invalid json")
    session.request.return_value = bad_response

    with pytest.raises(SportsAPIMalformedResponseError):
        client(session=session).get_json("league/v1/resources")


def test_non_object_json_is_rejected():
    session = Mock(spec=requests.Session)
    session.request.return_value = response(payload=[])

    with pytest.raises(SportsAPIMalformedResponseError):
        client(session=session).get_json("league/v1/resources")


def test_missing_required_field_is_rejected():
    session = Mock(spec=requests.Session)
    session.request.return_value = response(payload={"meta": {}})

    with pytest.raises(SportsAPIValidationError, match="data"):
        client(session=session).get_json(
            "league/v1/resources", required_fields=("data",)
        )


def test_endpoint_validator_failures_are_translated():
    session = Mock(spec=requests.Session)
    session.request.return_value = response(payload={"data": "wrong"})

    def validate(payload):
        if not isinstance(payload["data"], list):
            raise TypeError("data must be a list")

    with pytest.raises(SportsAPIValidationError):
        client(session=session).get_json(
            "league/v1/resources", validator=validate
        )


def test_non_retryable_http_error_preserves_status():
    session = Mock(spec=requests.Session)
    session.request.return_value = response(status=400)

    with pytest.raises(SportsAPIResponseError) as error:
        client(session=session).get_json("league/v1/resources")

    assert error.value.status_code == 400
    session.request.assert_called_once()


def test_missing_key_and_absolute_endpoint_are_rejected():
    with pytest.raises(SportsAPIConfigurationError):
        client(api_key=" ")

    with pytest.raises(SportsAPIConfigurationError):
        client().get_json("https://untrusted.example/resources")

    with pytest.raises(SportsAPIConfigurationError, match="HTTPS"):
        client(base_url="http://api.example.test")

    with pytest.raises(SportsAPIConfigurationError, match="credential-free"):
        client(base_url="https://username:password@api.example.test")

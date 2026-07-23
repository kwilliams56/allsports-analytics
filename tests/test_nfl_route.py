"""NFL page behavior with injected, mocked services."""

from unittest.mock import Mock

import pytest

from app import create_app
from app.services.exceptions import (
    SportsAPIAuthenticationError,
    SportsAPIConnectionError,
    SportsAPIMalformedResponseError,
    SportsAPIRateLimitError,
    SportsAPIResponseError,
    SportsAPITimeoutError,
)
from app.services.nfl_teams import NFLTeam, NFLTeamsService
from config import TestingConfig


class MissingKeyConfig(TestingConfig):
    SPORTS_API_KEY = None


def test_nfl_page_renders_normalized_team_cards():
    app = create_app(TestingConfig)
    service = Mock(spec=NFLTeamsService)
    service.get_teams.return_value = (
        NFLTeam("Ravens", "Baltimore", "AFC", "NORTH", "BAL"),
    )
    app.extensions["nfl_teams_service"] = service

    response = app.test_client().get("/nfl/")

    assert response.status_code == 200
    assert b"Baltimore" in response.data
    assert b"Ravens" in response.data
    assert b"AFC NORTH" in response.data
    assert b"BAL" in response.data
    service.get_teams.assert_called_once_with()


def test_nfl_page_handles_empty_provider_response():
    app = create_app(TestingConfig)
    service = Mock(spec=NFLTeamsService)
    service.get_teams.return_value = ()
    app.extensions["nfl_teams_service"] = service

    response = app.test_client().get("/nfl/")

    assert response.status_code == 200
    assert b"No teams found" in response.data


def test_nfl_page_handles_missing_api_key_without_requesting_data():
    app = create_app(MissingKeyConfig)

    response = app.test_client().get("/nfl/")

    assert response.status_code == 200
    assert b"Team data unavailable" in response.data
    assert b"not configured" in response.data


@pytest.mark.parametrize(
    ("failure", "expected_text"),
    [
        (
            SportsAPIAuthenticationError("unauthorized"),
            b"provider access could not be verified",
        ),
        (
            SportsAPIRateLimitError("rate limited"),
            b"receiving heavy traffic",
        ),
        (SportsAPITimeoutError("timeout"), b"not responding right now"),
        (SportsAPIConnectionError("offline"), b"not responding right now"),
        (
            SportsAPIMalformedResponseError("bad json"),
            b"could not load reliable NFL team data",
        ),
        (
            SportsAPIResponseError("not found", status_code=404),
            b"could not load reliable NFL team data",
        ),
        (
            SportsAPIResponseError("server error", status_code=503),
            b"could not load reliable NFL team data",
        ),
    ],
)
def test_nfl_page_renders_safe_provider_error_states(failure, expected_text):
    app = create_app(TestingConfig)
    service = Mock(spec=NFLTeamsService)
    service.get_teams.side_effect = failure
    app.extensions["nfl_teams_service"] = service

    response = app.test_client().get("/nfl/")

    assert response.status_code == 200
    assert expected_text in response.data
    assert str(failure).encode() not in response.data

"""Reliable, provider-agnostic HTTP client for documented sports APIs."""

import hashlib
import json
import logging
import time
from collections.abc import Callable, Iterable, Mapping
from typing import Any
from urllib.parse import urlparse

import requests

from app.services.cache import Cache, MemoryTTLCache
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

ResponseValidator = Callable[[Mapping[str, Any]], None]


class SportsAPIClient:
    """Perform authenticated JSON requests with retries, validation, and caching."""

    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str,
        timeout_seconds: float = 5.0,
        max_retries: int = 3,
        backoff_seconds: float = 0.5,
        cache_ttl_seconds: int = 300,
        cache: Cache | None = None,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
        logger: logging.Logger | None = None,
    ) -> None:
        self._api_key = self._validate_api_key(api_key)
        self._cache_namespace = hashlib.sha256(self._api_key.encode()).hexdigest()[:16]
        self.base_url = self._validate_base_url(base_url)
        if timeout_seconds <= 0:
            raise SportsAPIConfigurationError("API timeout must be greater than zero.")
        if max_retries < 0 or backoff_seconds < 0 or cache_ttl_seconds < 0:
            raise SportsAPIConfigurationError(
                "Retry, backoff, and cache settings cannot be negative."
            )

        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.cache_ttl_seconds = cache_ttl_seconds
        self.cache = cache or MemoryTTLCache()
        self.session = session or requests.Session()
        self.sleep = sleep
        self.logger = logger or logging.getLogger(__name__)

    @classmethod
    def from_config(
        cls, config: Mapping[str, Any], **overrides: Any
    ) -> "SportsAPIClient":
        """Build a client from Flask's mapping-like application config."""
        settings = {
            "api_key": config.get("SPORTS_API_KEY"),
            "base_url": config.get("SPORTS_API_BASE_URL", ""),
            "timeout_seconds": config.get("SPORTS_API_TIMEOUT_SECONDS", 5.0),
            "max_retries": config.get("SPORTS_API_MAX_RETRIES", 3),
            "backoff_seconds": config.get("SPORTS_API_BACKOFF_SECONDS", 0.5),
            "cache_ttl_seconds": config.get("SPORTS_API_CACHE_TTL_SECONDS", 300),
        }
        settings.update(overrides)
        return cls(**settings)

    def get_json(
        self,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
        required_fields: Iterable[str] = (),
        validator: ResponseValidator | None = None,
        use_cache: bool = True,
    ) -> Mapping[str, Any]:
        """Fetch and validate a JSON object from a relative provider endpoint."""
        url = self._build_url(endpoint)
        cache_key = self._cache_key(endpoint, params)

        if use_cache and self.cache_ttl_seconds > 0:
            cached = self.cache.get(cache_key)
            if cached is not None:
                self._log(logging.DEBUG, "sports_api_cache_hit", endpoint=endpoint)
                return cached

        payload = self._request_json(url, endpoint=endpoint, params=params)
        self._validate_response(payload, required_fields, validator)

        if use_cache:
            self.cache.set(cache_key, payload, self.cache_ttl_seconds)
        return payload

    def _request_json(
        self,
        url: str,
        *,
        endpoint: str,
        params: Mapping[str, Any] | None,
    ) -> Mapping[str, Any]:
        attempts = self.max_retries + 1
        for attempt in range(attempts):
            try:
                response = self.session.request(
                    "GET",
                    url,
                    params=params,
                    headers={
                        "Authorization": self._api_key,
                        "Accept": "application/json",
                    },
                    timeout=self.timeout_seconds,
                )
            except requests.Timeout as exc:
                if attempt < self.max_retries:
                    self._retry("timeout", endpoint, attempt)
                    continue
                self._log(logging.ERROR, "sports_api_timeout", endpoint=endpoint)
                raise SportsAPITimeoutError(
                    "The sports-data provider timed out."
                ) from exc
            except requests.ConnectionError as exc:
                if attempt < self.max_retries:
                    self._retry("connection_error", endpoint, attempt)
                    continue
                self._log(
                    logging.ERROR, "sports_api_connection_failed", endpoint=endpoint
                )
                raise SportsAPIConnectionError(
                    "Could not connect to the sports-data provider."
                ) from exc
            except requests.RequestException as exc:
                self._log(logging.ERROR, "sports_api_request_failed", endpoint=endpoint)
                raise SportsAPIConnectionError(
                    "The sports-data request could not be completed."
                ) from exc

            status = response.status_code
            if status in {401, 403}:
                self._log(
                    logging.WARNING,
                    "sports_api_access_denied",
                    endpoint=endpoint,
                    status_code=status,
                )
                raise SportsAPIAuthenticationError(
                    "The API key is invalid or the account cannot access this resource."
                )

            if status == 429 or 500 <= status < 600:
                retry_after = self._retry_after(response)
                if attempt < self.max_retries:
                    self._retry(
                        "rate_limited" if status == 429 else "server_error",
                        endpoint,
                        attempt,
                        status_code=status,
                        retry_after=retry_after,
                    )
                    continue
                if status == 429:
                    self._log(
                        logging.WARNING,
                        "sports_api_rate_limit_exhausted",
                        endpoint=endpoint,
                        status_code=status,
                        retry_after=retry_after,
                    )
                    raise SportsAPIRateLimitError(
                        "The sports-data provider rate limit was exceeded.",
                        retry_after=retry_after,
                    )
                self._log(
                    logging.ERROR,
                    "sports_api_server_error_exhausted",
                    endpoint=endpoint,
                    status_code=status,
                )
                raise SportsAPIResponseError(
                    "The sports-data provider is temporarily unavailable.",
                    status_code=status,
                )

            if not 200 <= status < 300:
                self._log(
                    logging.WARNING,
                    "sports_api_http_error",
                    endpoint=endpoint,
                    status_code=status,
                )
                raise SportsAPIResponseError(
                    f"The sports-data provider returned HTTP {status}.",
                    status_code=status,
                )

            try:
                payload = response.json()
            except ValueError as exc:
                self._log(
                    logging.ERROR,
                    "sports_api_malformed_json",
                    endpoint=endpoint,
                    status_code=status,
                )
                raise SportsAPIMalformedResponseError(
                    "The sports-data provider returned malformed JSON."
                ) from exc
            if not isinstance(payload, Mapping):
                self._log(
                    logging.ERROR,
                    "sports_api_invalid_json_shape",
                    endpoint=endpoint,
                    status_code=status,
                )
                raise SportsAPIMalformedResponseError(
                    "The sports-data provider response must be a JSON object."
                )

            self._log(
                logging.INFO,
                "sports_api_request_succeeded",
                endpoint=endpoint,
                status_code=status,
                attempt=attempt + 1,
            )
            return payload

        raise AssertionError("Request loop exited unexpectedly.")

    def _retry(
        self,
        reason: str,
        endpoint: str,
        attempt: int,
        *,
        status_code: int | None = None,
        retry_after: float | None = None,
    ) -> None:
        exponential_delay = self.backoff_seconds * (2**attempt)
        delay = retry_after if retry_after is not None else exponential_delay
        delay = min(max(delay, exponential_delay), 30.0)
        self._log(
            logging.WARNING,
            "sports_api_retry_scheduled",
            endpoint=endpoint,
            reason=reason,
            status_code=status_code,
            retry_number=attempt + 1,
            delay_seconds=delay,
        )
        self.sleep(delay)

    @staticmethod
    def _validate_response(
        payload: Mapping[str, Any],
        required_fields: Iterable[str],
        validator: ResponseValidator | None,
    ) -> None:
        missing = [field for field in required_fields if field not in payload]
        if missing:
            fields = ", ".join(sorted(missing))
            raise SportsAPIValidationError(
                f"Sports-data response is missing required fields: {fields}."
            )
        if validator is not None:
            try:
                validator(payload)
            except SportsAPIValidationError:
                raise
            except (KeyError, TypeError, ValueError) as exc:
                raise SportsAPIValidationError(
                    "Sports-data response failed schema validation."
                ) from exc

    @staticmethod
    def _validate_api_key(api_key: str | None) -> str:
        if not api_key or not api_key.strip():
            raise SportsAPIConfigurationError(
                "BALLDONTLIE_API_KEY is required to call the sports-data provider."
            )
        return api_key.strip()

    @staticmethod
    def _validate_base_url(base_url: str) -> str:
        parsed = urlparse(base_url)
        if (
            parsed.scheme != "https"
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise SportsAPIConfigurationError(
                "SPORTS_API_BASE_URL must be a credential-free absolute HTTPS URL."
            )
        return base_url.rstrip("/")

    def _build_url(self, endpoint: str) -> str:
        parsed = urlparse(endpoint)
        if parsed.scheme or parsed.netloc or not endpoint.strip():
            raise SportsAPIConfigurationError(
                "Sports API endpoints must be non-empty relative paths."
            )
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def _cache_key(self, endpoint: str, params: Mapping[str, Any] | None) -> str:
        encoded = json.dumps(params or {}, sort_keys=True, separators=(",", ":"), default=str)
        return (
            f"sports-api:{self.base_url}:{self._cache_namespace}:"
            f"{endpoint.lstrip('/')}:{encoded}"
        )

    @staticmethod
    def _retry_after(response: requests.Response) -> float | None:
        value = response.headers.get("Retry-After")
        if value is None:
            return None
        try:
            return max(float(value), 0.0)
        except ValueError:
            return None

    def _log(self, level: int, event: str, **fields: Any) -> None:
        self.logger.log(level, event, extra={"event": event, **fields})

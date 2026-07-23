"""Service-layer exceptions safe for routes and business logic to handle."""


class SportsAPIError(Exception):
    """Base class for all external sports API failures."""


class SportsAPIConfigurationError(SportsAPIError):
    """The API client is missing or has invalid configuration."""


class SportsAPIConnectionError(SportsAPIError):
    """A connection to the provider could not be established."""


class SportsAPITimeoutError(SportsAPIError):
    """The provider did not respond within the configured timeout."""


class SportsAPIAuthenticationError(SportsAPIError):
    """The API key is invalid or the account cannot access the resource."""


class SportsAPIRateLimitError(SportsAPIError):
    """The provider rate limit remained active after retries."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class SportsAPIResponseError(SportsAPIError):
    """The provider returned an unexpected HTTP response."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class SportsAPIMalformedResponseError(SportsAPIError):
    """The provider response was not a valid JSON object."""


class SportsAPIValidationError(SportsAPIError):
    """The provider response omitted required fields or used invalid types."""

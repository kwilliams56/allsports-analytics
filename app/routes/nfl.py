"""NFL presentation routes; provider access remains in the service layer."""

from flask import Blueprint, current_app, render_template

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

nfl_bp = Blueprint("nfl", __name__, url_prefix="/nfl")


@nfl_bp.get("/")
def index():
    """Render normalized NFL teams or a safe, user-friendly error state."""
    teams = ()
    error_message = None
    service = current_app.extensions.get("nfl_teams_service")

    try:
        if service is None:
            raise SportsAPIConfigurationError("NFL data service is not configured.")
        teams = service.get_teams()
    except SportsAPIConfigurationError as exc:
        error_message = (
            "NFL team data is not configured yet. Please try again after setup is complete."
        )
        _log_service_error(exc)
    except SportsAPIAuthenticationError as exc:
        error_message = (
            "NFL team data is temporarily unavailable because provider access could not "
            "be verified."
        )
        _log_service_error(exc)
    except SportsAPIRateLimitError as exc:
        error_message = (
            "NFL team data is receiving heavy traffic. Please try again in a moment."
        )
        _log_service_error(exc)
    except (SportsAPITimeoutError, SportsAPIConnectionError) as exc:
        error_message = (
            "The NFL data service is not responding right now. Please try again shortly."
        )
        _log_service_error(exc)
    except (
        SportsAPIMalformedResponseError,
        SportsAPIValidationError,
        SportsAPIResponseError,
    ) as exc:
        error_message = (
            "We could not load reliable NFL team data right now. Please try again later."
        )
        _log_service_error(exc)

    return render_template("nfl.html", teams=teams, error_message=error_message)


def _log_service_error(error: Exception) -> None:
    """Log safe failure metadata without credentials or response content."""
    fields = {
        "event": "nfl_teams_load_failed",
        "error_type": type(error).__name__,
    }
    status_code = getattr(error, "status_code", None)
    if status_code is not None:
        fields["status_code"] = status_code
    current_app.logger.warning("nfl_teams_load_failed", extra=fields)

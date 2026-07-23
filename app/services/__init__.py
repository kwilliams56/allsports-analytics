"""Public service-layer interfaces for external sports data."""

from flask import Flask

from app.services.base_client import SportsAPIClient
from app.services.cache import Cache, MemoryTTLCache
from app.services.exceptions import SportsAPIError
from app.services.nfl_teams import NFLAPIHealth, NFLTeam, NFLTeamsService


def init_services(app: Flask) -> None:
    """Create configured service objects without making network requests."""
    if not app.config.get("SPORTS_API_KEY"):
        app.extensions["nfl_teams_service"] = None
        return

    client = SportsAPIClient.from_config(app.config, logger=app.logger)
    app.extensions["nfl_teams_service"] = NFLTeamsService(client)


__all__ = [
    "Cache",
    "MemoryTTLCache",
    "NFLAPIHealth",
    "NFLTeam",
    "NFLTeamsService",
    "SportsAPIClient",
    "SportsAPIError",
    "init_services",
]

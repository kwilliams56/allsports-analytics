"""NFL team data normalized from the documented BALLDONTLIE endpoint."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from app.services.base_client import SportsAPIClient
from app.services.exceptions import SportsAPIValidationError


@dataclass(frozen=True, slots=True)
class NFLTeam:
    """Presentation-safe NFL team fields documented by BALLDONTLIE."""

    name: str
    location: str
    conference: str
    division: str
    abbreviation: str


@dataclass(frozen=True, slots=True)
class NFLAPIHealth:
    """Result of checking the documented free teams resource."""

    available: bool
    team_count: int


class NFLTeamsService:
    """Provide normalized NFL team data without leaking provider responses."""

    TEAMS_ENDPOINT = "nfl/v1/teams"
    TEAM_FIELDS = ("name", "location", "conference", "division", "abbreviation")

    def __init__(self, client: SportsAPIClient) -> None:
        self.client = client

    def get_teams(self) -> tuple[NFLTeam, ...]:
        """Return all documented NFL teams, cached by the base client."""
        payload = self.client.get_json(
            self.TEAMS_ENDPOINT,
            required_fields=("data",),
            validator=self._validate_teams_response,
            use_cache=True,
        )
        teams = tuple(self._normalize_team(item) for item in payload["data"])
        return tuple(
            sorted(
                teams,
                key=lambda team: (
                    team.conference,
                    team.division,
                    team.location,
                    team.name,
                ),
            )
        )

    def health_check(self) -> NFLAPIHealth:
        """Check API availability through the documented cached teams request."""
        teams = self.get_teams()
        return NFLAPIHealth(available=True, team_count=len(teams))

    @classmethod
    def _validate_teams_response(cls, payload: Mapping[str, Any]) -> None:
        data = payload["data"]
        if not isinstance(data, list):
            raise SportsAPIValidationError("NFL teams data must be a list.")
        for index, item in enumerate(data):
            if not isinstance(item, Mapping):
                raise SportsAPIValidationError(
                    f"NFL team at index {index} must be an object."
                )
            missing = [field for field in cls.TEAM_FIELDS if field not in item]
            if missing:
                raise SportsAPIValidationError(
                    "NFL team response is missing documented fields: "
                    + ", ".join(sorted(missing))
                    + "."
                )
            invalid = [field for field in cls.TEAM_FIELDS if not isinstance(item[field], str)]
            if invalid:
                raise SportsAPIValidationError(
                    "NFL team response contains invalid fields: "
                    + ", ".join(sorted(invalid))
                    + "."
                )

    @classmethod
    def _normalize_team(cls, item: Mapping[str, Any]) -> NFLTeam:
        values = {field: item[field].strip() for field in cls.TEAM_FIELDS}
        return NFLTeam(**values)

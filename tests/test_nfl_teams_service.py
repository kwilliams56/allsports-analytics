"""Tests for documented NFL team response normalization."""

from unittest.mock import Mock

from app.services.base_client import SportsAPIClient
from app.services.nfl_teams import NFLTeam, NFLTeamsService


def test_successful_teams_response_is_normalized_and_sorted():
    api_client = Mock(spec=SportsAPIClient)
    api_client.get_json.return_value = {
        "data": [
            {
                "id": 2,
                "conference": "NFC",
                "division": "WEST",
                "location": "Seattle",
                "name": "Seahawks",
                "full_name": "Seattle Seahawks",
                "abbreviation": "SEA",
            },
            {
                "id": 1,
                "conference": "AFC",
                "division": "NORTH",
                "location": "Baltimore",
                "name": "Ravens",
                "full_name": "Baltimore Ravens",
                "abbreviation": "BAL",
            },
        ]
    }

    teams = NFLTeamsService(api_client).get_teams()

    assert teams == (
        NFLTeam("Ravens", "Baltimore", "AFC", "NORTH", "BAL"),
        NFLTeam("Seahawks", "Seattle", "NFC", "WEST", "SEA"),
    )
    api_client.get_json.assert_called_once()
    call = api_client.get_json.call_args
    assert call.args == ("nfl/v1/teams",)
    assert call.kwargs["required_fields"] == ("data",)
    assert call.kwargs["use_cache"] is True
    call.kwargs["validator"](api_client.get_json.return_value)


def test_empty_teams_response_returns_empty_collection():
    api_client = Mock(spec=SportsAPIClient)
    api_client.get_json.return_value = {"data": []}

    assert NFLTeamsService(api_client).get_teams() == ()


def test_health_check_reuses_documented_teams_resource():
    api_client = Mock(spec=SportsAPIClient)
    api_client.get_json.return_value = {"data": []}

    health = NFLTeamsService(api_client).health_check()

    assert health.available is True
    assert health.team_count == 0
    api_client.get_json.assert_called_once()

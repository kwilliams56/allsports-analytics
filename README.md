# AthletiQ

AthletiQ is a responsive Flask foundation for a professional multi-league sports analytics platform. This first milestone includes the application architecture and interface only; sports data, persistence, search, and authentication are intentionally not implemented yet.

## Tech stack

- Python 3 and Flask
- Flask Blueprints and Jinja2
- Bootstrap 5, custom CSS, and vanilla JavaScript
- Environment-based configuration
- Reliable external API client with retries, validation, and caching
- Gunicorn for Render deployment

## Run locally

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   ```

2. Install dependencies and create local configuration:

   ```bash
   pip install -r requirements-dev.txt
   Copy-Item .env.example .env
   ```

3. Start the app:

   ```bash
   flask --app app.py run --debug
   ```

Open `http://127.0.0.1:5000`.

## Render deployment

Create a new Render Web Service connected to this repository and use:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn 'app:create_app()'`
- Environment variables: `SECRET_KEY` with a secure random value and `BALLDONTLIE_API_KEY` with the provider key

## Architecture

The app factory in `app/__init__.py` creates and configures Flask. Each major feature owns a Blueprint in `app/routes`. External sports integrations live behind `app/services`; routes and templates never call a provider directly. Future domain objects belong in `app/models`, while templates and static assets remain presentation-only.

### Sports-data reliability layer

`SportsAPIClient` is the reusable HTTP boundary for documented provider endpoints. It reads credentials and network settings from Flask configuration, applies a timeout, retries temporary `429` and `5xx` responses with exponential backoff, translates provider/network failures into service exceptions, validates JSON objects and required fields, and caches successful GET responses for a short TTL. It does not contain league-specific endpoint paths or response schemas.

`Cache` is a small interface. `MemoryTTLCache` is the default development implementation; a shared cache such as Redis can replace it later without changing league services. The in-memory cache is process-local and is not intended to coordinate multiple production workers.

Service events use structured JSON logs. API keys and response bodies are deliberately excluded from logs.

Configuration profiles are selected with `APP_ENV=development`, `testing`, or `production`. Copy `.env.example` to `.env`, replace the placeholders locally, and never commit `.env` or a real API key.

`BALLDONTLIE_API_KEY` is the canonical credential variable. `SPORTS_API_KEY` remains a temporary backward-compatible local fallback for installations created before the provider-specific name was introduced.

### NFL teams

The NFL page uses `NFLTeamsService` to fetch the documented free `GET /nfl/v1/teams` resource. The service validates the response and converts provider objects into immutable `NFLTeam` records containing only `name`, `location`, `conference`, `division`, and `abbreviation`. The base client caches the successful JSON response for the configured TTL; authentication failures and all other failures are never cached.

Provider documentation was reverified on July 23, 2026. The official NFL reference continues to document `GET https://api.balldontlie.io/nfl/v1/teams`, direct API-key authentication through the `Authorization` header, and a top-level `data` array whose team objects include `id`, `conference`, `division`, `location`, `name`, `full_name`, and `abbreviation`. AthletiQ's existing endpoint path and normalized fields match that contract, so this review required no endpoint-code change.

`NFLTeamsService.health_check()` checks provider availability through the same documented teams resource and benefits from the same cache. BALLDONTLIE does not document a separate NFL health endpoint.

The Flask route receives normalized records from the configured service and renders the page server-side. It never constructs a provider URL or sends an HTTP request. Expected provider and network failures render a safe error panel while technical failure types and HTTP statuses are logged server-side without credentials or response data.

To test the page manually:

1. Set `BALLDONTLIE_API_KEY` in your untracked `.env` file.
2. Start Flask from the repository root:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   flask --app app.py run --debug
   ```

3. Open `http://127.0.0.1:5000/nfl/`. A successful response displays the NFL team directory. Refreshing within the configured cache TTL should reuse the cached provider response.

### Run tests

Install development dependencies and run the unit suite from the repository root:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

The tests mock the HTTP session and never send a request to BALLDONTLIE.

### BALLDONTLIE verification before NFL player search

The implementation is based only on the current official [BALLDONTLIE NFL documentation](https://nfl.balldontlie.io/) and its linked [NFL OpenAPI specification](https://www.balldontlie.io/openapi/nfl.yml). The documentation currently states:

- The sports API base URL is `https://api.balldontlie.io`, and the API key is sent directly in the `Authorization` header.
- NFL player listing/search is documented at `GET /nfl/v1/players`; it supports cursor pagination plus `search`, `first_name`, `last_name`, `team_ids`, and `player_ids` filters.
- Teams, players, and games are listed as available on the free NFL tier. The free limit is 5 requests per minute; ALL-STAR is 60/minute and GOAT is 600/minute.
- Paid subscriptions are sport-specific. ALL-ACCESS is required to apply one subscription across all supported sports.
- The separate Active Players endpoint requires ALL-STAR or GOAT. Team roster access requires GOAT, and roster data begins with the 2025 season.

For the current teams page, the free plan's primary limitation is its 5-request-per-minute cap. AthletiQ therefore caches successful team responses for five minutes by default. The in-memory cache is process-local, so a future multi-worker deployment should use a shared cache to avoid each worker consuming its own provider request. This task does not use any paid endpoint.

Before implementing player search, verify the account's active NFL subscription in the BALLDONTLIE dashboard, decide whether the product needs all historical players or only active players, and confirm that the selected tier's rate limit is sufficient. Endpoint-specific validation should then be implemented from the current NFL OpenAPI schema rather than inferred from examples.

## Reliability foundation files

Created:

- `app/logging_config.py`
- `app/services/base_client.py`
- `app/services/cache.py`
- `app/services/exceptions.py`
- `app/services/nfl_teams.py`
- `requirements-dev.txt`
- `tests/conftest.py`
- `tests/test_cache.py`
- `tests/test_config.py`
- `tests/test_nfl_route.py`
- `tests/test_nfl_teams_service.py`
- `tests/test_sports_api_client.py`

Changed:

- `.env.example`
- `app/__init__.py`
- `app/routes/nfl.py`
- `app/services/__init__.py`
- `app/static/css/style.css`
- `app/templates/nfl.html`
- `config.py`
- `requirements.txt`
- `README.md`

# AthletiQ Development Roadmap

This file is the source of truth for the AthletiQ project.

## Instructions for Codex

Before starting any task:

1. Read this entire `TODO.md`.
2. Review the current project structure and existing code.
3. Work on only the first unchecked task unless the user explicitly selects another task.
4. Do not rebuild working features unnecessarily.
5. Preserve the Flask Blueprint and services-layer architecture.
6. Use only documented sports-data APIs.
7. Never use scraping, unofficial ESPN endpoints, or guessed API fields.
8. Never hardcode, print, log, or commit API keys.
9. Keep `.env`, `.venv`, `__pycache__`, logs, and generated files out of Git.
10. Add or update tests for every feature.
11. Mark a task complete only after its tests pass and the app still runs.
12. Update this file after completing a task.

## Definition of Done

A task is complete only when:

- The feature works locally.
- External API failures do not crash the application.
- Empty or missing data is handled.
- Relevant automated tests pass.
- The existing pages still work.
- No secrets or generated files are staged.
- Documentation is updated when necessary.
- Codex provides the exact Git commands for committing and pushing.

---

# Phase 1 — Project Foundation

- [x] Create Flask application factory.
- [x] Organize routes with Flask Blueprints.
- [x] Create services, models, templates, and static directories.
- [x] Create responsive homepage.
- [x] Add NFL, NBA, MLB, and NHL placeholder pages.
- [x] Add base template, navigation, and footer.
- [x] Add initial README and environment example.
- [x] Move project files to the repository root.
- [x] Create the correct root-level virtual environment.

# Phase 2 — Reliability Foundation

- [x] Create reusable base API client.
- [x] Load API configuration from environment variables.
- [x] Add request timeout handling.
- [x] Add retry behavior for temporary failures.
- [x] Add custom service exceptions.
- [x] Add application logging.
- [x] Add a cache abstraction.
- [x] Add mocked service tests.
- [x] Review the reliability implementation for security, duplication, and unnecessary complexity.
- [x] Confirm `.env`, `.venv`, caches, and logs are ignored by Git.
- [ ] Run the entire test suite and fix any failures.

# Phase 3 — NFL Teams

## Current Priority

- [ ] Verify the current official NFL provider documentation before changing endpoint code.
- [ ] Confirm the NFL teams endpoint is available on the current API plan.
- [ ] Implement or finish the NFL teams service.
- [ ] Normalize provider responses into an internal team model/dictionary.
- [ ] Display all NFL teams on the NFL landing page.
- [ ] Display available team fields only:
  - name
  - city/location
  - abbreviation
  - conference
  - division
- [ ] Add a professional empty state when no teams are returned.
- [ ] Add a professional error state when the provider is unavailable.
- [ ] Cache the teams response to reduce API usage.
- [ ] Add tests for:
  - successful response
  - empty response
  - missing API key
  - unauthorized response
  - rate limit response
  - timeout
  - connection failure
  - malformed provider response
- [ ] Manually verify the NFL page in the browser.
- [ ] Update README with the NFL teams feature.
- [ ] Commit and push the completed NFL teams milestone.

# Phase 4 — NFL Player Search

Do not begin until Phase 3 is complete.

- [ ] Verify the official player-search endpoint and plan access.
- [ ] Add a player search form to the NFL page.
- [ ] Search by partial or full player name.
- [ ] Keep external requests inside the NFL service.
- [ ] Normalize player responses.
- [ ] Display a list when multiple players match.
- [ ] Add a player profile route and template.
- [ ] Display only documented and available player fields.
- [ ] Handle inactive players and missing fields safely.
- [ ] Add no-results and provider-error states.
- [ ] Add mocked tests for search and profile behavior.
- [ ] Update README.
- [ ] Commit and push the milestone.

# Phase 5 — NFL Games and Schedule

Do not begin until API access has been verified.

- [ ] Verify games and schedule endpoint availability.
- [ ] Add season and week filters.
- [ ] Display game date, status, teams, and score when available.
- [ ] Distinguish scheduled, live, postponed, and final games.
- [ ] Use caching appropriate to game status.
- [ ] Add graceful error and empty states.
- [ ] Add mocked tests.
- [ ] Update README.
- [ ] Commit and push the milestone.

# Phase 6 — NFL Team Detail Pages

- [ ] Add a route for individual NFL teams.
- [ ] Display team identity and conference/division information.
- [ ] Display schedule or recent games when plan access allows.
- [ ] Display roster when plan access allows.
- [ ] Add navigation from team cards.
- [ ] Add tests.
- [ ] Update README.
- [ ] Commit and push the milestone.

# Phase 7 — NFL Statistics and Charts

Do not implement paid features without confirming the user has access.

- [ ] Verify plan access for player game statistics.
- [ ] Verify plan access for season averages.
- [ ] Verify plan access for standings.
- [ ] Add charts only after reliable data is available.
- [ ] Handle incomplete historical data.
- [ ] Add tests for data transformation.
- [ ] Update README.
- [ ] Commit and push the milestone.

# Phase 8 — NBA Module

- [ ] Select and verify a documented, stable NBA data provider.
- [ ] Do not reuse the unreliable architecture from the old NBA dashboard.
- [ ] Implement NBA teams.
- [ ] Implement NBA player search.
- [ ] Implement NBA player profiles.
- [ ] Implement NBA games and schedules.
- [ ] Add NBA statistics only when endpoint access is confirmed.
- [ ] Add tests for each feature.
- [ ] Commit after each milestone.

# Phase 9 — MLB Module

- [ ] Verify a documented MLB data provider.
- [ ] Implement teams.
- [ ] Implement player search and profiles.
- [ ] Implement games and schedules.
- [ ] Add available statistics and charts.
- [ ] Add tests.
- [ ] Commit after each milestone.

# Phase 10 — NHL Module

- [ ] Verify a documented NHL data provider.
- [ ] Implement teams.
- [ ] Implement player search and profiles.
- [ ] Implement games and schedules.
- [ ] Add available statistics and charts.
- [ ] Add tests.
- [ ] Commit after each milestone.

# Phase 11 — Cross-League Features

- [ ] Global search with league filtering.
- [ ] League-specific leaderboards.
- [ ] Team and player favorites.
- [ ] Player comparison within the same league.
- [ ] Responsive charts.
- [ ] Consistent loading, empty, and error states.
- [ ] Accessibility review.
- [ ] Mobile layout review.
- [ ] Performance review.

# Phase 12 — Database and Accounts

Do not begin until the core public analytics experience is stable.

- [ ] Add PostgreSQL.
- [ ] Add database migrations.
- [ ] Add user registration and login.
- [ ] Store favorites per user.
- [ ] Add secure password hashing.
- [ ] Add CSRF protection.
- [ ] Add authentication tests.
- [ ] Add production-safe configuration.

# Phase 13 — Deployment and Portfolio Polish

- [ ] Add production server dependency.
- [ ] Confirm Render start command.
- [ ] Configure environment variables on Render.
- [ ] Deploy without committing secrets.
- [ ] Add production logging.
- [ ] Add health-check route.
- [ ] Verify all league pages after deployment.
- [ ] Add screenshots to README.
- [ ] Add architecture overview to README.
- [ ] Add setup and testing instructions.
- [ ] Add live demo link.
- [ ] Add project to resume, GitHub profile, and LinkedIn.

---

# Required End-of-Task Report from Codex

After completing each task, Codex must provide:

1. A concise summary of what changed.
2. Every file created, modified, or deleted.
3. Tests run and their results.
4. Manual browser-testing steps.
5. Known limitations or unfinished items.
6. Output or interpretation of:
   - `git status`
   - `git diff --stat`
7. Confirmation that none of these will be committed:
   - `.env`
   - `.venv`
   - API keys
   - `__pycache__`
   - log files
   - test caches
8. A recommended commit message.
9. Exact Git commands to stage, commit, and push.
10. Stop and wait for user approval before pushing.

# Git Safety Checklist

Before every commit:

```bash
git status
git diff --stat
```

Confirm `.env` is not listed.

Prefer staging specific files when secrets or unrelated work may be present:

```bash
git add path/to/file1 path/to/file2
```

Then:

```bash
git status
git commit -m "Describe the completed milestone"
git push
```

# Prompt to Use After Adding This File

Paste this into Codex:

```text
Read TODO.md and treat it as the source of truth for this project.

Review the current implementation and work only on the first unchecked task under
"Phase 2 — Reliability Foundation." If those review tasks are already satisfied,
continue with the first unchecked task under "Phase 3 — NFL Teams."

Do not skip ahead. Do not implement player search, schedules, standings, or statistics yet.

Follow the Definition of Done and Required End-of-Task Report in TODO.md. Update TODO.md
only for tasks you actually complete and verify. Use current official provider documentation,
do not guess endpoint URLs or response fields, and do not expose or commit secrets.

After completing the selected task, run the relevant tests, confirm the Flask app still starts,
provide the Git safety report and exact commit commands, and stop for my approval.
```

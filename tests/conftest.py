"""Global test safeguards."""

import pytest
import requests


@pytest.fixture(autouse=True)
def prevent_real_http_requests(monkeypatch):
    """Fail immediately if any test attempts a real Requests call."""

    def blocked_request(*args, **kwargs):
        pytest.fail("Unit tests must not make real external HTTP requests.")

    monkeypatch.setattr(requests.sessions.Session, "request", blocked_request)

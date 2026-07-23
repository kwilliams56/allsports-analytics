"""Security and duplication tests for structured application logging."""

import json
import logging

from app import create_app
from app.logging_config import JSONFormatter
from config import TestingConfig


def test_structured_logging_redacts_credential_like_extra_fields():
    record = logging.makeLogRecord(
        {
            "name": "app",
            "levelno": logging.INFO,
            "levelname": "INFO",
            "msg": "provider_event",
            "args": (),
            "event": "provider_event",
            "api_key": "never-output-this-value",
            "authorization": "never-output-this-header",
        }
    )

    payload = json.loads(JSONFormatter().format(record))

    assert payload["api_key"] == "[REDACTED]"
    assert payload["authorization"] == "[REDACTED]"
    assert "never-output" not in json.dumps(payload)


def test_app_logger_has_one_handler_and_does_not_propagate():
    app = create_app(TestingConfig)

    assert len(app.logger.handlers) == 1
    assert app.logger.propagate is False

"""Structured JSON logging for application and service events."""

import json
import logging
from datetime import datetime, timezone

from flask import Flask


class JSONFormatter(logging.Formatter):
    """Format log records as one-line JSON for local and hosted runtimes."""

    _standard_fields = set(logging.makeLogRecord({}).__dict__)
    _sensitive_terms = ("authorization", "key", "password", "secret", "token")

    @classmethod
    def _safe_extra_fields(cls, record: logging.LogRecord) -> dict:
        """Return structured extras with credential-like fields redacted."""
        fields = {}
        for key, value in record.__dict__.items():
            if key in cls._standard_fields or key == "message":
                continue
            fields[key] = (
                "[REDACTED]"
                if any(term in key.lower() for term in cls._sensitive_terms)
                else value
            )
        return fields

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(self._safe_extra_fields(record))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(app: Flask) -> None:
    """Attach a structured handler without duplicating handlers in tests."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.propagate = False

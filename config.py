"""Environment-specific application configuration."""

import os
from typing import Type

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


class BaseConfig:
    """Settings shared by every AthletiQ environment."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    TESTING = False
    DEBUG = False
    REQUIRE_SECURE_SECRET = False

    # The provider key remains environment-only; the generic client receives it
    # through Flask configuration and never reads or logs it directly.
    SPORTS_API_KEY = os.getenv("BALLDONTLIE_API_KEY") or os.getenv("SPORTS_API_KEY")
    SPORTS_API_BASE_URL = os.getenv(
        "SPORTS_API_BASE_URL", "https://api.balldontlie.io"
    ).rstrip("/")
    SPORTS_API_TIMEOUT_SECONDS = float(
        os.getenv("SPORTS_API_TIMEOUT_SECONDS", "5")
    )
    SPORTS_API_MAX_RETRIES = int(os.getenv("SPORTS_API_MAX_RETRIES", "3"))
    SPORTS_API_BACKOFF_SECONDS = float(
        os.getenv("SPORTS_API_BACKOFF_SECONDS", "0.5")
    )
    SPORTS_API_CACHE_TTL_SECONDS = int(
        os.getenv("SPORTS_API_CACHE_TTL_SECONDS", "300")
    )


class DevelopmentConfig(BaseConfig):
    """Local development settings."""

    DEBUG = _as_bool(os.getenv("FLASK_DEBUG", "true"))


class TestingConfig(BaseConfig):
    """Deterministic settings for tests; no real credentials are required."""

    TESTING = True
    SECRET_KEY = "testing-secret"
    SPORTS_API_KEY = "testing-api-key"
    SPORTS_API_MAX_RETRIES = 0
    SPORTS_API_CACHE_TTL_SECONDS = 0


class ProductionConfig(BaseConfig):
    """Production settings with Flask debugging disabled."""

    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    REQUIRE_SECURE_SECRET = True


CONFIG_BY_NAME: dict[str, Type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(environment: str | None = None) -> Type[BaseConfig]:
    """Return the configuration class for an environment name."""
    name = (environment or os.getenv("APP_ENV", "development")).lower()
    try:
        return CONFIG_BY_NAME[name]
    except KeyError as exc:
        valid = ", ".join(sorted(CONFIG_BY_NAME))
        raise ValueError(f"Unknown APP_ENV '{name}'. Choose one of: {valid}.") from exc

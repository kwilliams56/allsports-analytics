"""Tests for environment-specific Flask configuration."""

import pytest

from app import create_app
from config import DevelopmentConfig, ProductionConfig, TestingConfig, get_config


def test_named_configurations_have_expected_modes():
    assert get_config("development") is DevelopmentConfig
    assert get_config("testing") is TestingConfig
    assert get_config("production") is ProductionConfig
    assert TestingConfig.TESTING is True
    assert ProductionConfig.DEBUG is False


def test_unknown_environment_fails_clearly():
    with pytest.raises(ValueError, match="Unknown APP_ENV"):
        get_config("unknown")


def test_app_factory_accepts_testing_configuration():
    app = create_app(TestingConfig)
    assert app.testing is True
    assert app.test_client().get("/").status_code == 200

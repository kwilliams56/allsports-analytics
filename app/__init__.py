"""AthletiQ application factory."""

from flask import Flask

from config import get_config

from app.logging_config import configure_logging


def create_app(config_class=None):
    """Create, configure, and return the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class or get_config())
    configure_logging(app)

    # Import locally to avoid circular imports during app creation.
    from app.routes import register_blueprints
    from app.services import init_services

    init_services(app)
    register_blueprints(app)
    return app

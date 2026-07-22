"""AthletiQ application factory."""

from flask import Flask

from config import Config


def create_app(config_class=Config):
    """Create, configure, and return the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Import locally to avoid circular imports during app creation.
    from app.routes import register_blueprints

    register_blueprints(app)
    return app

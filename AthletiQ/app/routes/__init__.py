"""Blueprint registration for all AthletiQ routes."""

from flask import Flask

from app.routes.home import home_bp
from app.routes.mlb import mlb_bp
from app.routes.nba import nba_bp
from app.routes.nfl import nfl_bp
from app.routes.nhl import nhl_bp


def register_blueprints(app: Flask) -> None:
    """Attach all feature Blueprints to the application."""
    app.register_blueprint(home_bp)
    app.register_blueprint(nfl_bp)
    app.register_blueprint(nba_bp)
    app.register_blueprint(mlb_bp)
    app.register_blueprint(nhl_bp)

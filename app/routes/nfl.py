"""NFL feature routes."""

from flask import Blueprint, render_template

nfl_bp = Blueprint("nfl", __name__, url_prefix="/nfl")


@nfl_bp.get("/")
def index():
    return render_template("nfl.html")

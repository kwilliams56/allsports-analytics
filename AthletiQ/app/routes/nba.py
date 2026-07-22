"""NBA feature routes."""
from flask import Blueprint, render_template

nba_bp = Blueprint("nba", __name__, url_prefix="/nba")

@nba_bp.get("/")
def index():
    return render_template("nba.html")

"""NHL feature routes."""
from flask import Blueprint, render_template

nhl_bp = Blueprint("nhl", __name__, url_prefix="/nhl")

@nhl_bp.get("/")
def index():
    return render_template("nhl.html")

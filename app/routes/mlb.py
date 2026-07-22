"""MLB feature routes."""
from flask import Blueprint, render_template

mlb_bp = Blueprint("mlb", __name__, url_prefix="/mlb")

@mlb_bp.get("/")
def index():
    return render_template("mlb.html")

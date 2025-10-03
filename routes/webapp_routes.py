"""
WebApp routes for PulseAI Dashboard.
"""

from flask import Blueprint, render_template

# Create WebApp blueprint
webapp_bp = Blueprint("webapp", __name__)


@webapp_bp.route("/webapp")
def webapp():
    """WebApp Dashboard route"""
    return render_template("webapp.html")


__all__ = ["webapp_bp"]

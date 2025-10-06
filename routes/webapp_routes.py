from flask import Blueprint, render_template

webapp_bp = Blueprint("webapp", __name__)


@webapp_bp.route("/webapp")
def webapp():
    """WebApp Dashboard route"""
    return render_template("webapp.html")


@webapp_bp.route("/live")
def live_dashboard():
    """Live Reactor Dashboard route"""
    return render_template("pages/live_dashboard.html", active_page="live")

@webapp_bp.route("/app")
def react_app():
    """React Frontend App route"""
    return render_template("react_app.html")

from flask import Blueprint, render_template

webapp_bp = Blueprint("webapp", __name__)

@webapp_bp.route("/webapp")
def webapp():
    """WebApp Dashboard route"""
    return render_template("webapp.html")

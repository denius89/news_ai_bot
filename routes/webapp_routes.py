from flask import Blueprint, render_template

webapp_bp = Blueprint("webapp", __name__)


# УДАЛЕН: Конфликтующий маршрут /webapp
# Теперь используется serve_react() из webapp.py


@webapp_bp.route("/live")
def live_dashboard():
    """Live Reactor Dashboard route"""
    return render_template("pages/live_dashboard.html", active_page="live")


# УДАЛЕН: Конфликтующий маршрут /app
# Теперь используется serve_react() из webapp.py

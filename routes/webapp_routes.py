from flask import Blueprint, render_template

webapp_bp = Blueprint("webapp", __name__)


@webapp_bp.route("/webapp")
def webapp():
    """WebApp Dashboard route - перенаправляем на React"""
    from flask import redirect
    import logging
    logger = logging.getLogger("news_ai_bot")
    logger.info("📱 WebApp dashboard accessed - redirecting to React")
    # Перенаправляем на React приложение
    return redirect("http://localhost:3000/webapp")


@webapp_bp.route("/live")
def live_dashboard():
    """Live Reactor Dashboard route"""
    return render_template("pages/live_dashboard.html", active_page="live")

@webapp_bp.route("/app")
def react_app():
    """React Frontend App route - перенаправляем на React"""
    from flask import redirect
    import logging
    logger = logging.getLogger("news_ai_bot")
    logger.info("📱 React app accessed - redirecting to React")
    return redirect("http://localhost:3000/webapp")

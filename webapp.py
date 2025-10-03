import logging
from flask import Flask, render_template

from config.settings import VERSION, DEBUG, WEBAPP_PORT, WEBAPP_HOST
from routes.news_routes import news_bp
from routes.webapp_routes import webapp_bp
from routes.api_routes import api_bp
from utils.logging_setup import setup_logging

# --- ЛОГИРОВАНИЕ ---
setup_logging()
logger = logging.getLogger("news_ai_bot")

app = Flask(__name__)
app.config["VERSION"] = VERSION


# 🔥 Фильтр для отображения иконок важности
def importance_icon(value: float) -> str:
    if value is None:
        return "❔"
    if value >= 0.8:
        return "🔥"
    elif value >= 0.5:
        return "⚡"
    return "💤"


# Регистрируем фильтр в Jinja
app.jinja_env.filters["importance_icon"] = importance_icon


# Главная страница
@app.route("/")
def index():
    return render_template("index.html", active_page="home")


# Регистрируем маршруты
app.register_blueprint(news_bp)
app.register_blueprint(webapp_bp)
app.register_blueprint(api_bp)


# --- Точка входа ---
if __name__ == "__main__":
    from database.db_models import get_latest_news

    logger.info(f"🚀 Webapp запущен (хост {WEBAPP_HOST}, порт {WEBAPP_PORT}, debug={DEBUG})")

    try:
        latest = get_latest_news(limit=5)
        logger.debug("🔎 Последние новости из БД:")
        for n in latest:
            logger.debug(
                "- %s... (credibility=%s, importance=%s)",
                n["title"][:50],
                n.get("credibility"),
                n.get("importance"),
            )
    except Exception:
        logger.exception("⚠️ Ошибка при debug-загрузке новостей")

    app.run(host=WEBAPP_HOST, port=WEBAPP_PORT, debug=DEBUG)

import logging
from flask import Flask, render_template

from config.settings import VERSION, DEBUG, WEBAPP_PORT, WEBAPP_HOST, REACTOR_ENABLED
from routes.news_routes import news_bp
from routes.webapp_routes import webapp_bp
from routes.api_routes import api_bp
# WebSocket routes removed - using FastAPI now
# from routes.ws_routes import ws_bp, init_socketio
from routes.metrics_routes import metrics_bp
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
# WebSocket blueprint removed - using FastAPI now
# app.register_blueprint(ws_bp)
app.register_blueprint(metrics_bp)

# WebSocket initialization removed - using FastAPI now
# if REACTOR_ENABLED:
#     try:
#         init_socketio(app)
#         logger.info("✅ WebSocket Hub инициализирован")
#     except Exception as e:
#         logger.error(f"❌ Ошибка инициализации WebSocket: {e}")
# else:
#     logger.info("⚠️ Reactor отключен, WebSocket не инициализирован")


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

    # WebSocket support removed - using FastAPI now
    # if REACTOR_ENABLED:
    #     # Используем SocketIO для запуска с WebSocket поддержкой
    #     from routes.ws_routes import socketio
    #     if socketio:
    #         socketio.run(app, host=WEBAPP_HOST, port=WEBAPP_PORT, debug=DEBUG, allow_unsafe_werkzeug=True)
    #     else:
    #         logger.error("❌ SocketIO не инициализирован, запускаем обычный Flask")
    #         app.run(host=WEBAPP_HOST, port=WEBAPP_PORT, debug=DEBUG)
    # else:
    #     # Обычный Flask запуск
    #     app.run(host=WEBAPP_HOST, port=WEBAPP_PORT, debug=DEBUG)
    
    # Запускаем обычный Flask без WebSocket
    logger.info("⚠️ WebSocket отключен, запускаем обычный Flask")
    app.run(host=WEBAPP_HOST, port=WEBAPP_PORT, debug=DEBUG)

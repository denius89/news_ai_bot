import logging
import os
from flask import Flask, render_template, send_from_directory, redirect

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.core.settings import VERSION, DEBUG, WEBAPP_PORT, WEBAPP_HOST, REACTOR_ENABLED
from routes.news_routes import news_bp

# webapp_bp удален - конфликтовал с serve_react()
from routes.api_routes import api_bp
from routes.dashboard_api import dashboard_api

# WebSocket routes removed - using FastAPI now
# from routes.ws_routes import ws_bp, init_socketio
from routes.metrics_routes import metrics_bp
from utils.logging.logging_setup import setup_logging

# --- ЛОГИРОВАНИЕ ---
setup_logging()
logger = logging.getLogger("news_ai_bot")

app = Flask(__name__)
app.config["VERSION"] = VERSION


# Добавляем REACTOR_ENABLED в контекст шаблонов
@app.context_processor
def inject_config():
    return {"config": {"REACTOR_ENABLED": REACTOR_ENABLED}}


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


# Импортируем централизованную систему путей
from config.paths import get_path, setup_pythonpath

# Настраиваем PYTHONPATH
setup_pythonpath()

# Путь к собранному React
REACT_DIST_PATH = get_path("webapp_dist")


# React статические файлы
@app.route("/webapp")
@app.route("/webapp/")
@app.route("/webapp/<path:path>")
def serve_react(path=""):
    """Обслуживает React приложение как статику"""
    logger.info(f"🎯 serve_react() вызвана с path='{path}'")
    try:
        if path == "" or path == "/":
            logger.info("📄 Отдаем index.html")
            response = send_from_directory(REACT_DIST_PATH, "index.html")
            # Добавляем заголовки для Telegram WebApp
            response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"
            response.headers["Cross-Origin-Opener-Policy"] = "unsafe-none"
            response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
            return response

        # Попробовать отдать статический файл
        try:
            response = send_from_directory(REACT_DIST_PATH, path)
            # Добавляем заголовки для Telegram WebApp
            response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"
            response.headers["Cross-Origin-Opener-Policy"] = "unsafe-none"
            response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
            return response
        except BaseException:
            # React Router fallback - все неизвестные пути ведут на index.html
            response = send_from_directory(REACT_DIST_PATH, "index.html")
            # Добавляем заголовки для Telegram WebApp
            response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"
            response.headers["Cross-Origin-Opener-Policy"] = "unsafe-none"
            response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
            return response
    except FileNotFoundError:
        # Если папка dist не существует, показать сообщение
        return (
            f"""
        <h1>React не собран</h1>
        <p>Запустите: <code>cd webapp && npm run build</code></p>
        <p>Папка {REACT_DIST_PATH} не найдена.</p>
        """,
            404,
        )


# Главная страница перенаправляет на React
@app.route("/")
def index():
    return redirect("/webapp")


# Регистрируем маршруты
app.register_blueprint(news_bp)
# webapp_bp удален - конфликтовал с serve_react()
app.register_blueprint(api_bp)
app.register_blueprint(dashboard_api)
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

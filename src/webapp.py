import logging
import os
from flask import Flask, send_from_directory, redirect, session, request, g
from flask_cors import CORS
from datetime import timedelta

import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.core.settings import VERSION, DEBUG, WEBAPP_PORT, WEBAPP_HOST, REACTOR_ENABLED
from utils.auth.telegram_auth import verify_telegram_auth
from routes.news_routes import news_bp
from routes.events_routes import register_events_routes

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

app = Flask(__name__, static_folder="dist")
app.config["VERSION"] = VERSION

# Flask session configuration для безопасности
app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=not DEBUG,  # Только для HTTPS в production
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
)


# Middleware для единой аутентификации
@app.before_request  # noqa: E302  # noqa: E302
def authenticate_request():
    """Единая точка аутентификации для всех защищенных endpoints."""
    if request.path.startswith("/api/"):
        # Публичные API endpoints, которые не требуют аутентификации
        public_paths = [
            "/api/health",
            "/api/users/by-telegram-id",  # Только для первичной аутентификации
            "/api/categories",
            "/api/digests/categories",
            "/api/digests/styles",
            "/api/latest",
            "/api/dashboard/stats",
            "/api/dashboard/latest_news",
            "/api/dashboard/news_trend",
            "/api/events",  # Events API - публичный доступ
        ]

        # Проверяем, является ли endpoint публичным
        is_public = any(request.path.startswith(path) for path in public_paths)

        if not is_public:
            # Для защищенных endpoints проверяем аутентификацию
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            auth_result = verify_telegram_auth(
                request_headers=dict(request.headers), session_data=session, bot_token=bot_token
            )

            if not auth_result["success"]:
                from flask import jsonify

                logger.warning(f"Authentication failed for {request.path}: {auth_result['message']}")
                return jsonify({"error": auth_result["message"]}), 401

            # Устанавливаем данные пользователя в g для использования в endpoints
            g.current_user = auth_result

            # Устанавливаем session для быстрой повторной аутентификации
            if auth_result["method"] != "session":
                session["user_id"] = auth_result["user_id"]
                session["telegram_id"] = auth_result["telegram_id"]
                session.permanent = True


# Middleware для обработки Telegram WebApp запросов
@app.before_request  # noqa: E302  # noqa: E302
def process_telegram_request():
    """Обрабатывает Telegram WebApp запросы и устанавливает флаги."""
    from utils.auth.telegram_auth import is_telegram_webapp_request

    g.is_telegram_webapp = is_telegram_webapp_request(dict(request.headers))

    if g.is_telegram_webapp:
        logger.debug(f"Telegram WebApp request detected: {request.path}")


# Настройка CORS для Telegram WebApp
CORS(
    app,
    origins=[  # noqa: E305
        "https://design-treasures-titten-formation.trycloudflare.com",
        "https://*.trycloudflare.com",
        "https://telegram.org",
        "https://web.telegram.org",
    ],
)


# Middleware для разрешения встраивания в iframe (Telegram WebApp)
@app.after_request  # noqa: E302  # noqa: E302
def set_frame_options(response):
    """Устанавливает заголовки для разрешения встраивания в iframe"""
    response.headers["X-Frame-Options"] = "ALLOWALL"
    # Обновленная CSP политика для Telegram WebApp
    csp_policy = (
        "frame-ancestors *; "
        "connect-src 'self' https://*.trycloudflare.com https://telegram.org https://web.telegram.org wss://*.telegram.org wss://*.web.telegram.org data:; "
        "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: https://telegram.org; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://telegram.org; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' data: https://fonts.gstatic.com; "
        "img-src 'self' data: blob: https:; "
        "object-src 'none'; "
        "base-uri 'self'"
    )
    response.headers["Content-Security-Policy"] = csp_policy
    return response


# Middleware для обработки Telegram WebApp заголовков
@app.before_request  # noqa: E302
def handle_telegram_headers():
    """Обработка заголовков Telegram WebApp"""
    from flask import request, g

    # Логируем заголовки для отладки
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token"):
        logger.info("🔍 Telegram WebApp request detected")
        logger.info(f"Headers: {dict(request.headers)}")

    # Устанавливаем флаг для Telegram WebApp
    g.is_telegram_webapp = bool(request.headers.get("X-Telegram-Bot-Api-Secret-Token"))


# Middleware для отключения кэширования API запросов
@app.after_request  # noqa: E302
def disable_api_caching(response):
    """Отключаем кэширование для всех API запросов"""
    from flask import request

    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


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
register_events_routes(app)  # Register events routes
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

import logging
from flask import Flask

from config.constants import VERSION
from routes.news_routes import news_bp
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
    else:
        return "💤"


# Регистрируем фильтр в Jinja
app.jinja_env.filters["importance_icon"] = importance_icon

# Регистрируем маршруты
app.register_blueprint(news_bp)


# --- Точка входа ---
if __name__ == "__main__":
    from database.db_models import get_latest_news

    logger.info("🚀 Webapp запущен (порт 5000)")

    # Debug: последние новости
    print("🔎 Debug: последние новости из БД")
    try:
        latest = get_latest_news(limit=5)
        for n in latest:
            print(f"- {n['title'][:50]}...")
            print(f"  credibility={n.get('credibility')}, importance={n.get('importance')}")
    except Exception as e:
        print(f"⚠️ Ошибка при debug-загрузке новостей: {e}")

    app.run(host="127.0.0.1", port=8001, debug=True)

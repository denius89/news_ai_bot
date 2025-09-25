import logging
from flask import Flask

from config.constants import VERSION  # ✅ правильный импорт
from routes.news_routes import news_bp
from utils.logging_setup import setup_logging

# --- ЛОГИРОВАНИЕ ---
setup_logging()
logger = logging.getLogger("news_ai_bot")

app = Flask(__name__)
app.config["VERSION"] = VERSION  # ✅ берём из constants.py


# 🔥 Добавляем фильтр для отображения иконок важности
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

if __name__ == "__main__":
    logger.info("🚀 Webapp запущен (порт 5000)")
    app.run(debug=True, port=5000)

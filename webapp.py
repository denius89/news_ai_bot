from flask import Flask
from routes.news_routes import news_bp
import config

app = Flask(__name__)
app.config['VERSION'] = config.VERSION

app = Flask(__name__)

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
app.jinja_env.filters['importance_icon'] = importance_icon

# Регистрируем маршруты
app.register_blueprint(news_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
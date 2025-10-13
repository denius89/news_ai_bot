import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# telegram_bot/handlers/__init__.py
from . import start, digest, digest_ai, events, dashboard, notifications, subscriptions

# Список всех роутеров для подключения в bot.py
# Оставляем только основные команды: /start, /digest, /events, /help
routers = [
    start.router,
    digest.router,
    digest_ai.router,
    events.router,
    dashboard.router,
    notifications.router,
    subscriptions.router,
]

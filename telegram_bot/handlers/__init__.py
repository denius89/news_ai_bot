# telegram_bot/handlers/__init__.py
from . import start, digest, digest_ai, events, dashboard

# Список всех роутеров для подключения в bot.py
# Subscriptions removed - now handled in WebApp Dashboard
routers = [
    start.router,
    digest_ai.router,
    digest.router,
    events.router,
    dashboard.router,
]

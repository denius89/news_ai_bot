# telegram_bot/handlers/__init__.py
from . import start, digest, digest_ai, events, subscriptions

# Список всех роутеров для подключения в bot.py
routers = [
    start.router,
    digest_ai.router,
    digest.router,
    events.router,
    subscriptions.router,
]

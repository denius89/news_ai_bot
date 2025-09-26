# telegram_bot/handlers/__init__.py
from . import start, digest, digest_ai, events

# Список всех роутеров для подключения в bot.py
routers = [
    start.router,
    digest.router,
    digest_ai.router,
    events.router,
]

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# telegram_bot/handlers/__init__.py
from . import start

# Список всех роутеров для подключения в bot.py
routers = [
    start.router,  # /start
]

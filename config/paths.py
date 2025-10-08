"""
Централизованная система путей для проекта PulseAI.

Этот модуль содержит все пути проекта в одном месте,
что предотвращает ошибки с неправильными путями.
"""

from pathlib import Path

# Корневая директория проекта
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Основные пути
PATHS = {
    # Конфигурация
    "config": PROJECT_ROOT / "config",
    "settings": PROJECT_ROOT / "config" / "core" / "settings.py",
    "cloudflare": PROJECT_ROOT / "config" / "core" / "cloudflare.py",
    # Веб-приложение
    "webapp": PROJECT_ROOT / "webapp",
    "webapp_dist": PROJECT_ROOT / "webapp" / "dist",
    "webapp_index": PROJECT_ROOT / "webapp" / "dist" / "index.html",
    # Логи
    "logs": PROJECT_ROOT / "logs",
    "webapp_log": PROJECT_ROOT / "logs" / "webapp.log",
    "bot_log": PROJECT_ROOT / "logs" / "bot.log",
    # База данных
    "database": PROJECT_ROOT / "database",
    # AI модули
    "ai_modules": PROJECT_ROOT / "ai_modules",
    # Утилиты
    "utils": PROJECT_ROOT / "utils",
    # Telegram Bot
    "telegram_bot": PROJECT_ROOT / "telegram_bot",
    # Скрипты
    "scripts": PROJECT_ROOT / "scripts",
}


def get_path(key: str) -> Path:
    """Получить путь по ключу."""
    if key not in PATHS:
        raise KeyError(f"Путь '{key}' не найден. Доступные пути: {list(PATHS.keys())}")
    return PATHS[key]


def ensure_path_exists(key: str) -> Path:
    """Получить путь и убедиться, что он существует."""
    path = get_path(key)
    if not path.exists():
        raise FileNotFoundError(f"Путь '{key}' не существует: {path}")
    return path


def setup_pythonpath():
    """Настроить PYTHONPATH для проекта."""
    import sys

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))


# Автоматически настраиваем PYTHONPATH при импорте
setup_pythonpath()

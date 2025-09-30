# config/settings.py
import os
from pathlib import Path

# Корень репозитория
BASE_DIR = Path(__file__).resolve().parents[1]

# ---- БАЗОВЫЕ НАСТРОЙКИ ----
APP_ENV = os.getenv("APP_ENV", "dev")
DEBUG = os.getenv("DEBUG", "0") == "1"
TIMEZONE = os.getenv("TZ", "Europe/Warsaw")

# Версия приложения
VERSION = os.getenv("VERSION", "0.1.0")

# Настройки webapp
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "8001"))

# ---- БД ----
# Пример: postgres://user:pass@host:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/news_ai_bot.sqlite3")

# ---- ВНЕШНИЕ КЛЮЧИ ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ---- AI ----
AI_MODEL_SUMMARY = os.getenv("AI_MODEL_SUMMARY", "gpt-4o-mini")
AI_MODEL_SCORING = os.getenv("AI_MODEL_SCORING", "gpt-4o-mini")
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "800"))

# ---- ПУТИ ДО YAML-КОНФИГОВ ----
LOGGING_YAML = str(BASE_DIR / "config" / "logging.yaml")
SOURCES_YAML = str(BASE_DIR / "config" / "sources.yaml")


# Удобный алиас, если где-то используется "config.SOMETHING"
class _C:
    BASE_DIR = BASE_DIR
    APP_ENV = APP_ENV
    DEBUG = DEBUG
    TIMEZONE = TIMEZONE
    DATABASE_URL = DATABASE_URL
    OPENAI_API_KEY = OPENAI_API_KEY
    TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN
    AI_MODEL_SUMMARY = AI_MODEL_SUMMARY
    AI_MODEL_SCORING = AI_MODEL_SCORING
    AI_MAX_TOKENS = AI_MAX_TOKENS
    LOGGING_YAML = LOGGING_YAML
    SOURCES_YAML = SOURCES_YAML


config = _C()

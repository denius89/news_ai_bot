# config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Корень репозитория
BASE_DIR = Path(__file__).resolve().parents[1]

# ---- БАЗОВЫЕ НАСТРОЙКИ ----
APP_ENV = os.getenv("APP_ENV", "dev")
DEBUG = os.getenv("DEBUG", "1") == "1"
TIMEZONE = os.getenv("TZ", "Europe/Warsaw")

# Версия приложения
VERSION = os.getenv("VERSION", "0.1.0")

# Настройки webapp
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "8001"))
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:8001")

# Supabase настройки
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

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

# ---- REACTOR CORE ----
REACTOR_ENABLED = os.getenv("REACTOR_ENABLED", "true").lower() == "true"
REACTOR_WS_PATH = os.getenv("REACTOR_WS_PATH", "/ws/stream")
REACTOR_LOG_PATH = os.getenv("REACTOR_LOG_PATH", "logs/reactor.log")

# ---- ПУТИ ДО YAML-КОНФИГОВ ----
LOGGING_YAML = str(BASE_DIR / "config" / "logging.yaml")
SOURCES_YAML = str(BASE_DIR / "config" / "sources.yaml")


# Удобный алиас, если где-то используется "config.SOMETHING"
class _C:
    BASE_DIR = BASE_DIR
    APP_ENV = APP_ENV
    DEBUG = DEBUG
    TIMEZONE = TIMEZONE
    WEBAPP_HOST = WEBAPP_HOST
    WEBAPP_PORT = WEBAPP_PORT
    WEBAPP_URL = WEBAPP_URL
    SUPABASE_URL = SUPABASE_URL
    SUPABASE_KEY = SUPABASE_KEY
    DATABASE_URL = DATABASE_URL
    OPENAI_API_KEY = OPENAI_API_KEY
    TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN
    AI_MODEL_SUMMARY = AI_MODEL_SUMMARY
    AI_MODEL_SCORING = AI_MODEL_SCORING
    AI_MAX_TOKENS = AI_MAX_TOKENS
    REACTOR_ENABLED = REACTOR_ENABLED
    REACTOR_WS_PATH = REACTOR_WS_PATH
    REACTOR_LOG_PATH = REACTOR_LOG_PATH
    LOGGING_YAML = LOGGING_YAML
    SOURCES_YAML = SOURCES_YAML


config = _C()


# ---- Маппинг стран → ISO-коды (минимально нужное, при необходимости расширишь) ----
COUNTRY_MAP = {
    "united states": "us",
    "us": "us",
    "u.s.": "us",
    "usa": "us",
    "canada": "ca",
    "ca": "ca",
    "mexico": "mx",
    "mx": "mx",
    "brazil": "br",
    "br": "br",
    "argentina": "ar",
    "ar": "ar",
    "chile": "cl",
    "cl": "cl",
    "united kingdom": "gb",
    "uk": "gb",
    "gb": "gb",
    "england": "gb",
    "britain": "gb",
    "euro zone": "eu",
    "euro area": "eu",
    "eu": "eu",
    "germany": "de",
    "france": "fr",
    "italy": "it",
    "spain": "es",
    "portugal": "pt",
    "netherlands": "nl",
    "holland": "nl",
    "belgium": "be",
    "switzerland": "ch",
    "sweden": "se",
    "norway": "no",
    "denmark": "dk",
    "finland": "fi",
    "austria": "at",
    "greece": "gr",
    "ireland": "ie",
    "poland": "pl",
    "czech republic": "cz",
    "czechia": "cz",
    "hungary": "hu",
    "romania": "ro",
    "slovakia": "sk",
    "slovenia": "si",
    "china": "cn",
    "japan": "jp",
    "india": "in",
    "hong kong": "hk",
    "singapore": "sg",
    "south korea": "kr",
    "korea": "kr",
    "republic of korea": "kr",
    "taiwan": "tw",
    "indonesia": "id",
    "malaysia": "my",
    "thailand": "th",
    "philippines": "ph",
    "australia": "au",
    "new zealand": "nz",
    "south africa": "za",
    "egypt": "eg",
    "nigeria": "ng",
    "israel": "il",
    "turkey": "tr",
    "saudi arabia": "sa",
    "uae": "ae",
    "united arab emirates": "ae",
    "qatar": "qa",
    "kuwait": "kw",
    "": None,
}

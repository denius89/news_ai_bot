"""
Глобальные константы и справочники для проекта.
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# --- Категории источников ---
CATEGORIES = ["crypto", "economy", "world", "technology", "politics"]

# --- Теги по умолчанию ---
DEFAULT_TAGS = ["news", "macro", "events"]

# --- Маппинг стран для флагов ---
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

# --- Версия проекта ---
VERSION = "0.1.0"

# --- API ключи (из .env) ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Telegram Bot ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

import os
import hashlib
import logging
from datetime import datetime, timezone
from supabase import create_client
from dotenv import load_dotenv

from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance

# --- ЛОГИРОВАНИЕ ---
logger = logging.getLogger("database")

# --- ПОДКЛЮЧЕНИЕ К SUPABASE ---
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = None
if url and key:
    supabase = create_client(url, key)
    logger.info("Supabase client initialized")
else:
    logger.warning("⚠️ Supabase не инициализирован (нет ключей). Unit-тесты будут выполняться без БД.")

# --- Маппинг стран для флагов ---
COUNTRY_MAP = {
    "united states": "us", "us": "us", "u.s.": "us", "usa": "us",
    "canada": "ca", "ca": "ca",
    "mexico": "mx", "mx": "mx",
    "brazil": "br", "br": "br",
    "argentina": "ar", "ar": "ar",
    "chile": "cl", "cl": "cl",
    "united kingdom": "gb", "uk": "gb", "gb": "gb", "england": "gb", "britain": "gb",
    "euro zone": "eu", "euro area": "eu", "eu": "eu",
    "germany": "de", "france": "fr", "italy": "it", "spain": "es",
    "portugal": "pt", "netherlands": "nl", "holland": "nl", "belgium": "be",
    "switzerland": "ch", "sweden": "se", "norway": "no", "denmark": "dk",
    "finland": "fi", "austria": "at", "greece": "gr", "ireland": "ie",
    "poland": "pl", "czech republic": "cz", "czechia": "cz", "hungary": "hu",
    "romania": "ro", "slovakia": "sk", "slovenia": "si",
    "china": "cn", "japan": "jp", "india": "in", "hong kong": "hk",
    "singapore": "sg", "south korea": "kr", "korea": "kr", "republic of korea": "kr",
    "taiwan": "tw", "indonesia": "id", "malaysia": "my", "thailand": "th", "philippines": "ph",
    "australia": "au", "new zealand": "nz",
    "south africa": "za", "egypt": "eg", "nigeria": "ng",
    "israel": "il", "turkey": "tr", "saudi arabia": "sa",
    "uae": "ae", "united arab emirates": "ae", "qatar": "qa", "kuwait": "kw",
    "": None,
}

# --- UID для дедупликации ---
def make_uid(url: str, title: str) -> str:
    return hashlib.sha256(f"{url}|{title}".encode()).hexdigest()

# --- UPSERT новостей ---
def upsert_news(items: list[dict]):
    """Вставляет новости в Supabase без дублей (по uid)."""
    if not supabase:
        logger.warning("Supabase не подключён, данные не будут сохранены.")
        return

    rows = []
    for item in items:
        try:
            uid = make_uid(item["url"], item["title"])
            rows.append({
                "uid": uid,
                "title": item["title"][:512],
                "content": item.get("summary", ""),   # парсер summary → content
                "link": item["url"],                  # парсер url → link
                "published_at": (item.get("published_at").isoformat() if item.get("published_at") else datetime.now(timezone.utc).isoformat()),
                "source": item.get("source"),
                "category": item.get("category"),
                "credibility": item.get("credibility"),  # можно рассчитать отдельно
                "importance": item.get("importance"),
            })
        except Exception as e:
            logger.error(f"Ошибка подготовки новости: {e}, item={item}")

    try:
        if rows:
            res = supabase.table("news").upsert(rows, on_conflict="uid").execute()
            logger.info(f"Inserted {len(rows)} news items (upsert).")
            return res
        else:
            logger.info("Нет данных для вставки")
    except Exception as e:
        logger.error(f"Ошибка при вставке в Supabase: {e}")

# --- Пример функции для обновления credibility/importance ---
def enrich_news_with_ai(news_item: dict) -> dict:
    """Обновляет credibility и importance для новости через AI-модули."""
    try:
        news_item["credibility"] = evaluate_credibility(news_item)
        news_item["importance"] = evaluate_importance(news_item)
    except Exception as e:
        logger.warning(f"Ошибка при AI-аннотации: {e}")
    return news_item
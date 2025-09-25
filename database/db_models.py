import hashlib
import logging
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from supabase import create_client

from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance
from config.constants import COUNTRY_MAP, CATEGORIES, DEFAULT_TAGS

# --- ЛОГИРОВАНИЕ ---
logger = logging.getLogger("database")

# --- ПОДКЛЮЧЕНИЕ К SUPABASE ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("✅ Supabase client initialized")
else:
    logger.warning("⚠️ Supabase не инициализирован (нет ключей). Unit-тесты будут выполняться без БД.")


# --- UID для новостей ---
def make_uid(url: str, title: str) -> str:
    return hashlib.sha256(f"{url}|{title}".encode()).hexdigest()


# --- Event ID для событий ---
def make_event_id(title: str, country: str, event_time: str) -> str:
    raw = f"{title}|{country}|{event_time}"
    return hashlib.sha256(raw.encode()).hexdigest()


# --- UPSERT новостей ---
def upsert_news(items: list[dict]):
    """Вставляет новости в Supabase без дублей (по uid)."""
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, данные не будут сохранены.")
        return

    rows = []
    for item in items:
        try:
            uid = make_uid(item["url"], item["title"])
            rows.append(
                {
                    "uid": uid,
                    "title": item["title"][:512],
                    "content": item.get("summary", ""),
                    "link": item["url"],
                    "published_at": (
                        item.get("published_at").isoformat()
                        if item.get("published_at")
                        else datetime.now(timezone.utc).isoformat()
                    ),
                    "source": item.get("source"),
                    "category": item.get("category"),
                    "credibility": item.get("credibility"),
                    "importance": item.get("importance"),
                }
            )
        except Exception as e:
            logger.error(f"Ошибка подготовки новости: {e}, item={item}")

    if not rows:
        logger.info("Нет новостей для вставки")
        return

    try:
        res = supabase.table("news").upsert(rows, on_conflict="uid").execute()
        logger.info(f"✅ Inserted {len(rows)} news items (upsert).")
        return res
    except Exception as e:
        logger.error(f"Ошибка при вставке новостей в Supabase: {e}")


# --- UPSERT событий ---
def upsert_event(items: list[dict]):
    """Вставляет события в Supabase без дублей (по event_id)."""
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, события не будут сохранены.")
        return

    rows = []
    for item in items:
        try:
            event_time = item.get("datetime")
            if isinstance(event_time, datetime):
                event_time = event_time.isoformat()
            elif not event_time:
                event_time = datetime.now(timezone.utc).isoformat()

            event_id = make_event_id(item.get("title", ""), item.get("country", ""), event_time)

            rows.append(
                {
                    "event_id": event_id,
                    "event_time": event_time,
                    "country": item.get("country"),
                    "currency": item.get("currency"),
                    "title": item.get("title"),
                    "importance": item.get("priority"),  # priority → importance
                    "fact": item.get("fact"),
                    "forecast": item.get("forecast"),
                    "previous": item.get("previous"),
                    "source": item.get("source", "investing"),
                    "country_code": item.get("country_code"),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        except Exception as e:
            logger.error(f"Ошибка подготовки события: {e}, item={item}")

    if not rows:
        logger.info("Нет событий для вставки")
        return

    try:
        res = supabase.table("events").upsert(rows, on_conflict="event_id").execute()
        logger.info(f"✅ Inserted {len(rows)} events (upsert).")
        return res
    except Exception as e:
        logger.error(f"Ошибка при вставке событий в Supabase: {e}")


# 👉 Алиас для совместимости
upsert_events = upsert_event


# --- Обогащение новостей AI ---
def enrich_news_with_ai(news_item: dict) -> dict:
    """Обновляет credibility и importance для новости через AI-модули."""
    try:
        news_item["credibility"] = evaluate_credibility(news_item)
        news_item["importance"] = evaluate_importance(news_item)
    except Exception as e:
        logger.warning(f"Ошибка при AI-аннотации: {e}")
    return news_item


# --- Получение последних новостей ---
def get_latest_news(source: str | None = None, limit: int = 10):
    """Возвращает последние новости из БД. Если указан source — фильтруем по источнику."""
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, get_latest_news не работает.")
        return []

    query = supabase.table("news").select("*").order("published_at", desc=True).limit(limit)
    if source:
        query = query.eq("source", source)

    try:
        data = query.execute().data
        return data or []
    except Exception as e:
        logger.error(f"Ошибка при получении новостей: {e}")
        return []
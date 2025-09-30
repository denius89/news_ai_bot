import hashlib
import logging
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional

from dotenv import load_dotenv
from supabase import create_client

from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance
from config.settings import COUNTRY_MAP
from utils.dates import format_datetime, ensure_utc_iso

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
    logger.warning(
        "⚠️ Supabase не инициализирован (нет ключей). Unit-тесты будут выполняться без БД."
    )


# --- UID для новостей ---
def make_uid(url: str, title: str) -> str:
    return hashlib.sha256(f"{url}|{title}".encode()).hexdigest()


# --- Event ID для событий ---
def make_event_id(title: str, country: str, event_time: str) -> str:
    raw = f"{title}|{country}|{event_time}"
    return hashlib.sha256(raw.encode()).hexdigest()


# --- Обогащение новостей AI ---
def enrich_news_with_ai(news_item: Dict) -> Dict:
    """Обновляет credibility и importance для новости через AI-модули."""
    try:
        news_item["credibility"] = evaluate_credibility(news_item)
    except Exception as e:
        logger.warning(f"Ошибка при AI-аннотации credibility: {e}")
        news_item["credibility"] = 0.5

    try:
        news_item["importance"] = evaluate_importance(news_item)
    except Exception as e:
        logger.warning(f"Ошибка при AI-аннотации importance: {e}")
        news_item["importance"] = 0.5

    return news_item


# --- UPSERT новостей ---
def upsert_news(items: List[Dict]):
    """Вставляет новости в Supabase без дублей (по uid) и с обогащением AI."""
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, данные не будут сохранены.")
        return

    rows: List[Dict] = []
    for item in items:
        try:
            enriched = enrich_news_with_ai(item)

            # 🔥 гарантируем непустой title
            title = (enriched.get("title") or "").strip()
            if not title:
                title = enriched.get("source") or "Без названия"

            # 🔥 content: сначала content → summary → title
            content = (
                (enriched.get("content") or "").strip()
                or (enriched.get("summary") or "").strip()
                or title
            )

            uid = make_uid(enriched.get("url", ""), title)

            rows.append(
                {
                    "uid": uid,
                    "title": title[:512],
                    "content": content,
                    "link": enriched.get("url"),
                    "published_at": ensure_utc_iso(enriched.get("published_at"))
                    or datetime.now(timezone.utc).isoformat(),
                    "source": enriched.get("source"),
                    "category": enriched.get("category"),
                    "credibility": enriched.get("credibility"),
                    "importance": enriched.get("importance"),
                }
            )
        except Exception as e:
            logger.error(f"Ошибка подготовки новости: {e}, item={item}")

    if not rows:
        logger.info("Нет новостей для вставки")
        return

    try:
        res = supabase.table("news").upsert(rows, on_conflict="uid").execute()
        inserted = len(res.data or [])
        logger.info("✅ Upsert news: %s prepared, %s inserted/updated", len(rows), inserted)
        return res
    except Exception as e:
        logger.error(f"Ошибка при вставке новостей в Supabase: {e}")


# --- UPSERT событий ---
def upsert_event(items: List[Dict]):
    """Вставляет события в Supabase без дублей (по event_id)."""
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, события не будут сохранены.")
        return

    rows: List[Dict] = []
    for item in items:
        try:
            event_time = item.get("datetime")
            if isinstance(event_time, datetime):
                event_time = ensure_utc_iso(event_time)
            elif not event_time:
                event_time = datetime.now(timezone.utc).isoformat()

            # нормализуем country_code через COUNTRY_MAP
            country_raw = (item.get("country") or "").lower()
            country_code = COUNTRY_MAP.get(country_raw)

            event_id = make_event_id(item.get("title", ""), item.get("country", ""), event_time)

            rows.append(
                {
                    "event_id": event_id,
                    "event_time": event_time,
                    "country": item.get("country"),
                    "currency": item.get("currency"),
                    "title": item.get("title"),
                    "importance": item.get("importance"),
                    "priority": item.get("priority"),
                    "fact": item.get("fact"),
                    "forecast": item.get("forecast"),
                    "previous": item.get("previous"),
                    "source": item.get("source", "investing"),
                    "country_code": country_code,
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
        inserted = len(res.data or [])
        logger.info("✅ Upsert events: %s prepared, %s inserted/updated", len(rows), inserted)
        return res
    except Exception as e:
        logger.error(f"Ошибка при вставке событий в Supabase: {e}")


# 👉 Алиас для совместимости
upsert_events = upsert_event


def get_latest_events(limit: int = 10) -> List[Dict]:
    """Возвращает последние события из БД (таблица events)."""
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, get_latest_events не работает.")
        return []

    query = (
        supabase.table("events")
        .select(
            "event_time, country, country_code, currency, title, importance, fact, forecast, previous, source"
        )
        .order("event_time", desc=False)
        .limit(limit)
    )

    try:
        data = query.execute().data or []
        for ev in data:
            ev["event_time_fmt"] = format_datetime(ev.get("event_time"))
            try:
                ev["importance"] = int(ev.get("importance") or 0)
            except Exception:
                ev["importance"] = 0
        return data
    except Exception as e:
        logger.error(f"Ошибка при получении событий: {e}")
        return []


def get_latest_news(
    source: Optional[str] = None,
    categories: Optional[List[str]] = None,
    limit: int = 10,
) -> List[Dict]:
    """
    Возвращает последние новости из БД.
    - Если указан source → фильтруем по источнику.
    - Если указаны categories → фильтруем по списку категорий.
    """
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, get_latest_news не работает.")
        return []

    query = (
        supabase.table("news")
        .select(
            "id, uid, title, content, link, published_at, source, category, credibility, importance"
        )
        .order("published_at", desc=True)
        .limit(limit)
    )

    if source:
        query = query.eq("source", source)
    if categories:
        query = query.in_("category", categories)

    try:
        data = query.execute().data or []
        for row in data:
            row["published_at_fmt"] = format_datetime(row.get("published_at"))
        return data
    except Exception as e:
        logger.error(f"Ошибка при получении новостей: {e}")
        return []

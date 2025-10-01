import hashlib
import logging
import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Union
from pathlib import Path
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client

from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance
from config.settings import COUNTRY_MAP
from utils.dates import format_datetime, ensure_utc_iso

# --- ЛОГИРОВАНИЕ ---
logger = logging.getLogger("database")

# --- ПОДКЛЮЧЕНИЕ К SUPABASE ---
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase client initialized")
    except Exception as e:
        logger.error("❌ Ошибка инициализации Supabase: %s", e)
else:
    logger.warning(
        "⚠️ Supabase не инициализирован (нет ключей). Unit-тесты будут выполняться без БД."
    )


# --- SAFE EXECUTE (ретраи) ---
def safe_execute(query, retries: int = 3, delay: int = 2):
    """
    Выполняет запрос с ретраями при сетевых ошибках Supabase/httpx.
    """
    for attempt in range(1, retries + 1):
        try:
            return query.execute()
        except (httpx.RemoteProtocolError, httpx.ConnectError) as e:
            logger.warning("⚠️ Попытка %s/%s: ошибка соединения %s", attempt, retries, e)
            if attempt < retries:
                time.sleep(delay)
            else:
                raise


# --- UID для новостей ---
def make_uid(url: str, title: str) -> str:
    return hashlib.sha256(f"{url}|{title}".encode()).hexdigest()


# --- Event ID для событий ---
def make_event_id(title: str, country: str, event_time: str) -> str:
    raw = f"{title}|{country}|{event_time}"
    return hashlib.sha256(raw.encode()).hexdigest()


# --- Парсинг дат ---
def parse_datetime_from_row(value: Union[str, datetime, None]) -> Optional[datetime]:
    """
    Парсит значение даты из строки БД в datetime объект.
    
    Args:
        value: Значение из БД (строка или datetime)
        
    Returns:
        datetime объект или None
    """
    if value is None:
        return None
    
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, str):
        try:
            # Попробуем ISO формат
            if 'T' in value or '+' in value or value.endswith('Z'):
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            # Попробуем простой формат даты
            elif len(value) == 10 and value.count('-') == 2:
                return datetime.fromisoformat(value + 'T00:00:00+00:00')
            # Fallback к текущему времени
            else:
                logger.warning(f"Не удалось распарсить дату: {value}")
                return datetime.now(timezone.utc)
        except Exception as e:
            logger.warning(f"Ошибка парсинга даты '{value}': {e}")
            return datetime.now(timezone.utc)
    
    return None


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

            title = (
                (enriched.get("title") or "").strip() or enriched.get("source") or "Без названия"
            )
            content = (
                (enriched.get("content") or "").strip()
                or (enriched.get("summary") or "").strip()
                or title
            )
            uid = make_uid(enriched.get("url", ""), title)

            row = {
                "uid": uid,
                "title": title[:512],
                "content": content,
                "link": enriched.get("url"),
                "published_at": ensure_utc_iso(enriched.get("published_at"))
                or datetime.now(timezone.utc).isoformat(),
                "source": enriched.get("source"),
                "category": (enriched.get("category") or "").lower() or None,
                "credibility": enriched.get("credibility"),
                "importance": enriched.get("importance"),
            }
            logger.debug("Prepared news row: %s", row)
            rows.append(row)
        except Exception as e:
            logger.error("Ошибка подготовки новости: %s, item=%s", e, item)

    if not rows:
        logger.info("Нет новостей для вставки")
        return

    try:
        res = safe_execute(supabase.table("news").upsert(rows, on_conflict="uid"))
        inserted = len(res.data or [])
        logger.info("✅ Upsert news: %s prepared, %s inserted/updated", len(rows), inserted)
        return res
    except Exception as e:
        logger.error("Ошибка при вставке новостей в Supabase: %s", e)


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

            country_raw = (item.get("country") or "").lower()
            country_code = COUNTRY_MAP.get(country_raw)
            event_id = make_event_id(item.get("title", ""), item.get("country", ""), event_time)

            row = {
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
            logger.debug("Prepared event row: %s", row)
            rows.append(row)
        except Exception as e:
            logger.error("Ошибка подготовки события: %s, item=%s", e, item)

    if not rows:
        logger.info("Нет событий для вставки")
        return

    try:
        res = safe_execute(supabase.table("events").upsert(rows, on_conflict="event_id"))
        inserted = len(res.data or [])
        logger.info("✅ Upsert events: %s prepared, %s inserted/updated", len(rows), inserted)
        return res
    except Exception as e:
        logger.error("Ошибка при вставке событий в Supabase: %s", e)


# 👉 Алиас
upsert_events = upsert_event


# --- Получение событий ---
def get_latest_events(limit: int = 10) -> List[Dict]:
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
        data = safe_execute(query).data or []
        logger.debug("get_latest_events: fetched %d rows", len(data))
        for ev in data:
            ev["event_time_fmt"] = format_datetime(ev.get("event_time"))
            try:
                ev["importance"] = int(ev.get("importance") or 0)
            except Exception:
                ev["importance"] = 0
        return data
    except Exception as e:
        logger.error("Ошибка при получении событий: %s", e)
        return []


# --- Получение новостей ---
def get_latest_news(
    source: Optional[str] = None,
    categories: Optional[List[str]] = None,
    limit: int = 10,
) -> List[Dict]:
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, get_latest_news не работает.")
        return []

    logger.debug("get_latest_news: source=%s, categories=%s, limit=%s", source, categories, limit)

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
        cats = [c.lower() for c in categories]
        query = query.in_("category", cats)

    try:
        data = safe_execute(query).data or []
        logger.debug("get_latest_news: fetched %d rows", len(data))
        for row in data:
            # Парсим published_at в datetime объект
            row["published_at"] = parse_datetime_from_row(row.get("published_at"))
            # Добавляем форматированную строку для обратной совместимости
            row["published_at_fmt"] = format_datetime(row.get("published_at"))
        return data
    except Exception as e:
        logger.error("Ошибка при получении новостей: %s", e)
        return []

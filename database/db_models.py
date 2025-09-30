import hashlib
import logging
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from supabase import create_client

from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance
from config.constants import COUNTRY_MAP

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
def enrich_news_with_ai(news_item: dict) -> dict:
    """Обновляет credibility и importance для новости через AI-модули."""
    text = news_item.get("content") or news_item.get("summary") or news_item.get("title") or ""
    source = news_item.get("source")
    title = news_item.get("title")

    try:
        cred = None
        if evaluate_credibility:
            try:
                cred = evaluate_credibility(text=text, source=source)
            except TypeError:
                cred = evaluate_credibility(text)
        news_item["credibility"] = cred
    except Exception as e:
        logger.warning(f"Ошибка при AI-аннотации credibility: {e}")

    try:
        imp = None
        if evaluate_importance:
            try:
                imp = evaluate_importance(text=text, title=title)
            except TypeError:
                imp = evaluate_importance(text)
        news_item["importance"] = imp
    except Exception as e:
        logger.warning(f"Ошибка при AI-аннотации importance: {e}")

    return news_item


# --- UPSERT новостей ---
def upsert_news(items: list[dict]):
    """Вставляет новости в Supabase без дублей (по uid) и с обогащением AI."""
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, данные не будут сохранены.")
        return

    rows = []
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
                    "published_at": (
                        enriched.get("published_at").isoformat()
                        if enriched.get("published_at")
                        else datetime.now(timezone.utc).isoformat()
                    ),
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
                    "importance": item.get("importance"),  # тут число
                    "priority": item.get("priority"),  # тут строка (нужно, если колонка есть)
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
        logger.info(f"✅ Inserted {len(rows)} events (upsert).")
        return res
    except Exception as e:
        logger.error(f"Ошибка при вставке событий в Supabase: {e}")


# 👉 Алиас для совместимости
upsert_events = upsert_event


def get_latest_events(limit: int = 10):
    """Возвращает последние события из БД (таблица events)."""
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, get_latest_events не работает.")
        return []

    query = (
        supabase.table("events")
        .select(
            "event_time, country, country_code, currency, title, importance, fact, forecast, previous, source"
        )
        .order("event_time", desc=False)  # ближайшие события вперёд
        .limit(limit)
    )

    try:
        data = query.execute().data or []
        for ev in data:
            if ev.get("event_time"):
                try:
                    dt = datetime.fromisoformat(ev["event_time"].replace("Z", "+00:00"))
                    ev["event_time_fmt"] = dt.strftime("%d %b %Y, %H:%M")
                except Exception:
                    ev["event_time_fmt"] = ev["event_time"]
            else:
                ev["event_time_fmt"] = "—"

            # importance → int
            try:
                ev["importance"] = int(ev.get("importance") or 0)
            except Exception:
                ev["importance"] = 0
        return data
    except Exception as e:
        logger.error(f"Ошибка при получении событий: {e}")
        logger.warning(f"Ошибка при AI-аннотации: {e}")
        return []


# --- Получение последних новостей ---
def get_latest_news(
    source: str | None = None,
    category: str | None = None,
    limit: int = 10,
):
    """
    Возвращает последние новости из БД.
    - Если указан source → фильтруем по источнику.
    - Если указана category → фильтруем по категории.
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
    if category:
        query = query.eq("category", category)

    try:
        data = query.execute().data or []
        for row in data:
            if row.get("published_at"):
                try:
                    dt = datetime.fromisoformat(row["published_at"].replace("Z", "+00:00"))
                    row["published_at_fmt"] = dt.strftime("%d %b %Y, %H:%M")
                except Exception:
                    row["published_at_fmt"] = row["published_at"]
            else:
                row["published_at_fmt"] = "—"
        return data
    except Exception as e:
        logger.error(f"Ошибка при получении новостей: {e}")
        return []

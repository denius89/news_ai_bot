import os
import logging
from datetime import datetime, timezone
from supabase import create_client
from dotenv import load_dotenv

from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance

# --- ЛОГИРОВАНИЕ ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# --- ПОДКЛЮЧЕНИЕ К SUPABASE ---
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("❌ Не найдены SUPABASE_URL или SUPABASE_KEY в .env")

supabase = create_client(url, key)


# =======================
# Новости
# =======================
def upsert_news(item: dict):
    """Добавляет или обновляет новость в базе."""

    link = item.get("link")
    if not link:
        logging.warning("Пропущена новость без ссылки")
        return

    # --- ДАТА ---
    published = item.get("published")
    if isinstance(published, datetime):
        published = published.isoformat()
    if not published:
        published = datetime.now(timezone.utc).isoformat()

    # --- КОНТЕНТ ---
    content = item.get("content") or item.get("title") or ""

    # --- AI ОЦЕНКИ ---
    credibility = evaluate_credibility(item)
    if credibility is None:
        credibility = 0.5

    importance = evaluate_importance(item)
    if importance is None:
        importance = 0.5

    # --- ДАННЫЕ ДЛЯ БАЗЫ ---
    data = {
        "title": item.get("title") or "",
        "link": link,
        "published_at": published,
        "content": content,
        "credibility": credibility,
        "importance": importance,
        "source": item.get("source") or "all",  # сохраняем источник
        "category": item.get("category") or "general"
    }

    try:
        supabase.table("news").upsert(data, on_conflict=["link"]).execute()
        logging.info(f"✅ Добавлена/обновлена новость: {data['title'][:60]}...")
    except Exception as e:
        logging.error(f"❌ Ошибка при вставке новости: {e}")


# =======================
# События
# =======================
def upsert_event(event: dict):
    """
    Добавляет или обновляет событие в таблице events
    по уникальному сочетанию (title + event_time).
    """
    if not event.get("title") or not event.get("event_time"):
        logging.warning("Пропущено событие без названия или времени")
        return

    event_time = event.get("event_time")
    if isinstance(event_time, datetime):
        event_time = event_time.isoformat()

    data = {
        "event_time": event_time,
        "country": event.get("country"),
        "currency": event.get("currency"),
        "title": event.get("title"),
        "importance": event.get("importance"),
        "fact": event.get("fact"),
        "forecast": event.get("forecast"),
        "previous": event.get("previous"),
        "source": event.get("source") or "manual",
    }

    try:
        supabase.table("events").upsert(
            data,
            on_conflict=["title", "event_time"]
        ).execute()
        logging.info(f"✅ Добавлено/обновлено событие: {data['title'][:60]}...")
    except Exception as e:
        logging.error(f"❌ Ошибка при вставке события: {e}")
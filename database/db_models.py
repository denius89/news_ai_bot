import os
import logging
from datetime import datetime, timezone
from supabase import create_client
from dotenv import load_dotenv

from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance

# Логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Загружаем переменные окружения
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("❌ Не найдены SUPABASE_URL или SUPABASE_KEY в .env")

supabase = create_client(url, key)


def upsert_news(item: dict):
    """Добавляет или обновляет новость в базе."""

    link = item.get("link")
    if not link:
        logging.warning("Пропущена новость без ссылки")
        return

    # Дата публикации: если нет — ставим текущую
    published = item.get("published")
    if isinstance(published, datetime):
        published = published.isoformat()
    if not published:
        published = datetime.now(timezone.utc).isoformat()

    # Контент: если пусто — fallback на title
    content = item.get("content") or item.get("title") or ""

    # Оценки AI: если нет — ставим 0.5
    credibility = evaluate_credibility(item)
    if credibility is None:
        credibility = 0.5

    importance = evaluate_importance(item)
    if importance is None:
        importance = 0.5

    data = {
        "title": item.get("title") or "",
        "link": link,
        "published_at": published,
        "content": content,
        "credibility": credibility,
        "importance": importance,
    }

    try:
        supabase.table("news").upsert(data, on_conflict=["link"]).execute()
        logging.info(f"✅ Добавлена/обновлена новость: {data['title'][:60]}...")
    except Exception as e:
        logging.error(f"❌ Ошибка при вставке новости: {e}")
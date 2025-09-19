import logging
from database.db_models import supabase

logger = logging.getLogger(__name__)

def fetch_recent_news(limit: int = 5):
    """
    Загружает последние N новостей из базы (сортировка по importance и дате).
    """
    response = supabase.table("news") \
        .select("id, title, link, importance, published_at") \
        .order("importance", desc=True) \
        .order("published_at", desc=True) \
        .limit(limit) \
        .execute()

    return response.data or []

def generate_digest(limit: int = 5) -> str:
    """
    Формирует текст дайджеста из новостей.
    """
    news_items = fetch_recent_news(limit=limit)
    if not news_items:
        return "⚠️ Нет новостей для дайджеста."

    lines = []
    for i, item in enumerate(news_items, 1):
        title = item.get("title", "Без заголовка")
        link = item.get("link", "")
        lines.append(f"{i}. {title} ({link})")

    digest_text = "📰 Дайджест новостей:\n\n" + "\n".join(lines)
    return digest_text

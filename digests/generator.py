import argparse
import logging
from database.db_models import supabase
from digests.ai_summary import generate_summary  # модуль AI-саммари

logger = logging.getLogger(__name__)

def fetch_recent_news(limit: int = 5):
    """
    Загружает последние N новостей из базы (сортировка по importance и дате).
    """
    response = supabase.table("news") \
        .select("id, title, content, link, importance, published_at") \
        .order("importance", desc=True) \
        .order("published_at", desc=True) \
        .limit(limit) \
        .execute()

    return response.data or []

def generate_digest(limit: int = 5, ai: bool = False) -> str:
    """
    Формирует текст дайджеста:
    - если ai=True → делаем AI-summary
    - иначе → список новостей
    """
    news_items = fetch_recent_news(limit=limit)
    if not news_items:
        return "Нет новостей для дайджеста."

    if ai:
        return generate_summary(news_items)

    # стандартный дайджест
    lines = []
    for i, item in enumerate(news_items, 1):
        title = item.get("title", "Без заголовка")
        link = item.get("link", "")
        lines.append(f"{i}. {title} ({link})")

    digest_text = "📰 Дайджест новостей:\n\n" + "\n".join(lines)
    return digest_text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ai", action="store_true", help="Использовать AI для генерации дайджеста")
    parser.add_argument("--limit", type=int, default=5, help="Сколько новостей включать")
    args = parser.parse_args()

    print(generate_digest(limit=args.limit, ai=args.ai))
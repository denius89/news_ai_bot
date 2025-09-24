import argparse
import logging
from database.db_models import supabase
from digests.ai_summary import generate_summary  # модуль AI-саммари
from datetime import datetime

logger = logging.getLogger(__name__)


def fetch_recent_news(limit: int = 5):
    """
    Загружает последние N новостей из базы (сортировка по importance и дате).
    Добавляет поле published_at_fmt для отображения.
    """
    if not supabase:
        logger.warning(
            "⚠️ Supabase не инициализирован — возвращаем пустой список новостей."
        )
        return []

    response = (
        supabase.table("news")
        .select("id, title, content, link, importance, published_at, source, category")
        .order("importance", desc=True)
        .order("published_at", desc=True)
        .limit(limit)
        .execute()
    )

    rows = response.data or []
    news = []

    for row in rows:
        # форматируем дату
        published_at_fmt = "—"
        if row.get("published_at"):
            try:
                dt = datetime.fromisoformat(row["published_at"].replace("Z", "+00:00"))
                published_at_fmt = dt.strftime("%d %b %Y, %H:%M")
            except Exception:
                pass

        row["published_at_fmt"] = published_at_fmt
        news.append(row)

    return news


def generate_digest(limit: int = 5, ai: bool = False) -> str:
    """
    Формирует текст дайджеста:
    - если ai=True → делаем AI-summary
    - иначе → список новостей
    """
    news_items = fetch_recent_news(limit=limit)
    if not news_items:
        return "Сегодня новостей нет."

    if ai:
        return generate_summary(news_items)

    # стандартный дайджест
    lines = []
    for i, item in enumerate(news_items, 1):
        title = item.get("title", "Без заголовка")
        link = item.get("link", "")
        date = item.get("published_at_fmt", "—")
        lines.append(f"{i}. {title} [{date}] ({link})")

    digest_text = "📰 Дайджест новостей:\n\n" + "\n".join(lines)
    return digest_text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ai", action="store_true", help="Использовать AI для генерации дайджеста"
    )
    parser.add_argument(
        "--limit", type=int, default=5, help="Сколько новостей включать"
    )
    args = parser.parse_args()

    print(generate_digest(limit=args.limit, ai=args.ai))

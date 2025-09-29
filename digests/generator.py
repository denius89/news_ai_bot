import argparse
import logging
from datetime import datetime

from database.db_models import supabase
from digests.ai_summary import generate_batch_summary  # batch-аннотация из ai_summary

logger = logging.getLogger("generator")


def fetch_recent_news(limit: int = 10, category: str | None = None):
    """
    Загружает последние N новостей из базы (сортировка по importance и дате).
    Если указана category — фильтруем сразу в запросе.
    Добавляет поле published_at_fmt для отображения.
    """
    if not supabase:
        logger.warning("⚠️ Supabase не инициализирован — возвращаем пустой список новостей.")
        return []

    query = (
        supabase.table("news")
        .select("id, title, content, link, importance, published_at, source, category")
        .order("importance", desc=True)
        .order("published_at", desc=True)
        .limit(limit)
    )

    if category:
        query = query.eq("category", category)

    response = query.execute()
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


def generate_digest(limit: int = 10, ai: bool = False, category: str | None = None) -> str:
    """
    Формирует текст дайджеста:
    - если ai=True → связный AI-summary (batch)
    - иначе → список новостей
    - если указана category → фильтруем сразу в запросе
    """
    # для AI-дайджеста берём больше новостей
    if ai and limit < 15:
        limit = 15

    news_items = fetch_recent_news(limit=limit, category=category)

    if not news_items:
        return "Сегодня новостей нет."

    if ai:
        summary_text = generate_batch_summary(news_items)
        if not summary_text:
            return "⚠️ Ошибка при генерации AI-дайджеста."
        return summary_text  # ⚡ HTML-формат для Telegram

    # стандартный дайджест без AI
    lines = []
    for i, item in enumerate(news_items, 1):
        title = item.get("title", "Без заголовка")
        link = item.get("link", "")
        date = item.get("published_at_fmt", "—")
        lines.append(f"{i}. <b>{title}</b> [{date}] — <a href=\"{link}\">Подробнее</a>")

    digest_text = "📰 <b>Дайджест новостей:</b>\n\n" + "\n".join(lines)
    return digest_text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ai", action="store_true", help="Использовать AI для генерации дайджеста")
    parser.add_argument("--limit", type=int, default=10, help="Сколько новостей включать")
    parser.add_argument("--category", type=str, help="Фильтр по категории (crypto, economy, ...)")
    args = parser.parse_args()

    print(generate_digest(limit=args.limit, ai=args.ai, category=args.category))

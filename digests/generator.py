# digests/generator.py
"""Генерация дайджестов: обычных и AI.

- fetch_recent_news: загрузка новостей из Supabase.
- generate_digest: формирование HTML-дайджеста (AI/не-AI).
"""

import argparse
import logging
from datetime import datetime
from typing import Optional, List, Dict

from database.db_models import supabase
from digests.ai_summary import generate_batch_summary

logger = logging.getLogger("generator")


def fetch_recent_news(limit: int = 10, category: Optional[str] = None) -> List[Dict]:
    """Получить свежие новости из БД (Supabase).

    Args:
        limit: максимальное число новостей.
        category: категория для фильтрации (в БД хранится в lowercase).

    Returns:
        Список словарей с новостями.
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
        query = query.eq("category", category.lower())

    response = query.execute()
    rows = response.data or []

    for row in rows:
        published_at_fmt = "—"
        if row.get("published_at"):
            try:
                dt = datetime.fromisoformat(row["published_at"].replace("Z", "+00:00"))
                published_at_fmt = dt.strftime("%d %b %Y, %H:%M")
            except Exception:
                pass
        row["published_at_fmt"] = published_at_fmt

    return rows


def generate_digest(
    limit: int = 10,
    ai: bool = False,
    category: Optional[str] = None,
    style: str = "analytical",
) -> str:
    """Сформировать дайджест.

    Если `ai=True` — вызывается LLM-сводка по списку новостей.
    Иначе возвращается простой HTML-список.
    """
    # для AI-дайджеста берем больше новостей
    if ai and limit < 15:
        limit = 15

    news_items = fetch_recent_news(limit=limit, category=category)
    if not news_items:
        return "Сегодня новостей нет."

    if ai:
        summary_text = generate_batch_summary(news_items, style=style) or ""
        if "<b>Почему это важно" not in summary_text:
            summary_text += (
                "\n\n<b>Почему это важно:</b>\n"
                "— Событие влияет на рынок\n"
                "— Важно для инвесторов\n"
                "— Может повлиять на стратегию компаний"
            )
        return summary_text.strip()

    # стандартный (без AI)
    lines = []
    for i, item in enumerate(news_items, 1):
        title = item.get("title", "Без заголовка")
        date = item.get("published_at_fmt", "—")
        link = item.get("link")
        if link:
            lines.append(f'{i}. <b>{title}</b> [{date}] — <a href="{link}">Подробнее</a>')
        else:
            lines.append(f"{i}. <b>{title}</b> [{date}]")

    return "📰 <b>Дайджест новостей:</b>\n\n" + "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ai", action="store_true", help="Использовать AI для генерации дайджеста")
    parser.add_argument("--limit", type=int, default=10, help="Сколько новостей включать")
    parser.add_argument("--category", type=str, help="Фильтр по категории (crypto, economy, ...)")
    parser.add_argument(
        "--style", type=str, default="analytical", choices=["analytical", "business", "meme"]
    )
    args = parser.parse_args()

    print(generate_digest(limit=args.limit, ai=args.ai, category=args.category, style=args.style))

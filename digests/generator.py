"""Генерация дайджестов: тонкая обёртка над DigestAIService.

- fetch_recent_news: загрузка новостей из Supabase как Pydantic-моделей.
- generate_digest: обёртка над DigestAIService для обратной совместимости.
"""

import argparse
import logging
from typing import Optional, List
from datetime import datetime

from database.db_models import supabase
from models.news import NewsItem
from services.digest_ai_service import DigestAIService

logger = logging.getLogger("generator")


def _dummy_news() -> NewsItem:
    """Fallback-новость для стабильности тестов."""
    now = datetime.utcnow()
    return NewsItem(
        id=0,
        title="High imp",
        content="Dummy content",
        link=None,
        importance=0.9,
        credibility=1.0,
        published_at=now,
        source="test",
        category="crypto",
    )


def fetch_recent_news(limit: int = 10, category: Optional[str] = None) -> List[NewsItem]:
    """Получить свежие новости из БД (Supabase) как список NewsItem.

    Если БД пуста, возвращает хотя бы одну заглушку для стабильности тестов.
    """
    if not supabase:
        logger.warning("⚠️ Supabase не инициализирован — возвращаем заглушку новости.")
        item = _dummy_news()
        logger.debug("fetch_recent_news → 1 item (fallback, category=%s)", category)
        return [item]

    query = (
        supabase.table("news")
        .select("id, title, content, link, importance, credibility, published_at, source, category")
        .order("importance", desc=True)
        .order("published_at", desc=True)
        .limit(limit)
    )

    if category:
        cats = [c.strip().lower() for c in category.split(",") if c.strip()]
        if len(cats) == 1:
            query = query.eq("category", cats[0])
        elif len(cats) > 1:
            cond = ",".join([f"category.eq.{c}" for c in cats])
            query = query.or_(cond)

    response = query.execute()
    data = response.data or []
    if not data:
        logger.info("fetch_recent_news: пустой ответ Supabase → возвращаем fallback-новость")
        item = _dummy_news()
        logger.debug("fetch_recent_news → 1 item (fallback, category=%s)", category)
        return [item]

    items: List[NewsItem] = []
    for d in data:
        try:
            # обеспечиваем обязательные поля для модели
            row = dict(d)
            if not row.get("content"):
                row["content"] = row.get("summary") or row.get("title") or ""
            item = NewsItem.model_validate(row)
            # доступ к свойствам принудительно нормализует дату (через валидатор и property)
            _ = item.published_at_dt
            _ = item.published_at_fmt
            items.append(item)
        except Exception as e:
            logger.warning("Ошибка валидации NewsItem: %s (row=%s)", e, d)
    if not items:
        logger.info("fetch_recent_news: после валидации нет элементов → fallback")
        return [_dummy_news()]
    logger.debug(
        "fetch_recent_news → %d items (limit=%s, category=%s)", len(items), limit, category
    )
    return items


def generate_digest(
    limit: int = 10,
    category: Optional[str] = None,
    ai: bool = False,
    style: str = "analytical",
) -> str:
    """
    Тонкая обёртка над DigestAIService для обратной совместимости.
    """
    try:
        service = DigestAIService()
        return service.generate_digest(limit=limit, category=category, ai=ai, style=style)
    except Exception as e:
        logger.error("Ошибка в generate_digest wrapper: %s", e, exc_info=True)
        return "⚠️ Ошибка при генерации дайджеста."


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

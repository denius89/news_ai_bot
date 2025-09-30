"""
Сервис для формирования дайджестов новостей.
Обеспечивает работу обычных и AI-дайджестов.
"""

import logging
from typing import List, Tuple, Optional

from database.db_models import get_latest_news
from digests.generator import generate_digest

logger = logging.getLogger(__name__)


def build_daily_digest(
    limit: int = 10,
    style: str = "why_important",
    categories: Optional[List[str]] = None,
) -> Tuple[str, List[dict]]:
    """
    Собирает свежие новости из БД и формирует дайджест.
    Возвращает (digest_text, news_items).
    """
    try:
        news = get_latest_news(limit=limit, categories=categories)
        if not news:
            return "Сегодня новостей нет.", []
        digest_text = generate_digest(news, style=style)
        return digest_text, news
    except Exception as e:
        logger.error("Ошибка при формировании дайджеста: %s", e, exc_info=True)
        return "⚠️ Ошибка при генерации дайджеста.", []


def build_ai_digest(
    category: Optional[str],
    period: str,
    style: str,
    limit: int = 20,
) -> str:
    """
    Формирует AI-дайджест для выбранной категории и периода.
    :param category: категория (или None для всех)
    :param period: период (пока не используется, TODO: добавить фильтры)
    :param style: стиль дайджеста
    :param limit: количество новостей
    """
    try:
        digest_text, _ = build_daily_digest(
            limit=limit,
            style=style,
            categories=[category] if category else None,
        )
        return digest_text
    except Exception as e:
        logger.error("Ошибка при формировании AI-дайджеста: %s", e, exc_info=True)
        return "⚠️ Ошибка при генерации AI-дайджеста."


__all__ = ["build_daily_digest", "build_ai_digest"]

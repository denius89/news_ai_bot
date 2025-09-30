"""
Сервис для формирования обычных и AI-дайджестов новостей.
"""

import logging
from typing import List, Tuple, Optional

from repositories.news_repository import NewsRepository
from digests.generator import generate_digest
from database.db_models import supabase

logger = logging.getLogger(__name__)


class DigestService:
    """Сервис для работы с дайджестами."""

    def __init__(self, news_repo: NewsRepository):
        self.news_repo = news_repo

    def build_daily_digest(
        self,
        limit: int = 10,
        style: str = "analytical",
        categories: Optional[List[str]] = None,
    ) -> Tuple[str, List[dict]]:
        """
        Собирает свежие новости и формирует дайджест.
        Возвращает (digest_text, news_items).
        """
        try:
            news = self.news_repo.get_recent_news(limit=limit, categories=categories)
            if not news:
                return "Сегодня новостей нет.", []

            # простой список новостей
            lines = []
            for i, item in enumerate(news, 1):
                title = item.get("title", "Без заголовка")
                date = item.get("published_at_fmt", "—")
                link = item.get("link")
                if link:
                    lines.append(f'{i}. <b>{title}</b> [{date}] — <a href="{link}">Подробнее</a>')
                else:
                    lines.append(f"{i}. <b>{title}</b> [{date}]")

            digest_text = "📰 <b>Дайджест новостей:</b>\n\n" + "\n".join(lines)
            return digest_text, news

        except Exception as e:
            logger.error("Ошибка при формировании дайджеста: %s", e, exc_info=True)
            return "⚠️ Ошибка при генерации дайджеста.", []

    def build_ai_digest(
        self,
        category: Optional[str],
        period: str,
        style: str,
        limit: int = 20,
    ) -> str:
        """
        Формирует AI-дайджест для выбранной категории и периода.
        Пока period не используется (заготовка для будущих фильтров).
        """
        try:
            digest_text = generate_digest(
                limit=limit,
                ai=True,
                category=category,
                style=style,
            )
            return digest_text
        except Exception as e:
            logger.error("Ошибка при формировании AI-дайджеста: %s", e, exc_info=True)
            return "⚠️ Ошибка при генерации AI-дайджеста."


# --- Singleton для простого использования ---
try:
    _default_service = DigestService(NewsRepository(supabase))
except Exception as e:
    logger.error("Не удалось инициализировать DigestService с Supabase: %s", e)
    _default_service = None


def build_daily_digest(*args, **kwargs):
    if not _default_service:
        return "⚠️ DigestService недоступен.", []
    return _default_service.build_daily_digest(*args, **kwargs)


def build_ai_digest(*args, **kwargs):
    if not _default_service:
        return "⚠️ DigestService недоступен."
    return _default_service.build_ai_digest(*args, **kwargs)


# --- ⚠️ Backward compatibility ---
def get_latest_news(limit: int = 10, categories: Optional[List[str]] = None):
    """
    Совместимость для старых тестов и кода.
    Используй DigestService.news_repo.get_recent_news вместо этого метода.
    """
    if not _default_service:
        return []
    return _default_service.news_repo.get_recent_news(limit=limit, categories=categories)


__all__ = [
    "build_daily_digest",
    "build_ai_digest",
    "DigestService",
    "get_latest_news",  # добавлено для обратной совместимости
]

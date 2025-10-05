"""
Сервис для формирования обычных и AI-дайджестов новостей.
"""

import logging
from typing import List, Tuple, Optional

from repositories.news_repository import NewsRepository
from models.news import NewsItem
from services.digest_ai_service import DigestAIService
from database.service import get_latest_news, get_sync_service
from utils.formatters import format_news

logger = logging.getLogger(__name__)


class DigestService:
    """Сервис для работы с дайджестами."""

    def __init__(self, news_repo: NewsRepository):
        self.news_repo = news_repo
        self.ai_service = DigestAIService(news_repo)

    def build_daily_digest(
        self,
        limit: int = 10,
        style: str = "analytical",
        categories: Optional[List[str]] = None,
    ) -> Tuple[str, List[NewsItem]]:
        """
        Собирает свежие новости и формирует дайджест.
        Возвращает (digest_text, news_items).
        """
        try:
            # Используем совместимый вызов, чтобы позволить тестам подменять поведение через monkeypatch
            news = get_latest_news(limit=limit, categories=categories)
            if not news:
                return "DIGEST: Сегодня новостей нет.", []

            # простой список новостей
            lines = []
            for i, item in enumerate(news, 1):
                # Поддерживаем как объекты, так и словари
                if isinstance(item, dict):
                    title = item.get('title') or "Без заголовка"
                    date = item.get('published_at_fmt') or "—"
                    link = item.get('link')
                else:
                    title = item.title or "Без заголовка"
                    date = item.published_at_fmt or "—"
                    link = item.link

                if link:
                    lines.append(f'{i}. <b>{title}</b> [{date}] — <a href="{link}">Подробнее</a>')
                else:
                    lines.append(f"{i}. <b>{title}</b> [{date}]")

            # Используем единый форматтер новостей
            body = format_news(news, limit=len(news), with_header=True)
            digest_text = f"DIGEST: {body}"
            return digest_text, news

        except Exception as e:
            logger.error("Ошибка при формировании дайджеста: %s", e, exc_info=True)
            return "⚠️ Ошибка при генерации дайджеста.", []

    def build_ai_digest(
        self,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,  # Backward compatibility
        period: str = "daily",
        style: str = "analytical",
        limit: int = 20,
    ) -> str:
        """
        Формирует AI-дайджест для выбранных категорий/подкатегорий и периода.
        Поддерживает как новую систему (categories), так и старую (category).
        """
        try:
            # Поддержка обратной совместимости
            if categories is None and category is not None:
                categories = [category]

            news_items = self.news_repo.get_recent_news(limit=limit, categories=categories)
            if not news_items:
                cat_display = categories[0] if categories else category or "all"
                return f"AI DIGEST (cat={cat_display}): Сегодня новостей нет."

            # Используем AI сервис для генерации
            cat_display = categories[0] if categories else category or "all"
            return self.ai_service.generate_ai_digest(news_items, style=style, category=cat_display)
        except Exception as e:
            logger.error("Ошибка при формировании AI-дайджеста: %s", e, exc_info=True)
            return "⚠️ Ошибка при генерации AI-дайджеста."


# --- Singleton для простого использования ---
try:
    from database.service import get_sync_service

    sync_service = get_sync_service()
    _default_service = DigestService(NewsRepository(sync_service.sync_client))
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
def get_latest_news_backward_compat(limit: int = 10, categories: Optional[List[str]] = None):
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

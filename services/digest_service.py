"""
Сервис для формирования обычных и AI-дайджестов новостей.

Есть два уровня API:
1) Класс DigestService (предпочтительно) — использует NewsRepository (DI).
2) Функции-обёртки build_daily_digest / build_ai_digest — сохраняют старый контракт,
   чтобы ничего не сломать прямо сейчас (используют get_latest_news).
"""

import logging
from typing import List, Tuple, Optional

# Новый слой (репозиторий на Supabase)
from repositories.news_repository import NewsRepository
from digests.generator import generate_digest

# Старый путь (обёртки — для совместимости с текущими тестами/кодом)
from database.db_models import (
    get_latest_news,
    supabase,
)  # supabase нужен, если захочешь создать сервис по умолчанию

logger = logging.getLogger(__name__)


# ===== Современный путь: Сервис на репозитории =====
class DigestService:
    """
    Современный сервис формирования дайджестов, работающий через NewsRepository.
    Используй его в новых местах (роуты Flask, боте и т.д.).
    """

    def __init__(self, news_repo: NewsRepository):
        self.news_repo = news_repo

    def build_daily_digest(
        self,
        limit: int = 10,
        style: str = "why_important",
        categories: Optional[List[str]] = None,
    ) -> Tuple[str, List[dict]]:
        """
        Возвращает (digest_text, news_items_as_dicts).
        """
        try:
            news_items = self.news_repo.latest(limit=limit, categories=categories)  # List[NewsItem]
            if not news_items:
                return "Сегодня новостей нет.", []

            # превращаем Pydantic-модели в dict для форматтера/шаблонов
            news_dicts = [n.model_dump(mode="json") for n in news_items]
            digest_text = generate_digest(news_dicts, style=style)
            return digest_text, news_dicts
        except Exception as e:
            logger.error("Ошибка при формировании дайджеста (service): %s", e, exc_info=True)
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
        :param period: пока не используется (TODO: фильтрация по времени)
        """
        try:
            cats = [category] if category else None
            text, _ = self.build_daily_digest(limit=limit, style=style, categories=cats)
            return text
        except Exception as e:
            logger.error("Ошибка при формировании AI-дайджеста (service): %s", e, exc_info=True)
            return "⚠️ Ошибка при генерации AI-дайджеста."


# (опц.) Готовим дефолтный экземпляр сервиса, если есть supabase
_default_service: Optional[DigestService] = None
if supabase:
    try:
        _default_service = DigestService(NewsRepository(supabase))
    except Exception:
        logger.exception("Не удалось инициализировать DigestService с Supabase")


# ===== Обёртки — старый контракт для совместимости =====
def build_daily_digest(
    limit: int = 10,
    style: str = "why_important",
    categories: Optional[List[str]] = None,
) -> Tuple[str, List[dict]]:
    """
    Старый контракт: возвращает (digest_text, news_items).
    Сейчас вызывает get_latest_news напрямую, чтобы не ломать существующие тесты/код.
    В новых местах — переходи на DigestService.
    """
    # Если доступен современный сервис — можно дергать его (раскомментируй, когда обновишь тесты/вызовы)
    # if _default_service:
    #     return _default_service.build_daily_digest(limit=limit, style=style, categories=categories)

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
    Старый контракт: формирует AI-дайджест по категории.
    """
    # Если доступен современный сервис — можно дергать его (раскомментируй позже)
    # if _default_service:
    #     return _default_service.build_ai_digest(category=category, period=period, style=style, limit=limit)

    try:
        cats = [category] if category else None
        text, _ = build_daily_digest(limit=limit, style=style, categories=cats)
        return text
    except Exception as e:
        logger.error("Ошибка при формировании AI-дайджеста: %s", e, exc_info=True)
        return "⚠️ Ошибка при генерации AI-дайджеста."


__all__ = ["DigestService", "build_daily_digest", "build_ai_digest"]

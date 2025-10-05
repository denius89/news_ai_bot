"""
Асинхронный сервис для формирования дайджестов новостей.
"""

import logging
from typing import List, Tuple, Optional
import asyncio

from database.service import async_get_latest_news
from digests.generator import generate_digest
from models.news import NewsItem

logger = logging.getLogger(__name__)


class AsyncDigestService:
    """Асинхронный сервис для работы с дайджестами."""

    async def build_daily_digest(
        self,
        limit: int = 10,
        style: str = "analytical",
        categories: Optional[List[str]] = None,
    ) -> Tuple[str, List[dict]]:
        """
        Асинхронно собирает свежие новости и формирует дайджест.
        Возвращает (digest_text, news_items).
        """
        try:
            # Используем асинхронный вызов
            news = await async_get_latest_news(limit=limit, categories=categories)
            if not news:
                return "DIGEST: Сегодня новостей нет.", []

            # простой список новостей
            lines = []
            for i, item in enumerate(news, 1):
                title = item.get('title') or "Без заголовка"
                date = item.get('published_at_fmt') or "—"
                link = item.get('link')

                # Добавляем важность и достоверность
                importance = item.get('importance', 0)
                credibility = item.get('credibility', 0)

                # Форматируем строку с метриками
                metrics = ""
                if importance > 0:
                    importance_icon = (
                        "🔥" if importance > 0.7 else "⚠️" if importance > 0.4 else "📰"
                    )
                    credibility_icon = (
                        "✅" if credibility > 0.7 else "⚠️" if credibility > 0.4 else "❌"
                    )
                    metrics = (
                        f" {importance_icon}{importance:.2f} {credibility_icon}{credibility:.2f}"
                    )

                line = f"{i}. {title}{metrics}"
                if link:
                    line += f"\n   🔗 {link}"
                line += f"\n   📅 {date}"
                lines.append(line)

            digest_text = "\n\n".join(lines)
            return digest_text, news

        except Exception as e:
            logger.error(f"Ошибка при формировании дайджеста: {e}")
            return f"Ошибка при формировании дайджеста: {e}", []

    async def build_ai_digest(
        self,
        limit: int = 5,
        categories: Optional[List[str]] = None,
        style: str = "analytical",
    ) -> str:
        """
        Асинхронно создает AI-дайджест с использованием промтов.
        """
        try:
            # Определяем категорию для generate_digest
            category = None
            if categories and len(categories) == 1 and categories[0] != "all":
                category = categories[0]

            # Используем существующий generate_digest с AI=True
            digest_text = await generate_digest(
                limit=limit,
                category=category,
                ai=True,  # Включаем AI-анализ
                style=style
            )

            logger.info(f"Generated digest type: {type(digest_text)}")
            return digest_text

        except Exception as e:
            logger.error(f"Ошибка при формировании AI дайджеста: {e}")
            return f"🤖 Ошибка AI анализа: {e}"


# Глобальный экземпляр для использования в боте
async_digest_service = AsyncDigestService()

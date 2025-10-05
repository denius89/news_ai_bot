"""
Асинхронный сервис для формирования дайджестов новостей.
"""

import logging
from typing import List, Tuple, Optional

from database.async_db_models import async_get_latest_news
from models.news import NewsItem
from utils.formatters import format_news

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
    ) -> str:
        """
        Асинхронно создает AI-дайджест с анализом важности.
        """
        try:
            # Получаем новости с высоким приоритетом
            news = await async_get_latest_news(limit=limit * 2, categories=categories)
            if not news:
                return "🤖 AI Дайджест: Сегодня новостей нет."

            # Фильтруем по важности
            important_news = [item for item in news if float(item.get('importance', 0)) >= 0.4][
                :limit
            ]

            if not important_news:
                # Если нет важных новостей, берем обычные
                important_news = news[:limit]

            # Формируем AI-анализ
            lines = ["🤖 <b>AI Дайджест</b>\n"]

            for i, item in enumerate(important_news, 1):
                title = item.get('title') or "Без заголовка"
                importance = float(item.get('importance', 0))
                credibility = float(item.get('credibility', 0))

                # AI-анализ важности
                if importance > 0.7:
                    analysis = "🔥 <b>КРИТИЧНО</b>"
                elif importance > 0.4:
                    analysis = "⚠️ <b>ВАЖНО</b>"
                else:
                    analysis = "📰 Обычная новость"

                # AI-анализ достоверности
                if credibility > 0.7:
                    trust = "✅ Высокая достоверность"
                elif credibility > 0.4:
                    trust = "⚠️ Средняя достоверность"
                else:
                    trust = "❌ Низкая достоверность"

                line = f"{i}. {analysis}: {title}\n   {trust} (важность: {importance:.2f}, достоверность: {credibility:.2f})"
                lines.append(line)

            return "\n\n".join(lines)

        except Exception as e:
            logger.error(f"Ошибка при формировании AI дайджеста: {e}")
            return f"🤖 Ошибка AI анализа: {e}"


# Глобальный экземпляр для использования в боте
async_digest_service = AsyncDigestService()

# services/digest_service.py
import logging
from database.db_models import get_latest_news
from digests.generator import generate_digest

logger = logging.getLogger("digest_service")


def build_daily_digest(limit: int = 10, style: str = "why_important") -> str:
    """
    Собирает свежие новости из БД и формирует дайджест.
    """
    try:
        news = get_latest_news(limit=limit)
        if not news:
            return "Сегодня новостей нет."
        return generate_digest(news, style=style)
    except Exception as e:
        logger.error(f"Ошибка при формировании дайджеста: {e}", exc_info=True)
        return "⚠️ Ошибка при генерации дайджеста."

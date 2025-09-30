"""
AI Digest Service - centralized digest generation for both normal and AI digests.
"""

import logging
from typing import List, Optional, Union

from repositories.news_repository import NewsRepository
from models.news import NewsItem
from utils.formatters import format_news, format_ai_fallback
from digests.ai_summary import generate_batch_summary
from database.db_models import supabase

logger = logging.getLogger(__name__)


class DigestAIService:
    """Centralized service for generating both normal and AI digests."""

    def __init__(self, news_repo: Optional[NewsRepository] = None):
        self.news_repo = news_repo or NewsRepository(supabase)

    def generate_digest(
        self,
        limit: int = 10,
        category: Optional[str] = None,
        ai: bool = False,
        style: str = "analytical",
    ) -> str:
        """
        Generate digest (normal or AI) based on parameters.
        
        Args:
            limit: maximum number of news items
            category: filter by category (None for all)
            ai: if True, generate AI digest, else normal HTML digest
            style: style for AI generation
            
        Returns:
            Formatted digest text
        """
        try:
            # Get news items
            categories = [category] if category else None
            news_items = self.news_repo.get_recent_news(limit=limit, categories=categories)
            
            if not news_items:
                if ai:
                    return f"AI DIGEST (cat={category}): Сегодня новостей нет."
                return format_news([], limit=None, with_header=True)
            
            if ai:
                return self.generate_ai_digest(news_items, style=style, category=category)
            else:
                return format_news(news_items, limit=limit, with_header=True)
                
        except Exception as e:
            logger.error("Ошибка при генерации дайджеста: %s", e, exc_info=True)
            if ai:
                return f"AI DIGEST (cat={category}): ⚠️ Ошибка при генерации дайджеста."
            return "⚠️ Ошибка при генерации дайджеста."

    def generate_ai_digest(
        self,
        news_items: List[NewsItem],
        style: str = "analytical",
        category: Optional[str] = None,
    ) -> str:
        """
        Generate AI digest from news items.
        
        Args:
            news_items: list of NewsItem models
            style: AI generation style
            category: category for display
            
        Returns:
            AI digest text with fallback block
        """
        try:
            # Generate AI summary
            ai_text = generate_batch_summary(news_items, style=style) or ""
            
            # Add fallback block if missing
            if "<b>Почему это важно" not in ai_text:
                ai_text += format_ai_fallback()
            
            return f"AI DIGEST (cat={category}):\n\n{ai_text}".strip()
            
        except Exception as e:
            logger.error("Ошибка при генерации AI-дайджеста: %s", e, exc_info=True)
            return f"AI DIGEST (cat={category}): ⚠️ Ошибка при генерации AI-дайджеста."


# Singleton instance for backward compatibility
try:
    _default_ai_service = DigestAIService()
except Exception as e:
    logger.error("Не удалось инициализировать DigestAIService: %s", e)
    _default_ai_service = None


def generate_digest(
    limit: int = 10,
    category: Optional[str] = None,
    ai: bool = False,
    style: str = "analytical",
) -> str:
    """
    Backward compatibility wrapper for generate_digest.
    """
    if not _default_ai_service:
        return "⚠️ DigestAIService недоступен."
    return _default_ai_service.generate_digest(limit=limit, category=category, ai=ai, style=style)


__all__ = ["DigestAIService", "generate_digest"]

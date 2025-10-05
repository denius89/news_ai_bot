"""
Unified Digest Service for PulseAI.

This module provides a unified interface for both synchronous and asynchronous
digest generation, eliminating code duplication between sync and async versions.
"""

import logging
from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime, timezone

from database.service import get_sync_service, get_async_service
from digests.ai_service import DigestAIService
from utils.formatters import format_news
from utils.clean_text import clean_for_telegram

logger = logging.getLogger("unified_digest_service")


class UnifiedDigestService:
    """
    Unified digest service for both sync and async operations.

    This class provides a clean interface for generating both regular and AI digests,
    automatically choosing between sync and async implementations based on the method called.
    """

    def __init__(self, async_mode: bool = False):
        """
        Initialize unified digest service.

        Args:
            async_mode: If True, uses async database operations
        """
        self.async_mode = async_mode
        if async_mode:
            self.db_service = get_async_service()
        else:
            self.db_service = get_sync_service()

    def build_daily_digest(
        self,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        source: Optional[str] = None,
    ) -> str:
        """
        Build daily digest (sync version).

        Args:
            limit: Maximum number of news items
            categories: List of categories to filter
            source: Filter by source name

        Returns:
            Formatted digest text
        """
        try:
            news_items = self.db_service.get_latest_news(
                source=source, categories=categories, limit=limit
            )

            if not news_items:
                return "📰 <b>Дайджест новостей</b>\n\nСегодня новостей нет."

            digest_text = format_news(news_items, limit=limit, with_header=True)
            return clean_for_telegram(digest_text)

        except Exception as e:
            logger.error("❌ Error building daily digest: %s", e)
            return "⚠️ Ошибка при генерации дайджеста."

    async def async_build_daily_digest(
        self,
        limit: int = 10,
        categories: Optional[List[str]] = None,
        source: Optional[str] = None,
    ) -> str:
        """
        Build daily digest (async version).

        Args:
            limit: Maximum number of news items
            categories: List of categories to filter
            source: Filter by source name

        Returns:
            Formatted digest text
        """
        try:
            news_items = await self.db_service.async_get_latest_news(
                source=source, categories=categories, limit=limit
            )

            if not news_items:
                return "📰 <b>Дайджест новостей</b>\n\nСегодня новостей нет."

            digest_text = format_news(news_items, limit=limit, with_header=True)
            return clean_for_telegram(digest_text)

        except Exception as e:
            logger.error("❌ Error building async daily digest: %s", e)
            return "⚠️ Ошибка при генерации дайджеста."

    def build_ai_digest(
        self,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,  # Backward compatibility
        period: str = "daily",
        style: str = "analytical",
        limit: int = 20,
    ) -> str:
        """
        Build AI digest (sync version).

        Args:
            categories: List of categories to filter
            category: Single category for backward compatibility
            period: Time period for digest
            style: AI generation style
            limit: Maximum number of news items

        Returns:
            AI-generated digest text
        """
        try:
            # Backward compatibility
            if categories is None and category is not None:
                categories = [category]

            news_items = self.db_service.get_latest_news(categories=categories, limit=limit)

            if not news_items:
                cat_display = categories[0] if categories else category or "all"
                return f"📰 <b>AI-дайджест</b> ({cat_display.title()})\n\nСегодня новостей нет."

            # Use AI service for generation
            cat_display = categories[0] if categories else category or "all"
            ai_service = DigestAIService()
            ai_digest = ai_service.generate_ai_digest(
                news_items=news_items, category=cat_display, style=style, period=period
            )

            return clean_for_telegram(ai_digest)

        except Exception as e:
            logger.error("❌ Error building AI digest: %s", e)
            return "⚠️ Ошибка при генерации AI-дайджеста."

    async def async_build_ai_digest(
        self,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,  # Backward compatibility
        period: str = "daily",
        style: str = "analytical",
        limit: int = 20,
    ) -> str:
        """
        Build AI digest (async version).

        Args:
            categories: List of categories to filter
            category: Single category for backward compatibility
            period: Time period for digest
            style: AI generation style
            limit: Maximum number of news items

        Returns:
            AI-generated digest text
        """
        try:
            # Backward compatibility
            if categories is None and category is not None:
                categories = [category]

            news_items = await self.db_service.async_get_latest_news(
                categories=categories, limit=limit
            )

            if not news_items:
                cat_display = categories[0] if categories else category or "all"
                return f"📰 <b>AI-дайджест</b> ({cat_display.title()})\n\nСегодня новостей нет."

            # Use AI service for generation
            cat_display = categories[0] if categories else category or "all"
            ai_service = DigestAIService()
            ai_digest = ai_service.generate_ai_digest(
                news_items=news_items, category=cat_display, style=style, period=period
            )

            return clean_for_telegram(ai_digest)

        except Exception as e:
            logger.error("❌ Error building async AI digest: %s", e)
            return "⚠️ Ошибка при генерации AI-дайджеста."

    def get_news_with_analysis(
        self,
        categories: Optional[List[str]] = None,
        limit: int = 10,
        min_importance: float = 0.3,
    ) -> List[Dict]:
        """
        Get news items with AI analysis (sync version).

        Args:
            categories: List of categories to filter
            limit: Maximum number of news items
            min_importance: Minimum importance threshold

        Returns:
            List of news items with AI analysis
        """
        try:
            news_items = self.db_service.get_latest_news(
                categories=categories, limit=limit * 2  # Get more to filter by importance
            )

            # Filter by importance
            filtered_items = [
                item for item in news_items if item.get('importance', 0) >= min_importance
            ]

            return filtered_items[:limit]

        except Exception as e:
            logger.error("❌ Error getting news with analysis: %s", e)
            return []

    async def async_get_news_with_analysis(
        self,
        categories: Optional[List[str]] = None,
        limit: int = 10,
        min_importance: float = 0.3,
    ) -> List[Dict]:
        """
        Get news items with AI analysis (async version).

        Args:
            categories: List of categories to filter
            limit: Maximum number of news items
            min_importance: Minimum importance threshold

        Returns:
            List of news items with AI analysis
        """
        try:
            news_items = await self.db_service.async_get_latest_news(
                categories=categories, limit=limit * 2  # Get more to filter by importance
            )

            # Filter by importance
            filtered_items = [
                item for item in news_items if item.get('importance', 0) >= min_importance
            ]

            return filtered_items[:limit]

        except Exception as e:
            logger.error("❌ Error getting async news with analysis: %s", e)
            return []

    def close(self):
        """Close database connections."""
        self.db_service.close()

    async def aclose(self):
        """Close async database connections."""
        await self.db_service.aclose()


# Global service instances
_sync_digest_service: Optional[UnifiedDigestService] = None
_async_digest_service: Optional[UnifiedDigestService] = None


def get_sync_digest_service() -> UnifiedDigestService:
    """Get or create sync digest service instance."""
    global _sync_digest_service
    if _sync_digest_service is None:
        _sync_digest_service = UnifiedDigestService(async_mode=False)
    return _sync_digest_service


def get_async_digest_service() -> UnifiedDigestService:
    """Get or create async digest service instance."""
    global _async_digest_service
    if _async_digest_service is None:
        _async_digest_service = UnifiedDigestService(async_mode=True)
    return _async_digest_service


# Backward compatibility functions
def build_daily_digest(
    limit: int = 10,
    categories: Optional[List[str]] = None,
    source: Optional[str] = None,
) -> str:
    """Backward compatibility function for building daily digest."""
    service = get_sync_digest_service()
    return service.build_daily_digest(limit, categories, source)


async def async_build_daily_digest(
    limit: int = 10,
    categories: Optional[List[str]] = None,
    source: Optional[str] = None,
) -> str:
    """Backward compatibility function for building async daily digest."""
    service = get_async_digest_service()
    return await service.async_build_daily_digest(limit, categories, source)


def build_ai_digest(
    categories: Optional[List[str]] = None,
    category: Optional[str] = None,
    period: str = "daily",
    style: str = "analytical",
    limit: int = 20,
) -> str:
    """Backward compatibility function for building AI digest."""
    service = get_sync_digest_service()
    return service.build_ai_digest(categories, category, period, style, limit)


async def async_build_ai_digest(
    categories: Optional[List[str]] = None,
    category: Optional[str] = None,
    period: str = "daily",
    style: str = "analytical",
    limit: int = 20,
) -> str:
    """Backward compatibility function for building async AI digest."""
    service = get_async_digest_service()
    return await service.async_build_ai_digest(categories, category, period, style, limit)

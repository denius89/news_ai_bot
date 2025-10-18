"""
Unified Digest Service for PulseAI.

This module provides a unified interface for both synchronous and asynchronous
digest generation, eliminating code duplication between sync and async versions.
"""

import logging
from typing import List, Dict, Optional

from database.service import get_sync_service, get_async_service
from digests.ai_service import DigestAIService
from utils.text.formatters import format_news
from utils.text.clean_text import clean_for_telegram

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
            news_items = self.db_service.get_latest_news(source=source, categories=categories, limit=limit)

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
            news_items = await self.db_service.async_get_latest_news(source=source, categories=categories, limit=limit)

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
            # For sync version, use fallback digest
            from utils.text.formatters import format_news

            ai_digest = format_news(news_items, limit=limit)

            return clean_for_telegram(ai_digest)

        except Exception as e:
            logger.error("❌ Error building AI digest: %s", e)
            return "⚠️ Ошибка при генерации AI-дайджеста."

    async def async_build_ai_digest(
        self,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,  # Backward compatibility
        subcategory: Optional[str] = None,  # Новый параметр субкатегории
        period: str = "daily",
        style: str = "analytical",
        length: str = "medium",  # НОВЫЙ ПАРАМЕТР ДЛИНЫ ТЕКСТА
        limit: int = 20,
        min_importance: Optional[float] = None,  # НОВЫЙ ПАРАМЕТР ДЛЯ УМНОЙ ФИЛЬТРАЦИИ
        # Новые параметры для расширенных возможностей
        use_multistage: bool = False,
        use_rag: bool = True,
        use_personalization: bool = True,
        user_id: Optional[str] = None,
        audience: str = "general",
    ) -> str:
        """
        Build AI digest (async version).

        Args:
            categories: List of categories to filter
            category: Single category for backward compatibility
            subcategory: Specific subcategory (e.g., "bitcoin", "stocks")
            period: Time period for digest
            style: AI generation style
            length: Text length (short, medium, long)
            limit: Maximum number of news items
            min_importance: Minimum importance threshold for news filtering
            use_multistage: Enable multi-stage generation with Chain-of-Thought
            use_rag: Enable RAG system with high-quality examples
            use_personalization: Enable personalization based on user profile
            user_id: User ID for personalization
            audience: Target audience type (general, pro)

        Returns:
            AI-generated digest text
        """
        try:
            # Backward compatibility
            if categories is None and category is not None:
                categories = [category]

            # Convert period to days_back for database filtering
            days_back = None
            if period == "7d":
                days_back = 7
            elif period == "30d":
                days_back = 30
            elif period == "today":
                days_back = 1
            # "daily" and other values default to None (no date filtering)

            logger.info(f"🔍 Period '{period}' converted to days_back={days_back} for category={categories}")
            logger.info(
                f"🔍 Filtering parameters: categories={categories}, limit={limit}, min_importance={min_importance}"
            )

            # ИСПОЛЬЗУЕМ НОВУЮ ФУНКЦИЮ С ФИЛЬТРАЦИЕЙ ПО ВАЖНОСТИ
            if min_importance is not None:
                logger.info(f"🔍 Using importance filter: min_importance={min_importance}")
                news_items = await self.db_service.async_get_latest_news_with_importance(
                    categories=categories, limit=limit, min_importance=min_importance, days_back=days_back
                )
            else:
                logger.info("🔍 Using standard filter (no min_importance)")
                # Use updated function with date filtering
                news_items = await self.db_service.async_get_latest_news(
                    categories=categories, limit=limit, days_back=days_back
                )

            logger.info(
                f"📰 Retrieved {len(news_items)} news items for period={period}, days_back={days_back}, categories={categories}"
            )

            # Fallback: если не найдено новостей с фильтром по важности, попробуем без него
            if not news_items and min_importance is not None and categories:
                logger.warning(
                    f"⚠️ No news with importance filter, trying without importance filter for categories={categories}"
                )
                news_items = await self.db_service.async_get_latest_news(
                    categories=categories, limit=limit, days_back=days_back
                )
                logger.info(f"📰 Fallback retrieved {len(news_items)} news items without importance filter")
            # Логируем первые несколько новостей для отладки
            if news_items:
                logger.info(
                    f"📰 First few news items: {[{'title': item.get('title', '')[:50], 'category': item.get('category'), 'importance': item.get('importance')} for item in news_items[:3]]}"
                )
            else:
                logger.warning(f"⚠️ No news items found for categories={categories}, period={period}")

            if not news_items:
                cat_display = categories[0] if categories else category or "all"
                return f"📰 <b>AI-дайджест</b> ({cat_display.title()})\n\nСегодня новостей нет."

            # Use AI service for generation with new capabilities
            cat_display = categories[0] if categories else category or "all"

            # Create configuration with new parameters
            from digests.ai_service import DigestConfig

            config = DigestConfig(
                use_multistage=use_multistage,
                use_rag=use_rag,
                use_personalization=use_personalization,
                user_id=user_id,
                audience=audience,
                max_items=limit,
            )
            ai_service = DigestAIService(config=config)

            # Convert dicts to NewsItem objects
            from models.news import NewsItem

            news_objects = []
            for item in news_items:
                if isinstance(item, dict):
                    news_obj = NewsItem(
                        title=item.get("title", ""),
                        content=item.get("content", ""),
                        link=item.get("link", ""),
                        source=item.get("source", ""),
                        published_at=item.get("published_at", ""),
                        category=item.get("category", ""),
                        subcategory=item.get("subcategory", ""),
                        credibility=item.get("credibility", 0.0),
                        importance=item.get("importance", 0.0),
                    )
                    news_objects.append(news_obj)
                else:
                    news_objects.append(item)

            ai_digest = await ai_service.build_digest(
                news_items=news_objects, style=style, category=cat_display, length=length, subcategory=subcategory
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
            filtered_items = [item for item in news_items if item.get("importance", 0) >= min_importance]

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
            filtered_items = [item for item in news_items if item.get("importance", 0) >= min_importance]

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

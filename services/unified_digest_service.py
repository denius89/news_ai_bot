"""
Unified Digest Service for PulseAI.

This service consolidates both sync and async digest generation into a single interface,
eliminating code duplication and providing consistent behavior across all modes.
"""

import logging

from database.service import get_sync_service, get_async_service
from utils.error_handler import handle_database_error, handle_parsing_error
from utils.formatters import format_news, format_ai_fallback

logger = logging.getLogger("unified_digest_service")


class UnifiedDigestService:
    """
    Unified service for generating both sync and async digests.

    This class provides a single interface for all digest operations,
    automatically choosing between sync and async implementations based on
    the method called.
    """

    def __init__(self, async_mode: bool = False):
        """
        Initialize unified digest service.

        Args:
            async_mode: If True, initializes async mode. If False, sync mode.
        """
        self.async_mode = async_mode
        self.sync_service = get_sync_service()
        self.async_service = get_async_service()

        # Initialize async service if needed
        if async_mode:
            asyncio.create_task(self._init_async())

    async def _init_async(self):
        """Initialize async database service."""
        await self.async_service._init_async_client()

    def build_daily_digest(
        self,
        limit: int = 10,
        style: str = "analytical",
        categories: Optional[List[str]] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Build daily digest (sync version).

        Args:
            limit: Maximum number of news items
            style: Digest style (analytical, business, etc.)
            categories: List of categories to filter

        Returns:
            Tuple of (digest_text, news_items)
        """
        if self.async_mode:
            # Run async version in sync context
            return asyncio.run(self.async_build_daily_digest(limit, style, categories))

        return self._build_daily_digest_sync(limit, style, categories)

    async def async_build_daily_digest(
        self,
        limit: int = 10,
        style: str = "analytical",
        categories: Optional[List[str]] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Build daily digest (async version).

        Args:
            limit: Maximum number of news items
            style: Digest style (analytical, business, etc.)
            categories: List of categories to filter

        Returns:
            Tuple of (digest_text, news_items)
        """
        return await self._build_daily_digest_async(limit, style, categories)

    @handle_database_error("build daily digest")
    def _build_daily_digest_sync(
        self,
        limit: int = 10,
        style: str = "analytical",
        categories: Optional[List[str]] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Internal sync implementation."""
        try:
            # Get news items
            news = self.sync_service.get_latest_news(
                source=None, categories=categories, limit=limit
            )

            if not news:
                return "DIGEST: Сегодня новостей нет.", []

            # Format digest
            digest_text = self._format_daily_digest(news, style)
            return digest_text, news

        except Exception as e:
            logger.error("Error building sync daily digest: %s", e)
            return "⚠️ Ошибка при генерации дайджеста.", []

    @handle_database_error("build async daily digest")
    async def _build_daily_digest_async(
        self,
        limit: int = 10,
        style: str = "analytical",
        categories: Optional[List[str]] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Internal async implementation."""
        try:
            # Ensure async service is initialized
            if not self.async_service.async_client:
                await self.async_service._init_async_client()

            # Get news items
            news = await self.async_service.async_get_latest_news(
                source=None, categories=categories, limit=limit
            )

            if not news:
                return "DIGEST: Сегодня новостей нет.", []

            # Format digest
            digest_text = self._format_daily_digest(news, style)
            return digest_text, news

        except Exception as e:
            logger.error("Error building async daily digest: %s", e)
            return "⚠️ Ошибка при генерации дайджеста.", []

    def build_ai_digest(
        self,
        limit: int = 20,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,  # Backward compatibility
        period: str = "daily",
        style: str = "analytical",
    ) -> str:
        """
        Build AI digest (sync version).

        Args:
            limit: Maximum number of news items
            categories: List of categories to filter
            category: Single category for backward compatibility
            period: Time period for digest
            style: AI generation style

        Returns:
            AI digest text
        """
        if self.async_mode:
            # Run async version in sync context
            return asyncio.run(
                self.async_build_ai_digest(limit, categories, category, period, style)
            )

        return self._build_ai_digest_sync(limit, categories, category, period, style)

    async def async_build_ai_digest(
        self,
        limit: int = 20,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,  # Backward compatibility
        period: str = "daily",
        style: str = "analytical",
    ) -> str:
        """
        Build AI digest (async version).

        Args:
            limit: Maximum number of news items
            categories: List of categories to filter
            category: Single category for backward compatibility
            period: Time period for digest
            style: AI generation style

        Returns:
            AI digest text
        """
        return await self._build_ai_digest_async(limit, categories, category, period, style)

    @handle_database_error("build AI digest")
    def _build_ai_digest_sync(
        self,
        limit: int = 20,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,
        period: str = "daily",
        style: str = "analytical",
    ) -> str:
        """Internal sync AI digest implementation."""
        try:
            # Support backward compatibility
            if categories is None and category is not None:
                categories = [category]

            # Get news items with higher limit for AI analysis
            news = self.sync_service.get_latest_news(
                source=None, categories=categories, limit=limit * 2
            )

            if not news:
                cat_display = categories[0] if categories else category or "all"
                return f"AI DIGEST (cat={cat_display}): Сегодня новостей нет."

            # Filter by importance for AI digest
            important_news = [item for item in news if float(item.get('importance', 0)) >= 0.4][
                :limit
            ]

            if not important_news:
                important_news = news[:limit]

            # Generate AI digest
            return self._format_ai_digest(important_news, style, categories, category)

        except Exception as e:
            logger.error("Error building sync AI digest: %s", e)
            cat_display = categories[0] if categories else category or "all"
            return f"AI DIGEST (cat={cat_display}): ⚠️ Ошибка при генерации AI-дайджеста."

    @handle_database_error("build async AI digest")
    async def _build_ai_digest_async(
        self,
        limit: int = 20,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,
        period: str = "daily",
        style: str = "analytical",
    ) -> str:
        """Internal async AI digest implementation."""
        try:
            # Support backward compatibility
            if categories is None and category is not None:
                categories = [category]

            # Ensure async service is initialized
            if not self.async_service.async_client:
                await self.async_service._init_async_client()

            # Get news items with higher limit for AI analysis
            news = await self.async_service.async_get_latest_news(
                source=None, categories=categories, limit=limit * 2
            )

            if not news:
                cat_display = categories[0] if categories else category or "all"
                return f"AI DIGEST (cat={cat_display}): Сегодня новостей нет."

            # Filter by importance for AI digest
            important_news = [item for item in news if float(item.get('importance', 0)) >= 0.4][
                :limit
            ]

            if not important_news:
                important_news = news[:limit]

            # Generate AI digest
            return self._format_ai_digest(important_news, style, categories, category)

        except Exception as e:
            logger.error("Error building async AI digest: %s", e)
            cat_display = categories[0] if categories else category or "all"
            return f"AI DIGEST (cat={cat_display}): ⚠️ Ошибка при генерации AI-дайджеста."

    def _format_daily_digest(self, news: List[Dict[str, Any]], style: str) -> str:
        """
        Format daily digest text.

        Args:
            news: List of news items
            style: Digest style

        Returns:
            Formatted digest text
        """
        if not news:
            return "DIGEST: Сегодня новостей нет."

        lines = []

        for i, item in enumerate(news, 1):
            title = item.get('title') or "Без заголовка"
            date = item.get('published_at_fmt') or "—"
            link = item.get('link')

            # Add importance and credibility metrics
            importance = float(item.get('importance', 0))
            credibility = float(item.get('credibility', 0))

            # Format metrics
            metrics = ""
            if importance > 0:
                importance_icon = "🔥" if importance > 0.7 else "⚠️" if importance > 0.4 else "📰"
                credibility_icon = "✅" if credibility > 0.7 else "⚠️" if credibility > 0.4 else "❌"
                metrics = f" {importance_icon}{importance:.2f} {credibility_icon}{credibility:.2f}"

            line = f"{i}. {title}{metrics}"
            if link:
                line += f"\n   🔗 {link}"
            line += f"\n   📅 {date}"
            lines.append(line)

        return "\n\n".join(lines)

    def _format_ai_digest(
        self,
        news: List[Dict[str, Any]],
        style: str,
        categories: Optional[List[str]] = None,
        category: Optional[str] = None,
    ) -> str:
        """
        Format AI digest text.

        Args:
            news: List of news items
            style: AI generation style
            categories: Categories for display
            category: Single category for display

        Returns:
            Formatted AI digest text
        """
        if not news:
            cat_display = categories[0] if categories else category or "all"
            return f"AI DIGEST (cat={cat_display}): Сегодня новостей нет."

        # Determine category display
        cat_display = categories[0] if categories else category or "all"

        # Try to generate AI analysis
        try:
            ai_text = self._generate_ai_analysis(news, style)
        except Exception as e:
            logger.warning("AI analysis failed, using fallback: %s", e)
            ai_text = format_ai_fallback()

        return f"AI DIGEST (cat={cat_display}):\n\n{ai_text}".strip()

    def _generate_ai_analysis(self, news: List[Dict[str, Any]], style: str) -> str:
        """
        Generate AI analysis for news items.

        Args:
            news: List of news items
            style: AI generation style

        Returns:
            AI analysis text
        """
        try:
            from digests.ai_summary import generate_batch_summary

            # Prepare news items for AI analysis
            news_for_ai = []
            for item in news:
                news_for_ai.append(
                    {
                        'title': item.get('title', ''),
                        'content': item.get('content', ''),
                        'importance': float(item.get('importance', 0)),
                        'credibility': float(item.get('credibility', 0)),
                    }
                )

            # Generate AI summary
            ai_text = generate_batch_summary(news_for_ai, style=style)

            if not ai_text or ai_text.strip() == "":
                ai_text = format_ai_fallback()

            return ai_text

        except Exception as e:
            logger.error("Error generating AI analysis: %s", e)
            return format_ai_fallback()

    def get_digest_stats(self, news: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about news items in digest.

        Args:
            news: List of news items

        Returns:
            Dictionary with digest statistics
        """
        if not news:
            return {
                "total_items": 0,
                "avg_importance": 0.0,
                "avg_credibility": 0.0,
                "high_importance_count": 0,
                "high_credibility_count": 0,
            }

        total_items = len(news)
        importance_values = [float(item.get('importance', 0)) for item in news]
        credibility_values = [float(item.get('credibility', 0)) for item in news]

        avg_importance = sum(importance_values) / total_items if total_items > 0 else 0.0
        avg_credibility = sum(credibility_values) / total_items if total_items > 0 else 0.0

        high_importance_count = sum(1 for imp in importance_values if imp > 0.7)
        high_credibility_count = sum(1 for cred in credibility_values if cred > 0.7)

        return {
            "total_items": total_items,
            "avg_importance": round(avg_importance, 3),
            "avg_credibility": round(avg_credibility, 3),
            "high_importance_count": high_importance_count,
            "high_credibility_count": high_credibility_count,
        }


# Global service instances for backward compatibility
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
    style: str = "analytical",
    categories: Optional[List[str]] = None,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Backward compatibility function for build_daily_digest."""
    service = get_sync_digest_service()
    return service.build_daily_digest(limit, style, categories)


async def async_build_daily_digest(
    limit: int = 10,
    style: str = "analytical",
    categories: Optional[List[str]] = None,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Backward compatibility function for async_build_daily_digest."""
    service = get_async_digest_service()
    return await service.async_build_daily_digest(limit, style, categories)


def build_ai_digest(
    limit: int = 20,
    categories: Optional[List[str]] = None,
    category: Optional[str] = None,
    period: str = "daily",
    style: str = "analytical",
) -> str:
    """Backward compatibility function for build_ai_digest."""
    service = get_sync_digest_service()
    return service.build_ai_digest(limit, categories, category, period, style)


async def async_build_ai_digest(
    limit: int = 20,
    categories: Optional[List[str]] = None,
    category: Optional[str] = None,
    period: str = "daily",
    style: str = "analytical",
) -> str:
    """Backward compatibility function for async_build_ai_digest."""
    service = get_async_digest_service()
    return await service.async_build_ai_digest(limit, categories, category, period, style)

"""
Simplified Unified Database Service for PulseAI.

This module provides a clean, simplified interface for both synchronous
and asynchronous database operations without complex coroutine handling.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pathlib import Path
import sys

import httpx
from httpx import HTTPTransport, AsyncHTTPTransport
from supabase import create_client, create_async_client, Client, AsyncClient

# Add project root to path
sys.path.insert(0, "/Users/denisfedko/news_ai_bot")

from ai_modules.credibility import evaluate_credibility  # noqa: E402
from ai_modules.importance import evaluate_importance  # noqa: E402
from utils.system.dates import ensure_utc_iso  # noqa: E402

# from utils.system.cache import get_news_cache, cached  # noqa: E402
from config.core.settings import SUPABASE_URL, SUPABASE_KEY  # noqa: E402

logger = logging.getLogger("database.service")


class DatabaseService:
    """
    Simplified unified database service for both sync and async operations.

    This class provides a clean interface without complex coroutine handling.
    Separate instances should be used for sync and async operations.
    """

    def __init__(self, async_mode: bool = False):
        """
        Initialize database service.

        Args:
            async_mode: If True, initializes async client. If False, sync client.
        """
        self.async_mode = async_mode
        self.sync_client: Optional[Client] = None
        self.async_client: Optional[AsyncClient] = None

        if async_mode:
            self._init_async_client()
        else:
            self._init_sync_client()

    def _init_sync_client(self):
        """Initialize synchronous Supabase client."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.warning("⚠️ Supabase credentials not found")
            return

        try:
            # Принудительно отключаем HTTP/2 для решения pseudo-header ошибки
            import os
            os.environ["HTTPX_NO_HTTP2"] = "1"
            os.environ["SUPABASE_HTTP2_DISABLED"] = "1"
            
            self.sync_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✅ Sync Supabase client initialized with HTTP/2 disabled via environment")
        except Exception as e:
            logger.error("❌ Failed to initialize Sync Supabase: %s", e)

    def _init_async_client(self):
        """Initialize asynchronous Supabase client."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.warning("⚠️ Supabase credentials not found")
            return

        try:
            # For async client, we'll initialize it in the async context
            self.async_client = None
            logger.info("✅ Async Supabase client ready for initialization")
        except Exception as e:
            logger.error("❌ Failed to prepare Async Supabase: %s", e)

    async def _get_async_client(self) -> AsyncClient:
        """Get or initialize async client."""
        if self.async_client is None:
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise RuntimeError("Supabase credentials not found")
            self.async_client = await create_async_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✅ Async Supabase client initialized")
        return self.async_client

    def safe_execute(self, query, retries: int = 3, delay: float = 1.0):
        """
        Execute query with retries for network errors (sync version).

        Args:
            query: Supabase query object
            retries: Number of retry attempts
            delay: Base delay between retries in seconds

        Returns:
            Query result
        """
        for attempt in range(retries):
            try:
                return query.execute()
            except (httpx.RemoteProtocolError, httpx.ConnectError, httpx.TimeoutException) as e:
                logger.warning("⚠️ Attempt %d/%d: connection error %s", attempt + 1, retries, e)
                if attempt < retries - 1:
                    time.sleep(delay * (2**attempt))  # Exponential backoff
                else:
                    raise
            except Exception as e:
                logger.error("❌ Unexpected error in safe_execute: %s", e)
                raise

    async def async_safe_execute(self, query, retries: int = 3, delay: float = 1.0):
        """
        Execute query with retries for network errors (async version).

        Args:
            query: Supabase async query object
            retries: Number of retry attempts
            delay: Base delay between retries in seconds

        Returns:
            Query result
        """
        for attempt in range(retries):
            try:
                return await query.execute()
            except (httpx.RemoteProtocolError, httpx.ConnectError, httpx.TimeoutException) as e:
                logger.warning("⚠️ Attempt %d/%d: async connection error %s", attempt + 1, retries, e)
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (2**attempt))  # Exponential backoff
                else:
                    raise
            except Exception as e:
                logger.error("❌ Unexpected error in async_safe_execute: %s", e)
                raise

    # === SYNC METHODS ===

    def get_latest_news(
        self,
        source: Optional[str] = None,
        categories: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Get latest news (sync version).

        Args:
            source: Filter by source name
            categories: Filter by categories
            limit: Maximum number of news items

        Returns:
            List of news dictionaries
        """
        if not self.sync_client:
            logger.warning("⚠️ Sync Supabase client not available")
            return []

        logger.debug("get_latest_news: source=%s, categories=%s, limit=%s", source, categories, limit)

        query = (
            self.sync_client.table("news")
            .select(
                "id, uid, title, content, link, published_at, source, category, subcategory, credibility, importance"
            )
            .order("published_at", desc=True)
            .limit(limit)
        )

        if source:
            query = query.eq("source", source)

        if categories:
            query = query.in_("category", categories)

        try:
            result = self.safe_execute(query)
            news_items = result.data or []

            # Add formatted dates for backward compatibility
            for item in news_items:
                if item.get("published_at"):
                    from utils.system.dates import format_datetime

                    item["published_at_fmt"] = format_datetime(item["published_at"])

            logger.info("✅ Retrieved %d news items", len(news_items))
            return news_items
        except Exception as e:
            logger.error("❌ Error retrieving news: %s", e)
            return []

    def upsert_news(self, items: List[Dict]) -> int:
        """
        Upsert news items (sync version).

        Args:
            items: List of news dictionaries

        Returns:
            Number of items processed
        """
        if not self.sync_client:
            logger.warning("⚠️ Sync Supabase client not available")
            return 0

        if not items:
            logger.info("No news items to insert")
            return 0

        try:
            # Prepare items for upsert
            rows = self._prepare_news_items(items)

            if not rows:
                logger.info("No valid news items to insert")
                return 0

            # Upsert with conflict resolution
            self.safe_execute(self.sync_client.table("news").upsert(rows, on_conflict="uid"))

            logger.info("✅ Upsert: processed %d news items", len(rows))
            return len(rows)

        except Exception as e:
            logger.error("❌ Error upserting news: %s", e)
            return 0

    # === ASYNC METHODS ===

    async def async_get_latest_news(
        self,
        source: Optional[str] = None,
        categories: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Get latest news (async version).

        Args:
            source: Filter by source name
            categories: Filter by categories
            limit: Maximum number of news items

        Returns:
            List of news dictionaries
        """
        try:
            client = await self._get_async_client()
        except Exception as e:
            logger.error("❌ Failed to get async client: %s", e)
            return []

        logger.debug("async_get_latest_news: source=%s, categories=%s, limit=%s", source, categories, limit)

        query = (
            client.table("news")
            .select(
                "id, uid, title, content, link, published_at, source, category, subcategory, credibility, importance"
            )
            .order("published_at", desc=True)
            .limit(limit)
        )

        if source:
            query = query.eq("source", source)

        if categories:
            query = query.in_("category", categories)

        try:
            result = await self.async_safe_execute(query)
            news_items = result.data or []

            # Add formatted dates for backward compatibility
            for item in news_items:
                if item.get("published_at"):
                    from utils.system.dates import format_datetime

                    item["published_at_fmt"] = format_datetime(item["published_at"])

            logger.info("✅ Async: retrieved %d news items", len(news_items))
            return news_items
        except Exception as e:
            logger.error("❌ Error async retrieving news: %s", e)
            return []

    async def async_get_latest_news_with_importance(
        self,
        source: Optional[str] = None,
        categories: Optional[List[str]] = None,
        limit: int = 10,
        min_importance: Optional[float] = None,
    ) -> List[Dict]:
        """
        Get latest news with importance filtering (async version).

        Args:
            source: Filter by source name
            categories: Filter by categories
            limit: Maximum number of news items
            min_importance: Minimum importance threshold

        Returns:
            List of news dictionaries sorted by importance
        """
        try:
            client = await self._get_async_client()
        except Exception as e:
            logger.error("❌ Failed to get async client: %s", e)
            return []

        logger.debug("async_get_latest_news_with_importance: source=%s, categories=%s, limit=%s, min_importance=%s", 
                    source, categories, limit, min_importance)

        query = (
            client.table("news")
            .select(
                "id, uid, title, content, link, published_at, source, category, subcategory, credibility, importance"
            )
            .order("published_at", desc=True)
            .limit(limit)
        )

        if source:
            query = query.eq("source", source)

        if categories:
            query = query.in_("category", categories)

        if min_importance is not None:
            query = query.gte("importance", min_importance)

        try:
            result = await self.async_safe_execute(query)
            news_items = result.data or []

            # Add formatted dates for backward compatibility
            for item in news_items:
                if item.get("published_at"):
                    from utils.system.dates import format_datetime
                    item["published_at_fmt"] = format_datetime(item["published_at"])

            # Sort by importance if not filtered by min_importance
            if min_importance is None:
                news_items = sorted(news_items, key=lambda x: x.get("importance", 0), reverse=True)

            logger.info("✅ Async: retrieved %d news items with importance filtering", len(news_items))
            return news_items
        except Exception as e:
            logger.error("❌ Error async retrieving news with importance: %s", e)
            # Fallback на обычную функцию
            return await self.async_get_latest_news(source, categories, limit)

    async def async_upsert_news(self, items: List[Dict]) -> int:
        """
        Upsert news items (async version).

        Args:
            items: List of news dictionaries

        Returns:
            Number of items processed
        """
        try:
            client = await self._get_async_client()
        except Exception as e:
            logger.error("❌ Failed to get async client: %s", e)
            return 0

        if not items:
            logger.info("No news items to insert")
            return 0

        try:
            # Prepare items for upsert
            rows = self._prepare_news_items(items)

            if not rows:
                logger.info("No valid news items to insert")
                return 0

            # Upsert with conflict resolution
            await self.async_safe_execute(client.table("news").upsert(rows, on_conflict="uid"))

            logger.info("✅ Async upsert: processed %d news items", len(rows))
            return len(rows)

        except Exception as e:
            logger.error("❌ Error async upserting news: %s", e)
            return 0

    # === HELPER METHODS ===

    def _prepare_news_items(self, items: List[Dict]) -> List[Dict]:
        """
        Prepare news items for database insertion.

        Args:
            items: Raw news items

        Returns:
            Prepared items ready for database
        """
        rows = []
        for item in items:
            try:
                # Validate item
                if not isinstance(item, dict):
                    logger.error("Received non-dict item: %s = %s", type(item), item)
                    continue

                # Enrich with AI analysis
                enriched = self._enrich_news_with_ai(item)

                # Extract and validate fields
                title = (enriched.get("title") or "").strip() or enriched.get("source") or "Без названия"
                content = (enriched.get("content") or "").strip() or (enriched.get("summary") or "").strip() or title

                # Generate UID
                uid = self._make_uid(enriched.get("link", ""), title)

                # Prepare row
                row = {
                    "uid": uid,
                    "title": title[:512],  # Limit title length
                    "content": content,
                    "link": enriched.get("link"),
                    "published_at": ensure_utc_iso(enriched.get("published_at"))
                    or datetime.now(timezone.utc).isoformat(),
                    "source": enriched.get("source"),
                    "category": (enriched.get("category") or "").lower() or None,
                    "subcategory": enriched.get("subcategory"),
                    "credibility": enriched.get("credibility"),
                    "importance": enriched.get("importance"),
                }

                rows.append(row)
                logger.debug("Prepared news row: %s", row)

            except Exception as e:
                logger.error("Error preparing news item: %s, item=%s", e, item)

        return rows

    def _enrich_news_with_ai(self, news_item: Dict) -> Dict:
        """
        Enrich news item with AI analysis.

        Args:
            news_item: Raw news item

        Returns:
            Enriched news item
        """
        try:
            # AI analysis
            news_item["credibility"] = evaluate_credibility(news_item)
            news_item["importance"] = evaluate_importance(news_item)
        except Exception as e:
            logger.warning("AI analysis failed: %s", e)
            news_item["credibility"] = 0.5
            news_item["importance"] = 0.5

        return news_item

    def _make_uid(self, url: str, title: str) -> str:
        """
        Generate unique ID for news item.

        Args:
            url: News URL
            title: News title

        Returns:
            SHA256 hash as UID
        """
        import hashlib

        return hashlib.sha256(f"{url}|{title}".encode()).hexdigest()

    def close(self):
        """Close database connections."""
        if self.sync_client:
            # Sync client doesn't need explicit closing
            self.sync_client = None
            logger.info("✅ Sync client closed")

    async def aclose(self):
        """Close async database connections."""
        if self.async_client:
            await self.async_client.aclose()
            self.async_client = None
            logger.info("✅ Async client closed")


# Global service instances for backward compatibility
_sync_service: Optional[DatabaseService] = None
_async_service: Optional[DatabaseService] = None


def get_sync_service() -> DatabaseService:
    """Get or create sync database service instance."""
    global _sync_service
    if _sync_service is None:
        _sync_service = DatabaseService(async_mode=False)
    return _sync_service


def get_async_service() -> DatabaseService:
    """Get or create async database service instance."""
    global _async_service
    if _async_service is None:
        _async_service = DatabaseService(async_mode=True)
    return _async_service


# Backward compatibility functions
def get_latest_news(
    source: Optional[str] = None,
    categories: Optional[List[str]] = None,
    limit: int = 10,
) -> List[Dict]:
    """Backward compatibility function for get_latest_news."""
    service = get_sync_service()
    return service.get_latest_news(source, categories, limit)


def upsert_news(items: List[Dict]) -> int:
    """Backward compatibility function for upsert_news."""
    service = get_sync_service()
    return service.upsert_news(items)


async def async_get_latest_news(
    source: Optional[str] = None,
    categories: Optional[List[str]] = None,
    limit: int = 10,
) -> List[Dict]:
    """Backward compatibility function for async_get_latest_news."""
    service = get_async_service()
    return await service.async_get_latest_news(source, categories, limit)


async def async_upsert_news(items: List[Dict]) -> int:
    """Backward compatibility function for async_upsert_news."""
    service = get_async_service()
    return await service.async_upsert_news(items)

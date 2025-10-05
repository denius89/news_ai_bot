"""
Unified Database Service for PulseAI.

This module provides a unified interface for both synchronous and asynchronous
database operations, eliminating code duplication between sync and async versions.
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pathlib import Path
import sys

import httpx
from dotenv import load_dotenv
from supabase import create_client, create_async_client, Client, AsyncClient

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ai_modules.credibility import evaluate_credibility  # noqa: E402
from ai_modules.importance import evaluate_importance  # noqa: E402
from utils.dates import ensure_utc_iso  # noqa: E402

logger = logging.getLogger("database.service")

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


class DatabaseService:
    """
    Unified database service supporting both sync and async operations.

    This class provides a single interface for all database operations,
    automatically choosing between sync and async implementations based on
    the method called.
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
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                self.sync_client = create_client(SUPABASE_URL, SUPABASE_KEY)
                logger.info("✅ Sync Supabase client initialized")
            except Exception as e:
                logger.error("❌ Ошибка инициализации Sync Supabase: %s", e)
        else:
            logger.warning("⚠️ Supabase не инициализирован (нет ключей)")

    async def _init_async_client(self):
        """Initialize asynchronous Supabase client."""
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                # Close existing client if any
                if self.async_client:
                    await self.async_client.aclose()
                    self.async_client = None

                self.async_client = await create_async_client(SUPABASE_URL, SUPABASE_KEY)
                logger.info("✅ Async Supabase client initialized")
            except Exception as e:
                logger.error("❌ Ошибка инициализации Async Supabase: %s", e)
        else:
            logger.warning("⚠️ Async Supabase не инициализирован (нет ключей)")

    def safe_execute(self, query, retries: int = 3, delay: int = 2):
        """
        Execute query with retries for network errors (sync version).

        Args:
            query: Supabase query object
            retries: Number of retry attempts
            delay: Delay between retries in seconds

        Returns:
            Query result
        """
        for attempt in range(1, retries + 1):
            try:
                return query.execute()
            except (httpx.RemoteProtocolError, httpx.ConnectError) as e:
                logger.warning("⚠️ Попытка %s/%s: ошибка соединения %s", attempt, retries, e)
                if attempt < retries:
                    time.sleep(delay)
                else:
                    raise

    async def async_safe_execute(self, query, retries: int = 3, delay: int = 2):
        """
        Execute query with retries for network errors (async version).

        Args:
            query: Supabase async query object
            retries: Number of retry attempts
            delay: Delay between retries in seconds

        Returns:
            Query result
        """
        for attempt in range(1, retries + 1):
            try:
                return await query.execute()
            except Exception as e:
                logger.warning("⚠️ Попытка %s/%s: ошибка соединения %s", attempt, retries, e)
                if attempt < retries:
                    await asyncio.sleep(delay)
                else:
                    raise e

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
        if self.async_mode:
            # Run async version in sync context
            return asyncio.run(self.async_get_latest_news(source, categories, limit))

        if not self.sync_client:
            logger.warning("⚠️ Sync Supabase не подключён")
            return []

        logger.debug(
            "get_latest_news: source=%s, categories=%s, limit=%s", source, categories, limit
        )

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
            logger.info("✅ Получено %d новостей", len(news_items))
            return news_items
        except Exception as e:
            logger.error("❌ Ошибка получения новостей: %s", e)
            return []

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
        if not self.async_client:
            logger.warning("⚠️ Async Supabase не подключён")
            return []

        logger.debug(
            "async_get_latest_news: source=%s, categories=%s, limit=%s", source, categories, limit
        )

        query = (
            self.async_client.table("news")
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
            logger.info("✅ Async: получено %d новостей", len(news_items))
            return news_items
        except Exception as e:
            logger.error("❌ Ошибка async получения новостей: %s", e)
            return []

    def upsert_news(self, items: List[Dict]) -> int:
        """
        Upsert news items (sync version).

        Args:
            items: List of news dictionaries

        Returns:
            Number of items processed
        """
        if self.async_mode:
            # Run async version in sync context
            return asyncio.run(self.async_upsert_news(items))

        if not self.sync_client:
            logger.warning("⚠️ Sync Supabase не подключён")
            return 0

        if not items:
            logger.info("Нет новостей для вставки")
            return 0

        try:
            # Prepare items for upsert
            rows = self._prepare_news_items(items)

            if not rows:
                logger.info("Нет валидных новостей для вставки")
                return 0

            # Upsert with conflict resolution
            self.safe_execute(
                self.sync_client.table("news").upsert(rows, on_conflict="uid")
            )

            logger.info("✅ Upsert: обработано %d новостей", len(rows))
            return len(rows)

        except Exception as e:
            logger.error("❌ Ошибка upsert новостей: %s", e)
            return 0

    async def async_upsert_news(self, items: List[Dict]) -> int:
        """
        Upsert news items (async version).

        Args:
            items: List of news dictionaries

        Returns:
            Number of items processed
        """
        if not self.async_client:
            logger.warning("⚠️ Async Supabase не подключён")
            return 0

        if not items:
            logger.info("Нет новостей для вставки")
            return 0

        try:
            # Prepare items for upsert
            rows = self._prepare_news_items(items)

            if not rows:
                logger.info("Нет валидных новостей для вставки")
                return 0

            # Upsert with conflict resolution
            await self.async_safe_execute(
                self.async_client.table("news").upsert(rows, on_conflict="uid")
            )

            logger.info("✅ Async upsert: обработано %d новостей", len(rows))
            return len(rows)

        except Exception as e:
            logger.error("❌ Ошибка async upsert новостей: %s", e)
            return 0

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
                    logger.error("Получен не словарь: %s = %s", type(item), item)
                    continue

                # Enrich with AI analysis
                enriched = self._enrich_news_with_ai(item)

                # Extract and validate fields
                title = (
                    (enriched.get("title") or "").strip()
                    or enriched.get("source")
                    or "Без названия"
                )
                content = (
                    (enriched.get("content") or "").strip()
                    or (enriched.get("summary") or "").strip()
                    or title
                )

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
                logger.error("Ошибка подготовки новости: %s, item=%s", e, item)

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
            logger.warning("AI анализ не удался: %s", e)
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

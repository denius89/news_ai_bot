"""
Module: database.service
Purpose: Unified Database Service for PulseAI (Recommended)
Location: database/service.py

Description:
    Современный унифицированный сервис для работы с базой данных через Supabase.
    Поддерживает как синхронные, так и асинхронные операции в едином интерфейсе.

    ✅ РЕКОМЕНДУЕТСЯ: Используйте этот модуль для нового кода вместо db_models

Key Features:
    - Unified API для sync и async операций
    - Retry logic с exponential backoff
    - Proper error handling и logging
    - Type hints для всех методов
    - HTTP/2 workaround для Supabase
    - Factory functions для создания сервисов

Architecture:
    ```python
    class DatabaseService:
        def __init__(self, async_mode: bool = False)

        # Sync methods
        def get_latest_news()
        def upsert_news()
        def get_latest_events()
        def upsert_event()

        # Async methods
        async def async_get_latest_news()
        async def async_upsert_news()
        async def async_get_latest_events()
        async def async_upsert_event()

    # Factory functions
    def get_sync_service() -> DatabaseService
    def get_async_service() -> DatabaseService
    ```

Dependencies:
    External:
        - supabase-py: Supabase Python client
        - httpx: HTTP client with HTTP/2 support
    Internal:
        - config.core.settings: Configuration (правильный путь!)

Usage Example:
    ```python
    from database.service import get_sync_service, get_async_service

    # Sync usage
    db_service = get_sync_service()
    news = db_service.get_latest_news(limit=10)

    # Async usage
    async def fetch_data():
        db_service = get_async_service()
        news = await db_service.async_get_latest_news(limit=10)
        return news
    ```

Migration from db_models:
    ```python
    # Старый способ (db_models):
    from database.db_models import get_latest_news, upsert_news
    news = get_latest_news(limit=10)
    upsert_news(news_items)

    # Новый способ (service):
    from database.service import get_sync_service
    db_service = get_sync_service()
    news = db_service.get_latest_news(limit=10)
    db_service.upsert_news(news_items)
    ```

Advantages over db_models:
    - ✅ Object-oriented design
    - ✅ Async support без сложностей
    - ✅ Proper configuration management
    - ✅ Better error handling
    - ✅ Retry logic
    - ✅ Type safety
    - ✅ Testable (dependency injection ready)

Notes:
    - Загружает конфигурацию из config.core.settings (правильно!)
    - HTTP/2 отключен для избежания pseudo-header errors
    - Использует httpx transport для лучшей производительности
    - Поддерживает как sync, так и async клиенты

Author: PulseAI Team
Last Updated: October 2025
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pathlib import Path
import sys
import threading
from queue import Queue, Empty

import httpx
from supabase import create_client, create_async_client, Client, AsyncClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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

    # Connection pool для переиспользования клиентов
    _sync_pool = Queue(maxsize=5)
    _async_pool = Queue(maxsize=5)
    _pool_initialized = False
    _lock = threading.Lock()

    def __init__(self, async_mode: bool = False):
        """
        Initialize database service.

        Args:
            async_mode: If True, initializes async client. If False, sync client.
        """
        self.async_mode = async_mode
        self.sync_client: Optional[Client] = None
        self.async_client: Optional[AsyncClient] = None

        # Инициализируем pool если нужно
        self._ensure_pool_initialized()

        if async_mode:
            self._init_async_client()
        else:
            self._init_sync_client()

    def _ensure_pool_initialized(self):
        """Инициализация connection pool"""
        if not DatabaseService._pool_initialized:
            with DatabaseService._lock:
                if not DatabaseService._pool_initialized:
                    # Создаем 5 клиентов для pool
                    for _ in range(5):
                        try:
                            sync_client = self._create_sync_client()
                            DatabaseService._sync_pool.put(sync_client)
                        except Exception as e:
                            logger.warning(f"Failed to create sync client for pool: {e}")
                    DatabaseService._pool_initialized = True

    def _get_from_pool(self) -> Optional[Client]:
        """Получить клиент из pool"""
        try:
            return DatabaseService._sync_pool.get_nowait()
        except Empty:
            return None

    def _return_to_pool(self, client: Client):
        """Вернуть клиент в pool"""
        try:
            DatabaseService._sync_pool.put_nowait(client)
        except Exception:
            pass  # Pool full, ignore

    def _init_sync_client(self):
        """Initialize synchronous Supabase client with connection pooling."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.warning("⚠️ Supabase credentials not found")
            return

        # Попробуем получить клиент из pool
        self.sync_client = self._get_from_pool()

        if not self.sync_client:
            # Создаем новый клиент если pool пуст
            try:
                # Принудительно отключаем HTTP/2 для решения pseudo-header ошибки
                import os

                os.environ["HTTPX_NO_HTTP2"] = "1"
                os.environ["SUPABASE_HTTP2_DISABLED"] = "1"

                self.sync_client = self._create_sync_client()
                logger.info("✅ New sync Supabase client created with HTTP/2 disabled")
            except Exception as e:
                logger.error("❌ Failed to initialize Sync Supabase: %s", e)

    def _create_sync_client(self) -> Client:
        """Создать новый sync клиент"""
        return create_client(SUPABASE_URL, SUPABASE_KEY)

    def __del__(self):
        """Возвращаем клиент в pool при удалении объекта"""
        if self.sync_client and not self.async_mode:
            self._return_to_pool(self.sync_client)

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
        days_back: Optional[int] = None,
    ) -> List[Dict]:
        """
        Get latest news (async version).

        Args:
            source: Filter by source name
            categories: Filter by categories
            limit: Maximum number of news items
            days_back: Number of days back to filter (e.g., 7 for last 7 days)

        Returns:
            List of news dictionaries
        """
        try:
            client = await self._get_async_client()
        except Exception as e:
            logger.error("❌ Failed to get async client: %s", e)
            return []

        logger.debug(
            "async_get_latest_news: source=%s, categories=%s, limit=%s, days_back=%s",
            source,
            categories,
            limit,
            days_back,
        )

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
            logger.debug(f"Added category filter: {categories}")

        # Add date filtering if days_back is specified
        if days_back:
            from datetime import datetime, timezone, timedelta

            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            cutoff_iso = cutoff_date.isoformat()
            query = query.gte("published_at", cutoff_iso)
            logger.debug(f"Filtering news from last {days_back} days (since {cutoff_iso})")

        try:
            logger.debug(f"Executing query: categories={categories}, limit={limit}, days_back={days_back}")
            result = await self.async_safe_execute(query)
            news_items = result.data or []
            logger.debug(f"Query returned {len(news_items)} items")

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
        days_back: Optional[int] = None,
    ) -> List[Dict]:
        """
        Get latest news with importance filtering (async version).

        Args:
            source: Filter by source name
            categories: Filter by categories
            limit: Maximum number of news items
            min_importance: Minimum importance threshold
            days_back: Number of days back to filter (e.g., 7 for last 7 days)

        Returns:
            List of news dictionaries sorted by importance
        """
        try:
            client = await self._get_async_client()
        except Exception as e:
            logger.error("❌ Failed to get async client: %s", e)
            return []

        logger.debug(
            "async_get_latest_news_with_importance: source=%s, categories=%s, limit=%s, min_importance=%s, days_back=%s",
            source,
            categories,
            limit,
            min_importance,
            days_back,
        )

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
            logger.debug(f"Added category filter to importance query: {categories}")

        if min_importance is not None:
            query = query.gte("importance", min_importance)
            logger.debug(f"Added importance filter: >= {min_importance}")

        # Add date filtering if days_back is specified
        if days_back:
            from datetime import datetime, timezone, timedelta

            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            cutoff_iso = cutoff_date.isoformat()
            query = query.gte("published_at", cutoff_iso)
            logger.debug(f"Filtering news with importance from last {days_back} days (since {cutoff_iso})")

        try:
            logger.debug(
                f"Executing importance query: categories={categories}, limit={limit}, min_importance={min_importance}, days_back={days_back}"
            )
            result = await self.async_safe_execute(query)
            news_items = result.data or []
            logger.debug(f"Importance query returned {len(news_items)} items")

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
            return await self.async_get_latest_news(source, categories, limit, days_back)

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

    # User Management Methods
    def get_user_by_telegram(self, telegram_id: int) -> Optional[Dict]:
        """
        Get user by Telegram ID.

        Args:
            telegram_id: Telegram user ID

        Returns:
            User data dict or None if not found
        """
        try:
            query = (
                self.sync_client.table("users")
                .select("id, telegram_id, username, categories, sources, notification_enabled, updated_at")
                .eq("telegram_id", telegram_id)
            )
            result = self.safe_execute(query)

            if result.data and len(result.data) > 0:
                return result.data[0]
            return None

        except Exception as e:
            logger.error("❌ Error getting user by telegram_id %d: %s", telegram_id, e)
            return None

    def upsert_user_by_telegram(self, telegram_id: int, user_data: Dict) -> Optional[Dict]:
        """
        Upsert user by Telegram ID.

        Args:
            telegram_id: Telegram user ID
            user_data: User data to upsert

        Returns:
            Upserted user data or None if failed
        """
        try:
            # Add telegram_id to user_data
            user_data["telegram_id"] = telegram_id

            query = self.sync_client.table("users").upsert(user_data)
            result = self.safe_execute(query)

            if result.data and len(result.data) > 0:
                return result.data[0]
            return None

        except Exception as e:
            logger.error("❌ Error upserting user by telegram_id %d: %s", telegram_id, e)
            return None

    # Digest Management Methods
    def save_digest(self, digest_data: Dict) -> Optional[str]:
        """
        Save digest to database.

        Args:
            digest_data: Digest data to save

        Returns:
            Digest ID or None if failed
        """
        try:
            logger.debug(f"🔍 save_digest called with data keys: {digest_data.keys()}")
            query = self.sync_client.table("digests").insert(digest_data)
            logger.debug("🔍 Executing insert query for digest")
            result = self.safe_execute(query)

            logger.debug(
                f"🔍 Insert result: data={result.data is not None}, count={len(result.data) if result.data else 0}"
            )
            if result.data and len(result.data) > 0:
                digest_id = result.data[0]["id"]
                logger.info(f"✅ Digest saved successfully with ID: {digest_id}")
                return digest_id
            else:
                logger.error("❌ save_digest: result.data is empty or None")
                return None

        except Exception as e:
            logger.error("❌ Error saving digest: %s", e)
            import traceback

            logger.error("❌ Traceback: %s", traceback.format_exc())
            return None

    def get_user_digests(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
        include_deleted: bool = False,
        include_archived: bool = False,
    ) -> List[Dict]:
        """
        Get user digests with filtering support.

        Args:
            user_id: User ID
            limit: Maximum number of digests to return
            offset: Number of digests to skip
            include_deleted: Include deleted digests
            include_archived: Include archived digests

        Returns:
            List of digest data
        """
        try:
            query = (
                self.sync_client.table("digests")
                .select(
                    "id, user_id, title, content, category, style, tone, length, audience, "
                    "confidence, feedback_score, created_at, deleted_at, archived"
                )
                .eq("user_id", user_id)
            )

            # Фильтрация по статусу
            if include_deleted and include_archived:
                # Все дайджесты
                pass
            elif include_deleted and not include_archived:
                # Только удаленные (не архивированные)
                query = query.not_.is_("deleted_at", "null")
                query = query.eq("archived", False)
            elif not include_deleted and include_archived:
                # Только архивированные (не удаленные)
                query = query.is_("deleted_at", "null")
                query = query.eq("archived", True)
            else:  # not include_deleted and not include_archived
                # Только активные (не удаленные и не архивированные)
                query = query.is_("deleted_at", "null")
                query = query.eq("archived", False)

            query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

            result = self.safe_execute(query)
            return result.data if result.data else []

        except Exception as e:
            logger.error("❌ Error getting user digests for user %s: %s", user_id, e)
            return []


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
    days_back: Optional[int] = None,
) -> List[Dict]:
    """Backward compatibility function for async_get_latest_news."""
    service = get_async_service()
    return await service.async_get_latest_news(source, categories, limit, days_back)


async def async_upsert_news(items: List[Dict]) -> int:
    """Backward compatibility function for async_upsert_news."""
    service = get_async_service()
    return await service.async_upsert_news(items)

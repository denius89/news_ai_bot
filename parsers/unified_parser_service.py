import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys
import requests
import feedparser
from dateutil import parser as dtp
from utils.clean_text import clean_text  # noqa: E402
from services.categories import get_all_sources  # noqa: E402
from database.service import (
from utils.error_handler import (
            import aiohttp
"""
Unified Parser Service for PulseAI.

This service consolidates both sync and async RSS parsing into a single interface,
eliminating code duplication and providing consistent behavior across all modes.
"""



# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

    upsert_news,
    async_upsert_news,
    get_sync_service,
    get_async_service,
)  # noqa: E402
    handle_network_error,
    handle_parsing_error,
    NetworkError,
    ParsingError,
)  # noqa: E402

logger = logging.getLogger("unified_parser_service")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0; +https://example.com)"}


class UnifiedParserService:
    """
    Unified service for parsing RSS feeds in both sync and async modes.

    This class provides a single interface for all parsing operations,
    automatically choosing between sync and async implementations based on
    the method called.
    """

    def __init__(self, async_mode: bool = False):
        """
        Initialize unified parser service.

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

    def parse_all_sources(
        self, per_source_limit: Optional[int] = None, save_to_db: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Parse all RSS sources (sync version).

        Args:
            per_source_limit: Maximum items per source
            save_to_db: Whether to save results to database

        Returns:
            List of parsed news items
        """
        if self.async_mode:
            # Run async version in sync context
            return asyncio.run(self.async_parse_all_sources(per_source_limit, save_to_db))

        return self._parse_all_sources_sync(per_source_limit, save_to_db)

    async def async_parse_all_sources(
        self, per_source_limit: Optional[int] = None, save_to_db: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Parse all RSS sources (async version).

        Args:
            per_source_limit: Maximum items per source
            save_to_db: Whether to save results to database

        Returns:
            List of parsed news items
        """
        return await self._parse_all_sources_async(per_source_limit, save_to_db)

    def parse_source(
        self,
        url: str,
        category: str,
        subcategory: str,
        source_name: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Parse single RSS source (sync version).

        Args:
            url: RSS feed URL
            category: News category
            subcategory: News subcategory
            source_name: Source name
            limit: Maximum items to parse

        Returns:
            List of parsed news items
        """
        if self.async_mode:
            # Run async version in sync context
            return asyncio.run(
                self.async_parse_source(url, category, subcategory, source_name, limit)
            )

        return self._parse_source_sync(url, category, subcategory, source_name, limit)

    async def async_parse_source(
        self,
        url: str,
        category: str,
        subcategory: str,
        source_name: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Parse single RSS source (async version).

        Args:
            url: RSS feed URL
            category: News category
            subcategory: News subcategory
            source_name: Source name
            limit: Maximum items to parse

        Returns:
            List of parsed news items
        """
        return await self._parse_source_async(url, category, subcategory, source_name, limit)

    def parse_and_save(self, per_source_limit: Optional[int] = None) -> int:
        """
        Parse all sources and save to database (sync version).

        Args:
            per_source_limit: Maximum items per source

        Returns:
            Number of items saved
        """
        if self.async_mode:
            # Run async version in sync context
            return asyncio.run(self.async_parse_and_save(per_source_limit))

        return self._parse_and_save_sync(per_source_limit)

    async def async_parse_and_save(self, per_source_limit: Optional[int] = None) -> int:
        """
        Parse all sources and save to database (async version).

        Args:
            per_source_limit: Maximum items per source

        Returns:
            Number of items saved
        """
        return await self._parse_and_save_async(per_source_limit)

    @handle_parsing_error("all sources")
    def _parse_all_sources_sync(
        self, per_source_limit: Optional[int] = None, save_to_db: bool = True
    ) -> List[Dict[str, Any]]:
        """Internal sync implementation for parsing all sources."""
        try:
            sources = get_all_sources()
            all_news = []

            logger.info("🔄 Парсинг {len(sources)} источников (sync)...")

            for source_info in sources:
                try:
                    news_items = self._parse_source_sync(
                        url=source_info["url"],
                        category=source_info["category"],
                        subcategory=source_info["subcategory"],
                        source_name=source_info["name"],
                        limit=per_source_limit,
                    )
                    all_news.extend(news_items)
                    logger.debug("✅ {source_info['name']}: {len(news_items)} новостей")

                except Exception as e:
                    logger.warning("⚠️ Ошибка парсинга {source_info['name']}: {e}")
                    continue

            logger.info("📊 Всего получено: {len(all_news)} новостей")

            # Save to database if requested
            if save_to_db and all_news:
                saved_count = upsert_news(all_news)
                logger.info("💾 Сохранено в БД: {saved_count} новостей")

            return all_news

        except Exception as e:
            logger.error("❌ Ошибка парсинга всех источников: {e}")
            return []

    @handle_parsing_error("all sources")
    async def _parse_all_sources_async(
        self, per_source_limit: Optional[int] = None, save_to_db: bool = True
    ) -> List[Dict[str, Any]]:
        """Internal async implementation for parsing all sources."""
        try:
            sources = get_all_sources()
            all_news = []

            logger.info("🔄 Парсинг {len(sources)} источников (async)...")

            # Parse sources concurrently
            tasks = []
            for source_info in sources:
                task = self.async_parse_source(
                    url=source_info["url"],
                    category=source_info["category"],
                    subcategory=source_info["subcategory"],
                    source_name=source_info["name"],
                    limit=per_source_limit,
                )
                tasks.append(task)

            # Wait for all parsing tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Collect results
            for i, result in enumerate(results):
                source_name = sources[i]["name"]
                if isinstance(result, Exception):
                    logger.warning("⚠️ Ошибка парсинга {source_name}: {result}")
                else:
                    all_news.extend(result)
                    logger.debug("✅ {source_name}: {len(result)} новостей")

            logger.info("📊 Всего получено: {len(all_news)} новостей")

            # Save to database if requested
            if save_to_db and all_news:
                saved_count = await async_upsert_news(all_news)
                logger.info("💾 Сохранено в БД: {saved_count} новостей")

            return all_news

        except Exception as e:
            logger.error("❌ Ошибка async парсинга всех источников: {e}")
            return []

    @handle_parsing_error("single source")
    def _parse_source_sync(
        self,
        url: str,
        category: str,
        subcategory: str,
        source_name: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Internal sync implementation for parsing single source."""
        try:
            feed = self._fetch_feed(url)
            if not feed:
                return []

            news_items = []
            entries = feed.entries[:limit] if limit else feed.entries

            for entry in entries:
                try:
                    news_item = self._parse_entry(entry, category, subcategory, source_name)
                    if news_item:
                        news_items.append(news_item)
                except Exception as e:
                    logger.warning("⚠️ Ошибка парсинга записи из {source_name}: {e}")
                    continue

            return news_items

        except Exception as e:
            logger.error("❌ Ошибка парсинга источника {source_name}: {e}")
            raise ParsingError(
                "Failed to parse {source_name}", source=source_name, url=url, cause=e
            )

    @handle_parsing_error("single source")
    async def _parse_source_async(
        self,
        url: str,
        category: str,
        subcategory: str,
        source_name: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Internal async implementation for parsing single source."""
        try:
            feed = await self._async_fetch_feed(url)
            if not feed:
                return []

            news_items = []
            entries = feed.entries[:limit] if limit else feed.entries

            for entry in entries:
                try:
                    news_item = self._parse_entry(entry, category, subcategory, source_name)
                    if news_item:
                        news_items.append(news_item)
                except Exception as e:
                    logger.warning("⚠️ Ошибка парсинга записи из {source_name}: {e}")
                    continue

            return news_items

        except Exception as e:
            logger.error("❌ Ошибка парсинга источника {source_name}: {e}")
            raise ParsingError(
                "Failed to parse {source_name}", source=source_name, url=url, cause=e
            )

    @handle_network_error("RSS feed fetch")
    def _fetch_feed(self, url: str):
        """Fetch RSS feed (sync version)."""
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()

            # Parse feed
            feed = feedparser.parse(response.content)

            if feed.bozo:
                logger.warning("⚠️ Bozo feed from {url}: {feed.bozo_exception}")

            return feed

        except requests.RequestException as e:
            raise NetworkError("Failed to fetch RSS feed", url=url, cause=e)

    @handle_network_error("RSS feed fetch")
    async def _async_fetch_feed(self, url: str):
        """Fetch RSS feed (async version)."""
        try:

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=HEADERS, timeout=30) as response:
                    response.raise_for_status()
                    content = await response.read()

                    # Parse feed
                    feed = feedparser.parse(content)

                    if feed.bozo:
                        logger.warning("⚠️ Bozo feed from {url}: {feed.bozo_exception}")

                    return feed

        except Exception as e:
            raise NetworkError("Failed to fetch RSS feed", url=url, cause=e)

    def _parse_entry(
        self, entry: Any, category: str, subcategory: str, source_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse individual RSS entry.

        Args:
            entry: FeedParser entry object
            category: News category
            subcategory: News subcategory
            source_name: Source name

        Returns:
            Parsed news item or None if invalid
        """
        try:
            # Extract basic fields
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary", "").strip()
            published = entry.get("published", "").strip()

            if not title or not link:
                return None

            # Clean and process content
            content = clean_text(summary or title)
            if not content:
                content = title

            # Parse date
            published_at = self._normalize_date(published)

            # Generate UID
            uid = self._make_uid(link, title)

            # Create news item
            news_item = {
                "uid": uid,
                "title": title,
                "content": content,
                "link": link,
                "source": source_name,
                "category": category,
                "subcategory": subcategory,
                "published_at": published_at.isoformat() if published_at else None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            return news_item

        except Exception as e:
            logger.warning("⚠️ Ошибка парсинга записи: {e}")
            return None

    def _normalize_date(self, date_str: str) -> Optional[datetime]:
        """Normalize date string to UTC datetime."""
        if not date_str:
            return None

        try:
            # Try to parse the date
            dt = dtp.parse(date_str)

            # Ensure it's timezone-aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            # Convert to UTC
            return dt.astimezone(timezone.utc)

        except Exception as e:
            logger.debug("⚠️ Ошибка парсинга даты '{date_str}': {e}")
            return None

    def _make_uid(self, url: str, title: str) -> str:
        """Generate unique ID for news item."""
        return hashlib.sha256("{url}|{title}".encode()).hexdigest()

    @handle_parsing_error("parse and save")
    def _parse_and_save_sync(self, per_source_limit: Optional[int] = None) -> int:
        """Internal sync implementation for parse and save."""
        try:
            news_items = self._parse_all_sources_sync(per_source_limit, save_to_db=False)

            if not news_items:
                logger.warning("Нет новостей для сохранения")
                return 0

            # Save to database
            saved_count = upsert_news(news_items)

            logger.info("🎉 Парсинг и сохранение завершены: {saved_count} новостей")
            return saved_count

        except Exception as e:
            logger.error("❌ Ошибка parse_and_save: {e}")
            return 0

    @handle_parsing_error("async parse and save")
    async def _parse_and_save_async(self, per_source_limit: Optional[int] = None) -> int:
        """Internal async implementation for parse and save."""
        try:
            news_items = await self._parse_all_sources_async(per_source_limit, save_to_db=False)

            if not news_items:
                logger.warning("Нет новостей для сохранения")
                return 0

            # Save to database
            saved_count = await async_upsert_news(news_items)

            logger.info("🎉 Async парсинг и сохранение завершены: {saved_count} новостей")
            return saved_count

        except Exception as e:
            logger.error("❌ Ошибка async parse_and_save: {e}")
            return 0

    def get_parser_stats(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about parsed news items.

        Args:
            news_items: List of parsed news items

        Returns:
            Dictionary with parser statistics
        """
        if not news_items:
            return {
                "total_items": 0,
                "sources_count": 0,
                "categories_count": 0,
                "subcategories_count": 0,
                "items_with_dates": 0,
                "avg_content_length": 0,
            }

        sources = set(item.get("source", "") for item in news_items)
        categories = set(item.get("category", "") for item in news_items)
        subcategories = set(item.get("subcategory", "") for item in news_items)

        items_with_dates = sum(1 for item in news_items if item.get("published_at"))
        content_lengths = [len(item.get("content", "")) for item in news_items]
        avg_content_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0

        return {
            "total_items": len(news_items),
            "sources_count": len(sources),
            "categories_count": len(categories),
            "subcategories_count": len(subcategories),
            "items_with_dates": items_with_dates,
            "avg_content_length": round(avg_content_length, 2),
        }


# Global service instances for backward compatibility
_sync_parser_service: Optional[UnifiedParserService] = None
_async_parser_service: Optional[UnifiedParserService] = None


def get_sync_parser_service() -> UnifiedParserService:
    """Get or create sync parser service instance."""
    global _sync_parser_service
    if _sync_parser_service is None:
        _sync_parser_service = UnifiedParserService(async_mode=False)
    return _sync_parser_service


def get_async_parser_service() -> UnifiedParserService:
    """Get or create async parser service instance."""
    global _async_parser_service
    if _async_parser_service is None:
        _async_parser_service = UnifiedParserService(async_mode=True)
    return _async_parser_service


# Backward compatibility functions
def parse_all_sources(per_source_limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Backward compatibility function for parse_all_sources."""
    service = get_sync_parser_service()
    return service.parse_all_sources(per_source_limit, save_to_db=False)


async def async_parse_all_sources(per_source_limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Backward compatibility function for async_parse_all_sources."""
    service = get_async_parser_service()
    return await service.async_parse_all_sources(per_source_limit, save_to_db=False)


def parse_source(
    url: str, category: str, subcategory: str, source_name: str
) -> List[Dict[str, Any]]:
    """Backward compatibility function for parse_source."""
    service = get_sync_parser_service()
    return service.parse_source(url, category, subcategory, source_name)


async def async_parse_source(
    url: str, category: str, subcategory: str, source_name: str
) -> List[Dict[str, Any]]:
    """Backward compatibility function for async_parse_source."""
    service = get_async_parser_service()
    return await service.async_parse_source(url, category, subcategory, source_name)


def parse_and_save(per_source_limit: Optional[int] = None) -> int:
    """Backward compatibility function for parse_and_save."""
    service = get_sync_parser_service()
    return service.parse_and_save(per_source_limit)


async def async_parse_and_save(per_source_limit: Optional[int] = None) -> int:
    """Backward compatibility function for async_parse_and_save."""
    service = get_async_parser_service()
    return await service.async_parse_and_save(per_source_limit)

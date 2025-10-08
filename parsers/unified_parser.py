"""
Unified Parser Service for PulseAI.

This module provides a unified interface for parsing RSS feeds and events,
combining the best features from all existing parsers.
"""

import asyncio
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

import aiohttp
import requests
import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from tenacity import retry, stop_after_attempt, wait_exponential

from services.categories import get_all_sources
from utils.text.clean_text import clean_text
from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance
from database.service import get_sync_service, get_async_service

logger = logging.getLogger("unified_parser")


class UnifiedParser:
    """
    Unified parser for RSS feeds and events.

    This class provides a clean interface for parsing various content types,
    with automatic retry logic, content extraction, and AI analysis.
    """

    def __init__(self, async_mode: bool = False):
        """
        Initialize unified parser.

        Args:
            async_mode: If True, uses async operations
        """
        self.async_mode = async_mode
        if async_mode:
            self.db_service = get_async_service()
        else:
            self.db_service = get_sync_service()

        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; PulseAI/1.0; +https://pulseai.bot)"}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def _fetch_url_async(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Fetch URL content asynchronously with retry logic."""
        try:
            async with session.get(url, headers=self.headers, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _fetch_url_sync(self, url: str) -> Optional[str]:
        """Fetch URL content synchronously with retry logic."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"HTTP {response.status_code} for {url}")
                return None
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            raise

    def normalize_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string and return UTC datetime."""
        if not date_str:
            return None
        try:
            dt = date_parser.parse(date_str)
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception as e:
            logger.warning(f"Failed to parse date: {date_str} ({e})")
            return None

    def make_uid(self, url: str, title: str) -> str:
        """Generate unique ID for content."""
        return hashlib.sha256(f"{url}|{title}".encode()).hexdigest()

    def parse_rss_feed(self, content: str, source_name: str) -> List[Dict]:
        """Parse RSS feed content."""
        try:
            feed = feedparser.parse(content)

            if not feed.entries:
                logger.warning(f"Empty feed: {source_name}")
                return []

            news_items = []
            for entry in feed.entries:
                try:
                    # Clean text
                    title = clean_text(entry.get("title", ""))
                    content_text = clean_text(entry.get("summary", "") or entry.get("description", ""))

                    if not title:
                        continue

                    # Parse date
                    published_at = self.normalize_date(
                        entry.get("published") or entry.get("updated") or str(entry.get("published_parsed", ""))
                    )

                    if not published_at:
                        published_at = datetime.now(timezone.utc)

                    # Create news item
                    news_item = {
                        "uid": self.make_uid(entry.get("link", ""), title),
                        "title": title,
                        "content": content_text,
                        "link": entry.get("link", ""),
                        "source": source_name,
                        "published_at": published_at.isoformat(),
                    }

                    # Add AI analysis
                    try:
                        news_item["credibility"] = evaluate_credibility(news_item)
                        news_item["importance"] = evaluate_importance(news_item)
                    except Exception as e:
                        logger.warning(f"AI analysis failed for {title}: {e}")
                        news_item["credibility"] = 0.5
                        news_item["importance"] = 0.5

                    news_items.append(news_item)

                except Exception as e:
                    logger.warning(f"Error parsing entry from {source_name}: {e}")
                    continue

            logger.info(f"✅ Parsed {source_name}: {len(news_items)} news items")
            return news_items

        except Exception as e:
            logger.error(f"❌ Error parsing RSS feed {source_name}: {e}")
            return []

    async def parse_source_async(self, url: str, category: str, subcategory: str, source_name: str) -> List[Dict]:
        """Parse single RSS source asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                content = await self._fetch_url_async(session, url)

                if not content:
                    return []

                news_items = self.parse_rss_feed(content, source_name)

                # Add category and subcategory
                for item in news_items:
                    item["category"] = category
                    item["subcategory"] = subcategory

                return news_items

        except Exception as e:
            logger.error(f"❌ Error parsing source {source_name}: {e}")
            return []

    def parse_source_sync(self, url: str, category: str, subcategory: str, source_name: str) -> List[Dict]:
        """Parse single RSS source synchronously."""
        try:
            content = self._fetch_url_sync(url)

            if not content:
                return []

            news_items = self.parse_rss_feed(content, source_name)

            # Add category and subcategory
            for item in news_items:
                item["category"] = category
                item["subcategory"] = subcategory

            return news_items

        except Exception as e:
            logger.error(f"❌ Error parsing source {source_name}: {e}")
            return []

    async def parse_all_sources_async(
        self, categories: Optional[List[str]] = None, limit_per_source: int = 5
    ) -> List[Dict]:
        """Parse all RSS sources asynchronously."""
        all_sources = get_all_sources()

        # Filter by categories if specified
        if categories:
            all_sources = [(cat, subcat, name, url) for cat, subcat, name, url in all_sources if cat in categories]

        logger.info(f"Starting async parsing of {len(all_sources)} sources")

        async with aiohttp.ClientSession():
            tasks = []
            for category, subcategory, name, url in all_sources:
                task = self.parse_source_async(url, category, subcategory, name)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten results and limit
        all_news = []
        for result in results:
            if isinstance(result, list):
                all_news.extend(result[:limit_per_source])
            elif isinstance(result, Exception):
                logger.error(f"Task failed: {result}")

        logger.info(f"✅ Async parsing completed: {len(all_news)} total news items")
        return all_news

    def parse_all_sources_sync(self, categories: Optional[List[str]] = None, limit_per_source: int = 5) -> List[Dict]:
        """Parse all RSS sources synchronously."""
        all_sources = get_all_sources()

        # Filter by categories if specified
        if categories:
            all_sources = [(cat, subcat, name, url) for cat, subcat, name, url in all_sources if cat in categories]

        logger.info(f"Starting sync parsing of {len(all_sources)} sources")

        all_news = []
        for category, subcategory, name, url in all_sources:
            try:
                news_items = self.parse_source_sync(url, category, subcategory, name)
                all_news.extend(news_items[:limit_per_source])
            except Exception as e:
                logger.error(f"Error parsing {name}: {e}")

        logger.info(f"✅ Sync parsing completed: {len(all_news)} total news items")
        return all_news

    def parse_events(self, days_ahead: int = 7) -> List[Dict]:
        """Parse economic events from Investing.com."""
        try:
            # Calculate date range
            start_date = datetime.now(timezone.utc)
            end_date = start_date + timedelta(days=days_ahead)

            url = "https://www.investing.com/economic-calendar/"

            content = self._fetch_url_sync(url)
            if not content:
                return []

            soup = BeautifulSoup(content, "html.parser")
            events = []

            # Parse events from the calendar
            event_rows = soup.find_all("tr", {"data-event-datetime": True})

            for row in event_rows:
                try:
                    event_time_str = row.get("data-event-datetime")
                    event_time = self.normalize_date(event_time_str)

                    if not event_time or event_time > end_date:
                        continue

                    # Extract event data
                    cells = row.find_all("td")
                    if len(cells) < 6:
                        continue

                    country = cells[0].get_text(strip=True)
                    title = cells[3].get_text(strip=True)
                    importance_cell = cells[4]

                    # Parse importance
                    importance = 1
                    priority = "low"
                    stars = importance_cell.find_all("i", class_="icon-gray-full-bullish")
                    if stars:
                        star_count = len(stars)
                        importance = min(max(star_count, 1), 3)
                        priority_map = {1: "low", 2: "medium", 3: "high"}
                        priority = priority_map[importance]

                    # Extract additional data
                    fact = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                    forecast = cells[6].get_text(strip=True) if len(cells) > 6 else ""
                    previous = cells[7].get_text(strip=True) if len(cells) > 7 else ""

                    # Create event item
                    event_item = {
                        "event_id": self.make_uid(f"{event_time_str}|{title}", country),
                        "event_time": event_time.isoformat(),
                        "country": country,
                        "title": title,
                        "importance": importance,
                        "priority": priority,
                        "fact": fact,
                        "forecast": forecast,
                        "previous": previous,
                        "source": "investing.com",
                        "category": "economy",
                        "subcategory": "events",
                    }

                    events.append(event_item)

                except Exception as e:
                    logger.warning(f"Error parsing event row: {e}")
                    continue

            logger.info(f"✅ Parsed {len(events)} events")
            return events

        except Exception as e:
            logger.error(f"❌ Error parsing events: {e}")
            return []

    async def save_news_async(self, news_items: List[Dict]) -> int:
        """Save news items to database asynchronously."""
        try:
            return await self.db_service.async_upsert_news(news_items)
        except Exception as e:
            logger.error(f"❌ Error saving news async: {e}")
            return 0

    def save_news_sync(self, news_items: List[Dict]) -> int:
        """Save news items to database synchronously."""
        try:
            return self.db_service.upsert_news(news_items)
        except Exception as e:
            logger.error(f"❌ Error saving news sync: {e}")
            return 0

    def close(self):
        """Close database connections."""
        self.db_service.close()

    async def aclose(self):
        """Close async database connections."""
        await self.db_service.aclose()


# Global service instances
_sync_parser: Optional[UnifiedParser] = None
_async_parser: Optional[UnifiedParser] = None


def get_sync_parser() -> UnifiedParser:
    """Get or create sync parser instance."""
    global _sync_parser
    if _sync_parser is None:
        _sync_parser = UnifiedParser(async_mode=False)
    return _sync_parser


def get_async_parser() -> UnifiedParser:
    """Get or create async parser instance."""
    global _async_parser
    if _async_parser is None:
        _async_parser = UnifiedParser(async_mode=True)
    return _async_parser


# Backward compatibility functions
def parse_source(url: str, category: str, subcategory: str, source_name: str) -> List[Dict]:
    """Backward compatibility function for parsing single source."""
    parser = get_sync_parser()
    return parser.parse_source_sync(url, category, subcategory, source_name)


async def async_parse_source(url: str, category: str, subcategory: str, source_name: str) -> List[Dict]:
    """Backward compatibility function for async parsing single source."""
    parser = get_async_parser()
    return await parser.parse_source_async(url, category, subcategory, source_name)


def parse_all_sources(categories: Optional[List[str]] = None, limit_per_source: int = 5) -> List[Dict]:
    """Backward compatibility function for parsing all sources."""
    parser = get_sync_parser()
    return parser.parse_all_sources_sync(categories, limit_per_source)


async def async_parse_all_sources(categories: Optional[List[str]] = None, limit_per_source: int = 5) -> List[Dict]:
    """Backward compatibility function for async parsing all sources."""
    parser = get_async_parser()
    return await parser.async_parse_all_sources_async(categories, limit_per_source)

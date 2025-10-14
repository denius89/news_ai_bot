"""
Base Provider for PulseAI Event Sources.

This module provides the abstract base class for all event providers.
"""

import hashlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

from events.providers.rate_limiter import get_rate_limiter, RateLimiter

logger = logging.getLogger("base_provider")


class BaseEventProvider(ABC):
    """
    Abstract base class for all event providers.

    All event providers must inherit from this class and implement
    the fetch_events method.
    """

    def __init__(self, name: str, category: str, rate_limiter: Optional[RateLimiter] = None):
        """
        Initialize base provider.

        Args:
            name: Provider name (e.g., 'coingecko', 'football_data')
            category: Event category (e.g., 'crypto', 'sports')
            rate_limiter: Optional custom rate limiter (default: auto from config)
        """
        self.name = name
        self.category = category
        self.session = None

        # Set up rate limiter
        if rate_limiter is not None:
            self.rate_limiter = rate_limiter
        else:
            self.rate_limiter = get_rate_limiter(name)

        logger.info(
            f"Initialized {name} provider for {category} category "
            f"(rate: {self.rate_limiter.calls_per_second:.2f} req/sec)"
        )

    @abstractmethod
    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch events from provider.

        Must return list of dicts with standard fields:
        - title (str): Event title
        - starts_at (datetime): Event start time
        - ends_at (datetime, optional): Event end time
        - subcategory (str): Event subcategory
        - importance (float): Importance score 0.0-1.0
        - description (str, optional): Event description
        - link (str, optional): Event URL
        - location (str, optional): Event location
        - organizer (str, optional): Event organizer
        - metadata (dict, optional): Additional metadata

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries

        Note:
            Use self.rate_limiter.acquire() before making API requests
            to respect rate limits.
        """
        pass

    async def _rate_limited_request(self, session, method: str, url: str, **kwargs):
        """
        Make a rate-limited HTTP request.

        Args:
            session: aiohttp session
            method: HTTP method (get, post, etc.)
            url: Request URL
            **kwargs: Additional arguments for request

        Returns:
            aiohttp response
        """
        await self.rate_limiter.acquire()
        return await getattr(session, method)(url, **kwargs)

    def create_unique_hash(self, title: str, starts_at: datetime, source: str) -> str:
        """
        Create unique hash for event deduplication.

        Args:
            title: Event title
            starts_at: Event start time
            source: Source name

        Returns:
            SHA256 hash string
        """
        raw = f"{title.lower().strip()}|{starts_at.isoformat()}|{source.lower()}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def normalize_event(self, event_data: Dict) -> Dict:
        """
        Normalize event data to standard format.

        Args:
            event_data: Raw event data from provider

        Returns:
            Normalized event dictionary
        """
        starts_at = event_data.get("starts_at")
        if not starts_at:
            logger.warning(f"Event missing starts_at: {event_data.get('title')}")
            return None

        title = event_data.get("title", "").strip()
        if not title:
            logger.warning("Event missing title")
            return None

        normalized = {
            "title": title,
            "category": self.category,
            "subcategory": event_data.get("subcategory", "general"),
            "starts_at": starts_at,
            "ends_at": event_data.get("ends_at"),
            "source": self.name,
            "link": event_data.get("link", ""),
            "importance": float(event_data.get("importance", 0.5)),
            "description": event_data.get("description"),
            "location": event_data.get("location"),
            "organizer": event_data.get("organizer"),
            "unique_hash": self.create_unique_hash(title, starts_at, self.name),
            "metadata": event_data.get("metadata", {}),
            "status": "upcoming",
        }

        return normalized

    async def close(self) -> None:
        """Close HTTP session if exists."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info(f"Closed session for {self.name} provider")

    def get_info(self) -> Dict:
        """
        Get provider information.

        Returns:
            Dictionary with provider metadata
        """
        return {
            "name": self.name,
            "category": self.category,
            "description": f"{self.name} event provider",
        }

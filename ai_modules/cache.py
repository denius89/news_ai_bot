"""
AI Cache module for storing and retrieving AI evaluation results.

This module provides caching for AI importance and credibility scores
to avoid redundant API calls for similar news items.
"""

import hashlib
import logging
import json
import re
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

import yaml

logger = logging.getLogger("cache")


@dataclass
class CacheEntry:
    """Cache entry for AI evaluation results."""

    ai_importance: float
    ai_credibility: float
    ai_summary: Optional[str] = None
    ai_model: str = "gpt-4o-mini"
    processed_at: str = ""
    ttl_expires_at: Optional[str] = None

    def __post_init__(self):
        if not self.processed_at:
            self.processed_at = datetime.now(timezone.utc).isoformat()
        if not self.ttl_expires_at:
            # Set TTL to 3 days by default
            expires = datetime.now(timezone.utc) + timedelta(days=3)
            self.ttl_expires_at = expires.isoformat()


class AICache:
    """
    Cache for AI evaluation results.

    Uses in-memory storage with optional persistence to file.
    Cache key is based on normalized title, link, source, and date.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize cache with configuration."""
        self.config = self._load_config(config_path)
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = self.config.get("cache", {}).get("max_size", 10000)
        self.ttl_seconds = self.config.get("cache", {}).get("ttl_seconds", 0)
        self.ttl_days = self.config.get("cache", {}).get("ttl_days", 3)
        self.partial_update = self.config.get("cache", {}).get("partial_update", True)
        self.key_format = self.config.get("cache", {}).get(
            "dedup_key_format", "{title_norm}|{link_norm}|{source}|{date_yyyy_mm_dd}"
        )

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "ai_optimization.yaml"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def _normalize_text(self, text: str) -> str:
        """Normalize text for consistent hashing."""
        if not text:
            return ""

        # Convert to lowercase, strip whitespace, remove emojis and special chars
        normalized = re.sub(r"[^\w\s]", "", text.lower().strip())
        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing tracking parameters."""
        if not url:
            return ""

        # Remove common tracking parameters
        tracking_params = [
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "fbclid",
            "gclid",
            "ref",
            "source",
            "campaign",
        ]

        # Simple URL cleaning (could be improved with urllib.parse)
        cleaned_url = url
        for param in tracking_params:
            # Remove parameter and its value
            pattern = rf"[?&]{param}=[^&]*"
            cleaned_url = re.sub(pattern, "", cleaned_url)

        # Clean up multiple ? and &
        cleaned_url = re.sub(r"[?&]+", "?", cleaned_url)
        cleaned_url = cleaned_url.rstrip("?&")

        return cleaned_url

    def _generate_cache_key(self, news_item: Dict) -> str:
        """
        Generate cache key for news item.

        Args:
            news_item: Dictionary containing news item data

        Returns:
            Cache key string
        """
        title = news_item.get("title", "")
        link = news_item.get("link", "")
        source = news_item.get("source", "")
        published_at = news_item.get("published_at", "")

        # Normalize inputs
        title_norm = self._normalize_text(title)
        link_norm = self._normalize_url(link)
        source_norm = self._normalize_text(source)

        # Extract date in YYYY-MM-DD format
        date_str = ""
        if published_at:
            try:
                if isinstance(published_at, str):
                    # Try to parse ISO format
                    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    date_str = dt.strftime("%Y-%m-%d")
                else:
                    date_str = published_at.strftime("%Y-%m-%d")
            except Exception:
                date_str = datetime.now().strftime("%Y-%m-%d")

        # Create key using configured format
        key_template = self.key_format
        key = key_template.format(
            title_norm=title_norm, link_norm=link_norm, source=source_norm, date_yyyy_mm_dd=date_str
        )

        # Hash the key for consistent length
        return hashlib.sha1(key.encode("utf-8")).hexdigest()

    def get(self, news_item: Dict) -> Optional[CacheEntry]:
        """
        Get cached AI evaluation results.

        Args:
            news_item: Dictionary containing news item data

        Returns:
            CacheEntry if found and valid, None otherwise
        """
        if not self.is_enabled():
            return None

        cache_key = self._generate_cache_key(news_item)

        if cache_key not in self.cache:
            return None

        entry = self.cache[cache_key]

        # Check TTL if configured
        if self._is_expired(entry):
            # Expired, remove from cache
            del self.cache[cache_key]
            logger.debug(f"[CACHE] expired entry removed: {cache_key[:8]}...")
            return None

        return entry

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        if not self.is_ttl_enabled():
            return False

        try:
            # Use ttl_expires_at if available, otherwise calculate from processed_at
            if entry.ttl_expires_at:
                expires_time = datetime.fromisoformat(entry.ttl_expires_at.replace("Z", "+00:00"))
                return datetime.now(timezone.utc) > expires_time
            else:
                # Fallback to old TTL logic
                processed_time = datetime.fromisoformat(entry.processed_at.replace("Z", "+00:00"))
                age_seconds = (datetime.now(timezone.utc) - processed_time).total_seconds()
                return age_seconds > self.ttl_seconds
        except Exception as e:
            logger.warning(f"Error checking cache TTL: {e}")
            return False

    def needs_refresh(self, entry: CacheEntry) -> bool:
        """Check if cache entry needs refresh (partial update)."""
        if not self.is_ttl_enabled() or not self.partial_update:
            return False

        try:
            # Check if entry is close to expiration (within 1 day)
            if entry.ttl_expires_at:
                expires_time = datetime.fromisoformat(entry.ttl_expires_at.replace("Z", "+00:00"))
                time_until_expiry = (expires_time - datetime.now(timezone.utc)).total_seconds()
                # Refresh if less than 1 day remaining
                return time_until_expiry < 86400
            return False
        except Exception as e:
            logger.warning(f"Error checking refresh need: {e}")
            return False

    def is_ttl_enabled(self) -> bool:
        """Check if TTL is enabled."""
        return self.config.get("features", {}).get("cache_ttl_enabled", True) and (
            self.ttl_seconds > 0 or self.ttl_days > 0
        )

    def set(
        self,
        news_item: Dict,
        importance: float,
        credibility: float,
        summary: Optional[str] = None,
        model: str = "gpt-4o-mini",
    ) -> None:
        """
        Cache AI evaluation results.

        Args:
            news_item: Dictionary containing news item data
            importance: AI importance score
            credibility: AI credibility score
            summary: AI summary (optional)
            model: AI model used
        """
        if not self.is_enabled():
            return

        cache_key = self._generate_cache_key(news_item)

        # Create cache entry with TTL
        entry = CacheEntry(ai_importance=importance, ai_credibility=credibility, ai_summary=summary, ai_model=model)

        # Set TTL expiration time
        if self.is_ttl_enabled():
            ttl_seconds = self.ttl_seconds if self.ttl_seconds > 0 else self.ttl_days * 86400
            expires = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
            entry.ttl_expires_at = expires.isoformat()

        # Store in cache
        self.cache[cache_key] = entry

        # Enforce max size limit
        if len(self.cache) > self.max_size:
            # Remove oldest entries (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        logger.debug(f"Cached AI results for key: {cache_key[:8]}...")

    def update_partial(
        self,
        news_item: Dict,
        importance: Optional[float] = None,
        credibility: Optional[float] = None,
        summary: Optional[str] = None,
    ) -> None:
        """
        Partially update cache entry (only specific fields).

        Args:
            news_item: Dictionary containing news item data
            importance: New importance score (optional)
            credibility: New credibility score (optional)
            summary: New summary (optional)
        """
        if not self.is_enabled():
            return

        cache_key = self._generate_cache_key(news_item)

        if cache_key in self.cache:
            entry = self.cache[cache_key]

            # Update only provided fields
            if importance is not None:
                entry.ai_importance = importance
            if credibility is not None:
                entry.ai_credibility = credibility
            if summary is not None:
                entry.ai_summary = summary

            # Update processed time and TTL
            entry.processed_at = datetime.now(timezone.utc).isoformat()
            if self.is_ttl_enabled():
                ttl_seconds = self.ttl_seconds if self.ttl_seconds > 0 else self.ttl_days * 86400
                expires = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
                entry.ttl_expires_at = expires.isoformat()

            logger.debug(f"[CACHE] partial update for key: {cache_key[:8]}...")

    def is_enabled(self) -> bool:
        """Check if cache is enabled."""
        return self.config.get("features", {}).get("cache_enabled", True)

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "enabled": self.is_enabled(),
        }

    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
        logger.info("Cache cleared")


# Global cache instance
_cache_instance: Optional[AICache] = None


def get_cache() -> AICache:
    """Get global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = AICache()
    return _cache_instance


def get_cached_evaluation(news_item: Dict) -> Optional[CacheEntry]:
    """
    Convenience function to get cached AI evaluation.

    Args:
        news_item: Dictionary containing news item data

    Returns:
        CacheEntry if found, None otherwise
    """
    cache = get_cache()
    return cache.get(news_item)


def cache_evaluation(
    news_item: Dict, importance: float, credibility: float, summary: Optional[str] = None, model: str = "gpt-4o-mini"
) -> None:
    """
    Convenience function to cache AI evaluation.

    Args:
        news_item: Dictionary containing news item data
        importance: AI importance score
        credibility: AI credibility score
        summary: AI summary (optional)
        model: AI model used
    """
    cache = get_cache()
    cache.set(news_item, importance, credibility, summary, model)

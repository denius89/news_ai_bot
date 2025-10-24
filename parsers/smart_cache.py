"""
Module: parsers.smart_cache
Purpose: Smart caching mechanism with ETag/Last-Modified support
Location: parsers/smart_cache.py

Description:
    Умный кэш с поддержкой:
    - ETag / Last-Modified для HTTP 304
    - Stale cache как fallback
    - Статистика hits/misses

Author: PulseAI Team
Last Updated: January 2025
"""

from diskcache import Cache
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import logging

logger = logging.getLogger(__name__)


class SmartCache:
    """
    Умный кэш с поддержкой:
    - ETag / Last-Modified для HTTP 304
    - Stale cache как fallback
    - Статистика hits/misses
    """

    def __init__(self, cache_dir: str = "cache/feeds"):
        self.cache = Cache(cache_dir, size_limit=1024**3)  # 1 GB
        self.metadata = Cache(f"{cache_dir}_meta")
        self.stats = {"hits": 0, "misses": 0, "stale_used": 0}

    def _make_key(self, url: str) -> str:
        """Создать кэш-ключ из URL"""
        return hashlib.md5(url.encode()).hexdigest()

    def get_feed(self, url: str, max_age_hours: int = 6) -> Optional[bytes]:
        """
        Получить закэшированный feed если не устарел

        Args:
            url: URL фида
            max_age_hours: Максимальный возраст кэша (часы)

        Returns:
            Закэшированный контент или None
        """
        key = self._make_key(url)
        cached = self.cache.get(key)

        if cached:
            content, timestamp = cached
            age = datetime.now() - timestamp

            if age < timedelta(hours=max_age_hours):
                self.stats["hits"] += 1
                logger.debug(f"Cache HIT: {url} (age: {age})")
                return content
            else:
                logger.debug(f"Cache EXPIRED: {url} (age: {age})")

        self.stats["misses"] += 1
        return None

    def get_conditional_headers(self, url: str) -> dict:
        """
        Получить заголовки для conditional request (304 Not Modified)

        Если есть ETag/Last-Modified - вернем их для HTTP запроса.
        Сервер может ответить 304, и мы возьмем контент из кэша.
        """
        meta = self.metadata.get(url)
        headers = {}

        if meta:
            if meta.get("etag"):
                headers["If-None-Match"] = meta["etag"]
            if meta.get("last_modified"):
                headers["If-Modified-Since"] = meta["last_modified"]

            if headers:
                logger.debug(f"Conditional headers for {url}: {list(headers.keys())}")

        return headers

    def save_feed_with_meta(
        self, url: str, content: bytes, etag: Optional[str] = None, last_modified: Optional[str] = None
    ):
        """
        Сохранить feed с метаданными для conditional requests

        Args:
            url: URL фида
            content: Контент для кэширования
            etag: ETag из HTTP response
            last_modified: Last-Modified из HTTP response
        """
        key = self._make_key(url)

        # Сохранить контент с timestamp
        self.cache.set(key, (content, datetime.now()), expire=86400 * 7)  # 7 дней

        # Сохранить метаданные отдельно (не истекают)
        if etag or last_modified:
            self.metadata.set(
                url, {"etag": etag, "last_modified": last_modified, "updated_at": datetime.now().isoformat()}
            )
            logger.debug(f"Saved metadata for {url}")

    def get_stale(self, url: str) -> Optional[bytes]:
        """
        Получить устаревший кэш как последний fallback

        Используется когда все попытки fetch провалились,
        но лучше показать старые данные чем ничего.
        """
        key = self._make_key(url)
        cached = self.cache.get(key)

        if cached:
            content, timestamp = cached
            age = datetime.now() - timestamp
            self.stats["stale_used"] += 1
            logger.warning(f"Using STALE cache: {url} (age: {age})")
            return content

        return None

    def clear_old_entries(self, max_age_days: int = 30):
        """Очистить кэш старше N дней"""
        # diskcache автоматически управляет размером, но можно добавить очистку
        pass

    def get_stats(self) -> dict:
        """Статистика для мониторинга"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0

        return {**self.stats, "hit_rate_percent": round(hit_rate, 2), "cache_size_mb": self.cache.size / (1024**2)}

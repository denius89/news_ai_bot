"""
Caching Utilities for PulseAI.

This module provides caching functionality for improving performance
of database queries and API calls.
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger("cache")


class MemoryCache:
    """
    Simple in-memory cache with TTL support.
    """
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    def _make_key(self, key: Union[str, Dict]) -> str:
        """Convert key to string."""
        if isinstance(key, dict):
            key_str = json.dumps(key, sort_keys=True)
            return hashlib.md5(key_str.encode()).hexdigest()
        return str(key)
    
    async def get(self, key: Union[str, Dict]) -> Optional[Any]:
        """Get value from cache."""
        cache_key = self._make_key(key)
        
        async with self._lock:
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if entry['expires'] > time.time():
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return entry['value']
                else:
                    # Expired, remove it
                    del self.cache[cache_key]
                    logger.debug(f"Cache expired for key: {cache_key}")
        
        logger.debug(f"Cache miss for key: {cache_key}")
        return None
    
    async def set(self, key: Union[str, Dict], value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        cache_key = self._make_key(key)
        expires = time.time() + (ttl or self.default_ttl)
        
        async with self._lock:
            self.cache[cache_key] = {
                'value': value,
                'expires': expires,
                'created': time.time()
            }
            logger.debug(f"Cache set for key: {cache_key}, TTL: {ttl or self.default_ttl}s")
    
    async def delete(self, key: Union[str, Dict]) -> bool:
        """Delete key from cache."""
        cache_key = self._make_key(key)
        
        async with self._lock:
            if cache_key in self.cache:
                del self.cache[cache_key]
                logger.debug(f"Cache deleted for key: {cache_key}")
                return True
        return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self.cache.clear()
            logger.info("Cache cleared")
    
    async def cleanup_expired(self) -> int:
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = []
        
        async with self._lock:
            for key, entry in self.cache.items():
                if entry['expires'] <= current_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        current_time = time.time()
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if entry['expires'] <= current_time)
        
        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_entries,
            'expired_entries': expired_entries,
            'hit_ratio': getattr(self, '_hit_ratio', 0.0)
        }


class CacheManager:
    """
    Centralized cache manager for the application.
    """
    
    def __init__(self):
        self.caches: Dict[str, MemoryCache] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def get_cache(self, name: str, default_ttl: int = 300) -> MemoryCache:
        """Get or create a named cache."""
        if name not in self.caches:
            self.caches[name] = MemoryCache(default_ttl=default_ttl)
        return self.caches[name]
    
    async def start_cleanup_task(self, interval: int = 300) -> None:
        """Start periodic cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop(interval))
            logger.info(f"Started cache cleanup task with {interval}s interval")
    
    async def stop_cleanup_task(self) -> None:
        """Stop periodic cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped cache cleanup task")
    
    async def _cleanup_loop(self, interval: int) -> None:
        """Periodic cleanup loop."""
        while True:
            try:
                await asyncio.sleep(interval)
                total_cleaned = 0
                for cache in self.caches.values():
                    total_cleaned += await cache.cleanup_expired()
                
                if total_cleaned > 0:
                    logger.info(f"Cleanup cycle completed: {total_cleaned} entries removed")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup loop: {e}")
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches."""
        stats = {}
        for name, cache in self.caches.items():
            stats[name] = cache.get_stats()
        return stats


# Global cache manager instance
_cache_manager = CacheManager()


def get_cache(name: str, default_ttl: int = 300) -> MemoryCache:
    """Get a named cache instance."""
    return _cache_manager.get_cache(name, default_ttl)


def get_cache_manager() -> CacheManager:
    """Get the global cache manager."""
    return _cache_manager


# Cache decorators
def cached(cache_name: str = "default", ttl: int = 300):
    """
    Decorator for caching function results.
    
    Args:
        cache_name: Name of the cache to use
        ttl: Time to live in seconds
    """
    def decorator(func):
        cache = get_cache(cache_name, ttl)
        
        if asyncio.iscoroutinefunction(func):
            @asyncio.coroutine
            async def async_wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                cache_key = {
                    'func': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                }
                
                # Try to get from cache
                result = await cache.get(cache_key)
                if result is not None:
                    return result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await cache.set(cache_key, result, ttl)
                return result
            
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                cache_key = {
                    'func': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                }
                
                # Try to get from cache (sync version)
                import asyncio
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(cache.get(cache_key))
                if result is not None:
                    return result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                loop.run_until_complete(cache.set(cache_key, result, ttl))
                return result
            
            return sync_wrapper
    
    return decorator


# Specialized caches
def get_news_cache() -> MemoryCache:
    """Get cache for news data."""
    return get_cache("news", default_ttl=600)  # 10 minutes


def get_user_cache() -> MemoryCache:
    """Get cache for user data."""
    return get_cache("users", default_ttl=1800)  # 30 minutes


def get_categories_cache() -> MemoryCache:
    """Get cache for categories data."""
    return get_cache("categories", default_ttl=3600)  # 1 hour


def get_digest_cache() -> MemoryCache:
    """Get cache for digest data."""
    return get_cache("digests", default_ttl=300)  # 5 minutes

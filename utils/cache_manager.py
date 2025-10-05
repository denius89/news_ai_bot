"""
Cache Manager for PulseAI.

This module provides a unified caching system with Redis support,
memory cache fallback, and intelligent cache invalidation.
"""

import json
import time
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
from datetime import datetime, timedelta
from pathlib import Path

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger("cache_manager")


class CacheManager:
    """
    Unified cache manager with Redis and memory fallback.
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl: int = 3600,
        max_memory_size: int = 1000,
        enable_memory_cache: bool = True
    ):
        """
        Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default time-to-live in seconds
            max_memory_size: Maximum items in memory cache
            enable_memory_cache: Whether to enable memory cache fallback
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.max_memory_size = max_memory_size
        self.enable_memory_cache = enable_memory_cache
        
        # Memory cache fallback
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.memory_access_times: Dict[str, float] = {}
        
        # Redis connection
        self.redis_client: Optional[redis.Redis] = None
        self.redis_available = False
        
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE or not self.redis_url:
            logger.info("Redis not available, using memory cache only")
            return
        
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis cache connected successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}, using memory cache")
            self.redis_client = None
            self.redis_available = False
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments."""
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            elif isinstance(arg, (list, tuple)):
                key_parts.append(",".join(str(x) for x in arg))
            elif isinstance(arg, dict):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                key_parts.append(str(hash(str(arg))))
        
        # Add keyword arguments
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            for key, value in sorted_kwargs:
                if isinstance(value, (str, int, float, bool)):
                    key_parts.append(f"{key}:{value}")
                elif isinstance(value, (list, tuple)):
                    key_parts.append(f"{key}:{','.join(str(x) for x in value)}")
                elif isinstance(value, dict):
                    key_parts.append(f"{key}:{json.dumps(value, sort_keys=True)}")
                else:
                    key_parts.append(f"{key}:{hash(str(value))}")
        
        # Create hash of the key parts to avoid too long keys
        key_string = "|".join(key_parts)
        if len(key_string) > 250:  # Redis key length limit
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        
        return key_string
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        # Try Redis first
        if self.redis_available and self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value is not None:
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get error for key {key}: {e}")
        
        # Fallback to memory cache
        if self.enable_memory_cache and key in self.memory_cache:
            cache_entry = self.memory_cache[key]
            
            # Check if expired
            if cache_entry["expires_at"] > time.time():
                self.memory_access_times[key] = time.time()
                return cache_entry["value"]
            else:
                # Remove expired entry
                del self.memory_cache[key]
                if key in self.memory_access_times:
                    del self.memory_access_times[key]
        
        return default
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            tags: Cache tags for invalidation
            
        Returns:
            True if successful, False otherwise
        """
        if ttl is None:
            ttl = self.default_ttl
        
        expires_at = time.time() + ttl
        cache_entry = {
            "value": value,
            "expires_at": expires_at,
            "created_at": time.time(),
            "tags": tags or []
        }
        
        # Try Redis first
        if self.redis_available and self.redis_client:
            try:
                # Store in Redis with TTL
                redis_value = json.dumps(cache_entry)
                result = self.redis_client.setex(key, ttl, redis_value)
                
                # Store tags for invalidation
                if tags:
                    for tag in tags:
                        self.redis_client.sadd(f"tag:{tag}", key)
                        self.redis_client.expire(f"tag:{tag}", ttl)
                
                return bool(result)
                
            except Exception as e:
                logger.warning(f"Redis set error for key {key}: {e}")
        
        # Fallback to memory cache
        if self.enable_memory_cache:
            # Remove oldest entries if cache is full
            if len(self.memory_cache) >= self.max_memory_size:
                self._cleanup_memory_cache()
            
            self.memory_cache[key] = cache_entry
            self.memory_access_times[key] = time.time()
            return True
        
        return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted, False otherwise
        """
        deleted = False
        
        # Delete from Redis
        if self.redis_available and self.redis_client:
            try:
                deleted = bool(self.redis_client.delete(key))
            except Exception as e:
                logger.warning(f"Redis delete error for key {key}: {e}")
        
        # Delete from memory cache
        if self.enable_memory_cache and key in self.memory_cache:
            del self.memory_cache[key]
            if key in self.memory_access_times:
                del self.memory_access_times[key]
            deleted = True
        
        return deleted
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """
        Invalidate cache entries by tags.
        
        Args:
            tags: List of tags to invalidate
            
        Returns:
            Number of keys invalidated
        """
        invalidated_count = 0
        
        if not self.redis_available or not self.redis_client:
            # Memory cache doesn't support tag-based invalidation efficiently
            return 0
        
        try:
            for tag in tags:
                tag_key = f"tag:{tag}"
                keys = self.redis_client.smembers(tag_key)
                
                if keys:
                    invalidated_count += self.redis_client.delete(*keys)
                    self.redis_client.delete(tag_key)
                    
        except Exception as e:
            logger.warning(f"Redis tag invalidation error: {e}")
        
        return invalidated_count
    
    def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful, False otherwise
        """
        cleared = False
        
        # Clear Redis
        if self.redis_available and self.redis_client:
            try:
                self.redis_client.flushdb()
                cleared = True
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")
        
        # Clear memory cache
        if self.enable_memory_cache:
            self.memory_cache.clear()
            self.memory_access_times.clear()
            cleared = True
        
        return cleared
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            "redis_available": self.redis_available,
            "memory_cache_size": len(self.memory_cache),
            "memory_cache_max_size": self.max_memory_size,
            "memory_cache_usage": len(self.memory_cache) / self.max_memory_size * 100,
            "default_ttl": self.default_ttl
        }
        
        if self.redis_available and self.redis_client:
            try:
                redis_info = self.redis_client.info()
                stats.update({
                    "redis_used_memory": redis_info.get("used_memory_human", "unknown"),
                    "redis_connected_clients": redis_info.get("connected_clients", 0),
                    "redis_keyspace_hits": redis_info.get("keyspace_hits", 0),
                    "redis_keyspace_misses": redis_info.get("keyspace_misses", 0)
                })
            except Exception as e:
                logger.warning(f"Redis stats error: {e}")
        
        return stats
    
    def _cleanup_memory_cache(self):
        """Clean up memory cache by removing oldest entries."""
        if len(self.memory_cache) < self.max_memory_size:
            return
        
        # Sort by access time and remove oldest 10%
        sorted_keys = sorted(
            self.memory_access_times.keys(),
            key=lambda k: self.memory_access_times[k]
        )
        
        keys_to_remove = sorted_keys[:max(1, len(sorted_keys) // 10)]
        
        for key in keys_to_remove:
            if key in self.memory_cache:
                del self.memory_cache[key]
            if key in self.memory_access_times:
                del self.memory_access_times[key]


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager(
    redis_url: Optional[str] = None,
    default_ttl: int = 3600,
    max_memory_size: int = 1000
) -> CacheManager:
    """
    Get global cache manager instance.
    
    Args:
        redis_url: Redis connection URL
        default_ttl: Default TTL in seconds
        max_memory_size: Maximum memory cache size
        
    Returns:
        CacheManager instance
    """
    global _cache_manager
    
    if _cache_manager is None:
        _cache_manager = CacheManager(
            redis_url=redis_url,
            default_ttl=default_ttl,
            max_memory_size=max_memory_size
        )
    
    return _cache_manager


def cached(
    ttl: int = 3600,
    tags: Optional[List[str]] = None,
    key_prefix: str = "cache",
    cache_manager: Optional[CacheManager] = None
):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time-to-live in seconds
        tags: Cache tags for invalidation
        key_prefix: Key prefix for cache keys
        cache_manager: Cache manager instance (uses global if None)
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            manager = cache_manager or get_cache_manager()
            
            # Generate cache key
            cache_key = manager._make_key(
                key_prefix,
                func.__name__,
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_result = manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            manager.set(cache_key, result, ttl=ttl, tags=tags)
            logger.debug(f"Cached result for {func.__name__}: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def cache_invalidate(tags: List[str], cache_manager: Optional[CacheManager] = None) -> int:
    """
    Invalidate cache entries by tags.
    
    Args:
        tags: List of tags to invalidate
        cache_manager: Cache manager instance (uses global if None)
        
    Returns:
        Number of keys invalidated
    """
    manager = cache_manager or get_cache_manager()
    return manager.invalidate_by_tags(tags)


def cache_clear(cache_manager: Optional[CacheManager] = None) -> bool:
    """
    Clear all cache entries.
    
    Args:
        cache_manager: Cache manager instance (uses global if None)
        
    Returns:
        True if successful
    """
    manager = cache_manager or get_cache_manager()
    return manager.clear()


def cache_stats(cache_manager: Optional[CacheManager] = None) -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Args:
        cache_manager: Cache manager instance (uses global if None)
        
    Returns:
        Dictionary with cache statistics
    """
    manager = cache_manager or get_cache_manager()
    return manager.get_stats()


# Convenience functions for common cache operations
def cache_news_items(category: str, subcategory: str, items: List[Dict], ttl: int = 1800):
    """Cache news items with category-specific TTL."""
    cache_manager = get_cache_manager()
    cache_key = cache_manager._make_key("news", category, subcategory)
    cache_manager.set(cache_key, items, ttl=ttl, tags=[f"news:{category}", f"news:{category}:{subcategory}"])
    return len(items)


def get_cached_news_items(category: str, subcategory: str) -> Optional[List[Dict]]:
    """Get cached news items."""
    cache_manager = get_cache_manager()
    cache_key = cache_manager._make_key("news", category, subcategory)
    return cache_manager.get(cache_key)


def cache_user_subscriptions(user_id: int, subscriptions: Dict[str, Any], ttl: int = 3600):
    """Cache user subscriptions."""
    cache_manager = get_cache_manager()
    cache_key = cache_manager._make_key("user_subscriptions", user_id)
    cache_manager.set(cache_key, subscriptions, ttl=ttl, tags=[f"user:{user_id}", "subscriptions"])
    return len(subscriptions)


def get_cached_user_subscriptions(user_id: int) -> Optional[Dict[str, Any]]:
    """Get cached user subscriptions."""
    cache_manager = get_cache_manager()
    cache_key = cache_manager._make_key("user_subscriptions", user_id)
    return cache_manager.get(cache_key)


def cache_ai_analysis(content_hash: str, analysis: Dict[str, float], ttl: int = 7200):
    """Cache AI analysis results."""
    cache_manager = get_cache_manager()
    cache_key = cache_manager._make_key("ai_analysis", content_hash)
    cache_manager.set(cache_key, analysis, ttl=ttl, tags=["ai_analysis"])
    return analysis


def get_cached_ai_analysis(content_hash: str) -> Optional[Dict[str, float]]:
    """Get cached AI analysis."""
    cache_manager = get_cache_manager()
    cache_key = cache_manager._make_key("ai_analysis", content_hash)
    return cache_manager.get(cache_key)

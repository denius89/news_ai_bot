"""
Rate Limit Manager for PulseAI Event Intelligence.

This module provides smart rate limiting and caching for all event API providers.
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json

logger = logging.getLogger("rate_limit_manager")

# Rate limit configuration for all providers
RATE_LIMITS = {
    'coinmarketcal': {'requests': 100, 'period': 86400, 'cache_ttl': 43200},  # 100/day, cache 12h
    'fmp': {'requests': 250, 'period': 86400, 'cache_ttl': 3600},  # 250/day, cache 1h
    'finnhub': {'requests': 60, 'period': 60, 'cache_ttl': 300},  # 60/min, cache 5min
    'football_data': {'requests': 10, 'period': 60, 'cache_ttl': 900},  # 10/min, cache 15min
    'pandascore': {'requests': 100, 'period': 86400, 'cache_ttl': 7200},  # 100/day, cache 2h
    'thesportsdb': {'requests': 100, 'period': 3600, 'cache_ttl': 1800},  # 100/h, cache 30min
    'github_releases': {'requests': 60, 'period': 3600, 'cache_ttl': 3600},  # 60/h, cache 1h
    'coingecko': {'requests': 50, 'period': 60, 'cache_ttl': 600},  # 50/min, cache 10min
    'defillama': {'requests': 300, 'period': 300, 'cache_ttl': 600},  # 300/5min, cache 10min
    'tokenunlocks': {'requests': 100, 'period': 3600, 'cache_ttl': 1800},  # 100/h, cache 30min
    'eodhd': {'requests': 100, 'period': 86400, 'cache_ttl': 3600},  # 100/day, cache 1h
    'oecd': {'requests': 50, 'period': 3600, 'cache_ttl': 21600},  # 50/h, cache 6h (HTML scraping)
}


class RateLimitManager:
    """
    Manages rate limits for all API providers.
    
    Features:
    - Request tracking per provider
    - Automatic wait time calculation
    - Smart caching with TTL
    - Rate limit logging and monitoring
    """
    
    def __init__(self):
        """Initialize rate limit manager."""
        self.request_history = defaultdict(list)
        self.cache = {}
        self.cache_timestamps = {}
        self.limit_exceeded_count = defaultdict(int)
        
        logger.info("RateLimitManager initialized")
    
    def can_make_request(self, provider: str) -> bool:
        """
        Check if request can be made within rate limit.
        
        Args:
            provider: Provider name
            
        Returns:
            True if request can be made, False otherwise
        """
        if provider not in RATE_LIMITS:
            logger.debug(f"No rate limit configured for {provider}, allowing request")
            return True
        
        config = RATE_LIMITS[provider]
        now = time.time()
        period = config['period']
        
        # Clean old requests
        self.request_history[provider] = [
            ts for ts in self.request_history[provider]
            if now - ts < period
        ]
        
        # Check limit
        current_requests = len(self.request_history[provider])
        max_requests = config['requests']
        
        can_request = current_requests < max_requests
        
        if not can_request:
            self.limit_exceeded_count[provider] += 1
            logger.warning(
                f"Rate limit exceeded for {provider}: "
                f"{current_requests}/{max_requests} requests in {period}s"
            )
        
        return can_request
    
    def record_request(self, provider: str):
        """
        Record a request for rate limiting.
        
        Args:
            provider: Provider name
        """
        now = time.time()
        self.request_history[provider].append(now)
        
        logger.debug(
            f"Recorded request for {provider}: "
            f"{len(self.request_history[provider])} requests in current period"
        )
    
    def get_cached(self, provider: str, key: str) -> Optional[Dict]:
        """
        Get cached data if still valid.
        
        Args:
            provider: Provider name
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        if provider not in RATE_LIMITS:
            return None
        
        cache_key = f"{provider}:{key}"
        if cache_key not in self.cache:
            return None
        
        config = RATE_LIMITS[provider]
        cache_time = self.cache_timestamps.get(cache_key, 0)
        
        if time.time() - cache_time < config['cache_ttl']:
            logger.info(f"Cache HIT: {cache_key}")
            return self.cache[cache_key]
        
        logger.info(f"Cache MISS: {cache_key} (expired)")
        # Clean expired cache
        del self.cache[cache_key]
        del self.cache_timestamps[cache_key]
        return None
    
    def set_cache(self, provider: str, key: str, data: Any):
        """
        Cache data for provider.
        
        Args:
            provider: Provider name
            key: Cache key
            data: Data to cache
        """
        cache_key = f"{provider}:{key}"
        self.cache[cache_key] = data
        self.cache_timestamps[cache_key] = time.time()
        logger.info(f"Cache SET: {cache_key}")
    
    def get_wait_time(self, provider: str) -> float:
        """
        Get time to wait before next request.
        
        Args:
            provider: Provider name
            
        Returns:
            Wait time in seconds (0.0 if can make request now)
        """
        if provider not in RATE_LIMITS:
            return 0.0
        
        config = RATE_LIMITS[provider]
        now = time.time()
        period = config['period']
        
        # Clean old requests
        self.request_history[provider] = [
            ts for ts in self.request_history[provider]
            if now - ts < period
        ]
        
        if len(self.request_history[provider]) < config['requests']:
            return 0.0
        
        # Calculate wait time
        oldest_request = min(self.request_history[provider])
        wait_time = period - (now - oldest_request)
        return max(0.0, wait_time)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get rate limit statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            "providers": {},
            "total_cached_items": len(self.cache),
            "total_limit_exceeded": sum(self.limit_exceeded_count.values()),
        }
        
        for provider, config in RATE_LIMITS.items():
            now = time.time()
            period = config['period']
            
            # Count current requests
            current_requests = len([
                ts for ts in self.request_history[provider]
                if now - ts < period
            ])
            
            stats["providers"][provider] = {
                "current_requests": current_requests,
                "max_requests": config['requests'],
                "period_seconds": period,
                "cache_ttl": config['cache_ttl'],
                "limit_exceeded_count": self.limit_exceeded_count[provider],
                "can_request": current_requests < config['requests'],
                "wait_time": self.get_wait_time(provider),
            }
        
        return stats
    
    def clear_cache(self, provider: Optional[str] = None):
        """
        Clear cache for provider or all providers.
        
        Args:
            provider: Provider name (None for all)
        """
        if provider is None:
            self.cache.clear()
            self.cache_timestamps.clear()
            logger.info("Cleared all cache")
        else:
            keys_to_remove = [k for k in self.cache.keys() if k.startswith(f"{provider}:")]
            for key in keys_to_remove:
                del self.cache[key]
                del self.cache_timestamps[key]
            logger.info(f"Cleared cache for {provider}: {len(keys_to_remove)} items")


# Global instance
_rate_limit_manager = None


def get_rate_limit_manager() -> RateLimitManager:
    """Get global Rate Limit Manager instance."""
    global _rate_limit_manager
    if _rate_limit_manager is None:
        _rate_limit_manager = RateLimitManager()
    return _rate_limit_manager


__all__ = ["RateLimitManager", "get_rate_limit_manager", "RATE_LIMITS"]


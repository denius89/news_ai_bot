"""
Rate Limiter for API providers.

Implements token bucket algorithm for rate limiting API requests.
"""

import asyncio
import logging
import time
from typing import Dict, Optional

logger = logging.getLogger("rate_limiter")


class RateLimiter:
    """
    Token bucket rate limiter for API requests.

    Features:
    - Token bucket algorithm
    - Configurable rates (requests per second/minute/hour)
    - Async-safe
    - Per-provider instances
    """

    def __init__(
        self,
        calls_per_second: Optional[float] = None,
        calls_per_minute: Optional[float] = None,
        calls_per_hour: Optional[float] = None,
        calls_per_day: Optional[float] = None,
    ):
        """
        Initialize rate limiter.

        Args:
            calls_per_second: Maximum calls per second
            calls_per_minute: Maximum calls per minute
            calls_per_hour: Maximum calls per hour
            calls_per_day: Maximum calls per day

        Note: Only one limit should be specified. If multiple are given,
              the most restrictive will be used.
        """
        # Convert all to calls_per_second
        rates = []

        if calls_per_second is not None:
            rates.append(calls_per_second)
        if calls_per_minute is not None:
            rates.append(calls_per_minute / 60.0)
        if calls_per_hour is not None:
            rates.append(calls_per_hour / 3600.0)
        if calls_per_day is not None:
            rates.append(calls_per_day / 86400.0)

        if not rates:
            # Default: 1 request per second
            self.calls_per_second = 1.0
        else:
            # Use most restrictive rate
            self.calls_per_second = min(rates)

        self.min_interval = 1.0 / self.calls_per_second
        self.last_call = 0
        self._lock = asyncio.Lock()

        logger.info(
            f"RateLimiter initialized: {self.calls_per_second:.2f} calls/sec "
            f"(min interval: {self.min_interval:.2f}s)"
        )

    async def acquire(self) -> None:
        """
        Acquire permission to make a request.

        Blocks until rate limit allows the request.
        """
        async with self._lock:
            now = time.time()
            time_since_last = now - self.last_call

            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                logger.debug(f"Rate limit: sleeping {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)

            self.last_call = time.time()

    def get_info(self) -> Dict[str, float]:
        """Get rate limiter information."""
        return {
            "calls_per_second": self.calls_per_second,
            "min_interval_sec": self.min_interval,
            "calls_per_minute": self.calls_per_second * 60,
            "calls_per_hour": self.calls_per_second * 3600,
        }


# Predefined rate limiters for common APIs
RATE_LIMITERS = {
    # Sports
    "football_data": RateLimiter(calls_per_minute=10),  # 10 req/min (FREE tier)
    "thesportsdb": RateLimiter(calls_per_minute=30),  # Increased from hourly
    "pandascore": RateLimiter(calls_per_minute=50),  # ~1000 req/hour
    "liquipedia": RateLimiter(calls_per_minute=10),  # MediaWiki: reasonable
    "liquipedia_parse": RateLimiter(calls_per_minute=2),  # action=parse: 2/min
    "gosugamers": RateLimiter(calls_per_minute=6),  # RSS: every 10 seconds
    # Crypto
    "coinmarketcal": RateLimiter(calls_per_minute=5),  # ~100/day = reasonable 5/min
    "coingecko": RateLimiter(calls_per_minute=10),  # Free: 10-50/min, use 10
    "defillama": RateLimiter(calls_per_second=2),  # Increased
    "tokenunlocks": RateLimiter(calls_per_second=2),  # Increased
    # Markets
    "finnhub": RateLimiter(calls_per_minute=60),  # Free: 60 req/min
    "eodhd": RateLimiter(calls_per_second=2),  # Increased
    "fmp": RateLimiter(calls_per_second=2),  # Increased
    "nasdaq_rss": RateLimiter(calls_per_minute=6),  # RSS: every 10 sec
    "oecd_events": RateLimiter(calls_per_minute=10),  # Increased
    # Tech
    "github_releases": RateLimiter(calls_per_minute=80),  # ~5000/hour = 83/min
    "lf_events": RateLimiter(calls_per_minute=10),  # ICS/HTML: reasonable
    "cncf_events": RateLimiter(calls_per_minute=10),  # ICS/HTML: reasonable
    "wikidata": RateLimiter(calls_per_second=2),  # SPARQL: reasonable
    # World
    "un_sc": RateLimiter(calls_per_minute=10),  # HTML: reasonable
    "eu_council": RateLimiter(calls_per_minute=10),  # HTML: reasonable
    "ifes": RateLimiter(calls_per_minute=10),  # HTML: reasonable
    "unfccc": RateLimiter(calls_per_minute=10),  # HTML: reasonable
}


def get_rate_limiter(provider_name: str) -> RateLimiter:
    """
    Get rate limiter for a provider.

    Args:
        provider_name: Provider name (e.g., 'football_data', 'coingecko')

    Returns:
        RateLimiter instance
    """
    if provider_name in RATE_LIMITERS:
        return RATE_LIMITERS[provider_name]

    # Default: conservative 1 req/sec
    logger.warning(f"No rate limiter configured for '{provider_name}', " f"using default (1 req/sec)")
    return RateLimiter(calls_per_second=1)

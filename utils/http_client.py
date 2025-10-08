"""
HTTP Client with Connection Pooling for PulseAI.

This module provides optimized HTTP clients with connection pooling
for better performance and resource management.
"""

import asyncio
import logging
from typing import Dict, Optional
from contextlib import asynccontextmanager

import aiohttp
import httpx

logger = logging.getLogger("http_client")


class HTTPConnectionManager:
    """
    Manages HTTP connections with pooling and retry logic.
    """

    def __init__(self):
        self._aiohttp_session: Optional[aiohttp.ClientSession] = None
        self._httpx_client: Optional[httpx.Client] = None
        self._async_httpx_client: Optional[httpx.AsyncClient] = None

    def get_aiohttp_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._aiohttp_session is None or self._aiohttp_session.closed:
            try:
                # Try to get current event loop
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, create connector without loop
                connector = aiohttp.TCPConnector(
                    limit=100,  # Total connection pool size
                    limit_per_host=30,  # Per-host connection limit
                    ttl_dns_cache=300,  # DNS cache TTL
                    use_dns_cache=True,
                    keepalive_timeout=30,
                    enable_cleanup_closed=True,
                )
            else:
                # Running loop exists, create connector with loop
                connector = aiohttp.TCPConnector(
                    limit=100,  # Total connection pool size
                    limit_per_host=30,  # Per-host connection limit
                    ttl_dns_cache=300,  # DNS cache TTL
                    use_dns_cache=True,
                    keepalive_timeout=30,
                    enable_cleanup_closed=True,
                    loop=loop,
                )

            timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=10)

            self._aiohttp_session = aiohttp.ClientSession(
                connector=connector, timeout=timeout, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; PulseAI/1.0; +https://pulseai.bot)"}, )
            logger.info("Created new aiohttp session with connection pooling")

        return self._aiohttp_session

    @property
    def httpx_client(self) -> httpx.Client:
        """Get or create httpx sync client."""
        if self._httpx_client is None or self._httpx_client.is_closed:
            limits = httpx.Limits(
                max_keepalive_connections=100,
                max_connections=100,
                keepalive_expiry=30.0)

            self._httpx_client = httpx.Client(
                limits=limits, timeout=30.0, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; PulseAI/1.0; +https://pulseai.bot)"}, )
            logger.info("Created new httpx sync client with connection pooling")

        return self._httpx_client

    @property
    def async_httpx_client(self) -> httpx.AsyncClient:
        """Get or create httpx async client."""
        if self._async_httpx_client is None or self._async_httpx_client.is_closed:
            limits = httpx.Limits(
                max_keepalive_connections=100,
                max_connections=100,
                keepalive_expiry=30.0)

            self._async_httpx_client = httpx.AsyncClient(
                limits=limits, timeout=30.0, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; PulseAI/1.0; +https://pulseai.bot)"}, )
            logger.info("Created new httpx async client with connection pooling")

        return self._async_httpx_client

    async def close_all(self):
        """Close all HTTP connections."""
        if self._aiohttp_session and not self._aiohttp_session.closed:
            await self._aiohttp_session.close()
            logger.info("Closed aiohttp session")

        if self._httpx_client and not self._httpx_client.is_closed:
            self._httpx_client.close()
            logger.info("Closed httpx sync client")

        if self._async_httpx_client and not self._async_httpx_client.is_closed:
            await self._async_httpx_client.aclose()
            logger.info("Closed httpx async client")


# Global connection manager
_connection_manager = HTTPConnectionManager()


def get_aiohttp_session() -> aiohttp.ClientSession:
    """Get global aiohttp session."""
    return _connection_manager.get_aiohttp_session()


def get_httpx_client() -> httpx.Client:
    """Get global httpx sync client."""
    return _connection_manager.httpx_client


def get_async_httpx_client() -> httpx.AsyncClient:
    """Get global httpx async client."""
    return _connection_manager.async_httpx_client


async def close_all_connections():
    """Close all HTTP connections."""
    await _connection_manager.close_all()


@asynccontextmanager
async def http_session():
    """Context manager for HTTP session."""
    session = get_aiohttp_session()
    try:
        yield session
    finally:
        # Don't close the session here as it's managed globally
        pass


class OptimizedHTTPClient:
    """
    Optimized HTTP client with caching and connection pooling.
    """

    def __init__(self, cache_ttl: int = 300):
        self.cache_ttl = cache_ttl
        self._session = None
        self._sync_client = None

    @property
    def session(self):
        """Get aiohttp session."""
        if self._session is None:
            self._session = get_aiohttp_session()
        return self._session

    @property
    def sync_client(self):
        """Get httpx sync client."""
        if self._sync_client is None:
            self._sync_client = get_httpx_client()
        return self._sync_client

    async def get(self, url: str, **kwargs) -> Optional[str]:
        """Async GET request with caching."""
        from utils.cache import get_cache

        cache = get_cache("http_requests", self.cache_ttl)
        cache_key = {"url": url, "method": "GET", "kwargs": kwargs}

        # Try cache first
        cached_response = await cache.get(cache_key)
        if cached_response is not None:
            logger.debug(f"HTTP cache hit for {url}")
            return cached_response

        try:
            async with self.session.get(url, **kwargs) as response:
                if response.status == 200:
                    content = await response.text()
                    await cache.set(cache_key, content, self.cache_ttl)
                    return content
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"HTTP request failed for {url}: {e}")
            return None

    def get_sync(self, url: str, **kwargs) -> Optional[str]:
        """Sync GET request."""
        try:
            response = self.sync_client.get(url, **kwargs)
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"HTTP {response.status_code} for {url}")
                return None
        except Exception as e:
            logger.error(f"HTTP request failed for {url}: {e}")
            return None

    async def post(self, url: str, data: Optional[Dict] = None, **kwargs) -> Optional[str]:
        """Async POST request."""
        try:
            async with self.session.post(url, data=data, **kwargs) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"HTTP request failed for {url}: {e}")
            return None

    def post_sync(self, url: str, data: Optional[Dict] = None, **kwargs) -> Optional[str]:
        """Sync POST request."""
        try:
            response = self.sync_client.post(url, data=data, **kwargs)
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"HTTP {response.status_code} for {url}")
                return None
        except Exception as e:
            logger.error(f"HTTP request failed for {url}: {e}")
            return None


# Global HTTP client instance
_http_client = OptimizedHTTPClient()


def get_http_client() -> OptimizedHTTPClient:
    """Get global HTTP client."""
    return _http_client


async def cleanup_http_resources():
    """Cleanup HTTP resources on application shutdown."""
    await close_all_connections()

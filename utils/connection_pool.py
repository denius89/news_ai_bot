"""
Connection Pool Manager for PulseAI.

This module provides connection pooling for HTTP requests, database connections,
and other network resources to improve performance and resource utilization.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from contextlib import asynccontextmanager, contextmanager
import threading
from collections import defaultdict

try:
    import aiohttp
    import httpx

    HTTP_LIBS_AVAILABLE = True
except ImportError:
    HTTP_LIBS_AVAILABLE = False
    aiohttp = None
    httpx = None

logger = logging.getLogger("connection_pool")


@dataclass
class PoolConfig:
    """Configuration for connection pool."""

    max_connections: int = 100
    max_connections_per_host: int = 10
    keepalive_timeout: int = 30
    connect_timeout: int = 10
    read_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0


@dataclass
class PoolStats:
    """Statistics for connection pool."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    avg_response_time: float = 0.0
    last_reset: float = 0.0


class HTTPConnectionPool:
    """
    HTTP connection pool manager with aiohttp and httpx support.
    """

    def __init__(self, config: Optional[PoolConfig] = None):
        """
        Initialize HTTP connection pool.

        Args:
            config: Pool configuration
        """
        self.config = config or PoolConfig()
        self.stats = PoolStats()
        self.stats.last_reset = time.time()

        # aiohttp session
        self.aiohttp_session: Optional[aiohttp.ClientSession] = None
        self.aiohttp_connector: Optional[aiohttp.TCPConnector] = None

        # httpx client
        self.httpx_client: Optional[httpx.AsyncClient] = None

        # Thread safety
        self._lock = threading.Lock()
        self._session_lock = asyncio.Lock() if HTTP_LIBS_AVAILABLE else None

        # Request tracking
        self._request_times: Dict[str, List[float]] = defaultdict(list)

    async def _init_aiohttp_session(self):
        """Initialize aiohttp session with connection pooling."""
        if not HTTP_LIBS_AVAILABLE or aiohttp is None:
            return

        if self.aiohttp_session is not None:
            return

        async with self._session_lock:
            if self.aiohttp_session is not None:
                return

            # Create TCP connector with connection pooling
            self.aiohttp_connector = aiohttp.TCPConnector(
                limit=self.config.max_connections,
                limit_per_host=self.config.max_connections_per_host,
                keepalive_timeout=self.config.keepalive_timeout,
                enable_cleanup_closed=True,
                ttl_dns_cache=300,
                use_dns_cache=True,
                family=0,  # Allow both IPv4 and IPv6
                ssl=False,  # Will be handled by individual requests
            )

            # Create session with timeout configuration
            timeout = aiohttp.ClientTimeout(
                total=self.config.read_timeout,
                connect=self.config.connect_timeout,
                sock_read=self.config.read_timeout,
            )

            self.aiohttp_session = aiohttp.ClientSession(
                connector=self.aiohttp_connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'PulseAI/1.0 (News Bot)',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Encoding': 'gzip, deflate',
                },
            )

            logger.info("✅ aiohttp session initialized with connection pooling")

    async def _init_httpx_client(self):
        """Initialize httpx client with connection pooling."""
        if not HTTP_LIBS_AVAILABLE or httpx is None:
            return

        if self.httpx_client is not None:
            return

        async with self._session_lock:
            if self.httpx_client is not None:
                return

            # Create httpx client with connection limits
            limits = httpx.Limits(
                max_keepalive_connections=self.config.max_connections,
                max_connections=self.config.max_connections,
                keepalive_expiry=self.config.keepalive_timeout,
            )

            timeout = httpx.Timeout(
                connect=self.config.connect_timeout,
                read=self.config.read_timeout,
                write=10.0,
                pool=5.0,
            )

            self.httpx_client = httpx.AsyncClient(
                limits=limits,
                timeout=timeout,
                headers={
                    'User-Agent': 'PulseAI/1.0 (News Bot)',
                    'Accept': 'application/json, text/plain, */*',
                },
                follow_redirects=True,
                http2=True,
            )

            logger.info("✅ httpx client initialized with connection pooling")

    @asynccontextmanager
    async def get_aiohttp_session(self):
        """
        Get aiohttp session with connection pooling.

        Yields:
            aiohttp.ClientSession: Configured session
        """
        await self._init_aiohttp_session()

        if self.aiohttp_session is None:
            raise RuntimeError("aiohttp session not available")

        try:
            yield self.aiohttp_session
        except Exception as e:
            logger.warning(f"aiohttp session error: {e}")
            raise

    @asynccontextmanager
    async def get_httpx_client(self):
        """
        Get httpx client with connection pooling.

        Yields:
            httpx.AsyncClient: Configured client
        """
        await self._init_httpx_client()

        if self.httpx_client is None:
            raise RuntimeError("httpx client not available")

        try:
            yield self.httpx_client
        except Exception as e:
            logger.warning(f"httpx client error: {e}")
            raise

    async def request_with_retry(
        self, method: str, url: str, **kwargs
    ) -> Tuple[int, bytes, Dict[str, str]]:
        """
        Make HTTP request with retry logic and connection pooling.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            Tuple of (status_code, content, headers)
        """
        start_time = time.time()
        last_exception = None

        for attempt in range(self.config.retry_attempts):
            try:
                # Use aiohttp for async requests
                async with self.get_aiohttp_session() as session:
                    async with session.request(method, url, **kwargs) as response:
                        content = await response.read()
                        headers = dict(response.headers)

                        # Update stats
                        self._update_stats(True, time.time() - start_time)

                        return response.status, content, headers

            except Exception as e:
                last_exception = e
                logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")

                if attempt < self.config.retry_attempts - 1:
                    delay = self.config.retry_delay * (self.config.backoff_factor**attempt)
                    await asyncio.sleep(delay)

        # Update stats for final failure
        self._update_stats(False, time.time() - start_time)

        if last_exception:
            raise last_exception
        else:
            raise RuntimeError(f"All {self.config.retry_attempts} attempts failed")

    def _update_stats(self, success: bool, response_time: float):
        """Update connection pool statistics."""
        with self._lock:
            self.stats.total_requests += 1

            if success:
                self.stats.successful_requests += 1
            else:
                self.stats.failed_requests += 1

            # Update average response time
            total_time = self.stats.avg_response_time * (self.stats.total_requests - 1)
            self.stats.avg_response_time = (total_time + response_time) / self.stats.total_requests

    def get_stats(self) -> PoolStats:
        """
        Get connection pool statistics.

        Returns:
            PoolStats: Current statistics
        """
        with self._lock:
            # Get connection stats if available
            if self.aiohttp_connector:
                self.stats.active_connections = len(self.aiohttp_connector._closed)
                self.stats.idle_connections = len(self.aiohttp_connector._closed)

            return PoolStats(
                total_requests=self.stats.total_requests,
                successful_requests=self.stats.successful_requests,
                failed_requests=self.stats.failed_requests,
                active_connections=self.stats.active_connections,
                idle_connections=self.stats.idle_connections,
                avg_response_time=self.stats.avg_response_time,
                last_reset=self.stats.last_reset,
            )

    def reset_stats(self):
        """Reset connection pool statistics."""
        with self._lock:
            self.stats = PoolStats()
            self.stats.last_reset = time.time()
            self._request_times.clear()

    async def close(self):
        """Close all connections and cleanup resources."""
        if self.aiohttp_session:
            await self.aiohttp_session.close()
            self.aiohttp_session = None

        if self.aiohttp_connector:
            await self.aiohttp_connector.close()
            self.aiohttp_connector = None

        if self.httpx_client:
            await self.httpx_client.aclose()
            self.httpx_client = None

        logger.info("✅ HTTP connection pool closed")


class DatabaseConnectionPool:
    """
    Database connection pool manager for Supabase and other databases.
    """

    def __init__(self, config: Optional[PoolConfig] = None):
        """
        Initialize database connection pool.

        Args:
            config: Pool configuration
        """
        self.config = config or PoolConfig()
        self.stats = PoolStats()
        self.stats.last_reset = time.time()

        # Connection tracking
        self._connections: Dict[str, Any] = {}
        self._connection_locks: Dict[str, asyncio.Lock] = {}
        self._lock = threading.Lock()

    async def get_connection(self, connection_id: str, connection_factory: callable):
        """
        Get or create database connection.

        Args:
            connection_id: Unique connection identifier
            connection_factory: Function to create new connection

        Returns:
            Database connection
        """
        if connection_id not in self._connection_locks:
            self._connection_locks[connection_id] = asyncio.Lock()

        async with self._connection_locks[connection_id]:
            if connection_id not in self._connections:
                try:
                    self._connections[connection_id] = await connection_factory()
                    logger.info(f"✅ Database connection created: {connection_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to create database connection {connection_id}: {e}")
                    raise

            return self._connections[connection_id]

    def get_stats(self) -> PoolStats:
        """
        Get database connection pool statistics.

        Returns:
            PoolStats: Current statistics
        """
        with self._lock:
            return PoolStats(
                total_requests=self.stats.total_requests,
                successful_requests=self.stats.successful_requests,
                failed_requests=self.stats.failed_requests,
                active_connections=len(self._connections),
                idle_connections=len(self._connections),
                avg_response_time=self.stats.avg_response_time,
                last_reset=self.stats.last_reset,
            )

    async def close_all(self):
        """Close all database connections."""
        for connection_id, connection in self._connections.items():
            try:
                if hasattr(connection, 'close'):
                    await connection.close()
                elif hasattr(connection, 'aclose'):
                    await connection.aclose()
                logger.info(f"✅ Database connection closed: {connection_id}")
            except Exception as e:
                logger.warning(f"⚠️ Error closing database connection {connection_id}: {e}")

        self._connections.clear()
        self._connection_locks.clear()


# Global connection pools
_http_pool: Optional[HTTPConnectionPool] = None
_db_pool: Optional[DatabaseConnectionPool] = None


def get_http_pool(config: Optional[PoolConfig] = None) -> HTTPConnectionPool:
    """
    Get global HTTP connection pool.

    Args:
        config: Pool configuration

    Returns:
        HTTPConnectionPool: Global HTTP connection pool
    """
    global _http_pool

    if _http_pool is None:
        _http_pool = HTTPConnectionPool(config)

    return _http_pool


def get_db_pool(config: Optional[PoolConfig] = None) -> DatabaseConnectionPool:
    """
    Get global database connection pool.

    Args:
        config: Pool configuration

    Returns:
        DatabaseConnectionPool: Global database connection pool
    """
    global _db_pool

    if _db_pool is None:
        _db_pool = DatabaseConnectionPool(config)

    return _db_pool


async def close_all_pools():
    """Close all global connection pools."""
    global _http_pool, _db_pool

    if _http_pool:
        await _http_pool.close()
        _http_pool = None

    if _db_pool:
        await _db_pool.close_all()
        _db_pool = None

    logger.info("✅ All connection pools closed")


# Convenience functions for common operations
async def http_get(url: str, **kwargs) -> Tuple[int, bytes, Dict[str, str]]:
    """Make HTTP GET request using connection pool."""
    pool = get_http_pool()
    return await pool.request_with_retry("GET", url, **kwargs)


async def http_post(url: str, data: Any = None, **kwargs) -> Tuple[int, bytes, Dict[str, str]]:
    """Make HTTP POST request using connection pool."""
    pool = get_http_pool()
    return await pool.request_with_retry("POST", url, data=data, **kwargs)


@asynccontextmanager
async def http_session():
    """Get aiohttp session from connection pool."""
    pool = get_http_pool()
    async with pool.get_aiohttp_session() as session:
        yield session


@asynccontextmanager
async def http_client():
    """Get httpx client from connection pool."""
    pool = get_http_pool()
    async with pool.get_httpx_client() as client:
        yield client

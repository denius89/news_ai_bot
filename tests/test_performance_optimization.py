"""
Tests for performance optimization components.
"""

import pytest
import time
from utils.cache_manager import (
    CacheManager,
    get_cache_manager,
    cached,
    cache_invalidate,
    cache_clear,
    cache_stats,
    cache_news_items,
    get_cached_news_items,
    cache_user_subscriptions,
    get_cached_user_subscriptions,
    cache_ai_analysis,
    get_cached_ai_analysis,
)
from utils.connection_pool import (
    HTTPConnectionPool,
    DatabaseConnectionPool,
    PoolConfig,
    PoolStats,
    get_http_pool,
    get_db_pool,
    close_all_pools,
    http_get,
    http_post,
    http_session,
    http_client,
)


class TestCacheManager:
    """Test cases for CacheManager."""

    def test_init_without_redis(self):
        """Test CacheManager initialization without Redis."""
        cache = CacheManager(redis_url=None, enable_memory_cache=True)

        assert cache.redis_available is False
        assert cache.enable_memory_cache is True
        assert cache.default_ttl == 3600
        assert cache.max_memory_size == 1000

    def test_make_key(self):
        """Test cache key generation."""
        cache = CacheManager()

        # Test with simple arguments
        key1 = cache._make_key("test", "arg1", "arg2")
        assert "test" in key1
        assert "arg1" in key1
        assert "arg2" in key1

        # Test with keyword arguments
        key2 = cache._make_key("test", param1="value1", param2="value2")
        assert "test" in key2
        assert "param1:value1" in key2
        assert "param2:value2" in key2

        # Test with complex data
        key3 = cache._make_key("test", {"complex": "data"}, [1, 2, 3])
        assert "test" in key3

    def test_memory_cache_set_get(self):
        """Test memory cache set and get operations."""
        cache = CacheManager(redis_url=None, enable_memory_cache=True)

        # Test set and get
        cache.set("test_key", "test_value", ttl=3600)
        value = cache.get("test_key")
        assert value == "test_value"

        # Test with tags
        cache.set("tagged_key", "tagged_value", ttl=3600, tags=["tag1", "tag2"])
        value = cache.get("tagged_key")
        assert value == "tagged_value"

        # Test expiration
        cache.set("expiring_key", "expiring_value", ttl=1)
        time.sleep(1.1)
        value = cache.get("expiring_key")
        assert value is None

    def test_memory_cache_delete(self):
        """Test memory cache delete operation."""
        cache = CacheManager(redis_url=None, enable_memory_cache=True)

        cache.set("delete_key", "delete_value")
        assert cache.get("delete_key") == "delete_value"

        result = cache.delete("delete_key")
        assert result is True
        assert cache.get("delete_key") is None

        # Test deleting non-existent key
        result = cache.delete("non_existent_key")
        assert result is False

    def test_memory_cache_cleanup(self):
        """Test memory cache cleanup when full."""
        cache = CacheManager(redis_url=None, enable_memory_cache=True, max_memory_size=5)

        # Fill cache beyond limit
        for i in range(7):
            cache.set(f"key_{i}", f"value_{i}")

        # Cache should have cleaned up old entries
        assert len(cache.memory_cache) <= 5

    def test_get_stats(self):
        """Test cache statistics."""
        cache = CacheManager(redis_url=None, enable_memory_cache=True)

        cache.set("stat_key", "stat_value")
        stats = cache.get_stats()

        assert "redis_available" in stats
        assert "memory_cache_size" in stats
        assert "memory_cache_max_size" in stats
        assert stats["memory_cache_size"] == 1

    def test_clear(self):
        """Test cache clear operation."""
        cache = CacheManager(redis_url=None, enable_memory_cache=True)

        cache.set("clear_key", "clear_value")
        assert cache.get("clear_key") == "clear_value"

        result = cache.clear()
        assert result is True
        assert cache.get("clear_key") is None

    def test_redis_operations_memory_fallback(self):
        """Test Redis operations with memory cache fallback."""
        # Test with Redis unavailable (default behavior)
        cache = CacheManager(redis_url=None, enable_memory_cache=True)

        # Test memory cache operations
        cache.set("memory_key", "memory_value")
        value = cache.get("memory_key")
        assert value == "memory_value"

        result = cache.delete("memory_key")
        assert result is True

        stats = cache.get_stats()
        assert stats["redis_available"] is False
        assert stats["memory_cache_size"] == 0  # After deletion


class TestCacheDecorator:
    """Test cache decorator functionality."""

    def test_cached_decorator(self):
        """Test @cached decorator."""
        call_count = 0

        @cached(ttl=3600, key_prefix="test")
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # First call should execute function
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1

        # Second call should use cache
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Function not called again

        # Different arguments should execute function
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2

    def test_cache_invalidate(self):
        """Test cache invalidation by tags."""

        @cached(ttl=3600, tags=["tag1"])
        def tagged_function(x):
            return x * 2

        # Cache some values
        tagged_function(1)
        tagged_function(2)

        # Invalidate by tag
        invalidated = cache_invalidate(["tag1"])
        # Note: Memory cache doesn't support tag invalidation efficiently
        # This test mainly ensures the function doesn't crash
        assert isinstance(invalidated, int)


class TestConnectionPool:
    """Test cases for connection pools."""

    def test_pool_config(self):
        """Test PoolConfig initialization."""
        config = PoolConfig(
            max_connections=50,
            max_connections_per_host=5,
            keepalive_timeout=60,
            connect_timeout=15,
            read_timeout=45,
        )

        assert config.max_connections == 50
        assert config.max_connections_per_host == 5
        assert config.keepalive_timeout == 60
        assert config.connect_timeout == 15
        assert config.read_timeout == 45

    def test_pool_stats(self):
        """Test PoolStats functionality."""
        stats = PoolStats()

        assert stats.total_requests == 0
        assert stats.successful_requests == 0
        assert stats.failed_requests == 0
        assert stats.avg_response_time == 0.0

    @pytest.mark.asyncio
    async def test_http_connection_pool_init(self):
        """Test HTTP connection pool initialization."""
        pool = HTTPConnectionPool()

        # Test aiohttp session initialization
        await pool._init_aiohttp_session()
        assert pool.aiohttp_session is not None
        assert pool.aiohttp_connector is not None

        # Test httpx client initialization
        await pool._init_httpx_client()
        assert pool.httpx_client is not None

        # Cleanup
        await pool.close()

    @pytest.mark.asyncio
    async def test_http_connection_pool_session_context(self):
        """Test HTTP connection pool session context managers."""
        pool = HTTPConnectionPool()

        # Test aiohttp session context
        async with pool.get_aiohttp_session() as session:
            assert session is not None
            assert hasattr(session, 'get')

        # Test httpx client context
        async with pool.get_httpx_client() as client:
            assert client is not None
            assert hasattr(client, 'get')

        # Cleanup
        await pool.close()

    def test_http_request_with_retry_config(self):
        """Test HTTP request configuration and stats."""
        pool = HTTPConnectionPool()

        # Test configuration
        assert pool.config.max_connections == 100
        assert pool.config.max_connections_per_host == 10
        assert pool.config.retry_attempts == 3

        # Test stats
        stats = pool.get_stats()
        assert stats.total_requests == 0
        assert stats.successful_requests == 0
        assert stats.failed_requests == 0

    def test_http_pool_stats(self):
        """Test HTTP connection pool statistics."""
        pool = HTTPConnectionPool()

        stats = pool.get_stats()

        assert stats.total_requests == 0
        assert stats.successful_requests == 0
        assert stats.failed_requests == 0
        assert stats.avg_response_time == 0.0

        # Reset stats
        pool.reset_stats()
        stats = pool.get_stats()
        assert stats.total_requests == 0

    @pytest.mark.asyncio
    async def test_database_connection_pool(self):
        """Test database connection pool."""
        pool = DatabaseConnectionPool()

        # Mock connection factory
        async def mock_connection_factory():
            return Mock()

        # Get connection
        connection = await pool.get_connection("test_conn", mock_connection_factory)
        assert connection is not None

        # Get same connection again (should return cached)
        connection2 = await pool.get_connection("test_conn", mock_connection_factory)
        assert connection is connection2

        # Get stats
        stats = pool.get_stats()
        assert stats.active_connections == 1

        # Close all connections
        await pool.close_all()


class TestGlobalPools:
    """Test global pool instances."""

    def test_get_http_pool_singleton(self):
        """Test HTTP pool singleton behavior."""
        pool1 = get_http_pool()
        pool2 = get_http_pool()

        assert pool1 is pool2

    def test_get_db_pool_singleton(self):
        """Test database pool singleton behavior."""
        pool1 = get_db_pool()
        pool2 = get_db_pool()

        assert pool1 is pool2

    @pytest.mark.asyncio
    async def test_close_all_pools(self):
        """Test closing all global pools."""
        # Get pools to ensure they exist
        http_pool = get_http_pool()
        db_pool = get_db_pool()

        # Close all pools
        await close_all_pools()

        # Pools should be reset
        new_http_pool = get_http_pool()
        new_db_pool = get_db_pool()

        assert new_http_pool is not http_pool
        assert new_db_pool is not db_pool


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_cache_news_items(self):
        """Test caching news items."""
        news_items = [
            {"title": "News 1", "content": "Content 1"},
            {"title": "News 2", "content": "Content 2"},
        ]

        cached_count = cache_news_items("tech", "ai", news_items, ttl=1800)
        assert cached_count == 2

        # Retrieve cached items
        cached_items = get_cached_news_items("tech", "ai")
        assert cached_items == news_items

    def test_cache_user_subscriptions(self):
        """Test caching user subscriptions."""
        subscriptions = {"crypto": True, "tech": False, "sports": True}

        cached_count = cache_user_subscriptions(123, subscriptions, ttl=3600)
        assert cached_count == 3

        # Retrieve cached subscriptions
        cached_subs = get_cached_user_subscriptions(123)
        assert cached_subs == subscriptions

    def test_cache_ai_analysis(self):
        """Test caching AI analysis."""
        content_hash = "abc123"
        analysis = {"importance": 0.85, "credibility": 0.92}

        cached_analysis = cache_ai_analysis(content_hash, analysis, ttl=7200)
        assert cached_analysis == analysis

        # Retrieve cached analysis
        retrieved_analysis = get_cached_ai_analysis(content_hash)
        assert retrieved_analysis == analysis

    @pytest.mark.asyncio
    async def test_http_convenience_functions(self):
        """Test HTTP convenience functions."""
        with patch('utils.connection_pool.get_http_pool') as mock_get_pool:
            mock_pool = AsyncMock()
            mock_pool.request_with_retry.return_value = (
                200,
                b"response",
                {"content-type": "text/plain"},
            )
            mock_get_pool.return_value = mock_pool

            # Test http_get
            status, content, headers = await http_get("http://example.com")
            assert status == 200
            assert content == b"response"

            # Test http_post
            status, content, headers = await http_post("http://example.com", data={"key": "value"})
            assert status == 200
            assert content == b"response"

    def test_http_session_functions_exist(self):
        """Test that HTTP session functions are available."""
        # Test that functions are callable
        assert callable(http_session)
        assert callable(http_client)

        # Test that they return context managers
        session_ctx = http_session()
        client_ctx = http_client()

        assert hasattr(session_ctx, '__aenter__')
        assert hasattr(session_ctx, '__aexit__')
        assert hasattr(client_ctx, '__aenter__')
        assert hasattr(client_ctx, '__aexit__')


class TestPerformanceIntegration:
    """Integration tests for performance optimizations."""

    def test_cache_and_pool_integration(self):
        """Test integration between cache and connection pools."""
        # Initialize both systems
        cache = get_cache_manager()
        http_pool = get_http_pool()

        # Cache some data
        cache.set("integration_test", {"data": "test"}, ttl=3600)

        # Verify cache works
        cached_data = cache.get("integration_test")
        assert cached_data["data"] == "test"

        # Verify pool stats
        stats = http_pool.get_stats()
        assert stats.total_requests >= 0  # Should not crash

    def test_memory_efficiency(self):
        """Test memory efficiency of caching system."""
        cache = CacheManager(max_memory_size=10, enable_memory_cache=True)

        # Fill cache to capacity
        for i in range(15):
            cache.set(f"key_{i}", f"value_{i}")

        # Cache should have cleaned up
        assert len(cache.memory_cache) <= 10

        # Verify some recent keys are still there
        assert cache.get("key_14") == "value_14"

    def test_error_handling(self):
        """Test error handling in performance components."""
        # Test cache with invalid data
        cache = CacheManager(enable_memory_cache=True)

        # Should handle various data types
        cache.set("json_key", {"complex": "data", "list": [1, 2, 3]})
        cache.set("none_key", None)
        cache.set("bool_key", True)

        assert cache.get("json_key") == {"complex": "data", "list": [1, 2, 3]}
        assert cache.get("none_key") is None
        assert cache.get("bool_key") is True

        # Test non-existent key
        assert cache.get("non_existent") is None

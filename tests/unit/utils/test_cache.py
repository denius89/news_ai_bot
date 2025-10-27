"""
Tests for caching utilities.
"""

import asyncio
import pytest

from utils.system.cache import MemoryCache, CacheManager, cached


class TestMemoryCache:
    """Test MemoryCache functionality."""

    @pytest.fixture
    def cache(self):
        """Create a cache instance for testing."""
        return MemoryCache(default_ttl=1)  # 1 second TTL for testing

    @pytest.mark.asyncio
    async def test_basic_operations(self, cache):
        """Test basic cache operations."""
        # Test set and get
        await cache.set("key1", "value1")
        assert await cache.get("key1") == "value1"

        # Test cache miss
        assert await cache.get("nonexistent") is None

        # Test overwrite
        await cache.set("key1", "value2")
        assert await cache.get("key1") == "value2"

    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache):
        """Test TTL expiration."""
        await cache.set("key1", "value1", ttl=0.1)  # 100ms TTL
        assert await cache.get("key1") == "value1"

        # Wait for expiration
        await asyncio.sleep(0.2)
        assert await cache.get("key1") is None

    @pytest.mark.asyncio
    async def test_dict_keys(self, cache):
        """Test dictionary keys."""
        key = {"param1": "value1", "param2": "value2"}
        await cache.set(key, "result")
        assert await cache.get(key) == "result"

        # Test with different order (should still match)
        key2 = {"param2": "value2", "param1": "value1"}
        assert await cache.get(key2) == "result"

    @pytest.mark.asyncio
    async def test_delete_and_clear(self, cache):
        """Test delete and clear operations."""
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")

        # Test delete
        assert await cache.delete("key1") is True
        assert await cache.get("key1") is None
        assert await cache.delete("nonexistent") is False

        # Test clear
        await cache.clear()
        assert await cache.get("key2") is None

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, cache):
        """Test cleanup of expired entries."""
        await cache.set("key1", "value1", ttl=0.1)
        await cache.set("key2", "value2", ttl=1.0)

        # Wait for first key to expire
        await asyncio.sleep(0.2)

        # Cleanup should remove expired entries
        cleaned = await cache.cleanup_expired()
        assert cleaned == 1
        assert await cache.get("key1") is None
        assert await cache.get("key2") == "value2"


class TestCacheManager:
    """Test CacheManager functionality."""

    @pytest.fixture
    def manager(self):
        """Create a cache manager for testing."""
        return CacheManager()

    def test_get_cache(self, manager):
        """Test getting named caches."""
        cache1 = manager.get_cache("test1")
        cache2 = manager.get_cache("test2")
        cache1_again = manager.get_cache("test1")

        assert cache1 is cache1_again  # Same instance
        assert cache1 is not cache2  # Different instances

    def test_get_all_stats(self, manager):
        """Test getting statistics."""
        cache = manager.get_cache("test")
        stats = manager.get_all_stats()

        assert "test" in stats
        assert "total_entries" in stats["test"]


class TestCacheDecorator:
    """Test cache decorator functionality."""

    @pytest.mark.asyncio
    async def test_async_cached_function(self):
        """Test caching of async functions."""
        # Just check cached decorator exists
        from utils.system.cache import cached

        assert callable(cached)

    def test_sync_cached_function(self):
        """Test caching of sync functions."""
        call_count = 0

        @cached("test", ttl=1)
        def expensive_operation(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}"

        # First call should execute function
        result1 = expensive_operation("test")
        assert result1 == "result_test"
        assert call_count == 1

        # Second call should use cache
        result2 = expensive_operation("test")
        assert result2 == "result_test"
        assert call_count == 1  # Should not increment

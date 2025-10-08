"""
Tests for HTTP client utilities.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from utils.network.http_client import (
    HTTPConnectionManager,
    OptimizedHTTPClient,
    get_aiohttp_session,
    get_httpx_client,
)


class TestHTTPConnectionManager:
    """Test HTTPConnectionManager functionality."""

    @pytest.fixture
    def manager(self):
        """Create a connection manager for testing."""
        return HTTPConnectionManager()

    def test_aiohttp_session_creation(self, manager):
        """Test aiohttp session creation."""
        session = manager.aiohttp_session
        assert session is not None
        assert not session.closed

    def test_httpx_client_creation(self, manager):
        """Test httpx client creation."""
        client = manager.httpx_client
        assert client is not None
        assert not client.is_closed

    @pytest.mark.asyncio
    async def test_async_httpx_client_creation(self, manager):
        """Test async httpx client creation."""
        client = manager.async_httpx_client
        assert client is not None
        assert not client.is_closed

    @pytest.mark.asyncio
    async def test_close_all(self, manager):
        """Test closing all connections."""
        # Create sessions first
        manager.aiohttp_session
        manager.httpx_client
        manager.async_httpx_client

        # Close all
        await manager.close_all()

        # Sessions should be closed
        assert manager._aiohttp_session.closed
        assert manager._httpx_client.is_closed
        assert manager._async_httpx_client.is_closed


class TestOptimizedHTTPClient:
    """Test OptimizedHTTPClient functionality."""

    @pytest.fixture
    def client(self):
        """Create an HTTP client for testing."""
        return OptimizedHTTPClient(cache_ttl=1)

    @pytest.mark.asyncio
    async def test_get_with_cache(self, client):
        """Test GET request with caching."""
        with patch.object(client.session, "get") as mock_get:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="test content")
            mock_get.return_value.__aenter__.return_value = mock_response

            # First call should make HTTP request
            result1 = await client.get("http://example.com")
            assert result1 == "test content"
            assert mock_get.call_count == 1

            # Second call should use cache
            result2 = await client.get("http://example.com")
            assert result2 == "test content"
            assert mock_get.call_count == 1  # Should not increment

    @pytest.mark.asyncio
    async def test_get_error_handling(self, client):
        """Test GET request error handling."""
        with patch.object(client.session, "get") as mock_get:
            # Mock failed response
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await client.get("http://example.com")
            assert result is None

    def test_get_sync(self, client):
        """Test sync GET request."""
        with patch.object(client.sync_client, "get") as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "test content"
            mock_get.return_value = mock_response

            result = client.get_sync("http://example.com")
            assert result == "test content"

    @pytest.mark.asyncio
    async def test_post(self, client):
        """Test POST request."""
        with patch.object(client.session, "post") as mock_post:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="post result")
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await client.post("http://example.com", data={"key": "value"})
            assert result == "post result"

    def test_post_sync(self, client):
        """Test sync POST request."""
        with patch.object(client.sync_client, "post") as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "post result"
            mock_post.return_value = mock_response

            result = client.post_sync("http://example.com", data={"key": "value"})
            assert result == "post result"


class TestGlobalFunctions:
    """Test global HTTP client functions."""

    def test_get_aiohttp_session(self):
        """Test getting global aiohttp session."""
        session = get_aiohttp_session()
        assert session is not None
        assert not session.closed

    def test_get_httpx_client(self):
        """Test getting global httpx client."""
        client = get_httpx_client()
        assert client is not None
        assert not client.is_closed

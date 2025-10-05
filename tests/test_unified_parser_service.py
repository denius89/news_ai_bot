"""
Tests for unified parser service.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from parsers.unified_parser_service import (
    UnifiedParserService,
    get_sync_parser_service,
    get_async_parser_service,
    parse_all_sources,
    async_parse_all_sources,
    parse_source,
    async_parse_source,
    parse_and_save,
    async_parse_and_save,
)


class TestUnifiedParserService:
    """Test cases for UnifiedParserService."""
    
    def test_init_sync_mode(self):
        """Test initialization in sync mode."""
        service = UnifiedParserService(async_mode=False)
        
        assert not service.async_mode
        assert service.sync_service is not None
        assert service.async_service is not None
    
    def test_init_async_mode(self):
        """Test initialization in async mode."""
        service = UnifiedParserService(async_mode=True)
        
        assert service.async_mode
        assert service.sync_service is not None
        assert service.async_service is not None
    
    def test_parse_source_sync(self):
        """Test parse_source in sync mode."""
        with patch('parsers.unified_parser_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            # Mock feedparser
            with patch('parsers.unified_parser_service.feedparser') as mock_feedparser:
                mock_feed = Mock()
                mock_entry = Mock()
                mock_entry.get.side_effect = lambda key, default="": {
                    "title": "Test News",
                    "link": "http://example.com/news",
                    "summary": "Test summary",
                    "published": "2025-01-01T00:00:00Z"
                }.get(key, default)
                
                mock_feed.entries = [mock_entry]
                mock_feed.bozo = False
                mock_feedparser.parse.return_value = mock_feed
                
                # Mock requests
                with patch('parsers.unified_parser_service.requests') as mock_requests:
                    mock_response = Mock()
                    mock_response.content = b"<rss></rss>"
                    mock_requests.get.return_value = mock_response
                    
                    service = UnifiedParserService(async_mode=False)
                    service.sync_service = mock_service
                    
                    news_items = service.parse_source(
                        url="http://example.com/rss",
                        category="tech",
                        subcategory="ai",
                        source_name="Test Source"
                    )
                    
                    assert len(news_items) == 1
                    assert news_items[0]["title"] == "Test News"
                    assert news_items[0]["category"] == "tech"
                    assert news_items[0]["subcategory"] == "ai"
                    assert news_items[0]["source"] == "Test Source"
    
    def test_parse_source_empty_feed(self):
        """Test parse_source with empty feed."""
        with patch('parsers.unified_parser_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            # Mock feedparser with empty feed
            with patch('parsers.unified_parser_service.feedparser') as mock_feedparser:
                mock_feed = Mock()
                mock_feed.entries = []
                mock_feed.bozo = False
                mock_feedparser.parse.return_value = mock_feed
                
                # Mock requests
                with patch('parsers.unified_parser_service.requests') as mock_requests:
                    mock_response = Mock()
                    mock_response.content = b"<rss></rss>"
                    mock_requests.get.return_value = mock_response
                    
                    service = UnifiedParserService(async_mode=False)
                    service.sync_service = mock_service
                    
                    news_items = service.parse_source(
                        url="http://example.com/rss",
                        category="tech",
                        subcategory="ai",
                        source_name="Test Source"
                    )
                    
                    assert len(news_items) == 0
    
    @pytest.mark.asyncio
    async def test_async_parse_source(self):
        """Test async_parse_source."""
        with patch('parsers.unified_parser_service.get_async_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_get_service.return_value = mock_service
            
            # Mock feedparser
            with patch('parsers.unified_parser_service.feedparser') as mock_feedparser:
                mock_feed = Mock()
                mock_entry = Mock()
                mock_entry.get.side_effect = lambda key, default="": {
                    "title": "Async Test News",
                    "link": "http://example.com/async",
                    "summary": "Async test summary",
                    "published": "2025-01-01T00:00:00Z"
                }.get(key, default)
                
                mock_feed.entries = [mock_entry]
                mock_feed.bozo = False
                mock_feedparser.parse.return_value = mock_feed
                
                # Mock aiohttp
                with patch('parsers.unified_parser_service.aiohttp') as mock_aiohttp:
                    mock_session = AsyncMock()
                    mock_response = AsyncMock()
                    mock_response.read.return_value = b"<rss></rss>"
                    mock_session.get.return_value.__aenter__.return_value = mock_response
                    mock_aiohttp.ClientSession.return_value.__aenter__.return_value = mock_session
                    
                    service = UnifiedParserService(async_mode=True)
                    service.async_service = mock_service
                    
                    news_items = await service.async_parse_source(
                        url="http://example.com/rss",
                        category="crypto",
                        subcategory="bitcoin",
                        source_name="Async Test Source"
                    )
                    
                    assert len(news_items) == 1
                    assert news_items[0]["title"] == "Async Test News"
                    assert news_items[0]["category"] == "crypto"
                    assert news_items[0]["subcategory"] == "bitcoin"
                    assert news_items[0]["source"] == "Async Test Source"
    
    def test_parse_all_sources_sync(self):
        """Test parse_all_sources in sync mode."""
        with patch('parsers.unified_parser_service.get_all_sources') as mock_get_sources:
            mock_sources = [
                {
                    "url": "http://example.com/rss1",
                    "category": "tech",
                    "subcategory": "ai",
                    "name": "Tech Source"
                },
                {
                    "url": "http://example.com/rss2",
                    "category": "crypto",
                    "subcategory": "bitcoin",
                    "name": "Crypto Source"
                }
            ]
            mock_get_sources.return_value = mock_sources
            
            with patch('parsers.unified_parser_service.get_sync_service') as mock_get_service:
                mock_service = Mock()
                mock_get_service.return_value = mock_service
                
                # Mock feedparser
                with patch('parsers.unified_parser_service.feedparser') as mock_feedparser:
                    mock_feed = Mock()
                    mock_entry = Mock()
                    mock_entry.get.side_effect = lambda key, default="": {
                        "title": "Test News",
                        "link": "http://example.com/news",
                        "summary": "Test summary",
                        "published": "2025-01-01T00:00:00Z"
                    }.get(key, default)
                    
                    mock_feed.entries = [mock_entry]
                    mock_feed.bozo = False
                    mock_feedparser.parse.return_value = mock_feed
                    
                    # Mock requests
                    with patch('parsers.unified_parser_service.requests') as mock_requests:
                        mock_response = Mock()
                        mock_response.content = b"<rss></rss>"
                        mock_requests.get.return_value = mock_response
                        
                        service = UnifiedParserService(async_mode=False)
                        service.sync_service = mock_service
                        
                        news_items = service.parse_all_sources(per_source_limit=2)
                        
                        assert len(news_items) == 2  # One item from each source
                        assert all(item["title"] == "Test News" for item in news_items)
    
    @pytest.mark.asyncio
    async def test_async_parse_all_sources(self):
        """Test async_parse_all_sources."""
        with patch('parsers.unified_parser_service.get_all_sources') as mock_get_sources:
            mock_sources = [
                {
                    "url": "http://example.com/rss1",
                    "category": "tech",
                    "subcategory": "ai",
                    "name": "Tech Source"
                }
            ]
            mock_get_sources.return_value = mock_sources
            
            with patch('parsers.unified_parser_service.get_async_service') as mock_get_service:
                mock_service = AsyncMock()
                mock_get_service.return_value = mock_service
                
                # Mock feedparser
                with patch('parsers.unified_parser_service.feedparser') as mock_feedparser:
                    mock_feed = Mock()
                    mock_entry = Mock()
                    mock_entry.get.side_effect = lambda key, default="": {
                        "title": "Async News",
                        "link": "http://example.com/async",
                        "summary": "Async summary",
                        "published": "2025-01-01T00:00:00Z"
                    }.get(key, default)
                    
                    mock_feed.entries = [mock_entry]
                    mock_feed.bozo = False
                    mock_feedparser.parse.return_value = mock_feed
                    
                    # Mock aiohttp
                    with patch('parsers.unified_parser_service.aiohttp') as mock_aiohttp:
                        mock_session = AsyncMock()
                        mock_response = AsyncMock()
                        mock_response.read.return_value = b"<rss></rss>"
                        mock_session.get.return_value.__aenter__.return_value = mock_response
                        mock_aiohttp.ClientSession.return_value.__aenter__.return_value = mock_session
                        
                        service = UnifiedParserService(async_mode=True)
                        service.async_service = mock_service
                        
                        news_items = await service.async_parse_all_sources(per_source_limit=1)
                        
                        assert len(news_items) == 1
                        assert news_items[0]["title"] == "Async News"
    
    def test_parse_and_save_sync(self):
        """Test parse_and_save in sync mode."""
        with patch('parsers.unified_parser_service.get_all_sources') as mock_get_sources:
            mock_sources = [
                {
                    "url": "http://example.com/rss",
                    "category": "tech",
                    "subcategory": "ai",
                    "name": "Test Source"
                }
            ]
            mock_get_sources.return_value = mock_sources
            
            with patch('parsers.unified_parser_service.get_sync_service') as mock_get_service:
                mock_service = Mock()
                mock_get_service.return_value = mock_service
                
                # Mock feedparser
                with patch('parsers.unified_parser_service.feedparser') as mock_feedparser:
                    mock_feed = Mock()
                    mock_entry = Mock()
                    mock_entry.get.side_effect = lambda key, default="": {
                        "title": "Save Test News",
                        "link": "http://example.com/save",
                        "summary": "Save test summary",
                        "published": "2025-01-01T00:00:00Z"
                    }.get(key, default)
                    
                    mock_feed.entries = [mock_entry]
                    mock_feed.bozo = False
                    mock_feedparser.parse.return_value = mock_feed
                    
                    # Mock requests
                    with patch('parsers.unified_parser_service.requests') as mock_requests:
                        mock_response = Mock()
                        mock_response.content = b"<rss></rss>"
                        mock_requests.get.return_value = mock_response
                        
                        # Mock upsert_news
                        with patch('parsers.unified_parser_service.upsert_news') as mock_upsert:
                            mock_upsert.return_value = 1
                            
                            service = UnifiedParserService(async_mode=False)
                            service.sync_service = mock_service
                            
                            saved_count = service.parse_and_save(per_source_limit=1)
                            
                            assert saved_count == 1
                            mock_upsert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_parse_and_save(self):
        """Test async_parse_and_save."""
        with patch('parsers.unified_parser_service.get_all_sources') as mock_get_sources:
            mock_sources = [
                {
                    "url": "http://example.com/rss",
                    "category": "crypto",
                    "subcategory": "bitcoin",
                    "name": "Async Test Source"
                }
            ]
            mock_get_sources.return_value = mock_sources
            
            with patch('parsers.unified_parser_service.get_async_service') as mock_get_service:
                mock_service = AsyncMock()
                mock_get_service.return_value = mock_service
                
                # Mock feedparser
                with patch('parsers.unified_parser_service.feedparser') as mock_feedparser:
                    mock_feed = Mock()
                    mock_entry = Mock()
                    mock_entry.get.side_effect = lambda key, default="": {
                        "title": "Async Save News",
                        "link": "http://example.com/async-save",
                        "summary": "Async save summary",
                        "published": "2025-01-01T00:00:00Z"
                    }.get(key, default)
                    
                    mock_feed.entries = [mock_entry]
                    mock_feed.bozo = False
                    mock_feedparser.parse.return_value = mock_feed
                    
                    # Mock aiohttp
                    with patch('parsers.unified_parser_service.aiohttp') as mock_aiohttp:
                        mock_session = AsyncMock()
                        mock_response = AsyncMock()
                        mock_response.read.return_value = b"<rss></rss>"
                        mock_session.get.return_value.__aenter__.return_value = mock_response
                        mock_aiohttp.ClientSession.return_value.__aenter__.return_value = mock_session
                        
                        # Mock async_upsert_news
                        with patch('parsers.unified_parser_service.async_upsert_news') as mock_upsert:
                            mock_upsert.return_value = 1
                            
                            service = UnifiedParserService(async_mode=True)
                            service.async_service = mock_service
                            
                            saved_count = await service.async_parse_and_save(per_source_limit=1)
                            
                            assert saved_count == 1
                            mock_upsert.assert_called_once()
    
    def test_normalize_date(self):
        """Test _normalize_date method."""
        service = UnifiedParserService(async_mode=False)
        
        # Test valid date
        date_str = "2025-01-01T12:00:00Z"
        result = service._normalize_date(date_str)
        assert result is not None
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 1
        
        # Test invalid date
        result = service._normalize_date("invalid date")
        assert result is None
        
        # Test empty date
        result = service._normalize_date("")
        assert result is None
    
    def test_make_uid(self):
        """Test _make_uid method."""
        service = UnifiedParserService(async_mode=False)
        
        uid1 = service._make_uid("http://example.com", "Test News")
        uid2 = service._make_uid("http://example.com", "Test News")
        uid3 = service._make_uid("http://other.com", "Test News")
        
        assert uid1 == uid2  # Same URL and title should produce same UID
        assert uid1 != uid3  # Different URL should produce different UID
        assert len(uid1) == 64  # SHA256 produces 64-character hex string
    
    def test_get_parser_stats(self):
        """Test get_parser_stats method."""
        service = UnifiedParserService(async_mode=False)
        
        news_items = [
            {
                "source": "Source 1",
                "category": "tech",
                "subcategory": "ai",
                "published_at": "2025-01-01",
                "content": "Short content"
            },
            {
                "source": "Source 2",
                "category": "tech",
                "subcategory": "mobile",
                "published_at": None,
                "content": "This is a much longer content that should increase the average length"
            },
            {
                "source": "Source 1",
                "category": "crypto",
                "subcategory": "bitcoin",
                "published_at": "2025-01-01",
                "content": "Medium content length"
            }
        ]
        
        stats = service.get_parser_stats(news_items)
        
        assert stats["total_items"] == 3
        assert stats["sources_count"] == 2  # Source 1, Source 2
        assert stats["categories_count"] == 2  # tech, crypto
        assert stats["subcategories_count"] == 3  # ai, mobile, bitcoin
        assert stats["items_with_dates"] == 2  # 2 items have published_at
        assert stats["avg_content_length"] > 0
    
    def test_get_parser_stats_empty(self):
        """Test get_parser_stats with empty news list."""
        service = UnifiedParserService(async_mode=False)
        
        stats = service.get_parser_stats([])
        
        assert stats["total_items"] == 0
        assert stats["sources_count"] == 0
        assert stats["categories_count"] == 0
        assert stats["subcategories_count"] == 0
        assert stats["items_with_dates"] == 0
        assert stats["avg_content_length"] == 0


class TestGlobalServices:
    """Test global service instances."""
    
    def test_get_sync_parser_service(self):
        """Test get_sync_parser_service returns singleton instance."""
        # Reset global state
        import parsers.unified_parser_service
        parsers.unified_parser_service._sync_parser_service = None
        
        with patch('parsers.unified_parser_service.UnifiedParserService') as mock_service:
            service1 = get_sync_parser_service()
            service2 = get_sync_parser_service()
            
            # Should return same instance
            assert service1 == service2
            mock_service.assert_called_once_with(async_mode=False)
    
    def test_get_async_parser_service(self):
        """Test get_async_parser_service returns singleton instance."""
        # Reset global state
        import parsers.unified_parser_service
        parsers.unified_parser_service._async_parser_service = None
        
        with patch('parsers.unified_parser_service.UnifiedParserService') as mock_service:
            service1 = get_async_parser_service()
            service2 = get_async_parser_service()
            
            # Should return same instance
            assert service1 == service2
            mock_service.assert_called_once_with(async_mode=True)


class TestBackwardCompatibility:
    """Test backward compatibility functions."""
    
    def test_backward_compatibility_parse_all_sources(self):
        """Test backward compatibility for parse_all_sources."""
        with patch('parsers.unified_parser_service.get_sync_parser_service') as mock_get_service:
            mock_service = Mock()
            mock_service.parse_all_sources.return_value = [{"title": "Test News"}]
            mock_get_service.return_value = mock_service
            
            news_items = parse_all_sources(per_source_limit=5)
            
            assert len(news_items) == 1
            assert news_items[0]["title"] == "Test News"
            mock_service.parse_all_sources.assert_called_once_with(5, False)
    
    @pytest.mark.asyncio
    async def test_backward_compatibility_async_parse_all_sources(self):
        """Test backward compatibility for async_parse_all_sources."""
        with patch('parsers.unified_parser_service.get_async_parser_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.async_parse_all_sources.return_value = [{"title": "Async Test News"}]
            mock_get_service.return_value = mock_service
            
            news_items = await async_parse_all_sources(per_source_limit=3)
            
            assert len(news_items) == 1
            assert news_items[0]["title"] == "Async Test News"
            mock_service.async_parse_all_sources.assert_called_once_with(3, False)
    
    def test_backward_compatibility_parse_source(self):
        """Test backward compatibility for parse_source."""
        with patch('parsers.unified_parser_service.get_sync_parser_service') as mock_get_service:
            mock_service = Mock()
            mock_service.parse_source.return_value = [{"title": "Source News"}]
            mock_get_service.return_value = mock_service
            
            news_items = parse_source(
                url="http://example.com/rss",
                category="tech",
                subcategory="ai",
                source_name="Test Source"
            )
            
            assert len(news_items) == 1
            assert news_items[0]["title"] == "Source News"
            mock_service.parse_source.assert_called_once_with(
                "http://example.com/rss", "tech", "ai", "Test Source", None
            )
    
    def test_backward_compatibility_parse_and_save(self):
        """Test backward compatibility for parse_and_save."""
        with patch('parsers.unified_parser_service.get_sync_parser_service') as mock_get_service:
            mock_service = Mock()
            mock_service.parse_and_save.return_value = 5
            mock_get_service.return_value = mock_service
            
            saved_count = parse_and_save(per_source_limit=10)
            
            assert saved_count == 5
            mock_service.parse_and_save.assert_called_once_with(10)

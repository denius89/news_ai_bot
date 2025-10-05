"""
Tests for unified DatabaseService.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from database.service import DatabaseService, get_sync_service, get_async_service


class TestDatabaseService:
    """Test cases for DatabaseService."""

    def test_init_sync_mode(self):
        """Test initialization in sync mode."""
        with patch('database.service.create_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client

            service = DatabaseService(async_mode=False)

            assert not service.async_mode
            assert service.sync_client == mock_client
            assert service.async_client is None

    @pytest.mark.asyncio
    async def test_init_async_mode(self):
        """Test initialization in async mode."""
        with patch('database.service.create_async_client') as mock_create:
            mock_client = AsyncMock()
            mock_create.return_value = mock_client

            service = DatabaseService(async_mode=True)
            await service._init_async_client()

            assert service.async_mode
            assert service.async_client == mock_client
            assert service.sync_client is None

    def test_get_latest_news_sync(self):
        """Test get_latest_news in sync mode."""
        with patch('database.service.create_client') as mock_create:
            mock_client = Mock()
            mock_query = Mock()
            mock_result = Mock()
            mock_result.data = [{"id": 1, "title": "Test News"}]

            mock_client.table.return_value.select.return_value.order.return_value.limit.return_value = (
                mock_query
            )
            mock_query.eq.return_value = mock_query
            mock_query.in_.return_value = mock_query
            mock_query.execute.return_value = mock_result

            mock_create.return_value = mock_client

            service = DatabaseService(async_mode=False)
            result = service.get_latest_news(limit=5)

            assert len(result) == 1
            assert result[0]["title"] == "Test News"
            mock_client.table.assert_called_once_with("news")

    def test_get_latest_news_sync_with_filters(self):
        """Test get_latest_news with filters in sync mode."""
        with patch('database.service.create_client') as mock_create:
            mock_client = Mock()
            mock_query = Mock()
            mock_result = Mock()
            mock_result.data = []

            mock_client.table.return_value.select.return_value.order.return_value.limit.return_value = (
                mock_query
            )
            mock_query.eq.return_value = mock_query
            mock_query.in_.return_value = mock_query
            mock_query.execute.return_value = mock_result

            mock_create.return_value = mock_client

            service = DatabaseService(async_mode=False)
            result = service.get_latest_news(
                source="test_source", categories=["crypto", "tech"], limit=10
            )

            assert result == []
            # Verify filters were applied
            mock_query.eq.assert_called_with("source", "test_source")
            mock_query.in_.assert_called_with("category", ["crypto", "tech"])

    def test_get_latest_news_no_client(self):
        """Test get_latest_news when client is not initialized."""
        service = DatabaseService(async_mode=False)
        service.sync_client = None

        result = service.get_latest_news()
        assert result == []

    def test_upsert_news_sync(self):
        """Test upsert_news in sync mode."""
        with patch('database.service.create_client') as mock_create:
            mock_client = Mock()
            mock_query = Mock()
            mock_result = Mock()

            mock_client.table.return_value.upsert.return_value = mock_query
            mock_query.execute.return_value = mock_result

            mock_create.return_value = mock_client

            service = DatabaseService(async_mode=False)

            # Mock AI analysis
            with patch.object(service, '_enrich_news_with_ai') as mock_enrich:
                mock_enrich.return_value = {
                    "title": "Test News",
                    "content": "Test content",
                    "link": "http://example.com",
                    "source": "test",
                    "category": "crypto",
                    "credibility": 0.8,
                    "importance": 0.7,
                }

                items = [{"title": "Test News", "content": "Test content"}]
                result = service.upsert_news(items)

                assert result == 1
                mock_client.table.assert_called_with("news")
                mock_query.execute.assert_called_once()

    def test_upsert_news_empty_list(self):
        """Test upsert_news with empty list."""
        with patch('database.service.create_client'):
            service = DatabaseService(async_mode=False)
            result = service.upsert_news([])
            assert result == 0

    def test_prepare_news_items(self):
        """Test _prepare_news_items method."""
        service = DatabaseService(async_mode=False)

        # Mock AI analysis
        with patch.object(service, '_enrich_news_with_ai') as mock_enrich:
            mock_enrich.return_value = {
                "title": "Test News",
                "content": "Test content",
                "link": "http://example.com",
                "source": "test",
                "category": "crypto",
                "subcategory": "bitcoin",
                "credibility": 0.8,
                "importance": 0.7,
            }

            items = [{"title": "Test News", "content": "Test content"}]
            result = service._prepare_news_items(items)

            assert len(result) == 1
            row = result[0]
            assert row["title"] == "Test News"
            assert row["content"] == "Test content"
            assert row["source"] == "test"
            assert row["category"] == "crypto"
            assert row["subcategory"] == "bitcoin"
            assert row["credibility"] == 0.8
            assert row["importance"] == 0.7
            assert "uid" in row

    def test_make_uid(self):
        """Test _make_uid method."""
        service = DatabaseService(async_mode=False)

        uid1 = service._make_uid("http://example.com", "Test News")
        uid2 = service._make_uid("http://example.com", "Test News")
        uid3 = service._make_uid("http://other.com", "Test News")

        assert uid1 == uid2  # Same URL and title should produce same UID
        assert uid1 != uid3  # Different URL should produce different UID
        assert len(uid1) == 64  # SHA256 produces 64-character hex string

    def test_enrich_news_with_ai(self):
        """Test _enrich_news_with_ai method."""
        service = DatabaseService(async_mode=False)

        with (
            patch('database.service.evaluate_credibility') as mock_cred,
            patch('database.service.evaluate_importance') as mock_imp,
        ):

            mock_cred.return_value = 0.8
            mock_imp.return_value = 0.7

            news_item = {"title": "Test News", "content": "Test content"}
            result = service._enrich_news_with_ai(news_item)

            assert result["credibility"] == 0.8
            assert result["importance"] == 0.7
            mock_cred.assert_called_once_with(news_item)
            mock_imp.assert_called_once_with(news_item)

    def test_enrich_news_with_ai_error(self):
        """Test _enrich_news_with_ai when AI analysis fails."""
        service = DatabaseService(async_mode=False)

        with patch('database.service.evaluate_credibility', side_effect=Exception("AI Error")):
            news_item = {"title": "Test News", "content": "Test content"}
            result = service._enrich_news_with_ai(news_item)

            assert result["credibility"] == 0.5  # Default value
            assert result["importance"] == 0.5  # Default value


class TestGlobalServices:
    """Test global service instances."""

    def test_get_sync_service(self):
        """Test get_sync_service returns singleton instance."""
        # Reset global state
        import database.service

        database.service._sync_service = None

        with patch('database.service.DatabaseService') as mock_service:
            service1 = get_sync_service()
            service2 = get_sync_service()

            # Should return same instance
            assert service1 == service2
            mock_service.assert_called_once_with(async_mode=False)

    def test_get_async_service(self):
        """Test get_async_service returns singleton instance."""
        # Reset global state
        import database.service

        database.service._async_service = None

        with patch('database.service.DatabaseService') as mock_service:
            service1 = get_async_service()
            service2 = get_async_service()

            # Should return same instance
            assert service1 == service2
            mock_service.assert_called_once_with(async_mode=True)


class TestBackwardCompatibility:
    """Test backward compatibility functions."""

    def test_backward_compatibility_get_latest_news(self):
        """Test backward compatibility for get_latest_news."""
        with patch('database.service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_latest_news.return_value = [{"id": 1}]
            mock_get_service.return_value = mock_service

            from database.service import get_latest_news

            result = get_latest_news(source="test", limit=5)

            assert result == [{"id": 1}]
            mock_service.get_latest_news.assert_called_once_with("test", None, 5)

    def test_backward_compatibility_upsert_news(self):
        """Test backward compatibility for upsert_news."""
        with patch('database.service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_service.upsert_news.return_value = 2
            mock_get_service.return_value = mock_service

            from database.service import upsert_news

            result = upsert_news([{"title": "Test"}])

            assert result == 2
            mock_service.upsert_news.assert_called_once_with([{"title": "Test"}])

    @pytest.mark.asyncio
    async def test_backward_compatibility_async_get_latest_news(self):
        """Test backward compatibility for async_get_latest_news."""
        with patch('database.service.get_async_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.async_get_latest_news.return_value = [{"id": 1}]
            mock_get_service.return_value = mock_service

            from database.service import async_get_latest_news

            result = await async_get_latest_news(source="test", limit=5)

            assert result == [{"id": 1}]
            mock_service.async_get_latest_news.assert_called_once_with("test", None, 5)

    @pytest.mark.asyncio
    async def test_backward_compatibility_async_upsert_news(self):
        """Test backward compatibility for async_upsert_news."""
        with patch('database.service.get_async_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.async_upsert_news.return_value = 2
            mock_get_service.return_value = mock_service

            from database.service import async_upsert_news

            result = await async_upsert_news([{"title": "Test"}])

            assert result == 2
            mock_service.async_upsert_news.assert_called_once_with([{"title": "Test"}])

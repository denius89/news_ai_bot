"""
Tests for unified services.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from services.unified_digest_service import (
    UnifiedDigestService,
    get_sync_digest_service,
    get_async_digest_service,
    build_daily_digest,
    build_ai_digest,
)
from services.unified_user_service import (
    UnifiedUserService,
    get_sync_user_service,
    get_async_user_service,
    get_or_create_user,
    add_subscription,
    remove_subscription,
    list_subscriptions,
)


class TestUnifiedDigestService:
    """Test cases for UnifiedDigestService."""

    def test_init_sync_mode(self):
        """Test initialization in sync mode."""
        service = UnifiedDigestService(async_mode=False)

        assert not service.async_mode
        assert service.sync_service is not None
        assert service.async_service is not None
        assert service.news_repo is not None

    def test_init_async_mode(self):
        """Test initialization in async mode."""
        service = UnifiedDigestService(async_mode=True)

        assert service.async_mode
        assert service.sync_service is not None
        assert service.async_service is not None
        assert service.news_repo is None  # Will be initialized async

    @patch('services.unified_digest_service.NewsRepository')
    def test_generate_digest_empty(self, mock_repo_class):
        """Test generate_digest with no news items."""
        mock_repo = Mock()
        mock_repo.get_recent_news.return_value = []
        mock_repo_class.return_value = mock_repo

        service = UnifiedDigestService(async_mode=False)
        service.news_repo = mock_repo

        result = service.generate_digest(limit=10, categories=["tech"])

        assert "Сегодня новостей нет" in result
        mock_repo.get_recent_news.assert_called_once_with(limit=10, categories=["tech"])

    @patch('services.unified_digest_service.NewsRepository')
    @patch('services.unified_digest_service.format_news')
    def test_generate_digest_normal(self, mock_format, mock_repo_class):
        """Test generate_digest with normal formatting."""
        mock_news = [{"title": "Test News", "content": "Test content"}]
        mock_repo = Mock()
        mock_repo.get_recent_news.return_value = mock_news
        mock_repo_class.return_value = mock_repo

        mock_format.return_value = "Formatted News"

        service = UnifiedDigestService(async_mode=False)
        service.news_repo = mock_repo

        result = service.generate_digest(limit=5, categories=["crypto"])

        assert result == "Formatted News"
        mock_repo.get_recent_news.assert_called_once_with(limit=5, categories=["crypto"])
        mock_format.assert_called_once_with(mock_news, limit=5, with_header=True)

    @patch('services.unified_digest_service.NewsRepository')
    @patch('services.unified_digest_service.generate_batch_summary')
    def test_generate_digest_ai(self, mock_ai, mock_repo_class):
        """Test generate_digest with AI enhancement."""
        mock_news = [{"title": "AI News", "content": "AI content"}]
        mock_repo = Mock()
        mock_repo.get_recent_news.return_value = mock_news
        mock_repo_class.return_value = mock_repo

        mock_ai.return_value = "AI Summary"

        service = UnifiedDigestService(async_mode=False)
        service.news_repo = mock_repo

        result = service.generate_digest(limit=3, categories=["sports"], ai=True)

        assert "🤖 AI DIGEST" in result
        assert "AI Summary" in result
        assert "cat=sports" in result
        mock_ai.assert_called_once_with(mock_news, style="analytical")

    @pytest.mark.asyncio
    async def test_async_generate_digest(self):
        """Test async generate_digest."""
        with patch('services.unified_digest_service.get_async_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_get_service.return_value = mock_service

            with patch('services.unified_digest_service.NewsRepository') as mock_repo_class:
                mock_repo = AsyncMock()
                mock_repo.async_get_recent_news.return_value = []
                mock_repo_class.return_value = mock_repo

                service = UnifiedDigestService(async_mode=True)
                service.async_service = mock_service

                result = await service.async_generate_digest(limit=10, categories=["tech"])

                assert "Сегодня новостей нет" in result
                mock_repo.async_get_recent_news.assert_called_once_with(
                    limit=10, categories=["tech"]
                )

    def test_build_daily_digest_backward_compat(self):
        """Test backward compatibility for build_daily_digest."""
        with patch('services.unified_digest_service.get_sync_digest_service') as mock_get_service:
            mock_service = Mock()
            mock_service.build_daily_digest.return_value = "Daily Digest"
            mock_get_service.return_value = mock_service

            result = build_daily_digest(limit=5, categories=["crypto"])

            assert result == "Daily Digest"
            mock_service.build_daily_digest.assert_called_once_with(limit=5, categories=["crypto"])

    def test_build_ai_digest_backward_compat(self):
        """Test backward compatibility for build_ai_digest."""
        with patch('services.unified_digest_service.get_sync_digest_service') as mock_get_service:
            mock_service = Mock()
            mock_service.build_ai_digest.return_value = "AI Digest"
            mock_get_service.return_value = mock_service

            result = build_ai_digest(limit=3, categories=["sports"], style="analytical")

            assert result == "AI Digest"
            mock_service.build_ai_digest.assert_called_once_with(
                limit=3, categories=["sports"], style="analytical"
            )


class TestUnifiedUserService:
    """Test cases for UnifiedUserService."""

    def test_init_sync_mode(self):
        """Test initialization in sync mode."""
        service = UnifiedUserService(async_mode=False)

        assert not service.async_mode
        assert service.sync_service is not None
        assert service.async_service is not None

    def test_init_async_mode(self):
        """Test initialization in async mode."""
        service = UnifiedUserService(async_mode=True)

        assert service.async_mode
        assert service.sync_service is not None
        assert service.async_service is not None

    def test_get_or_create_user_existing(self):
        """Test get_or_create_user with existing user."""
        with patch('services.unified_user_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_user_by_telegram.return_value = {"id": "user123"}
            mock_get_service.return_value = mock_service

            service = UnifiedUserService(async_mode=False)
            service.sync_service = mock_service

            result = service.get_or_create_user(12345, "testuser")

            assert result == "user123"
            mock_service.get_user_by_telegram.assert_called_once_with(12345)
            mock_service.upsert_user_by_telegram.assert_not_called()

    def test_get_or_create_user_new(self):
        """Test get_or_create_user with new user."""
        with patch('services.unified_user_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_user_by_telegram.return_value = None
            mock_service.upsert_user_by_telegram.return_value = "newuser123"
            mock_get_service.return_value = mock_service

            service = UnifiedUserService(async_mode=False)
            service.sync_service = mock_service

            result = service.get_or_create_user(12345, "newuser")

            assert result == "newuser123"
            mock_service.get_user_by_telegram.assert_called_once_with(12345)
            mock_service.upsert_user_by_telegram.assert_called_once_with(12345, "newuser", "ru")

    def test_add_subscription(self):
        """Test add_subscription."""
        with patch('services.unified_user_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_service.add_subscription.return_value = True
            mock_get_service.return_value = mock_service

            service = UnifiedUserService(async_mode=False)
            service.sync_service = mock_service

            result = service.add_subscription("user123", "crypto")

            assert result is True
            mock_service.add_subscription.assert_called_once_with("user123", "crypto")

    def test_remove_subscription(self):
        """Test remove_subscription."""
        with patch('services.unified_user_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_service.remove_subscription.return_value = 1
            mock_get_service.return_value = mock_service

            service = UnifiedUserService(async_mode=False)
            service.sync_service = mock_service

            result = service.remove_subscription("user123", "tech")

            assert result == 1
            mock_service.remove_subscription.assert_called_once_with("user123", "tech")

    def test_list_subscriptions(self):
        """Test list_subscriptions."""
        with patch('services.unified_user_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_subscriptions = [{"category": "crypto"}, {"category": "tech"}]
            mock_service.get_user_subscriptions.return_value = mock_subscriptions
            mock_get_service.return_value = mock_service

            service = UnifiedUserService(async_mode=False)
            service.sync_service = mock_service

            result = service.list_subscriptions("user123")

            assert result == mock_subscriptions
            mock_service.get_user_subscriptions.assert_called_once_with("user123")

    @pytest.mark.asyncio
    async def test_async_get_or_create_user(self):
        """Test async_get_or_create_user."""
        with patch('services.unified_user_service.get_async_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_user_by_telegram.return_value = {"id": "asyncuser123"}
            mock_get_service.return_value = mock_service

            service = UnifiedUserService(async_mode=True)
            service.async_service = mock_service

            result = await service.async_get_or_create_user(67890, "asyncuser")

            assert result == "asyncuser123"
            mock_service.get_user_by_telegram.assert_called_once_with(67890)
            mock_service.upsert_user_by_telegram.assert_not_called()

    def test_upsert_notification(self):
        """Test upsert_notification."""
        with patch('services.unified_user_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service

            service = UnifiedUserService(async_mode=False)
            service.sync_service = mock_service

            service.upsert_notification(12345, "digest", "daily", True, 9)

            mock_service.upsert_notification.assert_called_once_with(
                12345, "digest", "daily", True, 9
            )

    def test_convenience_methods(self):
        """Test convenience methods."""
        with patch('services.unified_user_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service

            service = UnifiedUserService(async_mode=False)
            service.sync_service = mock_service

            # Test convenience methods
            service.upsert_digest_daily("user123", 8)
            service.upsert_events_daily("user123", 10)
            service.upsert_breaking_instant("user123")

            assert mock_service.upsert_notification.call_count == 3

    def test_global_service_instances(self):
        """Test global service instances."""
        service1 = get_sync_user_service()
        service2 = get_sync_user_service()

        # Should return same instance
        assert service1 is service2
        assert not service1.async_mode

        async_service1 = get_async_user_service()
        async_service2 = get_async_user_service()

        # Should return same instance
        assert async_service1 is async_service2
        assert async_service1.async_mode

    def test_backward_compatibility_functions(self):
        """Test backward compatibility functions."""
        with patch('services.unified_user_service.get_sync_user_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_or_create_user.return_value = "user123"
            mock_service.add_subscription.return_value = True
            mock_service.remove_subscription.return_value = 1
            mock_service.list_subscriptions.return_value = [{"category": "crypto"}]
            mock_get_service.return_value = mock_service

            # Test backward compatibility functions
            assert get_or_create_user(12345, "test") == "user123"
            assert add_subscription("user123", "crypto") is True
            assert remove_subscription("user123", "tech") == 1
            assert list_subscriptions("user123") == [{"category": "crypto"}]

            mock_service.get_or_create_user.assert_called_once_with(12345, "test")
            mock_service.add_subscription.assert_called_once_with("user123", "crypto")
            mock_service.remove_subscription.assert_called_once_with("user123", "tech")
            mock_service.list_subscriptions.assert_called_once_with("user123")


class TestServiceIntegration:
    """Integration tests for unified services."""

    def test_digest_service_integration(self):
        """Test digest service integration."""
        sync_service = get_sync_digest_service()
        async_service = get_async_digest_service()

        assert sync_service is not async_service
        assert not sync_service.async_mode
        assert async_service.async_mode

    def test_user_service_integration(self):
        """Test user service integration."""
        sync_service = get_sync_user_service()
        async_service = get_async_user_service()

        assert sync_service is not async_service
        assert not sync_service.async_mode
        assert async_service.async_mode

    def test_services_initialization(self):
        """Test that all services initialize properly."""
        # Test sync services
        sync_digest = get_sync_digest_service()
        sync_user = get_sync_user_service()

        assert sync_digest.sync_service is not None
        assert sync_user.sync_service is not None

        # Test async services
        async_digest = get_async_digest_service()
        async_user = get_async_user_service()

        assert async_digest.async_service is not None
        assert async_user.async_service is not None

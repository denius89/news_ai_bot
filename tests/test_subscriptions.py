"""
Unit tests for subscription and notification services.

Tests SubscriptionService and NotificationService with mocked database functions.
"""

import pytest
from unittest.mock import patch

from services.subscription_service import SubscriptionService
from services.notification_service import NotificationService


class TestSubscriptionService:
    """Test cases for SubscriptionService."""

    @pytest.mark.asyncio
    async def test_get_or_create_user_existing_user(self):
        """Test get_or_create_user with existing user."""
        service = SubscriptionService()

        # Mock existing user data
        mock_user = {"id": "uuid-123", "telegram_id": 456789, "username": "testuser"}

        with patch("services.subscription_service.db_models") as mock_db:
            # Mock get_user_by_telegram to return existing user
            mock_db.get_user_by_telegram.return_value = mock_user

            result = await service.get_or_create_user(456789, "testuser", "ru")

            assert result == "uuid-123"
            mock_db.get_user_by_telegram.assert_called_once_with(456789)
            mock_db.upsert_user_by_telegram.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_or_create_user_new_user(self):
        """Test get_or_create_user with new user."""
        service = SubscriptionService()

        with patch("services.subscription_service.db_models") as mock_db:
            # Mock get_user_by_telegram to return None (user not found)
            mock_db.get_user_by_telegram.return_value = None
            # Mock upsert_user_by_telegram to return new user ID
            mock_db.upsert_user_by_telegram.return_value = "uuid-456"

            result = await service.get_or_create_user(456789, "newuser", "en")

            assert result == "uuid-456"
            mock_db.get_user_by_telegram.assert_called_once_with(456789)
            mock_db.upsert_user_by_telegram.assert_called_once_with(456789, "newuser", "en")

    @pytest.mark.asyncio
    async def test_add_subscription_success(self):
        """Test successful subscription addition."""
        service = SubscriptionService()

        with patch("services.subscription_service.db_models") as mock_db:
            mock_db.add_subscription.return_value = True

            result = await service.add("uuid-123", "crypto")

            assert result is True
            mock_db.add_subscription.assert_called_once_with("uuid-123", "crypto")

    @pytest.mark.asyncio
    async def test_add_subscription_already_exists(self):
        """Test subscription addition when already exists."""
        service = SubscriptionService()

        with patch("services.subscription_service.db_models") as mock_db:
            mock_db.add_subscription.return_value = False

            result = await service.add(123, "economy")

            assert result is False
            mock_db.add_subscription.assert_called_once_with(123, "economy")

    @pytest.mark.asyncio
    async def test_remove_subscription_success(self):
        """Test successful subscription removal."""
        service = SubscriptionService()

        with patch("services.subscription_service.db_models") as mock_db:
            mock_db.remove_subscription.return_value = 1

            result = await service.remove(123, "tech")

            assert result == 1
            mock_db.remove_subscription.assert_called_once_with(123, "tech")

    @pytest.mark.asyncio
    async def test_remove_subscription_not_found(self):
        """Test subscription removal when subscription doesn't exist."""
        service = SubscriptionService()

        with patch("services.subscription_service.db_models") as mock_db:
            mock_db.remove_subscription.return_value = 0

            result = await service.remove(123, "politics")

            assert result == 0
            mock_db.remove_subscription.assert_called_once_with(123, "politics")

    @pytest.mark.asyncio
    async def test_list_subscriptions(self):
        """Test listing user subscriptions."""
        service = SubscriptionService()

        mock_subscriptions = [
            {"id": 1, "user_id": 123, "category": "crypto", "created_at": "2025-10-02T10:00:00Z"},
            {"id": 2, "user_id": 123, "category": "economy", "created_at": "2025-10-02T10:05:00Z"},
        ]

        with patch("services.subscription_service.db_models") as mock_db:
            mock_db.list_subscriptions.return_value = mock_subscriptions

            result = await service.list(123)

            assert result == mock_subscriptions
            assert len(result) == 2
            assert result[0]["category"] == "crypto"
            assert result[1]["category"] == "economy"
            mock_db.list_subscriptions.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_list_subscriptions_empty(self):
        """Test listing subscriptions when user has none."""
        service = SubscriptionService()

        with patch("services.subscription_service.db_models") as mock_db:
            mock_db.list_subscriptions.return_value = []

            result = await service.list(123)

            assert result == []
            mock_db.list_subscriptions.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_success(self):
        """Test getting user by telegram ID."""
        service = SubscriptionService()

        mock_user = {"id": 123, "telegram_id": 456789, "username": "testuser", "locale": "ru"}

        with patch("services.subscription_service.db_models") as mock_db:
            mock_db.get_user_by_telegram.return_value = mock_user

            result = await service.get_user_by_telegram(456789)

            assert result == mock_user
            mock_db.get_user_by_telegram.assert_called_once_with(456789)

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_not_found(self):
        """Test getting user by telegram ID when user doesn't exist."""
        service = SubscriptionService()

        with patch("services.subscription_service.db_models") as mock_db:
            mock_db.get_user_by_telegram.return_value = None

            result = await service.get_user_by_telegram(456789)

            assert result is None
            mock_db.get_user_by_telegram.assert_called_once_with(456789)

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in subscription service methods."""
        service = SubscriptionService()

        with patch("services.subscription_service.db_models") as mock_db:
            # Mock database error
            mock_db.add_subscription.side_effect = Exception("Database error")

            # Should return False on error
            result = await service.add(123, "crypto")
            assert result is False


class TestNotificationService:
    """Test cases for NotificationService."""

    @pytest.mark.asyncio
    async def test_upsert_digest_daily(self):
        """Test setting up daily digest notifications."""
        service = NotificationService()

        with patch("services.notification_service.db_models") as mock_db:
            mock_db.upsert_notification.return_value = None

            await service.upsert_digest_daily(123, 9)

            mock_db.upsert_notification.assert_called_once_with(123, "digest", "daily", True, 9)

    @pytest.mark.asyncio
    async def test_upsert_digest_daily_default_hour(self):
        """Test setting up daily digest with default hour."""
        service = NotificationService()

        with patch("services.notification_service.db_models") as mock_db:
            mock_db.upsert_notification.return_value = None

            await service.upsert_digest_daily(123)

            mock_db.upsert_notification.assert_called_once_with(123, "digest", "daily", True, 9)

    @pytest.mark.asyncio
    async def test_upsert_events_daily(self):
        """Test setting up daily events notifications."""
        service = NotificationService()

        with patch("services.notification_service.db_models") as mock_db:
            mock_db.upsert_notification.return_value = None

            await service.upsert_events_daily(123, 10)

            mock_db.upsert_notification.assert_called_once_with(123, "events", "daily", True, 10)

    @pytest.mark.asyncio
    async def test_upsert_breaking_instant(self):
        """Test setting up instant breaking news notifications."""
        service = NotificationService()

        with patch("services.notification_service.db_models") as mock_db:
            mock_db.upsert_notification.return_value = None

            await service.upsert_breaking_instant(123)

            mock_db.upsert_notification.assert_called_once_with(123, "breaking", "instant", True, 0)

    @pytest.mark.asyncio
    async def test_disable_notification(self):
        """Test disabling a notification type."""
        service = NotificationService()

        with patch("services.notification_service.db_models") as mock_db:
            mock_db.upsert_notification.return_value = None

            await service.disable(123, "digest")

            mock_db.upsert_notification.assert_called_once_with(123, "digest", "daily", False, 9)

    @pytest.mark.asyncio
    async def test_enable_notification(self):
        """Test enabling a notification type."""
        service = NotificationService()

        with patch("services.notification_service.db_models") as mock_db:
            mock_db.upsert_notification.return_value = None

            await service.enable(123, "events", "weekly", 14)

            mock_db.upsert_notification.assert_called_once_with(123, "events", "weekly", True, 14)

    @pytest.mark.asyncio
    async def test_upsert_custom_notification(self):
        """Test custom notification settings."""
        service = NotificationService()

        with patch("services.notification_service.db_models") as mock_db:
            mock_db.upsert_notification.return_value = None

            await service.upsert_custom(123, "breaking", "instant", True, 0)

            mock_db.upsert_notification.assert_called_once_with(123, "breaking", "instant", True, 0)

    @pytest.mark.asyncio
    async def test_list_notifications(self):
        """Test listing user notification settings."""
        service = NotificationService()

        mock_notifications = [
            {
                "id": 1,
                "user_id": 123,
                "type": "digest",
                "frequency": "daily",
                "enabled": True,
                "preferred_hour": 9,
                "created_at": "2025-10-02T10:00:00Z",
            },
            {
                "id": 2,
                "user_id": 123,
                "type": "events",
                "frequency": "weekly",
                "enabled": False,
                "preferred_hour": 10,
                "created_at": "2025-10-02T10:05:00Z",
            },
        ]

        with patch("services.notification_service.db_models") as mock_db:
            mock_db.list_notifications.return_value = mock_notifications

            result = await service.list(123)

            assert result == mock_notifications
            assert len(result) == 2
            assert result[0]["type"] == "digest"
            assert result[1]["type"] == "events"
            mock_db.list_notifications.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_list_notifications_empty(self):
        """Test listing notifications when user has none."""
        service = NotificationService()

        with patch("services.notification_service.db_models") as mock_db:
            mock_db.list_notifications.return_value = []

            result = await service.list(123)

            assert result == []
            mock_db.list_notifications.assert_called_once_with(123)

    @pytest.mark.asyncio
    async def test_get_by_type_found(self):
        """Test getting notification by type when found."""
        service = NotificationService()

        mock_notifications = [
            {"id": 1, "user_id": 123, "type": "digest", "enabled": True},
            {"id": 2, "user_id": 123, "type": "events", "enabled": False},
        ]

        with patch.object(service, "list", return_value=mock_notifications):
            result = await service.get_by_type(123, "digest")

            assert result == mock_notifications[0]
            assert result["type"] == "digest"
            assert result["enabled"] is True

    @pytest.mark.asyncio
    async def test_get_by_type_not_found(self):
        """Test getting notification by type when not found."""
        service = NotificationService()

        mock_notifications = [
            {"id": 1, "user_id": 123, "type": "digest", "enabled": True},
        ]

        with patch.object(service, "list", return_value=mock_notifications):
            result = await service.get_by_type(123, "events")

            assert result is None

    @pytest.mark.asyncio
    async def test_is_enabled_true(self):
        """Test checking if notification is enabled (returns True)."""
        service = NotificationService()

        mock_notification = {"id": 1, "user_id": 123, "type": "digest", "enabled": True}

        with patch.object(service, "get_by_type", return_value=mock_notification):
            result = await service.is_enabled(123, "digest")

            assert result is True

    @pytest.mark.asyncio
    async def test_is_enabled_false(self):
        """Test checking if notification is enabled (returns False)."""
        service = NotificationService()

        mock_notification = {"id": 1, "user_id": 123, "type": "events", "enabled": False}

        with patch.object(service, "get_by_type", return_value=mock_notification):
            result = await service.is_enabled(123, "events")

            assert result is False

    @pytest.mark.asyncio
    async def test_is_enabled_not_found(self):
        """Test checking if notification is enabled when notification doesn't exist."""
        service = NotificationService()

        with patch.object(service, "get_by_type", return_value=None):
            result = await service.is_enabled(123, "breaking")

            assert result is False

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in notification service methods."""
        service = NotificationService()

        with patch("services.notification_service.db_models") as mock_db:
            # Mock database error
            mock_db.upsert_notification.side_effect = Exception("Database error")

            # Should not raise exception
            await service.upsert_digest_daily(123, 9)
            mock_db.upsert_notification.assert_called_once()


@pytest.mark.asyncio
async def test_global_service_instances():
    """Test that global service instances are properly initialized."""
    from services.subscription_service import subscription_service
    from services.notification_service import notification_service

    assert isinstance(subscription_service, SubscriptionService)
    assert isinstance(notification_service, NotificationService)

"""
Notification Service - async wrapper for user notification management.

This service provides async methods for managing user notification settings,
wrapping the synchronous database functions from db_models.
"""

import asyncio
import logging
from typing import List, Dict

from database import db_models

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing user notification settings."""

    async def upsert_digest_daily(self, user_id: str, preferred_hour: int = 9) -> None:
        """
        Set up daily digest notifications for user.

        Args:
            user_id: User ID
            preferred_hour: Preferred hour for daily notifications (0-23)
        """
        try:
            await asyncio.to_thread(
                db_models.upsert_notification, user_id, "digest", "daily", True, preferred_hour
            )
            logger.info("Updated digest notification: user_id=%s, hour=%d", user_id, preferred_hour)

        except Exception as e:
            logger.error("Error setting digest notification: %s", e)

    async def upsert_events_daily(self, user_id: str, preferred_hour: int = 9) -> None:
        """
        Set up daily events notifications for user.

        Args:
            user_id: User ID
            preferred_hour: Preferred hour for daily notifications (0-23)
        """
        try:
            await asyncio.to_thread(
                db_models.upsert_notification, user_id, "events", "daily", True, preferred_hour
            )
            logger.info("Updated events notification: user_id=%s, hour=%d", user_id, preferred_hour)

        except Exception as e:
            logger.error("Error setting events notification: %s", e)

    async def upsert_breaking_instant(self, user_id: str) -> None:
        """
        Set up instant breaking news notifications for user.

        Args:
            user_id: User ID
        """
        try:
            await asyncio.to_thread(
                db_models.upsert_notification, user_id, "breaking", "instant", True, 0
            )
            logger.info("Updated breaking news notification: user_id=%s", user_id)

        except Exception as e:
            logger.error("Error setting breaking news notification: %s", e)

    async def disable(self, user_id: str, type_: str) -> None:
        """
        Disable notification of specific type for user.

        Args:
            user_id: User ID
            type_: Notification type ('digest', 'events', 'breaking')
        """
        try:
            await asyncio.to_thread(
                db_models.upsert_notification, user_id, type_, "daily", False, 9
            )
            logger.info("Disabled notification: user_id=%s, type=%s", user_id, type_)

        except Exception as e:
            logger.error("Error disabling notification: %s", e)

    async def enable(
        self, user_id: str, type_: str, frequency: str = "daily", preferred_hour: int = 9
    ) -> None:
        """
        Enable notification of specific type for user.

        Args:
            user_id: User ID
            type_: Notification type ('digest', 'events', 'breaking')
            frequency: Notification frequency ('daily', 'weekly', 'instant')
            preferred_hour: Preferred hour for daily notifications (0-23)
        """
        try:
            await asyncio.to_thread(
                db_models.upsert_notification, user_id, type_, frequency, True, preferred_hour
            )
            logger.info(
                "Enabled notification: user_id=%s, type=%s, frequency=%s", user_id, type_, frequency
            )

        except Exception as e:
            logger.error("Error enabling notification: %s", e)

    async def upsert_custom(
        self,
        user_id: str,
        type_: str,
        frequency: str = "daily",
        enabled: bool = True,
        preferred_hour: int = 9,
    ) -> None:
        """
        Set custom notification settings for user.

        Args:
            user_id: User ID
            type_: Notification type ('digest', 'events', 'breaking')
            frequency: Notification frequency ('daily', 'weekly', 'instant')
            enabled: Whether notification is enabled
            preferred_hour: Preferred hour for daily notifications (0-23)
        """
        try:
            await asyncio.to_thread(
                db_models.upsert_notification, user_id, type_, frequency, enabled, preferred_hour
            )
            logger.info(
                "Updated custom notification: user_id=%s, type=%s, frequency=%s, enabled=%s",
                user_id,
                type_,
                frequency,
                enabled,
            )

        except Exception as e:
            logger.error("Error updating custom notification: %s", e)

    async def list(self, user_id: str) -> List[Dict]:
        """
        Get list of user notification settings.

        Args:
            user_id: User ID

        Returns:
            List of notification setting dictionaries
        """
        try:
            notifications = await asyncio.to_thread(db_models.list_notifications, user_id)
            logger.debug("Retrieved %d notifications for user_id=%s", len(notifications), user_id)
            return notifications

        except Exception as e:
            logger.error("Error listing notifications: %s", e)
            return []

    async def get_by_type(self, user_id: str, type_: str) -> Dict | None:
        """
        Get specific notification setting by type.

        Args:
            user_id: User ID
            type_: Notification type ('digest', 'events', 'breaking')

        Returns:
            Notification setting dict or None if not found
        """
        try:
            notifications = await self.list(user_id)
            for notification in notifications:
                if notification.get("type") == type_:
                    return notification
            return None

        except Exception as e:
            logger.error("Error getting notification by type: %s", e)
            return None

    async def is_enabled(self, user_id: str, type_: str) -> bool:
        """
        Check if specific notification type is enabled for user.

        Args:
            user_id: User ID
            type_: Notification type ('digest', 'events', 'breaking')

        Returns:
            True if notification is enabled, False otherwise
        """
        try:
            notification = await self.get_by_type(user_id, type_)
            return notification.get("enabled", False) if notification else False

        except Exception as e:
            logger.error("Error checking notification status: %s", e)
            return False

    async def get_users_by_notification_type(
        self, type_: str, preferred_hour: int = None
    ) -> List[Dict]:
        """
        Get users with specific notification type and optional hour preference.

        Args:
            type_: Notification type ('digest', 'events', 'breaking')
            preferred_hour: Preferred hour for notifications (0-23), None for any hour

        Returns:
            List of user data dicts with enabled notifications
        """
        try:
            # This is a simplified implementation
            # In a real scenario, you'd query the database directly
            # For now, we'll return an empty list since we don't have
            # a direct database query method for this complex join

            logger.info("Getting users for notification type=%s, hour=%s", type_, preferred_hour)

            # TODO: Implement actual database query:
            # SELECT u.id, u.telegram_id, u.username, u.locale
            # FROM users u
            # JOIN notifications n ON u.id = n.user_id
            # WHERE n.type = ? AND n.enabled = true
            # AND (? IS NULL OR n.preferred_hour = ?)

            # For now, return empty list
            users = []
            logger.info("Found %d users for notification type %s", len(users), type_)
            return users

        except Exception as e:
            logger.error("Error getting users by notification type: %s", e)
            return []


# Global instance for easy import
notification_service = NotificationService()

__all__ = ["NotificationService", "notification_service"]

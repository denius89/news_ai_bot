"""
Subscription Service - async wrapper for user subscription management.

This service provides async methods for managing user subscriptions,
wrapping the synchronous database functions from db_models.
"""

import asyncio
import logging
from typing import List, Dict, Optional

from database import db_models

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for managing user subscriptions and notifications."""

    async def get_or_create_user(
        self, telegram_id: int, username: str | None = None, locale: str = "ru"
    ) -> str:
        """
        Get existing user or create new one by Telegram ID.

        Args:
            telegram_id: Telegram user ID
            username: Telegram username (optional)
            locale: User locale (default: 'ru')

        Returns:
            User ID (UUID string) from database
        """
        try:
            # First try to find existing user
            user = await asyncio.to_thread(db_models.get_user_by_telegram, telegram_id)
            if user:
                logger.debug("Found existing user: ID=%s", user["id"])
                return user["id"]

            # Create new user if not found
            user_id = await asyncio.to_thread(
                db_models.upsert_user_by_telegram, telegram_id, username, locale
            )
            logger.info("Created new user: ID=%s, telegram_id=%s", user_id, telegram_id)
            return user_id

        except Exception as e:
            logger.error("Error in get_or_create_user: %s", e)
            return ""

    async def add(self, user_id: str, category: str) -> bool:
        """
        Add subscription for user to category.

        Args:
            user_id: User ID
            category: News category

        Returns:
            True if subscription was added, False if already exists
        """
        try:
            result = await asyncio.to_thread(db_models.add_subscription, user_id, category)
            logger.info(
                "Subscription add result: user_id=%s, category=%s, added=%s",
                user_id,
                category,
                result,
            )
            return result

        except Exception as e:
            logger.error("Error adding subscription: %s", e)
            return False

    async def remove(self, user_id: str, category: str) -> int:
        """
        Remove subscription for user from category.

        Args:
            user_id: User ID
            category: News category

        Returns:
            Number of subscriptions removed (0 or 1)
        """
        try:
            result = await asyncio.to_thread(db_models.remove_subscription, user_id, category)
            logger.info(
                "Subscription remove result: user_id=%s, category=%s, removed=%d",
                user_id,
                category,
                result,
            )
            return result

        except Exception as e:
            logger.error("Error removing subscription: %s", e)
            return 0

    async def list(self, user_id: str) -> List[Dict]:
        """
        Get list of user subscriptions.

        Args:
            user_id: User ID

        Returns:
            List of subscription dictionaries
        """
        try:
            subscriptions = await asyncio.to_thread(db_models.list_subscriptions, user_id)
            logger.debug("Retrieved %d subscriptions for user_id=%s", len(subscriptions), user_id)
            return subscriptions

        except Exception as e:
            logger.error("Error listing subscriptions: %s", e)
            return []

    async def get_user_by_telegram(self, telegram_id: int) -> Optional[Dict]:
        """
        Get user data by Telegram ID.

        Args:
            telegram_id: Telegram user ID

        Returns:
            User data dict or None if not found
        """
        try:
            user = await asyncio.to_thread(db_models.get_user_by_telegram, telegram_id)
            return user

        except Exception as e:
            logger.error("Error getting user by telegram_id: %s", e)
            return None

    async def upsert_notification(
        self,
        user_id: int,
        type_: str = "digest",
        frequency: str = "daily",
        enabled: bool = True,
        preferred_hour: int = 9,
    ) -> None:
        """
        Create or update notification settings for user.

        Args:
            user_id: User ID
            type_: Notification type ('digest', 'events', 'breaking')
            frequency: Notification frequency ('daily', 'weekly', 'instant')
            enabled: Whether notification is enabled
            preferred_hour: Preferred hour for daily notifications (0-23)
        """
        try:
            await asyncio.to_thread(
                db_models.upsert_notification,
                user_id,
                type_,
                frequency,
                enabled,
                preferred_hour,
            )
            logger.info("Updated notification settings: user_id=%s, type=%s", user_id, type_)

        except Exception as e:
            logger.error("Error updating notification settings: %s", e)

    async def list_notifications(self, user_id: int) -> List[Dict]:
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


# Global instance for easy import
subscription_service = SubscriptionService()

__all__ = ["SubscriptionService", "subscription_service"]

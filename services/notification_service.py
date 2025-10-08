"""
Notification Service for PulseAI.

This module provides notification management functionality for users.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone

from database.service import get_sync_service, get_async_service

logger = logging.getLogger("notification_service")


class NotificationService:
    """Service for managing user notifications."""

    def __init__(self, async_mode: bool = False):
        """
        Initialize notification service.

        Args:
            async_mode: If True, uses async database operations
        """
        self.async_mode = async_mode
        if async_mode:
            self.db_service = get_async_service()
        else:
            self.db_service = get_sync_service()

    async def get_user_notifications(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get user's notifications.

        Args:
            user_id: Telegram user ID
            limit: Maximum number of notifications

        Returns:
            List of notification dictionaries
        """
        try:
            if self.async_mode:
                client = await self.db_service._get_async_client()
                result = await self.db_service.async_safe_execute(
                    client.table("user_notifications")
                    .select("*")
                    .eq("user_id", user_id)
                    .order("timestamp", desc=True)
                    .limit(limit)
                )
            else:
                result = self.db_service.safe_execute(
                    self.db_service.sync_client.table("user_notifications")
                    .select("*")
                    .eq("user_id", user_id)
                    .order("timestamp", desc=True)
                    .limit(limit)
                )

            return result.data or []

        except Exception as e:
            logger.error("❌ Error getting user notifications: %s", e)
            return []

    async def create_notification(self, user_id: int, title: str, text: str, notification_type: str = "info") -> bool:
        """
        Create a new notification for user.

        Args:
            user_id: Telegram user ID
            title: Notification title
            text: Notification text
            notification_type: Type of notification (info, warning, error, success)

        Returns:
            True if successful, False otherwise
        """
        try:
            notification_data = {
                "user_id": user_id,
                "title": title,
                "message": text,
                "category": notification_type,
                "read": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if self.async_mode:
                client = await self.db_service._get_async_client()
                await self.db_service.async_safe_execute(client.table("user_notifications").insert(notification_data))
            else:
                self.db_service.safe_execute(
                    self.db_service.sync_client.table("user_notifications").insert(notification_data)
                )

            logger.info("✅ Created notification for user %d: %s", user_id, title)
            return True

        except Exception as e:
            logger.error("❌ Error creating notification: %s", e)
            return False

    async def mark_notification_read(self, user_id: int, notification_id: int) -> bool:
        """
        Mark a notification as read.

        Args:
            user_id: Telegram user ID
            notification_id: Notification ID

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.async_mode:
                client = await self.db_service._get_async_client()
                await self.db_service.async_safe_execute(
                    client.table("user_notifications")
                    .update({"read": True})
                    .eq("id", notification_id)
                    .eq("user_id", user_id)
                )
            else:
                self.db_service.safe_execute(
                    self.db_service.sync_client.table("user_notifications")
                    .update({"read": True})
                    .eq("id", notification_id)
                    .eq("user_id", user_id)
                )

            logger.info("✅ Marked notification %d as read for user %d", notification_id, user_id)
            return True

        except Exception as e:
            logger.error("❌ Error marking notification as read: %s", e)
            return False

    async def mark_all_notifications_read(self, user_id: int) -> bool:
        """
        Mark all notifications as read for user.

        Args:
            user_id: Telegram user ID

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.async_mode:
                client = await self.db_service._get_async_client()
                await self.db_service.async_safe_execute(
                    client.table("user_notifications").update({"read": True}).eq("user_id", user_id).eq("read", False)
                )
            else:
                self.db_service.safe_execute(
                    self.db_service.sync_client.table("user_notifications")
                    .update({"read": True})
                    .eq("user_id", user_id)
                    .eq("read", False)
                )

            logger.info("✅ Marked all notifications as read for user %d", user_id)
            return True

        except Exception as e:
            logger.error("❌ Error marking all notifications as read: %s", e)
            return False

    async def get_unread_count(self, user_id: int) -> int:
        """
        Get count of unread notifications for user.

        Args:
            user_id: Telegram user ID

        Returns:
            Number of unread notifications
        """
        try:
            if self.async_mode:
                client = await self.db_service._get_async_client()
                result = await self.db_service.async_safe_execute(
                    client.table("user_notifications")
                    .select("id", count="exact")
                    .eq("user_id", user_id)
                    .eq("read", False)
                )
            else:
                result = self.db_service.safe_execute(
                    self.db_service.sync_client.table("user_notifications")
                    .select("id", count="exact")
                    .eq("user_id", user_id)
                    .eq("read", False)
                )

            return result.count or 0

        except Exception as e:
            logger.error("❌ Error getting unread count: %s", e)
            return 0

    async def delete_old_notifications(self, user_id: int, days_old: int = 30) -> int:
        """
        Delete old notifications for user.

        Args:
            user_id: Telegram user ID
            days_old: Delete notifications older than this many days

        Returns:
            Number of deleted notifications
        """
        try:
            cutoff_date = datetime.now(timezone.utc).replace(day=datetime.now(timezone.utc).day - days_old)

            if self.async_mode:
                client = await self.db_service._get_async_client()
                result = await self.db_service.async_safe_execute(
                    client.table("user_notifications")
                    .delete()
                    .eq("user_id", user_id)
                    .lt("timestamp", cutoff_date.isoformat())
                )
            else:
                result = self.db_service.safe_execute(
                    self.db_service.sync_client.table("user_notifications")
                    .delete()
                    .eq("user_id", user_id)
                    .lt("timestamp", cutoff_date.isoformat())
                )

            deleted_count = len(result.data or [])
            logger.info("✅ Deleted %d old notifications for user %d", deleted_count, user_id)
            return deleted_count

        except Exception as e:
            logger.error("❌ Error deleting old notifications: %s", e)
            return 0

    async def enable_auto_digest(self, user_id: int, enabled: bool = True) -> bool:
        """
        Enable or disable auto-digest notifications for user.

        Args:
            user_id: Telegram user ID
            enabled: Whether to enable auto-digest

        Returns:
            True if successful, False otherwise
        """
        try:
            settings_data = {
                "user_id": user_id,
                "auto_digest_enabled": enabled,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            if self.async_mode:
                client = await self.db_service._get_async_client()
                await self.db_service.async_safe_execute(
                    client.table("user_settings").upsert(settings_data, on_conflict="user_id")
                )
            else:
                self.db_service.safe_execute(
                    self.db_service.sync_client.table("user_settings").upsert(settings_data, on_conflict="user_id")
                )

            status = "enabled" if enabled else "disabled"
            logger.info("✅ Auto-digest %s for user %d", status, user_id)
            return True

        except Exception as e:
            logger.error("❌ Error updating auto-digest setting: %s", e)
            return False

    async def is_auto_digest_enabled(self, user_id: int) -> bool:
        """
        Check if auto-digest is enabled for user.

        Args:
            user_id: Telegram user ID

        Returns:
            True if auto-digest is enabled, False otherwise
        """
        try:
            if self.async_mode:
                client = await self.db_service._get_async_client()
                result = await self.db_service.async_safe_execute(
                    client.table("user_settings").select("auto_digest_enabled").eq("user_id", user_id).single()
                )
            else:
                result = self.db_service.safe_execute(
                    self.db_service.sync_client.table("user_settings")
                    .select("auto_digest_enabled")
                    .eq("user_id", user_id)
                    .single()
                )

            if result.data:
                return result.data.get("auto_digest_enabled", False)
            return False

        except Exception as e:
            logger.error("❌ Error checking auto-digest setting: %s", e)
            return False


# Global service instances
_sync_notification_service: Optional[NotificationService] = None
_async_notification_service: Optional[NotificationService] = None


def get_sync_notification_service() -> NotificationService:
    """Get or create sync notification service instance."""
    global _sync_notification_service
    if _sync_notification_service is None:
        _sync_notification_service = NotificationService(async_mode=False)
    return _sync_notification_service


def get_async_notification_service() -> NotificationService:
    """Get or create async notification service instance."""
    global _async_notification_service
    if _async_notification_service is None:
        _async_notification_service = NotificationService(async_mode=True)
    return _async_notification_service


# Backward compatibility functions
async def enable_auto_digest(user_id: int, enabled: bool = True) -> bool:
    """Backward compatibility function for enabling auto-digest."""
    service = get_async_notification_service()
    return await service.enable_auto_digest(user_id, enabled)


async def create_notification(user_id: int, title: str, text: str, notification_type: str = "info") -> bool:
    """Backward compatibility function for creating notifications."""
    service = get_async_notification_service()
    return await service.create_notification(user_id, title, text, notification_type)

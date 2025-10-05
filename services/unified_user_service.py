"""
Unified User Service for PulseAI.

This service consolidates user management, subscriptions, and notifications
into a single interface, eliminating code duplication.
"""

import asyncio
import logging
from typing import List, Dict, Optional

from database.service import get_sync_service, get_async_service

logger = logging.getLogger(__name__)


class UnifiedUserService:
    """
    Unified service for user management, subscriptions, and notifications.
    """
    
    def __init__(self, async_mode: bool = False):
        """
        Initialize unified user service.
        
        Args:
            async_mode: Whether to use async operations
        """
        self.async_mode = async_mode
        self.sync_service = get_sync_service()
        self.async_service = get_async_service()
    
    async def _init_async(self):
        """Initialize async service."""
        if not self.async_mode:
            return
        
        try:
            await self.async_service._init_async_client()
        except Exception as e:
            logger.error(f"Failed to initialize async user service: {e}")
            raise
    
    # User Management
    
    def get_or_create_user(
        self, 
        telegram_id: int, 
        username: Optional[str] = None, 
        locale: str = "ru"
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
            user = self.sync_service.get_user_by_telegram(telegram_id)
            if user:
                logger.debug("Found existing user: ID=%s", user["id"])
                return user["id"]
            
            # Create new user if not found
            user_id = self.sync_service.upsert_user_by_telegram(telegram_id, username, locale)
            logger.info("Created new user: ID=%s, telegram_id=%s", user_id, telegram_id)
            return user_id
            
        except Exception as e:
            logger.error("Error in get_or_create_user: %s", e)
            return ""
    
    async def async_get_or_create_user(
        self, 
        telegram_id: int, 
        username: Optional[str] = None, 
        locale: str = "ru"
    ) -> str:
        """
        Async version of get_or_create_user.
        """
        await self._init_async()
        
        try:
            # First try to find existing user
            user = await self.async_service.get_user_by_telegram(telegram_id)
            if user:
                logger.debug("Found existing user: ID=%s", user["id"])
                return user["id"]
            
            # Create new user if not found
            user_id = await self.async_service.upsert_user_by_telegram(telegram_id, username, locale)
            logger.info("Created new user: ID=%s, telegram_id=%s", user_id, telegram_id)
            return user_id
            
        except Exception as e:
            logger.error("Error in async_get_or_create_user: %s", e)
            return ""
    
    # Subscription Management
    
    def add_subscription(self, user_id: str, category: str) -> bool:
        """
        Add subscription for user to category.
        
        Args:
            user_id: User ID
            category: News category
            
        Returns:
            True if subscription was added, False if already exists
        """
        try:
            result = self.sync_service.add_subscription(user_id, category)
            logger.info(
                "Subscription add result: user_id=%s, category=%s, added=%s",
                user_id, category, result
            )
            return result
            
        except Exception as e:
            logger.error("Error adding subscription: %s", e)
            return False
    
    async def async_add_subscription(self, user_id: str, category: str) -> bool:
        """
        Async version of add_subscription.
        """
        await self._init_async()
        
        try:
            result = await self.async_service.add_subscription(user_id, category)
            logger.info(
                "Subscription add result: user_id=%s, category=%s, added=%s",
                user_id, category, result
            )
            return result
            
        except Exception as e:
            logger.error("Error adding async subscription: %s", e)
            return False
    
    def remove_subscription(self, user_id: str, category: str) -> int:
        """
        Remove subscription for user from category.
        
        Args:
            user_id: User ID
            category: News category
            
        Returns:
            Number of subscriptions removed (0 or 1)
        """
        try:
            result = self.sync_service.remove_subscription(user_id, category)
            logger.info(
                "Subscription remove result: user_id=%s, category=%s, removed=%d",
                user_id, category, result
            )
            return result
            
        except Exception as e:
            logger.error("Error removing subscription: %s", e)
            return 0
    
    async def async_remove_subscription(self, user_id: str, category: str) -> int:
        """
        Async version of remove_subscription.
        """
        await self._init_async()
        
        try:
            result = await self.async_service.remove_subscription(user_id, category)
            logger.info(
                "Subscription remove result: user_id=%s, category=%s, removed=%d",
                user_id, category, result
            )
            return result
            
        except Exception as e:
            logger.error("Error removing async subscription: %s", e)
            return 0
    
    def list_subscriptions(self, user_id: str) -> List[Dict]:
        """
        Get list of user subscriptions.
        
        Args:
            user_id: User ID
            
        Returns:
            List of subscription dictionaries
        """
        try:
            subscriptions = self.sync_service.get_user_subscriptions(user_id)
            logger.debug("Retrieved %d subscriptions for user_id=%s", len(subscriptions), user_id)
            return subscriptions
            
        except Exception as e:
            logger.error("Error listing subscriptions: %s", e)
            return []
    
    async def async_list_subscriptions(self, user_id: str) -> List[Dict]:
        """
        Async version of list_subscriptions.
        """
        await self._init_async()
        
        try:
            subscriptions = await self.async_service.get_user_subscriptions(user_id)
            logger.debug("Retrieved %d subscriptions for user_id=%s", len(subscriptions), user_id)
            return subscriptions
            
        except Exception as e:
            logger.error("Error listing async subscriptions: %s", e)
            return []
    
    # Notification Management
    
    def upsert_notification(
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
            self.sync_service.upsert_notification(
                user_id, type_, frequency, enabled, preferred_hour
            )
            logger.info("Updated notification settings: user_id=%s, type=%s", user_id, type_)
            
        except Exception as e:
            logger.error("Error updating notification settings: %s", e)
    
    async def async_upsert_notification(
        self,
        user_id: int,
        type_: str = "digest",
        frequency: str = "daily",
        enabled: bool = True,
        preferred_hour: int = 9,
    ) -> None:
        """
        Async version of upsert_notification.
        """
        await self._init_async()
        
        try:
            await self.async_service.upsert_notification(
                user_id, type_, frequency, enabled, preferred_hour
            )
            logger.info("Updated async notification settings: user_id=%s, type=%s", user_id, type_)
            
        except Exception as e:
            logger.error("Error updating async notification settings: %s", e)
    
    def list_notifications(self, user_id: int) -> List[Dict]:
        """
        Get list of user notification settings.
        
        Args:
            user_id: User ID
            
        Returns:
            List of notification setting dictionaries
        """
        try:
            notifications = self.sync_service.get_users_by_notification_type("digest")
            user_notifications = [n for n in notifications if n.get("user_id") == user_id]
            logger.debug("Retrieved %d notifications for user_id=%s", len(user_notifications), user_id)
            return user_notifications
            
        except Exception as e:
            logger.error("Error listing notifications: %s", e)
            return []
    
    async def async_list_notifications(self, user_id: int) -> List[Dict]:
        """
        Async version of list_notifications.
        """
        await self._init_async()
        
        try:
            notifications = await self.async_service.get_users_by_notification_type("digest")
            user_notifications = [n for n in notifications if n.get("user_id") == user_id]
            logger.debug("Retrieved %d async notifications for user_id=%s", len(user_notifications), user_id)
            return user_notifications
            
        except Exception as e:
            logger.error("Error listing async notifications: %s", e)
            return []
    
    # Convenience Methods
    
    def upsert_digest_daily(self, user_id: str, preferred_hour: int = 9) -> None:
        """Set up daily digest notifications for user."""
        self.upsert_notification(user_id, "digest", "daily", True, preferred_hour)
    
    def upsert_events_daily(self, user_id: str, preferred_hour: int = 9) -> None:
        """Set up daily events notifications for user."""
        self.upsert_notification(user_id, "events", "daily", True, preferred_hour)
    
    def upsert_breaking_instant(self, user_id: str) -> None:
        """Set up instant breaking news notifications for user."""
        self.upsert_notification(user_id, "breaking", "instant", True, 0)
    
    async def async_upsert_digest_daily(self, user_id: str, preferred_hour: int = 9) -> None:
        """Async set up daily digest notifications for user."""
        await self.async_upsert_notification(user_id, "digest", "daily", True, preferred_hour)
    
    async def async_upsert_events_daily(self, user_id: str, preferred_hour: int = 9) -> None:
        """Async set up daily events notifications for user."""
        await self.async_upsert_notification(user_id, "events", "daily", True, preferred_hour)
    
    async def async_upsert_breaking_instant(self, user_id: str) -> None:
        """Async set up instant breaking news notifications for user."""
        await self.async_upsert_notification(user_id, "breaking", "instant", True, 0)


# Global service instances
_sync_user_service: Optional[UnifiedUserService] = None
_async_user_service: Optional[UnifiedUserService] = None


def get_sync_user_service() -> UnifiedUserService:
    """Get sync user service instance."""
    global _sync_user_service
    if _sync_user_service is None:
        _sync_user_service = UnifiedUserService(async_mode=False)
    return _sync_user_service


def get_async_user_service() -> UnifiedUserService:
    """Get async user service instance."""
    global _async_user_service
    if _async_user_service is None:
        _async_user_service = UnifiedUserService(async_mode=True)
    return _async_user_service


# Backward compatibility functions
def get_or_create_user(*args, **kwargs):
    """Backward compatibility function."""
    return get_sync_user_service().get_or_create_user(*args, **kwargs)


def add_subscription(*args, **kwargs):
    """Backward compatibility function."""
    return get_sync_user_service().add_subscription(*args, **kwargs)


def remove_subscription(*args, **kwargs):
    """Backward compatibility function."""
    return get_sync_user_service().remove_subscription(*args, **kwargs)


def list_subscriptions(*args, **kwargs):
    """Backward compatibility function."""
    return get_sync_user_service().list_subscriptions(*args, **kwargs)

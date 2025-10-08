"""
Subscription Service for PulseAI.

This module provides subscription management functionality for users.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone

from database.service import get_sync_service, get_async_service

logger = logging.getLogger("subscription_service")


class SubscriptionService:
    """Service for managing user subscriptions to categories and subcategories."""

    def __init__(self, async_mode: bool = False):
        """
        Initialize subscription service.

        Args:
            async_mode: If True, uses async database operations
        """
        self.async_mode = async_mode
        if async_mode:
            self.db_service = get_async_service()
        else:
            self.db_service = get_sync_service()

    async def get_user_subscriptions(self, user_id: int) -> Dict[str, List[str]]:
        """
        Get user's subscriptions to categories and subcategories.

        Args:
            user_id: Telegram user ID

        Returns:
            Dictionary with 'categories' and 'subcategories' lists
        """
        try:
            if self.async_mode:
                client = await self.db_service._get_async_client()
                result = await self.db_service.async_safe_execute(
                    client.table("subscriptions").select("category").eq("user_id", user_id)
                )
            else:
                result = self.db_service.safe_execute(self.db_service.sync_client.table(
                    "subscriptions").select("category").eq("user_id", user_id))

            subscriptions = result.data or []

            # Group by categories
            categories = set()

            for sub in subscriptions:
                if sub.get("category"):
                    categories.add(sub["category"])

            return {
                "categories": list(categories),
                "subcategories": [],  # Not implemented in current schema
            }

        except Exception as e:
            logger.error("❌ Error getting user subscriptions: %s", e)
            return {"categories": [], "subcategories": []}

    async def subscribe_to_category(self, user_id: int, category: str) -> bool:
        """
        Subscribe user to a category.

        Args:
            user_id: Telegram user ID
            category: Category name

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.async_mode:
                client = await self.db_service._get_async_client()
                await self.db_service.async_safe_execute(
                    client.table("subscriptions").upsert(
                        {
                            "user_id": user_id,
                            "category": category,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        },
                        on_conflict="user_id,category",
                    )
                )
            else:
                self.db_service.safe_execute(
                    self.db_service.sync_client.table("subscriptions").upsert(
                        {
                            "user_id": user_id,
                            "category": category,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        },
                        on_conflict="user_id,category",
                    )
                )

            logger.info("✅ User %d subscribed to category %s", user_id, category)
            return True

        except Exception as e:
            logger.error("❌ Error subscribing to category: %s", e)
            return False

    async def subscribe_to_subcategory(self, user_id: int, category: str, subcategory: str) -> bool:
        """
        Subscribe user to a subcategory.

        Args:
            user_id: Telegram user ID
            category: Category name
            subcategory: Subcategory name

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.async_mode:
                client = await self.db_service._get_async_client()
                await self.db_service.async_safe_execute(
                    client.table("user_subscriptions").upsert(
                        {
                            "user_id": user_id,
                            "category": category,
                            "subcategory": subcategory,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        },
                        on_conflict="user_id,category,subcategory",
                    )
                )
            else:
                self.db_service.safe_execute(
                    self.db_service.sync_client.table("user_subscriptions").upsert(
                        {
                            "user_id": user_id,
                            "category": category,
                            "subcategory": subcategory,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        },
                        on_conflict="user_id,category,subcategory",
                    )
                )

            logger.info("✅ User %d subscribed to subcategory %s/%s", user_id, category, subcategory)
            return True

        except Exception as e:
            logger.error("❌ Error subscribing to subcategory: %s", e)
            return False

    async def unsubscribe_from_category(self, user_id: int, category: str) -> bool:
        """
        Unsubscribe user from a category.

        Args:
            user_id: Telegram user ID
            category: Category name

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.async_mode:
                client = await self.db_service._get_async_client()
                await self.db_service.async_safe_execute(
                    client.table("subscriptions").delete().eq("user_id", user_id).eq("category", category)
                )
            else:
                self.db_service.safe_execute(
                    self.db_service.sync_client.table("subscriptions")
                    .delete()
                    .eq("user_id", user_id)
                    .eq("category", category)
                )

            logger.info("✅ User %d unsubscribed from category %s", user_id, category)
            return True

        except Exception as e:
            logger.error("❌ Error unsubscribing from category: %s", e)
            return False

    async def unsubscribe_from_subcategory(
            self,
            user_id: int,
            category: str,
            subcategory: str) -> bool:
        """
        Unsubscribe user from a subcategory.

        Args:
            user_id: Telegram user ID
            category: Category name
            subcategory: Subcategory name

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.async_mode:
                client = await self.db_service._get_async_client()
                await self.db_service.async_safe_execute(
                    client.table("user_subscriptions")
                    .delete()
                    .eq("user_id", user_id)
                    .eq("category", category)
                    .eq("subcategory", subcategory)
                )
            else:
                self.db_service.safe_execute(
                    self.db_service.sync_client.table("user_subscriptions")
                    .delete()
                    .eq("user_id", user_id)
                    .eq("category", category)
                    .eq("subcategory", subcategory)
                )

            logger.info(
                "✅ User %d unsubscribed from subcategory %s/%s",
                user_id,
                category,
                subcategory)
            return True

        except Exception as e:
            logger.error("❌ Error unsubscribing from subcategory: %s", e)
            return False

    async def is_subscribed(self, user_id: int, category: str,
                            subcategory: Optional[str] = None) -> bool:
        """
        Check if user is subscribed to category or subcategory.

        Args:
            user_id: Telegram user ID
            category: Category name
            subcategory: Optional subcategory name

        Returns:
            True if subscribed, False otherwise
        """
        try:
            if self.async_mode:
                client = await self.db_service._get_async_client()
                query = client.table("subscriptions").select("id").eq(
                    "user_id", user_id).eq("category", category)

                result = await self.db_service.async_safe_execute(query)
            else:
                query = (
                    self.db_service.sync_client.table("subscriptions")
                    .select("id")
                    .eq("user_id", user_id)
                    .eq("category", category)
                )

                result = self.db_service.safe_execute(query)

            return len(result.data or []) > 0

        except Exception as e:
            logger.error("❌ Error checking subscription: %s", e)
            return False


# Global service instances
_sync_subscription_service: Optional[SubscriptionService] = None
_async_subscription_service: Optional[SubscriptionService] = None


def get_sync_subscription_service() -> SubscriptionService:
    """Get or create sync subscription service instance."""
    global _sync_subscription_service
    if _sync_subscription_service is None:
        _sync_subscription_service = SubscriptionService(async_mode=False)
    return _sync_subscription_service


def get_async_subscription_service() -> SubscriptionService:
    """Get or create async subscription service instance."""
    global _async_subscription_service
    if _async_subscription_service is None:
        _async_subscription_service = SubscriptionService(async_mode=True)
    return _async_subscription_service


# Backward compatibility functions
async def subscribe_to_category(user_id: int, category: str) -> bool:
    """Backward compatibility function for subscribing to category."""
    service = get_async_subscription_service()
    return await service.subscribe_to_category(user_id, category)


async def get_user_subscriptions(user_id: int) -> Dict[str, List[str]]:
    """Backward compatibility function for getting user subscriptions."""
    service = get_async_subscription_service()
    return await service.get_user_subscriptions(user_id)

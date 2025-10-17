"""
Notification Service for PulseAI.

This service handles user notifications for important events via Telegram and WebApp.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone

logger = logging.getLogger("notification_service")


class NotificationService:
    """
    Full-featured notification system for PulseAI.

    Features:
    - User preference management
    - Smart event filtering
    - Daily digest preparation
    - Telegram and WebApp notifications
    - Notification rate limiting (max 3/day per user)
    """

    def __init__(self):
        """Initialize notification service."""
        self.max_notifications_per_day = 3
        logger.info("NotificationService initialized")

    async def prepare_daily_digest(self, user_id: int) -> Dict:
        """
        Prepare daily digest for user based on preferences.

        Args:
            user_id: Telegram user ID

        Returns:
            Dictionary with events and metadata
        """
        try:

            # Get user preferences
            prefs = await self.get_user_preferences(user_id)
            if not prefs:
                logger.info(f"No preferences found for user {user_id}, using defaults")
                return {"events": [], "count": 0}

            # Get events matching preferences
            events = await self._get_matching_events(user_id, prefs)

            # Group by importance
            high_importance = [e for e in events if e.get("importance_score", 0) >= 0.8]
            medium_importance = [e for e in events if 0.6 <= e.get("importance_score", 0) < 0.8]

            logger.info(
                f"Prepared digest for user {user_id}: "
                f"{len(high_importance)} high, {len(medium_importance)} medium importance events"
            )

            return {
                "events": events,
                "high_importance": high_importance,
                "medium_importance": medium_importance,
                "count": len(events),
                "user_id": user_id,
                "prepared_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error preparing daily digest for user {user_id}: {e}")
            return {"events": [], "count": 0, "error": str(e)}

    async def send_telegram_notification(self, user_id: int, events: List[Dict]) -> bool:
        """
        Send notification via Telegram bot.

        Args:
            user_id: Telegram user ID
            events: List of events to notify about

        Returns:
            True if notification sent successfully
        """
        try:
            # Check notification rate limit
            if not await self._can_send_notification(user_id):
                logger.warning(f"Notification rate limit reached for user {user_id}")
                return False

            # Format notification message
            message = self._format_telegram_message(events)  # noqa: F841

            # TODO: Send via Telegram bot
            # This will be integrated with telegram_bot/ in notifications/telegram_sender.py
            logger.info(f"Would send Telegram notification to user {user_id} about {len(events)} events")

            # Record notification
            await self._record_notification(user_id, "telegram", len(events))

            return True

        except Exception as e:
            logger.error(f"Error sending Telegram notification to user {user_id}: {e}")
            return False

    async def push_webapp_notification(self, user_id: int, events: List[Dict]) -> bool:
        """
        Push notification to WebApp via SSE.

        Args:
            user_id: Telegram user ID
            events: List of events to notify about

        Returns:
            True if notification pushed successfully
        """
        try:
            # Check notification rate limit
            if not await self._can_send_notification(user_id):
                logger.warning(f"Notification rate limit reached for user {user_id}")
                return False

            # Format notification data
            notification_data = {  # noqa: F841
                "type": "event_notification",
                "events": events,
                "count": len(events),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # TODO: Push via SSE stream
            # This will be integrated with services/events_stream.py
            logger.info(f"Would push WebApp notification to user {user_id} about {len(events)} events")

            # Record notification
            await self._record_notification(user_id, "webapp", len(events))

            return True

        except Exception as e:
            logger.error(f"Error pushing WebApp notification to user {user_id}: {e}")
            return False

    async def get_user_preferences(self, user_id: int) -> Optional[Dict]:
        """
        Get user notification preferences from database.

        Args:
            user_id: Telegram user ID

        Returns:
            User preferences dictionary or None
        """
        try:
            from database.db_models import supabase

            if not supabase:
                logger.error("Supabase not initialized")
                return None

            result = supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()

            if result.data and len(result.data) > 0:
                logger.debug(f"Found preferences for user {user_id}")
                return result.data[0]

            logger.debug(f"No preferences found for user {user_id}")
            return None

        except Exception as e:
            logger.error(f"Error getting user preferences for {user_id}: {e}")
            return None

    async def update_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        """
        Update user notification preferences in database.

        Args:
            user_id: Telegram user ID
            preferences: New preferences dictionary

        Returns:
            True if updated successfully
        """
        try:
            from database.db_models import supabase

            if not supabase:
                logger.error("Supabase not initialized")
                return False

            # Prepare preferences data
            prefs_data = {
                "user_id": user_id,
                "categories": preferences.get("categories", []),
                "min_importance": preferences.get("min_importance", 0.6),
                "delivery_method": preferences.get("delivery_method", "bot"),
                "notification_frequency": preferences.get("notification_frequency", "daily"),
                "max_notifications_per_day": preferences.get("max_notifications_per_day", 3),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            # Upsert preferences
            result = supabase.table("user_preferences").upsert(prefs_data, on_conflict="user_id").execute()

            success = len(result.data) > 0 if result.data else False
            if success:
                logger.info(f"Updated preferences for user {user_id}")
            return success

        except Exception as e:
            logger.error(f"Error updating user preferences for {user_id}: {e}")
            return False

    async def _get_matching_events(self, user_id: int, prefs: Dict) -> List[Dict]:
        """
        Get events matching user preferences.

        Args:
            user_id: Telegram user ID
            prefs: User preferences dictionary

        Returns:
            List of matching events
        """
        try:
            from database.db_models import supabase

            if not supabase:
                logger.error("Supabase not initialized")
                return []

            # Build query
            query = supabase.table("events_new").select(
                "id, title, category, subcategory, starts_at, importance, description, link"
            )

            # Filter by categories
            categories = prefs.get("categories", [])
            if categories and len(categories) > 0:
                query = query.in_("category", categories)

            # Filter by importance
            min_importance = prefs.get("min_importance", 0.6)
            query = query.gte("importance_score", min_importance)

            # Only upcoming events
            query = query.eq("status", "upcoming")

            # Only events starting within next 7 days
            now = datetime.now(timezone.utc)
            end_date = now + timedelta(days=7)
            query = query.gte("starts_at", now.isoformat())
            query = query.lte("starts_at", end_date.isoformat())

            # Add limit to prevent loading too many events
            query = query.limit(50)

            # Execute query
            result = query.execute()

            events = result.data or []
            logger.debug(f"Found {len(events)} matching events for user {user_id}")

            return events

        except Exception as e:
            logger.error(f"Error getting matching events for user {user_id}: {e}")
            return []

    async def _can_send_notification(self, user_id: int) -> bool:
        """
        Check if notification can be sent (rate limit).

        Args:
            user_id: Telegram user ID

        Returns:
            True if notification can be sent
        """
        try:
            from database.db_models import supabase

            if not supabase:
                return True  # Allow if DB not available

            # Get user preferences for max notifications
            prefs = await self.get_user_preferences(user_id)
            max_per_day = prefs.get("max_notifications_per_day", 3) if prefs else 3

            # Count notifications sent today
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

            result = (
                supabase.table("event_logs")
                .select("id", count="exact")
                .eq("user_id", user_id)
                .eq("action", "notified")
                .gte("created_at", today_start.isoformat())
                .execute()
            )

            count = result.count if hasattr(result, "count") else 0

            can_send = count < max_per_day
            logger.debug(f"User {user_id} notifications today: {count}/{max_per_day}, can_send: {can_send}")

            return can_send

        except Exception as e:
            logger.error(f"Error checking notification rate limit for user {user_id}: {e}")
            return True  # Allow on error

    async def _record_notification(self, user_id: int, method: str, events_count: int):
        """
        Record notification in event_logs.

        Args:
            user_id: Telegram user ID
            method: Notification method (telegram/webapp)
            events_count: Number of events notified about
        """
        try:
            from database.db_models import supabase

            if not supabase:
                return

            # Update last_notified_at in user_preferences
            await supabase.table("user_preferences").update(
                {"last_notified_at": datetime.now(timezone.utc).isoformat()}
            ).eq("user_id", user_id).execute()

            logger.debug(f"Recorded notification for user {user_id} via {method}: {events_count} events")

        except Exception as e:
            logger.error(f"Error recording notification for user {user_id}: {e}")

    def _format_telegram_message(self, events: List[Dict]) -> str:
        """
        Format events as Telegram message.

        Args:
            events: List of events

        Returns:
            Formatted message string
        """
        if not events:
            return "📅 Нет важных событий на ближайшее время."

        lines = ["📅 *Важные события:*\n"]

        for event in events[:5]:  # Limit to 5 events
            category_emoji = self._get_category_emoji(event.get("category", "unknown"))
            title = event.get("title", "Без названия")
            importance = event.get("importance_score", 0)
            starts_at = event.get("starts_at", "")

            # Format date
            try:
                date_obj = datetime.fromisoformat(starts_at.replace("Z", "+00:00"))
                date_str = date_obj.strftime("%d.%m %H:%M")
            except Exception:
                date_str = starts_at

            lines.append(f"{category_emoji} *{title}*")
            lines.append(f"   📊 Важность: {importance:.0%} | 📅 {date_str}\n")

        if len(events) > 5:
            lines.append(f"\n_И ещё {len(events) - 5} событий..._")

        return "\n".join(lines)

    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for category."""
        emojis = {
            "crypto": "🪙",
            "markets": "📈",
            "sports": "🏀",
            "tech": "💻",
            "world": "🌍",
        }
        return emojis.get(category, "📅")


# Global service instance
_notification_service_instance: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """Get global notification service instance."""
    global _notification_service_instance
    if _notification_service_instance is None:
        _notification_service_instance = NotificationService()
    return _notification_service_instance


__all__ = ["NotificationService", "get_notification_service"]

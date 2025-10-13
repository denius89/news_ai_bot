"""
Telegram Sender for PulseAI Notifications.

This module handles sending notifications via Telegram bot.
"""

import logging
from typing import Dict, List, Optional
import asyncio  # noqa: F401

logger = logging.getLogger("telegram_sender")


class TelegramSender:
    """
    Handles sending notifications via Telegram bot.

    Features:
    - Send formatted event notifications
    - Support for rich formatting (Markdown)
    - Integration with existing telegram_bot/
    - Async sending with error handling
    """

    def __init__(self):
        """Initialize Telegram sender."""
        self.bot = None
        self._initialize_bot()
        logger.info("TelegramSender initialized")

    def _initialize_bot(self):
        """Initialize Telegram bot instance."""
        try:
            # Try to import existing bot instance
            from telegram_bot.bot import get_bot_instance

            self.bot = get_bot_instance()
            logger.info("Connected to existing Telegram bot instance")
        except Exception as e:
            logger.warning(f"Could not connect to Telegram bot: {e}")
            self.bot = None

    async def send_notification(self, user_id: int, message: str, parse_mode: str = "Markdown") -> bool:
        """
        Send notification message to user via Telegram.

        Args:
            user_id: Telegram user ID
            message: Message text
            parse_mode: Parse mode (Markdown or HTML)

        Returns:
            True if sent successfully
        """
        try:
            if not self.bot:
                logger.error("Telegram bot not initialized")
                return False

            # Send message via bot
            await self.bot.send_message(chat_id=user_id, text=message, parse_mode=parse_mode)

            logger.info(f"Sent Telegram notification to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error sending Telegram notification to user {user_id}: {e}")
            return False

    async def send_event_notification(self, user_id: int, events: List[Dict]) -> bool:
        """
        Send formatted event notification to user.

        Args:
            user_id: Telegram user ID
            events: List of events to notify about

        Returns:
            True if sent successfully
        """
        try:
            if not events:
                logger.debug(f"No events to notify user {user_id}")
                return False

            # Format message
            message = self._format_event_message(events)

            # Send via Telegram
            return await self.send_notification(user_id, message)

        except Exception as e:
            logger.error(f"Error sending event notification to user {user_id}: {e}")
            return False

    async def send_daily_digest(self, user_id: int, digest_data: Dict) -> bool:
        """
        Send daily digest to user.

        Args:
            user_id: Telegram user ID
            digest_data: Digest data from NotificationService

        Returns:
            True if sent successfully
        """
        try:
            events = digest_data.get("events", [])
            high_importance = digest_data.get("high_importance", [])

            if not events:
                logger.debug(f"No events in digest for user {user_id}")
                return False

            # Format digest message
            message = self._format_digest_message(events, high_importance)

            # Send via Telegram
            return await self.send_notification(user_id, message)

        except Exception as e:
            logger.error(f"Error sending daily digest to user {user_id}: {e}")
            return False

    def _format_event_message(self, events: List[Dict]) -> str:
        """
        Format events as Telegram message.

        Args:
            events: List of events

        Returns:
            Formatted message string
        """
        if not events:
            return "📅 Нет важных событий на ближайшее время."

        lines = ["🔔 *Важные события:*\n"]

        for event in events[:5]:  # Limit to 5 events
            category_emoji = self._get_category_emoji(event.get("category", "unknown"))
            title = event.get("title", "Без названия")
            importance = event.get("importance_score", 0)
            starts_at = event.get("starts_at", "")

            # Format date
            try:
                from datetime import datetime

                date_obj = datetime.fromisoformat(starts_at.replace("Z", "+00:00"))
                date_str = date_obj.strftime("%d.%m %H:%M")
            except Exception:
                date_str = starts_at

            lines.append(f"{category_emoji} *{title}*")
            lines.append(f"   📊 Важность: {int(importance * 100)}% | 📅 {date_str}")

            # Add link if available
            link = event.get("link")
            if link:
                lines.append(f"   🔗 [Подробнее]({link})")

            lines.append("")  # Empty line

        if len(events) > 5:
            lines.append(f"_И ещё {len(events) - 5} событий..._")

        return "\n".join(lines)

    def _format_digest_message(self, events: List[Dict], high_importance: List[Dict]) -> str:
        """
        Format daily digest message.

        Args:
            events: All events
            high_importance: High importance events

        Returns:
            Formatted digest message
        """
        lines = ["📅 *Дайджест событий на сегодня*\n"]

        if high_importance:
            lines.append("🔥 *Особо важные события:*\n")
            for event in high_importance[:3]:
                category_emoji = self._get_category_emoji(event.get("category", "unknown"))
                title = event.get("title", "Без названия")
                lines.append(f"{category_emoji} {title}")
            lines.append("")

        lines.append(f"📊 Всего событий: {len(events)}")
        lines.append(f"🔥 Высокой важности: {len(high_importance)}")

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


# Global instance
_telegram_sender_instance: Optional[TelegramSender] = None


def get_telegram_sender() -> TelegramSender:
    """Get global Telegram sender instance."""
    global _telegram_sender_instance
    if _telegram_sender_instance is None:
        _telegram_sender_instance = TelegramSender()
    return _telegram_sender_instance


__all__ = ["TelegramSender", "get_telegram_sender"]

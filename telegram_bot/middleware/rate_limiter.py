"""
Rate limiting middleware for Telegram bot.

Protects against spam and abuse with configurable rate limits.
"""

import logging
import json
import time
from typing import Any, Awaitable, Callable, Dict, Optional
from datetime import datetime
from collections import defaultdict, deque

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update

from telegram_bot.utils.error_messages import ERROR_MESSAGES

logger = logging.getLogger("telegram_bot.rate_limiter")


class RateLimiterMiddleware(BaseMiddleware):
    """
    Rate limiting middleware.

    Provides protection against:
    - Spam commands
    - Excessive AI digest generation
    - Subscription abuse
    - General rate limiting
    """

    def __init__(self):
        super().__init__()

        # Rate limit configurations (only commands for minimalist bot)
        self.rate_limits = {
            "commands": {"limit": 5, "window": 60},  # 5 per minute
        }

        # User tracking: {user_id: {action: deque(timestamps)}}
        self.user_actions: Dict[int, Dict[str, deque]] = defaultdict(lambda: defaultdict(lambda: deque()))

        # Cleanup interval (remove old entries)
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes

    async def __call__(
        self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]], event: Update, data: Dict[str, Any]
    ) -> Any:
        """
        Process update with rate limiting.

        Args:
            handler: Next handler in chain
            event: Telegram update
            data: Handler data

        Returns:
            Handler result or None if rate limited
        """
        # Extract user ID
        user_id = self._get_user_id(event)
        if not user_id:
            return await handler(event, data)

        # Determine action type
        action_type = self._get_action_type(event)
        if not action_type:
            return await handler(event, data)

        # Check rate limit
        if not self._check_rate_limit(user_id, action_type):
            await self._handle_rate_limit(event, action_type)
            return None

        # Record action
        self._record_action(user_id, action_type)

        # Cleanup old entries periodically
        await self._cleanup_if_needed()

        # Call next handler
        return await handler(event, data)

    def _get_user_id(self, event: Update) -> Optional[int]:
        """Extract user ID from update."""
        if isinstance(event, Message):
            return event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            return event.from_user.id if event.from_user else None
        return None

    def _get_action_type(self, event: Update) -> Optional[str]:
        """Determine action type for rate limiting."""
        if isinstance(event, Message):
            return "commands"
        elif isinstance(event, CallbackQuery):
            return "commands"
        return None

    def _check_rate_limit(self, user_id: int, action_type: str) -> bool:
        """
        Check if user has exceeded rate limit for action type.

        Args:
            user_id: User ID
            action_type: Type of action

        Returns:
            True if within limits, False if exceeded
        """
        if action_type not in self.rate_limits:
            return True

        limit_config = self.rate_limits[action_type]
        limit = limit_config["limit"]
        window = limit_config["window"]

        now = time.time()
        user_actions = self.user_actions[user_id][action_type]

        # Remove old timestamps outside the window
        while user_actions and user_actions[0] < now - window:
            user_actions.popleft()

        # Check if limit exceeded
        if len(user_actions) >= limit:
            logger.warning(
                json.dumps(
                    {
                        "event": "rate_limit_exceeded",
                        "user_id": user_id,
                        "action_type": action_type,
                        "current_count": len(user_actions),
                        "limit": limit,
                        "window": window,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            )
            return False

        return True

    def _record_action(self, user_id: int, action_type: str):
        """Record user action timestamp."""
        now = time.time()
        self.user_actions[user_id][action_type].append(now)

    async def _handle_rate_limit(self, event: Update, action_type: str):
        """Handle rate limit exceeded."""
        limit_config = self.rate_limits[action_type]
        window = limit_config["window"]

        # Calculate remaining time
        user_id = self._get_user_id(event)
        if user_id:
            user_actions = self.user_actions[user_id][action_type]
            if user_actions:
                oldest_action = user_actions[0]
                remaining_time = int(window - (time.time() - oldest_action))
                remaining_time = max(0, remaining_time)
            else:
                remaining_time = 0
        else:
            remaining_time = window

        # Send error message
        message = ERROR_MESSAGES["rate_limit"].format(seconds=remaining_time)

        try:
            if isinstance(event, Message):
                await event.answer(message, parse_mode="HTML")
            elif isinstance(event, CallbackQuery):
                await event.answer(message, show_alert=True)
        except Exception as e:
            logger.error(f"Failed to send rate limit message: {e}")

    async def _cleanup_if_needed(self):
        """Clean up old entries to prevent memory leaks."""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return

        self.last_cleanup = now

        # Remove users with no recent activity
        max_window = max(config["window"] for config in self.rate_limits.values())
        cutoff_time = now - max_window - 3600  # Extra hour buffer

        users_to_remove = []
        for user_id, actions in self.user_actions.items():
            has_recent_activity = False
            for action_type, timestamps in actions.items():
                # Remove old timestamps
                while timestamps and timestamps[0] < cutoff_time:
                    timestamps.popleft()

                if timestamps:
                    has_recent_activity = True

            if not has_recent_activity:
                users_to_remove.append(user_id)

        for user_id in users_to_remove:
            del self.user_actions[user_id]

        logger.debug(f"Rate limiter cleanup: removed {len(users_to_remove)} inactive users")

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get rate limiting stats for user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with user stats
        """
        stats = {}
        now = time.time()

        for action_type, limit_config in self.rate_limits.items():
            user_actions = self.user_actions[user_id][action_type]
            window = limit_config["window"]

            # Count actions in current window
            count = sum(1 for timestamp in user_actions if timestamp > now - window)

            stats[action_type] = {
                "current_count": count,
                "limit": limit_config["limit"],
                "window": window,
                "remaining": max(0, limit_config["limit"] - count),
            }

        return stats

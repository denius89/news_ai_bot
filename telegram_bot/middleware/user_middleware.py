"""
User middleware for automatic user creation and management.

Handles user authentication, creation, and logging for all bot interactions.
Uses webapp pattern: normalize names, create via db_models, always pass telegram_id.
"""

import logging
import json
from typing import Any, Awaitable, Callable, Dict, Optional
from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update

from utils.text.name_normalizer import normalize_user_name
from database.db_models import create_user, get_user_by_telegram

logger = logging.getLogger("telegram_bot.user_middleware")


class UserMiddleware(BaseMiddleware):
    """
    User management middleware.

    Automatically handles:
    - User creation/retrieval from database
    - User ID injection into handler data
    - User action logging
    - User preferences caching
    """

    def __init__(self):
        super().__init__()

    async def __call__(
        self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]], event: Update, data: Dict[str, Any]
    ) -> Any:
        """
        Process update with user management using webapp pattern.

        Args:
            handler: Next handler in chain
            event: Telegram update
            data: Handler data

        Returns:
            Handler result
        """
        # Extract user info from update
        user_info = self._extract_user_info(event)
        if not user_info:
            logger.warning("No user info found in update")
            return await handler(event, data)

        # Skip bot users (they don't need DB records)
        if user_info.get("is_bot", False):
            logger.debug(f"Skipping bot user: {user_info.get('username', 'unknown')}")
            return await handler(event, data)

        # Extract telegram_id (always present in Telegram updates)
        telegram_id = user_info["telegram_id"]

        # 1. Normalize user name (webapp pattern)
        normalized_name = normalize_user_name(
            raw_name=user_info.get("first_name"), username=user_info.get("username"), user_id=telegram_id
        )

        # 2. ВАЖНО: telegram_id всегда передаем в обработчики
        data["user_id"] = telegram_id
        data["user_info"] = {**user_info, "display_name": normalized_name}

        # 3. Try to create/get user in DB (non-blocking)
        try:
            # Check if user exists
            existing_user = get_user_by_telegram(telegram_id)

            if existing_user:
                data["db_user_id"] = existing_user["id"]
                logger.debug(f"Found existing user: {telegram_id} -> {existing_user['id']}")
            else:
                # Create new user with normalized name
                new_user_id = create_user(
                    telegram_id=telegram_id,
                    username=user_info.get("username"),
                    locale=user_info.get("language_code", "ru"),
                    first_name=normalized_name,  # Use normalized name
                )
                if new_user_id:
                    data["db_user_id"] = new_user_id
                    logger.info(f"Created new user: {telegram_id} -> {new_user_id}")
                else:
                    logger.warning(f"Could not create DB record for user {telegram_id}, but continuing")
        except Exception as e:
            logger.error(f"Error creating DB user for {telegram_id}: {e}, but continuing")

        # Log user action
        await self._log_user_action(event, telegram_id, user_info)

        # Call next handler
        return await handler(event, data)

    def _extract_user_info(self, event: Update) -> Optional[Dict[str, Any]]:
        """Extract user information from update."""
        user = None

        if hasattr(event, "message") and event.message:
            user = event.message.from_user
        elif hasattr(event, "callback_query") and event.callback_query:
            user = event.callback_query.from_user

        if not user:
            return None

        return {
            "telegram_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "language_code": user.language_code,
            "is_bot": user.is_bot,
        }

    async def _log_user_action(self, event: Update, user_id: int, user_info: Dict[str, Any]):
        """
        Log user action for analytics.

        Args:
            event: Telegram update
            user_id: Telegram user ID
            user_info: User information
        """
        try:
            action_data = {
                "event": "user_action",
                "user_id": user_id,
                "telegram_id": user_info["telegram_id"],
                "username": user_info["username"],
                "display_name": user_info.get("display_name", "unknown"),
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Add action-specific data
            if isinstance(event, Message):
                action_data.update(
                    {
                        "action_type": "message",
                        "command": event.text.split()[0] if event.text else None,
                        "chat_type": event.chat.type if event.chat else None,
                    }
                )
            elif isinstance(event, CallbackQuery):
                action_data.update(
                    {
                        "action_type": "callback",
                        "callback_data": event.data,
                    }
                )

            logger.info(json.dumps(action_data))

        except Exception as e:
            logger.error(f"Failed to log user action: {e}")

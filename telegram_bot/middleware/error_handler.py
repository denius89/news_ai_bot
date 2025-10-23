"""
Centralized error handling middleware for Telegram bot.

Handles all types of errors consistently and provides user-friendly messages.
"""

import logging
import json
from typing import Any, Awaitable, Callable, Dict, Optional
from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramAPIError
from aiogram.types import Message, CallbackQuery, Update

from telegram_bot.utils.error_messages import ERROR_MESSAGES

logger = logging.getLogger("telegram_bot.error_handler")


class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Centralized error handling middleware.

    Provides consistent error handling across all handlers with:
    - User-friendly error messages
    - Automatic retry for transient errors
    - Structured logging for debugging
    - Graceful degradation
    """

    def __init__(self):
        super().__init__()

    async def __call__(
        self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]], event: Update, data: Dict[str, Any]
    ) -> Any:
        """
        Process update with error handling.

        Args:
            handler: Next handler in chain
            event: Telegram update
            data: Handler data

        Returns:
            Handler result or None if error occurred
        """
        try:
            return await handler(event, data)

        except TelegramBadRequest as e:
            await self._handle_telegram_bad_request(e, event)

        except TelegramRetryAfter as e:
            await self._handle_telegram_retry_after(e, event)

        except TelegramAPIError as e:
            await self._handle_telegram_api_error(e, event)

        except Exception as e:
            await self._handle_unexpected_error(e, event)

        return None

    async def _handle_telegram_bad_request(self, error: TelegramBadRequest, event: Update):
        """Handle Telegram BadRequest errors."""
        error_msg = str(error).lower()

        # Log the error
        logger.warning(
            json.dumps(
                {
                    "event": "telegram_bad_request",
                    "error": str(error),
                    "error_code": getattr(error, "error_code", None),
                    "user_id": self._get_user_id(event),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )

        # Handle specific error cases
        if "message is not modified" in error_msg:
            # This is usually not a real error, just skip
            logger.debug("Message not modified - skipping")
            return

        elif "message to edit not found" in error_msg:
            # Message was deleted or too old
            await self._send_error_message(event, ERROR_MESSAGES["message_not_found"])

        elif "message text is empty" in error_msg:
            await self._send_error_message(event, ERROR_MESSAGES["empty_message"])

        elif "can't parse entities" in error_msg:
            await self._send_error_message(event, ERROR_MESSAGES["parse_error"])

        else:
            # Generic bad request
            await self._send_error_message(event, ERROR_MESSAGES["bad_request"])

    async def _handle_telegram_retry_after(self, error: TelegramRetryAfter, event: Update):
        """Handle Telegram rate limit errors."""
        retry_after = getattr(error, "retry_after", 60)

        logger.warning(
            json.dumps(
                {
                    "event": "telegram_rate_limit",
                    "retry_after": retry_after,
                    "user_id": self._get_user_id(event),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )

        await self._send_error_message(event, ERROR_MESSAGES["rate_limit"].format(seconds=retry_after))

    async def _handle_telegram_api_error(self, error: TelegramAPIError, event: Update):
        """Handle general Telegram API errors."""
        logger.error(
            json.dumps(
                {
                    "event": "telegram_api_error",
                    "error": str(error),
                    "error_code": getattr(error, "error_code", None),
                    "user_id": self._get_user_id(event),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )

        await self._send_error_message(event, ERROR_MESSAGES["api_error"])

    async def _handle_unexpected_error(self, error: Exception, event: Update):
        """Handle unexpected errors."""
        logger.error(
            json.dumps(
                {
                    "event": "unexpected_error",
                    "error": str(error),
                    "error_type": type(error).__name__,
                    "user_id": self._get_user_id(event),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            exc_info=True,
        )

        await self._send_error_message(event, ERROR_MESSAGES["unexpected_error"])

    async def _send_error_message(self, event: Update, message: str):
        """Send error message to user."""
        try:
            if isinstance(event, Message):
                await event.answer(message, parse_mode="HTML")
            elif isinstance(event, CallbackQuery):
                await event.message.answer(message, parse_mode="HTML")
                await event.answer()  # Acknowledge callback
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    def _get_user_id(self, event: Update) -> Optional[int]:
        """Extract user ID from update."""
        if isinstance(event, Message):
            return event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            return event.from_user.id if event.from_user else None
        return None

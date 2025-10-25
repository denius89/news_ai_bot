"""
Review Handler for Human-in-the-loop Content Review.

This module handles preview and approval workflow for digest posts,
allowing admins to review content before publication.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass

import yaml
from pathlib import Path

from aiogram import Bot  # noqa: F401
from aiogram.filters import Command  # noqa: F401
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter  # noqa: F401

from ai_modules.metrics import get_metrics

logger = logging.getLogger("review_handler")


@dataclass
class ReviewRequest:
    """Represents a pending review request."""

    digest_id: int
    message_text: str
    digest_data: Dict[str, Any]
    created_at: datetime
    expires_at: datetime
    admin_message_id: Optional[int] = None
    status: str = "pending"  # pending, approved, rejected, expired


class ReviewHandler:
    """
    Handles human-in-the-loop review process for digest posts.

    Features:
    - Preview posts to admin
    - Inline approval/rejection buttons
    - Auto-publish timeout
    - Review tracking and metrics
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize review handler with configuration."""
        self.config = self._load_config(config_path)
        self.metrics = get_metrics()

        # Configuration
        self.smart_posting_config = self.config.get("smart_posting", {})
        self.review_config = self.config.get("review_mode", {})

        self.enabled = self.smart_posting_config.get("review_mode", False)
        self.admin_id = self.review_config.get("admin_id")
        self.auto_post_timeout_min = self.review_config.get("auto_post_timeout_min", 10)

        # Bot instance
        self.bot = None

        # Pending reviews
        self.pending_reviews: Dict[int, ReviewRequest] = {}

        # Callback handlers
        self.approval_callback: Optional[Callable] = None
        self.rejection_callback: Optional[Callable] = None

        logger.info(f"ReviewHandler initialized: enabled={self.enabled}, admin_id={self.admin_id}")

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "ai_optimization.yaml"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def set_bot(self, bot: Bot) -> None:
        """Set bot instance for sending messages."""
        self.bot = bot

    def set_callbacks(self, approval_callback: Callable, rejection_callback: Callable) -> None:
        """Set callback functions for approval and rejection."""
        self.approval_callback = approval_callback
        self.rejection_callback = rejection_callback

    async def request_review(self, digest_data: Dict[str, Any], message_text: str) -> bool:
        """
        Request review for a digest post.

        Args:
            digest_data: Digest data dictionary
            message_text: Formatted message text to review

        Returns:
            True if review was requested successfully, False otherwise
        """
        try:
            if not self.enabled or not self.admin_id or not self.bot:
                logger.debug("Review mode disabled or not configured")
                return False

            digest_id = digest_data.get("id")
            if not digest_id:
                logger.error("No digest ID provided for review")
                return False

            # Create review request
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(minutes=self.auto_post_timeout_min)

            review_request = ReviewRequest(
                digest_id=digest_id,
                message_text=message_text,
                digest_data=digest_data,
                created_at=now,
                expires_at=expires_at,
            )

            # Store pending review
            self.pending_reviews[digest_id] = review_request

            # Send preview to admin
            await self._send_preview_to_admin(review_request)

            # Start auto-approval timer
            asyncio.create_task(self._auto_approve_timer(digest_id))

            logger.info(f"Review requested for digest {digest_id}, expires at {expires_at}")
            return True

        except Exception as e:
            logger.error(f"Error requesting review: {e}")
            return False

    async def _send_preview_to_admin(self, review_request: ReviewRequest) -> None:
        """Send preview message to admin with approval buttons."""
        try:
            # Create inline keyboard
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Опубликовать",
                            callback_data=f"approve_{review_request.digest_id}",
                        ),
                        InlineKeyboardButton(text="❌ Пропустить", callback_data=f"reject_{review_request.digest_id}"),
                    ],
                    [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{review_request.digest_id}")],
                ]
            )

            # Add expiration info to message
            preview_text = f"📋 **Предпросмотр поста**\n\n{review_request.message_text}\n\n⏰ Автопубликация через {self.auto_post_timeout_min} мин."

            # Send message to admin
            message = await self.bot.send_message(
                chat_id=self.admin_id,
                text=preview_text,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

            review_request.admin_message_id = message.message_id
            logger.debug(f"Sent preview to admin for digest {review_request.digest_id}")

        except Exception as e:
            logger.error(f"Error sending preview to admin: {e}")

    async def _auto_approve_timer(self, digest_id: int) -> None:
        """Auto-approve digest after timeout."""
        try:
            # Wait for timeout
            await asyncio.sleep(self.auto_post_timeout_min * 60)

            # Check if still pending
            if digest_id in self.pending_reviews:
                review_request = self.pending_reviews[digest_id]
                if review_request.status == "pending":
                    logger.info(f"Auto-approving digest {digest_id} after timeout")
                    await self._handle_approval(digest_id)

        except Exception as e:
            logger.error(f"Error in auto-approve timer for digest {digest_id}: {e}")

    async def handle_callback(self, callback_query: CallbackQuery) -> bool:
        """
        Handle callback query from admin buttons.

        Args:
            callback_query: Telegram callback query

        Returns:
            True if callback was handled, False otherwise
        """
        try:
            if not callback_query.data:
                return False

            # Parse callback data
            parts = callback_query.data.split("_")
            if len(parts) != 2:
                return False

            action, digest_id_str = parts
            digest_id = int(digest_id_str)

            # Check if review request exists
            if digest_id not in self.pending_reviews:
                await callback_query.answer("❌ Запрос на проверку не найден")
                return False

            review_request = self.pending_reviews[digest_id]

            # Check if already processed
            if review_request.status != "pending":
                await callback_query.answer("❌ Запрос уже обработан")
                return False

            # Handle different actions
            if action == "approve":
                await self._handle_approval(digest_id)
                await callback_query.answer("✅ Пост одобрен для публикации")

            elif action == "reject":
                await self._handle_rejection(digest_id)
                await callback_query.answer("❌ Пост отклонен")

            elif action == "edit":
                await self._handle_edit_request(digest_id)
                await callback_query.answer("✏️ Режим редактирования (в разработке)")

            else:
                await callback_query.answer("❓ Неизвестное действие")
                return False

            return True

        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await callback_query.answer("❌ Ошибка обработки запроса")
            return False

    async def _handle_approval(self, digest_id: int) -> None:
        """Handle digest approval."""
        try:
            review_request = self.pending_reviews.get(digest_id)
            if not review_request:
                return

            # Update status
            review_request.status = "approved"

            # Call approval callback if set
            if self.approval_callback:
                await self.approval_callback(review_request.digest_data)

            # Update admin message
            await self._update_admin_message(review_request, "✅ **ОДОБРЕНО**")

            # Update metrics
            self.metrics.increment_review_approved_total()

            # Clean up
            del self.pending_reviews[digest_id]

            logger.info(f"Digest {digest_id} approved for publication")

        except Exception as e:
            logger.error(f"Error handling approval for digest {digest_id}: {e}")

    async def _handle_rejection(self, digest_id: int) -> None:
        """Handle digest rejection."""
        try:
            review_request = self.pending_reviews.get(digest_id)
            if not review_request:
                return

            # Update status
            review_request.status = "rejected"

            # Call rejection callback if set
            if self.rejection_callback:
                await self.rejection_callback(review_request.digest_data)

            # Update admin message
            await self._update_admin_message(review_request, "❌ **ОТКЛОНЕНО**")

            # Update metrics
            self.metrics.increment_review_rejected_total()

            # Clean up
            del self.pending_reviews[digest_id]

            logger.info(f"Digest {digest_id} rejected")

        except Exception as e:
            logger.error(f"Error handling rejection for digest {digest_id}: {e}")

    async def _handle_edit_request(self, digest_id: int) -> None:
        """Handle edit request (placeholder for future implementation)."""
        try:
            review_request = self.pending_reviews.get(digest_id)
            if not review_request:
                return

            # For now, just send a message that editing is not implemented
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=f"✏️ Редактирование поста #{digest_id} пока не реализовано.\nИспользуйте 'Опубликовать' или 'Пропустить'.",
            )

            logger.info(f"Edit requested for digest {digest_id} (not implemented)")

        except Exception as e:
            logger.error(f"Error handling edit request for digest {digest_id}: {e}")

    async def _update_admin_message(self, review_request: ReviewRequest, status_text: str) -> None:
        """Update admin message with final status."""
        try:
            if not review_request.admin_message_id:
                return

            updated_text = f"📋 **Предпросмотр поста** {status_text}\n\n{review_request.message_text}"

            await self.bot.edit_message_text(
                chat_id=self.admin_id,
                message_id=review_request.admin_message_id,
                text=updated_text,
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Error updating admin message: {e}")

    def get_pending_reviews_count(self) -> int:
        """Get number of pending reviews."""
        return len([r for r in self.pending_reviews.values() if r.status == "pending"])

    def get_review_stats(self) -> Dict[str, Any]:
        """Get review statistics."""
        pending = len([r for r in self.pending_reviews.values() if r.status == "pending"])
        total = len(self.pending_reviews)

        return {
            "enabled": self.enabled,
            "admin_id": self.admin_id,
            "auto_post_timeout_min": self.auto_post_timeout_min,
            "pending_reviews": pending,
            "total_reviews": total,
        }

    def cleanup_expired_reviews(self) -> int:
        """Clean up expired review requests."""
        now = datetime.now(timezone.utc)
        expired_count = 0

        expired_ids = []
        for digest_id, review_request in self.pending_reviews.items():
            if review_request.expires_at < now and review_request.status == "pending":
                expired_ids.append(digest_id)

        for digest_id in expired_ids:
            review_request = self.pending_reviews[digest_id]
            review_request.status = "expired"
            del self.pending_reviews[digest_id]
            expired_count += 1

            # Update metrics
            self.metrics.increment_review_expired_total()

        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired review requests")

        return expired_count


# Global review handler instance
_review_handler_instance: Optional[ReviewHandler] = None


def get_review_handler() -> ReviewHandler:
    """Get global review handler instance."""
    global _review_handler_instance
    if _review_handler_instance is None:
        _review_handler_instance = ReviewHandler()
    return _review_handler_instance


async def request_digest_review(digest_data: Dict[str, Any], message_text: str) -> bool:
    """
    Convenience function to request review for a digest.

    Args:
        digest_data: Digest data dictionary
        message_text: Formatted message text

    Returns:
        True if review was requested successfully
    """
    handler = get_review_handler()
    return await handler.request_review(digest_data, message_text)

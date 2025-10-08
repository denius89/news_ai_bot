"""
Progress animation utilities for Telegram bot.
Provides animated progress indicators for AI digest generation.
"""

import asyncio
import logging
from typing import List, Optional
from aiogram import types
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)


class ProgressAnimation:
    """Class for managing animated progress in Telegram messages."""

    def __init__(self, callback_query: types.CallbackQuery):
        self.callback_query = callback_query
        self.message = callback_query.message
        self.user = callback_query.from_user
        self.is_running = False

    async def show_generation_progress(
        self, steps: List[str], progress_bar: bool = True, interval: float = 1.5
    ) -> None:
        """
        Show animated progress for digest generation.

        Args:
            steps: List of progress step messages
            progress_bar: Whether to show progress bar
            interval: Time between updates in seconds
        """
        if not steps:
            return

        self.is_running = True
        total_steps = len(steps)

        try:
            for i, step in enumerate(steps):
                if not self.is_running:
                    break

                progress_text = self._build_progress_text(step, i, total_steps, progress_bar)

                try:
                    await self.message.edit_text(progress_text, parse_mode="HTML", disable_web_page_preview=True)
                except TelegramBadRequest as e:
                    if "message is not modified" in str(e):
                        # Message content is the same, continue
                        logger.debug("Message not modified, continuing animation")
                    else:
                        logger.warning(f"Failed to update progress message: {e}")
                        break

                # Wait before next update (except for last step)
                if i < total_steps - 1:
                    await asyncio.sleep(interval)

        except Exception as e:
            logger.error(f"Error in progress animation: {e}")
        finally:
            self.is_running = False

    def _build_progress_text(self, step: str, current: int, total: int, show_bar: bool) -> str:
        """Build progress text with optional progress bar."""
        text = f"⏳ {step}"

        if show_bar and total > 1:
            progress_percent = int((current + 1) / total * 100)
            progress_bar_text = self._generate_progress_bar(current + 1, total)
            text += f"\n\n{progress_bar_text} {progress_percent}%"

        return text

    def _generate_progress_bar(self, current: int, total: int) -> str:
        """Generate a visual progress bar."""
        bar_length = 10
        filled = int(current / total * bar_length)

        filled_char = "▰"
        empty_char = "▱"

        bar = filled_char * filled + empty_char * (bar_length - filled)
        return f"Генерация дайджеста:\n{bar}"

    def stop(self) -> None:
        """Stop the animation."""
        self.is_running = False


async def show_generation_progress(
    callback_query: types.CallbackQuery,
    steps: Optional[List[str]] = None,
    progress_bar: bool = True,
    interval: float = 1.5,
) -> ProgressAnimation:
    """
    Convenience function to show generation progress.

    Args:
        callback_query: Telegram callback query object
        steps: List of progress messages (uses default if None)
        progress_bar: Whether to show progress bar
        interval: Time between updates in seconds

    Returns:
        ProgressAnimation object for control
    """
    if steps is None:
        steps = [
            "🧠 Анализируем новости...",
            "📊 Считаем важность и достоверность...",
            "✨ Формируем резюме...",
            "🔗 Проверяем источники...",
            "📝 Завершаем дайджест...",
        ]

    animation = ProgressAnimation(callback_query)

    # Start animation in background
    asyncio.create_task(animation.show_generation_progress(steps, progress_bar, interval))

    return animation


async def show_quick_progress(
    callback_query: types.CallbackQuery,
    message: str = "⏳ Генерация дайджеста для тебя...",
    duration: float = 2.0,
) -> None:
    """
    Show a quick progress message for immediate feedback.

    Args:
        callback_query: Telegram callback query object
        message: Initial progress message
        duration: How long to show the message
    """
    try:
        await callback_query.message.edit_text(message)
        await asyncio.sleep(duration)
    except Exception as e:
        logger.warning(f"Failed to show quick progress: {e}")


def build_digest_actions_keyboard(username: str, category: str = None) -> types.InlineKeyboardMarkup:
    """
    Build inline keyboard with digest actions.

    Args:
        username: User's username for personalization
        category: Selected category (if any)

    Returns:
        InlineKeyboardMarkup with action buttons
    """
    buttons = []

    # Subscribe button (if category is specified)
    if category and category != "all":
        buttons.append(
            [
                types.InlineKeyboardButton(
                    text=f"📋 Подписаться на {CATEGORIES.get(category, category)}",
                    callback_data=f"subscribe_category:{category}",
                )
            ]
        )

    # Enable auto-digest button
    buttons.append([types.InlineKeyboardButton(text="🔔 Включить авто-дайджест", callback_data="enable_auto_digest")])

    # Back button
    buttons.append([types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


# Import CATEGORIES here to avoid circular imports
try:
    from digests.configs import CATEGORIES
except ImportError:
    CATEGORIES = {}

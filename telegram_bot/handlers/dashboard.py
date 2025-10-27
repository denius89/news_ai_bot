"""
Dashboard handler for Telegram bot.
Provides WebApp Dashboard functionality.
"""

import logging
from config.core.settings import WEBAPP_URL
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)


async def open_dashboard(message: types.Message):
    """
    Open dashboard WebApp for user.

    Args:
        message: Telegram message with user context
    """
    # Build WebApp URL
    webapp_url = f"{WEBAPP_URL}/webapp"

    # Create keyboard with WebApp button
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть Dashboard", web_app=types.WebAppInfo(url=webapp_url))],
            [InlineKeyboardButton(text="◀️ Back to Bot", callback_data="back_to_bot")],
        ]
    )

    # Send message with WebApp button
    text = (
        "🚀 <b>PulseAI Dashboard</b>\n\n"
        "Управляйте своими:\n"
        "• Подписками\n"
        "• Уведомлениями\n"
        "• Настройками\n\n"
        "Нажмите кнопку ниже, чтобы открыть Dashboard"
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

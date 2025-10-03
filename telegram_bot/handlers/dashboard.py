"""
Telegram bot handlers for Dashboard WebApp.
"""

import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("dashboard"))
async def open_dashboard(message: types.Message):
    """
    Handler for /dashboard command.
    Sends a keyboard with WebApp button to open PulseAI Dashboard.
    """
    logger.info("📱 Dashboard command received from user %s", message.from_user.id)

    # TODO: Move WebApp URL to config.py
    webapp_url = "https://creativity-topic-boot-courage.trycloudflare.com/webapp"

    # Create keyboard with WebApp button
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Открыть Dashboard", web_app=WebAppInfo(url=webapp_url))]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )

    await message.answer(
        "🚀 <b>PulseAI Dashboard</b>\n\n"
        "Откройте ваш персональный дашборд для управления:\n"
        "• 📑 Подписками на категории\n"
        "• 🔔 Уведомлениями\n"
        "• 📅 Календарем событий\n\n"
        "💡 <i>Подсказка: В Dashboard есть кнопка 🔙 \"Back to Bot\" для возврата сюда.</i>\n\n"
        "Нажмите кнопку ниже для запуска:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )

    logger.info("📱 Dashboard WebApp sent to user %s", message.from_user.id)


__all__ = ["router"]

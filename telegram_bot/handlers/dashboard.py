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
    webapp_url = "https://example.invalid/webapp"

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


@router.callback_query(lambda c: c.data == "dashboard")
async def open_dashboard_callback(callback_query: types.CallbackQuery):
    """
    Handler for dashboard callback from inline keyboard.
    Sends a keyboard with WebApp button to open PulseAI Dashboard.
    """
    logger.info("📱 Dashboard callback received from user %s", callback_query.from_user.id)

    # TODO: Move WebApp URL to config.py
    webapp_url = "https://example.invalid/webapp"

    # Create keyboard with WebApp button
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Открыть Dashboard", web_app=WebAppInfo(url=webapp_url))]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )

    await callback_query.message.answer(
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

    # Answer the callback query to remove loading state
    await callback_query.answer()

    logger.info("📱 Dashboard WebApp sent to user %s via callback", callback_query.from_user.id)


__all__ = ["router"]

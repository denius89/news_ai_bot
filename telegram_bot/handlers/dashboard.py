"""
Telegram bot handlers for Dashboard WebApp.
"""

import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import (
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram_bot.keyboards import back_inline_keyboard  # noqa: F401
from config.core.settings import WEBAPP_URL

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("dashboard"))
async def open_dashboard(message: types.Message):
    """
    Handler for /dashboard command.
    Sends a keyboard with WebApp button to open PulseAI Dashboard.
    """
    logger.info("📱 Dashboard command received from user %s", message.from_user.id)

    webapp_url = f"{WEBAPP_URL}/webapp"
    logger.info("🔗 Using WebApp URL: %s", webapp_url)

    # Создаем inline клавиатуру с WebApp кнопкой и кнопкой "Назад"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 Открыть Dashboard", web_app=WebAppInfo(url=webapp_url))],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
        ]
    )

    await message.answer(
        "🌐 <b>PulseAI Dashboard</b>\n\n"
        "Полнофункциональный веб-интерфейс с расширенными возможностями!\n\n"
        "✨ <b>Что доступно:</b>\n\n"
        "📑 <b>Управление подписками</b>\n"
        "   • 70 категорий новостей\n"
        "   • Гибкая настройка интересов\n"
        "   • Мгновенное обновление\n\n"
        "🔔 <b>Система уведомлений</b>\n"
        "   • Уведомления о дайджестах\n"
        "   • Алерты важных событий\n"
        "   • Настройка времени и частоты\n\n"
        "📅 <b>Интерактивный календарь</b>\n"
        "   • События из 20+ провайдеров\n"
        "   • Фильтры по категориям\n"
        "   • AI-оценка важности\n\n"
        "📊 <b>Статистика и метрики</b>\n"
        "   • История дайджестов\n"
        "   • Аналитика качества\n"
        "   • Персональные рекомендации\n\n"
        '💡 <i>Подсказка: Используйте кнопку 🔙 "Back to Bot" для возврата в Telegram.</i>\n\n'
        "Нажмите кнопку ниже для запуска:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "dashboard")
async def cb_dashboard(query: types.CallbackQuery):
    """
    Handler for dashboard callback from main menu.
    Shows WebApp button to open PulseAI Dashboard.
    """
    logger.info("📱 Dashboard callback received from user %s", query.from_user.id)

    webapp_url = f"{WEBAPP_URL}/webapp"
    logger.info("🔗 Using WebApp URL: %s", webapp_url)

    # Создаем inline клавиатуру с WebApp кнопкой и кнопкой "Назад"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 Открыть Dashboard", web_app=WebAppInfo(url=webapp_url))],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
        ]
    )

    await query.message.edit_text(
        "🌐 <b>PulseAI Dashboard</b>\n\n"
        "Полнофункциональный веб-интерфейс с расширенными возможностями!\n\n"
        "✨ <b>Что доступно:</b>\n\n"
        "📑 <b>Управление подписками</b>\n"
        "   • 70 категорий новостей\n"
        "   • Гибкая настройка интересов\n"
        "   • Мгновенное обновление\n\n"
        "🔔 <b>Система уведомлений</b>\n"
        "   • Уведомления о дайджестах\n"
        "   • Алерты важных событий\n"
        "   • Настройка времени и частоты\n\n"
        "📅 <b>Интерактивный календарь</b>\n"
        "   • События из 20+ провайдеров\n"
        "   • Фильтры по категориям\n"
        "   • AI-оценка важности\n\n"
        "📊 <b>Статистика и метрики</b>\n"
        "   • История дайджестов\n"
        "   • Аналитика качества\n"
        "   • Персональные рекомендации\n\n"
        '💡 <i>Подсказка: Используйте кнопку 🔙 "Back to Bot" для возврата в Telegram.</i>\n\n'
        "Нажмите кнопку ниже для запуска:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await query.answer()

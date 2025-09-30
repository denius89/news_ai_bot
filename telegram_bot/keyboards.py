# telegram_bot/keyboards.py
from aiogram import types


def start_inline_keyboard() -> types.InlineKeyboardMarkup:
    """Стартовое меню (первая кнопка Старт)"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="🚀 Старт", callback_data="start")]]
    )


def main_inline_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="📰 Новости", callback_data="digest:all")],
            [types.InlineKeyboardButton(text="🤖 AI-дайджест", callback_data="digest_ai")],
            [types.InlineKeyboardButton(text="📅 События", callback_data="events")],
        ]
    )


def back_inline_keyboard() -> types.InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]]
    )

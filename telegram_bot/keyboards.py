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
            [types.InlineKeyboardButton(text="🔔 Уведомления", callback_data="notifications")],
            [types.InlineKeyboardButton(text="🌐 WebApp", callback_data="dashboard")],
        ]
    )


def back_inline_keyboard() -> types.InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]]
    )


def subscriptions_inline_keyboard() -> types.InlineKeyboardMarkup:
    """Клавиатура для управления подписками"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="📋 Мои подписки", callback_data="my_subs")],
            [types.InlineKeyboardButton(text="➕ Подписаться", callback_data="subscribe_menu")],
            [types.InlineKeyboardButton(text="➖ Отписаться", callback_data="unsubscribe_menu")],
            [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
        ]
    )


def notifications_inline_keyboard() -> types.InlineKeyboardMarkup:
    """Клавиатура для управления уведомлениями"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🔔 Мои уведомления", callback_data="my_notifications"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="✅ Включить дайджест", callback_data="notify_on_digest"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="❌ Выключить дайджест", callback_data="notify_off_digest"
                )
            ],
            [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
        ]
    )


def categories_inline_keyboard(action: str = "subscribe") -> types.InlineKeyboardMarkup:
    """Клавиатура для выбора категорий (для подписок/отписок)"""
    from digests.configs import CATEGORIES

    keyboard = []
    for key, label in CATEGORIES.items():
        keyboard.append([types.InlineKeyboardButton(text=label, callback_data=f"{action}:{key}")])

    keyboard.append([types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)

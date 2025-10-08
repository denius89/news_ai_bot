# telegram_bot/keyboards.py
from aiogram import types
from services.categories import get_categories, get_subcategories, get_emoji_icon


def start_inline_keyboard() -> types.InlineKeyboardMarkup:
    """Стартовое меню (первая кнопка Старт)"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="🚀 Старт", callback_data="start")]]
    )


def main_inline_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="📰 Новости", callback_data="digest_menu")],
            [types.InlineKeyboardButton(text="🤖 AI-дайджест", callback_data="digest_ai")],
            [types.InlineKeyboardButton(text="📅 События", callback_data="events")],
            [types.InlineKeyboardButton(text="🌐 WebApp", callback_data="dashboard")],
        ]
    )


def settings_inline_keyboard() -> types.InlineKeyboardMarkup:
    """Клавиатура настроек (объединяет подписки и уведомления)"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="📋 Подписки", callback_data="subscriptions")],
            [types.InlineKeyboardButton(text="🔔 Уведомления", callback_data="notifications")],
            [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
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
            [types.InlineKeyboardButton(text="🔔 Мои уведомления", callback_data="my_notifications")],
            [types.InlineKeyboardButton(text="✅ Включить дайджест", callback_data="notify_on_digest")],
            [types.InlineKeyboardButton(text="❌ Выключить дайджест", callback_data="notify_off_digest")],
            [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
        ]
    )


def categories_inline_keyboard(action: str = "subscribe") -> types.InlineKeyboardMarkup:
    """Динамическая клавиатура категорий для подписок"""
    categories = get_categories()

    buttons = []
    for category in categories:
        emoji = get_emoji_icon(category, "")  # Базовый emoji для категории
        buttons.append([types.InlineKeyboardButton(
            text=f"{emoji} {category.title()}", callback_data=f"{action}:{category}")])

    # Добавляем кнопку "Назад"
    buttons.append([types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def subcategories_inline_keyboard(category: str,
                                  action: str = "subscribe") -> types.InlineKeyboardMarkup:
    """Динамическая клавиатура подкатегорий для выбранной категории"""
    subcategories = get_subcategories(category)

    buttons = []
    for subcategory in subcategories:
        emoji = get_emoji_icon(category, subcategory)
        buttons.append(
            [
                types.InlineKeyboardButton(
                    text=f"{emoji} {subcategory.title()}",
                    callback_data=f"{action}:{category}:{subcategory}",
                )
            ]
        )

    # Добавляем кнопку "Назад"
    buttons.append([types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def digest_categories_inline_keyboard() -> types.InlineKeyboardMarkup:
    """Клавиатура категорий для дайджеста"""
    categories = get_categories()

    buttons = []
    # Кнопка "Все категории"
    buttons.append([types.InlineKeyboardButton(text="📰 Все категории", callback_data="digest:all")])

    # Кнопки по категориям
    for category in categories:
        emoji = get_emoji_icon(category, "")
        buttons.append([types.InlineKeyboardButton(
            text=f"{emoji} {category.title()}", callback_data=f"digest:{category}")])

    # Добавляем кнопку "Назад"
    buttons.append([types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

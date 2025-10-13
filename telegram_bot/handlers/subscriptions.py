"""
Telegram bot handlers for subscription and notification management.

This module provides aiogram v3 handlers for managing user subscriptions
and notifications through Telegram commands.
"""

import logging
from aiogram import Router, types, F
from aiogram.filters import Command

from services.subscription_service import SubscriptionService
from services.notification_service import NotificationService
from services.categories import get_categories
from telegram_bot.keyboards import (
    subscriptions_inline_keyboard,
    categories_inline_keyboard,
    back_inline_keyboard,
)

logger = logging.getLogger(__name__)

# Initialize services
subscription_service = SubscriptionService()
notification_service = NotificationService()

# Create router
router = Router()

# Available notification types
NOTIFICATION_TYPES = ["digest", "events", "breaking"]


# --- COMMAND HANDLERS ---


@router.message(Command("subscribe"))
async def cmd_subscribe(message: types.Message):
    """Handle /subscribe <category> command to add subscription."""
    try:
        # Parse command arguments
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer(
                "❌ Использование: /subscribe <category>\n" f"Доступные категории: {', '.join(get_categories())}"
            )
            return

        category = args[1].strip().lower()
        if category not in get_categories():
            await message.answer(
                f"❌ Неизвестная категория: {category}\n" f"Доступные категории: {', '.join(get_categories())}"
            )
            return

        # Get or create user
        user_id = await subscription_service.get_or_create_user(
            telegram_id=message.from_user.id, username=message.from_user.username, locale="ru"
        )

        if not user_id:
            await message.answer("❌ Не удалось выполнить действие")
            return

        # Add subscription
        success = await subscription_service.add(user_id, category)

        if success:
            await message.answer(f"✅ Подписка на {category} добавлена")
        else:
            await message.answer(f"ℹ️ Вы уже подписаны на {category}")

    except Exception as e:
        logger.error("Error in cmd_subscribe: %s", e)
        await message.answer("❌ Не удалось выполнить действие")


@router.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: types.Message):
    """Handle /unsubscribe <category> command to remove subscription."""
    try:
        # Parse command arguments
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer(
                "❌ Использование: /unsubscribe <category>\n" f"Доступные категории: {', '.join(get_categories())}"
            )
            return

        category = args[1].strip().lower()
        if category not in get_categories():
            await message.answer(
                f"❌ Неизвестная категория: {category}\n" f"Доступные категории: {', '.join(get_categories())}"
            )
            return

        # Get or create user
        user_id = await subscription_service.get_or_create_user(
            telegram_id=message.from_user.id, username=message.from_user.username, locale="ru"
        )

        if not user_id:
            await message.answer("❌ Не удалось выполнить действие")
            return

        # Remove subscription
        removed_count = await subscription_service.remove(user_id, category)

        if removed_count > 0:
            await message.answer(f"✅ Подписка на {category} удалена")
        else:
            await message.answer(f"ℹ️ Вы не были подписаны на {category}")

    except Exception as e:
        logger.error("Error in cmd_unsubscribe: %s", e)
        await message.answer("❌ Не удалось выполнить действие")


@router.message(Command("my_subs"))
async def cmd_my_subs(message: types.Message):
    """Handle /my_subs command to show user's subscriptions."""
    try:
        # Get or create user
        user_id = await subscription_service.get_or_create_user(
            telegram_id=message.from_user.id, username=message.from_user.username, locale="ru"
        )

        if not user_id:
            await message.answer("❌ Не удалось выполнить действие")
            return

        # Get subscriptions
        subscriptions = await subscription_service.list(user_id)

        if not subscriptions:
            await message.answer(
                "📋 У вас пока нет подписок.\n"
                f"Добавьте: /subscribe <category>\n"
                f"Доступные категории: {', '.join(get_categories())}"
            )
        else:
            # Format subscriptions list
            categories = sorted([sub["category"] for sub in subscriptions])
            text = "📋 <b>Ваши подписки:</b>\n\n"
            for i, category in enumerate(categories, 1):
                text += f"{i}. {category}\n"

            await message.answer(text, parse_mode="HTML")

    except Exception as e:
        logger.error("Error in cmd_my_subs: %s", e)
        await message.answer("❌ Не удалось выполнить действие")


@router.message(Command("categories"))
async def cmd_categories(message: types.Message):
    """Handle /categories command to show available categories."""
    categories_text = ", ".join(sorted(get_categories()))
    await message.answer(f"📋 Доступные категории:\n\n{categories_text}")


@router.message(Command("help_subs"))
async def cmd_help_subs(message: types.Message):
    """Handle /help_subs command to show subscription help."""
    help_text = """
📋 <b>Управление подписками:</b>

/subscribe <category> - подписаться на категорию
/unsubscribe <category> - отписаться от категории
/my_subs - показать ваши подписки
/categories - показать доступные категории

📊 <b>Доступные категории:</b>
{}

🔔 <b>Типы уведомлений:</b>
{}

<b>Примеры:</b>
/subscribe crypto
/notify_on digest
/notify_off events
""".format(
        ", ".join(get_categories()), ", ".join(NOTIFICATION_TYPES)
    )

    await message.answer(help_text, parse_mode="HTML")


# --- CALLBACK HANDLERS ---


@router.callback_query(F.data == "subscriptions")
async def cb_subscriptions_menu(query: types.CallbackQuery):
    """Показать меню подписок"""
    text = "📋 <b>Управление подписками</b>\n\nВыберите действие:"
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=subscriptions_inline_keyboard())


# Удален дублирующий обработчик - теперь используется в notifications.py


@router.callback_query(F.data == "my_subs")
async def cb_my_subs(query: types.CallbackQuery):
    """Показать подписки пользователя через callback"""
    try:
        # Get or create user
        user_id = await subscription_service.get_or_create_user(
            telegram_id=query.from_user.id, username=query.from_user.username, locale="ru"
        )

        if not user_id:
            await query.message.edit_text("❌ Не удалось выполнить действие", reply_markup=back_inline_keyboard())
            return

        # Get subscriptions
        subscriptions = await subscription_service.list(user_id)

        if not subscriptions:
            text = (
                "📋 <b>Ваши подписки</b>\n\n"
                "У вас пока нет подписок.\n"
                "Добавьте: /subscribe <category>\n"
                f"Доступные категории: {', '.join(get_categories())}"
            )
        else:
            # Format subscriptions list
            categories = sorted([sub["category"] for sub in subscriptions])
            text = "📋 <b>Ваши подписки:</b>\n\n"
            for i, category in enumerate(categories, 1):
                text += f"{i}. {category}\n"

        await query.message.edit_text(text, parse_mode="HTML", reply_markup=back_inline_keyboard())

    except Exception as e:
        logger.error("Error in cb_my_subs: %s", e)
        await query.message.edit_text("❌ Не удалось выполнить действие", reply_markup=back_inline_keyboard())


@router.callback_query(F.data == "subscribe_menu")
async def cb_subscribe_menu(query: types.CallbackQuery):
    """Показать меню выбора категории для подписки"""
    text = "➕ <b>Подписаться на категорию</b>\n\nВыберите категорию:"
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=categories_inline_keyboard("subscribe"))


@router.callback_query(F.data == "unsubscribe_menu")
async def cb_unsubscribe_menu(query: types.CallbackQuery):
    """Показать меню выбора категории для отписки"""
    text = "➖ <b>Отписаться от категории</b>\n\nВыберите категорию:"
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=categories_inline_keyboard("unsubscribe"))


@router.callback_query(F.data.startswith("subscribe:"))
async def cb_subscribe_category(query: types.CallbackQuery):
    """Подписаться на выбранную категорию"""
    try:
        category = query.data.split(":", 1)[1]

        # Get or create user
        user_id = await subscription_service.get_or_create_user(
            telegram_id=query.from_user.id, username=query.from_user.username, locale="ru"
        )

        if not user_id:
            await query.answer("❌ Не удалось выполнить действие")
            return

        # Add subscription
        success = await subscription_service.add(user_id, category)

        if success:
            await query.answer(f"✅ Подписка на {category} добавлена")
        else:
            await query.answer(f"ℹ️ Вы уже подписаны на {category}")

        # Return to subscriptions menu (with error handling)
        try:
            await cb_subscriptions_menu(query)
        except Exception as menu_error:
            if "message is not modified" in str(menu_error):
                logger.debug("Menu update skipped (same content): %s", menu_error)
            else:
                raise

    except Exception as e:
        logger.error("Error in cb_subscribe_category: %s", e)
        await query.answer("❌ Не удалось выполнить действие")


@router.callback_query(F.data.startswith("unsubscribe:"))
async def cb_unsubscribe_category(query: types.CallbackQuery):
    """Отписаться от выбранной категории"""
    try:
        category = query.data.split(":", 1)[1]

        # Get or create user
        user_id = await subscription_service.get_or_create_user(
            telegram_id=query.from_user.id, username=query.from_user.username, locale="ru"
        )

        if not user_id:
            await query.answer("❌ Не удалось выполнить действие")
            return

        # Remove subscription
        removed_count = await subscription_service.remove(user_id, category)

        if removed_count > 0:
            await query.answer(f"✅ Подписка на {category} удалена")
        else:
            await query.answer(f"ℹ️ Вы не были подписаны на {category}")

        # Return to subscriptions menu (with error handling)
        try:
            await cb_subscriptions_menu(query)
        except Exception as menu_error:
            if "message is not modified" in str(menu_error):
                logger.debug("Menu update skipped (same content): %s", menu_error)
            else:
                raise

    except Exception as e:
        logger.error("Error in cb_unsubscribe_category: %s", e)
        await query.answer("❌ Не удалось выполнить действие")


@router.callback_query(F.data == "my_notifications")
async def cb_my_notifications(query: types.CallbackQuery):
    """Показать настройки уведомлений пользователя через callback"""
    try:
        # Get or create user
        user_id = await subscription_service.get_or_create_user(
            telegram_id=query.from_user.id, username=query.from_user.username, locale="ru"
        )

        if not user_id:
            await query.message.edit_text("❌ Не удалось выполнить действие", reply_markup=back_inline_keyboard())
            return

        # Get notifications
        notifications = await notification_service.list(user_id)

        if not notifications:
            text = (
                "🔔 <b>Ваши уведомления</b>\n\n"
                "У вас нет настроенных уведомлений.\n"
                f"Включите: /notify_on <type>\n"
                f"Доступные типы: {', '.join(NOTIFICATION_TYPES)}"
            )
        else:
            # Format notifications list
            text = "🔔 <b>Ваши уведомления:</b>\n\n"
            for i, notif in enumerate(notifications, 1):
                status = "✅ включено" if notif.get("enabled", False) else "❌ отключено"
                frequency = notif.get("frequency", "daily")
                hour = notif.get("preferred_hour", 9)
                text += f"{i}. {notif['type']} - {status}\n"
                if notif.get("enabled", False):
                    if frequency == "instant":
                        text += "   Мгновенно\n"
                    else:
                        text += f"   Частота: {frequency}, время: {hour}:00\n"

        await query.message.edit_text(text, parse_mode="HTML", reply_markup=back_inline_keyboard())

    except Exception as e:
        logger.error("Error in cb_my_notifications: %s", e)
        await query.message.edit_text("❌ Не удалось выполнить действие", reply_markup=back_inline_keyboard())


@router.callback_query(F.data == "notify_on_digest")
async def cb_notify_on_digest(query: types.CallbackQuery):
    """Включить уведомления дайджеста"""
    try:
        # Get or create user
        user_id = await subscription_service.get_or_create_user(
            telegram_id=query.from_user.id, username=query.from_user.username, locale="ru"
        )

        if not user_id:
            await query.answer("❌ Не удалось выполнить действие")
            return

        # Enable notification
        await notification_service.enable(user_id, "digest")
        await query.answer("✅ Уведомления digest включены")

        # Return to notifications menu (with error handling)
        try:
            await cb_my_notifications(query)
        except Exception as menu_error:
            if "message is not modified" in str(menu_error):
                logger.debug("Menu update skipped (same content): %s", menu_error)
            else:
                raise

    except Exception as e:
        logger.error("Error in cb_notify_on_digest: %s", e)
        await query.answer("❌ Не удалось выполнить действие")


@router.callback_query(F.data == "notify_off_digest")
async def cb_notify_off_digest(query: types.CallbackQuery):
    """Отключить уведомления дайджеста"""
    try:
        # Get or create user
        user_id = await subscription_service.get_or_create_user(
            telegram_id=query.from_user.id, username=query.from_user.username, locale="ru"
        )

        if not user_id:
            await query.answer("❌ Не удалось выполнить действие")
            return

        # Disable notification
        await notification_service.disable(user_id, "digest")
        await query.answer("✅ Уведомления digest отключены")

        # Return to notifications menu (with error handling)
        try:
            await cb_my_notifications(query)
        except Exception as menu_error:
            if "message is not modified" in str(menu_error):
                logger.debug("Menu update skipped (same content): %s", menu_error)
            else:
                raise

    except Exception as e:
        logger.error("Error in cb_notify_off_digest: %s", e)
        await query.answer("❌ Не удалось выполнить действие")

"""
Telegram bot handlers for notifications.

Этот модуль предоставляет обработчики для работы с уведомлениями в Telegram-боте,
включая отправку уведомлений и обработку callback'ов для отметки прочитанными.
"""

import logging
from aiogram import Router, types, F
from aiogram.filters import Command

from services.notification_service import get_notification_service
from telegram_bot.keyboards import notifications_inline_keyboard, back_inline_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("notifications"))
async def cmd_notifications(message: types.Message):
    """Обработчик команды /notifications."""
    await message.answer(
        "🔔 <b>Управление уведомлениями</b>\n\n"
        "Здесь вы можете управлять своими уведомлениями.\n"
        "Используйте кнопки ниже для навигации.",
        parse_mode="HTML",
        reply_markup=notifications_inline_keyboard(),
    )


@router.callback_query(F.data == "notifications")
async def cb_notifications_menu(query: types.CallbackQuery):
    """Показать меню уведомлений."""
    await query.message.edit_text(
        "🔔 <b>Управление уведомлениями</b>\n\n"
        "Здесь вы можете управлять своими уведомлениями.\n"
        "Используйте кнопки ниже для навигации.",
        parse_mode="HTML",
        reply_markup=notifications_inline_keyboard(),
    )
    await query.answer()


@router.callback_query(F.data == "my_notifications")
async def cb_my_notifications(query: types.CallbackQuery):
    """Показать уведомления пользователя."""
    try:
        from database.db_models import get_user_notifications

        # Получаем уведомления пользователя
        notifications = await get_user_notifications(user_id=query.from_user.id)

        if not notifications:
            await query.message.edit_text(
                "📭 <b>У вас пока нет уведомлений</b>\n\n"
                "Когда появятся новые уведомления, они будут показаны здесь.",
                parse_mode="HTML",
                reply_markup=back_inline_keyboard(),
            )
            await query.answer()
            return

        # Форматируем список уведомлений
        text = "🔔 <b>Ваши уведомления</b>\n\n"

        for i, notification in enumerate(notifications[:10], 1):  # Показываем последние 10
            status = "✅" if notification.get("read", False) else "🔔"
            title = notification.get("title", "Без заголовка")
            created_at = notification.get("created_at", "")

            # Форматируем дату
            if created_at:
                try:
                    from datetime import datetime

                    if isinstance(created_at, str):
                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    else:
                        dt = created_at
                    formatted_date = dt.strftime("%d.%m.%Y %H:%M")
                except Exception:
                    formatted_date = str(created_at)
            else:
                formatted_date = "—"

            text += f"{status} <b>{title}</b>\n"
            text += f"📅 {formatted_date}\n\n"

        if len(notifications) > 10:
            text += f"... и еще {len(notifications) - 10} уведомлений"

        await query.message.edit_text(text, parse_mode="HTML", reply_markup=back_inline_keyboard())
        await query.answer()

    except Exception as e:
        logger.error(f"❌ Error getting notifications for user {query.from_user.id}: {e}")
        await query.message.edit_text(
            "❌ <b>Ошибка при загрузке уведомлений</b>\n\n" "Попробуйте позже или обратитесь в поддержку.",
            parse_mode="HTML",
            reply_markup=back_inline_keyboard(),
        )
        await query.answer("❌ Ошибка при загрузке уведомлений")


@router.callback_query(F.data.startswith("mark_read:"))
async def cb_mark_read(query: types.CallbackQuery):
    """Обработчик для отметки уведомления как прочитанного."""
    try:
        # Извлекаем notification_id из callback_data
        notification_id = query.data.split(":", 1)[1]

        # Обрабатываем через сервис
        notification_service = get_notification_service()
        success = await notification_service.mark_notification_read(
            user_id=query.from_user.id, notification_id=int(notification_id)
        )

        if not success:
            logger.warning(f"⚠️ Failed to mark notification {notification_id} as read for user {query.from_user.id}")

    except Exception as e:
        logger.error(f"❌ Error handling mark_read callback: {e}")
        await query.answer("❌ Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "notify_on_digest")
async def cb_notify_on_digest(query: types.CallbackQuery):
    """Включить уведомления о дайджестах."""
    try:
        # Здесь можно добавить логику для включения уведомлений о дайджестах
        # Пока просто показываем сообщение
        await query.message.edit_text(
            "✅ <b>Уведомления о дайджестах включены</b>\n\n"
            "Теперь вы будете получать уведомления о новых дайджестах.",
            parse_mode="HTML",
            reply_markup=back_inline_keyboard(),
        )
        await query.answer("✅ Уведомления включены")

    except Exception as e:
        logger.error(f"❌ Error enabling digest notifications: {e}")
        await query.answer("❌ Ошибка при включении уведомлений")


@router.callback_query(F.data == "notify_off_digest")
async def cb_notify_off_digest(query: types.CallbackQuery):
    """Выключить уведомления о дайджестах."""
    try:
        # Здесь можно добавить логику для выключения уведомлений о дайджестах
        # Пока просто показываем сообщение
        await query.message.edit_text(
            "❌ <b>Уведомления о дайджестах выключены</b>\n\n"
            "Вы больше не будете получать уведомления о новых дайджестах.",
            parse_mode="HTML",
            reply_markup=back_inline_keyboard(),
        )
        await query.answer("❌ Уведомления выключены")

    except Exception as e:
        logger.error(f"❌ Error disabling digest notifications: {e}")
        await query.answer("❌ Ошибка при выключении уведомлений")

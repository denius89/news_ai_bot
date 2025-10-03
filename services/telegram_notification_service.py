"""
Сервис для отправки уведомлений через Telegram-бот.

Этот модуль предоставляет функции для отправки уведомлений пользователям
через Telegram-бота с поддержкой inline-кнопок для отметки прочитанным.
"""

import logging
from datetime import datetime
from typing import Optional
from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.settings import TELEGRAM_BOT_TOKEN
from database.db_models import get_user_notifications, mark_notification_read

logger = logging.getLogger(__name__)


class TelegramNotificationService:
    """Сервис для отправки уведомлений через Telegram-бот."""

    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

    async def send_notification_via_bot(
        self, user_id: int, title: str, text: str, notification_id: Optional[str] = None
    ) -> bool:
        """
        Отправляет уведомление пользователю через Telegram-бот.

        Args:
            user_id: Telegram user ID
            title: Заголовок уведомления
            text: Текст уведомления
            notification_id: ID уведомления для кнопки "Отметить прочитанным"

        Returns:
            bool: True если уведомление отправлено успешно, False иначе
        """
        if not self.bot:
            logger.error("❌ Telegram bot token not configured")
            return False

        try:
            # Форматируем сообщение
            message_text = self._format_notification_message(title, text)

            # Создаем клавиатуру с кнопкой "Отметить прочитанным"
            keyboard = None
            if notification_id:
                keyboard = self._create_mark_read_keyboard(notification_id)

            # Отправляем сообщение
            await self.bot.send_message(
                chat_id=user_id, text=message_text, parse_mode="HTML", reply_markup=keyboard
            )

            logger.info(
                f"✅ Notification sent to user {user_id}, notification_id: {notification_id}"
            )
            return True

        except TelegramForbiddenError:
            logger.warning(f"⚠️ User {user_id} blocked the bot or has privacy settings")
            return False
        except TelegramBadRequest as e:
            logger.error(f"❌ Telegram API error for user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending notification to user {user_id}: {e}")
            return False

    def _format_notification_message(self, title: str, text: str) -> str:
        """Форматирует сообщение уведомления."""
        current_time = datetime.now().strftime("%H:%M %d.%m")

        return f"<b>🔔 {title}</b>\n\n" f"{text}\n\n" f"<i>📅 {current_time}</i>"

    def _create_mark_read_keyboard(self, notification_id: str) -> types.InlineKeyboardMarkup:
        """Создает клавиатуру с кнопкой 'Отметить прочитанным'."""
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Отметить прочитанным", callback_data=f"mark_read:{notification_id}")
        return builder.as_markup()

    async def handle_mark_read_callback(
        self, query: types.CallbackQuery, notification_id: str
    ) -> bool:
        """
        Обрабатывает callback для отметки уведомления как прочитанного.

        Args:
            query: Callback query от пользователя
            notification_id: ID уведомления

        Returns:
            bool: True если операция выполнена успешно
        """
        try:
            # Вызываем API для отметки прочитанным
            success = await self._mark_notification_read_via_api(
                user_id=query.from_user.id, notification_id=notification_id
            )

            if success:
                # Редактируем сообщение
                await query.message.edit_text(
                    query.message.text + "\n\n✅ <b>Прочитано</b>", parse_mode="HTML"
                )
                await query.answer("✅ Уведомление отмечено как прочитанное")
                logger.info(
                    f"✅ Notification {notification_id} marked as read by user {query.from_user.id}"
                )
                return True
            else:
                await query.answer("❌ Ошибка при отметке прочитанным", show_alert=True)
                return False

        except TelegramBadRequest as e:
            if "message is not modified" in str(e).lower():
                # Сообщение уже было отредактировано (идемпотентность)
                await query.answer("✅ Уведомление уже отмечено как прочитанное")
                return True
            else:
                logger.error(f"❌ Telegram API error: {e}")
                await query.answer("❌ Ошибка при обновлении сообщения", show_alert=True)
                return False
        except Exception as e:
            logger.error(f"❌ Unexpected error handling mark_read callback: {e}")
            await query.answer("❌ Произошла ошибка", show_alert=True)
            return False

    async def _mark_notification_read_via_api(self, user_id: int, notification_id: str) -> bool:
        """
        Вызывает API для отметки уведомления как прочитанного.

        Args:
            user_id: Telegram user ID
            notification_id: ID уведомления

        Returns:
            bool: True если операция выполнена успешно
        """
        try:
            # Здесь мы можем либо вызывать API напрямую, либо работать с базой данных
            # Для простоты используем прямое обращение к базе данных
            result = mark_notification_read(user_id=user_id, notification_id=notification_id)

            if result:
                logger.info(
                    f"✅ API: Notification {notification_id} marked as read for user {user_id}"
                )
                return True
            else:
                logger.warning(
                    f"⚠️ API: Failed to mark notification {notification_id} as read for user {user_id}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ API error marking notification {notification_id} as read: {e}")
            return False

    async def close(self):
        """Закрывает сессию бота."""
        if self.bot:
            await self.bot.session.close()


# Глобальный экземпляр сервиса
telegram_notification_service = TelegramNotificationService()

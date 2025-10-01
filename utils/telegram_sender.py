"""
Telegram Sender Utility - асинхронная отправка сообщений через aiogram.

Этот модуль предоставляет простой интерфейс для отправки сообщений
в Telegram через aiogram Bot API с обработкой ошибок и логированием.
"""

import asyncio
import logging
import os
from typing import Optional

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter

logger = logging.getLogger(__name__)


class TelegramSender:
    """Класс для отправки сообщений в Telegram через aiogram."""

    def __init__(self, bot_token: Optional[str] = None):
        """
        Инициализация TelegramSender.

        Args:
            bot_token: Токен бота. Если не указан, берется из TELEGRAM_BOT_TOKEN
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")

        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")

        self.bot = Bot(token=self.bot_token)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = ParseMode.HTML,
        disable_web_page_preview: bool = True,
        disable_notification: bool = False,
    ) -> bool:
        """
        Отправить сообщение пользователю в Telegram.

        Args:
            chat_id: Telegram ID пользователя
            text: Текст сообщения
            parse_mode: Режим парсинга (HTML, Markdown, MarkdownV2)
            disable_web_page_preview: Отключить предварительный просмотр ссылок
            disable_notification: Отключить уведомления

        Returns:
            True если сообщение отправлено успешно, False иначе
        """
        try:
            # Ограничиваем длину сообщения (Telegram лимит ~4096 символов)
            if len(text) > 4000:
                self.logger.warning(
                    "Сообщение для пользователя %d слишком длинное (%d символов), обрезаем",
                    chat_id,
                    len(text),
                )
                text = text[:3950] + "\n\n... (сообщение обрезано)"

            # Отправляем сообщение
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                disable_notification=disable_notification,
            )

            self.logger.debug("✅ Сообщение отправлено пользователю %d", chat_id)
            return True

        except TelegramForbiddenError as e:
            # Пользователь заблокировал бота или удалил чат
            self.logger.warning(
                "❌ Пользователь %d заблокировал бота или удалил чат: %s", chat_id, str(e)
            )
            return False

        except TelegramBadRequest as e:
            # Неверный запрос (неверный chat_id, неправильный текст и т.д.)
            self.logger.error("❌ Ошибка запроса для пользователя %d: %s", chat_id, str(e))
            return False

        except TelegramRetryAfter as e:
            # Превышен лимит запросов, нужно подождать
            self.logger.warning(
                "⏳ Превышен лимит запросов для пользователя %d, ждем %d секунд: %s",
                chat_id,
                e.retry_after,
                str(e),
            )
            await asyncio.sleep(e.retry_after)
            # Повторяем попытку
            return await self.send_message(
                chat_id, text, parse_mode, disable_web_page_preview, disable_notification
            )

        except Exception as e:
            # Неожиданная ошибка
            self.logger.error(
                "❌ Неожиданная ошибка при отправке сообщения пользователю %d: %s", chat_id, str(e)
            )
            return False

    async def send_digest(
        self, chat_id: int, digest_text: str, title: str = "📰 Дайджест новостей"
    ) -> bool:
        """
        Отправить дайджест пользователю с красивым форматированием.

        Args:
            chat_id: Telegram ID пользователя
            digest_text: Текст дайджеста
            title: Заголовок дайджеста

        Returns:
            True если дайджест отправлен успешно, False иначе
        """
        try:
            # Форматируем дайджест
            formatted_text = f"{title}\n\n{digest_text}"

            return await self.send_message(
                chat_id=chat_id,
                text=formatted_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

        except Exception as e:
            self.logger.error("❌ Ошибка отправки дайджеста пользователю %d: %s", chat_id, str(e))
            return False

    async def send_error_message(
        self, chat_id: int, error_message: str = "❌ Произошла ошибка при обработке запроса"
    ) -> bool:
        """
        Отправить сообщение об ошибке пользователю.

        Args:
            chat_id: Telegram ID пользователя
            error_message: Текст сообщения об ошибке

        Returns:
            True если сообщение отправлено успешно, False иначе
        """
        try:
            return await self.send_message(
                chat_id=chat_id, text=error_message, parse_mode=ParseMode.HTML
            )

        except Exception as e:
            self.logger.error(
                "❌ Ошибка отправки сообщения об ошибке пользователю %d: %s", chat_id, str(e)
            )
            return False

    async def send_help_message(self, chat_id: int, help_text: str) -> bool:
        """
        Отправить справочное сообщение пользователю.

        Args:
            chat_id: Telegram ID пользователя
            help_text: Текст справки

        Returns:
            True если сообщение отправлено успешно, False иначе
        """
        try:
            return await self.send_message(
                chat_id=chat_id,
                text=help_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

        except Exception as e:
            self.logger.error("❌ Ошибка отправки справки пользователю %d: %s", chat_id, str(e))
            return False

    async def close(self):
        """Закрыть сессию бота."""
        try:
            await self.bot.session.close()
            self.logger.debug("🔒 Сессия Telegram бота закрыта")
        except Exception as e:
            self.logger.error("❌ Ошибка закрытия сессии бота: %s", str(e))

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Глобальная функция для удобства использования
async def send_message(chat_id: int, text: str, **kwargs) -> bool:
    """
    Отправить сообщение пользователю в Telegram.

    Args:
        chat_id: Telegram ID пользователя
        text: Текст сообщения
        **kwargs: Дополнительные параметры для send_message

    Returns:
        True если сообщение отправлено успешно, False иначе
    """
    try:
        async with TelegramSender() as sender:
            return await sender.send_message(chat_id, text, **kwargs)
    except Exception as e:
        logger.error("❌ Ошибка в глобальной функции send_message: %s", str(e))
        return False


# Функция для отправки дайджеста
async def send_digest(chat_id: int, digest_text: str, title: str = "📰 Дайджест новостей") -> bool:
    """
    Отправить дайджест пользователю.

    Args:
        chat_id: Telegram ID пользователя
        digest_text: Текст дайджеста
        title: Заголовок дайджеста

    Returns:
        True если дайджест отправлен успешно, False иначе
    """
    try:
        async with TelegramSender() as sender:
            return await sender.send_digest(chat_id, digest_text, title)
    except Exception as e:
        logger.error("❌ Ошибка в глобальной функции send_digest: %s", str(e))
        return False


__all__ = ["TelegramSender", "send_message", "send_digest"]

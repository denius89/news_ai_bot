import sys
from pathlib import Path
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.core.settings import TELEGRAM_BOT_TOKEN
from telegram_bot.handlers import routers
from telegram_bot.middleware import (
    ErrorHandlerMiddleware,
    UserMiddleware,
    RateLimiterMiddleware,
    MetricsMiddleware,
)
from telegram_bot.config import BOT_COMMANDS
from utils.logging.logging_setup import setup_logging
from database.service import get_async_service

# --- ЛОГИРОВАНИЕ ---
setup_logging()
logger = logging.getLogger("telegram_bot")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN is not set in environment")


async def main():
    # Инициализируем асинхронную базу данных
    async_service = get_async_service()
    # Проверяем, что сервис инициализирован
    if not async_service.async_mode:
        logger.error("❌ Не удалось инициализировать асинхронную базу данных")
        return

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Register middleware (order matters!)
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    dp.message.middleware(RateLimiterMiddleware())
    dp.callback_query.middleware(RateLimiterMiddleware())

    dp.message.middleware(MetricsMiddleware())
    dp.callback_query.middleware(MetricsMiddleware())

    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())

    # Register bot commands - очищаем все команды
    from aiogram.types import BotCommand

    if BOT_COMMANDS:
        commands = [BotCommand(command=cmd["command"], description=cmd["description"]) for cmd in BOT_COMMANDS]
        await bot.set_my_commands(commands)
    else:
        # Явно очищаем команды если список пустой
        await bot.set_my_commands([])

    # Регистрируем все роутеры
    for router in routers:
        dp.include_router(router)

    logger.info("🚀 Telegram bot started")
    try:
        # Настройки polling с ограничениями
        await dp.start_polling(
            bot,
            allowed_updates=["message", "callback_query", "inline_query"],
            drop_pending_updates=True,  # Игнорируем старые обновления
            timeout=30,  # Таймаут для получения обновлений
            request_timeout=30,  # Таймаут для запросов к API
            close_bot_session=True,  # Закрывать сессию при завершении
        )
    except Exception as e:
        logger.exception(f"❌ Ошибка в Telegram-боте: {e}")
        # При конфликте завершаем работу
        if "Conflict" in str(e):
            logger.error("❌ Конфликт: другой экземпляр бота уже запущен")
            logger.error("💡 Остановите другие экземпляры: ./stop_services.sh")
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

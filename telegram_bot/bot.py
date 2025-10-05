import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.settings import TELEGRAM_BOT_TOKEN
from telegram_bot.handlers import routers
from utils.logging_setup import setup_logging
from database.service import get_async_service

# --- ЛОГИРОВАНИЕ ---
setup_logging()
logger = logging.getLogger("telegram_bot")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN is not set in environment")


async def main():
    # Инициализируем асинхронную базу данных
    async_service = get_async_service()
    await async_service._init_async_client()
    if not async_service.async_client:
        logger.error("❌ Не удалось инициализировать асинхронную базу данных")
        return

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Регистрируем все роутеры
    for router in routers:
        dp.include_router(router)

    logger.info("🚀 Telegram bot started")
    try:
        await dp.start_polling(bot)
    except Exception:
        logger.exception("❌ Ошибка в Telegram-боте")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

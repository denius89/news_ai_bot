import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from telegram_bot.handlers import routers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram_bot")

# ✅ Загружаем токен из .env или переменной окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN is not set in environment")


async def main():
    # создаём бота с настройками по умолчанию
    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # регистрируем все роутеры
    for router in routers:
        dp.include_router(router)

    logger.info("🚀 Telegram bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

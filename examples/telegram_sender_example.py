"""
Example usage of Telegram sender utility.

This script demonstrates how to use the TelegramSender class and global functions.
"""

import asyncio
import logging
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
import sys

sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()

from utils.telegram_sender import TelegramSender, send_message, send_digest

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_with_class():
    """Example using TelegramSender class directly."""
    logger.info("🔧 Пример использования TelegramSender класса")

    try:
        # Initialize sender
        sender = TelegramSender()

        # Send a simple message
        chat_id = 123456789  # Replace with actual chat ID
        success = await sender.send_message(
            chat_id, "👋 <b>Привет!</b>\n\nЭто тестовое сообщение от <i>PulseAI</i> бота."
        )

        if success:
            logger.info("✅ Сообщение отправлено успешно")
        else:
            logger.info("❌ Не удалось отправить сообщение")

        # Send a digest
        digest_content = """
<b>📰 Дайджест новостей</b>

<b>1. Криптовалюты</b>
Bitcoin достиг нового максимума $50,000
<a href="https://example.com/btc-news">Подробнее</a>

<b>2. Экономика</b>
ФРС повысила ставку на 0.25%
<a href="https://example.com/fed-news">Подробнее</a>
"""

        success = await sender.send_digest(chat_id, digest_content, "📰 Ежедневный дайджест")

        if success:
            logger.info("✅ Дайджест отправлен успешно")
        else:
            logger.info("❌ Не удалось отправить дайджест")

        # Close the sender
        await sender.close()

    except Exception as e:
        logger.error("❌ Ошибка в примере с классом: %s", str(e))


async def example_with_global_functions():
    """Example using global convenience functions."""
    logger.info("🔧 Пример использования глобальных функций")

    try:
        chat_id = 123456789  # Replace with actual chat ID

        # Send message using global function
        success = await send_message(
            chat_id, "🚀 Это сообщение отправлено через глобальную функцию!"
        )

        if success:
            logger.info("✅ Глобальная функция send_message работает")
        else:
            logger.info("❌ Глобальная функция send_message не сработала")

        # Send digest using global function
        digest_content = """
<b>🤖 AI Анализ</b>

Сегодня в мире технологий:
• OpenAI анонсировала GPT-5
• Tesla запустила новую систему автопилота
• Microsoft инвестировала $10B в ИИ
"""

        success = await send_digest(chat_id, digest_content, "🤖 AI Дайджест")

        if success:
            logger.info("✅ Глобальная функция send_digest работает")
        else:
            logger.info("❌ Глобальная функция send_digest не сработала")

    except Exception as e:
        logger.error("❌ Ошибка в примере с глобальными функциями: %s", str(e))


async def example_context_manager():
    """Example using async context manager."""
    logger.info("🔧 Пример использования async context manager")

    try:
        chat_id = 123456789  # Replace with actual chat ID

        # Use async context manager
        async with TelegramSender() as sender:
            success = await sender.send_message(
                chat_id, "🔄 Это сообщение отправлено через async context manager!"
            )

            if success:
                logger.info("✅ Context manager работает")
            else:
                logger.info("❌ Context manager не сработал")

        # Sender is automatically closed here

    except Exception as e:
        logger.error("❌ Ошибка в примере с context manager: %s", str(e))


async def example_error_handling():
    """Example demonstrating error handling."""
    logger.info("🔧 Пример обработки ошибок")

    try:
        sender = TelegramSender()

        # Try to send to invalid chat ID
        invalid_chat_id = 999999999
        success = await sender.send_message(
            invalid_chat_id, "Это сообщение не должно быть доставлено"
        )

        if not success:
            logger.info("✅ Обработка ошибок работает - сообщение не отправлено")

        # Try to send empty message
        success = await sender.send_message(123456789, "")

        if not success:
            logger.info("✅ Пустое сообщение корректно отклонено")

        await sender.close()

    except Exception as e:
        logger.error("❌ Ошибка в примере обработки ошибок: %s", str(e))


async def main():
    """Main function to run all examples."""
    logger.info("🚀 Запуск примеров использования Telegram sender")

    # Check if token is available
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        logger.error("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        logger.info("💡 Добавьте TELEGRAM_BOT_TOKEN в .env файл для тестирования")
        return

    logger.info("✅ TELEGRAM_BOT_TOKEN найден")

    # Run examples
    await example_with_class()
    await asyncio.sleep(1)

    await example_with_global_functions()
    await asyncio.sleep(1)

    await example_context_manager()
    await asyncio.sleep(1)

    await example_error_handling()

    logger.info("✅ Все примеры завершены")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Остановка по сигналу пользователя")
    except Exception as e:
        logger.error("💥 Критическая ошибка: %s", str(e))

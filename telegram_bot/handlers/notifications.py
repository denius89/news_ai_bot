"""
Simplified notifications handler - только отправка уведомлений.
"""

import logging
from aiogram import Bot

logger = logging.getLogger("notifications")


async def send_notification(bot: Bot, user_id: int, message: str, parse_mode: str = "HTML"):
    """
    Send notification to user.

    Args:
        bot: Aiogram Bot instance
        user_id: Telegram user ID
        message: Message text to send
        parse_mode: Message parse mode (HTML by default)
    """
    try:
        await bot.send_message(chat_id=user_id, text=message, parse_mode=parse_mode)
        logger.info(f"✅ Notification sent to user {user_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send notification to user {user_id}: {e}")
        return False

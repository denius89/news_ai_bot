#!/usr/bin/env python3
"""
Тестовый скрипт для проверки отправки уведомлений через Telegram-бот.

Этот скрипт создает тестовое уведомление и отправляет его пользователю через бот.
"""

import asyncio
import logging
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.notification_delivery_service import notification_delivery_service
from database.db_models import get_user_notifications

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_telegram_notifications():
    """Тестирует отправку уведомлений через Telegram-бот."""
    
    # Тестовый пользователь (замените на реальный Telegram user ID)
    test_user_id = 1  # Замените на реальный user_id
    
    logger.info("🧪 Начинаем тестирование Telegram уведомлений...")
    
    try:
        # 1. Создаем и отправляем тестовое уведомление
        logger.info("📝 Создаем и отправляем тестовое уведомление...")
        
        notification_id = await notification_delivery_service.send_notification(
            user_id=test_user_id,
            title="🧪 Тестовое уведомление",
            content="Это тестовое уведомление для проверки работы Telegram-бота. "
                   "Если вы видите это сообщение, значит интеграция работает корректно!",
            category="test",
            via_telegram=True,
            via_webapp=True
        )
        
        if not notification_id:
            logger.error("❌ Не удалось создать и отправить тестовое уведомление")
            return False
            
        logger.info(f"✅ Тестовое уведомление создано и отправлено с ID: {notification_id}")
        
        # 2. Проверяем, что уведомление появилось в базе данных
        logger.info("🔍 Проверяем уведомления в базе данных...")
        
        notifications = await get_user_notifications(user_id=test_user_id)
        
        if notifications:
            logger.info(f"✅ Найдено {len(notifications)} уведомлений для пользователя {test_user_id}")
            
            # Ищем наше тестовое уведомление
            test_notification = None
            for notification in notifications:
                if notification.get("id") == notification_id:
                    test_notification = notification
                    break
            
            if test_notification:
                logger.info(f"✅ Тестовое уведомление найдено в базе данных:")
                logger.info(f"   - ID: {test_notification.get('id')}")
                logger.info(f"   - Заголовок: {test_notification.get('title')}")
                logger.info(f"   - Прочитано: {test_notification.get('read')}")
                logger.info(f"   - Via Telegram: {test_notification.get('via_telegram')}")
            else:
                logger.warning("⚠️ Тестовое уведомление не найдено в базе данных")
        else:
            logger.warning("⚠️ Уведомления для пользователя не найдены")
        
        logger.info("🎉 Тестирование завершено успешно!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка во время тестирования: {e}")
        return False
    
    finally:
        # Закрываем сессию бота
        from services.telegram_notification_service import telegram_notification_service
        await telegram_notification_service.close()


async def main():
    """Главная функция."""
    print("🚀 Запуск тестирования Telegram уведомлений...")
    print("=" * 50)
    
    success = await test_telegram_notifications()
    
    print("=" * 50)
    if success:
        print("✅ Тестирование завершено успешно!")
    else:
        print("❌ Тестирование завершилось с ошибками!")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())

"""
Сервис доставки уведомлений.

Этот модуль объединяет создание уведомлений в базе данных и их доставку
через различные каналы (Telegram, WebApp).
"""

import logging
from typing import Optional
from database.db_models import create_user_notification
# from database.db_models import get_user_notifications  # TODO: implement
from services.telegram_notification_service import telegram_notification_service

logger = logging.getLogger(__name__)


class NotificationDeliveryService:
    """Сервис для создания и доставки уведомлений."""

    async def send_notification(
        self,
        user_id: int,
        title: str,
        content: str,
        category: str = "general",
        via_telegram: bool = False,
        via_webapp: bool = True,
    ) -> Optional[str]:
        """
        Создает уведомление и доставляет его через указанные каналы.

        Args:
            user_id: ID пользователя
            title: Заголовок уведомления
            content: Содержимое уведомления
            category: Категория уведомления
            via_telegram: Отправлять ли через Telegram
            via_webapp: Показывать ли в WebApp

        Returns:
            ID созданного уведомления или None в случае ошибки
        """
        try:
            # 1. Создаем уведомление в базе данных
            notification_id = create_user_notification(
                user_id=user_id,
                title=title,
                content=content,
                category=category,
                read=False,
                via_telegram=via_telegram,
                via_webapp=via_webapp,
            )

            if not notification_id:
                logger.error(f"❌ Не удалось создать уведомление для user_id={user_id}")
                return None

            # 2. Отправляем через Telegram, если требуется
            if via_telegram:
                telegram_success = await telegram_notification_service.send_notification_via_bot(
                    user_id=user_id, title=title, text=content, notification_id=notification_id
                )

                if telegram_success:
                    logger.info(
                        f"✅ Уведомление {notification_id} отправлено через Telegram для user_id={user_id}"
                    )
                else:
                    logger.warning(
                        f"⚠️ Не удалось отправить уведомление {notification_id} через Telegram для user_id={user_id}"
                    )

            logger.info(
                f"✅ Уведомление {notification_id} создано и доставлено для user_id={user_id}"
            )
            return notification_id

        except Exception as e:
            logger.error(f"❌ Ошибка при создании и доставке уведомления: {e}")
            return None

    async def send_bulk_notification(
        self,
        user_ids: list[int],
        title: str,
        content: str,
        category: str = "general",
        via_telegram: bool = False,
        via_webapp: bool = True,
    ) -> dict[str, int]:
        """
        Отправляет уведомление нескольким пользователям.

        Args:
            user_ids: Список ID пользователей
            title: Заголовок уведомления
            content: Содержимое уведомления
            category: Категория уведомления
            via_telegram: Отправлять ли через Telegram
            via_webapp: Показывать ли в WebApp

        Returns:
            Словарь с результатами: {"success": count, "failed": count}
        """
        results = {"success": 0, "failed": 0}

        for user_id in user_ids:
            notification_id = await self.send_notification(
                user_id=user_id,
                title=title,
                content=content,
                category=category,
                via_telegram=via_telegram,
                via_webapp=via_webapp,
            )

            if notification_id:
                results["success"] += 1
            else:
                results["failed"] += 1

        logger.info(
            f"📊 Массовая отправка завершена: успешно={results['success']}, ошибок={results['failed']}"
        )
        return results


# Глобальный экземпляр сервиса
notification_delivery_service = NotificationDeliveryService()

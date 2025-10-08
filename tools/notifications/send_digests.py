"""
Daily Digests Sender - автоматическая отправка ежедневных дайджестов.

Этот инструмент запускается по расписанию (cron) и отправляет
персонализированные дайджесты пользователям Telegram бота.

Архитектура:
- Использует asyncio для параллельной рассылки
- Логирование через logging
- Настройки из .env (TELEGRAM_BOT_TOKEN, SUPABASE_URL, SUPABASE_KEY)
"""

import asyncio
import logging
import os
import sys
import zoneinfo
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv

from config.core.constants import CATEGORIES
from database.db_models import get_latest_news
from digests.ai_service import DigestAIService, DigestConfig
from models.news import NewsItem
from services.notification_service import NotificationService
from services.subscription_service import SubscriptionService
from utils.network.telegram_sender import TelegramSender

# Добавляем корневую директорию в PYTHONPATH для импортов
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Загружаем переменные окружения
load_dotenv(Path(__file__).resolve().parent.parent / "config_files" / ".env")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


async def get_current_hour_warsaw() -> int:
    """
    Получить текущий час в часовом поясе Europe/Warsaw.

    Returns:
        Текущий час (0-23)
    """
    try:
        warsaw_tz = zoneinfo.ZoneInfo("Europe/Warsaw")
        now_warsaw = datetime.now(warsaw_tz)
        return now_warsaw.hour
    except Exception as e:
        logger.warning(f"⚠️ Ошибка получения времени Warsaw, используем UTC: {e}")
        return datetime.now().hour


async def get_users_for_digest(notif_svc: NotificationService, target_hour: int) -> List[Dict]:
    """
    Получить список пользователей, которым нужно отправить дайджест.

    Args:
        notif_svc: Сервис уведомлений
        target_hour: Целевой час для отправки

    Returns:
        Список пользователей с включенными дайджестами на указанный час
    """
    logger.info(f"🔍 Поиск пользователей для часа {target_hour}")

    try:
        # Получаем пользователей с включенными дайджестами на указанный час
        users = await notif_svc.get_users_by_notification_type("digest", target_hour)

        logger.info(f"👥 Найдено {len(users)} пользователей для уведомления")
        return users

    except Exception as e:
        logger.error(f"❌ Ошибка получения пользователей: {e}")
        return []


async def get_user_subscriptions(subs_svc: SubscriptionService, user_id: str) -> List[str]:
    """
    Получить список категорий подписок пользователя.

    Args:
        subs_svc: Сервис подписок
        user_id: ID пользователя

    Returns:
        Список категорий подписок
    """
    try:
        subscriptions = await subs_svc.list(user_id)
        categories = [sub["category"] for sub in subscriptions]

        # Валидируем категории
        valid_categories = [cat for cat in categories if cat in CATEGORIES]

        if len(valid_categories) != len(categories):
            invalid = set(categories) - set(valid_categories)
            logger.warning(f"⚠️ Невалидные категории для пользователя {user_id}: {invalid}")

        return valid_categories

    except Exception as e:
        logger.error(f"❌ Ошибка получения подписок для пользователя {user_id}: {e}")
        return []


async def fetch_news_by_categories(categories: List[str], limit: int = 10) -> List[NewsItem]:
    """
    Получить свежие новости по указанным категориям.

    Args:
        categories: Список категорий для фильтрации
        limit: Максимальное количество новостей

    Returns:
        Список объектов NewsItem
    """
    try:
        logger.info(f"📰 Получение новостей по категориям: {categories}")

        # Получаем все последние новости
        news_data = get_latest_news(limit=limit * 2)  # Берем больше, чтобы отфильтровать

        if not news_data:
            logger.info("ℹ️ Новостей в базе данных нет")
            return []

        # Фильтруем по категориям
        filtered_news = []
        for row in news_data:
            news_item = NewsItem.model_validate(row)
            if news_item.category in categories:
                filtered_news.append(news_item)
                if len(filtered_news) >= limit:
                    break

        logger.info("📊 Получено %d новостей по категориям %s", len(filtered_news), categories)
        return filtered_news

    except Exception as e:
        logger.error(f"❌ Ошибка получения новостей: {e}")
        return []


async def generate_personalized_digest(
    news_items: List[NewsItem], user_categories: List[str], style: str = "analytical"
) -> str:
    """
    Сгенерировать персонализированный дайджест для пользователя.

    Args:
        news_items: Список новостей
        user_categories: Категории подписок пользователя
        style: Стиль дайджеста

    Returns:
        Текст дайджеста
    """
    try:
        if not news_items:
            return (
                f"📰 **Дайджест новостей**\n\n"
                f"По вашим подпискам ({', '.join(user_categories)}) "
                f"новостей сегодня нет.\n\n"
                f"Добавьте новые категории: /subscribe <category>\n"
                f"Доступные: {', '.join(CATEGORIES)}"
            )

        # Создаем AI сервис для генерации дайджеста
        config = DigestConfig(max_items=min(8, len(news_items)), include_fallback=True, style=style)

        service = DigestAIService(config)
        digest_text = await service.build_digest(news_items, style)

        # Добавляем заголовок с категориями пользователя
        header = f"📰 **Дайджест по категориям: {', '.join(user_categories)}**\n\n"
        return header + digest_text

    except Exception as e:
        logger.error(f"❌ Ошибка генерации дайджеста: {e}")
        # Fallback - простой список новостей
        fallback_text = "📰 **Дайджест новостей**\n\n"
        fallback_text += f"По категориям: {', '.join(user_categories)}\n\n"

        for i, item in enumerate(news_items[:8], 1):
            fallback_text += f"{i}. **{item.title}**\n"
            if item.link:
                fallback_text += f"   🔗 {item.link}\n"
            fallback_text += "\n"

        return fallback_text


async def send_personalized_digest(user: Dict, subs_svc: SubscriptionService, telegram_sender: TelegramSender) -> bool:
    """
    Отправить персонализированный дайджест пользователю.

    Args:
        user: Данные пользователя
        subs_svc: Сервис подписок
        telegram_sender: Отправитель Telegram

    Returns:
        True если дайджест отправлен успешно, False иначе
    """
    user_id = user["user_id"]
    telegram_id = user["telegram_id"]

    logger.info(f"📰 Генерация дайджеста для пользователя {telegram_id}")

    try:
        # 1. Получить подписки пользователя
        categories = await get_user_subscriptions(subs_svc, user_id)

        if not categories:
            logger.info(f"ℹ️ У пользователя {telegram_id} нет активных подписок")
            # Отправляем сообщение с предложением подписаться
            message = (
                f"👋 Привет!\n\n"
                f"У вас пока нет активных подписок на новости.\n\n"
                f"Добавьте подписку: /subscribe <category>\n"
                f"Доступные категории: {', '.join(CATEGORIES)}\n\n"
                f"Например: /subscribe crypto"
            )

            return await telegram_sender.send_message(telegram_id, message)

        # 2. Получить новости по категориям
        news_items = await fetch_news_by_categories(categories, limit=10)

        # 3. Сгенерировать дайджест
        digest_text = await generate_personalized_digest(news_items, categories)

        # 4. Отправить в Telegram
        success = await telegram_sender.send_message(telegram_id, digest_text)

        if success:
            logger.info(f"✅ Дайджест отправлен пользователю {telegram_id}")
        else:
            logger.error(f"❌ Не удалось отправить дайджест пользователю {telegram_id}")

        return success

    except Exception as e:
        logger.error(f"❌ Ошибка отправки дайджеста пользователю {telegram_id}: {e}")
        return False


async def main():
    """Основная функция для отправки ежедневных дайджестов."""
    logger.info("🚀 Запуск отправки ежедневных дайджестов")

    # Проверяем наличие необходимых переменных окружения
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        return

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL или SUPABASE_KEY не найдены в переменных окружения")
        return

    # Инициализируем сервисы
    subs_svc = SubscriptionService()
    notif_svc = NotificationService()
    telegram_sender = TelegramSender(bot_token)

    try:
        # 1. Получить текущий час в Warsaw
        current_hour = await get_current_hour_warsaw()
        logger.info(f"⏰ Текущий час (Europe/Warsaw): {current_hour}")

        # 2. Получить пользователей для уведомления
        users_to_notify = await get_users_for_digest(notif_svc, current_hour)
        logger.info(f"👥 Найдено пользователей для уведомления: {len(users_to_notify)}")

        if not users_to_notify:
            logger.info("ℹ️ Нет пользователей для отправки дайджестов")
            return

        # 3. Отправить дайджесты (с ограничением параллелизма)
        semaphore = asyncio.Semaphore(5)  # Максимум 5 одновременных отправок

        async def send_to_user(user):
            async with semaphore:
                return await send_personalized_digest(user, subs_svc, telegram_sender)

        # Запускаем параллельную отправку
        results = await asyncio.gather(*[send_to_user(user) for user in users_to_notify], return_exceptions=True)

        # Подсчитываем результаты
        sent_count = sum(1 for result in results if result is True)
        failed_count = len(results) - sent_count

        logger.info("📊 Результат рассылки:")
        logger.info(f"   ✅ Успешно отправлено: {sent_count}")
        logger.info(f"   ❌ Ошибок: {failed_count}")
        logger.info(f"   📈 Всего пользователей: {len(users_to_notify)}")

        # Логируем ошибки
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                user_id = users_to_notify[i]["telegram_id"]
                logger.error(f"❌ Исключение для пользователя {user_id}: {result}")

    except Exception as e:
        logger.error(f"💥 Критическая ошибка в main(): {e}")
        raise
    finally:
        # Закрываем HTTP клиент
        await telegram_sender.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Остановка по сигналу пользователя")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        sys.exit(1)

"""
Test script for daily digests sender.

This script tests the daily digest functionality without actually sending messages.
"""

import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from tools.send_daily_digests import (
    get_current_hour_warsaw,
    get_user_subscriptions,
    fetch_news_by_categories,
    generate_personalized_digest,
)
from services.subscription_service import SubscriptionService
from services.notification_service import NotificationService

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_daily_digests():
    """Test the daily digest functionality."""
    logger.info("🧪 Тестирование функций daily digest sender")

    # Test 1: Get current hour
    hour = await get_current_hour_warsaw()
    logger.info(f"⏰ Текущий час: {hour}")

    # Test 2: Test notification service
    notif_svc = NotificationService()
    users = await notif_svc.get_users_by_notification_type("digest", hour)
    logger.info(f"👥 Пользователи для уведомления: {len(users)}")

    # Test 3: Test subscription service (with dummy user)
    subs_svc = SubscriptionService()
    test_user_id = "test-user-123"
    categories = await get_user_subscriptions(subs_svc, test_user_id)
    logger.info(f"📋 Категории для тестового пользователя: {categories}")

    # Test 4: Fetch news by categories
    test_categories = ["crypto", "economy"]
    news_items = await fetch_news_by_categories(test_categories, limit=5)
    logger.info(f"📰 Получено новостей: {len(news_items)}")

    # Test 5: Generate personalized digest
    if news_items:
        digest_text = await generate_personalized_digest(news_items, test_categories)
        logger.info(f"📝 Сгенерирован дайджест длиной {len(digest_text)} символов")
        logger.info(f"📄 Превью дайджеста:\n{digest_text[:200]}...")
    else:
        logger.info("ℹ️ Новостей нет, тестируем fallback дайджест")
        digest_text = await generate_personalized_digest([], test_categories)
        logger.info(f"📝 Fallback дайджест:\n{digest_text}")

    logger.info("✅ Тестирование завершено")


if __name__ == "__main__":
    asyncio.run(test_daily_digests())

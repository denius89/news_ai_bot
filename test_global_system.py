#!/usr/bin/env python3
"""
Глобальный тест всей системы PulseAI.

Проверяет все компоненты после рефакторинга этапов 1-3.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from database.service import get_sync_service, get_async_service
from services.unified_digest_service import get_sync_digest_service, get_async_digest_service
from services.subscription_service import get_async_subscription_service
from services.notification_service import get_async_notification_service
from parsers.unified_parser import get_sync_parser, get_async_parser
from utils.cache import get_cache_manager, get_news_cache
from utils.http_client import get_http_client
from utils.standard_logging import PerformanceTimer, get_structured_logger
from config.settings import WEBAPP_URL, SUPABASE_URL

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("global_test")


async def test_database_layer():
    """Тест слоя базы данных."""
    logger.info("🔧 Тестирую слой базы данных...")
    
    try:
        # Тест синхронного сервиса
        sync_db = get_sync_service()
        news = sync_db.get_latest_news(limit=5)
        logger.info(f"✅ Sync DB: получено {len(news)} новостей")
        
        # Тест асинхронного сервиса
        async_db = get_async_service()
        async_news = await async_db.async_get_latest_news(limit=5)
        logger.info(f"✅ Async DB: получено {len(async_news)} новостей")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в слое БД: {e}")
        return False


async def test_services_layer():
    """Тест слоя сервисов."""
    logger.info("🔧 Тестирую слой сервисов...")
    
    try:
        # Тест сервиса дайджестов
        sync_digest = get_sync_digest_service()
        digest_text = sync_digest.build_daily_digest(limit=3)
        logger.info(f"✅ Digest Service: сгенерирован дайджест ({len(digest_text)} символов)")
        
        # Тест асинхронного сервиса дайджестов
        async_digest = get_async_digest_service()
        async_digest_text = await async_digest.async_build_daily_digest(limit=3)
        logger.info(f"✅ Async Digest Service: сгенерирован дайджест ({len(async_digest_text)} символов)")
        
        # Тест AI дайджеста
        ai_digest = sync_digest.build_ai_digest(category="crypto", style="analytical", limit=3)
        logger.info(f"✅ AI Digest: сгенерирован AI дайджест ({len(ai_digest)} символов)")
        
        # Тест сервиса подписок
        subscription_service = get_async_subscription_service()
        subscriptions = await subscription_service.get_user_subscriptions(1)
        logger.info(f"✅ Subscription Service: получены подписки {subscriptions}")
        
        # Тест сервиса уведомлений
        notification_service = get_async_notification_service()
        notifications = await notification_service.get_user_notifications(1, limit=5)
        logger.info(f"✅ Notification Service: получено {len(notifications)} уведомлений")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в слое сервисов: {e}")
        return False


async def test_parsers_layer():
    """Тест слоя парсеров."""
    logger.info("🔧 Тестирую слой парсеров...")
    
    try:
        # Тест синхронного парсера
        sync_parser = get_sync_parser()
        events = sync_parser.parse_events(days_ahead=1)
        logger.info(f"✅ Sync Parser: спарсено {len(events)} событий")
        
        # Тест асинхронного парсера
        async_parser = get_async_parser()
        # Тест парсинга одного источника
        news_items = await async_parser.parse_source_async(
            "https://feeds.feedburner.com/oreilly/radar",
            "tech", "ai", "O'Reilly Radar"
        )
        logger.info(f"✅ Async Parser: спарсено {len(news_items)} новостей")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в слое парсеров: {e}")
        return False


async def test_performance_optimizations():
    """Тест оптимизаций производительности."""
    logger.info("🔧 Тестирую оптимизации производительности...")
    
    try:
        # Тест кэширования
        cache_manager = get_cache_manager()
        news_cache = get_news_cache()
        
        # Тест кэша
        await news_cache.set("test_key", "test_value", ttl=60)
        cached_value = await news_cache.get("test_key")
        assert cached_value == "test_value"
        logger.info("✅ Cache: кэширование работает")
        
        # Тест HTTP клиента
        http_client = get_http_client()
        logger.info("✅ HTTP Client: клиент инициализирован")
        
        # Тест PerformanceTimer
        with PerformanceTimer("Test operation"):
            await asyncio.sleep(0.1)
        logger.info("✅ Performance Timer: мониторинг работает")
        
        # Тест структурированного логгера
        structured_logger = get_structured_logger("test")
        structured_logger.info("Test message", test_param="value")
        logger.info("✅ Structured Logger: логирование работает")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в оптимизациях: {e}")
        return False


async def test_telegram_integration():
    """Тест интеграции с Telegram."""
    logger.info("🔧 Тестирую интеграцию с Telegram...")
    
    try:
        # Тест импорта handlers
        from telegram_bot.handlers import routers
        logger.info(f"✅ Telegram Handlers: загружено {len(routers)} роутеров")
        
        # Тест импорта keyboards
        from telegram_bot.keyboards import back_inline_keyboard
        logger.info("✅ Telegram Keyboards: клавиатуры загружены")
        
        # Тест импорта bot
        from telegram_bot.bot import main
        logger.info("✅ Telegram Bot: бот модуль загружен")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в Telegram интеграции: {e}")
        return False


async def test_webapp_integration():
    """Тест интеграции с WebApp."""
    logger.info("🔧 Тестирую интеграцию с WebApp...")
    
    try:
        # Тест импорта routes
        from routes import webapp_routes, api_routes, news_routes
        logger.info("✅ WebApp Routes: маршруты загружены")
        
        # Тест импорта templates
        from pathlib import Path
        templates_dir = Path("templates")
        template_files = list(templates_dir.glob("*.html"))
        logger.info(f"✅ WebApp Templates: найдено {len(template_files)} шаблонов")
        
        # Тест импорта static files
        static_dir = Path("static")
        css_files = list(static_dir.glob("*.css"))
        js_files = list(static_dir.glob("js/*.js"))
        logger.info(f"✅ WebApp Static: {len(css_files)} CSS, {len(js_files)} JS файлов")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в WebApp интеграции: {e}")
        return False


async def test_configuration():
    """Тест конфигурации."""
    logger.info("🔧 Тестирую конфигурацию...")
    
    try:
        # Тест основных настроек
        if SUPABASE_URL:
            logger.info("✅ Supabase URL настроен")
        else:
            logger.warning("⚠️ Supabase URL не настроен")
            
        if WEBAPP_URL:
            logger.info(f"✅ WebApp URL: {WEBAPP_URL}")
        else:
            logger.warning("⚠️ WebApp URL не настроен")
        
        # Тест импорта sources
        from services.categories import get_categories
        categories = get_categories()
        logger.info(f"✅ Categories: загружено {len(categories)} категорий")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в конфигурации: {e}")
        return False


async def test_error_handling():
    """Тест обработки ошибок."""
    logger.info("🔧 Тестирую обработку ошибок...")
    
    try:
        # Тест обработки несуществующих данных
        sync_db = get_sync_service()
        empty_news = sync_db.get_latest_news(categories=["nonexistent"], limit=1)
        logger.info(f"✅ Error Handling: корректно обработана пустая выборка ({len(empty_news)} новостей)")
        
        # Тест обработки несуществующих пользователей
        subscription_service = get_async_subscription_service()
        empty_subscriptions = await subscription_service.get_user_subscriptions(999999)
        logger.info(f"✅ Error Handling: корректно обработаны пустые подписки ({empty_subscriptions})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в обработке ошибок: {e}")
        return False


async def main():
    """Основная функция глобального тестирования."""
    logger.info("🚀 НАЧИНАЮ ГЛОБАЛЬНЫЙ ТЕСТ СИСТЕМЫ PULSEAI")
    logger.info("=" * 70)
    
    results = []
    
    # Тест 1: Слой базы данных
    logger.info("\n📋 ТЕСТ 1: Слой базы данных")
    db_ok = await test_database_layer()
    results.append(("База данных", db_ok))
    
    # Тест 2: Слой сервисов
    logger.info("\n📋 ТЕСТ 2: Слой сервисов")
    services_ok = await test_services_layer()
    results.append(("Сервисы", services_ok))
    
    # Тест 3: Слой парсеров
    logger.info("\n📋 ТЕСТ 3: Слой парсеров")
    parsers_ok = await test_parsers_layer()
    results.append(("Парсеры", parsers_ok))
    
    # Тест 4: Оптимизации производительности
    logger.info("\n📋 ТЕСТ 4: Оптимизации производительности")
    perf_ok = await test_performance_optimizations()
    results.append(("Производительность", perf_ok))
    
    # Тест 5: Интеграция с Telegram
    logger.info("\n📋 ТЕСТ 5: Интеграция с Telegram")
    telegram_ok = await test_telegram_integration()
    results.append(("Telegram", telegram_ok))
    
    # Тест 6: Интеграция с WebApp
    logger.info("\n📋 ТЕСТ 6: Интеграция с WebApp")
    webapp_ok = await test_webapp_integration()
    results.append(("WebApp", webapp_ok))
    
    # Тест 7: Конфигурация
    logger.info("\n📋 ТЕСТ 7: Конфигурация")
    config_ok = await test_configuration()
    results.append(("Конфигурация", config_ok))
    
    # Тест 8: Обработка ошибок
    logger.info("\n📋 ТЕСТ 8: Обработка ошибок")
    error_ok = await test_error_handling()
    results.append(("Обработка ошибок", error_ok))
    
    # Итоговый отчет
    logger.info("\n" + "=" * 70)
    logger.info("📊 ИТОГОВЫЙ ОТЧЕТ ГЛОБАЛЬНОГО ТЕСТИРОВАНИЯ")
    logger.info("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 РЕЗУЛЬТАТ: {passed}/{total} тестов пройдено")
    
    if passed == total:
        logger.info("🎉 ВСЕ ГЛОБАЛЬНЫЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        logger.info("🚀 СИСТЕМА PULSEAI ГОТОВА К ПРОДАКШЕНУ!")
        return True
    else:
        logger.error(f"⚠️ ПРОВАЛЕНО {total - passed} ТЕСТОВ")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

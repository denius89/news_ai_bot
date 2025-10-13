#!/usr/bin/env python3
"""
Скрипт для загрузки свежих новостей из каждой подкатегории в PulseAI.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.categories import get_categories, get_subcategories
from database.service import get_async_service
from parsers.advanced_parser import AdvancedParser

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def load_fresh_news():
    """Загрузка свежих новостей из каждой подкатегории."""
    try:
        logger.info("📰 Начинаем загрузку свежих новостей")

        # Инициализируем AdvancedParser
        parser = AdvancedParser(max_concurrent=5, min_importance=0.3)

        # Получаем все категории и подкатегории
        categories = get_categories()
        total_subcategories = 0

        for category in categories:
            subcategories = get_subcategories(category)
            total_subcategories += len(subcategories)

        logger.info(f"Найдено {len(categories)} категорий и " f"{total_subcategories} подкатегорий")

        # Запускаем парсинг
        logger.info("🚀 Запускаем AdvancedParser для загрузки новостей")

        # Используем AdvancedParser как async context manager
        async with parser:
            await parser.run()

        # Получаем статистику после загрузки
        db_service = get_async_service()
        if not db_service:
            logger.error("❌ Async database service not available")
            return

        client = await db_service._get_async_client()
        if not client:
            logger.error("❌ Async client not available")
            return

        # Считаем новости по категориям
        category_stats = {}
        for category in categories:
            result = await db_service.async_safe_execute(
                client.table("news").select("id", count="exact").eq("category", category)
            )

            if result and hasattr(result, "data"):
                count = len(result.data) if result.data else 0
                category_stats[category] = count

        # Общая статистика
        total_result = await db_service.async_safe_execute(client.table("news").select("id", count="exact"))

        total_count = (
            len(total_result.data) if total_result and hasattr(total_result, "data") and total_result.data else 0
        )

        logger.info("📊 Статистика загруженных новостей:")
        logger.info(f"📈 Всего новостей в базе: {total_count}")

        for category, count in category_stats.items():
            logger.info(f"  • {category}: {count} новостей")

        # Проверяем корректность заполнения полей
        logger.info("🔍 Проверяем корректность заполнения полей")

        sample_result = await db_service.async_safe_execute(client.table("news").select("*").limit(5))

        if sample_result and hasattr(sample_result, "data") and sample_result.data:
            sample_news = sample_result.data[0]
            required_fields = [
                "id",
                "title",
                "content",
                "source",
                "published_at",
                "link",
                "credibility",
                "importance",
                "category",
                "subcategory",
                "uid",
            ]

            missing_fields = []
            for field in required_fields:
                if field not in sample_news or sample_news[field] is None:
                    missing_fields.append(field)

            if missing_fields:
                logger.warning(f"⚠️ Пропущенные поля в новостях: {missing_fields}")
            else:
                logger.info("✅ Все обязательные поля заполнены корректно")

            # Проверяем типы данных
            if isinstance(sample_news.get("credibility"), (int, float)) and isinstance(
                sample_news.get("importance"), (int, float)
            ):
                logger.info("✅ Поля credibility и importance имеют " "корректные числовые значения")
            else:
                logger.warning("⚠️ Поля credibility или importance имеют " "некорректные значения")

        logger.info("✅ Загрузка свежих новостей завершена успешно")

        return {
            "total_news": total_count,
            "category_stats": category_stats,
            "subcategories_processed": total_subcategories,
        }

    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке новостей: {e}")
        raise


async def main():
    """Основная функция."""
    result = await load_fresh_news()
    return result


if __name__ == "__main__":
    asyncio.run(main())

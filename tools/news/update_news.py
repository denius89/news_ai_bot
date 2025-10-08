#!/usr/bin/env python3
"""
Обновление новостей с использованием нового универсального RSS парсера.
"""

from database.service import get_async_service
from parsers.universal_rss_parser import UniversalRSSParser
import sys
from pathlib import Path
import logging
import asyncio
from datetime import datetime

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def update_news_with_universal_parser():
    """Обновляет новости с использованием нового универсального парсера."""

    print("🚀 Запуск обновления новостей с универсальным парсером...\n")

    # Инициализируем парсер
    parser = UniversalRSSParser()
    db_service = get_async_service()

    try:
        # Получаем все источники и парсим их
        print("📰 Парсинг всех источников...")
        all_news = parser.fetch_all_sources(per_source_limit=10)  # Лимит 10 новостей на источник

        if not all_news:
            print("❌ Не удалось получить новости")
            return

        print(f"✅ Получено {len(all_news)} новостей от парсера")

        # Сохраняем в базу данных
        print("💾 Сохранение новостей в базу данных...")

        saved_count = 0
        for news_item in all_news:
            try:
                # Добавляем AI анализ (пустые значения, будут заполнены позже)
                news_item["importance"] = 0.0
                news_item["credibility"] = 0.0

                # Сохраняем в базу
                await db_service.async_upsert_news([news_item])
                saved_count += 1

                if saved_count % 50 == 0:
                    print(f"   💾 Сохранено {saved_count} новостей...")

            except Exception as e:
                logger.warning(
                    f"Ошибка сохранения новости {news_item.get('title', 'Unknown')}: {e}")
                continue

        print(f"✅ Успешно сохранено {saved_count} новостей")

        # Статистика по категориям
        categories = {}
        for news_item in all_news:
            cat = news_item.get("category", "unknown")
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1

        print(f"\n📊 Статистика по категориям:")
        for cat, count in categories.items():
            print(f"   {cat}: {count} новостей")

        print(f"\n🎉 Обновление завершено успешно!")

    except Exception as e:
        logger.error(f"Ошибка при обновлении новостей: {e}")
        raise
    finally:
        parser.close()


if __name__ == "__main__":
    asyncio.run(update_news_with_universal_parser())

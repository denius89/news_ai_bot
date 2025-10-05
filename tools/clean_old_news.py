#!/usr/bin/env python3
"""
Скрипт для очистки старых новостей из базы данных PulseAI.
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.service import get_async_service

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def clean_old_news():
    """Удаление старых новостей из базы данных."""
    try:
        db_service = get_async_service()
        logger.info("🗑️ Начинаем очистку старых новостей")

        # Получаем текущую дату
        now = datetime.now()

        # Удаляем новости старше 30 дней
        cutoff_date = now - timedelta(days=30)

        logger.info(f"Удаляем новости старше {cutoff_date.strftime('%Y-%m-%d')}")

        # Выполняем удаление через Supabase
        client = await db_service.async_client
        result = await db_service.async_safe_execute(
            client.table('news').delete().lt('published_at', cutoff_date.isoformat())
        )

        if result:
            logger.info(f"✅ Успешно удалены старые новости")
        else:
            logger.warning("⚠️ Не удалось удалить новости или они уже были удалены")

        # Также очищаем дубликаты по title и link
        logger.info("🧹 Очищаем дубликаты новостей")

        # Получаем все новости для проверки дубликатов
        all_news = await db_service.async_safe_execute(
            client.table('news').select('id, title, link').order('published_at', desc=True)
        )

        if all_news and hasattr(all_news, 'data') and all_news.data:
            seen_titles = set()
            seen_links = set()
            duplicates_to_delete = []

            for news in all_news.data:
                title = news.get('title', '').lower().strip()
                link = news.get('link', '').strip()

                # Проверяем дубликаты по title и link
                if (title in seen_titles or link in seen_links) and title and link:
                    duplicates_to_delete.append(news['id'])
                else:
                    if title:
                        seen_titles.add(title)
                    if link:
                        seen_links.add(link)

            # Удаляем дубликаты
            if duplicates_to_delete:
                logger.info(f"Найдено {len(duplicates_to_delete)} дубликатов")

                for news_id in duplicates_to_delete:
                    await db_service.async_safe_execute(
                        client.table('news').delete().eq('id', news_id)
                    )

                logger.info(f"✅ Удалено {len(duplicates_to_delete)} дубликатов")
            else:
                logger.info("✅ Дубликаты не найдены")

        # Получаем статистику после очистки
        count_result = await db_service.async_safe_execute(
            client.table('news').select('id', count='exact')
        )

        if count_result and hasattr(count_result, 'data'):
            total_count = len(count_result.data) if count_result.data else 0
            logger.info(f"📊 Всего новостей в базе после очистки: {total_count}")

        logger.info("✅ Очистка старых новостей завершена успешно")

    except Exception as e:
        logger.error(f"❌ Ошибка при очистке новостей: {e}")
        raise


async def main():
    """Основная функция."""
    await clean_old_news()


if __name__ == "__main__":
    asyncio.run(main())

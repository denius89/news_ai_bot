"""
Асинхронный парсер RSS-источников для PulseAI.
"""

import asyncio
import hashlib
import logging
import sys
import aiohttp
import feedparser
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from dateutil import parser as dtp

sys.path.append(str(Path(__file__).parent.parent))

from utils.clean_text import clean_text  # noqa: E402
from services.categories import get_all_sources  # noqa: E402
from database.service import async_upsert_news, get_async_service  # noqa: E402

logger = logging.getLogger("parsers.async_rss")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0; +https://example.com)"}


def normalize_date(date_str: str | None):
    """Парсит дату, возвращает UTC datetime или None."""
    if not date_str:
        return None
    try:
        dt = dtp.parse(date_str)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception as e:
        logger.warning(f"Не удалось распарсить дату: {date_str} ({e})")
        return None


async def fetch_feed_async(session: aiohttp.ClientSession, url: str):
    """Асинхронно запрашивает RSS фид."""
    try:
        async with session.get(
            url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            content_type = response.headers.get('content-type', '').lower()

            # Проверяем, что это XML/RSS, а не HTML
            if 'xml' in content_type or 'rss' in content_type or 'atom' in content_type:
                content = await response.text()
                return feedparser.parse(content)
            else:
                logger.warning(f"Неверный content-type для {url}: {content_type}")
                return None

    except asyncio.TimeoutError:
        logger.warning(f"Таймаут при загрузке {url}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при загрузке {url}: {e}")
        return None


async def parse_source_async(
    session: aiohttp.ClientSession, url: str, category: str, subcategory: str, source_name: str
) -> List[Dict]:
    """Асинхронно парсит один RSS источник."""
    try:
        feed = await fetch_feed_async(session, url)
        if not feed or not feed.entries:
            logger.warning(f"Пустой фид: {source_name} ({url})")
            return []

        news_items = []
        for entry in feed.entries:
            try:
                # Очистка текста
                title = clean_text(entry.get("title", ""))
                content = clean_text(entry.get("summary", ""))

                if not title:
                    continue

                # Парсинг даты
                published_at = normalize_date(entry.get("published", entry.get("updated")))
                if not published_at:
                    published_at = normalize_date(str(entry.get("published_parsed")))

                # Создание уникального ID
                uid = hashlib.md5(f"{entry.get('link', '')}{title}".encode()).hexdigest()

                news_item = {
                    "uid": uid,
                    "title": title,
                    "content": content,
                    "link": entry.get("link", ""),
                    "source": source_name,
                    "category": category,
                    "subcategory": subcategory,
                    "published_at": published_at.isoformat() if published_at else None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }

                news_items.append(news_item)

            except Exception as e:
                logger.warning(f"Ошибка парсинга записи из {source_name}: {e}")
                continue

        logger.info(f"✅ Async парсинг {source_name}: {len(news_items)} новостей")
        return news_items

    except Exception as e:
        logger.error(f"❌ Ошибка async парсинга источника {source_name}: {e}")
        return []


async def parse_all_sources_async(per_source_limit: Optional[int] = None) -> List[Dict]:
    """Асинхронно парсит все RSS источники параллельно."""
    all_sources = get_all_sources()

    if not all_sources:
        logger.warning("Нет источников для парсинга")
        return []

    logger.info(f"🔄 Async парсинг {len(all_sources)} источников...")

    # Создаем HTTP сессию
    async with aiohttp.ClientSession() as session:
        # Создаем задачи для параллельного выполнения
        tasks = []
        for cat, subcat, name, url in all_sources:
            task = parse_source_async(session, url, cat, subcat, name)
            tasks.append(task)

        # Выполняем все задачи параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Собираем результаты
        all_news = []
        seen = set()

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Ошибка в задаче {i}: {result}")
                continue

            # Применяем лимит если указан
            if per_source_limit and len(result) > per_source_limit:
                result = result[:per_source_limit]

            # Добавляем уникальные элементы
            for item in result:
                uid = item["uid"]
                if uid not in seen:
                    seen.add(uid)
                    all_news.append(item)

    logger.info(f"✅ Async парсинг завершен: {len(all_news)} уникальных новостей")
    return all_news


async def async_parse_and_save():
    """Асинхронно парсит новости и сохраняет их в базу данных."""
    # Инициализируем подключение к БД
    async_service = get_async_service()
    await async_service._init_async_client()
    if not async_service.async_client:
        logger.error("Не удалось инициализировать Async Supabase")
        return 0

    # Парсим новости
    news_items = await parse_all_sources_async(per_source_limit=5)

    if not news_items:
        logger.warning("Нет новостей для сохранения")
        return 0

    # Сохраняем в базу данных
    saved_count = await async_upsert_news(news_items)

    logger.info(f"🎉 Async парсинг и сохранение завершены: {saved_count} новостей")
    return saved_count


async def compare_sync_vs_async():
    """Сравнивает производительность синхронного и асинхронного парсинга."""
    import time

    # Тест асинхронного парсинга
    logger.info("🔄 Тестируем асинхронный парсинг...")
    start_time = time.time()
    async_news = await parse_all_sources_async(per_source_limit=3)
    async_time = time.time() - start_time

    logger.info("📊 Результаты асинхронного парсинга:")
    logger.info(f"  Async: {len(async_news)} новостей за {async_time:.2f}с")


if __name__ == "__main__":

    async def main():
        # Тест асинхронного парсинга
        await async_parse_and_save()

        # Сравнение производительности
        await compare_sync_vs_async()

    asyncio.run(main())

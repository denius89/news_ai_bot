"""
Асинхронные модели базы данных для PulseAI.
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pathlib import Path
import sys

from dotenv import load_dotenv
from supabase import create_async_client, AsyncClient

sys.path.append(str(Path(__file__).parent.parent))

from utils.dates import format_datetime  # noqa: E402

# --- ЛОГИРОВАНИЕ ---
logger = logging.getLogger("database.async")

# --- ПОДКЛЮЧЕНИЕ К SUPABASE ---
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async_supabase: Optional[AsyncClient] = None


async def init_async_supabase():
    """Инициализирует асинхронный клиент Supabase."""
    global async_supabase
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            # Закрываем существующий клиент если есть
            if async_supabase:
                await async_supabase.aclose()
                async_supabase = None

            # Создаем новый клиент
            async_supabase = await create_async_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✅ Async Supabase client initialized (fresh)")
            return True
        except Exception as e:
            logger.error("❌ Ошибка инициализации Async Supabase: %s", e)
            return False
    else:
        logger.warning(
            "⚠️ Async Supabase не инициализирован (нет ключей). Unit-тесты будут выполняться без БД."
        )
        return False


# --- ASYNC SAFE EXECUTE ---
async def async_safe_execute(query, retries: int = 3, delay: int = 2):
    """
    Асинхронно выполняет запрос с ретраями при сетевых ошибках.
    """
    for attempt in range(1, retries + 1):
        try:
            return await query.execute()
        except Exception as e:
            logger.warning("⚠️ Попытка %s/%s: ошибка соединения %s", attempt, retries, e)
            if attempt < retries:
                await asyncio.sleep(delay)
            else:
                raise e


# --- АСИНХРОННЫЕ ФУНКЦИИ ДЛЯ НОВОСТЕЙ ---
async def async_get_latest_news(
    source: Optional[str] = None,
    categories: Optional[List[str]] = None,
    limit: int = 10,
) -> List[Dict]:
    """Асинхронно получает последние новости."""
    if not async_supabase:
        logger.warning("⚠️ Async Supabase не подключён, async_get_latest_news не работает.")
        return []

    logger.debug(
        "async_get_latest_news: source=%s, categories=%s, limit=%s", source, categories, limit
    )

    query = (
        async_supabase.table("news")
        .select(
            "id, uid, title, content, link, published_at, source, category, subcategory, credibility, importance"
        )
        .order("published_at", desc=True)
        .limit(limit)
    )

    if source:
        query = query.eq("source", source)

    if categories:
        query = query.in_("category", categories)

    try:
        result = await async_safe_execute(query)
        return result.data or []
    except Exception as e:
        logger.error("❌ Ошибка получения новостей: %s", e)
        return []


async def async_insert_news_batch(news_items: List[Dict]) -> int:
    """Асинхронно вставляет пакет новостей в базу данных."""
    if not news_items:
        return 0

    try:
        # Используем только существующие колонки (без created_at и published_at_fmt)
        # Эти поля будут добавлены автоматически базой данных
        clean_items = []
        for item in news_items:
            clean_item = {
                "uid": item.get("uid"),
                "title": item.get("title"),
                "content": item.get("content"),
                "link": item.get("link"),
                "source": item.get("source"),
                "category": item.get("category"),
                "subcategory": item.get("subcategory"),
                "published_at": item.get("published_at"),
            }
            clean_items.append(clean_item)

        # Используем синхронный клиент для вставки
        from database.db_models import supabase, safe_execute

        if not supabase:
            logger.warning("⚠️ Синхронный Supabase не подключён")
            return 0

        safe_execute(supabase.table("news").upsert(clean_items, on_conflict="uid"))

        inserted_count = len(clean_items)
        logger.info("✅ Async: вставлено %s новостей", inserted_count)
        return inserted_count

    except Exception as e:
        logger.error("❌ Ошибка async_insert_news_batch: %s", e)
        return 0


async def async_get_news_count(categories: Optional[List[str]] = None) -> int:
    """Асинхронно получает количество новостей."""
    if not async_supabase:
        return 0

    try:
        query = async_supabase.table("news").select("id", count="exact")

        if categories:
            query = query.in_("category", categories)

        result = await async_safe_execute(query)
        return result.count or 0
    except Exception as e:
        logger.error("❌ Ошибка async_get_news_count: %s", e)
        return 0


# --- АСИНХРОННЫЕ ФУНКЦИИ ДЛЯ СОБЫТИЙ ---
async def async_get_latest_events(limit: int = 50) -> List[Dict]:
    """Асинхронно получает последние события."""
    if not async_supabase:
        logger.warning("⚠️ Async Supabase не подключён, async_get_latest_events не работает.")
        return []

    try:
        result = await async_safe_execute(
            async_supabase.table("events").select("*").order("event_time", desc=True).limit(limit)
        )

        events = result.data or []

        # Форматируем даты
        for event in events:
            if event.get("event_time"):
                event["event_time_fmt"] = format_datetime(event["event_time"])

        return events

    except Exception as e:
        logger.error("❌ Ошибка async_get_latest_events: %s", e)
        return []


# --- АСИНХРОННЫЕ ФУНКЦИИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ---
async def async_get_user_subscriptions(user_id: int) -> Dict:
    """Асинхронно получает подписки пользователя."""
    if not async_supabase:
        return {"categories": [], "sources": []}

    try:
        result = await async_safe_execute(
            async_supabase.table("users").select("categories, sources").eq("id", user_id).single()
        )

        if result.data:
            return {
                "categories": result.data.get("categories", []),
                "sources": result.data.get("sources", []),
            }
        else:
            return {"categories": [], "sources": []}

    except Exception as e:
        logger.error("❌ Ошибка async_get_user_subscriptions: %s", e)
        return {"categories": [], "sources": []}


async def async_update_user_subscriptions(
    user_id: int, categories: List[str], sources: List[str]
) -> bool:
    """Асинхронно обновляет подписки пользователя."""
    if not async_supabase:
        return False

    try:
        await async_safe_execute(
            async_supabase.table("users").upsert(
                {
                    "id": user_id,
                    "categories": categories,
                    "sources": sources,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        )

        logger.info("✅ Async: обновлены подписки пользователя %s", user_id)
        return True

    except Exception as e:
        logger.error("❌ Ошибка async_update_user_subscriptions: %s", e)
        return False


# --- ТЕСТИРОВАНИЕ ---
async def test_async_connection():
    """Тестирует асинхронное подключение к базе данных."""
    if not async_supabase:
        print("❌ Async Supabase не инициализирован")
        return False

    try:
        # Простой запрос для проверки подключения
        result = await async_safe_execute(async_supabase.table("news").select("id").limit(1))
        print(f"✅ Async подключение работает: {len(result.data)} записей")
        return True
    except Exception as e:
        print(f"❌ Async подключение не работает: {e}")
        return False


if __name__ == "__main__":
    # Тест асинхронного подключения
    async def main():
        # Инициализируем подключение
        if not await init_async_supabase():
            print("❌ Не удалось инициализировать Async Supabase")
            return

        await test_async_connection()

        # Тест получения новостей
        news = await async_get_latest_news(limit=3)
        print(f"📰 Получено {len(news)} новостей асинхронно")

        # Тест получения событий
        events = await async_get_latest_events(limit=3)
        print(f"📅 Получено {len(events)} событий асинхронно")

    asyncio.run(main())

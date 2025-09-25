#!/usr/bin/env python3
"""
Скрипт для парсинга новостей из RSS и сохранения их в базу Supabase.
"""

import logging

from parsers.rss_parser import load_sources, fetch_rss
from database.db_models import upsert_news

logger = logging.getLogger("tools.fetch_and_store_news")


def main(limit: int | None = None):
    logger.info("🔄 Загружаем источники...")
    sources = load_sources()

    all_items = []
    for src in sources.values():  # ✅ берём словари, а не ключи
        try:
            # fetch_rss ждёт dict[str, dict], поэтому оборачиваем один источник
            items = fetch_rss({src["name"]: src}, per_source_limit=limit)
            all_items.extend(items)
            logger.info(f"✅ {src['id']}: {len(items)} новостей")
        except Exception as e:
            logger.error(f"Ошибка при парсинге {src.get('id', src.get('name'))}: {e}")

    if not all_items:
        logger.warning("⚠️ Нет новостей для вставки")
        return

    # 🧹 Убираем дубли по uid
    unique_items = {item["uid"]: item for item in all_items}
    deduped_items = list(unique_items.values())

    logger.info(f"📦 После дедупа: {len(deduped_items)} новостей (из {len(all_items)})")

    upsert_news(deduped_items)


if __name__ == "__main__":
    main()

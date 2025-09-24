#!/usr/bin/env python3

"""
Скрипт для парсинга экономических событий и сохранения их в Supabase.
"""

import logging

from parsers.events_parser import fetch_investing_events
from database.db_models import upsert_events

logger = logging.getLogger("tools.fetch_and_store_events")


def main():
    logger.info("🔄 Загружаем события с Investing...")
    try:
        events = fetch_investing_events()
        if not events:
            logger.warning("⚠️ Нет событий для вставки")
            return
        upsert_events(events)
        logger.info(f"✅ Вставлено {len(events)} событий")
    except Exception as e:
        logger.error(f"Ошибка при парсинге событий: {e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Скрипт для парсинга экономических событий (Investing) и сохранения их в Supabase.
"""

import logging
import argparse

from parsers.events_parser import fetch_investing_events
from database.db_models import upsert_events

logger = logging.getLogger("tools.fetch_and_store_events")


def main():
    parser = argparse.ArgumentParser(description="Fetch and store Investing events")
    parser.add_argument(
        "--limit-days", type=int, default=2, help="Сколько дней загружать (по умолчанию 2)"
    )
    args = parser.parse_args()

    logger.info(f"🔄 Загружаем события с Investing (days={args.limit_days})...")
    try:
        events = fetch_investing_events(limit_days=args.limit_days)
        if not events:
            logger.warning("⚠️ Нет событий для вставки")
            return
        upsert_events(events)
        logger.info(f"✅ Вставлено {len(events)} событий в БД")
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге событий: {e}", exc_info=True)


if __name__ == "__main__":
    main()

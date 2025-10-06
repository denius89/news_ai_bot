"""
main.py — минимальный ETL + генерация дайджеста + загрузка событий.
RSS -> (AI-заглушки считаются внутри upsert) -> Supabase.
Events -> парсинг (Investing.com / API) -> Supabase.

Запуск ETL:
  python main.py --limit 30        # взять до 30 новостей
  python main.py --source crypto   # выбрать предустановленные источники
  python main.py --source all --limit 50  # все источники, но только 50 новостей

Запуск дайджеста:
  python main.py --digest 5        # дайджест из 5 новостей

Загрузка событий:
  python main.py --events          # загрузить экономические события
"""

import argparse
import logging

from database.db_models import upsert_event, upsert_news
from digests.generator import generate_digest
from parsers.events_parser import fetch_investing_events
from parsers.rss_parser import parse_source, get_sync_parser
from utils.logging_setup import setup_logging


def main():
    # --- ЛОГИРОВАНИЕ ---
    setup_logging()
    logger = logging.getLogger("news_ai_bot")

    parser = argparse.ArgumentParser(description="News AI Bot - ETL Pipeline")
    parser.add_argument("--source", type=str, default="all", help="Категория из sources.yaml или 'all'")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--digest",
        type=int,
        nargs="?",
        const=5,
        help="Сформировать дайджест (по умолчанию 5 новостей)",
    )
    parser.add_argument("--ai", action="store_true", help="Использовать AI для генерации дайджеста")
    parser.add_argument("--events", action="store_true", help="Загрузить экономические события")
    args = parser.parse_args()

    # --- Дайджест ---
    if args.digest is not None:
        logger.info(f"Генерация {'AI-' if args.ai else ''}дайджеста " f"(последние {args.digest} новостей)...")
        digest = generate_digest(limit=args.digest, ai=args.ai)
        print("\n" + digest + "\n")
        return

    # --- События ---
    if args.events:
        logger.info("Загружаем экономические события с Investing.com...")
        events = fetch_investing_events(limit_days=2)
        logger.info(f"Получено {len(events)} событий")

        for ev in events:
            upsert_event(ev)

        logger.info("✅ События сохранены")
        return

    # --- Новости (ETL) ---
    if args.source == "all":
        from services.categories import get_all_sources
        sources = get_all_sources()
    else:
        from services.categories import get_sources_by_category
        sources = get_sources_by_category(args.source)

    logger.info(f"Загружаем новости из {len(sources)} источников ({args.source})...")
    logger.info("Используемые источники:")
    for src in sources:
        logger.info(f"  {src['name']} ({src['category']}): {src['url']}")

    items = fetch_rss(sources)

    if args.limit and len(items) > args.limit:
        items = items[: args.limit]
        logger.info(f"Ограничение: берём только {args.limit} новостей")

    logger.info(f"Получено {len(items)} новостей. Записываем в базу...")
    upsert_news(items)

    logger.info("Готово ✅")


if __name__ == "__main__":
    main()

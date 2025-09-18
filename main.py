"""
main.py — минимальный ETL:
RSS -> (AI-заглушки считаются внутри upsert) -> Supabase.
Запуск:
  python main.py --limit 30       # взять до 30 новостей
  python main.py --source crypto  # выбрать предустановленные источники
"""

import argparse
import logging
from parsers.rss_parser import fetch_rss
from database.db_models import upsert_news

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

SOURCES = {
    "crypto": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://news.bitcoin.com/feed/"
    ],
    "economy": [
        "https://news.yahoo.com/rss/",
        "https://www.ft.com/?format=rss"
    ]
}

def main():
    parser = argparse.ArgumentParser(description="News AI Bot - ETL Pipeline")
    parser.add_argument("--source", choices=["crypto", "economy", "all"], default="all")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    urls = []
    if args.source == "all":
        for v in SOURCES.values():
            urls.extend(v)
    else:
        urls = SOURCES[args.source]

    logging.info(f"Загружаем новости из {len(urls)} источников ({args.source})...")
    items = fetch_rss(urls)

    if args.limit and len(items) > args.limit:
        items = items[:args.limit]
        logging.info(f"Ограничение: берём только {args.limit} новостей")

    logging.info(f"Получено {len(items)} новостей. Записываем в базу...")
    for item in items:
        upsert_news(item)
    logging.info("Готово ✅")

if __name__ == "__main__":
    main()
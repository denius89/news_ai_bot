"""
main.py — минимальный ETL + генерация дайджеста.
RSS -> (AI-заглушки считаются внутри upsert) -> Supabase.

Запуск ETL:
  python main.py --limit 30        # взять до 30 новостей
  python main.py --source crypto   # выбрать предустановленные источники

Запуск дайджеста:
  python main.py --digest 5        # дайджест из 5 новостей
"""

import argparse
import logging
from logging.handlers import RotatingFileHandler
import os
from parsers.rss_parser import fetch_rss
from database.db_models import upsert_news
from digests.generator import generate_digest

# --- ЛОГИРОВАНИЕ ---
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("news_ai_bot")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

file_handler = RotatingFileHandler("logs/app.log", maxBytes=1_000_000, backupCount=3)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# --- ИСТОЧНИКИ ---
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
    parser.add_argument("--digest", type=int, nargs="?", const=5, help="Сформировать дайджест (по умолчанию 5 новостей)")
    args = parser.parse_args()

    # если указан дайджест — формируем его и выходим
    if args.digest is not None:
        logger.info(f"Генерация дайджеста (последние {args.digest} новостей)...")
        digest = generate_digest(limit=args.digest)
        print("\n" + digest + "\n")
        return

    # иначе — обычный ETL
    if args.source == "all":
        urls = [u for group in SOURCES.values() for u in group]
    else:
        urls = SOURCES[args.source]

    logger.info(f"Загружаем новости из {len(urls)} источников ({args.source})...")
    items = fetch_rss(urls)

    if args.limit and len(items) > args.limit:
        items = items[:args.limit]
        logger.info(f"Ограничение: берём только {args.limit} новостей")

    logger.info(f"Получено {len(items)} новостей. Записываем в базу...")
    for item in items:
        item["source"] = args.source
        upsert_news(item)

    logger.info("Готово ✅")


if __name__ == "__main__":
    main()
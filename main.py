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
import yaml

# --- Загрузка источников ---
with open("config/sources.yaml", "r", encoding="utf-8") as f:
    SOURCES = yaml.safe_load(f)

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


def main():
    parser = argparse.ArgumentParser(description="News AI Bot - ETL Pipeline")
    parser.add_argument(
        "--source", choices=list(SOURCES.keys()) + ["all"], default="all"
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--digest", type=int, nargs="?", const=5,
        help="Сформировать дайджест (по умолчанию 5 новостей)"
    )
    parser.add_argument(
        "--ai", action="store_true",
        help="Использовать AI для генерации дайджеста"
    )
    args = parser.parse_args()

    # --- Дайджест ---
    if args.digest is not None:
        logger.info(
            f"Генерация {'AI-' if args.ai else ''}дайджеста "
            f"(последние {args.digest} новостей)..."
        )
        digest = generate_digest(limit=args.digest, ai=args.ai)
        print("\n" + digest + "\n")
        return

    # --- ETL ---
    if args.source == "all":
        urls = [u["url"] for group in SOURCES.values() for u in group]
    else:
        urls = [u["url"] for u in SOURCES[args.source]]

    logger.info(f"Загружаем новости из {len(urls)} источников ({args.source})...")
    logger.info("Используемые URL:")
    for group in (SOURCES.values() if args.source == "all" else [SOURCES[args.source]]):
        for src in group:
            logger.info(f"  {src['name']}: {src['url']}")

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
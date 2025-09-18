"""
main.py — минимальный ETL:
RSS -> (AI-заглушки считаются внутри upsert) -> Supabase.
Запуск:
  python main.py --limit 30       # взять до 30 новостей
  python main.py --sources crypto # выбрать предустановленные источники
"""

import argparse
from parsers.rss_parser import fetch_rss
from database.db_models import upsert_news

# Предустановленные наборы источников
SOURCES = {
    "crypto": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
    ],
    "economy": [
        "https://news.yahoo.com/rss/",
        "https://www.reutersagency.com/feed/?best-topics=economy&post_type=best",
    ],
    "all": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
        "https://news.yahoo.com/rss/",
    ],
}

def parse_args():
    p = argparse.ArgumentParser(description="News AI Bot — ETL runner")
    p.add_argument("--sources", choices=list(SOURCES.keys()), default="all",
                   help="набор источников (crypto/economy/all)")
    p.add_argument("--limit", type=int, default=50,
                   help="максимум новостей на прогона")
    return p.parse_args()

def main():
    args = parse_args()
    urls = SOURCES[args.sources]
    items = fetch_rss(urls)

    if args.limit and len(items) > args.limit:
        items = items[:args.limit]

    print(f"[ETL] Получено новостей: {len(items)} (источники={args.sources})")

    # upsert_news сам посчитает credibility/importance и сохранит в БД
    upsert_news(items)
    print("[ETL] Готово: новости сохранены в Supabase")

if __name__ == "__main__":
    main()

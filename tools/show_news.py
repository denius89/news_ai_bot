#!/usr/bin/env python3
import argparse
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from supabase import create_client


def show_latest_news(
    limit: int = 5,
    source: Optional[str] = None,
    category: Optional[str] = None,
    days: Optional[int] = None,
):
    """
    Выводит последние N новостей из базы Supabase.
    Можно фильтровать по source (CoinDesk, Bloomberg...) и по category (crypto, economy, tech...),
    а также ограничивать по давности (days).
    """
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("❌ Ошибка: SUPABASE_URL и SUPABASE_KEY не заданы в .env")
        return

    client = create_client(url, key)

    query = client.table("news").select("*").order("published_at", desc=True)

    if source and source.lower() != "all":
        query = query.eq("source", source)

    if category and category.lower() != "all":
        query = query.eq("category", category)

    if days:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        query = query.gte("published_at", since)

    if limit:
        query = query.limit(limit)

    response = query.execute()

    if not response.data:
        print("⚠️ Новости не найдены")
        return

    print(
        f"📰 Последние {len(response.data)} новостей"
        f"{' из источника ' + source if source and source.lower() != 'all' else ''}"
        f"{' в категории ' + category if category and category.lower() != 'all' else ''}"
        f"{' за ' + str(days) + ' дней' if days else ''}:\n"
    )

    for item in response.data:
        print(f"- {item.get('title')}")
        print(f"  📅 {item.get('published_at')}")
        print(f"  🏷 {item.get('source')} ({item.get('category')})")
        print(f"  ✅ Credibility: {item.get('credibility')}, Importance: {item.get('importance')}")
        print(f"  🔗 {item.get('link')}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Показать последние новости из базы Supabase")
    parser.add_argument("--limit", type=int, default=5, help="Сколько новостей показать")
    parser.add_argument("--source", type=str, default="all", help="Источник (например, CoinDesk)")
    parser.add_argument(
        "--category",
        type=str,
        default="all",
        help="Категория (crypto, economy, world, tech, politics)",
    )
    parser.add_argument("--days", type=int, help="Показать только новости за последние N дней")
    args = parser.parse_args()

    show_latest_news(limit=args.limit, source=args.source, category=args.category, days=args.days)

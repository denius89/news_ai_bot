import os
import argparse
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone


def show_latest_news(limit: int = 5, source: str = None, days: int = None):
    """
    Выводит последние N новостей из базы Supabase.
    Можно фильтровать по source (crypto, economy, all) и по давности (days).
    """
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("❌ Ошибка: SUPABASE_URL и SUPABASE_KEY не заданы в .env")
        return

    client = create_client(url, key)

    query = client.table("news").select("*").order("id", desc=True)

    if source and source != "all":
        query = query.eq("source", source)

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
        f"{' для ' + source if source and source != 'all' else ''}"
        f"{' за ' + str(days) + ' дней' if days else ''}:\n"
    )

    for item in response.data:
        print(f"- {item.get('title')}")
        print(f"  📅 {item.get('published_at')}")
        print(
            f"  ✅ Credibility: {item.get('credibility')}, Importance: {item.get('importance')}"
        )
        print(f"  🔗 {item.get('link')}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Показать последние новости из базы Supabase"
    )
    parser.add_argument(
        "--limit", type=int, default=5, help="Сколько новостей показать"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="all",
        choices=["all", "crypto", "economy"],
        help="Источник новостей",
    )
    parser.add_argument(
        "--days", type=int, help="Показать только новости за последние N дней"
    )
    args = parser.parse_args()

    show_latest_news(limit=args.limit, source=args.source, days=args.days)

import logging
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from supabase import create_client

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

# Загружаем .env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
client = create_client(url, key)


def fix_news():
    logging.info("🔍 Загружаем все новости из базы...")
    response = client.table("news").select("*").execute()
    rows = response.data
    logging.info(f"Найдено {len(rows)} новостей для проверки")

    fixed = 0
    for row in rows:
        update_needed = False
        data = {}

        # published_at fallback
        if not row.get("published_at"):
            data["published_at"] = datetime.now(timezone.utc).isoformat()
            update_needed = True

        # credibility fallback
        if row.get("credibility") is None:
            data["credibility"] = 0.5
            update_needed = True

        # importance fallback
        if row.get("importance") is None:
            data["importance"] = 0.5
            update_needed = True

        # content fallback
        if not row.get("content"):
            data["content"] = row.get("title", "")
            update_needed = True

        if update_needed:
            client.table("news").update(data).eq("id", row["id"]).execute()
            fixed += 1

    logging.info(f"✅ Обновлено {fixed} новостей")


if __name__ == "__main__":
    fix_news()

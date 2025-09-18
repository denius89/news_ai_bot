import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def upsert_news(items: list[dict]):
    """
    Сохраняет новости в таблицу 'news' (без дублей по link).
    """
    for item in items:
        link = item.get("link")
        if not link:
            continue

        # Проверка, есть ли уже новость с таким link
        existing = supabase.table("news").select("id").eq("link", link).execute()

        if existing.data:
            continue  # пропускаем дубликат

        # Вставляем запись
        supabase.table("news").insert({
            "title": item.get("title", ""),
            "link": link,
            "published_at": item.get("published_at")
        }).execute()

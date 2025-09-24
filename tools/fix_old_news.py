#!/usr/bin/env python3

"""
Скрипт для фиксации старых новостей в базе Supabase.
Например: обновление credibility / importance для новостей,
у которых эти поля отсутствуют.
"""

import os
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from supabase import create_client

from database.db_models import enrich_news_with_ai


def get_supabase_client():
    """Инициализация клиента Supabase."""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError("SUPABASE_URL и SUPABASE_KEY должны быть заданы в .env")

    return create_client(url, key)


def fix_old_news(limit: Optional[int] = 50):
    """
    Находит старые новости без credibility/importance
    и обновляет их через AI-модули.
    """
    client = get_supabase_client()

    query = client.table("news").select("*").is_("credibility", None).limit(limit)

    response = query.execute()
    items = response.data or []

    if not items:
        print("⚠️ Нет новостей для обновления")
        return

    print(f"🔄 Найдено {len(items)} новостей для обновления...")

    updates = []
    for item in items:
        enriched = enrich_news_with_ai(item)
        enriched["updated_at"] = datetime.now(timezone.utc).isoformat()
        updates.append(enriched)

    res = client.table("news").upsert(updates, on_conflict="uid").execute()
    print(f"✅ Обновлено {len(res.data or [])} новостей")


def main():
    fix_old_news(limit=50)


if __name__ == "__main__":
    main()

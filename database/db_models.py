import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance

# Настройка логирования (если не было настроено выше в main.py)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Загружаем переменные окружения
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Не найдены SUPABASE_URL или SUPABASE_KEY в .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upsert_news(items: List[Dict[str, Any]]) -> None:
    for item in items:
        link = item.get("link")
        if not link:
            logging.warning("Пропуск новости без ссылки")
            continue

        credibility = evaluate_credibility(item)
        importance = evaluate_importance(item)

        published = item.get("published")
        if isinstance(published, datetime):
            published = published.isoformat()

        data = {
            "title": item.get("title", ""),
            "link": link,
            "published_at": published,
            "content": item.get("content") or item.get("title"),
            "credibility": credibility,
            "importance": importance
        }

        try:
            supabase.table("news").upsert(data, on_conflict=["link"]).execute()
            logging.info(f"✅ Добавлена/обновлена новость: {data['title'][:60]}...")
        except Exception as e:
            logging.error(f"⚠️ Ошибка при вставке {link}: {e}")
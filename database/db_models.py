import os
from datetime import datetime
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Импорты AI-заглушек
from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance

# Загружаем переменные окружения
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Не найдены SUPABASE_URL или SUPABASE_KEY в .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def upsert_news(items: List[Dict[str, Any]]) -> None:
    """
    Добавляет новости в таблицу news, избегая дублей по ссылке.
    Дополнительно сохраняет AI-оценки: credibility и importance.
    """
    for item in items:
        link = item.get("link")
        if not link:
            continue

        # AI-оценки
        credibility = evaluate_credibility(item)
        importance = evaluate_importance(item)

        # Обработка даты: datetime → ISO string
        published = item.get("published")
        if isinstance(published, datetime):
            published = published.isoformat()

        data = {
            "title": item.get("title", ""),
            "link": link,
            "published_at": published,
            "credibility": credibility,
            "importance": importance
        }

        try:
            supabase.table("news").upsert(data, on_conflict=["link"]).execute()
        except Exception as e:
            print(f"⚠️ Ошибка при вставке новости: {e}")
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Импорты AI-заглушек
from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance

# Загружаем переменные окружения
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def upsert_news(items: list[dict]):
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

        supabase.table("news").upsert({
            "title": item.get("title", ""),
            "link": link,
            "published_at": published,
            "credibility": credibility,
            "importance": importance
        }, on_conflict=["link"]).execute()
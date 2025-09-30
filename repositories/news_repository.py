"""
Репозиторий для работы с таблицей news.
"""

from typing import List, Optional
from supabase import Client
from models.news import NewsItem


class NewsRepository:
    """
    Репозиторий новостей: чтение и вставка в Supabase.
    """

    def __init__(self, client: Client):
        self._db = client

    def latest(self, limit: int = 10, categories: Optional[List[str]] = None) -> List[NewsItem]:
        """
        Получить последние новости.
        :param limit: количество новостей
        :param categories: список категорий для фильтрации
        """
        q = self._db.table("news").select("*").order("published_at", desc=True).limit(limit)
        if categories:
            q = q.in_("category", categories)
        data = q.execute().data or []
        return [NewsItem.model_validate(d) for d in data]

    def upsert(self, items: List[NewsItem]) -> int:
        """
        Вставить или обновить список новостей (по uid).
        :return: количество вставленных строк
        """
        rows = [i.model_dump(mode="json") for i in items]
        res = self._db.table("news").upsert(rows, on_conflict="uid").execute()
        return len(res.data or [])

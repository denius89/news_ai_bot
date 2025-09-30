"""
Репозиторий для работы с таблицей events.
"""

from typing import List, Optional
from supabase import Client
from models.event import EventItem


class EventsRepository:
    """
    Репозиторий событий: чтение и вставка в Supabase.
    """

    def __init__(self, client: Client):
        self._db = client

    def upcoming(self, limit: int = 50, category: Optional[str] = None) -> List[EventItem]:
        """
        Получить ближайшие события.
        :param limit: количество событий
        :param category: категория для фильтрации
        """
        q = self._db.table("events").select("*").order("event_time", desc=False).limit(limit)
        if category:
            q = q.eq("category", category)
        data = q.execute().data or []
        return [EventItem.model_validate(d) for d in data]

    def upsert(self, items: List[EventItem]) -> int:
        """
        Вставить или обновить список событий (по event_id).
        :return: количество вставленных строк
        """
        rows = [i.model_dump(mode="json") for i in items]
        res = self._db.table("events").upsert(rows, on_conflict="event_id").execute()
        return len(res.data or [])

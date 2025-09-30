"""
Репозиторий для работы с таблицей events.
"""

import logging
from typing import List, Optional
from supabase import Client
from datetime import datetime
from models.event import EventItem

logger = logging.getLogger(__name__)


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
        :param category: категория для фильтрации (если есть)
        """
        if not self._db:
            logger.warning("⚠️ Supabase не инициализирован — возвращаем пустой список событий.")
            return []

        try:
            q = (
                self._db.table("events")
                .select(
                    "event_id, event_time, country, country_code, currency, "
                    "title, importance, fact, forecast, previous, source"
                )
                .order("event_time", desc=False)
                .limit(limit)
            )
            if category:
                q = q.eq("category", category.lower())

            data = q.execute().data or []
            events: List[EventItem] = []
            for d in data:
                try:
                    ev = EventItem.model_validate(d)
                    # форматированная дата для отображения
                    if ev.event_time:
                        try:
                            dt = datetime.fromisoformat(str(ev.event_time).replace("Z", "+00:00"))
                            d["event_time_fmt"] = dt.strftime("%d %b %Y, %H:%M")
                        except Exception:
                            d["event_time_fmt"] = "—"
                    events.append(ev)
                except Exception as e:
                    logger.warning("Ошибка валидации события: %s (row=%s)", e, d)
            return events

        except Exception as e:
            logger.error("Ошибка при получении событий: %s", e, exc_info=True)
            return []

    def upsert(self, items: List[EventItem]) -> int:
        """
        Вставить или обновить список событий (по event_id).
        :return: количество вставленных строк
        """
        if not self._db:
            logger.warning("⚠️ Supabase не инициализирован — upsert не выполнен.")
            return 0

        try:
            rows = [i.model_dump(mode="json") for i in items]
            res = self._db.table("events").upsert(rows, on_conflict="event_id").execute()
            count = len(res.data or [])
            logger.info("✅ Upsert events: %d", count)
            return count
        except Exception as e:
            logger.error("Ошибка при upsert событий: %s", e, exc_info=True)
            return 0

"""
Репозиторий для работы с таблицей events.
"""

import logging
from typing import List, Optional, Union
from supabase import Client
from datetime import datetime
from models.event import EventItem

logger = logging.getLogger(__name__)


class EventsRepository:
    """
    Репозиторий событий: чтение и вставка записей в Supabase.

    Выравнен по стилю с `NewsRepository`: использует модульный `logger`,
    строгие сигнатуры типов и обработку ошибок с логированием.
    """

    def __init__(self, client: Client):
        """
        Инициализирует репозиторий событий.

        :param client: экземпляр клиента Supabase.
        """
        self._db = client

    def upcoming(
        self,
        limit: int = 50,
        categories: Optional[Union[str, List[str]]] = None,
    ) -> List[EventItem]:
        """
        Получить ближайшие события в порядке по времени.

        - Возвращает список валидированных моделей `EventItem`.
        - Поддерживает фильтрацию по категории: можно передать строку или список строк.

        :param limit: максимальное число элементов выборки.
        :param categories: категория или список категорий для фильтрации; значения нормализуются к lower().
        :return: список объектов `EventItem`.
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
            if categories:
                if isinstance(categories, str):
                    q = q.eq("category", categories.lower())
                elif isinstance(categories, list):
                    cats = [c.strip().lower() for c in categories if c and c.strip()]
                    if len(cats) == 1:
                        q = q.eq("category", cats[0])
                    elif len(cats) > 1:
                        q = q.in_("category", cats)

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
            logger.debug(
                "EventsRepository.upcoming → %d rows (limit=%s, categories=%s)",
                len(events),
                limit,
                categories,
            )
            return events

        except Exception as e:
            logger.error("Ошибка при получении событий: %s", e, exc_info=True)
            return []

    def upsert(self, items: List[EventItem]) -> int:
        """
        Вставить или обновить список событий по ключу `event_id`.

        :param items: список валидированных объектов `EventItem` для сохранения.
        :return: количество вставленных/обновленных строк (по ответу Supabase), либо 0 при ошибке.
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


__all__ = ["EventsRepository"]

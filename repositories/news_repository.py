"""Репозиторий для работы с таблицей news в Supabase."""

import logging
from typing import List, Dict, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class NewsRepository:
    """Инкапсулирует работу с таблицей news."""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def get_recent_news(
        self,
        limit: int = 10,
        categories: Optional[Union[str, List[str]]] = None,
    ) -> List[Dict]:
        """Возвращает последние новости из таблицы news.

        Args:
            limit: сколько новостей брать
            categories: строка (одна категория) или список категорий
        """
        if not self.supabase:
            logger.warning("⚠️ Supabase не инициализирован — возвращаем пустой список.")
            return []

        try:
            query = (
                self.supabase.table("news")
                .select(
                    "id, title, content, link, importance, credibility, "
                    "published_at, source, category"
                )
                .order("importance", desc=True)
                .order("published_at", desc=True)
                .limit(limit)
            )

            # фильтрация по категориям
            if categories:
                if isinstance(categories, str):
                    query = query.eq("category", categories.lower())
                elif isinstance(categories, list):
                    cats = [c.lower() for c in categories if c.strip()]
                    if len(cats) == 1:
                        query = query.eq("category", cats[0])
                    elif len(cats) > 1:
                        query = query.in_("category", cats)

            rows = query.execute().data or []

            for row in rows:
                # формат даты
                fmt = "—"
                ts = row.get("published_at")
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        fmt = dt.strftime("%d %b %Y, %H:%M")
                    except Exception as e:
                        logger.debug("Не удалось преобразовать дату %s: %s", ts, e)
                row["published_at_fmt"] = fmt

                # нормализация credibility и importance
                row["credibility"] = float(row.get("credibility") or 0.5)
                row["importance"] = float(row.get("importance") or 0.5)

            logger.debug(
                "NewsRepository.get_recent_news → %d rows (limit=%s, categories=%s)",
                len(rows),
                limit,
                categories,
            )
            return rows

        except Exception as e:
            logger.error("Ошибка при получении новостей: %s", e, exc_info=True)
            return []

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
        if not self.supabase:
            logger.warning("⚠️ Supabase не инициализирован — возвращаем пустой список.")
            return []

        try:
            safe_limit = max(1, min(int(limit or 10), 50))

            query = (
                self.supabase.table("news")
                .select("id, title, content, link, importance, credibility, published_at, source, category")
                .order("importance", desc=True)
                .order("published_at", desc=True)
                .limit(safe_limit)
            )

            if categories:
                if isinstance(categories, str):
                    query = query.eq("category", categories.lower())
                elif isinstance(categories, list):
                    cats = [c.strip().lower() for c in categories if c and c.strip()]
                    if len(cats) == 1:
                        query = query.eq("category", cats[0])
                    elif len(cats) > 1:
                        query = query.in_("category", cats)

            rows = query.execute().data or []

            for row in rows:
                fmt = "—"
                ts = row.get("published_at")
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        fmt = dt.strftime("%d %b %Y, %H:%M")
                    except Exception as e:
                        logger.debug("Не удалось преобразовать дату %s: %s", ts, e)
                row["published_at_fmt"] = fmt

            logger.debug(
                "NewsRepository.get_recent_news → %d rows (limit=%s, categories=%s)",
                len(rows),
                safe_limit,
                categories,
            )
            return rows

        except Exception as e:
            logger.error("Ошибка при получении новостей: %s", e, exc_info=True)
            return []

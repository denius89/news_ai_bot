import logging
from datetime import datetime
from typing import List, Optional, Union

from supabase import Client
from models.news import NewsItem

logger = logging.getLogger(__name__)


class NewsRepository:
    """
    Репозиторий новостей: чтение записей из Supabase.
    Выравнен по стилю с `EventsRepository` и возвращает Pydantic-модели `NewsItem`.
    """

    def __init__(self, client: Client):
        """
        Инициализировать репозиторий новостей.

        :param client: экземпляр клиента Supabase.
        """
        self._db = client

    def get_recent_news(
        self,
        limit: int = 10,
        categories: Optional[Union[str, List[str]]] = None,
        subcategories: Optional[Union[str, List[str]]] = None,
    ) -> List[NewsItem]:
        """
        Получить список последних новостей с упорядочиванием по важности и времени публикации.

        - Возвращает список валидированных моделей `NewsItem`.
        - Поддерживает фильтрацию по категории и субкатегории: можно передать строку или список строк.

        :param limit: максимальное количество элементов (1..50). Значение вне диапазона будет ограничено.
        :param categories: категория или список категорий для фильтрации.
                           Регистр не учитывается, значения нормализуются к lower().
        :param subcategories: субкатегория или список субкатегорий для фильтрации.
                             Регистр не учитывается, значения нормализуются к lower().
        :return: список объектов `NewsItem`.
        """
        if not self._db:
            logger.warning("⚠️ Supabase не инициализирован — возвращаем пустой список новостей.")
            return []

        try:
            safe_limit = max(1, min(int(limit or 10), 50))

            q = (
                self._db.table("news")
                .select(
                    "id, title, content, link, importance, credibility, published_at, source, category, subcategory"
                )
                .order("importance", desc=True)
                .order("published_at", desc=True)
                .limit(safe_limit)
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

            if subcategories:
                if isinstance(subcategories, str):
                    q = q.eq("subcategory", subcategories.lower())
                elif isinstance(subcategories, list):
                    subcats = [sc.strip().lower() for sc in subcategories if sc and sc.strip()]
                    if len(subcats) == 1:
                        q = q.eq("subcategory", subcats[0])
                    elif len(subcats) > 1:
                        q = q.in_("subcategory", subcats)

            data = q.execute().data or []

            items: List[NewsItem] = []
            for d in data:
                try:
                    # приводим id к str, т.к. в источнике могут быть UUID
                    row = dict(d)
                    if "id" in row and row["id"] is not None:
                        row["id"] = str(row["id"])
                    item = NewsItem.model_validate(row)
                    # Дополнительно пытаемся вычислить человекочитаемую дату
                    # (как в EventsRepository), но не мутируем модель —
                    # формат пригоден для внешнего слоя, если потребуется.
                    ts = d.get("published_at")
                    if ts:
                        try:
                            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                            d["published_at_fmt"] = dt.strftime("%d %b %Y, %H:%M")
                        except Exception:
                            d["published_at_fmt"] = "—"
                    items.append(item)
                except Exception as e:
                    logger.warning("Ошибка валидации новости: %s (row=%s)", e, d)

            logger.debug(
                "NewsRepository.get_recent_news → %d rows (limit=%s, categories=%s, subcategories=%s)",
                len(items),
                safe_limit,
                categories,
                subcategories,
            )
            return items

        except Exception as e:
            logger.error("Ошибка при получении новостей: %s", e, exc_info=True)
            return []

    def get_news_by_subcategory(self, subcategory: str, limit: int = 15) -> List[NewsItem]:
        """
        Получить новости по конкретной субкатегории.

        :param subcategory: субкатегория для фильтрации
        :param limit: максимальное количество элементов
        :return: список объектов `NewsItem`
        """
        return self.get_recent_news(limit=limit, subcategories=subcategory)

    def get_all_subcategories(self) -> List[str]:
        """
        Получить список всех уникальных субкатегорий из базы данных.

        :return: список уникальных субкатегорий
        """
        if not self._db:
            logger.warning("⚠️ Supabase не инициализирован")
            return []

        try:
            response = self._db.table("news").select("subcategory").execute()
            data = response.data or []

            # Извлекаем уникальные субкатегории
            subcategories = set()
            for item in data:
                subcat = item.get("subcategory")
                if subcat and subcat.strip():
                    subcategories.add(subcat.strip().lower())

            return sorted(list(subcategories))

        except Exception as e:
            logger.error("Ошибка при получении субкатегорий: %s", e, exc_info=True)
            return []


__all__ = ["NewsRepository"]

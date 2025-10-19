"""
News Graph System - связывание новостей и создание контекста историй.

Создаёт граф связей между новостями и предоставляет контекст для дайджестов.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta, timezone
from collections import Counter

logger = logging.getLogger(__name__)


class NewsGraphBuilder:
    """Строит граф связей между новостями."""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def find_related_news(
        self, current_news: Dict, lookback_days: int = 30, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Находит связанные новости по ключевым словам и семантике.

        Args:
            current_news: Текущая новость (словарь с полями title, content, etc.)
            lookback_days: Количество дней назад для поиска
            max_results: Максимальное количество результатов

        Returns:
            Список связанных новостей с метриками схожести
        """
        try:
            # Получаем новости за последние N дней
            start_date = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()

            # Исключаем текущую новость если у неё есть ID
            query = (
                self.supabase.table("news")
                .select("*")
                .gte("created_at", start_date)
                .order("created_at", desc=True)
                .limit(100)
            )  # Ограничиваем для производительности

            if current_news.get("id"):
                query = query.neq("id", current_news["id"])

            result = query.execute()
            candidates = result.data or []

            if not candidates:
                logger.info("No news candidates found for graph building")
                return []

            # Вычисляем схожесть
            scored_news = []
            current_keywords = self._extract_keywords(current_news)
            current_entities = self._extract_entities(current_news)

            for news_item in candidates:
                similarity_score = self._calculate_similarity(
                    current_news, news_item, current_keywords, current_entities
                )

                if similarity_score > 0.3:  # Порог схожести
                    scored_news.append(
                        {
                            **news_item,
                            "similarity_score": similarity_score,
                            "keywords_overlap": self._get_keywords_overlap(
                                current_keywords, self._extract_keywords(news_item)
                            ),
                            "entities_overlap": self._get_entities_overlap(
                                current_entities, self._extract_entities(news_item)
                            ),
                        }
                    )

            # Сортируем по схожести и возвращаем топ результаты
            scored_news.sort(key=lambda x: x["similarity_score"], reverse=True)

            logger.info(f"Found {len(scored_news)} related news items for story context")
            return scored_news[:max_results]

        except Exception as e:
            logger.error(f"Error finding related news: {e}")
            return []

    def create_story_context(
        self, current_news_items: List[Dict], related_history: List[Dict], max_context_items: int = 3
    ) -> str:
        """
        Создаёт контекст '📚 Ранее мы писали...' для промпта.

        Args:
            current_news_items: Текущие новости для дайджеста
            related_history: Связанные предыдущие новости
            max_context_items: Максимальное количество элементов контекста

        Returns:
            Строка с историческим контекстом
        """
        if not related_history:
            return ""

        # Выбираем самые релевантные элементы истории
        top_history = sorted(related_history, key=lambda x: x.get("similarity_score", 0), reverse=True)
        top_history = top_history[:max_context_items]

        context_parts = ["📚 Ранее мы писали:"]

        for hist_item in top_history:
            title = hist_item.get("title", "Без названия")[:80]  # Ограничиваем длину
            similarity = hist_item.get("similarity_score", 0)
            date = self._format_date(hist_item.get("created_at") or hist_item.get("published_at"))

            context_parts.append(f"• {title} ({date}, схожесть: {similarity:.2f})")

        context_parts.append("")  # Пустая строка в конце

        logger.info(f"Created story context with {len(top_history)} historical items")
        return "\n".join(context_parts)

    def save_news_links(
        self,
        news_id_1: str,
        news_id_2: str,
        link_type: str = "related",
        similarity_score: float = 0.0,
        keywords_overlap: Dict = None,
        entities_overlap: Dict = None,
    ) -> bool:
        """
        Сохраняет связь между новостями в базу данных.

        Args:
            news_id_1: ID первой новости
            news_id_2: ID второй новости
            link_type: Тип связи
            similarity_score: Оценка схожести
            keywords_overlap: Пересекающиеся ключевые слова
            entities_overlap: Пересекающиеся сущности

        Returns:
            True если успешно сохранено
        """
        try:
            # Обеспечиваем правильный порядок ID для уникальности
            if news_id_1 > news_id_2:
                news_id_1, news_id_2 = news_id_2, news_id_1

            link_data = {
                "news_id_1": news_id_1,
                "news_id_2": news_id_2,
                "link_type": link_type,
                "similarity_score": similarity_score,
                "keywords_overlap": keywords_overlap or {},
                "entities_overlap": entities_overlap or {},
            }

            # Используем upsert чтобы избежать дубликатов
            self.supabase.table("news_links").upsert(link_data, on_conflict="news_id_1,news_id_2").execute()

            logger.info(f"Saved news link: {news_id_1} <-> {news_id_2} (score: {similarity_score:.3f})")
            return True

        except Exception as e:
            logger.error(f"Error saving news link: {e}")
            return False

    def _extract_keywords(self, news_item: Dict) -> List[str]:
        """Извлекает ключевые слова из новости."""
        text = f"{news_item.get('title', '')} {news_item.get('content', '')}".lower()

        # Простое извлечение ключевых слов (можно улучшить)
        words = text.split()
        # Убираем стоп-слова и короткие слова
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "а",
            "и",
            "или",
            "но",
            "в",
            "на",
            "к",
            "для",
            "о",
            "с",
            "по",
        }
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]

        # Возвращаем наиболее частые слова
        return [word for word, count in Counter(keywords).most_common(10)]

    def _extract_entities(self, news_item: Dict) -> List[str]:
        """Извлекает именованные сущности из новости."""
        # Простая реализация - можно улучшить с помощью NER
        text = f"{news_item.get('title', '')} {news_item.get('content', '')}"

        # Извлекаем слова с заглавной буквы как потенциальные сущности
        import re

        entities = re.findall(r"\b[A-ZА-Я][a-zа-я]+\b", text)
        return list(set(entities[:10]))  # Убираем дубликаты и ограничиваем

    def _calculate_similarity(self, news1: Dict, news2: Dict, keywords1: List[str], entities1: List[str]) -> float:
        """Вычисляет схожесть между двумя новостями."""
        keywords2 = self._extract_keywords(news2)
        entities2 = self._extract_entities(news2)

        # Схожесть по ключевым словам
        keyword_overlap = len(set(keywords1) & set(keywords2))
        keyword_total = len(set(keywords1) | set(keywords2))
        keyword_sim = keyword_overlap / keyword_total if keyword_total > 0 else 0

        # Схожесть по сущностям
        entity_overlap = len(set(entities1) & set(entities2))
        entity_total = len(set(entities1) | set(entities2))
        entity_sim = entity_overlap / entity_total if entity_total > 0 else 0

        # Схожесть по категории
        category_sim = 1.0 if news1.get("category") == news2.get("category") else 0.0

        # Схожесть по источнику
        source_sim = 1.0 if news1.get("source") == news2.get("source") else 0.0

        # Взвешенная сумма
        similarity = keyword_sim * 0.4 + entity_sim * 0.3 + category_sim * 0.2 + source_sim * 0.1

        return min(similarity, 1.0)

    def _get_keywords_overlap(self, keywords1: List[str], keywords2: List[str]) -> Dict:
        """Возвращает пересечение ключевых слов."""
        overlap = list(set(keywords1) & set(keywords2))
        return {"overlap_count": len(overlap), "overlap_words": overlap[:5]}  # Ограничиваем для JSON

    def _get_entities_overlap(self, entities1: List[str], entities2: List[str]) -> Dict:
        """Возвращает пересечение сущностей."""
        overlap = list(set(entities1) & set(entities2))
        return {"overlap_count": len(overlap), "overlap_entities": overlap[:5]}  # Ограничиваем для JSON

    def _format_date(self, date_str: str) -> str:
        """Форматирует дату для отображения."""
        try:
            if isinstance(date_str, str):
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                return dt.strftime("%d.%m")
            return "неизв."
        except (ValueError, TypeError, AttributeError):
            return "неизв."


class StoryContextManager:
    """Менеджер контекста историй - координирует работу с новостным графом."""

    def __init__(self, supabase_client):
        self.graph_builder = NewsGraphBuilder(supabase_client)

    def get_historical_context_for_digest(self, news_items: List[Dict], category: str, lookback_days: int = 30) -> str:
        """
        Получает исторический контекст для дайджеста.

        Args:
            news_items: Новости для текущего дайджеста
            category: Категория новостей
            lookback_days: Количество дней для поиска истории

        Returns:
            Строка с контекстом для добавления в промпт
        """
        if not news_items:
            return ""

        # Выбираем наиболее важную новость для поиска связей
        main_news = max(news_items, key=lambda x: x.get("importance", 0))

        # Находим связанные новости
        related_news = self.graph_builder.find_related_news(main_news, lookback_days=lookback_days, max_results=5)

        # Создаём контекст
        context = self.graph_builder.create_story_context(news_items, related_news, max_context_items=3)

        return context

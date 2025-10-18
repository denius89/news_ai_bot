"""
RAG (Retrieval-Augmented Generation) система для дайджестов.

Использует примеры высококачественных дайджестов для улучшения генерации.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from collections import Counter

logger = logging.getLogger(__name__)


class DigestRAGSystem:
    """RAG система для поиска релевантных примеров дайджестов."""

    def __init__(self, samples_file: str = "data/digest_training/samples.json"):
        self.samples_file = Path(samples_file)
        self.samples = []
        self._load_samples()

    def _load_samples(self):
        """Загрузить примеры дайджестов."""
        try:
            if self.samples_file.exists():
                with open(self.samples_file, "r", encoding="utf-8") as f:
                    self.samples = json.load(f)
                logger.info(f"Loaded {len(self.samples)} digest samples")
            else:
                logger.warning(f"Samples file not found: {self.samples_file}")
                self.samples = []
        except Exception as e:
            logger.error(f"Failed to load samples: {e}")
            self.samples = []

    def reload_samples(self):
        """Перезагрузить примеры из файла."""
        logger.info("Reloading samples from file...")
        self._load_samples()

    def _calculate_relevance_score(
        self,
        sample: Dict[str, Any],
        target_category: str,
        target_subcategory: Optional[str] = None,
        target_style: str = "analytical",
        news_keywords: List[str] = None,
    ) -> float:
        """Вычислить релевантность примера к целевым параметрам."""

        score = 0.0

        # Совпадение категории (+30)
        if sample.get("category") == target_category:
            score += 30.0

        # Совпадение подкатегории (+25)
        if target_subcategory and sample.get("subcategory") == target_subcategory:
            score += 25.0

        # Совпадение стиля (+20)
        if sample.get("style") == target_style:
            score += 20.0

        # Анализ ключевых слов в новостях
        if news_keywords and sample.get("digest"):
            digest_text = sample["digest"].lower()
            keyword_matches = sum(1 for keyword in news_keywords if keyword.lower() in digest_text)
            score += keyword_matches * 5.0

        # Приоритет по источнику (высококачественные источники)
        source_bonus = {
            "The Bell": 5.0,
            "Bloomberg": 5.0,
            "Reuters": 4.0,
            "CoinDesk": 3.0,
            "TechCrunch": 4.0,
            "WSJ": 5.0,
        }
        source = sample.get("source", "").lower()
        for high_quality_source, bonus in source_bonus.items():
            if high_quality_source.lower() in source:
                score += bonus
                break

        # Бонус за длину (более информативные дайджесты)
        word_count = sample.get("word_count", 0)
        if 300 <= word_count <= 800:  # Оптимальная длина
            score += 10.0
        elif 200 <= word_count < 300:
            score += 5.0

        return score

    def find_relevant_samples(
        self,
        category: str,
        subcategory: Optional[str] = None,
        style: str = "analytical",
        news_items: Optional[List[Any]] = None,
        max_samples: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Найти релевантные примеры для генерации.

        Args:
            category: Целевая категория
            subcategory: Целевая подкатегория
            style: Стиль дайджеста
            news_items: Новости для анализа ключевых слов
            max_samples: Максимальное количество примеров

        Returns:
            Список релевантных примеров с оценками
        """

        if not self.samples:
            logger.warning("No samples available for RAG")
            return []

        # Извлечь ключевые слова из новостей
        news_keywords = []
        if news_items:
            for item in news_items:
                if hasattr(item, "title") and item.title:
                    # Простое извлечение ключевых слов
                    words = re.findall(r"\b\w+\b", item.title.lower())
                    news_keywords.extend([w for w in words if len(w) > 3])

        # Рассчитать релевантность для каждого примера
        scored_samples = []

        for sample in self.samples:
            score = self._calculate_relevance_score(
                sample=sample,
                target_category=category,
                target_subcategory=subcategory,
                target_style=style,
                news_keywords=news_keywords,
            )

            if score > 0:  # Только релевантные примеры
                scored_samples.append({"sample": sample, "score": score})

        # Сортировать по релевантности
        scored_samples.sort(key=lambda x: x["score"], reverse=True)

        # Вернуть топ примеры
        result = scored_samples[:max_samples]

        if result:
            logger.info(
                f"Found {len(result)} relevant samples for {category}/{subcategory} with scores: {[r['score'] for r in result]}"
            )

        return result

    def create_rag_context(self, relevant_samples: List[Dict[str, Any]], max_context_length: int = 2000) -> str:
        """
        Создать контекст из релевантных примеров для промпта.

        Args:
            relevant_samples: Релевантные примеры с оценками
            max_context_length: Максимальная длина контекста

        Returns:
            Строка с контекстом для промпта
        """

        if not relevant_samples:
            return ""

        context_parts = []
        context_parts.append("📚 ПРИМЕРЫ ВЫСОКОКАЧЕСТВЕННЫХ ДАЙДЖЕСТОВ:\n")

        for i, item in enumerate(relevant_samples, 1):
            sample = item["sample"]
            score = item["score"]

            context_part = f"""
ПРИМЕР {i} (релевантность: {score:.1f}):
Источник: {sample.get('source', 'Unknown')}
Стиль: {sample.get('style', 'analytical')}
Слов: {sample.get('word_count', 0)}

{sample.get('digest', '')}
"""

            # Проверить, не превышает ли общая длина лимит
            if len("\n".join(context_parts) + context_part) > max_context_length:
                break

            context_parts.append(context_part)

        context_parts.append(
            "\n💡 ИСПОЛЬЗУЙ ЭТИ ПРИМЕРЫ КАК ОРИЕНТИР для стиля, структуры и качества твоего дайджеста."
        )

        return "\n".join(context_parts)

    def get_style_guidance(
        self, category: str, subcategory: Optional[str] = None, style: str = "analytical"
    ) -> Dict[str, Any]:
        """
        Получить рекомендации по стилю на основе примеров.

        Returns:
            Словарь с рекомендациями по стилю
        """

        relevant_samples = self.find_relevant_samples(
            category=category, subcategory=subcategory, style=style, max_samples=5
        )

        if not relevant_samples:
            return {"avg_word_count": 500, "common_phrases": [], "structure_pattern": "general"}

        # Анализ длины
        word_counts = [item["sample"].get("word_count", 0) for item in relevant_samples]
        avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 500

        # Анализ структуры
        structures = []
        for item in relevant_samples:
            digest = item["sample"].get("digest", "")
            if "##" in digest or "<h2>" in digest:
                structures.append("sectioned")
            elif len(digest.split("\n\n")) > 3:
                structures.append("paragraphs")
            else:
                structures.append("single")

        structure_pattern = Counter(structures).most_common(1)[0][0] if structures else "paragraphs"

        # Анализ ключевых фраз (простой)
        common_phrases = []
        for item in relevant_samples:
            digest = item["sample"].get("digest", "")
            # Извлечь первые слова абзацев как структурирующие фразы
            paragraphs = digest.split("\n\n")
            for para in paragraphs[:2]:  # Только первые два абзаца
                first_sentence = para.split(".")[0] if "." in para else para[:100]
                if len(first_sentence) > 20:
                    common_phrases.append(first_sentence.strip())

        return {
            "avg_word_count": int(avg_word_count),
            "common_phrases": common_phrases[:3],
            "structure_pattern": structure_pattern,
            "sample_count": len(relevant_samples),
        }


# Глобальный кэшированный экземпляр RAG системы для оптимизации
_global_rag_system = None


def _get_rag_system():
    """Получить глобальный экземпляр RAG системы с ленивой инициализацией."""
    global _global_rag_system
    if _global_rag_system is None:
        _global_rag_system = DigestRAGSystem()
        logger.info(f"Initialized global RAG system with {len(_global_rag_system.samples)} samples")
    return _global_rag_system


# Convenience functions
def get_rag_context(
    category: str,
    subcategory: Optional[str] = None,
    style: str = "analytical",
    news_items: Optional[List[Any]] = None,
    max_samples: int = 3,
) -> str:
    """Получить RAG контекст для промпта."""

    rag_system = _get_rag_system()
    # Перезагружаем примеры только если файл изменился (TODO: добавить проверку mtime)
    try:
        rag_system.reload_samples()
    except Exception as e:
        logger.warning(f"RAG reload failed, using cached: {e}")

    relevant_samples = rag_system.find_relevant_samples(
        category=category, subcategory=subcategory, style=style, news_items=news_items, max_samples=max_samples
    )

    return rag_system.create_rag_context(relevant_samples)


def get_style_recommendations(
    category: str, subcategory: Optional[str] = None, style: str = "analytical"
) -> Dict[str, Any]:
    """Получить рекомендации по стилю на основе примеров."""

    rag_system = DigestRAGSystem()
    # Перезагружаем примеры для получения актуальных данных
    rag_system.reload_samples()

    return rag_system.get_style_guidance(category=category, subcategory=subcategory, style=style)

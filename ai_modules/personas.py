"""
Editorial Personas System - автоматический выбор стиля редактора.

Содержит разные "личности редакторов" с разным стилем и ритмом.
Автоматически выбирает персону в зависимости от категории, подкатегории и горячести темы.
"""

import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


EDITORIAL_PERSONAS = {
    "reuters_editor": {
        "name": "Reuters Editor",
        "style": "newsroom",
        "characteristics": ["краткость", "факты", "нейтральность"],
        "use_cases": ["breaking_news", "urgent", "markets"],
        "tone": "neutral",
        "sentence_length": "short",
        "description": "Быстрые, фактологические новости в стиле ведущих информационных агентств",
    },
    "economist_analyst": {
        "name": "Economist Analyst",
        "style": "analytical",
        "characteristics": ["глубина", "анализ", "связи"],
        "use_cases": ["trends", "deep_analysis", "crypto"],
        "tone": "insightful",
        "sentence_length": "long",
        "description": "Глубокий анализ с выявлением связей между событиями",
    },
    "atlantic_writer": {
        "name": "Atlantic Writer",
        "style": "magazine",
        "characteristics": ["storytelling", "метафоры", "engaging"],
        "use_cases": ["features", "tech", "world"],
        "tone": "narrative",
        "sentence_length": "medium",
        "description": "Повествовательный стиль с живыми метафорами и интересными историями",
    },
    "telegram_blogger": {
        "name": "Telegram Blogger",
        "style": "casual",
        "characteristics": ["простота", "дружелюбие", "понятность"],
        "use_cases": ["quick_updates", "sports", "general"],
        "tone": "friendly",
        "sentence_length": "short",
        "description": "Простой, дружелюбный стиль для быстрых обновлений",
    },
    "bloomberg_trader": {
        "name": "Bloomberg Trader",
        "style": "financial",
        "characteristics": ["точность", "данные", "рынки"],
        "use_cases": ["markets", "financial_data", "earnings"],
        "tone": "precise",
        "sentence_length": "medium",
        "description": "Профессиональный финансовый стиль с акцентом на данные и рынки",
    },
    "tech_crunch_reporter": {
        "name": "TechCrunch Reporter",
        "style": "tech_focused",
        "characteristics": ["инновации", "технологии", "стартапы"],
        "use_cases": ["tech", "startups", "innovation"],
        "tone": "enthusiastic",
        "sentence_length": "medium",
        "description": "Энтузиаст технологий, который понимает тренды и инновации",
    },
}


class PersonaSelector:
    """Автоматически выбирает персону редактора на основе контекста."""

    def select_persona(
        self,
        category: str,
        subcategory: Optional[str] = None,
        urgency: float = 0.5,
        complexity: float = 0.5,
        news_count: int = 5,
        avg_importance: float = 0.5,
    ) -> str:
        """
        Возвращает ID персоны на основе контекста.

        Логика выбора:
        - Срочные новости (urgency > 0.8) → reuters_editor
        - Сложный анализ (complexity > 0.7) → economist_analyst
        - Технологии → tech_crunch_reporter
        - Финансы/рынки → bloomberg_trader
        - Истории (tech, world) → atlantic_writer
        - Простые обновления → telegram_blogger

        Args:
            category: Категория новостей (crypto, tech, markets, etc.)
            subcategory: Подкатегория (optional)
            urgency: Срочность (0.0-1.0)
            complexity: Сложность анализа (0.0-1.0)
            news_count: Количество новостей
            avg_importance: Средняя важность новостей

        Returns:
            ID персоны из EDITORIAL_PERSONAS
        """

        # Высокая срочность → быстрая подача фактов
        if urgency > 0.8:
            logger.info(f"High urgency ({urgency:.2f}), selecting reuters_editor")
            return "reuters_editor"

        # Сложный анализ → глубокий разбор
        if complexity > 0.7 or avg_importance > 0.8:
            logger.info(
                f"High complexity ({complexity:.2f}) or importance ({avg_importance:.2f}), selecting economist_analyst"
            )
            return "economist_analyst"

        # Категориальные предпочтения
        category_persona_map = {
            "tech": "tech_crunch_reporter",
            "crypto": "bloomberg_trader",
            "markets": "bloomberg_trader",
            "sports": "telegram_blogger",
            "world": "atlantic_writer" if complexity > 0.4 else "reuters_editor",
        }

        if category.lower() in category_persona_map:
            selected = category_persona_map[category.lower()]
            logger.info(f"Category-based selection: {category} → {selected}")
            return selected

        # Подкатегориальные уточнения
        if subcategory:
            subcategory_persona_map = {
                "breaking": "reuters_editor",
                "analysis": "economist_analyst",
                "startup": "tech_crunch_reporter",
                "trading": "bloomberg_trader",
                "earnings": "bloomberg_trader",
            }

            if subcategory.lower() in subcategory_persona_map:
                selected = subcategory_persona_map[subcategory.lower()]
                logger.info(f"Subcategory-based selection: {subcategory} → {selected}")
                return selected

        # Fallback по количеству новостей
        if news_count <= 3:
            logger.info(f"Few news items ({news_count}), selecting telegram_blogger")
            return "telegram_blogger"
        elif news_count >= 8:
            logger.info(f"Many news items ({news_count}), selecting economist_analyst")
            return "economist_analyst"
        else:
            logger.info(f"Default selection for category {category}: atlantic_writer")
            return "atlantic_writer"

    def get_persona_config(self, persona_id: str) -> Dict[str, Any]:
        """
        Получает конфигурацию персоны.

        Args:
            persona_id: ID персоны

        Returns:
            Словарь с конфигурацией персоны
        """
        if persona_id not in EDITORIAL_PERSONAS:
            logger.warning(f"Unknown persona_id: {persona_id}, using default")
            persona_id = "atlantic_writer"

        return EDITORIAL_PERSONAS[persona_id].copy()

    def get_persona_prompt_context(self, persona_id: str) -> str:
        """
        Генерирует контекст для промпта на основе персоны.

        Args:
            persona_id: ID персоны

        Returns:
            Строка с контекстом для промпта
        """
        config = self.get_persona_config(persona_id)

        context_parts = [
            f"Ты пишешь как {config['name']}.",
            f"Стиль: {config['description']}.",
            f"Характеристики: {', '.join(config['characteristics'])}.",
            f"Длина предложений: {config['sentence_length']}.",
        ]

        # Дополнительные инструкции по стилю
        style_instructions = {
            "reuters_editor": "Излагай факты кратко и нейтрально. Избегай личных оценок.",
            "economist_analyst": "Предоставляй глубокий анализ причин и следствий событий.",
            "atlantic_writer": "Используй живые метафоры и рассказывай истории.",
            "telegram_blogger": "Пиши просто и дружелюбно, как в личном блоге.",
            "bloomberg_trader": "Фокусируйся на данных, цифрах и рыночных последствиях.",
            "tech_crunch_reporter": "Подчеркивай инновации и технологические прорывы.",
        }

        if persona_id in style_instructions:
            context_parts.append(style_instructions[persona_id])

        return " ".join(context_parts)


def select_persona_for_context(
    category: str,
    subcategory: Optional[str] = None,
    urgency: float = 0.5,
    complexity: float = 0.5,
    news_count: int = 5,
    avg_importance: float = 0.5,
) -> tuple[str, Dict[str, Any]]:
    """
    Удобная функция для выбора персоны и получения её конфигурации.

    Args:
        category: Категория новостей
        subcategory: Подкатегория (optional)
        urgency: Срочность (0.0-1.0)
        complexity: Сложность анализа (0.0-1.0)
        news_count: Количество новостей
        avg_importance: Средняя важность новостей

    Returns:
        Tuple: (persona_id, persona_config)
    """
    selector = PersonaSelector()
    persona_id = selector.select_persona(category, subcategory, urgency, complexity, news_count, avg_importance)
    persona_config = selector.get_persona_config(persona_id)

    return persona_id, persona_config

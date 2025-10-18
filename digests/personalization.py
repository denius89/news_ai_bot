"""
Система персонализации дайджестов.

Адаптирует стиль, тон и контент под конкретного пользователя или аудиторию.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """Профиль пользователя для персонализации."""

    # Основные параметры
    experience_level: str = "intermediate"  # beginner, intermediate, expert
    interests: List[str] = None  # конкретные интересы
    preferred_style: str = "analytical"  # analytical, business, meme
    preferred_length: str = "medium"  # short, medium, long
    preferred_tone: str = "neutral"  # neutral, formal, casual

    # Поведенческие метрики
    avg_reading_time: Optional[float] = None  # секунды на дайджест
    preferred_topics: List[str] = None  # самые читаемые темы
    feedback_history: List[float] = None  # история оценок

    # Технические предпочтения
    wants_deep_analysis: bool = True
    wants_context: bool = True
    wants_predictions: bool = True
    wants_events: bool = True

    def __post_init__(self):
        if self.interests is None:
            self.interests = []
        if self.preferred_topics is None:
            self.preferred_topics = []
        if self.feedback_history is None:
            self.feedback_history = []


class PersonalizedDigestGenerator:
    """Генератор персонализированных дайджестов."""

    def __init__(self):
        self.audience_profiles = {
            "beginner": {
                "style": "explanatory",
                "tone": "friendly",
                "length": "medium",
                "technical_depth": "low",
                "additions": ["glossary", "context", "simple_explanations"],
            },
            "intermediate": {
                "style": "analytical",
                "tone": "neutral",
                "length": "medium",
                "technical_depth": "medium",
                "additions": ["analysis", "context", "trends"],
            },
            "expert": {
                "style": "technical",
                "tone": "formal",
                "length": "long",
                "technical_depth": "high",
                "additions": ["deep_analysis", "data", "expert_insights"],
            },
            "business": {
                "style": "business",
                "tone": "professional",
                "length": "short",
                "technical_depth": "medium",
                "additions": ["market_impact", "financial_data", "executive_summary"],
            },
            "general": {
                "style": "analytical",
                "tone": "neutral",
                "length": "medium",
                "technical_depth": "medium",
                "additions": ["context", "analysis"],
            },
        }

    def adapt_for_user(self, user_profile: Optional[UserProfile] = None, audience: str = "general") -> Dict[str, Any]:
        """
        Адаптировать параметры генерации под пользователя или аудиторию.

        Args:
            user_profile: Профиль конкретного пользователя
            audience: Тип аудитории если профиль не указан

        Returns:
            Адаптированные параметры для генерации
        """

        if user_profile:
            return self._adapt_for_personal_profile(user_profile)
        else:
            return self._adapt_for_audience(audience)

    def _adapt_for_personal_profile(self, profile: UserProfile) -> Dict[str, Any]:
        """Адаптация под персональный профиль пользователя."""

        # Базовые настройки
        config = {
            "style": profile.preferred_style,
            "tone": profile.preferred_tone,
            "length": profile.preferred_length,
            "max_words": self._get_length_words(profile.preferred_length),
            "technical_depth": self._get_technical_depth(profile.experience_level),
            "additions": [],
        }

        # Адаптация под опыт
        if profile.experience_level == "beginner":
            config.update(
                {
                    "additions": ["simple_explanations", "context", "glossary"],
                    "tone": "friendly" if profile.preferred_tone == "neutral" else profile.preferred_tone,
                    "technical_depth": "low",
                }
            )
        elif profile.experience_level == "expert":
            config.update(
                {"additions": ["deep_analysis", "expert_insights", "technical_details"], "technical_depth": "high"}
            )

        # Адаптация под предпочтения
        if profile.wants_deep_analysis:
            config["additions"].append("deep_analysis")

        if profile.wants_context:
            config["additions"].append("context")

        if profile.wants_predictions:
            config["additions"].append("predictions")

        if profile.wants_events:
            config["additions"].append("events")

        # Адаптация под интересы
        if profile.interests:
            config["focus_areas"] = profile.interests

        # Адаптация под историю оценок
        if profile.feedback_history and len(profile.feedback_history) > 3:
            avg_feedback = sum(profile.feedback_history[-10:]) / len(profile.feedback_history[-10:])
            if avg_feedback < 0.6:  # Низкие оценки
                config["additions"].extend(["simplify", "more_context"])
                config["tone"] = "friendly"
            elif avg_feedback > 0.8:  # Высокие оценки
                config["additions"].append("advanced_content")

        return config

    def _adapt_for_audience(self, audience: str) -> Dict[str, Any]:
        """Адаптация под тип аудитории."""

        profile = self.audience_profiles.get(audience, self.audience_profiles["general"])

        # Маппинг на поддерживаемые prompts_v2 значения
        style_mapping = {
            "explanatory": "explanatory",
            "technical": "technical",
            "business": "business",
            "analytical": "analytical",
            "newsroom": "newsroom",
            "magazine": "magazine",
            "casual": "casual",
        }

        tone_mapping = {"friendly": "neutral", "formal": "neutral", "professional": "neutral", "neutral": "neutral"}

        audience_mapping = {
            "beginner": "general",
            "intermediate": "general",
            "expert": "pro",
            "business": "pro",
            "general": "general",
        }

        # Получаем стиль с fallback
        mapped_style = style_mapping.get(profile["style"], "analytical")

        # Дополнительная проверка валидности стиля
        valid_styles = {"explanatory", "technical", "business", "analytical", "newsroom", "magazine", "casual"}
        if mapped_style not in valid_styles:
            mapped_style = "analytical"

        return {
            "style": mapped_style,
            "tone": tone_mapping.get(profile["tone"], "neutral"),
            "audience": audience_mapping.get(audience, "general"),
            "length": profile["length"],
            "max_words": self._get_length_words(profile["length"]),
            "technical_depth": profile["technical_depth"],
            "additions": profile["additions"],
        }

    def _get_length_words(self, length: str) -> int:
        """Получить количество слов для длины."""
        length_map = {"short": 300, "medium": 600, "long": 1000}
        return length_map.get(length, 600)

    def _get_technical_depth(self, experience_level: str) -> str:
        """Получить уровень технической глубины."""
        depth_map = {"beginner": "low", "intermediate": "medium", "expert": "high"}
        return depth_map.get(experience_level, "medium")

    def create_personalized_prompt_additions(
        self, config: Dict[str, Any], category: str, subcategory: Optional[str] = None
    ) -> str:
        """
        Создать дополнительные инструкции для промпта на основе персонализации.

        Args:
            config: Конфигурация персонализации
            category: Категория новостей
            subcategory: Подкатегория новостей

        Returns:
            Дополнительные инструкции для промпта
        """

        additions = []

        # Стиль и тон
        if config.get("tone") == "friendly":
            additions.append("Используй дружелюбный и понятный тон")
        elif config.get("tone") == "formal":
            additions.append("Используй формальный, деловой тон")

        # Техническая глубина
        tech_depth = config.get("technical_depth", "medium")
        if tech_depth == "low":
            additions.append("Объясняй сложные термины простыми словами")
        elif tech_depth == "high":
            additions.append("Используй профессиональную терминологию и углубленный анализ")

        # Добавления
        config_additions = config.get("additions", [])

        if "simple_explanations" in config_additions:
            additions.append("Включи простые объяснения ключевых концепций")

        if "context" in config_additions:
            additions.append("Добавь исторический контекст и предысторию событий")

        if "deep_analysis" in config_additions:
            additions.append("Проведи глубокий анализ причин и следствий")

        if "predictions" in config_additions:
            additions.append("Добавь прогнозы развития ситуации")

        if "events" in config_additions:
            additions.append("Упомяни релевантные предстоящие события")

        if "glossary" in config_additions:
            additions.append("Включи краткие определения важных терминов")

        if "market_impact" in config_additions:
            additions.append("Акцентируй внимание на влиянии на рынок")

        if "financial_data" in config_additions:
            additions.append("Используй конкретные финансовые данные и цифры")

        # Длина
        max_words = config.get("max_words", 600)
        additions.append(f"Целевая длина: до {max_words} слов")

        if additions:
            return "\n".join([f"• {addition}" for addition in additions])

        return ""


# Convenience functions
def get_user_profile_from_preferences(
    user_preferences: Optional[Dict[str, Any]] = None, feedback_history: Optional[List[float]] = None
) -> UserProfile:
    """
    Создать профиль пользователя на основе предпочтений и истории.

    Args:
        user_preferences: Предпочтения пользователя из БД
        feedback_history: История оценок дайджестов

    Returns:
        Профиль пользователя
    """

    profile = UserProfile()

    if user_preferences:
        # Определить опыт на основе активности
        if feedback_history and len(feedback_history) > 10:
            profile.experience_level = "expert"
        elif feedback_history and len(feedback_history) > 3:
            profile.experience_level = "intermediate"
        else:
            profile.experience_level = "beginner"

        # Интересы из предпочтений категорий
        if isinstance(user_preferences, dict):
            profile.interests = [cat for cat, subs in user_preferences.items() if subs is not None and len(subs) > 0]

        profile.feedback_history = feedback_history or []

    return profile


def personalize_digest_config(user_profile: Optional[UserProfile] = None, audience: str = "general") -> Dict[str, Any]:
    """
    Получить персонализированную конфигурацию для генерации дайджеста.

    Args:
        user_profile: Профиль пользователя
        audience: Тип аудитории

    Returns:
        Персонализированная конфигурация
    """

    generator = PersonalizedDigestGenerator()
    return generator.adapt_for_user(user_profile, audience)

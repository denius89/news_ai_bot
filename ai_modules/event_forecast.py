"""
Event Forecast Engine for PulseAI.

This module provides AI-powered forecasting for event outcomes,
impact analysis, and probability assessments.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from ai_modules.metrics import get_metrics

logger = logging.getLogger("event_forecast")


class ImpactType(Enum):
    """Enum for impact types."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class EventForecast:
    """Represents AI-generated forecast for an event."""

    event_id: int
    impact: ImpactType
    confidence: float
    summary: str
    market_reaction: str
    probability_outcomes: List[Tuple[str, float]]
    risk_factors: List[str]
    opportunities: List[str]
    generated_at: datetime


class EventForecastEngine:
    """
    AI-powered event forecast generator.

    Features:
    - Predicts event outcomes and market impact
    - Generates confidence scores
    - Identifies risk factors and opportunities
    - Provides probability assessments
    """

    def __init__(self):
        """Initialize event forecast engine."""
        self.metrics = get_metrics()

        # Impact prediction patterns
        self.impact_patterns = {
            "crypto": {
                "positive_keywords": ["upgrade", "launch", "partnership", "adoption", "approval", "listing"],
                "negative_keywords": ["hack", "regulation", "ban", "crash", "scam", "delay"],
                "neutral_keywords": ["meeting", "announcement", "update", "report", "conference"],
            },
            "markets": {
                "positive_keywords": ["rate cut", "stimulus", "growth", "recovery", "expansion", "positive"],
                "negative_keywords": ["rate hike", "recession", "decline", "crisis", "inflation", "negative"],
                "neutral_keywords": ["meeting", "decision", "data", "report", "policy", "maintain"],
            },
            "sports": {
                "positive_keywords": ["championship", "victory", "record", "achievement", "success", "win"],
                "negative_keywords": ["defeat", "injury", "scandal", "ban", "suspension", "loss"],
                "neutral_keywords": ["match", "game", "tournament", "season", "competition", "event"],
            },
            "tech": {
                "positive_keywords": ["breakthrough", "innovation", "launch", "success", "growth", "advancement"],
                "negative_keywords": ["security breach", "failure", "delay", "bug", "vulnerability", "outage"],
                "neutral_keywords": ["release", "update", "announcement", "conference", "development", "feature"],
            },
            "world": {
                "positive_keywords": ["agreement", "peace", "cooperation", "progress", "resolution", "success"],
                "negative_keywords": ["conflict", "crisis", "war", "tension", "dispute", "escalation"],
                "neutral_keywords": ["meeting", "summit", "discussion", "policy", "election", "decision"],
            },
        }

        # Market reaction templates
        self.market_reactions = {
            ImpactType.POSITIVE: [
                "Ожидается положительная реакция рынков с ростом ключевых индикаторов.",
                "Потенциальный рост интереса инвесторов и улучшение настроений.",
                "Возможное укрепление позиций в соответствующих секторах.",
            ],
            ImpactType.NEGATIVE: [
                "Возможная негативная реакция рынков с повышенной волатильностью.",
                "Потенциальное снижение инвесторского интереса и ухудшение настроений.",
                "Возможное ослабление позиций в соответствующих секторах.",
            ],
            ImpactType.NEUTRAL: [
                "Ожидается нейтральная реакция рынков без значительных изменений.",
                "Минимальное влияние на рыночные настроения и инвесторский интерес.",
                "Стабильность в соответствующих секторах без резких движений.",
            ],
            ImpactType.MIXED: [
                "Смешанная реакция рынков с дифференцированным влиянием по секторам.",
                "Различное влияние на различные группы активов и инвесторов.",
                "Неоднозначная реакция с потенциальными возможностями и рисками.",
            ],
        }

        logger.info("EventForecastEngine initialized")

    async def generate_event_forecast(self, event: Dict[str, Any]) -> EventForecast:
        """
        Generate AI forecast for an event.

        Args:
            event: Event dictionary with title, category, description, etc.

        Returns:
            EventForecast with impact prediction and analysis
        """
        try:
            event_id = event.get("id", 0)
            title = event.get("title", "")
            category = event.get("category", "unknown")
            description = event.get("description", "")
            importance = event.get("importance", 0.5)

            logger.debug(f"Generating forecast for event: {title}")

            # Predict impact
            impact = self._predict_impact(title, category, description, importance)

            # Calculate confidence
            confidence = self._calculate_confidence(title, category, importance)

            # Generate summary
            summary = self._generate_summary(title, category, impact, confidence)

            # Assess market reaction
            market_reaction = self._assess_market_reaction(impact, category, importance)

            # Generate probability outcomes
            probability_outcomes = self._generate_probability_outcomes(title, category, impact)

            # Identify risk factors
            risk_factors = self._identify_risk_factors(title, category, importance)

            # Identify opportunities
            opportunities = self._identify_opportunities(title, category, impact)

            # Create forecast object
            forecast = EventForecast(
                event_id=event_id,
                impact=impact,
                confidence=confidence,
                summary=summary,
                market_reaction=market_reaction,
                probability_outcomes=probability_outcomes,
                risk_factors=risk_factors,
                opportunities=opportunities,
                generated_at=datetime.now(timezone.utc),
            )

            # Update metrics
            self.metrics.increment_event_forecasts_total()
            self.metrics.update_event_forecast_confidence_avg(confidence)

            logger.info(f"Generated forecast for event {event_id}: impact={impact.value}, confidence={confidence:.2f}")

            return forecast

        except Exception as e:
            logger.error(f"Error generating event forecast: {e}")

            # Return fallback forecast
            return EventForecast(
                event_id=event.get("id", 0),
                impact=ImpactType.NEUTRAL,
                confidence=0.3,
                summary="Прогноз события требует дополнительного анализа.",
                market_reaction="Влияние на рынки оценивается.",
                probability_outcomes=[],
                risk_factors=[],
                opportunities=[],
                generated_at=datetime.now(timezone.utc),
            )

    def _predict_impact(self, title: str, category: str, description: str, importance: float) -> ImpactType:
        """Predict the impact of an event."""
        text = f"{title} {description}".lower()

        # Get category-specific patterns
        patterns = self.impact_patterns.get(category, {})
        positive_keywords = patterns.get("positive_keywords", [])
        negative_keywords = patterns.get("negative_keywords", [])
        neutral_keywords = patterns.get("neutral_keywords", [])

        # Count keyword matches
        positive_score = sum(1 for keyword in positive_keywords if keyword in text)
        negative_score = sum(1 for keyword in negative_keywords if keyword in text)
        neutral_score = sum(1 for keyword in neutral_keywords if keyword in text)

        # Adjust scores based on importance
        positive_score *= 1 + importance
        negative_score *= 1 + importance

        # Determine impact
        if positive_score > negative_score and positive_score > neutral_score:
            if positive_score > negative_score * 1.5:
                return ImpactType.POSITIVE
            else:
                return ImpactType.MIXED
        elif negative_score > positive_score and negative_score > neutral_score:
            if negative_score > positive_score * 1.5:
                return ImpactType.NEGATIVE
            else:
                return ImpactType.MIXED
        else:
            return ImpactType.NEUTRAL

    def _calculate_confidence(self, title: str, category: str, importance: float) -> float:
        """Calculate confidence score for the forecast."""
        confidence = 0.5  # Base confidence

        # Higher confidence for high-importance events
        if importance >= 0.8:
            confidence += 0.2
        elif importance >= 0.6:
            confidence += 0.1

        # Higher confidence for events with clear indicators
        title_lower = title.lower()

        # Strong positive indicators
        strong_positive = ["approval", "launch", "breakthrough", "success", "achievement"]
        if any(word in title_lower for word in strong_positive):
            confidence += 0.1

        # Strong negative indicators
        strong_negative = ["crisis", "crash", "hack", "scandal", "failure"]
        if any(word in title_lower for word in strong_negative):
            confidence += 0.1

        # Central bank or official decisions
        official_keywords = ["fomc", "ecb", "boe", "decision", "announcement", "policy"]
        if any(word in title_lower for word in official_keywords):
            confidence += 0.1

        # Crypto-specific confidence boosters
        if category == "crypto":
            crypto_keywords = ["upgrade", "merge", "listing", "partnership"]
            if any(word in title_lower for word in crypto_keywords):
                confidence += 0.05

        return min(1.0, max(0.0, confidence))

    def _generate_summary(self, title: str, category: str, impact: ImpactType, confidence: float) -> str:
        """Generate forecast summary."""
        confidence_percent = int(confidence * 100)

        if impact == ImpactType.POSITIVE:
            return f"Ожидается положительное влияние на {category} сектор с уверенностью {confidence_percent}%."
        elif impact == ImpactType.NEGATIVE:
            return f"Потенциальное негативное влияние на {category} сектор с уверенностью {confidence_percent}%."
        elif impact == ImpactType.MIXED:
            return f"Смешанное влияние на {category} сектор с уверенностью {confidence_percent}%."
        else:
            return f"Нейтральное влияние на {category} сектор с уверенностью {confidence_percent}%."

    def _assess_market_reaction(self, impact: ImpactType, category: str, importance: float) -> str:
        """Assess potential market reaction."""
        reactions = self.market_reactions.get(impact, [])

        # Select reaction based on importance
        if importance >= 0.8:
            reaction = reactions[0] if reactions else "Значительное влияние на рынки."
        elif importance >= 0.6:
            reaction = (
                reactions[1] if len(reactions) > 1 else reactions[0] if reactions else "Умеренное влияние на рынки."
            )
        else:
            reaction = (
                reactions[2] if len(reactions) > 2 else reactions[0] if reactions else "Ограниченное влияние на рынки."
            )

        return reaction

    def _generate_probability_outcomes(self, title: str, category: str, impact: ImpactType) -> List[Tuple[str, float]]:
        """Generate probability outcomes for the event."""
        outcomes = []

        if impact == ImpactType.POSITIVE:
            outcomes = [
                ("Значительное улучшение ситуации", 0.4),
                ("Умеренное положительное влияние", 0.35),
                ("Минимальное улучшение", 0.2),
                ("Нейтральный исход", 0.05),
            ]
        elif impact == ImpactType.NEGATIVE:
            outcomes = [
                ("Значительное ухудшение ситуации", 0.4),
                ("Умеренное негативное влияние", 0.35),
                ("Минимальное ухудшение", 0.2),
                ("Нейтральный исход", 0.05),
            ]
        elif impact == ImpactType.MIXED:
            outcomes = [
                ("Смешанные результаты", 0.4),
                ("Положительные аспекты", 0.3),
                ("Негативные аспекты", 0.2),
                ("Нейтральный исход", 0.1),
            ]
        else:  # NEUTRAL
            outcomes = [
                ("Стабильное развитие", 0.5),
                ("Незначительные изменения", 0.3),
                ("Неожиданные результаты", 0.2),
            ]

        return outcomes

    def _identify_risk_factors(self, title: str, category: str, importance: float) -> List[str]:
        """Identify potential risk factors."""
        risks = []

        # General risk factors
        if importance >= 0.8:
            risks.append("Высокая важность события увеличивает потенциальные риски")

        # Category-specific risks
        if category == "crypto":
            risks.extend(
                [
                    "Волатильность криптовалютных рынков",
                    "Регулятивные неопределенности",
                    "Технические риски блокчейн технологий",
                ]
            )
        elif category == "markets":
            risks.extend(["Макроэкономические факторы", "Валютные риски", "Инфляционное давление"])
        elif category == "sports":
            risks.extend(["Неожиданные результаты", "Травмы игроков", "Внешние факторы"])
        elif category == "tech":
            risks.extend(["Технические проблемы", "Конкурентные риски", "Задержки в разработке"])
        elif category == "world":
            risks.extend(["Геополитические факторы", "Экономические санкции", "Социальные волнения"])

        return risks[:3]  # Limit to 3 most relevant risks

    def _identify_opportunities(self, title: str, category: str, impact: ImpactType) -> List[str]:
        """Identify potential opportunities."""
        opportunities = []

        # Impact-based opportunities
        if impact == ImpactType.POSITIVE:
            opportunities.append("Потенциальный рост инвестиционных возможностей")
            opportunities.append("Улучшение рыночных условий")
        elif impact == ImpactType.MIXED:
            opportunities.append("Дифференцированные инвестиционные возможности")
            opportunities.append("Арбитражные возможности")

        # Category-specific opportunities
        if category == "crypto":
            opportunities.extend(["Раннее инвестирование в новые технологии", "DeFi и NFT возможности"])
        elif category == "markets":
            opportunities.extend(["Арбитражные возможности", "Хеджирование позиций"])
        elif category == "sports":
            opportunities.extend(["Спортивные ставки и аналитика", "Медиа и рекламные возможности"])
        elif category == "tech":
            opportunities.extend(["Инвестиции в инновационные компании", "Партнерские возможности"])
        elif category == "world":
            opportunities.extend(["Международные инвестиции", "Валютные возможности"])

        return opportunities[:3]  # Limit to 3 most relevant opportunities


# Global forecast engine instance
_forecast_engine_instance: Optional[EventForecastEngine] = None


def get_event_forecast_engine() -> EventForecastEngine:
    """Get global event forecast engine instance."""
    global _forecast_engine_instance
    if _forecast_engine_instance is None:
        _forecast_engine_instance = EventForecastEngine()
    return _forecast_engine_instance


async def generate_event_forecast(event: Dict[str, Any]) -> EventForecast:
    """
    Convenience function to generate forecast for an event.

    Args:
        event: Event dictionary

    Returns:
        EventForecast with impact prediction and analysis
    """
    engine = get_event_forecast_engine()
    return await engine.generate_event_forecast(event)

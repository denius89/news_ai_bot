"""
Event Intelligence Service for PulseAI.

This module integrates event context and forecasts into a unified system
and prepares data for Telegram and WebApp integration.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ai_modules.event_context import get_event_context_engine, EventContext
from ai_modules.event_forecast import get_event_forecast_engine, EventForecast, ImpactType
from database.events_service import get_events_service
from ai_modules.metrics import get_metrics

logger = logging.getLogger("event_intelligence")


@dataclass
class IntelligentEvent:
    """Represents an event with AI-generated context and forecast."""

    event_id: int
    title: str
    category: str
    subcategory: str
    starts_at: datetime
    ends_at: Optional[datetime]
    source: str
    link: str
    importance: float
    description: Optional[str]
    context: EventContext
    forecast: EventForecast
    intelligence_score: float


class EventIntelligenceService:
    """
    Unified event intelligence service.

    Features:
    - Analyzes upcoming events with AI context and forecasts
    - Generates intelligent event digests
    - Exports data for UI components
    - Integrates with existing PulseAI systems
    """

    def __init__(self):
        """Initialize event intelligence service."""
        self.context_engine = get_event_context_engine()
        self.forecast_engine = get_event_forecast_engine()
        self.events_service = get_events_service()
        self.metrics = get_metrics()

        logger.info("EventIntelligenceService initialized")

    async def analyze_upcoming_events(
        self,
        days_ahead: int = 30,
        category: Optional[str] = None,
        min_importance: float = 0.0,
        min_confidence: float = 0.6,
    ) -> List[IntelligentEvent]:
        """
        Analyze upcoming events with AI context and forecasts.

        Args:
            days_ahead: Number of days to look ahead
            category: Filter by category
            min_importance: Minimum importance threshold
            min_confidence: Minimum confidence threshold for AI analysis

        Returns:
            List of IntelligentEvent objects with AI analysis
        """
        try:
            logger.info(f"Analyzing upcoming events: {days_ahead} days, category={category}")

            # Get upcoming events from database
            events = await self.events_service.get_upcoming_events(
                days_ahead=days_ahead, category=category, min_importance=min_importance
            )

            logger.info(f"Found {len(events)} events to analyze")

            # Process events with AI analysis
            intelligent_events = []

            for event_record in events:
                try:
                    # Convert to dictionary format
                    event_dict = {
                        "id": event_record.id,
                        "title": event_record.title,
                        "category": event_record.category,
                        "subcategory": event_record.subcategory,
                        "starts_at": event_record.starts_at,
                        "ends_at": event_record.ends_at,
                        "source": event_record.source,
                        "link": event_record.link,
                        "importance": event_record.importance,
                        "description": event_record.description,
                        "location": event_record.location,
                        "organizer": event_record.organizer,
                    }

                    # Generate AI context and forecast
                    context, forecast = await asyncio.gather(
                        self.context_engine.generate_event_context(event_dict),
                        self.forecast_engine.generate_event_forecast(event_dict),
                    )

                    # Filter by confidence threshold
                    if context.confidence >= min_confidence and forecast.confidence >= min_confidence:
                        # Calculate intelligence score
                        intelligence_score = self._calculate_intelligence_score(
                            event_record.importance, context.confidence, forecast.confidence
                        )

                        # Create intelligent event
                        intelligent_event = IntelligentEvent(
                            event_id=event_record.id,
                            title=event_record.title,
                            category=event_record.category,
                            subcategory=event_record.subcategory,
                            starts_at=event_record.starts_at,
                            ends_at=event_record.ends_at,
                            source=event_record.source,
                            link=event_record.link,
                            importance=event_record.importance,
                            description=event_record.description,
                            context=context,
                            forecast=forecast,
                            intelligence_score=intelligence_score,
                        )

                        intelligent_events.append(intelligent_event)
                        logger.debug(f"Analyzed event: {event_record.title} (score: {intelligence_score:.2f})")

                except Exception as e:
                    logger.error(f"Error analyzing event {event_record.id}: {e}")
                    continue

            # Sort by intelligence score (highest first)
            intelligent_events.sort(key=lambda x: x.intelligence_score, reverse=True)

            logger.info(f"Successfully analyzed {len(intelligent_events)} events with AI")

            # Update metrics
            self.metrics.increment_events_analyzed_total(len(intelligent_events))

            return intelligent_events

        except Exception as e:
            logger.error(f"Error analyzing upcoming events: {e}")
            return []

    async def generate_ai_event_digest(
        self, days_ahead: int = 7, max_events: int = 5, min_importance: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate AI-powered event digest for Telegram.

        Args:
            days_ahead: Number of days to look ahead
            max_events: Maximum number of events to include
            min_importance: Minimum importance threshold

        Returns:
            Dictionary with digest content and metadata
        """
        try:
            logger.info(f"Generating AI event digest: {days_ahead} days, max {max_events} events")

            # Analyze upcoming events
            intelligent_events = await self.analyze_upcoming_events(
                days_ahead=days_ahead, min_importance=min_importance, min_confidence=0.6
            )

            # Take top events
            top_events = intelligent_events[:max_events]

            if not top_events:
                return {
                    "content": "📅 На ближайшие дни значимых событий не запланировано.",
                    "events_count": 0,
                    "total_analyzed": len(intelligent_events),
                }

            # Generate digest content
            digest_lines = ["📅 **Предстоящие события:**"]

            for event in top_events:
                # Format event line
                category_emoji = self._get_category_emoji(event.category)
                impact_emoji = self._get_impact_emoji(event.forecast.impact)
                confidence_percent = int(event.forecast.confidence * 100)

                event_line = (
                    f"{category_emoji} {event.title} → "
                    f"{impact_emoji} {self._get_impact_text(event.forecast.impact)} "
                    f"({confidence_percent}%)"
                )

                digest_lines.append(event_line)

            # Add summary
            if len(intelligent_events) > max_events:
                digest_lines.append(f"\n_Всего проанализировано: {len(intelligent_events)} событий_")

            digest_content = "\n".join(digest_lines)

            logger.info(f"Generated digest with {len(top_events)} events")

            # Update metrics
            self.metrics.increment_event_digests_generated_total()

            return {
                "content": digest_content,
                "events_count": len(top_events),
                "total_analyzed": len(intelligent_events),
                "events": [
                    {
                        "title": event.title,
                        "category": event.category,
                        "impact": event.forecast.impact.value,
                        "confidence": event.forecast.confidence,
                        "intelligence_score": event.intelligence_score,
                    }
                    for event in top_events
                ],
            }

        except Exception as e:
            logger.error(f"Error generating AI event digest: {e}")
            return {"content": "📅 Ошибка при анализе предстоящих событий.", "events_count": 0, "total_analyzed": 0}

    async def export_to_calendar_json(self, days_ahead: int = 30, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Export intelligent events data for UI components.

        Args:
            days_ahead: Number of days to look ahead
            category: Filter by category

        Returns:
            Dictionary with calendar data for UI
        """
        try:
            logger.info(f"Exporting calendar data: {days_ahead} days, category={category}")

            # Analyze upcoming events
            intelligent_events = await self.analyze_upcoming_events(
                days_ahead=days_ahead, category=category, min_confidence=0.5
            )

            # Group events by date
            events_by_date = {}

            for event in intelligent_events:
                date_key = event.starts_at.date().isoformat()

                if date_key not in events_by_date:
                    events_by_date[date_key] = []

                # Format event for UI
                ui_event = {
                    "id": event.event_id,
                    "title": event.title,
                    "category": event.category,
                    "subcategory": event.subcategory,
                    "starts_at": event.starts_at.isoformat(),
                    "ends_at": event.ends_at.isoformat() if event.ends_at else None,
                    "source": event.source,
                    "link": event.link,
                    "importance": event.importance,
                    "description": event.description,
                    "context": {
                        "text": event.context.context,
                        "related_trends": event.context.related_trends,
                        "significance": event.context.significance_explanation,
                        "market_impact": event.context.market_impact,
                        "confidence": event.context.confidence,
                    },
                    "forecast": {
                        "impact": event.forecast.impact.value,
                        "confidence": event.forecast.confidence,
                        "summary": event.forecast.summary,
                        "market_reaction": event.forecast.market_reaction,
                        "probability_outcomes": [
                            {"outcome": outcome, "probability": prob}
                            for outcome, prob in event.forecast.probability_outcomes
                        ],
                        "risk_factors": event.forecast.risk_factors,
                        "opportunities": event.forecast.opportunities,
                    },
                    "intelligence_score": event.intelligence_score,
                }

                events_by_date[date_key].append(ui_event)

            # Sort events within each date by intelligence score
            for date_key in events_by_date:
                events_by_date[date_key].sort(key=lambda x: x["intelligence_score"], reverse=True)

            logger.info(f"Exported {len(intelligent_events)} events for calendar UI")

            return {
                "events_by_date": events_by_date,
                "total_events": len(intelligent_events),
                "date_range": {
                    "start": datetime.now(timezone.utc).date().isoformat(),
                    "end": (datetime.now(timezone.utc) + timedelta(days=days_ahead)).date().isoformat(),
                },
                "categories": self._get_available_categories(intelligent_events),
                "exported_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error exporting calendar data: {e}")
            return {"events_by_date": {}, "total_events": 0, "error": str(e)}

    def _calculate_intelligence_score(
        self, importance: float, context_confidence: float, forecast_confidence: float
    ) -> float:
        """Calculate overall intelligence score for an event."""
        # Weighted combination of importance and AI confidences
        intelligence_score = importance * 0.4 + context_confidence * 0.3 + forecast_confidence * 0.3

        return round(intelligence_score, 3)

    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for event category."""
        emojis = {"crypto": "🪙", "markets": "📈", "sports": "🏀", "tech": "💻", "world": "🌍"}
        return emojis.get(category, "📅")

    def _get_impact_emoji(self, impact: ImpactType) -> str:
        """Get emoji for forecast impact."""
        emojis = {ImpactType.POSITIVE: "📈", ImpactType.NEGATIVE: "📉", ImpactType.NEUTRAL: "⚖️", ImpactType.MIXED: "🔄"}
        return emojis.get(impact, "❓")

    def _get_impact_text(self, impact: ImpactType) -> str:
        """Get text for forecast impact."""
        texts = {
            ImpactType.POSITIVE: "позитивное влияние",
            ImpactType.NEGATIVE: "негативное влияние",
            ImpactType.NEUTRAL: "нейтральное влияние",
            ImpactType.MIXED: "смешанное влияние",
        }
        return texts.get(impact, "неопределенное влияние")

    def _get_available_categories(self, events: List[IntelligentEvent]) -> List[str]:
        """Get list of available categories from events."""
        categories = set()
        for event in events:
            categories.add(event.category)
        return sorted(list(categories))


# Global service instance
_service_instance: Optional[EventIntelligenceService] = None


def get_event_intelligence_service() -> EventIntelligenceService:
    """Get global event intelligence service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = EventIntelligenceService()
    return _service_instance


async def analyze_upcoming_events(
    days_ahead: int = 30, category: Optional[str] = None, min_importance: float = 0.0, min_confidence: float = 0.6
) -> List[IntelligentEvent]:
    """
    Convenience function to analyze upcoming events.

    Args:
        days_ahead: Number of days to look ahead
        category: Filter by category
        min_importance: Minimum importance threshold
        min_confidence: Minimum confidence threshold

    Returns:
        List of IntelligentEvent objects
    """
    service = get_event_intelligence_service()
    return await service.analyze_upcoming_events(days_ahead, category, min_importance, min_confidence)


async def generate_ai_event_digest(
    days_ahead: int = 7, max_events: int = 5, min_importance: float = 0.7
) -> Dict[str, Any]:
    """
    Convenience function to generate AI event digest.

    Args:
        days_ahead: Number of days to look ahead
        max_events: Maximum number of events
        min_importance: Minimum importance threshold

    Returns:
        Dictionary with digest content
    """
    service = get_event_intelligence_service()
    return await service.generate_ai_event_digest(days_ahead, max_events, min_importance)

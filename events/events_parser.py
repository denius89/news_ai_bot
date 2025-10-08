"""
Events Parser for PulseAI.

This module provides unified event parsing and normalization
across different event providers and sources.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from core.reactor import reactor, Events

logger = logging.getLogger("events_parser")


@dataclass
class Event:
    """Represents a normalized event."""

    title: str
    category: str
    subcategory: str
    starts_at: datetime
    ends_at: Optional[datetime]
    source: str
    link: str
    importance: float
    description: Optional[str] = None
    location: Optional[str] = None
    organizer: Optional[str] = None


class EventsParser:
    """
    Unified events parser that aggregates events from multiple providers.

    Features:
    - Multi-provider event aggregation
    - Event normalization and deduplication
    - Importance scoring
    - Category classification
    """

    def __init__(self):
        """Initialize events parser."""
        self.providers = {}
        self._load_providers()

        logger.info("EventsParser initialized")

    def _load_providers(self) -> None:
        """Load available event providers."""
        try:
            from events.providers.coinmarketcal import CoinMarketCalProvider
            from events.providers.investing import InvestingProvider
            from events.providers.espn import ESPNProvider

            self.providers = {
                "coinmarketcal": CoinMarketCalProvider(),
                "investing": InvestingProvider(),
                "espn": ESPNProvider(),
            }

            logger.info(f"Loaded {len(self.providers)} event providers")

        except ImportError as e:
            logger.warning(f"Failed to load some providers: {e}")
            self.providers = {}

    async def fetch_events(
        self, start_date: datetime, end_date: datetime, providers: Optional[List[str]] = None
    ) -> List[Event]:
        """
        Fetch events from all providers within the specified date range.

        Args:
            start_date: Start date for event fetching
            end_date: End date for event fetching
            providers: List of provider names to use (None for all)

        Returns:
            List of normalized events
        """
        try:
            if providers is None:
                providers = list(self.providers.keys())

            # Fetch events from all providers in parallel
            tasks = []
            for provider_name in providers:
                if provider_name in self.providers:
                    task = self.providers[provider_name].fetch_events(start_date, end_date)
                    tasks.append(task)

            if not tasks:
                logger.warning("No providers available for event fetching")
                return []

            # Execute all fetches in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Combine and normalize results
            all_events = []
            for i, result in enumerate(results):
                provider_name = providers[i]

                if isinstance(result, Exception):
                    logger.error(f"Error fetching events from {provider_name}: {result}")
                    continue

                if isinstance(result, list):
                    all_events.extend(result)
                    logger.info(f"Fetched {len(result)} events from {provider_name}")
                else:
                    logger.warning(f"Unexpected result type from {provider_name}: {type(result)}")

            # Normalize and deduplicate events
            normalized_events = self._normalize_events(all_events)
            deduplicated_events = self._deduplicate_events(normalized_events)

            logger.info(
                f"Total events after normalization and deduplication: {len(deduplicated_events)}")

            # Эмитим событие о получении событий
            if deduplicated_events:
                reactor.emit_sync(
                    Events.EVENT_DETECTED,
                    {
                        "events_count": len(deduplicated_events),
                        "providers_used": providers,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

                # Эмитим каждое важное событие отдельно
                for event in deduplicated_events:
                    if event.importance > 0.7:  # Только важные события
                        reactor.emit_sync(
                            Events.EVENT_DETECTED,
                            {
                                "title": event.title,
                                "category": event.category,
                                "importance": event.importance,
                                "starts_at": event.starts_at.isoformat(),
                                "source": event.source,
                                "link": event.link,
                            },
                        )

            return deduplicated_events

        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return []

    def _normalize_events(self, events: List[Any]) -> List[Event]:
        """
        Normalize events from different providers to common format.

        Args:
            events: List of raw events from providers

        Returns:
            List of normalized Event objects
        """
        normalized = []

        for event_data in events:
            try:
                # Handle different input formats
                if isinstance(event_data, Event):
                    normalized.append(event_data)
                    continue

                if isinstance(event_data, dict):
                    event = self._dict_to_event(event_data)
                    if event:
                        normalized.append(event)
                        continue

                logger.warning(f"Unknown event format: {type(event_data)}")

            except Exception as e:
                logger.error(f"Error normalizing event: {e}")
                continue

        return normalized

    def _dict_to_event(self, event_dict: Dict[str, Any]) -> Optional[Event]:
        """
        Convert dictionary to Event object.

        Args:
            event_dict: Dictionary with event data

        Returns:
            Event object or None if conversion fails
        """
        try:
            # Required fields
            title = event_dict.get("title", "").strip()
            if not title:
                return None

            category = event_dict.get("category", "unknown").lower()
            subcategory = event_dict.get("subcategory", "general").lower()
            source = event_dict.get("source", "unknown")
            link = event_dict.get("link", "")
            importance = float(event_dict.get("importance", 0.5))

            # Date parsing
            starts_at = self._parse_datetime(event_dict.get("starts_at"))
            if not starts_at:
                return None

            ends_at = self._parse_datetime(event_dict.get("ends_at"))

            # Optional fields
            description = event_dict.get("description", "").strip() or None
            location = event_dict.get("location", "").strip() or None
            organizer = event_dict.get("organizer", "").strip() or None

            return Event(
                title=title,
                category=category,
                subcategory=subcategory,
                starts_at=starts_at,
                ends_at=ends_at,
                source=source,
                link=link,
                importance=importance,
                description=description,
                location=location,
                organizer=organizer,
            )

        except Exception as e:
            logger.error(f"Error converting dict to event: {e}")
            return None

    def _parse_datetime(self, date_str: Any) -> Optional[datetime]:
        """
        Parse datetime string to datetime object.

        Args:
            date_str: Date string in various formats

        Returns:
            datetime object or None if parsing fails
        """
        if not date_str:
            return None

        if isinstance(date_str, datetime):
            return date_str

        if isinstance(date_str, str):
            try:
                # Try ISO format first
                if "T" in date_str or "Z" in date_str:
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))

                # Try other common formats
                formats = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M",
                    "%Y-%m-%d",
                    "%d.%m.%Y %H:%M:%S",
                    "%d.%m.%Y %H:%M",
                    "%d.%m.%Y",
                ]

                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue

                logger.warning(f"Could not parse date: {date_str}")
                return None

            except Exception as e:
                logger.error(f"Error parsing date '{date_str}': {e}")
                return None

        return None

    def _deduplicate_events(self, events: List[Event]) -> List[Event]:
        """
        Remove duplicate events based on title, start time, and source.

        Args:
            events: List of events to deduplicate

        Returns:
            List of deduplicated events
        """
        seen = set()
        deduplicated = []

        for event in events:
            # Create a key for deduplication
            key = (event.title.lower().strip(), event.starts_at.isoformat(), event.source.lower())

            if key not in seen:
                seen.add(key)
                deduplicated.append(event)
            else:
                logger.debug(f"Removed duplicate event: {event.title}")

        return deduplicated

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about available providers.

        Returns:
            Dictionary with provider information
        """
        info = {}

        for name, provider in self.providers.items():
            try:
                provider_info = getattr(provider, "get_info", lambda: {})()
                info[name] = provider_info
            except Exception as e:
                logger.error(f"Error getting info for provider {name}: {e}")
                info[name] = {"error": str(e)}

        return info


# Global parser instance
_parser_instance: Optional[EventsParser] = None


def get_events_parser() -> EventsParser:
    """Get global events parser instance."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = EventsParser()
    return _parser_instance


async def fetch_events(start_date: datetime, end_date: datetime,
                       providers: Optional[List[str]] = None) -> List[Event]:
    """
    Convenience function to fetch events.

    Args:
        start_date: Start date for event fetching
        end_date: End date for event fetching
        providers: List of provider names to use

    Returns:
        List of normalized events
    """
    parser = get_events_parser()
    return await parser.fetch_events(start_date, end_date, providers)

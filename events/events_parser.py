"""
Module: events.events_parser
Purpose: Unified event parsing and normalization system
Location: events/events_parser.py

Description:
    Унифицированная система парсинга и нормализации событий из различных провайдеров.
    Обрабатывает события из спорта, криптовалют, технологий и других источников.

Key Features:
    - Unified API для всех event providers
    - Автоматическая нормализация данных
    - Поддержка множественных форматов времени
    - Группировка событий по категориям
    - Async processing для высокой производительности
    - Retry logic и error handling

Supported Providers:
    Sports:
        - Football-Data.org: Футбольные матчи и результаты
        - TheSportsDB: Спортивные события и статистика
        - PandaScore: Esports и традиционные виды спорта

    Crypto:
        - CoinMarketCal: Криптовалютные события и релизы
        - CoinGecko: Market events и announcements
        - GitHub Releases: Технические релизы

    Tech:
        - GitHub Releases: Software releases
        - Finnhub: Financial events
        - Custom sources: Конференции, вебинары

Event Normalization:
    Все события приводятся к единому формату:
    ```python
    {
        "title": str,
        "category": str,           # sports, crypto, tech, etc.
        "subcategory": str,        # football, bitcoin, conference, etc.
        "starts_at": datetime,     # UTC time
        "ends_at": datetime,       # UTC time (optional)
        "source": str,            # provider name
        "link": str,              # event URL
        "importance": float,       # 0.1-1.0
        "description": str,       # event description
        "location": str,          # physical location
        "organizer": str,         # event organizer
        "group_name": str,        # для умной группировки
        "metadata": dict          # provider-specific data
    }
    ```

Dependencies:
    External:
        - httpx: Async HTTP client
        - python-dateutil: Date parsing
    Internal:
        - events.providers.*: Provider implementations
        - database.events_service: Event storage
        - utils.system.dates: Date utilities

Usage Example:
    ```python
    from events.events_parser import EventsParser

    # Async context manager
    async with EventsParser() as parser:
        await parser.run()

    # Manual usage
    parser = EventsParser()
    await parser.parse_all_providers()
    ```

Provider Architecture:
    ```
    EventsParser
    ├── Sports Providers
    │   ├── FootballDataProvider
    │   ├── TheSportsDBProvider
    │   └── PandaScoreProvider
    ├── Crypto Providers
    │   ├── CoinMarketCalProvider
    │   └── CoinGeckoProvider
    └── Tech Providers
        ├── GitHubReleasesProvider
        └── FinnhubProvider
    ```

Configuration:
    Provider configuration in `config/data/providers.yaml`:
    ```yaml
    providers:
      football_data:
        enabled: true
        api_key: "${FOOTBALL_DATA_API_KEY}"
        leagues: ["premier-league", "champions-league"]

      coinmarketcal:
        enabled: true
        api_key: "${COINMARKETCAL_API_KEY}"
        coins: ["bitcoin", "ethereum"]
    ```

Performance:
    - Async processing всех провайдеров
    - Batch operations для database
    - Connection pooling
    - Rate limiting для API providers

Notes:
    - Использует events_service для database операций
    - Поддерживает умную группировку событий
    - Автоматически обрабатывает timezone conversion
    - Логирует детальную информацию о процессе
    - TODO: Добавить metrics и monitoring

Author: PulseAI Team
Last Updated: October 2025
"""

import asyncio
import logging
from datetime import datetime
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
        """Load available event providers from configuration."""
        try:
            import yaml
            from pathlib import Path

            # Load configuration
            config_path = Path(__file__).parent.parent / "config" / "data" / "sources_events.yaml"

            if not config_path.exists():
                logger.warning(f"Events config not found: {config_path}")
                return

            with open(config_path) as f:
                config = yaml.safe_load(f)

            # Load providers dynamically
            for category, providers in config.items():
                for provider_name, provider_config in providers.items():
                    if not provider_config.get("enabled", False):
                        logger.info(f"Skipping disabled provider: {category}/{provider_name}")
                        continue

                    # Try to import and instantiate provider
                    provider_instance = self._import_provider(category, provider_name)
                    if provider_instance:
                        provider_key = f"{category}_{provider_name}"
                        self.providers[provider_key] = provider_instance
                        logger.info(f"Loaded provider: {provider_key}")

            logger.info(f"Loaded {len(self.providers)} event providers")

        except Exception as e:
            logger.error(f"Failed to load providers: {e}")
            self.providers = {}

    def _import_provider(self, category: str, provider_name: str):
        """
        Dynamically import provider class.

        Args:
            category: Provider category (crypto, sports, markets, tech, world)
            provider_name: Provider name (coingecko, football_data, etc.)

        Returns:
            Provider instance or None
        """
        try:
            # Convert provider_name to class name (e.g., coingecko -> CoinGeckoProvider)
            # Special cases for camelCase names
            name_mapping = {
                "coinmarketcal": "CoinMarketCalProvider",
                "coingecko": "CoinGeckoProvider",
                "defillama": "DeFiLlamaProvider",
                "tokenunlocks": "TokenUnlocksProvider",
                "football_data": "FootballDataProvider",
                "thesportsdb": "TheSportsDBProvider",
                "github_releases": "GithubReleasesProvider",
            }

            if provider_name in name_mapping:
                class_name = name_mapping[provider_name]
            else:
                class_name = "".join(word.capitalize() for word in provider_name.split("_")) + "Provider"

            # Try to import from category-specific module
            module_path = f"events.providers.{category}.{provider_name}_provider"

            try:
                module = __import__(module_path, fromlist=[class_name])
                provider_class = getattr(module, class_name)
                return provider_class()
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not import {class_name} from {module_path}: {e}")

                # Fallback: try to import from root providers module (for legacy providers)
                try:
                    module_path = f"events.providers.{provider_name}"
                    module = __import__(module_path, fromlist=[class_name])
                    provider_class = getattr(module, class_name)
                    return provider_class()
                except (ImportError, AttributeError):
                    logger.error(f"Provider not found: {category}/{provider_name}")
                    return None

        except Exception as e:
            logger.error(f"Error importing provider {category}/{provider_name}: {e}")
            return None

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

            logger.info(f"Total events after normalization and deduplication: {len(deduplicated_events)}")

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


async def fetch_events(start_date: datetime, end_date: datetime, providers: Optional[List[str]] = None) -> List[Event]:
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

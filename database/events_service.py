"""
Events Service for PulseAI.

This module provides services for managing events in the database.
"""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

from database.db_models import supabase, safe_execute

logger = logging.getLogger("events_service")


@dataclass
class EventRecord:
    """Database record for event."""

    id: int
    title: str
    category: str
    subcategory: str
    starts_at: datetime
    ends_at: Optional[datetime]
    source: str
    link: str
    importance: float
    description: Optional[str]
    location: Optional[str]
    organizer: Optional[str]
    group_name: Optional[str]  # Название группы для умной группировки
    metadata: Optional[Dict]  # Метаданные в JSON формате
    created_at: datetime


class EventsService:
    """
    Service for managing events in the database.

    Features:
    - Query upcoming events
    - Filter by category and date range
    - Support for new grouping fields (category, group_name, metadata)
    """

    def __init__(self):
        """Initialize events service."""
        logger.info("EventsService initialized")

    async def get_events_by_date_range(
        self,
        from_date: datetime,
        to_date: datetime,
        category: Optional[str] = None,
    ) -> List[EventRecord]:
        """
        Get events within a date range.

        Args:
            from_date: Start date (UTC)
            to_date: End date (UTC)
            category: Optional category filter

        Returns:
            List of EventRecord objects
        """
        if not supabase:
            logger.warning("⚠️ Supabase не подключён, get_events_by_date_range не работает.")
            return []

        try:
            # Build query
            query = (
                supabase.table("events")
                .select(
                    "id, title, category, subcategory, event_time, country, currency, "
                    "importance, fact, forecast, previous, source, group_name, metadata, created_at"
                )
                .gte("event_time", from_date.isoformat())
                .lte("event_time", to_date.isoformat())
            )

            # Add category filter if specified
            if category:
                query = query.eq("category", category)

            # Order by event time
            query = query.order("event_time", desc=False)

            # Execute query
            result = safe_execute(query)
            events_data = result.data or []

            # Convert to EventRecord objects
            events = []
            for event_data in events_data:
                try:
                    # Parse event_time to datetime
                    event_time_str = event_data.get("event_time")
                    if isinstance(event_time_str, str):
                        starts_at = datetime.fromisoformat(event_time_str.replace("Z", "+00:00"))
                    else:
                        starts_at = event_time_str

                    event = EventRecord(
                        id=event_data.get("id", 0),
                        title=event_data.get("title", ""),
                        category=event_data.get("category") or "general",  # Default to "general" if null
                        subcategory=event_data.get("subcategory", ""),
                        starts_at=starts_at,
                        ends_at=None,  # Events don't have end_time in current schema
                        source=event_data.get("source", ""),
                        link="",  # No link field in current schema
                        importance=float(event_data.get("importance", 1)) / 10.0,  # Convert 1-10 to 0.1-1.0
                        description=event_data.get("fact", ""),  # Use fact as description
                        location=event_data.get("country", ""),  # Use country as location
                        organizer=None,
                        group_name=event_data.get("group_name"),
                        metadata=event_data.get("metadata", {}),
                        created_at=datetime.fromisoformat(
                            event_data.get(
                                "created_at",
                                datetime.now(timezone.utc).isoformat(),
                            ).replace("Z", "+00:00")
                        ),
                    )
                    events.append(event)

                except Exception as e:
                    logger.error(f"Error converting event data: {e}")
                    continue

            logger.info(f"Retrieved {len(events)} events from database")
            return events

        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return []

    async def get_upcoming_events(
        self,
        days: int = 30,
        category: Optional[str] = None,
        min_importance: float = 0.0,
    ) -> List[EventRecord]:
        """
        Get upcoming events within specified days.

        Args:
            days: Number of days to look ahead
            category: Optional category filter
            min_importance: Minimum importance threshold

        Returns:
            List of EventRecord objects
        """
        from_date = datetime.now(timezone.utc)
        to_date = from_date + timedelta(days=days)

        events = await self.get_events_by_date_range(from_date, to_date, category)

        # Filter by importance
        if min_importance > 0:
            events = [e for e in events if e.importance >= min_importance]

        return events

    def get_upcoming_events_sync(
        self,
        days_ahead: int = 30,
        category: Optional[str] = None,
        min_importance: float = 0.0,
    ) -> List[EventRecord]:
        """
        Synchronous wrapper for get_upcoming_events.

        Args:
            days_ahead: Number of days to look ahead
            category: Optional category filter
            min_importance: Minimum importance threshold

        Returns:
            List of EventRecord objects
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.get_upcoming_events(days_ahead, category, min_importance))


# Global instance
_events_service = None


def get_events_service() -> EventsService:
    """Get global events service instance."""
    global _events_service
    if _events_service is None:
        _events_service = EventsService()
    return _events_service

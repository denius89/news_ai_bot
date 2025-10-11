"""
Events Service for database operations.

This module provides database operations for events storage and retrieval.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from database.service import get_async_service

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
    created_at: datetime


class EventsService:
    """
    Service for managing events in the database.

    Features:
    - Insert events from providers
    - Query upcoming events
    - Filter by category and date range
    - Deduplication and cleanup
    """

    def __init__(self):
        """Initialize events service."""
        self.db_service = get_async_service()
        logger.info("EventsService initialized")

    async def insert_events(self, events: List[Dict[str, Any]]) -> int:
        """
        Insert events into the database using upsert logic.

        Args:
            events: List of event dictionaries

        Returns:
            Number of events inserted/updated
        """
        try:
            if not events:
                return 0

            from database.db_models import supabase

            if not supabase:
                logger.error("Supabase not initialized")
                return 0

            # Prepare insert data with new fields
            insert_data = []
            for event in events:
                event_data = {
                    "title": event.get("title", ""),
                    "category": event.get("category", "unknown"),
                    "subcategory": event.get("subcategory", "general"),
                    "starts_at": event.get("starts_at").isoformat() if event.get("starts_at") else None,
                    "ends_at": event.get("ends_at").isoformat() if event.get("ends_at") else None,
                    "source": event.get("source", ""),
                    "link": event.get("link", ""),
                    "importance": event.get("importance", 0.5),
                    "description": event.get("description"),
                    "location": event.get("location"),
                    "organizer": event.get("organizer"),
                    "unique_hash": event.get("unique_hash"),
                    "metadata": event.get("metadata", {}),
                    "status": event.get("status", "upcoming"),
                }
                insert_data.append(event_data)

            # Upsert events using unique_hash
            result = supabase.table("events_new").upsert(
                insert_data, on_conflict="unique_hash"
            ).execute()

            inserted_count = len(result.data) if result.data else 0

            logger.info(f"Upserted {inserted_count} events into database")
            return inserted_count

        except Exception as e:
            logger.error(f"Error inserting events: {e}")
            return 0

    async def get_upcoming_events(
        self, days_ahead: int = 30, category: Optional[str] = None, min_importance: float = 0.0
    ) -> List[EventRecord]:
        """
        Get upcoming events within specified days.

        Args:
            days_ahead: Number of days to look ahead
            category: Filter by category (optional)
            min_importance: Minimum importance threshold

        Returns:
            List of upcoming events
        """
        try:
            # Calculate date range
            now = datetime.now(timezone.utc)
            end_date = now + timedelta(days=days_ahead)

            # Build query
            query = """
                SELECT id, title, category, subcategory, starts_at, ends_at,
                       source, link, importance, description, location, organizer, created_at
                FROM events
                WHERE starts_at >= %s AND starts_at <= %s
                AND importance >= %s
            """
            params = [now, end_date, min_importance]

            if category:
                query += " AND category = %s"
                params.append(category)

            query += " ORDER BY starts_at ASC"

            # Execute query (this would need to be implemented in the database service)
            # For now, we'll return mock data
            events = await self._get_mock_events(days_ahead, category, min_importance)

            logger.info(f"Retrieved {len(events)} upcoming events")
            return events

        except Exception as e:
            logger.error(f"Error getting upcoming events: {e}")
            return []

    async def get_today_events(self, category: Optional[str] = None) -> List[EventRecord]:
        """
        Get events for today.

        Args:
            category: Filter by category (optional)

        Returns:
            List of today's events
        """
        try:
            today = datetime.now(timezone.utc).date()
            start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

            # Build query
            query = """
                SELECT id, title, category, subcategory, starts_at, ends_at,
                       source, link, importance, description, location, organizer, created_at
                FROM events
                WHERE starts_at >= %s AND starts_at <= %s
            """
            params = [start_of_day, end_of_day]

            if category:
                query += " AND category = %s"
                params.append(category)

            query += " ORDER BY starts_at ASC"

            # Execute query (this would need to be implemented in the database service)
            # For now, we'll return mock data
            events = await self._get_mock_today_events(category)

            logger.info(f"Retrieved {len(events)} events for today")
            return events

        except Exception as e:
            logger.error(f"Error getting today's events: {e}")
            return []

    async def get_events_by_date_range(
        self, start_date: datetime, end_date: datetime, category: Optional[str] = None
    ) -> List[EventRecord]:
        """
        Get events within a specific date range.

        Args:
            start_date: Start date for events
            end_date: End date for events
            category: Filter by category (optional)

        Returns:
            List of events in date range
        """
        try:
            # Build query
            query = """
                SELECT id, title, category, subcategory, starts_at, ends_at,
                       source, link, importance, description, location, organizer, created_at
                FROM events
                WHERE starts_at >= %s AND starts_at <= %s
            """
            params = [start_date, end_date]

            if category:
                query += " AND category = %s"
                params.append(category)

            query += " ORDER BY starts_at ASC"

            # Execute query (this would need to be implemented in the database service)
            # For now, we'll return mock data
            events = await self._get_mock_events_by_range(start_date, end_date, category)

            logger.info(f"Retrieved {len(events)} events in date range")
            return events

        except Exception as e:
            logger.error(f"Error getting events by date range: {e}")
            return []

    async def cleanup_old_events(self, days_to_keep: int = 7) -> int:
        """
        Remove events older than specified days.

        Args:
            days_to_keep: Number of days to keep events

        Returns:
            Number of events removed
        """
        try:
            # cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

            # Delete old events
            # query = "DELETE FROM events WHERE starts_at < %s"
            # params = [cutoff_date]

            # Execute query (this would need to be implemented in the database service)
            # For now, we'll simulate the cleanup
            removed_count = 0

            logger.info(f"Cleaned up {removed_count} old events")
            return removed_count

        except Exception as e:
            logger.error(f"Error cleaning up old events: {e}")
            return 0

    async def _get_mock_events(
        self, days_ahead: int, category: Optional[str] = None, min_importance: float = 0.0
    ) -> List[EventRecord]:
        """Get mock events for testing."""
        events = []

        # Generate some mock events
        now = datetime.now(timezone.utc)

        # Add some crypto events
        if not category or category == "crypto":
            events.append(
                EventRecord(
                    id=1,
                    title="Bitcoin Halving Event",
                    category="crypto",
                    subcategory="bitcoin",
                    starts_at=now + timedelta(days=5),
                    ends_at=None,
                    source="coinmarketcal.com",
                    link="https://coinmarketcal.com/event/bitcoin-halving",
                    importance=0.9,
                    description="Bitcoin mining reward halving event",
                    location=None,
                    organizer="Bitcoin Network",
                    created_at=now,
                )
            )

        # Add some market events
        if not category or category == "markets":
            events.append(
                EventRecord(
                    id=2,
                    title="FOMC Meeting",
                    category="markets",
                    subcategory="monetary_policy",
                    starts_at=now + timedelta(days=10),
                    ends_at=None,
                    source="investing.com",
                    link="https://investing.com/economic-calendar/fomc",
                    importance=0.95,
                    description="Federal Open Market Committee meeting",
                    location="Washington, DC",
                    organizer="Federal Reserve",
                    created_at=now,
                )
            )

        # Add some sports events
        if not category or category == "sports":
            events.append(
                EventRecord(
                    id=3,
                    title="Championship Finals",
                    category="sports",
                    subcategory="general",
                    starts_at=now + timedelta(days=15),
                    ends_at=now + timedelta(days=15, hours=3),
                    source="espn.com",
                    link="https://espn.com/sports/championship",
                    importance=0.8,
                    description="Major sports championship finals",
                    location="Various venues",
                    organizer="Sports League",
                    created_at=now,
                )
            )

        # Filter by importance
        events = [e for e in events if e.importance >= min_importance]

        return events

    async def _get_mock_today_events(self, category: Optional[str] = None) -> List[EventRecord]:
        """Get mock events for today."""
        events = []

        now = datetime.now(timezone.utc)
        today = now.date()

        # Add some events for today
        if not category or category == "crypto":
            events.append(
                EventRecord(
                    id=4,
                    title="Ethereum Network Upgrade",
                    category="crypto",
                    subcategory="ethereum",
                    starts_at=datetime.combine(today, datetime.min.time().replace(hour=14, minute=0)).replace(
                        tzinfo=timezone.utc
                    ),
                    ends_at=None,
                    source="coinmarketcal.com",
                    link="https://coinmarketcal.com/event/ethereum-upgrade",
                    importance=0.8,
                    description="Ethereum network protocol upgrade",
                    location=None,
                    organizer="Ethereum Foundation",
                    created_at=now,
                )
            )

        return events

    async def _get_mock_events_by_range(
        self, start_date: datetime, end_date: datetime, category: Optional[str] = None
    ) -> List[EventRecord]:
        """Get mock events in date range."""
        events = []

        # Generate events in the range
        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            daily_events = await self._get_mock_events_for_date(current_date, category)
            events.extend(daily_events)
            current_date += timedelta(days=1)

        return events

    async def _get_mock_events_for_date(self, date, category: Optional[str] = None) -> List[EventRecord]:
        """Get mock events for a specific date."""
        events = []

        # Add some events based on date
        if date.day % 7 == 1:  # First day of week
            events.append(
                EventRecord(
                    id=len(events) + 100,
                    title=f"Weekly Market Analysis - {date.strftime('%Y-%m-%d')}",
                    category="markets",
                    subcategory="analysis",
                    starts_at=datetime.combine(date, datetime.min.time().replace(hour=9, minute=0)).replace(
                        tzinfo=timezone.utc
                    ),
                    ends_at=None,
                    source="investing.com",
                    link="https://investing.com/analysis",
                    importance=0.6,
                    description="Weekly market analysis and outlook",
                    location=None,
                    organizer="Investment Firm",
                    created_at=datetime.now(timezone.utc),
                )
            )

        return events

    async def update_event_status(
        self, event_id: int, status: str, result_data: Optional[Dict] = None
    ) -> bool:
        """
        Update event status and results.

        Args:
            event_id: Event ID
            status: New status (upcoming, ongoing, completed, cancelled)
            result_data: Optional result data (for completed events)

        Returns:
            True if updated successfully
        """
        try:
            from database.db_models import supabase

            if not supabase:
                logger.error("Supabase not initialized")
                return False

            update_data = {"status": status}
            if result_data:
                update_data["result_data"] = result_data

            result = supabase.table("events_new").update(update_data).eq("id", event_id).execute()

            success = len(result.data) > 0 if result.data else False
            if success:
                logger.info(f"Updated event {event_id} status to {status}")
            return success

        except Exception as e:
            logger.error(f"Error updating event status: {e}")
            return False

    async def get_completed_events_without_results(self, days_back: int = 3) -> List[Dict]:
        """
        Get completed events that need result updates.

        Args:
            days_back: How many days back to check

        Returns:
            List of events needing updates
        """
        try:
            from database.db_models import supabase

            if not supabase:
                logger.error("Supabase not initialized")
                return []

            # Calculate date range
            now = datetime.now(timezone.utc)
            start_date = now - timedelta(days=days_back)

            # Query events that have ended but don't have results
            result = (
                supabase.table("events_new")
                .select("*")
                .gte("starts_at", start_date.isoformat())
                .lte("starts_at", now.isoformat())
                .eq("status", "upcoming")
                .is_("result_data", "null")
                .execute()
            )

            events = result.data or []
            logger.info(f"Found {len(events)} events needing result updates")
            return events

        except Exception as e:
            logger.error(f"Error getting events without results: {e}")
            return []

    async def get_event_by_hash(self, unique_hash: str) -> Optional[Dict]:
        """
        Get event by unique_hash for Smart Sync.

        Args:
            unique_hash: Unique hash of the event

        Returns:
            Event dictionary or None if not found
        """
        try:
            from database.db_models import supabase

            if not supabase:
                logger.error("Supabase not initialized")
                return None

            result = supabase.table("events_new").select("*").eq("unique_hash", unique_hash).execute()

            if result.data and len(result.data) > 0:
                return result.data[0]
            return None

        except Exception as e:
            logger.error(f"Error getting event by hash: {e}")
            return None

    async def update_event(self, event_id: int, event_data: Dict) -> bool:
        """
        Update existing event with new data.

        Args:
            event_id: Event ID to update
            event_data: New event data

        Returns:
            True if updated successfully
        """
        try:
            from database.db_models import supabase

            if not supabase:
                logger.error("Supabase not initialized")
                return False

            # Prepare update data
            update_data = {
                "title": event_data.get("title"),
                "description": event_data.get("description"),
                "starts_at": event_data.get("starts_at").isoformat() if event_data.get("starts_at") else None,
                "ends_at": event_data.get("ends_at").isoformat() if event_data.get("ends_at") else None,
                "importance_score": event_data.get("importance_score"),
                "credibility_score": event_data.get("credibility_score"),
                "status": event_data.get("status", "upcoming"),
                "location": event_data.get("location"),
                "organizer": event_data.get("organizer"),
                "metadata": event_data.get("metadata", {}),
                "sync_status": "updated",
                "last_synced_at": datetime.now(timezone.utc).isoformat(),
            }

            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}

            result = supabase.table("events_new").update(update_data).eq("id", event_id).execute()

            success = len(result.data) > 0 if result.data else False
            if success:
                logger.info(f"Updated event {event_id}")
            return success

        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return False


# Global service instance
_service_instance: Optional[EventsService] = None


def get_events_service() -> EventsService:
    """Get global events service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = EventsService()
    return _service_instance

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
            # Build query - reading from events_new table
            query = (
                supabase.table("events_new")
                .select(
                    "id, title, category, subcategory, starts_at, ends_at, "
                    "importance, description, location, organizer, source, link, group_name, metadata, created_at"
                )
                .gte("starts_at", from_date.isoformat())
                .lte("starts_at", to_date.isoformat())
            )

            # Add category filter if specified
            if category:
                query = query.eq("category", category)

            # Order by event time
            query = query.order("starts_at", desc=False)

            # Execute query
            result = safe_execute(query)
            events_data = result.data or []

            # Convert to EventRecord objects
            events = []
            for event_data in events_data:
                try:
                    # Parse starts_at to datetime
                    starts_at_str = event_data.get("starts_at")
                    if isinstance(starts_at_str, str):
                        starts_at = datetime.fromisoformat(starts_at_str.replace("Z", "+00:00"))
                    else:
                        starts_at = starts_at_str

                    # Parse ends_at if available
                    ends_at = None
                    ends_at_str = event_data.get("ends_at")
                    if ends_at_str:
                        if isinstance(ends_at_str, str):
                            ends_at = datetime.fromisoformat(ends_at_str.replace("Z", "+00:00"))
                        else:
                            ends_at = ends_at_str

                    event = EventRecord(
                        id=event_data.get("id", 0),
                        title=event_data.get("title", ""),
                        category=event_data.get("category") or "general",
                        subcategory=event_data.get("subcategory", ""),
                        starts_at=starts_at,
                        ends_at=ends_at,
                        source=event_data.get("source", ""),
                        link=event_data.get("link", ""),
                        importance=float(event_data.get("importance", 0.5)),  # Already 0.0-1.0 in events_new
                        description=event_data.get("description", ""),
                        location=event_data.get("location", ""),
                        organizer=event_data.get("organizer"),
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

    async def insert_events(self, events_data: List[Dict]) -> int:
        """
        Insert events into the database (events_new table).

        Args:
            events_data: List of event dictionaries

        Returns:
            Number of events inserted
        """
        if not supabase:
            logger.warning("⚠️ Supabase не подключён, события не будут сохранены.")
            return 0

        if not events_data:
            logger.info("Нет событий для вставки")
            return 0

        try:
            # Prepare rows for insertion
            rows = []
            for event in events_data:
                # Create unique hash for deduplication
                unique_hash = self._create_event_hash(
                    event.get("title", ""), event.get("starts_at"), event.get("source", "")
                )

                row = {
                    "title": event.get("title"),
                    "category": event.get("category"),
                    "subcategory": event.get("subcategory"),
                    "starts_at": (
                        event.get("starts_at").isoformat()
                        if isinstance(event.get("starts_at"), datetime)
                        else event.get("starts_at")
                    ),
                    "ends_at": (
                        event.get("ends_at").isoformat()
                        if isinstance(event.get("ends_at"), datetime)
                        else event.get("ends_at")
                    ),
                    "source": event.get("source"),
                    "link": event.get("link"),
                    "importance": event.get("importance"),
                    "description": event.get("description"),
                    "location": event.get("location"),
                    "organizer": event.get("organizer"),
                    "metadata": event.get("metadata", {}),
                    "group_name": event.get("group_name"),
                    "unique_hash": unique_hash,
                }
                rows.append(row)

            # Insert/Update into events_new table
            # Стратегия: фильтруем дубликаты до вставки, вставляем только новые
            try:
                # Получаем существующие unique_hash из БД для проверки дубликатов
                existing_hashes = set()
                try:
                    hash_list = [row["unique_hash"] for row in rows if row.get("unique_hash")]
                    if hash_list:
                        existing = safe_execute(
                            supabase.table("events_new").select("unique_hash").in_("unique_hash", hash_list)
                        )
                        existing_hashes = {e["unique_hash"] for e in (existing.data or [])}
                        logger.info(f"📊 Найдено существующих событий: {len(existing_hashes)} из {len(hash_list)}")
                except Exception as e:
                    logger.debug(f"Не удалось проверить существующие hash: {e}")

                # Фильтруем только новые события
                new_rows = [row for row in rows if row.get("unique_hash") not in existing_hashes]

                if not new_rows:
                    logger.info("✅ Все события уже существуют в БД (0 новых)")
                    return 0

                logger.info(
                    f"💾 Вставка {len(new_rows)} новых событий (пропущено дубликатов: {len(rows) - len(new_rows)})"
                )

                # Вставляем только новые события
                result = safe_execute(supabase.table("events_new").insert(new_rows))
                inserted = len(result.data or [])
                logger.info(f"✅ Inserted {inserted} new events into events_new table")
                return inserted

            except Exception as insert_error:
                # If insert fails, try without unique_hash (fallback)
                logger.warning(f"Insert failed, retrying without unique_hash: {insert_error}")

                # Remove unique_hash from rows
                rows_without_hash = []
                for row in rows:
                    row_copy = row.copy()
                    row_copy.pop("unique_hash", None)
                    rows_without_hash.append(row_copy)

                result = safe_execute(supabase.table("events_new").insert(rows_without_hash))
                inserted = len(result.data or [])
                logger.info(f"✅ Inserted {inserted} events (without unique_hash)")
                return inserted

        except Exception as e:
            logger.error(f"❌ Error inserting events: {e}")
            return 0

    def _create_event_hash(self, title: str, starts_at, source: str) -> str:
        """Create unique hash for event deduplication."""
        import hashlib

        if isinstance(starts_at, datetime):
            starts_at_str = starts_at.isoformat()
        else:
            starts_at_str = str(starts_at)

        raw = f"{title.lower().strip()}|{starts_at_str}|{source.lower()}"
        return hashlib.sha256(raw.encode()).hexdigest()


# Global instance
_events_service = None


def get_events_service() -> EventsService:
    """Get global events service instance."""
    global _events_service
    if _events_service is None:
        _events_service = EventsService()
    return _events_service

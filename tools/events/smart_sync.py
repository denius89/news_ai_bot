#!/usr/bin/env python3
"""
Smart Sync System for PulseAI Events.

This tool provides incremental synchronization of events,
updating only changed records to minimize database operations.
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.events_service import get_events_service

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/smart_sync.log"), logging.StreamHandler()],
)

logger = logging.getLogger("smart_sync")


class SmartSync:
    """
    Smart synchronization system for events.
    Updates only changed records for efficiency.
    """

    def __init__(self):
        """Initialize Smart Sync."""
        self.events_service = get_events_service()
        logger.info("SmartSync initialized")

    async def sync_events(self, new_events: List[Dict]) -> Dict:
        """
        Sync events with database using smart comparison.

        Args:
            new_events: List of event dictionaries to sync

        Returns:
            Dictionary with sync statistics
        """
        stats = {"added": 0, "updated": 0, "skipped": 0, "errors": 0, "total": len(new_events)}

        logger.info(f"Starting Smart Sync for {stats['total']} events")

        for event in new_events:
            try:
                unique_hash = event.get("unique_hash")
                if not unique_hash:
                    logger.warning(f"Event missing unique_hash: {event.get('title')}")
                    stats["errors"] += 1
                    continue

                # Check if event exists
                existing = await self.events_service.get_event_by_hash(unique_hash)

                if not existing:
                    # New event - add it
                    await self.events_service.insert_events([event])
                    stats["added"] += 1
                    logger.debug(f"Added new event: {event.get('title')}")
                else:
                    # Check if update needed
                    if self._needs_update(existing, event):
                        await self.events_service.update_event(existing["id"], event)
                        stats["updated"] += 1
                        logger.debug(f"Updated event: {event.get('title')}")
                    else:
                        stats["skipped"] += 1
                        logger.debug(f"Skipped unchanged event: {event.get('title')}")

            except Exception as e:
                logger.error(f"Error syncing event {event.get('title')}: {e}")
                stats["errors"] += 1

        logger.info(
            f"Smart Sync complete: {stats['added']} added, "
            f"{stats['updated']} updated, {stats['skipped']} skipped, "
            f"{stats['errors']} errors"
        )

        return stats

    def _needs_update(self, existing: Dict, new: Dict) -> bool:
        """
        Check if event needs update by comparing key fields.

        Args:
            existing: Existing event from database
            new: New event from provider

        Returns:
            bool: True if update is needed
        """
        # Fields to compare for changes
        fields_to_compare = [
            "title",
            "description",
            "starts_at",
            "ends_at",
            "importance_score",
            "credibility_score",
            "status",
            "location",
            "organizer",
        ]

        for field in fields_to_compare:
            existing_value = existing.get(field)
            new_value = new.get(field)

            # Handle datetime comparison
            if field in ["starts_at", "ends_at"]:
                if existing_value and new_value:
                    # Convert to strings for comparison if they're datetime objects
                    if isinstance(existing_value, datetime):
                        existing_value = existing_value.isoformat()
                    if isinstance(new_value, datetime):
                        new_value = new_value.isoformat()

            # Compare values
            if existing_value != new_value:
                logger.debug(f"Field '{field}' changed: '{existing_value}' -> '{new_value}'")
                return True

        return False

    async def sync_from_providers(
        self, days_ahead: int = 7, categories: Optional[List[str]] = None, providers: Optional[List[str]] = None
    ) -> Dict:
        """
        Fetch events from providers and sync them.

        Args:
            days_ahead: Number of days to look ahead
            categories: List of categories to sync
            providers: List of specific providers to use

        Returns:
            Dictionary with sync statistics
        """
        try:
            from events.events_parser import get_events_parser
            from ai_modules.importance_v2 import evaluator_v2

            # Get events parser
            parser = get_events_parser()

            # Calculate date range
            now = datetime.now(timezone.utc)
            start_date = now
            end_date = now + timedelta(days=days_ahead)

            logger.info(f"Fetching events from {start_date.date()} to {end_date.date()}")

            # Fetch events from providers
            events = await parser.fetch_events(start_date, end_date, providers)

            logger.info(f"Fetched {len(events)} events from providers")

            # Calculate ML importance scores
            for event in events:
                event_dict = event.__dict__ if hasattr(event, "__dict__") else event
                importance_score = evaluator_v2.evaluate_importance(event_dict)
                event_dict["importance_score"] = importance_score

            # Filter by importance >= 0.6
            filtered_events = [
                e.__dict__ if hasattr(e, "__dict__") else e
                for e in events
                if (e.__dict__ if hasattr(e, "__dict__") else e).get("importance_score", 0) >= 0.6
            ]

            logger.info(f"Filtered to {len(filtered_events)} events (importance >= 0.6)")

            # Sync filtered events
            stats = await self.sync_events(filtered_events)

            return stats

        except Exception as e:
            logger.error(f"Error in sync_from_providers: {e}")
            return {"added": 0, "updated": 0, "skipped": 0, "errors": 1, "total": 0, "error": str(e)}


async def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Smart Sync events for PulseAI")

    parser.add_argument("--days", type=int, default=7, help="Number of days to look ahead (default: 7)")

    parser.add_argument(
        "--categories",
        nargs="+",
        choices=["crypto", "sports", "markets", "tech", "world"],
        help="Specific categories to sync (default: all)",
    )

    parser.add_argument("--providers", nargs="+", help="Specific providers to use (default: all enabled)")

    args = parser.parse_args()

    # Create Smart Sync instance
    smart_sync = SmartSync()

    # Sync events from providers
    stats = await smart_sync.sync_from_providers(
        days_ahead=args.days, categories=args.categories, providers=args.providers
    )

    # Print results
    if stats.get("error"):
        print(f"❌ Error: {stats['error']}")
        sys.exit(1)
    else:
        print(f"✅ Smart Sync complete!")
        print(f"📊 Added: {stats['added']}")
        print(f"🔄 Updated: {stats['updated']}")
        print(f"⏭️  Skipped: {stats['skipped']}")
        if stats["errors"] > 0:
            print(f"⚠️  Errors: {stats['errors']}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Smart Sync cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Fetch and Store Events Tool for PulseAI.

This tool fetches events from various providers and stores them in the database.
"""

from ai_modules.metrics import get_metrics
from database.events_service import get_events_service
from events.events_parser import get_events_parser
import asyncio
import argparse
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/events_fetch.log"), logging.StreamHandler()],
)

logger = logging.getLogger("fetch_and_store_events")


async def fetch_and_store_events(
    days_since: int = 7, days_until: int = 30, providers: List[str] = None, dry_run: bool = False
) -> Dict[str, Any]:
    """
    Fetch events from providers and store them in the database.

    Args:
        days_since: Number of days to look back
        days_until: Number of days to look ahead
        providers: List of provider names to use
        dry_run: If True, don't actually store events

    Returns:
        Dictionary with fetch results
    """
    try:
        logger.info(f"Starting event fetch: {days_since} days back, {days_until} days ahead")

        # Calculate date range
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days_since)
        end_date = now + timedelta(days=days_until)

        logger.info(f"Date range: {start_date.date()} to {end_date.date()}")

        # Get events parser
        parser = get_events_parser()

        # Fetch events from providers
        logger.info(f"Fetching events from providers: {providers or 'all'}")
        events = await parser.fetch_events(start_date, end_date, providers)

        logger.info(f"Fetched {len(events)} events from providers")

        if dry_run:
            logger.info("DRY RUN: Not storing events to database")

            # Log sample events
            for i, event in enumerate(events[:5]):
                logger.info(
                    f"Sample event {i+1}: {event.title} ({event.category}) - {event.starts_at}")

            return {
                "success": True,
                "events_fetched": len(events),
                "events_stored": 0,
                "dry_run": True,
                "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            }

        # Store events in database
        events_service = get_events_service()

        # Convert events to dictionary format
        events_data = []
        for event in events:
            event_data = {
                "title": event.title,
                "category": event.category,
                "subcategory": event.subcategory,
                "starts_at": event.starts_at,
                "ends_at": event.ends_at,
                "source": event.source,
                "link": event.link,
                "importance": event.importance,
                "description": event.description,
                "location": event.location,
                "organizer": event.organizer,
            }
            events_data.append(event_data)

        # Insert events
        stored_count = await events_service.insert_events(events_data)

        logger.info(f"Stored {stored_count} events in database")

        # Update metrics
        metrics = get_metrics()
        metrics.increment_events_processed_total(stored_count)

        # Log summary by category
        category_counts = {}
        for event in events:
            category = event.category
            category_counts[category] = category_counts.get(category, 0) + 1

        logger.info("Events by category:")
        for category, count in category_counts.items():
            logger.info(f"  {category}: {count}")

        return {
            "success": True,
            "events_fetched": len(events),
            "events_stored": stored_count,
            "dry_run": False,
            "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "categories": category_counts,
            "providers_used": providers or list(parser.providers.keys()),
        }

    except Exception as e:
        logger.error(f"Error in fetch_and_store_events: {e}")

        # Update error metrics
        metrics = get_metrics()
        metrics.increment_events_fetch_errors_total()

        return {"success": False, "error": str(e), "events_fetched": 0, "events_stored": 0}


async def cleanup_old_events(days_to_keep: int = 30) -> int:
    """
    Clean up old events from the database.

    Args:
        days_to_keep: Number of days to keep events

    Returns:
        Number of events removed
    """
    try:
        logger.info(f"Cleaning up events older than {days_to_keep} days")

        events_service = get_events_service()
        removed_count = await events_service.cleanup_old_events(days_to_keep)

        logger.info(f"Removed {removed_count} old events")
        return removed_count

    except Exception as e:
        logger.error(f"Error cleaning up old events: {e}")
        return 0


async def get_provider_info() -> Dict[str, Any]:
    """Get information about available providers."""
    try:
        parser = get_events_parser()
        provider_info = parser.get_provider_info()

        logger.info("Available providers:")
        for name, info in provider_info.items():
            logger.info(f"  {name}: {info.get('description', 'No description')}")

        return provider_info

    except Exception as e:
        logger.error(f"Error getting provider info: {e}")
        return {}


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Fetch and store events for PulseAI")

    parser.add_argument(
        "--since",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)")

    parser.add_argument(
        "--until",
        type=int,
        default=30,
        help="Number of days to look ahead (default: 30)")

    parser.add_argument(
        "--providers",
        nargs="+",
        choices=["coinmarketcal", "investing", "espn"],
        help="Specific providers to use (default: all)",
    )

    parser.add_argument("--dry-run", action="store_true", help="Fetch events but don't store them")

    parser.add_argument("--cleanup", type=int, metavar="DAYS",
                        help="Clean up events older than specified days")

    parser.add_argument("--info", action="store_true", help="Show provider information")

    args = parser.parse_args()

    async def run():
        if args.info:
            await get_provider_info()
            return

        if args.cleanup:
            await cleanup_old_events(args.cleanup)
            return

        # Fetch and store events
        result = await fetch_and_store_events(
            days_since=args.since, days_until=args.until, providers=args.providers, dry_run=args.dry_run
        )

        # Print results
        if result["success"]:
            print(f"✅ Successfully processed {result['events_fetched']} events")
            if not result.get("dry_run", False):
                print(f"📊 Stored {result['events_stored']} events in database")

            if "categories" in result:
                print("📈 Events by category:")
                for category, count in result["categories"].items():
                    print(f"   {category}: {count}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    # Run the async function
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

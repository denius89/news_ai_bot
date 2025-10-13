#!/usr/bin/env python3
"""
Update Event Results Tool for PulseAI.

This tool updates results for completed events.
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.events_service import get_events_service

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/events_update.log"), logging.StreamHandler()],
)

logger = logging.getLogger("update_event_results")


async def update_event_results(days_back: int = 3, categories: list = None, dry_run: bool = False) -> Dict[str, Any]:
    """
    Update results for completed events.

    Args:
        days_back: How many days back to check (default: 3)
        categories: List of categories to update (default: all)
        dry_run: If True, don't update database

    Returns:
        Dictionary with update results
    """
    try:
        logger.info(f"Starting event results update: {days_back} days back")

        # Get events service
        events_service = get_events_service()

        # Get events needing updates
        events = await events_service.get_completed_events_without_results(days_back)

        logger.info(f"Found {len(events)} events needing updates")

        if dry_run:
            logger.info("DRY RUN: Not updating events")
            return {
                "success": True,
                "events_found": len(events),
                "events_updated": 0,
                "dry_run": True,
            }

        # Update each event
        updated_count = 0
        for event in events:
            # For now, just mark as completed
            # In production, this would fetch actual results from providers
            success = await events_service.update_event_status(event["id"], "completed", {"note": "Auto-completed"})
            if success:
                updated_count += 1

        logger.info(f"Updated {updated_count} events")

        return {
            "success": True,
            "events_found": len(events),
            "events_updated": updated_count,
            "dry_run": False,
        }

    except Exception as e:
        logger.error(f"Error updating event results: {e}")
        return {"success": False, "error": str(e), "events_found": 0, "events_updated": 0}


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Update event results for PulseAI")

    parser.add_argument("--days", type=int, default=3, help="Number of days to look back (default: 3)")

    parser.add_argument(
        "--categories",
        nargs="+",
        choices=["crypto", "sports", "markets", "tech", "world"],
        help="Specific categories to update (default: all)",
    )

    parser.add_argument("--dry-run", action="store_true", help="Check events but don't update them")

    args = parser.parse_args()

    async def run():
        result = await update_event_results(days_back=args.days, categories=args.categories, dry_run=args.dry_run)

        # Print results
        if result["success"]:
            print(f"✅ Found {result['events_found']} events needing updates")
            if not result.get("dry_run", False):
                print(f"📊 Updated {result['events_updated']} events")
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

#!/usr/bin/env python3
"""
Send Notifications Tool for PulseAI.

This tool sends event notifications to users based on their preferences.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.notification_service import get_notification_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("send_notifications")


async def send_to_user(user_id: int, test: bool = False):
    """
    Send notification to specific user.

    Args:
        user_id: Telegram user ID
        test: Send test notification
    """
    try:
        service = get_notification_service()

        logger.info(f"Preparing notification for user {user_id}")

        # Prepare digest
        digest = await service.prepare_daily_digest(user_id)

        events_count = digest.get("count", 0)
        high_importance_count = len(digest.get("high_importance", []))

        logger.info(f"Digest prepared: {events_count} events " f"({high_importance_count} high importance)")

        if events_count == 0:
            logger.info("No events matching user preferences")
            return

        # Send notification
        events = digest.get("events", [])

        if test:
            logger.info("TEST MODE: Would send notification with following events:")
            for event in events[:5]:
                logger.info(f"  - {event.get('title')} (importance: {event.get('importance_score', 0):.2f})")
        else:
            success = await service.send_telegram_notification(user_id, events)

            if success:
                logger.info(f"✓ Notification sent to user {user_id}")
            else:
                logger.warning(f"✗ Failed to send notification to user {user_id}")

    except Exception as e:
        logger.error(f"Error sending notification to user {user_id}: {e}", exc_info=True)


async def send_to_all_users(test: bool = False, min_importance: float = 0.7):
    """
    Send notifications to all users with preferences.

    Args:
        test: Test mode (don't actually send)
        min_importance: Minimum importance threshold
    """
    try:
        from database.db_models import supabase

        if not supabase:
            logger.error("Supabase not initialized")
            return

        # Get all users with notification preferences
        result = supabase.table("user_preferences").select("user_id").execute()

        if not result.data:
            logger.info("No users with notification preferences found")
            return

        user_ids = [row["user_id"] for row in result.data]

        logger.info(f"Found {len(user_ids)} users with notification preferences")

        sent_count = 0
        failed_count = 0
        skipped_count = 0

        for user_id in user_ids:
            try:
                service = get_notification_service()

                # Prepare digest
                digest = await service.prepare_daily_digest(user_id)

                events_count = digest.get("count", 0)

                if events_count == 0:
                    logger.debug(f"User {user_id}: No matching events, skipping")
                    skipped_count += 1
                    continue

                # Send notification
                events = digest.get("events", [])

                if test:
                    logger.info(f"TEST: Would send to user {user_id}: {events_count} events")
                    sent_count += 1
                else:
                    success = await service.send_telegram_notification(user_id, events)

                    if success:
                        logger.info(f"✓ Sent to user {user_id}: {events_count} events")
                        sent_count += 1
                    else:
                        logger.warning(f"✗ Failed to send to user {user_id}")
                        failed_count += 1

                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error processing user {user_id}: {e}")
                failed_count += 1

        logger.info("\n" + "=" * 60)
        logger.info("NOTIFICATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total users: {len(user_ids)}")
        logger.info(f"Sent: {sent_count}")
        logger.info(f"Failed: {failed_count}")
        logger.info(f"Skipped (no events): {skipped_count}")

    except Exception as e:
        logger.error(f"Error sending notifications to all users: {e}", exc_info=True)


async def show_user_preferences(user_id: int):
    """
    Show user notification preferences.

    Args:
        user_id: Telegram user ID
    """
    try:
        service = get_notification_service()

        prefs = await service.get_user_preferences(user_id)

        if not prefs:
            logger.info(f"User {user_id} has no notification preferences set")
            return

        logger.info("\n" + "=" * 60)
        logger.info(f"PREFERENCES FOR USER {user_id}")
        logger.info("=" * 60)
        logger.info(f"Categories: {', '.join(prefs.get('categories', [])) or 'All'}")
        logger.info(f"Min Importance: {prefs.get('min_importance', 0.6)}")
        logger.info(f"Delivery Method: {prefs.get('delivery_method', 'bot')}")
        logger.info(f"Frequency: {prefs.get('notification_frequency', 'daily')}")
        logger.info(f"Max/Day: {prefs.get('max_notifications_per_day', 3)}")
        logger.info(f"Last Notified: {prefs.get('last_notified_at', 'Never')}")

    except Exception as e:
        logger.error(f"Error getting user preferences: {e}", exc_info=True)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="PulseAI Notification Sender - Send event notifications to users")

    parser.add_argument("--user", type=int, metavar="USER_ID", help="Send to specific user (Telegram ID)")

    parser.add_argument("--all", action="store_true", help="Send to all users with preferences")

    parser.add_argument("--test", action="store_true", help="Test mode (don't actually send)")

    parser.add_argument("--show-preferences", type=int, metavar="USER_ID", help="Show user preferences")

    parser.add_argument("--min-importance", type=float, default=0.7, help="Minimum importance threshold (default: 0.7)")

    args = parser.parse_args()

    # Show preferences
    if args.show_preferences:
        asyncio.run(show_user_preferences(args.show_preferences))
        return

    # Send to specific user
    if args.user:
        asyncio.run(send_to_user(args.user, args.test))
        return

    # Send to all users
    if args.all:
        asyncio.run(send_to_all_users(args.test, args.min_importance))
        return

    # No action specified
    parser.print_help()


if __name__ == "__main__":
    main()

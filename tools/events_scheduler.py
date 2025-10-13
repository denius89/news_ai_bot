#!/usr/bin/env python3
"""
Events Scheduler for PulseAI.

This tool schedules event fetches with rate limit awareness.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from datetime import timedelta, timezone  # noqa: F401

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.rate_limit_manager import get_rate_limit_manager, RATE_LIMITS  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("events_scheduler")


# Fetch schedule configuration
FETCH_SCHEDULE = {
    'crypto': {
        'interval': 14400,  # 4 hours
        'providers': ['coinmarketcal', 'coingecko', 'defillama', 'tokenunlocks']
    },
    'markets': {
        'interval': 21600,  # 6 hours
        'providers': ['finnhub', 'fmp', 'eodhd']
    },
    'sports': {
        'interval': 7200,  # 2 hours
        'providers': ['football_data', 'thesportsdb', 'pandascore']
    },
    'tech': {
        'interval': 43200,  # 12 hours
        'providers': ['github_releases']
    },
    'world': {
        'interval': 21600,  # 6 hours
        'providers': ['oecd']
    },
}


async def schedule_fetches(category: str = None, force: bool = False):
    """
    Schedule event fetches with rate limit awareness.

    Args:
        category: Category to fetch (None for all)
        force: Force fetch even if not scheduled
    """
    try:
        rate_limiter = get_rate_limit_manager()

        # Determine categories to fetch
        if category:
            if category not in FETCH_SCHEDULE:
                logger.error(f"Unknown category: {category}")
                logger.info(f"Available categories: {', '.join(FETCH_SCHEDULE.keys())}")
                return
            categories = [category]
        else:
            categories = list(FETCH_SCHEDULE.keys())

        logger.info(f"Scheduling fetches for categories: {', '.join(categories)}")

        for cat in categories:
            schedule = FETCH_SCHEDULE[cat]
            providers = schedule['providers']
            interval = schedule['interval']

            logger.info(f"\n{'='*60}")
            logger.info(f"Category: {cat.upper()}")
            logger.info(f"Interval: {interval}s ({interval/3600:.1f}h)")
            logger.info(f"Providers: {', '.join(providers)}")
            logger.info(f"{'='*60}")

            # Check each provider
            for provider in providers:
                if provider not in RATE_LIMITS:
                    logger.warning(f"No rate limit config for {provider}, skipping")
                    continue

                # Check if can fetch
                can_fetch = rate_limiter.can_make_request(provider)
                wait_time = rate_limiter.get_wait_time(provider)

                if can_fetch or force:
                    if force:
                        logger.info(f"✓ {provider}: FORCED fetch")
                    else:
                        logger.info(f"✓ {provider}: Ready to fetch")

                    # TODO: Trigger actual fetch
                    # from events.events_parser import get_events_parser
                    # parser = get_events_parser()
                    # await parser.fetch_events(...)

                    # Record request for rate limiting
                    rate_limiter.record_request(provider)
                else:
                    logger.warning(
                        f"✗ {provider}: Rate limit reached, "
                        f"wait {wait_time:.0f}s ({wait_time/60:.1f}min)"
                    )

            logger.info("")

        # Print rate limit stats
        logger.info("\n" + "=" * 60)
        logger.info("RATE LIMIT STATISTICS")
        logger.info("=" * 60)

        stats = rate_limiter.get_stats()

        for provider, provider_stats in stats['providers'].items():
            status = "✓ OK" if provider_stats['can_request'] else "✗ LIMIT"
            logger.info(
                f"{status} {provider}: "
                f"{provider_stats['current_requests']}/{provider_stats['max_requests']} requests, "
                f"wait: {provider_stats['wait_time']:.0f}s"
            )

        logger.info(f"\nTotal cached items: {stats['total_cached_items']}")
        logger.info(f"Total limit exceeded: {stats['total_limit_exceeded']}")

    except Exception as e:
        logger.error(f"Error scheduling fetches: {e}", exc_info=True)


async def show_schedule():
    """Show fetch schedule for all categories."""
    logger.info("\n" + "=" * 60)
    logger.info("EVENT FETCH SCHEDULE")
    logger.info("=" * 60)

    for category, schedule in FETCH_SCHEDULE.items():
        interval = schedule['interval']
        providers = schedule['providers']

        logger.info(f"\n{category.upper()}:")
        logger.info(f"  Interval: {interval}s ({interval/3600:.1f}h)")
        logger.info(f"  Providers: {', '.join(providers)}")

        # Show provider rate limits
        for provider in providers:
            if provider in RATE_LIMITS:
                config = RATE_LIMITS[provider]
                logger.info(
                    f"    - {provider}: "
                    f"{config['requests']} req/{config['period']}s, "
                    f"cache: {config['cache_ttl']}s"
                )


async def clear_cache(provider: str = None):
    """
    Clear cache for provider or all providers.

    Args:
        provider: Provider name (None for all)
    """
    try:
        rate_limiter = get_rate_limit_manager()

        if provider:
            if provider not in RATE_LIMITS:
                logger.error(f"Unknown provider: {provider}")
                logger.info(f"Available providers: {', '.join(RATE_LIMITS.keys())}")
                return

            rate_limiter.clear_cache(provider)
            logger.info(f"Cleared cache for {provider}")
        else:
            rate_limiter.clear_cache()
            logger.info("Cleared all cache")

    except Exception as e:
        logger.error(f"Error clearing cache: {e}", exc_info=True)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PulseAI Events Scheduler - Smart event fetching with rate limit awareness"
    )

    parser.add_argument(
        "--category",
        choices=['crypto', 'markets', 'sports', 'tech', 'world'],
        help="Category to fetch (default: all)"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force fetch even if rate limit reached"
    )

    parser.add_argument(
        "--show-schedule",
        action="store_true",
        help="Show fetch schedule and exit"
    )

    parser.add_argument(
        "--clear-cache",
        nargs="?",
        const="all",
        metavar="PROVIDER",
        help="Clear cache for provider (or all)"
    )

    args = parser.parse_args()

    # Show schedule
    if args.show_schedule:
        asyncio.run(show_schedule())
        return

    # Clear cache
    if args.clear_cache:
        provider = None if args.clear_cache == "all" else args.clear_cache
        asyncio.run(clear_cache(provider))
        return

    # Schedule fetches
    asyncio.run(schedule_fetches(args.category, args.force))


if __name__ == "__main__":
    main()

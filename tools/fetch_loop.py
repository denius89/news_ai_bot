#!/usr/bin/env python3
"""
Fetch Loop with Auto-Posting Integration.

This script runs a continuous loop to fetch news, generate digests,
and automatically post them to Telegram channels.
"""

import asyncio
import argparse
import logging
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.optimized_parser import run_optimized_parser
from telegram_bot.handlers.digest_handler import get_digest_handler, auto_post_digest
from ai_modules.metrics import get_metrics

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/fetch_loop.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


class FetchLoop:
    """
    Continuous fetch loop with auto-posting integration.

    Features:
    - Configurable intervals
    - AI filtering
    - Auto-posting to Telegram
    - Graceful shutdown
    - Metrics tracking
    """

    def __init__(self, interval: int = 30, ai_filter: bool = True, auto_post: bool = False):
        """Initialize fetch loop."""
        self.interval = interval
        self.ai_filter = ai_filter
        self.auto_post = auto_post
        self.running = False
        self.metrics = get_metrics()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info(f"FetchLoop initialized: interval={interval}s, ai_filter={ai_filter}, auto_post={auto_post}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    async def _run_fetch_cycle(self) -> bool:
        """
        Run a single fetch cycle.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Starting fetch cycle...")
            start_time = datetime.now(timezone.utc)

            # Run optimized parser
            if self.ai_filter:
                logger.info("Running with AI filtering enabled")
                result = await run_optimized_parser()
            else:
                logger.info("Running without AI filtering")
                result = await run_optimized_parser()

            if not result.get("success", False):
                logger.error(f"Fetch cycle failed: {result.get('error', 'Unknown error')}")
                return False

            # Log results
            processed = result.get("processed", 0)
            saved = result.get("saved", 0)
            ai_calls = result.get("ai_calls", 0)

            logger.info(f"Fetch cycle completed: processed={processed}, saved={saved}, ai_calls={ai_calls}")

            # Run auto-posting if enabled
            if self.auto_post:
                logger.info("Running auto-posting...")
                post_result = await auto_post_digest()

                if post_result.get("success", False):
                    published = post_result.get("published_count", 0)
                    logger.info(f"Auto-posting completed: published={published} digests")
                else:
                    logger.warning(f"Auto-posting failed: {post_result.get('reason', 'Unknown error')}")

            # Calculate cycle time
            cycle_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"Cycle completed in {cycle_time:.2f} seconds")

            return True

        except Exception as e:
            logger.error(f"Error in fetch cycle: {e}")
            return False

    async def run(self):
        """Run the continuous fetch loop."""
        self.running = True
        logger.info("Starting fetch loop...")

        cycle_count = 0

        while self.running:
            try:
                cycle_count += 1
                logger.info(f"Starting cycle #{cycle_count}")

                # Run fetch cycle
                success = await self._run_fetch_cycle()

                if success:
                    logger.info(f"Cycle #{cycle_count} completed successfully")
                else:
                    logger.error(f"Cycle #{cycle_count} failed")

                # Wait for next cycle
                if self.running:
                    logger.info(f"Waiting {self.interval} seconds until next cycle...")
                    await asyncio.sleep(self.interval)

            except asyncio.CancelledError:
                logger.info("Fetch loop cancelled")
                break
            except Exception as e:
                logger.error(f"Unexpected error in fetch loop: {e}")
                if self.running:
                    logger.info(f"Waiting {self.interval} seconds before retry...")
                    await asyncio.sleep(self.interval)

        logger.info("Fetch loop stopped")

    async def stop(self):
        """Stop the fetch loop gracefully."""
        logger.info("Stopping fetch loop...")
        self.running = False


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Fetch loop with auto-posting")
    parser.add_argument("--interval", type=int, default=30, help="Interval between cycles in seconds (default: 30)")
    parser.add_argument("--ai-filter", action="store_true", help="Enable AI filtering")
    parser.add_argument("--auto-post", action="store_true", help="Enable auto-posting to Telegram")
    parser.add_argument("--once", action="store_true", help="Run only once instead of continuous loop")

    args = parser.parse_args()

    # Create fetch loop
    fetch_loop = FetchLoop(interval=args.interval, ai_filter=args.ai_filter, auto_post=args.auto_post)

    try:
        if args.once:
            # Run single cycle
            logger.info("Running single fetch cycle...")
            success = await fetch_loop._run_fetch_cycle()
            if success:
                logger.info("Single cycle completed successfully")
                sys.exit(0)
            else:
                logger.error("Single cycle failed")
                sys.exit(1)
        else:
            # Run continuous loop
            await fetch_loop.run()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        await fetch_loop.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

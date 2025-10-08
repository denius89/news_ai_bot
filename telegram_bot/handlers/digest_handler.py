"""
Telegram Auto-Posting Handler for PulseDigest 2.0.

This module handles automatic posting of digests to Telegram channels
with proper formatting, deduplication, and error handling.
"""

from database.service import get_async_service
from ai_modules.metrics import get_metrics
import asyncio
import logging
import re
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, parse_qs, urlencode

import yaml
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramAPIError

# Add project root to path
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


logger = logging.getLogger("digest_handler")


class TelegramDigestHandler:
    """
    Handles automatic posting of digests to Telegram channels.

    Features:
    - Idempotent posting (no duplicates)
    - PulseDigest 2.0 formatting
    - Rate limiting and error handling
    - Metrics tracking
    - Dry run support
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize digest handler with configuration."""
        self.config = self._load_config(config_path)
        self.metrics = get_metrics()

        # Configuration
        self.autopublish_config = self.config.get("autopublish", {})
        self.enabled = self.autopublish_config.get("enabled", False)
        self.dry_run = self.autopublish_config.get("dry_run", True)
        self.interval_minutes = self.autopublish_config.get("interval_minutes", 30)
        self.min_gap_minutes = self.autopublish_config.get("min_gap_minutes", 10)
        self.format_version = self.autopublish_config.get("format", "pulse_digest_v2")

        # Telegram configuration
        self.bot_token = self.config.get("telegram", {}).get("bot_token")
        self.channel_id = self.config.get("telegram", {}).get("channel_id")

        # Bot instance
        self.bot = None
        if self.bot_token and self.bot_token != "${TELEGRAM_BOT_TOKEN}":
            try:
                self.bot = Bot(token=self.bot_token)
            except Exception as e:
                logger.warning(f"Failed to initialize bot: {e}")
                self.bot = None

        # Category emojis for formatting
        self.category_emojis = {
            "crypto": "🪙",
            "tech": "💻",
            "sports": "🏀",
            "world": "🌍",
            "markets": "📈",
            "unknown": "📰",
        }

        # Rate limiting
        self.last_post_time = 0
        self.min_post_interval = 1.0  # 1 second between posts

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "app.yaml"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def _setup_publish_logger(self) -> None:
        """Setup dedicated logger for publish operations."""
        publish_logger = logging.getLogger("publish")
        publish_logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        for handler in publish_logger.handlers[:]:
            publish_logger.removeHandler(handler)

        # Add file handler for publish.log
        log_path = Path("logs/publish.log")
        log_path.parent.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        file_handler.setFormatter(formatter)

        publish_logger.addHandler(file_handler)
        publish_logger.propagate = False  # Don't propagate to root logger

    def _clean_url(self, url: str) -> str:
        """
        Clean URL by removing UTM parameters and shortening if needed.

        Args:
            url: Original URL

        Returns:
            Cleaned URL
        """
        try:
            # Parse URL
            parsed = urlparse(url)

            # Remove UTM parameters
            query_params = parse_qs(parsed.query)
            utm_params = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"]

            for param in utm_params:
                query_params.pop(param, None)

            # Rebuild URL
            if query_params:
                new_query = urlencode(query_params, doseq=True)
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
            else:
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

            # Shorten if too long
            if len(clean_url) > 80:
                clean_url = clean_url[:77] + "..."

            return clean_url

        except Exception as e:
            logger.debug(f"Error cleaning URL {url}: {e}")
            return url

    def _escape_markdown_v2(self, text: str) -> str:
        """
        Escape special characters for Markdown v2.

        Args:
            text: Text to escape

        Returns:
            Escaped text
        """
        # Characters that need escaping in Markdown v2
        escape_chars = ["_", "*", "[", "]", "(", ")", "~", "`",
                        ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]

        for char in escape_chars:
            text = text.replace(char, f"\\{char}")

        return text

    def _format_digest_message(self, digest: Dict[str, Any]) -> str:
        """
        Format digest for Telegram using PulseDigest 2.0 format.

        Args:
            digest: Digest data

        Returns:
            Formatted message (max 1024 characters)
        """
        try:
            title = digest.get("title", "")
            summary = digest.get("summary", "")
            why_important = digest.get("why_important", "")
            category = digest.get("category", "unknown")
            source = digest.get("source", "")
            published_at = digest.get("published_at", "")

            # Get category emoji
            emoji = self.category_emojis.get(category, "📰")

            # Clean and escape text
            title = self._escape_markdown_v2(title)[:100]
            summary = self._escape_markdown_v2(summary)[:200]
            why_important = self._escape_markdown_v2(why_important)[:150]

            # Format date
            try:
                if published_at:
                    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    date_str = dt.strftime("%d.%m.%Y %H:%M")
                else:
                    date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
            except BaseException:
                date_str = datetime.now().strftime("%d.%m.%Y %H:%M")

            # Clean source URL
            clean_source = self._clean_url(source) if source else ""

            # Build message
            message_parts = [
                f"{emoji} *{title}*",
                f"",
                f"🗞️ {summary}",
                f"",
                f"💡 Почему это важно: {why_important}",
                f"",
                f"📅 {date_str} | 🔗 {clean_source}",
            ]

            message = "\n".join(message_parts)

            # Ensure message is within Telegram limits
            if len(message) > 1024:
                # Truncate summary and why_important if needed
                max_summary = 150
                max_why = 100

                summary = summary[:max_summary] + "..." if len(summary) > max_summary else summary
                why_important = why_important[:max_why] + \
                    "..." if len(why_important) > max_why else why_important

                message_parts = [
                    f"{emoji} *{title}*",
                    f"",
                    f"🗞️ {summary}",
                    f"",
                    f"💡 Почему это важно: {why_important}",
                    f"",
                    f"📅 {date_str} | 🔗 {clean_source}",
                ]

                message = "\n".join(message_parts)

            return message

        except Exception as e:
            logger.error(f"Error formatting digest message: {e}")
            return f"📰 *{title}*\n\n{summary}"

    def _should_publish(self, digest: Dict[str, Any]) -> bool:
        """
        Check if digest should be published based on timing and status.

        Args:
            digest: Digest data

        Returns:
            True if should publish, False otherwise
        """
        try:
            # Check if already published
            if digest.get("published", False):
                return False

            # Check if digest is ready
            if digest.get("status") != "ready":
                return False

            # Check minimum gap between posts
            last_published = self.metrics.get_metrics_summary().get("last_digest_published_timestamp", "")
            if last_published:
                try:
                    last_time = datetime.fromisoformat(last_published.replace("Z", "+00:00"))
                    min_gap = timedelta(minutes=self.min_gap_minutes)

                    if datetime.now(timezone.utc) - last_time < min_gap:
                        return False
                except BaseException:
                    pass

            # Check rate limiting
            current_time = time.time()
            if current_time - self.last_post_time < self.min_post_interval:
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking if should publish: {e}")
            return False

    async def _get_unpublished_digests(self) -> List[Dict[str, Any]]:
        """
        Get digests that are ready for publishing.

        Returns:
            List of unpublished digests
        """
        try:
            db_service = get_async_service()

            # Query for unpublished digests
            query = """
                SELECT id, title, summary, why_important, category, source,
                       published_at, created_at, status, published
                FROM digests
                WHERE status = 'ready' AND published = false
                ORDER BY created_at DESC
                LIMIT 10
            """

            result = await db_service.execute_query(query)
            return result

        except Exception as e:
            logger.error(f"Error getting unpublished digests: {e}")
            return []

    async def _mark_digest_published(self, digest_id: int) -> None:
        """
        Mark digest as published in database.

        Args:
            digest_id: ID of the digest
        """
        try:
            db_service = get_async_service()

            # Update digest status
            query = """
                UPDATE digests
                SET published = true, published_at = NOW()
                WHERE id = %s
            """

            await db_service.execute_query(query, (digest_id,))

            # Update metadata
            metadata_query = """
                INSERT INTO metadata (key, value, updated_at)
                VALUES ('last_published_digest_id', %s, NOW())
                ON CONFLICT (key) DO UPDATE SET
                    value = EXCLUDED.value,
                    updated_at = EXCLUDED.updated_at
            """

            await db_service.execute_query(metadata_query, (str(digest_id),))

            logger.info(f"Marked digest {digest_id} as published")

        except Exception as e:
            logger.error(f"Error marking digest {digest_id} as published: {e}")

    async def _send_telegram_message(self, message: str, retries: int = 3) -> bool:
        """
        Send message to Telegram channel with retry logic.

        Args:
            message: Message to send
            retries: Number of retries

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.bot or not self.channel_id:
            logger.error("Bot or channel not configured")
            return False

        for attempt in range(retries):
            try:
                # Rate limiting
                current_time = time.time()
                time_since_last = current_time - self.last_post_time

                if time_since_last < self.min_post_interval:
                    sleep_time = self.min_post_interval - time_since_last
                    await asyncio.sleep(sleep_time)

                # Send message
                await self.bot.send_message(chat_id=self.channel_id, text=message, parse_mode="MarkdownV2")

                self.last_post_time = time.time()
                return True

            except TelegramRetryAfter as e:
                logger.warning(f"Rate limited, retry after {e.retry_after} seconds")
                await asyncio.sleep(e.retry_after)
                continue

            except TelegramBadRequest as e:
                logger.error(f"Bad request to Telegram API: {e}")
                break  # Don't retry bad requests

            except TelegramAPIError as e:
                logger.error(f"Telegram API error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    continue
                break

            except Exception as e:
                logger.error(
                    f"Unexpected error sending message (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                break

        return False

    async def auto_post_digest(self) -> Dict[str, Any]:
        """
        Automatically post digest to Telegram channel.

        Returns:
            Dictionary with posting results
        """
        # Setup logger
        self._setup_publish_logger()
        publish_logger = logging.getLogger("publish")

        start_time = time.time()

        try:
            # Check if autopublish is enabled
            if not self.enabled:
                publish_logger.info("Autopublish is disabled")
                return {
                    "success": False,
                    "reason": "disabled",
                    "message": "Autopublish is disabled"}

            # Get unpublished digests
            digests = await self._get_unpublished_digests()

            if not digests:
                publish_logger.info("No new digests to publish")
                self.metrics.increment_autopublish_skipped_no_content()
                return {
                    "success": True,
                    "reason": "no_content",
                    "message": "No new digests to publish",
                    "digests_checked": 0,
                }

            publish_logger.info(f"Found {len(digests)} unpublished digests")

            published_count = 0
            errors = []

            for digest in digests:
                try:
                    # Check if should publish
                    if not self._should_publish(digest):
                        continue

                    # Format message
                    message = self._format_digest_message(digest)

                    if self.dry_run:
                        publish_logger.info(
                            f"DRY RUN: Would publish digest #{digest['id']} → {self.channel_id}")
                        publish_logger.info(f"Message preview: {message[:100]}...")

                        # In dry run, just mark as published for testing
                        await self._mark_digest_published(digest["id"])
                        published_count += 1

                    else:
                        # Send to Telegram
                        success = await self._send_telegram_message(message)

                        if success:
                            # Mark as published
                            await self._mark_digest_published(digest["id"])

                            # Update metrics
                            self.metrics.increment_digests_published_total()
                            self.metrics.update_last_digest_published_timestamp(
                                datetime.now(timezone.utc).isoformat())

                            publish_logger.info(
                                f"Published digest #{digest['id']} → {self.channel_id}")
                            published_count += 1

                        else:
                            error_msg = f"Failed to publish digest #{digest['id']}"
                            publish_logger.error(error_msg)
                            self.metrics.increment_digests_publish_errors_total()
                            errors.append(error_msg)

                except Exception as e:
                    error_msg = f"Error processing digest #{digest.get('id', 'unknown')}: {e}"
                    publish_logger.error(error_msg)
                    self.metrics.increment_digests_publish_errors_total()
                    errors.append(error_msg)

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_autopublish_latency(latency_ms)

            result = {
                "success": published_count > 0 or not errors,
                "published_count": published_count,
                "digests_checked": len(digests),
                "errors": errors,
                "latency_ms": latency_ms,
                "dry_run": self.dry_run,
            }

            if published_count > 0:
                publish_logger.info(f"Successfully processed {published_count} digests")
            elif errors:
                publish_logger.error(f"Failed to publish any digests: {errors}")
            else:
                publish_logger.info("No digests met publishing criteria")

            return result

        except Exception as e:
            error_msg = f"Critical error in auto_post_digest: {e}"
            publish_logger.error(error_msg)
            logger.error(error_msg)

            self.metrics.increment_digests_publish_errors_total()

            return {
                "success": False,
                "reason": "critical_error",
                "message": error_msg,
                "published_count": 0,
                "digests_checked": 0,
                "errors": [error_msg],
            }

    async def close(self) -> None:
        """Close bot connection."""
        if self.bot:
            await self.bot.session.close()


# Global handler instance
_handler_instance: Optional[TelegramDigestHandler] = None


def get_digest_handler() -> TelegramDigestHandler:
    """Get global digest handler instance."""
    global _handler_instance
    if _handler_instance is None:
        _handler_instance = TelegramDigestHandler()
    return _handler_instance


async def auto_post_digest() -> Dict[str, Any]:
    """
    Convenience function to auto-post digests.

    Returns:
        Dictionary with posting results
    """
    handler = get_digest_handler()
    return await handler.auto_post_digest()

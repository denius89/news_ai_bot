"""
Events Stream Service for PulseAI.

This module provides real-time event updates via Server-Sent Events (SSE).
"""

import logging
import time
import json
from typing import Dict, Optional, Any
from datetime import datetime, timezone
from collections import defaultdict

logger = logging.getLogger("events_stream")


class EventsStream:
    """
    Real-time events stream via Server-Sent Events (SSE).

    Features:
    - SSE-based real-time updates
    - Per-user rate limiting (30s between updates)
    - Connection management
    - Event broadcasting
    """

    def __init__(self):
        """Initialize events stream."""
        self.connections: Dict[int, Any] = {}  # user_id -> connection
        self.last_update: Dict[int, float] = defaultdict(float)
        self.update_interval = 30  # seconds

        logger.info("EventsStream initialized")

    def add_connection(self, user_id: int, connection: Any):
        """
        Add user connection to stream.

        Args:
            user_id: Telegram user ID
            connection: Connection object
        """
        self.connections[user_id] = connection
        logger.info(f"Added connection for user {user_id}, total connections: {len(self.connections)}")

    def remove_connection(self, user_id: int):
        """
        Remove user connection from stream.

        Args:
            user_id: Telegram user ID
        """
        if user_id in self.connections:
            del self.connections[user_id]
            logger.info(f"Removed connection for user {user_id}, remaining: {len(self.connections)}")

    def can_send_update(self, user_id: int) -> bool:
        """
        Check if update can be sent (rate limit: 30s).

        Args:
            user_id: Telegram user ID

        Returns:
            True if update can be sent
        """
        last = self.last_update.get(user_id, 0)
        now = time.time()

        if now - last < self.update_interval:
            logger.debug(
                f"Rate limit for user {user_id}: " f"last update {now - last:.1f}s ago, need {self.update_interval}s"
            )
            return False

        return True

    async def broadcast_event(self, event_type: str, event_data: Dict, user_ids: Optional[list] = None):
        """
        Broadcast event to connected clients.

        Args:
            event_type: Event type (new, updated, removed)
            event_data: Event data dictionary
            user_ids: List of user IDs to send to (None for all)
        """
        try:
            message = {
                "type": event_type,
                "data": event_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            message_json = json.dumps(message)

            # Determine target users
            if user_ids is None:
                target_users = list(self.connections.keys())
            else:
                target_users = [uid for uid in user_ids if uid in self.connections]

            sent_count = 0
            failed_count = 0

            for user_id in target_users:
                try:
                    # Check rate limit
                    if not self.can_send_update(user_id):
                        continue

                    # Send message
                    connection = self.connections.get(user_id)
                    if connection:
                        await self._send_sse_message(connection, message_json)
                        self.last_update[user_id] = time.time()
                        sent_count += 1

                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    failed_count += 1
                    # Remove failed connection
                    self.remove_connection(user_id)

            logger.info(
                f"Broadcast {event_type}: sent to {sent_count} users, "
                f"failed: {failed_count}, total connections: {len(self.connections)}"
            )

        except Exception as e:
            logger.error(f"Error broadcasting event: {e}")

    async def send_to_user(self, user_id: int, event_type: str, event_data: Dict) -> bool:
        """
        Send event to specific user.

        Args:
            user_id: Telegram user ID
            event_type: Event type
            event_data: Event data

        Returns:
            True if sent successfully
        """
        try:
            if user_id not in self.connections:
                logger.debug(f"User {user_id} not connected to stream")
                return False

            # Check rate limit
            if not self.can_send_update(user_id):
                logger.debug(f"Rate limit reached for user {user_id}")
                return False

            message = {
                "type": event_type,
                "data": event_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            message_json = json.dumps(message)

            # Send message
            connection = self.connections[user_id]
            await self._send_sse_message(connection, message_json)
            self.last_update[user_id] = time.time()

            logger.debug(f"Sent {event_type} to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error sending to user {user_id}: {e}")
            self.remove_connection(user_id)
            return False

    async def _send_sse_message(self, connection: Any, message: str):
        """
        Send SSE formatted message.

        Args:
            connection: Connection object
            message: JSON message string
        """
        # Format as SSE
        sse_message = f"data: {message}\n\n"  # noqa: F841

        # Send via connection (implementation depends on Flask/async framework)
        # For now, this is a placeholder
        # In Flask, this would be: yield sse_message
        # In async framework: await connection.send(sse_message)
        pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Get stream statistics.

        Returns:
            Dictionary with statistics
        """
        now = time.time()

        active_users = []
        idle_users = []

        for user_id, last_update in self.last_update.items():
            if user_id in self.connections:
                time_since_update = now - last_update
                if time_since_update < 60:  # Active in last minute
                    active_users.append(user_id)
                else:
                    idle_users.append(user_id)

        return {
            "total_connections": len(self.connections),
            "active_users": len(active_users),
            "idle_users": len(idle_users),
            "update_interval": self.update_interval,
        }


# Global instance
_events_stream = None


def get_events_stream() -> EventsStream:
    """Get global Events Stream instance."""
    global _events_stream
    if _events_stream is None:
        _events_stream = EventsStream()
    return _events_stream


__all__ = ["EventsStream", "get_events_stream"]

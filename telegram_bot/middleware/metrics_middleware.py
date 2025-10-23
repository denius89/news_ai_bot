"""
Metrics collection middleware for Telegram bot.

Automatically collects performance metrics and user behavior analytics.
"""

import logging
import json
import time
from typing import Any, Awaitable, Callable, Dict, Optional
from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.types import Update

logger = logging.getLogger("telegram_bot.metrics")


class MetricsMiddleware(BaseMiddleware):
    """
    Metrics collection middleware.

    Automatically tracks:
    - Handler execution time
    - Success/failure rates
    - User behavior patterns
    - Performance metrics
    """

    def __init__(self):
        super().__init__()

        # Metrics storage
        self.metrics = {
            "handler_calls": 0,
            "handler_errors": 0,
            "total_execution_time": 0.0,
            "user_actions": {},
            "command_usage": {},
            "callback_usage": {},
        }

    async def __call__(
        self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]], event: Update, data: Dict[str, Any]
    ) -> Any:
        """
        Process update with metrics collection.

        Args:
            handler: Next handler in chain
            event: Telegram update
            data: Handler data

        Returns:
            Handler result
        """
        start_time = time.time()
        user_id = data.get("user_id")

        # Determine handler type and name
        handler_type, handler_name = self._get_handler_info(event)

        try:
            # Call handler
            result = await handler(event, data)

            # Record successful execution
            execution_time = time.time() - start_time
            await self._record_success(event, handler_type, handler_name, execution_time, user_id)

            return result

        except Exception as e:
            # Record error
            execution_time = time.time() - start_time
            await self._record_error(event, handler_type, handler_name, execution_time, user_id, e)
            raise

    def _get_handler_info(self, event: Update) -> tuple[str, str]:
        """Extract handler type and name from event."""
        if hasattr(event, "message") and event.message:
            if event.message.text and event.message.text.startswith("/"):
                command = event.message.text.split()[0].lower()
                return "command", command
            else:
                return "message", "text_message"
        elif hasattr(event, "callback_query") and event.callback_query:
            if event.callback_query.data:
                # Extract handler name from callback data
                callback_data = (
                    event.callback_query.data.split(":")[0]
                    if ":" in event.callback_query.data
                    else event.callback_query.data
                )
                return "callback", callback_data
            else:
                return "callback", "unknown_callback"
        else:
            return "unknown", "unknown_handler"

    async def _record_success(
        self, event: Update, handler_type: str, handler_name: str, execution_time: float, user_id: Optional[int]
    ):
        """Record successful handler execution."""
        self.metrics["handler_calls"] += 1
        self.metrics["total_execution_time"] += execution_time

        # Record user action
        if user_id:
            if user_id not in self.metrics["user_actions"]:
                self.metrics["user_actions"][user_id] = 0
            self.metrics["user_actions"][user_id] += 1

        # Record handler usage
        if handler_type == "command":
            if handler_name not in self.metrics["command_usage"]:
                self.metrics["command_usage"][handler_name] = 0
            self.metrics["command_usage"][handler_name] += 1
        elif handler_type == "callback":
            if handler_name not in self.metrics["callback_usage"]:
                self.metrics["callback_usage"][handler_name] = 0
            self.metrics["callback_usage"][handler_name] += 1

        # Log structured metrics
        logger.info(
            json.dumps(
                {
                    "event": "handler_success",
                    "handler_type": handler_type,
                    "handler_name": handler_name,
                    "execution_time_ms": round(execution_time * 1000, 2),
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )

    async def _record_error(
        self,
        event: Update,
        handler_type: str,
        handler_name: str,
        execution_time: float,
        user_id: Optional[int],
        error: Exception,
    ):
        """Record handler error."""
        self.metrics["handler_errors"] += 1

        # Log structured error metrics
        logger.error(
            json.dumps(
                {
                    "event": "handler_error",
                    "handler_type": handler_type,
                    "handler_name": handler_name,
                    "execution_time_ms": round(execution_time * 1000, 2),
                    "user_id": user_id,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get metrics summary.

        Returns:
            Dictionary with metrics summary
        """
        total_calls = self.metrics["handler_calls"]
        total_errors = self.metrics["handler_errors"]
        total_time = self.metrics["total_execution_time"]

        return {
            "total_handler_calls": total_calls,
            "total_handler_errors": total_errors,
            "error_rate": round(total_errors / max(total_calls, 1) * 100, 2),
            "average_execution_time_ms": round(total_time / max(total_calls, 1) * 1000, 2),
            "total_execution_time_ms": round(total_time * 1000, 2),
            "active_users": len(self.metrics["user_actions"]),
            "top_commands": dict(sorted(self.metrics["command_usage"].items(), key=lambda x: x[1], reverse=True)[:10]),
            "top_callbacks": dict(
                sorted(self.metrics["callback_usage"].items(), key=lambda x: x[1], reverse=True)[:10]
            ),
        }

    def reset_metrics(self):
        """Reset all metrics (useful for testing or periodic resets)."""
        self.metrics = {
            "handler_calls": 0,
            "handler_errors": 0,
            "total_execution_time": 0.0,
            "user_actions": {},
            "command_usage": {},
            "callback_usage": {},
        }
        logger.info("Metrics reset")

    def get_user_metrics(self, user_id: int) -> Dict[str, Any]:
        """
        Get metrics for specific user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with user metrics
        """
        return {
            "total_actions": self.metrics["user_actions"].get(user_id, 0),
            "command_usage": {cmd: count for cmd, count in self.metrics["command_usage"].items()},
            "callback_usage": {cb: count for cb, count in self.metrics["callback_usage"].items()},
        }

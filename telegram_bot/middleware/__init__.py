# telegram_bot/middleware/__init__.py
"""
Middleware package for Telegram bot.

Provides centralized error handling, user management, rate limiting,
and metrics collection for all bot handlers.
"""

from .error_handler import ErrorHandlerMiddleware
from .user_middleware import UserMiddleware
from .rate_limiter import RateLimiterMiddleware
from .metrics_middleware import MetricsMiddleware

__all__ = [
    "ErrorHandlerMiddleware",
    "UserMiddleware",
    "RateLimiterMiddleware",
    "MetricsMiddleware",
]

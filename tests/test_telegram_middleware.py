"""
Basic tests for Telegram bot middleware.

Tests core middleware functionality without external dependencies.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from telegram_bot.middleware.error_handler import ErrorHandlerMiddleware
from telegram_bot.middleware.user_middleware import UserMiddleware
from telegram_bot.middleware.rate_limiter import RateLimiterMiddleware
from telegram_bot.middleware.metrics_middleware import MetricsMiddleware
from telegram_bot.utils.error_messages import ERROR_MESSAGES, get_error_message


class TestErrorHandlerMiddleware:
    """Test error handler middleware."""

    def test_error_messages_exist(self):
        """Test that error messages are defined."""
        assert len(ERROR_MESSAGES) > 0
        assert "unexpected_error" in ERROR_MESSAGES
        assert "rate_limit" in ERROR_MESSAGES

    def test_get_error_message_formatting(self):
        """Test error message formatting."""
        message = get_error_message("rate_limit", seconds=30)
        assert "30" in message
        assert "секунд" in message

    def test_get_error_message_fallback(self):
        """Test error message fallback for unknown keys."""
        message = get_error_message("unknown_key")
        assert message == ERROR_MESSAGES["unexpected_error"]


class TestRateLimiterMiddleware:
    """Test rate limiter middleware."""

    def test_rate_limits_configuration(self):
        """Test rate limits are properly configured."""
        middleware = RateLimiterMiddleware()

        assert "commands" in middleware.rate_limits

        # Check limits are reasonable
        assert middleware.rate_limits["commands"]["limit"] == 5
        assert middleware.rate_limits["commands"]["window"] == 60

    def test_check_rate_limit_allows_first_request(self):
        """Test that first request is allowed."""
        middleware = RateLimiterMiddleware()

        # First request should be allowed
        assert middleware._check_rate_limit(12345, "commands") is True

    def test_check_rate_limit_blocks_excessive_requests(self):
        """Test that excessive requests are blocked."""
        middleware = RateLimiterMiddleware()
        user_id = 12345
        action_type = "commands"

        # Fill up the rate limit
        limit = middleware.rate_limits[action_type]["limit"]
        for _ in range(limit):
            middleware._record_action(user_id, action_type)

        # Next request should be blocked
        assert middleware._check_rate_limit(user_id, action_type) is False

    def test_get_user_stats(self):
        """Test user stats retrieval."""
        middleware = RateLimiterMiddleware()
        user_id = 12345

        # Record some actions
        middleware._record_action(user_id, "commands")
        middleware._record_action(user_id, "commands")

        stats = middleware.get_user_stats(user_id)

        assert "commands" in stats
        assert stats["commands"]["current_count"] == 2
        assert stats["commands"]["limit"] == 5
        assert stats["commands"]["remaining"] == 3


class TestMetricsMiddleware:
    """Test metrics middleware."""

    def test_metrics_initialization(self):
        """Test metrics are properly initialized."""
        middleware = MetricsMiddleware()

        assert middleware.metrics["handler_calls"] == 0
        assert middleware.metrics["handler_errors"] == 0
        assert middleware.metrics["total_execution_time"] == 0.0
        assert isinstance(middleware.metrics["user_actions"], dict)
        assert isinstance(middleware.metrics["command_usage"], dict)
        assert isinstance(middleware.metrics["callback_usage"], dict)

    def test_get_handler_info_message(self):
        """Test handler info extraction from message."""
        middleware = MetricsMiddleware()

        # Mock update with message
        update = Mock()
        update.message = Mock()
        update.message.text = "/start"
        update.callback_query = None

        handler_type, handler_name = middleware._get_handler_info(update)

        assert handler_type == "command"
        assert handler_name == "/start"

    def test_get_handler_info_callback(self):
        """Test handler info extraction from callback."""
        middleware = MetricsMiddleware()

        # Mock update with callback query
        update = Mock()
        update.message = None
        update.callback_query = Mock()
        update.callback_query.data = "start"

        handler_type, handler_name = middleware._get_handler_info(update)

        assert handler_type == "callback"
        assert handler_name == "start"

    def test_get_metrics_summary(self):
        """Test metrics summary generation."""
        middleware = MetricsMiddleware()

        # Simulate some metrics
        middleware.metrics["handler_calls"] = 100
        middleware.metrics["handler_errors"] = 5
        middleware.metrics["total_execution_time"] = 50.0
        middleware.metrics["command_usage"] = {"/start": 50, "/help": 30}

        summary = middleware.get_metrics_summary()

        assert summary["total_handler_calls"] == 100
        assert summary["total_handler_errors"] == 5
        assert summary["error_rate"] == 5.0  # 5/100 * 100
        assert summary["average_execution_time_ms"] == 500.0  # 50/100 * 1000
        assert summary["top_commands"]["/start"] == 50

    def test_reset_metrics(self):
        """Test metrics reset functionality."""
        middleware = MetricsMiddleware()

        # Add some data
        middleware.metrics["handler_calls"] = 100
        middleware.metrics["user_actions"][123] = 5

        # Reset
        middleware.reset_metrics()

        assert middleware.metrics["handler_calls"] == 0
        assert middleware.metrics["user_actions"] == {}


class TestUserMiddleware:
    """Test user middleware."""

    def test_extract_user_info_from_message(self):
        """Test user info extraction from message."""
        middleware = UserMiddleware()

        # Mock update with message
        update = Mock()
        update.message = Mock()
        update.message.from_user = Mock()
        update.message.from_user.id = 12345
        update.message.from_user.username = "testuser"
        update.message.from_user.first_name = "Test"
        update.message.from_user.last_name = "User"
        update.message.from_user.language_code = "ru"
        update.message.from_user.is_bot = False
        update.callback_query = None

        user_info = middleware._extract_user_info(update)

        assert user_info is not None
        assert user_info["telegram_id"] == 12345
        assert user_info["username"] == "testuser"
        assert user_info["first_name"] == "Test"
        assert user_info["last_name"] == "User"
        assert user_info["language_code"] == "ru"
        assert user_info["is_bot"] is False

    def test_extract_user_info_from_callback(self):
        """Test user info extraction from callback query."""
        middleware = UserMiddleware()

        # Mock update with callback query
        update = Mock()
        update.message = None
        update.callback_query = Mock()
        update.callback_query.from_user = Mock()
        update.callback_query.from_user.id = 67890
        update.callback_query.from_user.username = "callbackuser"
        update.callback_query.from_user.first_name = "Callback"
        update.callback_query.from_user.last_name = None
        update.callback_query.from_user.language_code = "en"
        update.callback_query.from_user.is_bot = False

        user_info = middleware._extract_user_info(update)

        assert user_info is not None
        assert user_info["telegram_id"] == 67890
        assert user_info["username"] == "callbackuser"
        assert user_info["first_name"] == "Callback"
        assert user_info["last_name"] is None
        assert user_info["language_code"] == "en"

    def test_extract_user_info_no_user(self):
        """Test user info extraction when no user present."""
        middleware = UserMiddleware()

        # Mock update without user
        update = Mock()
        update.message = Mock()
        update.message.from_user = None
        update.callback_query = None

        user_info = middleware._extract_user_info(update)

        assert user_info is None


# Integration tests
class TestMiddlewareIntegration:
    """Test middleware integration."""

    @pytest.mark.asyncio
    async def test_middleware_chain_order(self):
        """Test that middleware are applied in correct order."""
        # This would test the actual middleware chain execution
        # For now, just verify they can be instantiated together
        error_middleware = ErrorHandlerMiddleware()
        user_middleware = UserMiddleware()
        rate_middleware = RateLimiterMiddleware()
        metrics_middleware = MetricsMiddleware()

        # All should be instantiable
        assert error_middleware is not None
        assert user_middleware is not None
        assert rate_middleware is not None
        assert metrics_middleware is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

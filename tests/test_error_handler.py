"""
Tests for standardized error handling system.
"""

import pytest
from utils.error_handler import (
    PulseAIError,
    DatabaseError,
    NetworkError,
    AIServiceError,
    TelegramError,
    ParsingError,
    ValidationError,
    ConfigurationError,
    ErrorSeverity,
    ErrorCategory,
    retry_on_error,
    safe_execute,
    async_safe_execute,
    handle_database_error,
    handle_network_error,
    handle_parsing_error,
    raise_database_error,
    raise_network_error,
    raise_ai_service_error,
    raise_telegram_error,
    raise_parsing_error,
    raise_validation_error,
    raise_configuration_error,
)


class TestPulseAIError:
    """Test cases for PulseAIError base class."""

    def test_basic_error_creation(self):
        """Test basic error creation."""
        error = PulseAIError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.category == ErrorCategory.UNKNOWN
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.details == {}
        assert error.cause is None

    def test_error_with_details(self):
        """Test error creation with details."""
        cause = ValueError("Original error")
        error = PulseAIError(
            message="Test error",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            details={"table": "users", "operation": "insert"},
            cause=cause,
        )

        assert error.message == "Test error"
        assert error.category == ErrorCategory.DATABASE
        assert error.severity == ErrorSeverity.HIGH
        assert error.details == {"table": "users", "operation": "insert"}
        assert error.cause == cause

    @patch('utils.error_handler.logger')
    def test_error_logging(self, mock_logger):
        """Test that errors are logged appropriately."""
        # Test critical error
        PulseAIError("Critical error", severity=ErrorSeverity.CRITICAL)
        mock_logger.critical.assert_called_once()

        # Test high severity error
        PulseAIError("High severity error", severity=ErrorSeverity.HIGH)
        mock_logger.error.assert_called_once()

        # Test medium severity error
        PulseAIError("Medium severity error", severity=ErrorSeverity.MEDIUM)
        mock_logger.warning.assert_called_once()

        # Test low severity error
        PulseAIError("Low severity error", severity=ErrorSeverity.LOW)
        mock_logger.info.assert_called_once()


class TestSpecificErrors:
    """Test cases for specific error types."""

    def test_database_error(self):
        """Test DatabaseError creation."""
        cause = Exception("Connection failed")
        error = DatabaseError(
            "Database connection failed",
            operation="connect",
            table="users",
            query="SELECT * FROM users",
            cause=cause,
        )

        assert error.message == "Database connection failed"
        assert error.category == ErrorCategory.DATABASE
        assert error.severity == ErrorSeverity.HIGH
        assert error.details["operation"] == "connect"
        assert error.details["table"] == "users"
        assert error.details["query"] == "SELECT * FROM users"
        assert error.cause == cause

    def test_network_error(self):
        """Test NetworkError creation."""
        cause = Exception("Connection timeout")
        error = NetworkError(
            "Request timeout", url="https://example.com", status_code=408, timeout=30.0, cause=cause
        )

        assert error.message == "Request timeout"
        assert error.category == ErrorCategory.NETWORK
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.details["url"] == "https://example.com"
        assert error.details["status_code"] == 408
        assert error.details["timeout"] == 30.0
        assert error.cause == cause

    def test_ai_service_error(self):
        """Test AIServiceError creation."""
        cause = Exception("API limit exceeded")
        error = AIServiceError(
            "AI service unavailable", model="gpt-4", prompt_length=1500, cause=cause
        )

        assert error.message == "AI service unavailable"
        assert error.category == ErrorCategory.AI_SERVICE
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.details["model"] == "gpt-4"
        assert error.details["prompt_length"] == 1500
        assert error.cause == cause

    def test_telegram_error(self):
        """Test TelegramError creation."""
        cause = Exception("Chat not found")
        error = TelegramError(
            "Failed to send message", chat_id=12345, user_id=67890, retry_after=60, cause=cause
        )

        assert error.message == "Failed to send message"
        assert error.category == ErrorCategory.TELEGRAM
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.details["chat_id"] == 12345
        assert error.details["user_id"] == 67890
        assert error.details["retry_after"] == 60
        assert error.cause == cause

    def test_parsing_error(self):
        """Test ParsingError creation."""
        cause = Exception("Invalid XML")
        error = ParsingError(
            "Failed to parse RSS feed",
            source="example.com",
            url="https://example.com/rss",
            content_type="text/xml",
            cause=cause,
        )

        assert error.message == "Failed to parse RSS feed"
        assert error.category == ErrorCategory.PARSING
        assert error.severity == ErrorSeverity.LOW
        assert error.details["source"] == "example.com"
        assert error.details["url"] == "https://example.com/rss"
        assert error.details["content_type"] == "text/xml"
        assert error.cause == cause

    def test_validation_error(self):
        """Test ValidationError creation."""
        error = ValidationError(
            "Invalid input value", field="email", value="invalid-email", expected_type=str
        )

        assert error.message == "Invalid input value"
        assert error.category == ErrorCategory.VALIDATION
        assert error.severity == ErrorSeverity.LOW
        assert error.details["field"] == "email"
        assert error.details["value"] == "invalid-email"
        assert error.details["expected_type"] == "str"

    def test_configuration_error(self):
        """Test ConfigurationError creation."""
        cause = Exception("File not found")
        error = ConfigurationError(
            "Configuration file missing",
            config_key="database_url",
            config_file="config.yaml",
            cause=cause,
        )

        assert error.message == "Configuration file missing"
        assert error.category == ErrorCategory.CONFIGURATION
        assert error.severity == ErrorSeverity.HIGH
        assert error.details["config_key"] == "database_url"
        assert error.details["config_file"] == "config.yaml"
        assert error.cause == cause


class TestRetryDecorator:
    """Test cases for retry_on_error decorator."""

    def test_sync_retry_success(self):
        """Test sync retry decorator with eventual success."""
        call_count = 0

        @retry_on_error(max_attempts=3, delay=0.01)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"

        result = flaky_function()
        assert result == "success"
        assert call_count == 3

    def test_sync_retry_failure(self):
        """Test sync retry decorator with eventual failure."""
        call_count = 0

        @retry_on_error(max_attempts=3, delay=0.01)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_failing_function()

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_async_retry_success(self):
        """Test async retry decorator with eventual success."""
        call_count = 0

        @retry_on_error(max_attempts=3, delay=0.01)
        async def async_flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"

        result = await async_flaky_function()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_async_retry_failure(self):
        """Test async retry decorator with eventual failure."""
        call_count = 0

        @retry_on_error(max_attempts=3, delay=0.01)
        async def async_always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            await async_always_failing_function()

        assert call_count == 3

    def test_retry_with_specific_exceptions(self):
        """Test retry decorator with specific exception types."""
        call_count = 0

        @retry_on_error(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def function_with_multiple_exceptions():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Should retry")
            else:
                raise RuntimeError("Should not retry")

        with pytest.raises(RuntimeError, match="Should not retry"):
            function_with_multiple_exceptions()

        assert call_count == 2  # Only retried once for ValueError


class TestSafeExecute:
    """Test cases for safe_execute functions."""

    def test_sync_safe_execute_success(self):
        """Test sync safe_execute with success."""

        def successful_function(x, y):
            return x + y

        result = safe_execute(successful_function, 2, 3)
        assert result == 5

    def test_sync_safe_execute_failure(self):
        """Test sync safe_execute with failure."""

        def failing_function():
            raise ValueError("Test error")

        result = safe_execute(failing_function, default_return="default")
        assert result == "default"

    def test_sync_safe_execute_reraise(self):
        """Test sync safe_execute with reraise."""

        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            safe_execute(failing_function, reraise=True)

    @pytest.mark.asyncio
    async def test_async_safe_execute_success(self):
        """Test async safe_execute with success."""

        async def async_successful_function(x, y):
            return x + y

        result = await async_safe_execute(async_successful_function, 2, 3)
        assert result == 5

    @pytest.mark.asyncio
    async def test_async_safe_execute_failure(self):
        """Test async safe_execute with failure."""

        async def async_failing_function():
            raise ValueError("Test error")

        result = await async_safe_execute(async_failing_function, default_return="default")
        assert result == "default"

    @pytest.mark.asyncio
    async def test_async_safe_execute_reraise(self):
        """Test async safe_execute with reraise."""

        async def async_failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await async_safe_execute(async_failing_function, reraise=True)


class TestErrorHandlingDecorators:
    """Test cases for error handling decorators."""

    def test_handle_database_error_sync(self):
        """Test handle_database_error decorator for sync functions."""

        @handle_database_error("test operation")
        def failing_database_function():
            raise Exception("Database connection failed")

        with pytest.raises(DatabaseError) as exc_info:
            failing_database_function()

        assert "Database error during test operation" in str(exc_info.value)
        assert exc_info.value.details["operation"] == "test operation"

    @pytest.mark.asyncio
    async def test_handle_database_error_async(self):
        """Test handle_database_error decorator for async functions."""

        @handle_database_error("async test operation")
        async def async_failing_database_function():
            raise Exception("Async database connection failed")

        with pytest.raises(DatabaseError) as exc_info:
            await async_failing_database_function()

        assert "Database error during async test operation" in str(exc_info.value)
        assert exc_info.value.details["operation"] == "async test operation"

    def test_handle_network_error(self):
        """Test handle_network_error decorator."""

        @handle_network_error("HTTP request")
        def failing_network_function():
            raise Exception("Network timeout")

        with pytest.raises(NetworkError) as exc_info:
            failing_network_function()

        assert "Network error during HTTP request" in str(exc_info.value)

    def test_handle_parsing_error(self):
        """Test handle_parsing_error decorator."""

        @handle_parsing_error("RSS feed")
        def failing_parsing_function():
            raise Exception("Invalid XML")

        with pytest.raises(ParsingError) as exc_info:
            failing_parsing_function()

        assert "Parsing error from RSS feed" in str(exc_info.value)
        assert exc_info.value.details["source"] == "RSS feed"


class TestConvenienceFunctions:
    """Test cases for convenience error raising functions."""

    def test_raise_database_error(self):
        """Test raise_database_error convenience function."""
        cause = Exception("Original error")

        with pytest.raises(DatabaseError) as exc_info:
            raise_database_error("Database failed", operation="insert", cause=cause)

        assert "Database failed" in str(exc_info.value)
        assert exc_info.value.details["operation"] == "insert"
        assert exc_info.value.cause == cause

    def test_raise_network_error(self):
        """Test raise_network_error convenience function."""
        cause = Exception("Connection failed")

        with pytest.raises(NetworkError) as exc_info:
            raise_network_error("Network failed", url="https://example.com", cause=cause)

        assert "Network failed" in str(exc_info.value)
        assert exc_info.value.details["url"] == "https://example.com"
        assert exc_info.value.cause == cause

    def test_raise_ai_service_error(self):
        """Test raise_ai_service_error convenience function."""
        cause = Exception("API error")

        with pytest.raises(AIServiceError) as exc_info:
            raise_ai_service_error("AI service failed", model="gpt-4", cause=cause)

        assert "AI service failed" in str(exc_info.value)
        assert exc_info.value.details["model"] == "gpt-4"
        assert exc_info.value.cause == cause

    def test_raise_telegram_error(self):
        """Test raise_telegram_error convenience function."""
        cause = Exception("Chat not found")

        with pytest.raises(TelegramError) as exc_info:
            raise_telegram_error("Telegram failed", chat_id=12345, cause=cause)

        assert "Telegram failed" in str(exc_info.value)
        assert exc_info.value.details["chat_id"] == 12345
        assert exc_info.value.cause == cause

    def test_raise_parsing_error(self):
        """Test raise_parsing_error convenience function."""
        cause = Exception("Invalid format")

        with pytest.raises(ParsingError) as exc_info:
            raise_parsing_error("Parsing failed", source="example.com", cause=cause)

        assert "Parsing failed" in str(exc_info.value)
        assert exc_info.value.details["source"] == "example.com"
        assert exc_info.value.cause == cause

    def test_raise_validation_error(self):
        """Test raise_validation_error convenience function."""
        with pytest.raises(ValidationError) as exc_info:
            raise_validation_error("Validation failed", field="email", value="invalid")

        assert "Validation failed" in str(exc_info.value)
        assert exc_info.value.details["field"] == "email"
        assert exc_info.value.details["value"] == "invalid"

    def test_raise_configuration_error(self):
        """Test raise_configuration_error convenience function."""
        cause = Exception("File not found")

        with pytest.raises(ConfigurationError) as exc_info:
            raise_configuration_error("Config failed", config_key="database_url", cause=cause)

        assert "Config failed" in str(exc_info.value)
        assert exc_info.value.details["config_key"] == "database_url"
        assert exc_info.value.cause == cause

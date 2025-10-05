"""
Standardized Error Handling System for PulseAI.

This module provides a unified approach to error handling across the entire project,
including custom exception classes, error logging, and retry mechanisms.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, Optional, Type, Union
from functools import wraps
from enum import Enum

logger = logging.getLogger("error_handler")


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization."""

    DATABASE = "database"
    NETWORK = "network"
    AI_SERVICE = "ai_service"
    TELEGRAM = "telegram"
    PARSING = "parsing"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class PulseAIError(Exception):
    """Base exception class for all PulseAI-specific errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.cause = cause

        # Log the error
        self._log_error()

    def _log_error(self):
        """Log the error with appropriate level based on severity."""
        log_message = f"[{self.category.value.upper()}] {self.message}"

        if self.details:
            log_message += f" | Details: {self.details}"

        if self.cause:
            log_message += f" | Caused by: {type(self.cause).__name__}: {self.cause}"

        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=True)
        elif self.severity == ErrorSeverity.HIGH:
            logger.error(log_message, exc_info=True)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)


class DatabaseError(PulseAIError):
    """Database-related errors."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        query: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        details = {}
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table
        if query:
            details["query"] = query

        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            details=details,
            cause=cause,
        )


class NetworkError(PulseAIError):
    """Network-related errors."""

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        timeout: Optional[float] = None,
        cause: Optional[Exception] = None,
    ):
        details = {}
        if url:
            details["url"] = url
        if status_code:
            details["status_code"] = status_code
        if timeout:
            details["timeout"] = timeout

        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            cause=cause,
        )


class AIServiceError(PulseAIError):
    """AI service-related errors."""

    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        prompt_length: Optional[int] = None,
        cause: Optional[Exception] = None,
    ):
        details = {}
        if model:
            details["model"] = model
        if prompt_length:
            details["prompt_length"] = prompt_length

        super().__init__(
            message=message,
            category=ErrorCategory.AI_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            cause=cause,
        )


class TelegramError(PulseAIError):
    """Telegram-related errors."""

    def __init__(
        self,
        message: str,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
        retry_after: Optional[int] = None,
        cause: Optional[Exception] = None,
    ):
        details = {}
        if chat_id:
            details["chat_id"] = chat_id
        if user_id:
            details["user_id"] = user_id
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message=message,
            category=ErrorCategory.TELEGRAM,
            severity=ErrorSeverity.MEDIUM,
            details=details,
            cause=cause,
        )


class ParsingError(PulseAIError):
    """Parsing-related errors."""

    def __init__(
        self,
        message: str,
        source: Optional[str] = None,
        url: Optional[str] = None,
        content_type: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        details = {}
        if source:
            details["source"] = source
        if url:
            details["url"] = url
        if content_type:
            details["content_type"] = content_type

        super().__init__(
            message=message,
            category=ErrorCategory.PARSING,
            severity=ErrorSeverity.LOW,
            details=details,
            cause=cause,
        )


class ValidationError(PulseAIError):
    """Validation-related errors."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        expected_type: Optional[Type] = None,
        cause: Optional[Exception] = None,
    ):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        if expected_type:
            details["expected_type"] = expected_type.__name__

        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            details=details,
            cause=cause,
        )


class ConfigurationError(PulseAIError):
    """Configuration-related errors."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        details = {}
        if config_key:
            details["config_key"] = config_key
        if config_file:
            details["config_file"] = config_file

        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            details=details,
            cause=cause,
        )


def retry_on_error(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    logger_instance: Optional[logging.Logger] = None,
):
    """
    Decorator for retrying functions on specific exceptions.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Factor to multiply delay by after each retry
        exceptions: Tuple of exception types to retry on
        logger_instance: Logger instance to use (defaults to module logger)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            log = logger_instance or logger
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        wait_time = delay * (backoff_factor**attempt)
                        log.warning(
                            "⚠️ Попытка %d/%d неудачна для %s: %s. Повтор через %.2fс",
                            attempt + 1,
                            max_attempts,
                            func.__name__,
                            e,
                            wait_time,
                        )
                        time.sleep(wait_time)
                    else:
                        log.error(
                            "❌ Все %d попыток неудачны для %s: %s", max_attempts, func.__name__, e
                        )

            raise last_exception

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            log = logger_instance or logger
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        wait_time = delay * (backoff_factor**attempt)
                        log.warning(
                            "⚠️ Попытка %d/%d неудачна для %s: %s. Повтор через %.2fс",
                            attempt + 1,
                            max_attempts,
                            func.__name__,
                            e,
                            wait_time,
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        log.error(
                            "❌ Все %d попыток неудачны для %s: %s", max_attempts, func.__name__, e
                        )

            raise last_exception

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def safe_execute(
    func: Callable,
    *args,
    default_return: Any = None,
    log_errors: bool = True,
    reraise: bool = False,
    **kwargs,
) -> Any:
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        *args: Positional arguments for the function
        default_return: Value to return if function fails
        log_errors: Whether to log errors
        reraise: Whether to reraise exceptions
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error("❌ Ошибка в safe_execute для %s: %s", func.__name__, e)

        if reraise:
            raise

        return default_return


async def async_safe_execute(
    func: Callable,
    *args,
    default_return: Any = None,
    log_errors: bool = True,
    reraise: bool = False,
    **kwargs,
) -> Any:
    """
    Safely execute an async function with error handling.

    Args:
        func: Async function to execute
        *args: Positional arguments for the function
        default_return: Value to return if function fails
        log_errors: Whether to log errors
        reraise: Whether to reraise exceptions
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or default_return on error
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error("❌ Ошибка в async_safe_execute для %s: %s", func.__name__, e)

        if reraise:
            raise

        return default_return


def handle_database_error(operation: str = "database operation") -> Callable:
    """
    Decorator for handling database errors with standardized exceptions.

    Args:
        operation: Description of the database operation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise DatabaseError(
                    message=f"Database error during {operation}",
                    operation=operation,
                    cause=e,
                )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise DatabaseError(
                    message=f"Database error during {operation}",
                    operation=operation,
                    cause=e,
                )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


def handle_network_error(operation: str = "network request") -> Callable:
    """
    Decorator for handling network errors with standardized exceptions.

    Args:
        operation: Description of the network operation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise NetworkError(
                    message=f"Network error during {operation}",
                    cause=e,
                )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise NetworkError(
                    message=f"Network error during {operation}",
                    cause=e,
                )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


def handle_parsing_error(source: str = "unknown source") -> Callable:
    """
    Decorator for handling parsing errors with standardized exceptions.

    Args:
        source: Source being parsed
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise ParsingError(
                    message=f"Parsing error from {source}",
                    source=source,
                    cause=e,
                )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise ParsingError(
                    message=f"Parsing error from {source}",
                    source=source,
                    cause=e,
                )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


# Convenience functions for common error patterns
def raise_database_error(
    message: str, operation: Optional[str] = None, cause: Optional[Exception] = None
):
    """Raise a standardized database error."""
    raise DatabaseError(message, operation=operation, cause=cause)


def raise_network_error(message: str, url: Optional[str] = None, cause: Optional[Exception] = None):
    """Raise a standardized network error."""
    raise NetworkError(message, url=url, cause=cause)


def raise_ai_service_error(
    message: str, model: Optional[str] = None, cause: Optional[Exception] = None
):
    """Raise a standardized AI service error."""
    raise AIServiceError(message, model=model, cause=cause)


def raise_telegram_error(
    message: str, chat_id: Optional[int] = None, cause: Optional[Exception] = None
):
    """Raise a standardized Telegram error."""
    raise TelegramError(message, chat_id=chat_id, cause=cause)


def raise_parsing_error(
    message: str, source: Optional[str] = None, cause: Optional[Exception] = None
):
    """Raise a standardized parsing error."""
    raise ParsingError(message, source=source, cause=cause)


def raise_validation_error(message: str, field: Optional[str] = None, value: Optional[Any] = None):
    """Raise a standardized validation error."""
    raise ValidationError(message, field=field, value=value)


def raise_configuration_error(
    message: str, config_key: Optional[str] = None, cause: Optional[Exception] = None
):
    """Raise a standardized configuration error."""
    raise ConfigurationError(message, config_key=config_key, cause=cause)

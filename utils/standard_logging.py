"""
Standardized Logging Utilities for PulseAI.

This module provides standardized logging functions and decorators
for consistent logging across the application.
"""

import functools
import logging
import time
from typing import Any, Callable, Dict, Optional, Union

logger = logging.getLogger("performance")


def log_function_call(
    level: int = logging.INFO, include_args: bool = False, include_result: bool = False
):
    """
    Decorator for logging function calls.

    Args:
        level: Logging level
        include_args: Whether to log function arguments
        include_result: Whether to log function result
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_logger = logging.getLogger(func.__module__)

            # Log function start
            args_str = ""
            if include_args and (args or kwargs):
                args_str = f" with args={args}, kwargs={kwargs}"

            func_logger.log(level, f"🔄 Calling {func.__name__}{args_str}")

            start_time = time.time()
            try:
                result = func(*args, **kwargs)

                # Log function success
                duration = time.time() - start_time
                result_str = ""
                if include_result and result is not None:
                    result_str = f" -> {result}"

                func_logger.log(
                    level, f"✅ {func.__name__} completed in {duration:.3f}s{result_str}"
                )

                # Log performance metrics
                logger.info(f"Function {func.__name__} took {duration:.3f}s")

                return result

            except Exception as e:
                # Log function error
                duration = time.time() - start_time
                func_logger.error(f"❌ {func.__name__} failed after {duration:.3f}s: {e}")
                raise

        return wrapper

    return decorator


def log_database_operation(operation: str):
    """
    Decorator for logging database operations.

    Args:
        operation: Type of database operation (e.g., 'SELECT', 'INSERT', 'UPDATE')
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            db_logger = logging.getLogger("database")

            start_time = time.time()
            try:
                result = func(*args, **kwargs)

                duration = time.time() - start_time
                db_logger.debug(f"✅ {operation} operation completed in {duration:.3f}s")

                # Log performance metrics
                logger.info(f"Database {operation} took {duration:.3f}s")

                return result

            except Exception as e:
                duration = time.time() - start_time
                db_logger.error(f"❌ {operation} operation failed after {duration:.3f}s: {e}")
                raise

        return wrapper

    return decorator


def log_api_call(url: str, method: str = "GET"):
    """
    Decorator for logging API calls.

    Args:
        url: API endpoint URL
        method: HTTP method
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            api_logger = logging.getLogger("api")

            api_logger.info(f"🌐 {method} {url}")

            start_time = time.time()
            try:
                result = func(*args, **kwargs)

                duration = time.time() - start_time
                api_logger.info(f"✅ {method} {url} completed in {duration:.3f}s")

                # Log performance metrics
                logger.info(f"API {method} {url} took {duration:.3f}s")

                return result

            except Exception as e:
                duration = time.time() - start_time
                api_logger.error(f"❌ {method} {url} failed after {duration:.3f}s: {e}")
                raise

        return wrapper

    return decorator


def log_parsing_operation(source_name: str):
    """
    Decorator for logging parsing operations.

    Args:
        source_name: Name of the source being parsed
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            parser_logger = logging.getLogger("parsers")

            parser_logger.info(f"📰 Parsing {source_name}")

            start_time = time.time()
            try:
                result = func(*args, **kwargs)

                duration = time.time() - start_time
                if isinstance(result, list):
                    count = len(result)
                    parser_logger.info(f"✅ Parsed {source_name}: {count} items in {duration:.3f}s")
                else:
                    parser_logger.info(f"✅ Parsed {source_name} in {duration:.3f}s")

                # Log performance metrics
                logger.info(f"Parsing {source_name} took {duration:.3f}s")

                return result

            except Exception as e:
                duration = time.time() - start_time
                parser_logger.error(f"❌ Failed to parse {source_name} after {duration:.3f}s: {e}")
                raise

        return wrapper

    return decorator


class StructuredLogger:
    """
    Structured logger for consistent log formatting.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, message: str, **kwargs):
        """Log info message with structured data."""
        if kwargs:
            structured_data = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.info(f"{message} | {structured_data}")
        else:
            self.logger.info(message)

    def error(self, message: str, **kwargs):
        """Log error message with structured data."""
        if kwargs:
            structured_data = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.error(f"{message} | {structured_data}")
        else:
            self.logger.error(message)

    def warning(self, message: str, **kwargs):
        """Log warning message with structured data."""
        if kwargs:
            structured_data = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.warning(f"{message} | {structured_data}")
        else:
            self.logger.warning(message)

    def debug(self, message: str, **kwargs):
        """Log debug message with structured data."""
        if kwargs:
            structured_data = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            self.logger.debug(f"{message} | {structured_data}")
        else:
            self.logger.debug(message)


def get_structured_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


# Performance monitoring utilities
class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(self, operation_name: str, logger_name: Optional[str] = None):
        self.operation_name = operation_name
        self.logger = logging.getLogger(logger_name or "performance")
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"🕐 Starting {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            if exc_type is None:
                self.logger.info(f"✅ {self.operation_name} completed in {duration:.3f}s")
            else:
                self.logger.error(f"❌ {self.operation_name} failed after {duration:.3f}s")

            # Log to performance logger
            perf_logger = logging.getLogger("performance")
            perf_logger.info(f"Operation {self.operation_name} took {duration:.3f}s")


# Convenience functions
def log_user_action(user_id: int, action: str, details: Optional[Dict] = None):
    """Log user action with structured data."""
    user_logger = logging.getLogger("user_actions")

    details_str = ""
    if details:
        details_str = " | " + " ".join([f"{k}={v}" for k, v in details.items()])

    user_logger.info(f"👤 User {user_id} performed {action}{details_str}")


def log_system_event(event: str, level: int = logging.INFO, **kwargs):
    """Log system event with structured data."""
    system_logger = logging.getLogger("system")

    kwargs_str = ""
    if kwargs:
        kwargs_str = " | " + " ".join([f"{k}={v}" for k, v in kwargs.items()])

    system_logger.log(level, f"🔧 {event}{kwargs_str}")


def log_business_metric(metric_name: str, value: Union[int, float, str], **kwargs):
    """Log business metric for monitoring."""
    metrics_logger = logging.getLogger("business_metrics")

    kwargs_str = ""
    if kwargs:
        kwargs_str = " | " + " ".join([f"{k}={v}" for k, v in kwargs.items()])

    metrics_logger.info(f"📊 {metric_name}={value}{kwargs_str}")

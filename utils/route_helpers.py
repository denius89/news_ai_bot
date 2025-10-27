"""
Route helpers for Flask endpoints.

Provides decorators and utilities for common route patterns like
pagination, error handling, and parameter validation.
"""

import logging
from functools import wraps
from flask import request, jsonify
from typing import Callable, Any, Dict

logger = logging.getLogger(__name__)


def validate_pagination(max_limit: int = 100) -> Callable:
    """
    Decorator to validate and inject pagination parameters.

    Args:
        max_limit: Maximum allowed limit per page (default: 100)

    Returns:
        Decorated function with page and limit parameters

    Usage:
        @app.route("/api/news")
        @validate_pagination(max_limit=50)
        def get_news(page, limit):
            # page and limit are already validated
            offset = (page - 1) * limit
            return get_data(limit=limit, offset=offset)
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                # Get page parameter (default: 1, minimum: 1)
                page = max(1, int(request.args.get("page", 1)))

                # Get limit parameter (default: 20, minimum: 1, maximum: max_limit)
                limit = int(request.args.get("limit", 20))
                limit = max(1, min(limit, max_limit))

                logger.debug(f"Pagination: page={page}, limit={limit}")

                # Inject pagination parameters
                kwargs["page"] = page
                kwargs["limit"] = limit

                return f(*args, **kwargs)

            except ValueError as e:
                logger.warning(f"Invalid pagination parameters: {e}")
                return (
                    jsonify({"error": "Invalid pagination parameters", "details": str(e)}),
                    400,
                )

        return wrapper

    return decorator


def handle_errors(f: Callable) -> Callable:
    """
    Decorator to handle exceptions and return proper JSON errors.

    Usage:
        @app.route("/api/data")
        @handle_errors
        def get_data():
            # Any exception will be caught and returned as JSON
            return {"data": process_data()}
    """

    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Error in {f.__name__}: {e}", exc_info=True)
            return (
                jsonify(
                    {
                        "error": "Internal server error",
                        "message": str(e),
                        "endpoint": f.__name__,
                    }
                ),
                500,
            )

    return wrapper


def build_pagination_response(data: list, page: int, limit: int, total: int) -> Dict[str, Any]:
    """
    Build standardized pagination response.

    Args:
        data: List of items for current page
        page: Current page number
        limit: Items per page
        total: Total number of items

    Returns:
        Dictionary with data and pagination metadata

    Example:
        {
            "data": [...],
            "pagination": {
                "page": 1,
                "limit": 20,
                "total": 150,
                "pages": 8,
                "has_next": true,
                "has_prev": false
            }
        }
    """
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return {
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    }


def calculate_offset(page: int, limit: int) -> int:
    """
    Calculate database offset from page and limit.

    Args:
        page: Page number (1-indexed)
        limit: Items per page

    Returns:
        Database offset (0-indexed)

    Example:
        calculate_offset(1, 20) -> 0
        calculate_offset(2, 20) -> 20
        calculate_offset(3, 20) -> 40
    """
    return (page - 1) * limit

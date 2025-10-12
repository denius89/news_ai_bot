"""
Events API Routes for PulseAI.

This module provides API endpoints for events and calendar functionality.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from database.events_service import get_events_service

logger = logging.getLogger("events_routes")

# Create blueprint
events_bp = Blueprint("events", __name__, url_prefix="/api/events")


@events_bp.route("/", methods=["GET"])
@cross_origin()
def get_events():
    """
    Get events within a date range with optional filtering.

    Query parameters:
    - from: Start date (YYYY-MM-DD format)
    - to: End date (YYYY-MM-DD format)
    - category: Filter by category (crypto, markets, sports, tech, world)
    - subcategory: Filter by subcategory
    - min_importance: Minimum importance threshold (0.0-1.0)
    - limit: Maximum number of events to return (default: 100)
    """
    try:
        # Parse query parameters
        from_date_str = request.args.get("from")
        to_date_str = request.args.get("to")
        category = request.args.get("category")
        subcategory = request.args.get("subcategory")
        min_importance = float(request.args.get("min_importance", 0.0))
        limit = int(request.args.get("limit", 100))

        # Parse dates
        if from_date_str:
            try:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                return jsonify({"success": False, "error": "Invalid from date format. Use YYYY-MM-DD"}), 400
        else:
            # Default to today
            from_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        if to_date_str:
            try:
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d").replace(
                    hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
                )
            except ValueError:
                return jsonify({"success": False, "error": "Invalid to date format. Use YYYY-MM-DD"}), 400
        else:
            # Default to 30 days from start date
            to_date = from_date + timedelta(days=30)

        # Validate date range
        if from_date > to_date:
            return jsonify({"success": False, "error": "From date must be before or equal to to date"}), 400

        # Validate parameters
        if min_importance < 0 or min_importance > 1:
            return jsonify({"success": False, "error": "min_importance must be between 0.0 and 1.0"}), 400

        if limit <= 0 or limit > 1000:
            return jsonify({"success": False, "error": "limit must be between 1 and 1000"}), 400

        # Get events service
        events_service = get_events_service()

        # Fetch events
        import asyncio
        events = asyncio.run(events_service.get_events_by_date_range(from_date, to_date, category))

        # Filter by subcategory if specified
        if subcategory:
            events = [e for e in events if e.subcategory == subcategory]

        # Filter by importance
        events = [e for e in events if e.importance >= min_importance]

        # Apply limit
        events = events[:limit]

        # Convert to JSON format
        events_data = []
        for event in events:
            event_data = {
                "id": event.id,
                "title": event.title,
                "category": event.category,
                "subcategory": event.subcategory,
                "starts_at": event.starts_at.isoformat(),
                "ends_at": event.ends_at.isoformat() if event.ends_at else None,
                "source": event.source,
                "link": event.link,
                "importance": event.importance,
                "description": event.description,
                "location": event.location,
                "organizer": event.organizer,
                "created_at": event.created_at.isoformat(),
            }
            events_data.append(event_data)

        return jsonify(
            {
                "success": True,
                "data": {
                    "events": events_data,
                    "count": len(events_data),
                    "date_range": {"from": from_date.isoformat(), "to": to_date.isoformat()},
                    "filters": {"category": category, "subcategory": subcategory, "min_importance": min_importance},
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@events_bp.route("/upcoming", methods=["GET"])
@cross_origin()
def get_upcoming_events():
    """
    Get upcoming events within specified days.

    Query parameters:
    - days: Number of days to look ahead (default: 30)
    - category: Filter by category
    - min_importance: Minimum importance threshold
    """
    try:
        # Parse query parameters
        days = int(request.args.get("days", 30))
        category = request.args.get("category")
        min_importance = float(request.args.get("min_importance", 0.0))

        # Validate parameters
        if days <= 0 or days > 365:
            return jsonify({"success": False, "error": "days must be between 1 and 365"}), 400

        if min_importance < 0 or min_importance > 1:
            return jsonify({"success": False, "error": "min_importance must be between 0.0 and 1.0"}), 400

        # Get events service
        events_service = get_events_service()

        # Fetch upcoming events (synchronous)
        events = events_service.get_upcoming_events_sync(
            days_ahead=days, category=category, min_importance=min_importance
        )

        # Convert to JSON format
        events_data = []
        for event in events:
            event_data = {
                "id": event.id,
                "title": event.title,
                "category": event.category,
                "subcategory": event.subcategory,
                "starts_at": event.starts_at.isoformat(),
                "ends_at": event.ends_at.isoformat() if event.ends_at else None,
                "source": event.source,
                "link": event.link,
                "importance": event.importance,
                "description": event.description,
                "location": event.location,
                "organizer": event.organizer,
                "created_at": event.created_at.isoformat(),
            }
            events_data.append(event_data)

        return jsonify(
            {
                "success": True,
                "data": {
                    "events": events_data,
                    "count": len(events_data),
                    "days_ahead": days,
                    "filters": {"category": category, "min_importance": min_importance},
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting upcoming events: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@events_bp.route("/today", methods=["GET"])
@cross_origin()
def get_today_events():
    """
    Get events for today.

    Query parameters:
    - category: Filter by category
    """
    try:
        # Parse query parameters
        category = request.args.get("category")

        # Get events service
        events_service = get_events_service()

        # Fetch today's events
        import asyncio
        events = asyncio.run(events_service.get_today_events(category=category))

        # Convert to JSON format
        events_data = []
        for event in events:
            event_data = {
                "id": event.id,
                "title": event.title,
                "category": event.category,
                "subcategory": event.subcategory,
                "starts_at": event.starts_at.isoformat(),
                "ends_at": event.ends_at.isoformat() if event.ends_at else None,
                "source": event.source,
                "link": event.link,
                "importance": event.importance,
                "description": event.description,
                "location": event.location,
                "organizer": event.organizer,
                "created_at": event.created_at.isoformat(),
            }
            events_data.append(event_data)

        return jsonify(
            {
                "success": True,
                "data": {
                    "events": events_data,
                    "count": len(events_data),
                    "date": datetime.now(timezone.utc).date().isoformat(),
                    "filters": {"category": category},
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting today's events: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@events_bp.route("/categories", methods=["GET"])
@cross_origin()
def get_categories():
    """
    Get available event categories and subcategories.
    """
    try:
        categories_data = {
            "crypto": {
                "name": "Cryptocurrency",
                "subcategories": {
                    "bitcoin": "Bitcoin",
                    "ethereum": "Ethereum",
                    "defi": "DeFi",
                    "nft": "NFT",
                    "general": "General",
                },
                "emoji": "🪙",
                "color": "#F7931A",
            },
            "markets": {
                "name": "Financial Markets",
                "subcategories": {
                    "monetary_policy": "Monetary Policy",
                    "employment": "Employment",
                    "inflation": "Inflation",
                    "economic_growth": "Economic Growth",
                    "earnings": "Earnings",
                    "general": "General",
                },
                "emoji": "📈",
                "color": "#00D4AA",
            },
            "sports": {
                "name": "Sports",
                "subcategories": {
                    "football": "Football",
                    "basketball": "Basketball",
                    "tennis": "Tennis",
                    "soccer": "Soccer",
                    "general": "General",
                },
                "emoji": "🏀",
                "color": "#FF6B6B",
            },
            "tech": {
                "name": "Technology",
                "subcategories": {
                    "ai": "Artificial Intelligence",
                    "software": "Software",
                    "hardware": "Hardware",
                    "startup": "Startups",
                    "general": "General",
                },
                "emoji": "💻",
                "color": "#4ECDC4",
            },
            "world": {
                "name": "World Events",
                "subcategories": {
                    "politics": "Politics",
                    "economics": "Economics",
                    "environment": "Environment",
                    "general": "General",
                },
                "emoji": "🌍",
                "color": "#45B7D1",
            },
        }

        return jsonify({"success": True, "data": categories_data})

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@events_bp.route("/stats", methods=["GET"])
@cross_origin()
def get_events_stats():
    """
    Get events statistics.
    """
    try:
        # Get events service
        events_service = get_events_service()

        # Get various event counts
        import asyncio
        today_events = asyncio.run(events_service.get_today_events())
        upcoming_events = asyncio.run(events_service.get_upcoming_events(days_ahead=7))
        upcoming_30d = asyncio.run(events_service.get_upcoming_events(days_ahead=30))

        # Calculate statistics
        stats = {
            "today": {"total": len(today_events), "by_category": {}},
            "upcoming_7d": {"total": len(upcoming_events), "by_category": {}},
            "upcoming_30d": {"total": len(upcoming_30d), "by_category": {}},
        }

        # Count by category
        for event_list, key in [
            (today_events, "today"),
            (upcoming_events, "upcoming_7d"),
            (upcoming_30d, "upcoming_30d"),
        ]:
            category_counts = {}
            for event in event_list:
                category = event.category
                category_counts[category] = category_counts.get(category, 0) + 1
            stats[key]["by_category"] = category_counts

        return jsonify({"success": True, "data": stats})

    except Exception as e:
        logger.error(f"Error getting events stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@events_bp.route("/<int:event_id>/result", methods=["GET"])
@cross_origin()
def get_event_result(event_id):
    """Get result data for completed event."""
    try:
        from database.db_models import supabase
        
        if not supabase:
            return jsonify({"success": False, "error": "Database not available"}), 500
        
        # Get event with result data
        result = supabase.table("events_new").select("*").eq("id", event_id).execute()
        
        if not result.data:
            return jsonify({"success": False, "error": "Event not found"}), 404
        
        event = result.data[0]
        
        return jsonify({
            "success": True,
            "data": {
                "id": event["id"],
                "title": event["title"],
                "status": event["status"],
                "result_data": event.get("result_data"),
                "updated_at": event.get("updated_at"),
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting event result: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@events_bp.route("/categories", methods=["GET"])
@cross_origin()
def get_event_categories():
    """Get available event categories with counts."""
    try:
        from database.db_models import supabase
        
        if not supabase:
            return jsonify({"success": False, "error": "Database not available"}), 500
        
        # Get category counts
        result = supabase.table("events_new").select("category").execute()
        
        category_counts = {}
        for event in result.data:
            category = event["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return jsonify({
            "success": True,
            "data": {
                "categories": category_counts,
                "total_events": sum(category_counts.values()),
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting event categories: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def register_events_routes(app):
    """Register events routes with Flask app."""
    app.register_blueprint(events_bp)
    logger.info("Events routes registered")

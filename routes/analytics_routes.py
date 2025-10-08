"""
Analytics Routes for Smart Content Posting.

This module provides API endpoints for analytics and insights
related to content publishing and engagement.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from ai_modules.metrics import get_metrics
from telegram_bot.services.content_scheduler import get_content_scheduler
from telegram_bot.services.post_selector import get_post_selector
from telegram_bot.services.feedback_tracker import get_feedback_tracker
from telegram_bot.handlers.review_handler import get_review_handler

logger = logging.getLogger("analytics_routes")

# Create blueprint
analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/posts_today", methods=["GET"])
@cross_origin()
def get_posts_today():
    """Get posts published today."""
    try:
        metrics = get_metrics()
        summary = metrics.get_metrics_summary()

        # Get today's posts (simplified - in real implementation, query database)
        today_posts = {
            "total_posts": summary.get("digests_published_total", 0),
            "posts_today": summary.get("digests_published_today", 0),
            "avg_post_length": summary.get("avg_post_length_chars", 0),
            "avg_ai_confidence": summary.get("avg_ai_confidence", 0.0),
            "avg_reaction_score": summary.get("avg_reaction_score", 0.0),
            "last_post_time": summary.get("last_digest_published_timestamp", ""),
            "current_window": summary.get("autopublish_window_current", "unknown"),
        }

        return jsonify({"success": True, "data": today_posts})

    except Exception as e:
        logger.error(f"Error getting posts today: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route("/engagement", methods=["GET"])
@cross_origin()
def get_engagement_analytics():
    """Get engagement analytics."""
    try:
        feedback_tracker = get_feedback_tracker()
        engagement_stats = feedback_tracker.get_engagement_stats()

        # Get top engaging categories
        top_categories = feedback_tracker.get_top_engaging_categories(limit=5)

        engagement_data = {
            "enabled": engagement_stats["enabled"],
            "tracked_posts": engagement_stats["tracked_posts"],
            "total_reactions": engagement_stats["total_reactions"],
            "average_engagement_score": engagement_stats["average_engagement_score"],
            "top_categories": [{"category": cat, "score": score} for cat, score in top_categories],
            "update_interval_min": engagement_stats["update_interval_min"],
        }

        return jsonify({"success": True, "data": engagement_data})

    except Exception as e:
        logger.error(f"Error getting engagement analytics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route("/top_categories", methods=["GET"])
@cross_origin()
def get_top_categories():
    """Get top categories by activity."""
    try:
        metrics = get_metrics()
        summary = metrics.get_metrics_summary()

        # Get category statistics (simplified - in real implementation, query database)
        category_stats = [
            {"category": "crypto", "posts": 15, "engagement": 0.85, "avg_score": 0.78},
            {"category": "tech", "posts": 12, "engagement": 0.78, "avg_score": 0.75},
            {"category": "sports", "posts": 8, "engagement": 0.72, "avg_score": 0.70},
            {"category": "world", "posts": 10, "engagement": 0.68, "avg_score": 0.73},
            {"category": "markets", "posts": 6, "engagement": 0.82, "avg_score": 0.80},
        ]

        # Sort by engagement score
        category_stats.sort(key=lambda x: x["engagement"], reverse=True)

        return jsonify(
            {
                "success": True,
                "data": {
                    "categories": category_stats,
                    "total_categories": len(category_stats),
                    "most_active": category_stats[0]["category"] if category_stats else None,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting top categories: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route("/schedule", methods=["GET"])
@cross_origin()
def get_schedule_analytics():
    """Get content schedule analytics."""
    try:
        scheduler = get_content_scheduler()
        schedule_info = scheduler.get_schedule_info()

        return jsonify({"success": True, "data": schedule_info})

    except Exception as e:
        logger.error(f"Error getting schedule analytics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route("/selection", methods=["GET"])
@cross_origin()
def get_selection_analytics():
    """Get post selection analytics."""
    try:
        selector = get_post_selector()
        selection_stats = selector.get_selection_stats()

        metrics = get_metrics()
        summary = metrics.get_metrics_summary()

        selection_data = {
            **selection_stats,
            "smart_priority_avg_score": summary.get("smart_priority_avg_score", 0.0),
            "smart_priority_skipped_total": summary.get("smart_priority_skipped_total", 0),
        }

        return jsonify({"success": True, "data": selection_data})

    except Exception as e:
        logger.error(f"Error getting selection analytics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route("/review", methods=["GET"])
@cross_origin()
def get_review_analytics():
    """Get review process analytics."""
    try:
        review_handler = get_review_handler()
        review_stats = review_handler.get_review_stats()

        metrics = get_metrics()
        summary = metrics.get_metrics_summary()

        review_data = {
            **review_stats,
            "review_approved_total": summary.get("review_approved_total", 0),
            "review_rejected_total": summary.get("review_rejected_total", 0),
            "review_expired_total": summary.get("review_expired_total", 0),
        }

        return jsonify({"success": True, "data": review_data})

    except Exception as e:
        logger.error(f"Error getting review analytics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route("/dashboard", methods=["GET"])
@cross_origin()
def get_dashboard_data():
    """Get comprehensive dashboard data."""
    try:
        metrics = get_metrics()
        summary = metrics.get_metrics_summary()

        # Get data from all analytics sources
        scheduler = get_content_scheduler()
        selector = get_post_selector()
        feedback_tracker = get_feedback_tracker()
        review_handler = get_review_handler()

        dashboard_data = {
            "overview": {
                "total_posts": summary.get("digests_published_total", 0),
                "posts_today": summary.get("digests_published_today", 0),
                "avg_engagement": summary.get("avg_reaction_score", 0.0),
                "smart_posting_enabled": summary.get("smart_posting_enabled", False),
            },
            "publishing": {
                "current_window": summary.get("autopublish_window_current", "unknown"),
                "window_posts_total": summary.get("autopublish_window_posts_total", 0),
                "skipped_out_of_window": summary.get("autopublish_skipped_out_of_window_total", 0),
                "avg_latency_ms": summary.get("autopublish_avg_latency_ms", 0.0),
            },
            "selection": {
                "smart_priority_avg_score": summary.get("smart_priority_avg_score", 0.0),
                "smart_priority_skipped_total": summary.get("smart_priority_skipped_total", 0),
                "recently_published_count": selector.get_selection_stats().get("recently_published_count", 0),
            },
            "engagement": {
                "total_reactions": summary.get("reactions_total", 0),
                "engagement_score_avg": summary.get("engagement_score_avg", 0.0),
                "reactions_to_ai_updates": summary.get("reactions_to_ai_updates_total", 0),
            },
            "review": {
                "enabled": review_handler.get_review_stats().get("enabled", False),
                "pending_reviews": review_handler.get_pending_reviews_count(),
                "approved_total": summary.get("review_approved_total", 0),
                "rejected_total": summary.get("review_rejected_total", 0),
            },
            "ai_optimization": {
                "teaser_generated_total": summary.get("teaser_generated_total", 0),
                "ai_calls_total": summary.get("ai_calls_total", 0),
                "ai_calls_saved_total": summary.get("ai_calls_saved_total", 0),
                "ai_error_rate": summary.get("ai_error_rate", 0.0),
            },
        }

        return jsonify({"success": True, "data": dashboard_data, "timestamp": datetime.now(timezone.utc).isoformat()})

    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@analytics_bp.route("/performance", methods=["GET"])
@cross_origin()
def get_performance_metrics():
    """Get performance metrics for the last 24 hours."""
    try:
        metrics = get_metrics()
        summary = metrics.get_metrics_summary()

        # Calculate performance metrics
        total_posts = summary.get("digests_published_total", 0)
        total_errors = summary.get("digests_publish_errors_total", 0)
        avg_latency = summary.get("autopublish_avg_latency_ms", 0.0)

        performance_data = {
            "publishing": {
                "total_posts": total_posts,
                "error_rate": (total_errors / max(1, total_posts)) * 100,
                "avg_latency_ms": avg_latency,
                "success_rate": ((total_posts - total_errors) / max(1, total_posts)) * 100,
            },
            "ai_efficiency": {
                "total_calls": summary.get("ai_calls_total", 0),
                "calls_saved": summary.get("ai_calls_saved_total", 0),
                "savings_percentage": (
                    summary.get("ai_calls_saved_total", 0) / max(1, summary.get("ai_calls_total", 1))
                )
                * 100,
                "avg_latency_ms": summary.get("ai_avg_latency_ms", 0.0),
            },
            "engagement": {
                "total_reactions": summary.get("reactions_total", 0),
                "avg_engagement_score": summary.get("engagement_score_avg", 0.0),
                "high_engagement_posts": summary.get("reactions_to_ai_updates_total", 0),
            },
            "system": {
                "uptime_seconds": summary.get("uptime_seconds", 0),
                "news_per_second": summary.get("news_per_second", 0.0),
                "memory_usage_mb": summary.get("memory_usage_mb", 0),
            },
        }

        return jsonify({"success": True, "data": performance_data})

    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def register_analytics_routes(app):
    """Register analytics routes with Flask app."""
    app.register_blueprint(analytics_bp)
    logger.info("Analytics routes registered")

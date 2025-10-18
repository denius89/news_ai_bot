"""
Metrics Routes - API endpoints for digest analytics and quality metrics.
"""

import logging
import json
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify

from database.db_models import supabase, get_daily_digest_analytics, get_digest_analytics

logger = logging.getLogger(__name__)

# Create metrics blueprint
metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/api/metrics/digests", methods=["GET"])
def get_digest_metrics():
    """
    GET /api/metrics/digests?days=7

    Returns digest analytics for specified number of days.
    Uses existing digest_analytics + digests.feedback_score data.
    """
    try:
        # Get query parameters
        days = int(request.args.get("days", 7))
        category = request.args.get("category")  # Optional filter

        # Validate days parameter
        if days < 1 or days > 365:
            return jsonify({"error": "Days must be between 1 and 365"}), 400

        # Get analytics data
        if category:
            # Filter by category if specified
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)

            analytics_data = get_digest_analytics(days=days)
            # Filter by category (would need to be implemented in get_digest_analytics)
            logger.info(f"Category filter requested for {category}, but not implemented yet")
        else:
            analytics_data = get_digest_analytics(days=days)

        # Also get today's analytics
        today_analytics = get_daily_digest_analytics()

        # Calculate summary metrics
        total_digests = len(analytics_data)
        successful_generations = sum(1 for a in analytics_data if a.get("success", True))
        avg_generation_time = sum(a.get("generation_time_ms", 0) for a in analytics_data) / max(total_digests, 1) / 1000

        # Response structure
        response = {
            "period_days": days,
            "summary": {
                "total_digests": total_digests,
                "successful_generations": successful_generations,
                "success_rate": successful_generations / max(total_digests, 1),
                "avg_generation_time_sec": round(avg_generation_time, 2),
            },
            "today": today_analytics,
            "details": analytics_data[-10:] if analytics_data else [],  # Last 10 records
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"Digest metrics requested: {days} days, {total_digests} total digests")
        return jsonify(response)

    except ValueError as e:
        logger.error(f"Invalid parameters for digest metrics: {e}")
        return jsonify({"error": "Invalid parameters"}), 400
    except Exception as e:
        logger.error(f"Error getting digest metrics: {e}")
        return jsonify({"error": "Internal server error"}), 500


@metrics_bp.route("/api/metrics/quality", methods=["GET"])
def get_quality_metrics():
    """
    GET /api/metrics/quality

    Returns quality metrics including feedback scores and QA results.
    """
    try:
        if not supabase:
            return jsonify({"error": "Database not available"}), 503

        # Get recent digests with feedback scores
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        digests = (
            supabase.table("digests")
            .select("feedback_score, feedback_count, confidence, style, category")
            .gte("created_at", start_date.isoformat())
            .not_.is_("feedback_score", "null")
            .gte("feedback_count", 1)
            .execute()
        )

        if not digests.data:
            return jsonify(
                {
                    "period_days": 7,
                    "total_digests": 0,
                    "avg_feedback_score": 0.0,
                    "quality_distribution": {},
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        # Calculate quality metrics
        feedback_scores = [d.get("feedback_score", 0) for d in digests.data if d.get("feedback_score")]
        avg_feedback = sum(feedback_scores) / len(feedback_scores) if feedback_scores else 0.0

        # Quality distribution by style
        quality_by_style = {}
        for digest in digests.data:
            style = digest.get("style", "unknown")
            score = digest.get("feedback_score", 0)
            if style not in quality_by_style:
                quality_by_style[style] = []
            quality_by_style[style].append(score)

        # Calculate averages by style
        style_quality = {}
        for style, scores in quality_by_style.items():
            style_quality[style] = {"avg_score": round(sum(scores) / len(scores), 3), "count": len(scores)}

        response = {
            "period_days": 7,
            "total_digests": len(digests.data),
            "avg_feedback_score": round(avg_feedback, 3),
            "quality_distribution": style_quality,
            "high_quality_count": len([s for s in feedback_scores if s >= 0.8]),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"Quality metrics: {len(digests.data)} digests, avg score: {avg_feedback:.3f}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error getting quality metrics: {e}")
        return jsonify({"error": "Internal server error"}), 500

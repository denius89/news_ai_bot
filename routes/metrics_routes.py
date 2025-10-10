"""
Metrics Routes - API endpoints for digest quality metrics and analytics.

This module provides endpoints for:
- /metrics - Current digest metrics
- /metrics/history - Historical metrics data
"""

from flask import Blueprint, jsonify, request
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from database.db_models import get_digest_analytics, get_digest_analytics_history

logger = logging.getLogger("metrics")

metrics_bp = Blueprint('metrics', __name__)


@metrics_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Get current digest metrics for today.
    
    Returns:
        JSON with metrics data:
        {
            "status": "success",
            "data": {
                "generated_today": 124,
                "avg_confidence": 0.87,
                "avg_generation_time_sec": 2.3,
                "skipped_low_quality": 12,
                "feedback_count": 58,
                "avg_feedback_score": 0.81
            }
        }
    """
    try:
        analytics = get_digest_analytics()
        
        return jsonify({
            "status": "success",
            "data": {
                "generated_today": analytics.get("generated_count", 0),
                "avg_confidence": round(analytics.get("avg_confidence", 0.0), 2),
                "avg_generation_time_sec": round(analytics.get("avg_generation_time_sec", 0.0), 2),
                "skipped_low_quality": analytics.get("skipped_low_quality", 0),
                "feedback_count": analytics.get("feedback_count", 0),
                "avg_feedback_score": round(analytics.get("avg_feedback_score", 0.0), 2)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@metrics_bp.route('/metrics/history', methods=['GET'])
def get_metrics_history():
    """
    Get metrics history for last N days.
    
    Query params:
        days: Number of days to retrieve (default: 7)
    
    Returns:
        JSON with historical metrics data
    """
    try:
        days = request.args.get('days', 7, type=int)
        
        # Limit to reasonable range
        if days < 1 or days > 30:
            days = 7
        
        history = get_digest_analytics_history(days)
        
        return jsonify({
            "status": "success",
            "data": history,
            "days_requested": days
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting metrics history: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@metrics_bp.route('/metrics/health', methods=['GET'])
def get_metrics_health():
    """
    Get health status based on metrics.
    
    Returns:
        JSON with health status and recommendations
    """
    try:
        analytics = get_digest_analytics()
        
        # Calculate health indicators
        avg_confidence = analytics.get("avg_confidence", 0.0)
        generated_count = analytics.get("generated_count", 0)
        avg_generation_time = analytics.get("avg_generation_time_sec", 0.0)
        
        # Determine health status
        if avg_confidence >= 0.8 and generated_count > 0:
            health_status = "excellent"
        elif avg_confidence >= 0.7 and generated_count > 0:
            health_status = "good"
        elif avg_confidence >= 0.6:
            health_status = "fair"
        else:
            health_status = "poor"
        
        # Generate recommendations
        recommendations = []
        if avg_confidence < 0.7:
            recommendations.append("Consider improving news source quality")
        if avg_generation_time > 5.0:
            recommendations.append("Generation time is high, check AI performance")
        if generated_count == 0:
            recommendations.append("No digests generated today")
        
        return jsonify({
            "status": "success",
            "data": {
                "health_status": health_status,
                "avg_confidence": round(avg_confidence, 2),
                "generated_count": generated_count,
                "avg_generation_time_sec": round(avg_generation_time, 2),
                "recommendations": recommendations
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting metrics health: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
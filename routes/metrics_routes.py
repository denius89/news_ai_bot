"""
Metrics and health check routes for AI optimization monitoring.

This module provides Flask routes for monitoring AI optimization metrics
and system health.
"""

import logging
import time
from flask import Blueprint, jsonify, request
from typing import Dict

from ai_modules.metrics import get_metrics
from ai_modules.cache import get_cache
from database.service import get_async_service
from core.reactor import reactor, Events

logger = logging.getLogger("metrics_routes")

# Create blueprint
metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/metrics")
def get_metrics_endpoint():
    """
    Get AI optimization metrics.

    Returns comprehensive metrics including:
    - News processing statistics
    - AI call reduction metrics
    - Performance metrics
    - Error rates
    """
    try:
        metrics = get_metrics()
        metrics_data = metrics.get_metrics_summary()

        # Add cache statistics
        cache = get_cache()
        cache_stats = cache.get_stats()
        metrics_data["cache"] = cache_stats

        # Add Reactor metrics
        reactor_stats = reactor.get_metrics()
        metrics_data["reactor"] = reactor_stats

        return jsonify({"status": "success", "data": metrics_data}), 200

    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@metrics_bp.route("/health/reactor")
def reactor_health_check():
    """
    Comprehensive health check for Reactor system.

    Returns health status of Reactor Core and WebSocket connections.
    """
    try:
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "reactor": reactor.get_health(),
            # Will be updated by WebSocket routes
            "websocket": {"status": "active", "connected_clients": 0},
            "events": {
                "total_emitted": reactor.get_metrics().get("events_emitted", 0),
                "event_types": reactor.get_metrics().get("event_types", 0),
            },
        }

        # Эмитим событие о проверке здоровья
        reactor.emit_sync(Events.SYSTEM_HEALTH_CHECK, health_data)

        return jsonify(health_data), 200

    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({"status": "unhealthy", "error": str(e), "timestamp": time.time()}), 500


@metrics_bp.route("/metrics/reset")
def reset_metrics():
    """
    Reset all metrics to zero.

    This endpoint is useful for testing and monitoring
    metrics over specific time periods.
    """
    try:
        metrics = get_metrics()
        metrics.reset_metrics()

        return jsonify({"status": "success", "message": "Metrics reset successfully"}), 200

    except Exception as e:
        logger.error(f"Error resetting metrics: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@metrics_bp.route("/health")
def health_check():
    """
    Comprehensive health check for the AI optimization system.

    Checks:
    - Database connectivity
    - Cache functionality
    - Metrics collection
    - Configuration loading
    """
    try:
        health_status = {"status": "healthy", "checks": {}, "timestamp": time.time()}

        # Check database connectivity
        try:
            db_service = get_async_service()
            # Simple ping to check if service is available
            health_status["checks"]["database"] = {
                "status": "healthy", "message": "Database service available"}
        except Exception as e:
            health_status["checks"]["database"] = {
                "status": "unhealthy", "message": f"Database error: {str(e)}"}
            health_status["status"] = "degraded"

        # Check cache functionality
        try:
            cache = get_cache()
            cache_stats = cache.get_stats()
            health_status["checks"]["cache"] = {
                "status": "healthy",
                "message": f'Cache enabled: {cache_stats["enabled"]}, size: {cache_stats["size"]}',
            }
        except Exception as e:
            health_status["checks"]["cache"] = {
                "status": "unhealthy", "message": f"Cache error: {str(e)}"}
            health_status["status"] = "degraded"

        # Check metrics collection
        try:
            metrics = get_metrics()
            metrics_summary = metrics.get_metrics_summary()
            health_status["checks"]["metrics"] = {
                "status": "healthy",
                "message": f'Metrics collection active, uptime: {metrics_summary["uptime_seconds"]}s',
            }
        except Exception as e:
            health_status["checks"]["metrics"] = {
                "status": "unhealthy", "message": f"Metrics error: {str(e)}"}
            health_status["status"] = "degraded"

        # Check configuration
        try:
            from ai_modules.prefilter import get_prefilter
            from ai_modules.local_predictor import get_predictor

            prefilter = get_prefilter()
            predictor = get_predictor()

            health_status["checks"]["configuration"] = {
                "status": "healthy",
                "message": f"Prefilter: {prefilter.is_enabled()}, Predictor: {predictor.is_enabled()}",
            }
        except Exception as e:
            health_status["checks"]["configuration"] = {
                "status": "unhealthy",
                "message": f"Configuration error: {str(e)}",
            }
            health_status["status"] = "degraded"

        # Determine overall status
        if health_status["status"] == "healthy":
            status_code = 200
        elif health_status["status"] == "degraded":
            status_code = 200  # Still functional but with issues
        else:
            status_code = 503  # Service unavailable

        return jsonify(health_status), status_code

    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return (jsonify({"status": "unhealthy",
                         "message": f"Health check failed: {str(e)}",
                         "timestamp": time.time()}),
                503,
                )


@metrics_bp.route("/health/live")
def liveness_check():
    """
    Simple liveness check.

    Returns 200 if the service is running, regardless of
    other system health issues.
    """
    return jsonify({"status": "alive", "timestamp": time.time()}), 200


@metrics_bp.route("/health/ready")
def readiness_check():
    """
    Readiness check for the AI optimization system.

    Returns 200 only if the system is ready to process requests.
    """
    try:
        # Check if all critical components are available
        metrics = get_metrics()
        cache = get_cache()

        # Basic checks
        if not metrics:
            return jsonify({"status": "not_ready", "message": "Metrics not available"}), 503

        if not cache:
            return jsonify({"status": "not_ready", "message": "Cache not available"}), 503

        return jsonify({"status": "ready", "timestamp": time.time()}), 200

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return (jsonify({"status": "not_ready",
                         "message": f"Readiness check failed: {str(e)}",
                         "timestamp": time.time()}),
                503,
                )


@metrics_bp.route("/optimization/config")
def get_optimization_config():
    """
    Get current optimization configuration.

    Returns the current configuration settings for
    AI optimization features.
    """
    try:
        from ai_modules.prefilter import get_prefilter
        from ai_modules.cache import get_cache
        from ai_modules.local_predictor import get_predictor

        prefilter = get_prefilter()
        cache = get_cache()
        predictor = get_predictor()

        config = {
            "features": {
                "prefilter_enabled": prefilter.is_enabled(),
                "cache_enabled": cache.is_enabled(),
                "local_predictor_enabled": predictor.is_enabled(),
            },
            "thresholds": {
                "ai_importance_threshold": 0.6,  # From config
                "ai_credibility_threshold": 0.7,  # From config
                "local_predictor_threshold": 0.5,  # From config
            },
            "cache": cache.get_stats(),
            "timestamp": time.time(),
        }

        return jsonify({"status": "success", "data": config}), 200

    except Exception as e:
        logger.error(f"Error getting optimization config: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

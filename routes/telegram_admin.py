"""
Admin panel for Telegram bot settings.

Provides API endpoints for managing bot configuration, rate limits, and monitoring.
"""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
import json

from telegram_bot.config import RATE_LIMITS, FEATURES
from telegram_bot.middleware.metrics_middleware import MetricsMiddleware
from telegram_bot.middleware.rate_limiter import RateLimiterMiddleware

logger = logging.getLogger("admin.telegram")

# Create blueprint
telegram_admin_bp = Blueprint("telegram_admin", __name__, url_prefix="/admin/telegram")

# Global instances for monitoring
metrics_middleware = MetricsMiddleware()
rate_limiter_middleware = RateLimiterMiddleware()


def check_admin_access():
    """Simple admin check - replace with proper auth later."""
    # For now, allow access to everyone (for testing)
    return True


@telegram_admin_bp.route("/rate-limits/update", methods=["POST"])
def update_rate_limits():
    """Update rate limits configuration."""
    if not check_admin_access():
        return jsonify({"error": "Доступ запрещен"}), 403

    try:
        data = request.get_json()

        # Validate data
        if not data or "rate_limits" not in data:
            return jsonify({"error": "Неверные данные"}), 400

        # Update rate limits
        new_limits = data["rate_limits"]

        # Validate each limit
        for limit_name, limit_config in new_limits.items():
            if not isinstance(limit_config, dict):
                return jsonify({"error": f"Неверная конфигурация для {limit_name}"}), 400

            if "limit" not in limit_config or "window" not in limit_config:
                return jsonify({"error": f"Отсутствуют обязательные поля для {limit_name}"}), 400

            if not isinstance(limit_config["limit"], int) or limit_config["limit"] <= 0:
                return jsonify({"error": f"Неверный лимит для {limit_name}"}), 400

            if not isinstance(limit_config["window"], int) or limit_config["window"] <= 0:
                return jsonify({"error": f"Неверное окно для {limit_name}"}), 400

        # Update global configuration
        RATE_LIMITS.update(new_limits)

        # Update rate limiter middleware
        rate_limiter_middleware.rate_limits.update(new_limits)

        # Save to JSON config file
        try:
            import os
            import json

            config_path = os.path.join(os.path.dirname(__file__), "..", "telegram_bot", "runtime_config.json")

            # Read current config file
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Update rate limits in config
            config_data["rate_limits"].update(new_limits)

            # Write back to file
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.warning(f"Could not save config to file: {e}")
            # Continue anyway - at least runtime config is updated

        # Log the change
        logger.info(
            json.dumps(
                {
                    "event": "rate_limits_updated",
                    "admin_user": "admin",  # Replace with actual user
                    "new_limits": new_limits,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )

        return jsonify({"success": True, "message": "Лимиты успешно обновлены", "updated_limits": new_limits})

    except Exception as e:
        logger.error(f"Error updating rate limits: {e}")
        return jsonify({"error": "Ошибка при обновлении лимитов"}), 500


# HTML routes removed - using React frontend instead


@telegram_admin_bp.route("/metrics/reset", methods=["POST"])
def reset_metrics():
    """Reset bot metrics."""
    if not check_admin_access():
        return jsonify({"error": "Доступ запрещен"}), 403

    try:
        metrics_middleware.reset_metrics()

        logger.info(
            json.dumps(
                {
                    "event": "metrics_reset",
                    "admin_user": "admin",  # Replace with actual user
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )

        return jsonify({"success": True, "message": "Метрики сброшены"})

    except Exception as e:
        logger.error(f"Error resetting metrics: {e}")
        return jsonify({"error": "Ошибка при сбросе метрик"}), 500


# HTML routes removed - using React frontend instead


@telegram_admin_bp.route("/reload-config", methods=["POST"])
def reload_config():
    """Reload bot configuration without restart."""
    if not check_admin_access():
        return jsonify({"error": "Доступ запрещен"}), 403

    try:
        # Reload configuration from JSON file
        from telegram_bot.config import load_runtime_config

        # Get fresh config
        new_config = load_runtime_config()

        # Update global variables
        RATE_LIMITS.clear()
        RATE_LIMITS.update(new_config["rate_limits"])

        FEATURES.clear()
        FEATURES.update(new_config["features"])

        # Update rate limiter middleware
        rate_limiter_middleware.rate_limits.update(new_config["rate_limits"])

        logger.info(
            json.dumps(
                {
                    "event": "config_reloaded",
                    "admin_user": "admin",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )

        return jsonify({"success": True, "message": "Конфигурация перезагружена"})

    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        return jsonify({"error": "Ошибка при перезагрузке конфигурации"}), 500


@telegram_admin_bp.route("/features/toggle", methods=["POST"])
def toggle_feature():
    """Toggle bot feature."""
    if not check_admin_access():
        return jsonify({"error": "Доступ запрещен"}), 403

    try:
        data = request.get_json()
        feature_name = data.get("feature")
        enabled = data.get("enabled", False)

        if feature_name not in FEATURES:
            return jsonify({"error": "Неизвестная функция"}), 400

        # Update feature
        FEATURES[feature_name]["enabled"] = enabled

        # Save to JSON config file
        try:
            import os
            import json

            config_path = os.path.join(os.path.dirname(__file__), "..", "telegram_bot", "runtime_config.json")

            # Read current config file
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Update feature in config
            config_data["features"][feature_name]["enabled"] = enabled

            # Write back to file
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.warning(f"Could not save feature config to file: {e}")
            # Continue anyway - at least runtime config is updated

        logger.info(
            json.dumps(
                {
                    "event": "feature_toggled",
                    "admin_user": "admin",  # Replace with actual user
                    "feature": feature_name,
                    "enabled": enabled,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )

        return jsonify(
            {
                "success": True,
                "message": f'Функция {FEATURES[feature_name]["name"]} {"включена" if enabled else "отключена"}',
            }
        )

    except Exception as e:
        logger.error(f"Error toggling feature: {e}")
        return jsonify({"error": "Ошибка при изменении функции"}), 500


@telegram_admin_bp.route("/api/status")
def api_status():
    """API endpoint for bot status."""
    if not check_admin_access():
        return jsonify({"error": "Доступ запрещен"}), 403

    try:
        # Get current status
        status = {
            "bot_running": True,  # This would check actual bot status
            "metrics": metrics_middleware.get_metrics_summary(),
            "rate_limits": RATE_LIMITS,
            "features": {key: value["enabled"] for key, value in FEATURES.items()},
            "features_details": FEATURES,
            "timestamp": datetime.utcnow().isoformat(),
        }

        return jsonify(status)

    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        return jsonify({"error": "Ошибка при получении статуса"}), 500


@telegram_admin_bp.route("/api/user-stats/<int:user_id>")
def api_user_stats(user_id):
    """Get user statistics."""
    if not check_admin_access():
        return jsonify({"error": "Доступ запрещен"}), 403

    try:
        user_metrics = metrics_middleware.get_user_metrics(user_id)
        rate_limit_stats = rate_limiter_middleware.get_user_stats(user_id)

        return jsonify(
            {
                "user_id": user_id,
                "metrics": user_metrics,
                "rate_limits": rate_limit_stats,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return jsonify({"error": "Ошибка при получении статистики пользователя"}), 500

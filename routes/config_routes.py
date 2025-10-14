"""
API endpoints для получения конфигурации приложения.
Публичные endpoints без аутентификации.
"""

import logging
from flask import Blueprint, jsonify

from config.core.cloudflare import (
    CLOUDFLARE_TUNNEL_URL,
    get_webapp_url,
    get_api_url,
    get_vite_allowed_hosts,
)

logger = logging.getLogger(__name__)

config_bp = Blueprint("config", __name__, url_prefix="/api/config")


@config_bp.route("/urls", methods=["GET"])
def get_urls():
    """
    Возвращает актуальные URL для фронтенда.

    Публичный endpoint - не требует аутентификации.
    Используется фронтендом для динамического получения конфигурации.

    Returns:
        JSON с URL конфигурацией
    """
    try:
        config_data = {
            "status": "success",
            "data": {
                "tunnel_url": CLOUDFLARE_TUNNEL_URL,
                "webapp_url": get_webapp_url(),
                "api_url": get_api_url(),
                "allowed_hosts": get_vite_allowed_hosts(),
            },
        }

        logger.debug(f"Config URLs requested: {config_data}")
        return jsonify(config_data)

    except Exception as e:
        logger.error(f"Error getting config URLs: {e}")
        return jsonify({"status": "error", "message": "Failed to get configuration"}), 500

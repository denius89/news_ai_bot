"""
Конфигурация Cloudflare Tunnel.
Единое место для всех настроек Cloudflare Tunnel.
"""

import os
from typing import Dict, List

# Загружаем переменные окружения
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent.parent / "config_files" / "environment" / ".env")

# ---- CLOUDFLARE TUNNEL CONFIGURATION ----

# Основной URL Cloudflare Tunnel
CLOUDFLARE_TUNNEL_URL = os.getenv("CLOUDFLARE_TUNNEL_URL", "https://scoring-side-receives-hudson.trycloudflare.com")

# Локальный URL для туннеля
CLOUDFLARE_LOCAL_URL = os.getenv("CLOUDFLARE_LOCAL_URL", "http://localhost:8001")

# Команда для запуска Cloudflare Tunnel
CLOUDFLARE_TUNNEL_COMMAND = os.getenv("CLOUDFLARE_TUNNEL_COMMAND", f"cloudflared tunnel --url {CLOUDFLARE_LOCAL_URL}")

# ---- URLS FOR DIFFERENT SERVICES ----


def get_webapp_url() -> str:
    """Возвращает URL для WebApp."""
    return f"{CLOUDFLARE_TUNNEL_URL}/webapp"


def get_api_url() -> str:
    """Возвращает базовый URL для API."""
    return CLOUDFLARE_TUNNEL_URL


def get_health_url() -> str:
    """Возвращает URL для health check."""
    return f"{CLOUDFLARE_TUNNEL_URL}/api/health"


def get_dashboard_url() -> str:
    """Возвращает URL для dashboard."""
    return f"{CLOUDFLARE_TUNNEL_URL}/webapp"


# ---- VITE CONFIGURATION ----


def get_vite_allowed_hosts() -> List[str]:
    """Возвращает список разрешенных хостов для Vite."""
    # Извлекаем домен из URL
    domain = CLOUDFLARE_TUNNEL_URL.replace("https://", "").replace("http://", "")

    return ["localhost", "127.0.0.1", domain, ".trycloudflare.com"]


# ---- DEPLOYMENT CONFIGURATION ----


def get_deployment_info() -> Dict[str, str]:
    """Возвращает информацию для развертывания."""
    return {
        "tunnel_url": CLOUDFLARE_TUNNEL_URL,
        "local_url": CLOUDFLARE_LOCAL_URL,
        "webapp_url": get_webapp_url(),
        "api_url": get_api_url(),
        "health_url": get_health_url(),
        "dashboard_url": get_dashboard_url(),
        "tunnel_command": CLOUDFLARE_TUNNEL_COMMAND,
    }


# ---- VALIDATION ----


def validate_cloudflare_config() -> bool:
    """Проверяет корректность конфигурации Cloudflare."""
    try:
        # Проверяем, что URL содержит trycloudflare.com
        if "trycloudflare.com" not in CLOUDFLARE_TUNNEL_URL:
            return False

        # Проверяем, что локальный URL корректен
        if not CLOUDFLARE_LOCAL_URL.startswith("http://localhost:"):
            return False

        return True
    except Exception:
        return False


# ---- BACKWARD COMPATIBILITY ----

# Для обратной совместимости с существующим кодом
WEBAPP_URL = CLOUDFLARE_TUNNEL_URL

# Экспорт основных переменных
__all__ = [
    "CLOUDFLARE_TUNNEL_URL",
    "CLOUDFLARE_LOCAL_URL",
    "CLOUDFLARE_TUNNEL_COMMAND",
    "WEBAPP_URL",
    "get_webapp_url",
    "get_api_url",
    "get_health_url",
    "get_dashboard_url",
    "get_vite_allowed_hosts",
    "get_deployment_info",
    "validate_cloudflare_config",
]

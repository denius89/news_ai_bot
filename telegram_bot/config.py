"""
Configuration constants for Telegram bot.

Simplified configuration for minimalist bot (gateway + notifications).
"""

import json
from pathlib import Path


def load_runtime_config():
    """Load configuration from runtime_config.json file."""
    config_path = Path(__file__).parent / "runtime_config.json"

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load runtime config: {e}")

    # Fallback to default configuration
    return {
        "rate_limits": {
            "commands": {"limit": 5, "window": 60, "description": "General command rate limit"},
        },
        "features": {
            "notifications": {
                "enabled": True,
                "name": "Уведомления",
                "description": "Push-уведомления о важных событиях",
                "details": "Автоматические уведомления при появлении критических новостей",
            },
        },
    }


# Load configuration
_runtime_config = load_runtime_config()

# Rate limiting configuration
RATE_LIMITS = _runtime_config["rate_limits"]

# Feature flags
FEATURES = _runtime_config["features"]

# Bot commands configuration - убираем все команды
BOT_COMMANDS = []

# Message limits
MESSAGE_LIMITS = {
    "max_length": 4000,  # Telegram message limit (safe)
}

# Timezone and locale settings
DEFAULT_TIMEZONE = "Europe/Kyiv"
DEFAULT_LOCALE = "ru"

# Logging settings
LOGGING = {
    "log_user_actions": True,
    "log_performance": True,
    "log_errors": True,
    "structured_logging": True,
}

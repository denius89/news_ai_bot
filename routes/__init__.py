"""
Routes module for Telegram bot.

This module imports and configures all bot routers.
"""

from . import subscriptions

# List of all routers to be included in the bot
routers = [
    subscriptions.router,
]

__all__ = ["routers"]

"""
Notifications module for PulseAI.

This module provides notification delivery via Telegram and WebApp.
"""

from notifications.telegram_sender import TelegramSender, get_telegram_sender

__all__ = ["TelegramSender", "get_telegram_sender"]

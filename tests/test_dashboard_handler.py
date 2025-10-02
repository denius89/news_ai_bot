"""
Tests for dashboard handler.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, User, Chat, WebAppInfo

from telegram_bot.handlers.dashboard import open_dashboard


@pytest.mark.asyncio
async def test_dashboard_command():
    """Test /dashboard command handler."""
    # Create mock message
    user = User(id=12345, is_bot=False, first_name="Test", username="testuser")
    chat = Chat(id=12345, type="private")
    message = Message(
        message_id=1,
        date=None,
        chat=chat,
        from_user=user,
        content_type="text",
        options={}
    )
    
    # Mock the answer method
    message.answer = AsyncMock()
    
    # Call the handler
    await open_dashboard(message)
    
    # Verify the response
    message.answer.assert_called_once()
    call_args = message.answer.call_args
    
    # Check message text
    assert "PulseAI Dashboard" in call_args[0][0]
    assert "Откройте ваш персональный дашборд" in call_args[0][0]
    
    # Check reply_markup exists
    assert "reply_markup" in call_args[1]
    keyboard = call_args[1]["reply_markup"]
    
    # Check keyboard structure
    assert keyboard.resize_keyboard is True
    assert keyboard.one_time_keyboard is False
    assert len(keyboard.keyboard) == 1
    assert len(keyboard.keyboard[0]) == 1
    
    # Check button
    button = keyboard.keyboard[0][0]
    assert button.text == "📱 Открыть Dashboard"
    assert isinstance(button.web_app, WebAppInfo)
    assert "webapp" in button.web_app.url
    
    # Check parse mode
    assert call_args[1]["parse_mode"] == "HTML"


@pytest.mark.unit
def test_dashboard_handler_import():
    """Test that dashboard handler can be imported."""
    from telegram_bot.handlers.dashboard import router
    assert router is not None

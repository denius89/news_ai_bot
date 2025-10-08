"""
Tests for progress animation utilities.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import types

from utils.system.progress_animation import (
    ProgressAnimation,
    show_generation_progress,
    build_digest_actions_keyboard,
)


@pytest.fixture
def mock_callback_query():
    """Create a mock callback query for testing."""
    query = MagicMock(spec=types.CallbackQuery)
    query.from_user = MagicMock()
    query.from_user.username = "testuser"
    query.from_user.first_name = "Test"

    query.message = AsyncMock()
    query.message.edit_text = AsyncMock()

    return query


@pytest.mark.asyncio
async def test_progress_animation_basic(mock_callback_query):
    """Test basic progress animation functionality."""
    steps = [
        "🧠 Анализируем новости...",
        "📊 Считаем важность и достоверность...",
        "✨ Формируем резюме...",
    ]

    animation = ProgressAnimation(mock_callback_query)

    # Mock the sleep to speed up test
    with patch("asyncio.sleep", new_callable=AsyncMock):
        await animation.show_generation_progress(steps, progress_bar=True, interval=0.1)

    # Verify that edit_text was called for each step
    assert mock_callback_query.message.edit_text.call_count == len(steps)

    # Check that progress bar was included
    calls = mock_callback_query.message.edit_text.call_args_list
    for i, call in enumerate(calls):
        text = call[0][0]  # First positional argument
        assert steps[i] in text
        if i == 0:  # First call should have progress bar
            assert "▰" in text or "▱" in text


@pytest.mark.asyncio
async def test_progress_animation_without_bar(mock_callback_query):
    """Test progress animation without progress bar."""
    steps = ["Step 1", "Step 2"]

    animation = ProgressAnimation(mock_callback_query)

    with patch("asyncio.sleep", new_callable=AsyncMock):
        await animation.show_generation_progress(steps, progress_bar=False, interval=0.1)

    # Check that progress bar was not included
    calls = mock_callback_query.message.edit_text.call_args_list
    for call in calls:
        text = call[0][0]
        assert "▰" not in text and "▱" not in text


@pytest.mark.asyncio
async def test_progress_animation_stop(mock_callback_query):
    """Test stopping progress animation."""
    steps = ["Step 1", "Step 2", "Step 3"]

    animation = ProgressAnimation(mock_callback_query)

    # Mock sleep to be instant and track calls
    sleep_calls = 0

    async def mock_sleep(delay):
        nonlocal sleep_calls
        sleep_calls += 1
        if sleep_calls == 1:  # Stop after first sleep
            animation.stop()
        return

    # Start animation with mocked sleep
    with patch("asyncio.sleep", side_effect=mock_sleep):
        await animation.show_generation_progress(steps, interval=0.1)

    # Should have called edit_text for first step only
    assert mock_callback_query.message.edit_text.call_count == 1


def test_progress_bar_generation():
    """Test progress bar generation."""
    animation = ProgressAnimation(MagicMock())

    # Test different progress levels
    bar1 = animation._generate_progress_bar(1, 5)
    assert "▰▰▱▱▱▱▱▱▱▱" in bar1  # 1/5 = 20% = 2 bars filled

    bar2 = animation._generate_progress_bar(5, 5)
    assert "▰▰▰▰▰▰▰▰▰▰" in bar2  # 5/5 = 100% = all bars filled

    bar3 = animation._generate_progress_bar(3, 6)
    assert "▰▰▰▰▰▱▱▱▱▱" in bar3  # 3/6 = 50% = 5 bars filled

    # Test edge cases
    bar4 = animation._generate_progress_bar(0, 10)
    assert "▱▱▱▱▱▱▱▱▱▱" in bar4  # 0/10 = 0% = no bars filled

    bar5 = animation._generate_progress_bar(10, 10)
    assert "▰▰▰▰▰▰▰▰▰▰" in bar5  # 10/10 = 100% = all bars filled


def test_build_progress_text():
    """Test progress text building."""
    animation = ProgressAnimation(MagicMock())

    # Test with progress bar (current=2, total=5 -> (2+1)/5*100 = 60%)
    text = animation._build_progress_text("Test step", 2, 5, show_bar=True)
    assert "Test step" in text
    assert "60%" in text
    assert "▰" in text or "▱" in text

    # Test without progress bar
    text = animation._build_progress_text("Test step", 2, 5, show_bar=False)
    assert "Test step" in text
    assert "60%" not in text
    assert "▰" not in text


@pytest.mark.asyncio
async def test_show_generation_progress_convenience(mock_callback_query):
    """Test the convenience function."""
    with patch("asyncio.sleep", new_callable=AsyncMock):
        animation = await show_generation_progress(mock_callback_query, interval=0.1)

        # Wait a bit for the background task to start
        await asyncio.sleep(0.1)

    assert isinstance(animation, ProgressAnimation)
    # The animation runs in background, so edit_text might not be called yet
    # Just verify the animation object is created correctly


def test_build_digest_actions_keyboard():
    """Test digest actions keyboard building."""
    # Test with category
    kb = build_digest_actions_keyboard("testuser", "crypto")

    # Should have subscribe button for category
    assert len(kb.inline_keyboard) >= 2  # Subscribe + auto-digest + back

    # Test without category
    kb = build_digest_actions_keyboard("testuser", None)

    # Should not have category-specific subscribe button
    assert len(kb.inline_keyboard) >= 2  # Auto-digest + back


@pytest.mark.asyncio
async def test_telegram_bad_request_handling(mock_callback_query):
    """Test handling of TelegramBadRequest errors."""
    from aiogram.exceptions import TelegramBadRequest

    # Mock edit_text to raise TelegramBadRequest
    mock_callback_query.message.edit_text.side_effect = TelegramBadRequest(
        message="message is not modified", method="editMessageText"
    )

    steps = ["Step 1", "Step 2"]
    animation = ProgressAnimation(mock_callback_query)

    # Should not raise exception
    with patch("asyncio.sleep", new_callable=AsyncMock):
        await animation.show_generation_progress(steps, interval=0.1)

    # Should have attempted to call edit_text
    assert mock_callback_query.message.edit_text.called


@pytest.mark.asyncio
async def test_progress_animation_error_handling(mock_callback_query):
    """Test error handling in progress animation."""
    # Mock edit_text to raise generic exception
    mock_callback_query.message.edit_text.side_effect = Exception("Test error")

    steps = ["Step 1"]
    animation = ProgressAnimation(mock_callback_query)

    # Should not raise exception
    with patch("asyncio.sleep", new_callable=AsyncMock):
        await animation.show_generation_progress(steps, interval=0.1)

    # Should have attempted to call edit_text
    assert mock_callback_query.message.edit_text.called

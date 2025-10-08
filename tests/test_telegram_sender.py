"""
Unit tests for Telegram sender utility.

Tests the TelegramSender class and global functions with mocked aiogram Bot.
"""

import pytest
from unittest.mock import AsyncMock, patch

from utils.telegram_sender import TelegramSender, send_message, send_digest


class TestTelegramSender:
    """Test cases for TelegramSender class."""

    def test_init_with_token(self):
        """Test initialization with provided token."""
        sender = TelegramSender("123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        assert sender.bot_token == "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        assert sender.bot is not None

    @patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"})
    def test_init_with_env_token(self):
        """Test initialization with token from environment."""
        sender = TelegramSender()
        assert sender.bot_token == "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"

    @patch.dict("os.environ", {}, clear=True)
    def test_init_no_token(self):
        """Test initialization without token raises ValueError."""
        with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN не найден"):
            TelegramSender()

    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Test successful message sending."""
        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock()
            mock_bot_class.return_value = mock_bot

            sender = TelegramSender("123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
            result = await sender.send_message(123456, "Test message")

            assert result is True
            mock_bot.send_message.assert_called_once_with(
                chat_id=123456,
                text="Test message",
                parse_mode="HTML",
                disable_web_page_preview=True,
                disable_notification=False,
            )

    @pytest.mark.asyncio
    async def test_send_message_too_long(self):
        """Test message sending with text too long."""
        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock()
            mock_bot_class.return_value = mock_bot

            sender = TelegramSender("123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
            long_text = "x" * 5000  # Longer than 4000 chars
            result = await sender.send_message(123456, long_text)

            assert result is True
            # Check that message was truncated
            call_args = mock_bot.send_message.call_args
            assert len(call_args[1]["text"]) <= 4000
            assert "... (сообщение обрезано)" in call_args[1]["text"]

    @pytest.mark.asyncio
    async def test_send_message_telegram_forbidden(self):
        """Test handling of TelegramForbiddenError (user blocked bot)."""
        from aiogram.exceptions import TelegramForbiddenError

        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock(
                side_effect=TelegramForbiddenError(
                    "Forbidden", "Forbidden"))
            mock_bot_class.return_value = mock_bot

            sender = TelegramSender("123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
            result = await sender.send_message(123456, "Test message")

            assert result is False

    @pytest.mark.asyncio
    async def test_send_message_telegram_bad_request(self):
        """Test handling of TelegramBadRequest."""
        from aiogram.exceptions import TelegramBadRequest

        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock(
                side_effect=TelegramBadRequest(
                    "Bad Request", "Bad Request"))
            mock_bot_class.return_value = mock_bot

            sender = TelegramSender("123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
            result = await sender.send_message(123456, "Test message")

            assert result is False

    @pytest.mark.asyncio
    async def test_send_message_retry_after(self):
        """Test handling of TelegramRetryAfter with retry."""
        from aiogram.exceptions import TelegramRetryAfter

        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()

            # First call raises RetryAfter, second succeeds
            mock_bot.send_message = AsyncMock(
                side_effect=[
                    TelegramRetryAfter(retry_after=1, message="Retry after", method="sendMessage"),
                    None,
                ]  # Success on retry
            )
            mock_bot_class.return_value = mock_bot

            sender = TelegramSender("123456789:ABCdefGHIjklMNOpqrsTUVwxyz")

            with patch("asyncio.sleep") as mock_sleep:
                result = await sender.send_message(123456, "Test message")

                assert result is True
                assert mock_sleep.called
                mock_sleep.assert_called_with(1)
                # Should have been called twice (original + retry)
                assert mock_bot.send_message.call_count == 2

    @pytest.mark.asyncio
    async def test_send_message_general_exception(self):
        """Test handling of general exceptions."""
        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock(side_effect=Exception("General error"))
            mock_bot_class.return_value = mock_bot

            sender = TelegramSender("123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
            result = await sender.send_message(123456, "Test message")

            assert result is False

    @pytest.mark.asyncio
    async def test_send_digest(self):
        """Test send_digest method."""
        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock()
            mock_bot_class.return_value = mock_bot

            sender = TelegramSender("123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
            result = await sender.send_digest(123456, "Digest content", "Custom Title")

            assert result is True
            call_args = mock_bot.send_message.call_args
            assert "Custom Title" in call_args[1]["text"]
            assert "Digest content" in call_args[1]["text"]

    @pytest.mark.asyncio
    async def test_send_error_message(self):
        """Test send_error_message method."""
        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock()
            mock_bot_class.return_value = mock_bot

            sender = TelegramSender("123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
            result = await sender.send_error_message(123456, "Custom error")

            assert result is True
            mock_bot.send_message.assert_called_once_with(
                chat_id=123456,
                text="Custom error",
                parse_mode="HTML",
                disable_web_page_preview=True,
                disable_notification=False,
            )

    @pytest.mark.asyncio
    async def test_send_help_message(self):
        """Test send_help_message method."""
        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock()
            mock_bot_class.return_value = mock_bot

            sender = TelegramSender("123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
            result = await sender.send_help_message(123456, "Help content")

            assert result is True
            mock_bot.send_message.assert_called_once_with(
                chat_id=123456,
                text="Help content",
                parse_mode="HTML",
                disable_web_page_preview=True,
                disable_notification=False,
            )

    @pytest.mark.asyncio
    async def test_close(self):
        """Test close method."""
        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.session = AsyncMock()
            mock_bot.session.close = AsyncMock()
            mock_bot_class.return_value = mock_bot

            sender = TelegramSender("123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
            await sender.close()

            mock_bot.session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.session = AsyncMock()
            mock_bot.session.close = AsyncMock()
            mock_bot_class.return_value = mock_bot

            async with TelegramSender("123456789:ABCdefGHIjklMNOpqrsTUVwxyz") as sender:
                assert sender is not None
                assert sender.bot_token == "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"

            # Should close session when exiting context
            mock_bot.session.close.assert_called_once()


class TestGlobalFunctions:
    """Test cases for global convenience functions."""

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "test-token"})
    async def test_send_message_global(self):
        """Test global send_message function."""
        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock()
            mock_bot.session = AsyncMock()
            mock_bot.session.close = AsyncMock()
            mock_bot_class.return_value = mock_bot

            result = await send_message(123456, "Test message")

            assert result is True
            mock_bot.send_message.assert_called_once()
            mock_bot.session.close.assert_called_once()

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "test-token"})
    async def test_send_digest_global(self):
        """Test global send_digest function."""
        with patch("utils.telegram_sender.Bot") as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock()
            mock_bot.session = AsyncMock()
            mock_bot.session.close = AsyncMock()
            mock_bot_class.return_value = mock_bot

            result = await send_digest(123456, "Digest content", "Custom Title")

            assert result is True
            call_args = mock_bot.send_message.call_args
            assert "Custom Title" in call_args[1]["text"]
            assert "Digest content" in call_args[1]["text"]
            mock_bot.session.close.assert_called_once()

    @pytest.mark.asyncio
    @patch.dict("os.environ", {}, clear=True)
    async def test_global_function_no_token(self):
        """Test global functions with no token."""
        result = await send_message(123456, "Test message")
        assert result is False

        result = await send_digest(123456, "Digest content")
        assert result is False

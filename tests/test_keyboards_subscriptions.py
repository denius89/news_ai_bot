"""
Unit tests for subscription and notification keyboards.

Tests the keyboard structure, button text, and callback data
for subscription and notification management.
"""

import pytest
from unittest.mock import patch

from telegram_bot.keyboards import (
    subscriptions_inline_keyboard,
    notifications_inline_keyboard,
    categories_inline_keyboard,
    main_inline_keyboard,
)


class TestSubscriptionKeyboards:
    """Test cases for subscription keyboards."""

    @pytest.mark.unit
    def test_subscriptions_keyboard_structure(self):
        """Test that subscriptions keyboard has correct structure."""
        keyboard = subscriptions_inline_keyboard()

        # Check keyboard type
        assert hasattr(keyboard, "inline_keyboard")
        assert isinstance(keyboard.inline_keyboard, list)

        # Should have 4 rows: 3 action buttons + 1 back button
        assert len(keyboard.inline_keyboard) == 4

    @pytest.mark.unit
    def test_subscriptions_keyboard_buttons(self):
        """Test that subscriptions keyboard has correct buttons."""
        keyboard = subscriptions_inline_keyboard()

        # Flatten all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            for button in row:
                all_buttons.append(button)

        # Check button texts
        button_texts = [button.text for button in all_buttons]

        assert "📋 Мои подписки" in button_texts
        assert "➕ Подписаться" in button_texts
        assert "➖ Отписаться" in button_texts
        assert "⬅️ Назад" in button_texts

    @pytest.mark.unit
    def test_subscriptions_keyboard_callback_data(self):
        """Test that subscriptions keyboard has correct callback data."""
        keyboard = subscriptions_inline_keyboard()

        # Flatten all buttons and get callback data
        callback_data_list = []
        for row in keyboard.inline_keyboard:
            for button in row:
                callback_data_list.append(button.callback_data)

        expected_callbacks = ["my_subs", "subscribe_menu", "unsubscribe_menu", "back"]

        for expected in expected_callbacks:
            assert expected in callback_data_list, f"Missing callback: {expected}"

    @pytest.mark.unit
    def test_notifications_keyboard_structure(self):
        """Test that notifications keyboard has correct structure."""
        keyboard = notifications_inline_keyboard()

        # Check keyboard type
        assert hasattr(keyboard, "inline_keyboard")
        assert isinstance(keyboard.inline_keyboard, list)

        # Should have 4 rows: 3 action buttons + 1 back button
        assert len(keyboard.inline_keyboard) == 4

    @pytest.mark.unit
    def test_notifications_keyboard_buttons(self):
        """Test that notifications keyboard has correct buttons."""
        keyboard = notifications_inline_keyboard()

        # Flatten all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            for button in row:
                all_buttons.append(button)

        # Check button texts
        button_texts = [button.text for button in all_buttons]

        assert "🔔 Мои уведомления" in button_texts
        assert "✅ Включить дайджест" in button_texts
        assert "❌ Выключить дайджест" in button_texts
        assert "⬅️ Назад" in button_texts

    @pytest.mark.unit
    def test_notifications_keyboard_callback_data(self):
        """Test that notifications keyboard has correct callback data."""
        keyboard = notifications_inline_keyboard()

        # Flatten all buttons and get callback data
        callback_data_list = []
        for row in keyboard.inline_keyboard:
            for button in row:
                callback_data_list.append(button.callback_data)

        expected_callbacks = ["my_notifications", "notify_on_digest", "notify_off_digest", "back"]

        for expected in expected_callbacks:
            assert expected in callback_data_list, f"Missing callback: {expected}"

    @pytest.mark.unit
    @patch(
        "digests.configs.CATEGORIES",
        {"crypto": "Криптовалюты", "economy": "Экономика", "tech": "Технологии"},
    )
    def test_categories_keyboard_subscribe(self):
        """Test categories keyboard for subscribe action."""
        keyboard = categories_inline_keyboard("subscribe")

        # Check keyboard structure
        assert hasattr(keyboard, "inline_keyboard")
        assert len(keyboard.inline_keyboard) == 6  # 5 categories + back button

        # Check callback data format
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data != "back":
                    assert button.callback_data.startswith("subscribe:")
                    category = button.callback_data.split(":", 1)[1]
                    assert category in ["crypto", "sports", "markets", "tech", "world"]

    @pytest.mark.unit
    @patch(
        "digests.configs.CATEGORIES",
        {"crypto": "Криптовалюты", "economy": "Экономика", "tech": "Технологии"},
    )
    def test_categories_keyboard_unsubscribe(self):
        """Test categories keyboard for unsubscribe action."""
        keyboard = categories_inline_keyboard("unsubscribe")

        # Check keyboard structure
        assert hasattr(keyboard, "inline_keyboard")
        assert len(keyboard.inline_keyboard) == 6  # 5 categories + back button

        # Check callback data format
        for row in keyboard.inline_keyboard:
            for button in row:
                if button.callback_data != "back":
                    assert button.callback_data.startswith("unsubscribe:")
                    category = button.callback_data.split(":", 1)[1]
                    assert category in ["crypto", "sports", "markets", "tech", "world"]

    @pytest.mark.unit
    def test_main_keyboard_has_subscription_buttons(self):
        """Test that main keyboard includes news and notification buttons."""
        keyboard = main_inline_keyboard()

        # Flatten all buttons
        all_buttons = []
        for row in keyboard.inline_keyboard:
            for button in row:
                all_buttons.append(button)

        # Check button texts
        button_texts = [button.text for button in all_buttons]

        assert "📰 Новости" in button_texts
        assert "🔔 Уведомления" in button_texts

    @pytest.mark.unit
    def test_main_keyboard_callback_data(self):
        """Test that main keyboard has correct callback data for buttons."""
        keyboard = main_inline_keyboard()

        # Flatten all buttons and get callback data
        callback_data_list = []
        for row in keyboard.inline_keyboard:
            for button in row:
                callback_data_list.append(button.callback_data)

        assert "digest:all" in callback_data_list
        assert "notifications" in callback_data_list

    @pytest.mark.unit
    def test_keyboard_button_count(self):
        """Test that keyboards have expected number of buttons."""
        # Main keyboard should have at least 5 buttons (original 3 + 2 new)
        main_kb = main_inline_keyboard()
        main_buttons = sum(len(row) for row in main_kb.inline_keyboard)
        assert main_buttons >= 5

        # Subscriptions keyboard should have 4 buttons
        subs_kb = subscriptions_inline_keyboard()
        subs_buttons = sum(len(row) for row in subs_kb.inline_keyboard)
        assert subs_buttons == 4

        # Notifications keyboard should have 4 buttons
        notif_kb = notifications_inline_keyboard()
        notif_buttons = sum(len(row) for row in notif_kb.inline_keyboard)
        assert notif_buttons == 4

    @pytest.mark.unit
    def test_keyboard_button_emojis(self):
        """Test that keyboards use appropriate emojis."""
        subs_kb = subscriptions_inline_keyboard()
        notif_kb = notifications_inline_keyboard()

        # Check subscription emojis
        subs_texts = []
        for row in subs_kb.inline_keyboard:
            for button in row:
                subs_texts.append(button.text)

        assert any("📋" in text for text in subs_texts)  # Мои подписки
        assert any("➕" in text for text in subs_texts)  # Подписаться
        assert any("➖" in text for text in subs_texts)  # Отписаться

        # Check notification emojis
        notif_texts = []
        for row in notif_kb.inline_keyboard:
            for button in row:
                notif_texts.append(button.text)

        assert any("🔔" in text for text in notif_texts)  # Мои уведомления
        assert any("✅" in text for text in notif_texts)  # Включить
        assert any("❌" in text for text in notif_texts)  # Выключить

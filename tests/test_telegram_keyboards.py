"""
Test Telegram keyboards functionality.

This test checks that all keyboard functions work correctly
without actually running the bot.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_keyboard_imports():
    """Test that all keyboard functions can be imported."""
    try:
        from telegram_bot.keyboards import (
            start_inline_keyboard,
            main_inline_keyboard,
            back_inline_keyboard,
            subscriptions_inline_keyboard,
            notifications_inline_keyboard,
            categories_inline_keyboard,
        )
        
        # Check that all functions exist
        functions = [
            start_inline_keyboard,
            main_inline_keyboard,
            back_inline_keyboard,
            subscriptions_inline_keyboard,
            notifications_inline_keyboard,
            categories_inline_keyboard,
        ]
        
        for func in functions:
            assert callable(func), f"Function {func.__name__} is not callable"
        
        print("✅ Все функции клавиатур импортированы успешно")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта клавиатур: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


def test_keyboard_structure():
    """Test that keyboards have correct structure."""
    try:
        from telegram_bot.keyboards import (
            main_inline_keyboard,
            subscriptions_inline_keyboard,
            notifications_inline_keyboard,
            categories_inline_keyboard,
        )
        
        # Test main keyboard
        main_kb = main_inline_keyboard()
        assert hasattr(main_kb, 'inline_keyboard')
        assert len(main_kb.inline_keyboard) >= 5  # Should have at least 5 buttons now
        
        # Check for new buttons
        all_buttons = []
        for row in main_kb.inline_keyboard:
            for button in row:
                all_buttons.append(button.text)
        
        assert "📋 Подписки" in all_buttons, "Subscriptions button not found in main keyboard"
        assert "🔔 Уведомления" in all_buttons, "Notifications button not found in main keyboard"
        
        # Test subscriptions keyboard
        subs_kb = subscriptions_inline_keyboard()
        assert hasattr(subs_kb, 'inline_keyboard')
        assert len(subs_kb.inline_keyboard) == 4  # 3 action buttons + back
        
        # Test notifications keyboard
        notif_kb = notifications_inline_keyboard()
        assert hasattr(notif_kb, 'inline_keyboard')
        assert len(notif_kb.inline_keyboard) == 4  # 3 action buttons + back
        
        # Test categories keyboard
        cat_kb = categories_inline_keyboard("subscribe")
        assert hasattr(cat_kb, 'inline_keyboard')
        assert len(cat_kb.inline_keyboard) > 1  # Categories + back button
        
        print("✅ Структура клавиатур корректна")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка структуры клавиатур: {e}")
        return False


def test_callback_data():
    """Test that callback data is properly formatted."""
    try:
        from telegram_bot.keyboards import (
            main_inline_keyboard,
            subscriptions_inline_keyboard,
            notifications_inline_keyboard,
            categories_inline_keyboard,
        )
        
        # Test main keyboard callback data
        main_kb = main_inline_keyboard()
        callback_data_list = []
        for row in main_kb.inline_keyboard:
            for button in row:
                callback_data_list.append(button.callback_data)
        
        assert "subscriptions" in callback_data_list
        assert "notifications" in callback_data_list
        
        # Test subscriptions keyboard callback data
        subs_kb = subscriptions_inline_keyboard()
        subs_callbacks = []
        for row in subs_kb.inline_keyboard:
            for button in row:
                subs_callbacks.append(button.callback_data)
        
        expected_subs_callbacks = ["my_subs", "subscribe_menu", "unsubscribe_menu", "back"]
        for expected in expected_subs_callbacks:
            assert expected in subs_callbacks, f"Missing callback: {expected}"
        
        # Test notifications keyboard callback data
        notif_kb = notifications_inline_keyboard()
        notif_callbacks = []
        for row in notif_kb.inline_keyboard:
            for button in row:
                notif_callbacks.append(button.callback_data)
        
        expected_notif_callbacks = ["my_notifications", "notify_on_digest", "notify_off_digest", "back"]
        for expected in expected_notif_callbacks:
            assert expected in notif_callbacks, f"Missing callback: {expected}"
        
        print("✅ Callback data корректно настроен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка callback data: {e}")
        return False


def main():
    """Run all keyboard tests."""
    print("🧪 Тестирование Telegram клавиатур")
    print("=" * 50)
    
    tests = [
        test_keyboard_imports,
        test_keyboard_structure,
        test_callback_data,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Тест {test.__name__} упал: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("✅ Все клавиатуры настроены правильно!")
        print("\n🎯 Доступные клавиатуры:")
        print("   📋 Подписки - управление подписками на категории")
        print("   🔔 Уведомления - управление уведомлениями")
        print("   ➕ Подписаться - выбор категории для подписки")
        print("   ➖ Отписаться - выбор категории для отписки")
        print("   🔔 Мои уведомления - просмотр настроек")
        print("   ✅/❌ Включить/Выключить дайджест")
        return True
    else:
        print("❌ Некоторые тесты не прошли")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

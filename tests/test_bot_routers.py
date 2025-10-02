"""
Test that all bot routers are properly configured.

This test checks that all routers are imported and configured correctly
without actually running the bot.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_routers_import():
    """Test that all routers can be imported."""
    try:
        from telegram_bot.handlers import routers

        # Check that routers list exists and is not empty
        assert routers is not None
        assert isinstance(routers, list)
        assert len(routers) > 0

        print(f"✅ Импортировано {len(routers)} роутеров")
        return True

    except ImportError as e:
        print(f"❌ Ошибка импорта роутеров: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


def test_subscriptions_router():
    """Test that subscriptions router is properly configured."""
    try:
        # Test individual imports
        from telegram_bot.handlers import subscriptions

        # Check that router exists
        assert hasattr(subscriptions, 'router')
        assert subscriptions.router is not None

        print("✅ Subscriptions роутер найден")
        return True

    except ImportError as e:
        print(f"❌ Ошибка импорта subscriptions: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка в subscriptions: {e}")
        return False


def test_all_handlers():
    """Test that all handler modules can be imported."""
    try:
        from telegram_bot.handlers import start, digest, digest_ai, events, subscriptions

        # Check that all modules have router attribute
        modules = [start, digest, digest_ai, events, subscriptions]
        for module in modules:
            assert hasattr(module, 'router'), f"Модуль {module.__name__} не имеет router"
            assert module.router is not None, f"Router в {module.__name__} равен None"

        print("✅ Все обработчики имеют роутеры")
        return True

    except ImportError as e:
        print(f"❌ Ошибка импорта обработчиков: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка в обработчиках: {e}")
        return False


def main():
    """Run all router tests."""
    print("🧪 Тестирование конфигурации роутеров Telegram бота")
    print("=" * 50)

    tests = [
        test_routers_import,
        test_subscriptions_router,
        test_all_handlers,
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
        print("✅ Все роутеры настроены правильно!")
        print("\n🎯 Доступные команды:")
        print("   /subscribe <category> - подписаться на категорию")
        print("   /unsubscribe <category> - отписаться от категории")
        print("   /my_subs - показать мои подписки")
        print("   /notify_on <type> - включить уведомления")
        print("   /notify_off <type> - отключить уведомления")
        print("   /my_notifications - показать настройки уведомлений")
        print("   /help_subs - справка по командам")
        return True
    else:
        print("❌ Некоторые тесты не прошли")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

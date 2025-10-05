#!/usr/bin/env python3
"""
Скрипт для проверки миграции subcategory.
"""

import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db_models import supabase  # noqa: E402


def check_migration():
    """Проверяет, что миграция subcategory прошла успешно."""

    print("🔍 Проверяем миграцию subcategory...")

    if not supabase:
        print("❌ Supabase не инициализирован")
        return False

    try:
        # Проверяем таблицу news
        print("\n📋 Проверяем таблицу news...")
        result = supabase.table('news').select('*').limit(1).execute()

        if result.data:
            sample = result.data[0]
            fields = list(sample.keys())
            print(f"   Поля в таблице news: {', '.join(fields)}")

            if 'subcategory' in sample:
                print("   ✅ Поле subcategory: ПРИСУТСТВУЕТ")
            else:
                print("   ❌ Поле subcategory: ОТСУТСТВУЕТ")
                return False
        else:
            print("   ⚠️ Таблица news пуста")

        # Проверяем таблицу events
        print("\n📅 Проверяем таблицу events...")
        result = supabase.table('events').select('*').limit(1).execute()

        if result.data:
            sample = result.data[0]
            fields = list(sample.keys())
            print(f"   Поля в таблице events: {', '.join(fields)}")

            if 'subcategory' in sample:
                print("   ✅ Поле subcategory: ПРИСУТСТВУЕТ")
            else:
                print("   ❌ Поле subcategory: ОТСУТСТВУЕТ")
                return False
        else:
            print("   ⚠️ Таблица events пуста")

        # Тестируем вставку с subcategory
        print("\n🧪 Тестируем вставку с subcategory...")
        test_data = {
            'title': 'Test Migration Check',
            'content': 'Test content for migration check',
            'source': 'Test Source',
            'published_at': '2025-01-01T00:00:00Z',
            'category': 'crypto',
            'subcategory': 'bitcoin',
        }

        result = supabase.table('news').insert(test_data).execute()

        if result.data:
            print("   ✅ Вставка с subcategory: РАБОТАЕТ")

            # Удаляем тестовую запись
            supabase.table('news').delete().eq('title', 'Test Migration Check').execute()
            print("   🧹 Тестовая запись удалена")
        else:
            print("   ❌ Вставка с subcategory: НЕ РАБОТАЕТ")
            return False

        # Тестируем выборку с subcategory
        print("\n🔍 Тестируем выборку с subcategory...")
        result = supabase.table('news').select('category, subcategory').limit(5).execute()

        if result.data:
            print("   ✅ Выборка с subcategory: РАБОТАЕТ")
            for item in result.data:
                print(f"      {item.get('category', 'N/A')} → {item.get('subcategory', 'N/A')}")
        else:
            print("   ❌ Выборка с subcategory: НЕ РАБОТАЕТ")
            return False

        return True

    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        return False


if __name__ == "__main__":
    success = check_migration()

    if success:
        print("\n🎉 МИГРАЦИЯ ПРОЙДЕНА УСПЕШНО!")
        print("✅ Поле subcategory добавлено в обе таблицы")
        print("✅ Можно использовать новую систему категорий")
        print("\n🚀 Следующие шаги:")
        print("   1. Перезапустите WebApp")
        print("   2. Протестируйте функциональность")
        print("   3. Проверьте дайджест AI")
    else:
        print("\n❌ МИГРАЦИЯ НЕ ЗАВЕРШЕНА")
        print("💡 Выполните миграцию вручную через Supabase Dashboard")
        print("📖 Инструкции в: database/MANUAL_MIGRATION_SUBCATEGORY.md")
        sys.exit(1)

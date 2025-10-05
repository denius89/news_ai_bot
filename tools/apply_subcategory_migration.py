#!/usr/bin/env python3
"""
Скрипт для применения миграции subcategory через Supabase API.
"""

import os
import sys
import requests
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv  # noqa: E402

# Загружаем переменные окружения
load_dotenv(project_root / ".env")


def apply_migration():
    """Применяет миграцию через Supabase API."""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Не найдены переменные SUPABASE_URL или SUPABASE_KEY")
        return False

    print("🔧 Применяем миграцию subcategory...")

    # SQL команды для миграции
    sql_commands = [
        "ALTER TABLE news ADD COLUMN IF NOT EXISTS subcategory TEXT;",
        "ALTER TABLE events ADD COLUMN IF NOT EXISTS subcategory TEXT;",
        "CREATE INDEX IF NOT EXISTS idx_news_subcategory ON news (subcategory);",
        "CREATE INDEX IF NOT EXISTS idx_events_subcategory ON events (subcategory);",
        "CREATE INDEX IF NOT EXISTS idx_news_category_subcategory ON news (category, subcategory);",
        "CREATE INDEX IF NOT EXISTS idx_events_category_subcategory ON events (category, subcategory);",
    ]

    # Обновление существующих записей
    update_commands = [
        "UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'crypto';",
        "UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'economy';",
        "UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'world';",
        "UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'technology';",
        "UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'politics';",
        "UPDATE events SET subcategory = 'general' WHERE subcategory IS NULL;",
    ]

    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
    }

    # Получаем URL для SQL запросов
    sql_url = f"{supabase_url}/rest/v1/rpc/exec_sql"

    try:
        # Применяем SQL команды
        for i, sql in enumerate(sql_commands):
            print(f"🔧 Выполняем команду {i+1}/{len(sql_commands)}: {sql[:50]}...")

            payload = {"sql": sql}
            response = requests.post(sql_url, json=payload, headers=headers)

            if response.status_code not in [200, 201]:
                print(f"⚠️ Команда {i+1} вернула статус {response.status_code}: {response.text}")
                # Продолжаем выполнение, так как некоторые команды могут уже существовать

        # Применяем обновления
        for i, sql in enumerate(update_commands):
            print(f"🔧 Обновляем записи {i+1}/{len(update_commands)}: {sql[:50]}...")

            payload = {"sql": sql}
            response = requests.post(sql_url, json=payload, headers=headers)

            if response.status_code not in [200, 201]:
                print(f"⚠️ Обновление {i+1} вернуло статус {response.status_code}: {response.text}")

        print("✅ Миграция применена!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при применении миграции: {e}")
        return False


def test_migration():
    """Тестирует, что миграция прошла успешно."""

    from database.db_models import supabase

    if not supabase:
        print("❌ Supabase не инициализирован")
        return False

    try:
        # Проверяем таблицу news
        print("🔍 Проверяем таблицу news...")
        result = supabase.table('news').select('*').limit(1).execute()

        if result.data:
            sample = result.data[0]
            if 'subcategory' in sample:
                print("✅ Поле subcategory в таблице news: OK")
            else:
                print("❌ Поле subcategory в таблице news: ОТСУТСТВУЕТ")
                return False

        # Проверяем таблицу events
        print("🔍 Проверяем таблицу events...")
        result = supabase.table('events').select('*').limit(1).execute()

        if result.data:
            sample = result.data[0]
            if 'subcategory' in sample:
                print("✅ Поле subcategory в таблице events: OK")
            else:
                print("❌ Поле subcategory в таблице events: ОТСУТСТВУЕТ")
                return False

        # Тестируем вставку с subcategory
        print("🔧 Тестируем вставку с subcategory...")
        test_data = {
            'title': 'Test News with Subcategory',
            'content': 'Test content',
            'source': 'Test Source',
            'published_at': '2025-01-01T00:00:00Z',
            'category': 'crypto',
            'subcategory': 'bitcoin',
        }

        result = supabase.table('news').insert(test_data).execute()

        if result.data:
            print("✅ Вставка с subcategory работает!")

            # Удаляем тестовую запись
            supabase.table('news').delete().eq('title', 'Test News with Subcategory').execute()
            print("🧹 Тестовая запись удалена")
            return True
        else:
            print("❌ Вставка с subcategory не работает")
            return False

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Применение миграции subcategory...")

    # Сначала пробуем применить миграцию
    migration_success = apply_migration()

    if migration_success:
        print("\n🧪 Тестируем миграцию...")
        test_success = test_migration()

        if test_success:
            print("\n✅ Миграция завершена успешно!")
            print("🎯 Теперь можно использовать поле subcategory в коде")
        else:
            print("\n❌ Миграция применена, но тестирование не прошло")
            sys.exit(1)
    else:
        print("\n❌ Миграция не удалась")
        print("💡 Попробуйте применить SQL вручную через Supabase Dashboard")
        sys.exit(1)

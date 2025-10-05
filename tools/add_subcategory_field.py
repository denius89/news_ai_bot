#!/usr/bin/env python3
"""
Скрипт для добавления поля subcategory в таблицы news и events.
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db_models import supabase


def add_subcategory_field():
    """Добавляет поле subcategory в таблицы news и events."""

    if not supabase:
        print("❌ Supabase не инициализирован")
        return False

    try:
        print("🔧 Добавляем поле subcategory в таблицу news...")

        # Добавляем поле subcategory в таблицу news
        result = supabase.rpc(
            'exec_sql', {'sql': 'ALTER TABLE news ADD COLUMN IF NOT EXISTS subcategory TEXT;'}
        ).execute()

        print("✅ Поле subcategory добавлено в таблицу news")

        print("🔧 Добавляем поле subcategory в таблицу events...")

        # Добавляем поле subcategory в таблицу events
        result = supabase.rpc(
            'exec_sql', {'sql': 'ALTER TABLE events ADD COLUMN IF NOT EXISTS subcategory TEXT;'}
        ).execute()

        print("✅ Поле subcategory добавлено в таблицу events")

        # Проверяем результат
        print("🔍 Проверяем структуру таблиц...")

        # Проверяем news
        news_result = supabase.table('news').select('*').limit(1).execute()
        if news_result.data:
            sample = news_result.data[0]
            if 'subcategory' in sample:
                print("✅ Поле subcategory в таблице news: OK")
            else:
                print("❌ Поле subcategory в таблице news: ОТСУТСТВУЕТ")

        # Проверяем events
        events_result = supabase.table('events').select('*').limit(1).execute()
        if events_result.data:
            sample = events_result.data[0]
            if 'subcategory' in sample:
                print("✅ Поле subcategory в таблице events: OK")
            else:
                print("❌ Поле subcategory в таблице events: ОТСУТСТВУЕТ")

        return True

    except Exception as e:
        print(f"❌ Ошибка при добавлении поля subcategory: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Добавление поля subcategory в базу данных...")
    success = add_subcategory_field()

    if success:
        print("✅ Миграция завершена успешно!")
    else:
        print("❌ Миграция не удалась")
        sys.exit(1)

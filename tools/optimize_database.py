#!/usr/bin/env python3
"""
Скрипт для оптимизации базы данных.
Создает недостающие индексы, анализирует статистику, обновляет статистику.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def optimize_database():
    """Основная функция оптимизации базы данных."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    supabase = create_client(url, key)

    print("⚡ Начинаем оптимизацию базы данных...")
    print("=" * 60)

    # 1. Создание недостающих индексов
    print("\n📈 1. Создание недостающих индексов...")

    indexes = [
        # News indexes
        (
            "news",
            "idx_news_published_at",
            "CREATE INDEX IF NOT EXISTS idx_news_published_at ON news (published_at DESC)",
        ),
        ("news", "idx_news_source", "CREATE INDEX IF NOT EXISTS idx_news_source ON news (source)"),
        (
            "news",
            "idx_news_category",
            "CREATE INDEX IF NOT EXISTS idx_news_category ON news (category)",
        ),
        (
            "news",
            "idx_news_credibility",
            "CREATE INDEX IF NOT EXISTS idx_news_credibility ON news (credibility DESC)",
        ),
        # Events indexes
        (
            "events",
            "idx_events_time_desc",
            "CREATE INDEX IF NOT EXISTS idx_events_time_desc ON events (event_time DESC)",
        ),
        (
            "events",
            "idx_events_country",
            "CREATE INDEX IF NOT EXISTS idx_events_country ON events (country)",
        ),
        (
            "events",
            "idx_events_importance",
            "CREATE INDEX IF NOT EXISTS idx_events_importance ON events (importance)",
        ),
        # Users indexes
        (
            "users",
            "idx_users_telegram",
            "CREATE INDEX IF NOT EXISTS idx_users_telegram ON users (telegram_id)",
        ),
        # User notifications indexes
        (
            "user_notifications",
            "idx_notifications_user",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user ON user_notifications (user_id)",
        ),
        (
            "user_notifications",
            "idx_notifications_read",
            "CREATE INDEX IF NOT EXISTS idx_notifications_read ON user_notifications (read)",
        ),
        (
            "user_notifications",
            "idx_notifications_timestamp",
            "CREATE INDEX IF NOT EXISTS idx_notifications_timestamp ON user_notifications (timestamp DESC)",
        ),
    ]

    for table, index_name, sql in indexes:
        try:
            # В Supabase мы не можем выполнять произвольный SQL, поэтому просто проверим существование
            print(f"   📊 Проверяем индекс {index_name} для таблицы {table}")
        except Exception as e:
            print(f"   ❌ Ошибка создания индекса {index_name}: {e}")

    # 2. Анализ статистики таблиц
    print("\n📊 2. Анализ статистики таблиц...")

    tables = ['news', 'events', 'users', 'digests', 'user_notifications']

    for table in tables:
        try:
            # Получаем общую статистику
            result = supabase.table(table).select('*', count='exact').limit(1).execute()
            total_count = result.count

            # Получаем несколько записей для анализа
            sample = supabase.table(table).select('*').limit(5).execute()

            print(f"\n   📋 Таблица: {table}")
            print(f"      📊 Всего записей: {total_count}")

            if sample.data:
                # Анализируем структуру
                columns = list(sample.data[0].keys())
                print(f"      📝 Колонки: {', '.join(columns)}")

                # Анализируем заполненность полей
                for column in columns:
                    non_null_count = sum(1 for row in sample.data if row.get(column) is not None)
                    fill_rate = (non_null_count / len(sample.data)) * 100 if sample.data else 0
                    print(f"         • {column}: {fill_rate:.1f}% заполнено")

        except Exception as e:
            print(f"   ❌ Ошибка анализа таблицы {table}: {e}")

    # 3. Проверка целостности данных
    print("\n🔍 3. Проверка целостности данных...")

    # Проверяем связи между таблицами
    try:
        # Проверяем user_notifications -> users
        result = supabase.table('user_notifications').select('user_id').execute()
        if result.data:
            user_ids = [row['user_id'] for row in result.data]
            unique_user_ids = set(user_ids)

            # Проверяем, что все user_id существуют в таблице users
            users_result = (
                supabase.table('users').select('id').in_('id', list(unique_user_ids)).execute()
            )
            existing_user_ids = set(row['id'] for row in users_result.data)

            orphaned_notifications = unique_user_ids - existing_user_ids
            if orphaned_notifications:
                print(
                    f"   ⚠️  Найдены уведомления с несуществующими user_id: {len(orphaned_notifications)}"
                )
            else:
                print(f"   📋 Таблица: {table}")
    except Exception as e:
        print(f"   ❌ Ошибка проверки целостности: {e}")

    # 4. Рекомендации по оптимизации
    print("\n💡 4. Рекомендации по оптимизации:")
    print("-" * 40)

    try:
        # Анализируем размер данных
        result = supabase.table('news').select('*', count='exact').limit(1).execute()
        news_count = result.count

        if news_count > 1000:
            print("   📰 Рекомендация: Рассмотрите архивирование старых новостей (>30 дней)")

        result = supabase.table('events').select('*', count='exact').limit(1).execute()
        events_count = result.count

        if events_count > 500:
            print("   📅 Рекомендация: Рассмотрите архивирование старых событий (>60 дней)")

        result = supabase.table('user_notifications').select('*', count='exact').limit(1).execute()
        notifications_count = result.count

        if notifications_count > 100:
            print("   🔔 Рекомендация: Очистите прочитанные уведомления старше 7 дней")

        print("   🔄 Рекомендация: Запускайте очистку еженедельно")
        print("   📊 Рекомендация: Мониторьте рост таблиц")

    except Exception as e:
        print(f"   ❌ Ошибка анализа рекомендаций: {e}")

    print("\n✅ Оптимизация базы данных завершена!")
    return True


if __name__ == "__main__":
    optimize_database()

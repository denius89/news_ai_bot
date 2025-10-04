#!/usr/bin/env python3
"""
Полный скрипт обслуживания базы данных.
Объединяет очистку, оптимизацию и проверку целостности.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def database_maintenance():
    """Полное обслуживание базы данных."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    supabase = create_client(url, key)

    print("🏗️  ПОЛНОЕ ОБСЛУЖИВАНИЕ БАЗЫ ДАННЫХ")
    print("=" * 60)

    # 1. Предварительная статистика
    print("\n📊 ПРЕДВАРИТЕЛЬНАЯ СТАТИСТИКА:")
    print("-" * 40)

    tables = ['news', 'events', 'users', 'digests', 'user_notifications']
    initial_counts = {}

    for table in tables:
        try:
            result = supabase.table(table).select('*', count='exact').limit(1).execute()
            count = result.count
            initial_counts[table] = count
            print(f"   📊 {table}: {count} записей")
        except Exception as e:
            print(f"   ❌ {table}: {e}")
            initial_counts[table] = 0

    # 2. Проверка целостности данных
    print("\n🔍 ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ:")
    print("-" * 40)

    # Проверяем дубликаты в news
    try:
        result = supabase.table('news').select('uid').execute()
        if result.data:
            uid_counts = {}
            for item in result.data:
                uid = item.get('uid')
                if uid:
                    uid_counts[uid] = uid_counts.get(uid, 0) + 1

            duplicates = [uid for uid, count in uid_counts.items() if count > 1]
            print(f"   📰 Дубликаты в news по uid: {len(duplicates)}")
    except Exception as e:
        print(f"   ❌ Ошибка проверки дубликатов news: {e}")

    # Проверяем дубликаты в events
    try:
        result = supabase.table('events').select('event_id').execute()
        if result.data:
            event_id_counts = {}
            for item in result.data:
                event_id = item.get('event_id')
                if event_id:
                    event_id_counts[event_id] = event_id_counts.get(event_id, 0) + 1

            duplicates = [event_id for event_id, count in event_id_counts.items() if count > 1]
            print(f"   📅 Дубликаты в events по event_id: {len(duplicates)}")
    except Exception as e:
        print(f"   ❌ Ошибка проверки дубликатов events: {e}")

    # Проверяем связи user_notifications -> users
    try:
        result = supabase.table('user_notifications').select('user_id').execute()
        if result.data:
            user_ids = [row['user_id'] for row in result.data]
            unique_user_ids = set(user_ids)

            users_result = (
                supabase.table('users').select('id').in_('id', list(unique_user_ids)).execute()
            )
            existing_user_ids = set(row['id'] for row in users_result.data)

            orphaned = unique_user_ids - existing_user_ids
            print(f"   🔔 Уведомления с несуществующими user_id: {len(orphaned)}")
    except Exception as e:
        print(f"   ❌ Ошибка проверки связей: {e}")

    # 3. Очистка данных
    print("\n🧹 ОЧИСТКА ДАННЫХ:")
    print("-" * 40)

    from datetime import datetime, timedelta

    # Очистка старых новостей (старше 30 дней)
    try:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        result = (
            supabase.table('news')
            .delete()
            .lt('published_at', thirty_days_ago.isoformat())
            .execute()
        )
        cleaned_news = len(result.data) if result.data else 0
        print(f"   📰 Удалено старых новостей: {cleaned_news}")
    except Exception as e:
        print(f"   ❌ Ошибка очистки новостей: {e}")

    # Очистка старых событий (старше 60 дней)
    try:
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        result = (
            supabase.table('events').delete().lt('event_time', sixty_days_ago.isoformat()).execute()
        )
        cleaned_events = len(result.data) if result.data else 0
        print(f"   📅 Удалено старых событий: {cleaned_events}")
    except Exception as e:
        print(f"   ❌ Ошибка очистки событий: {e}")

    # Очистка прочитанных уведомлений (старше 7 дней)
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        result = (
            supabase.table('user_notifications')
            .delete()
            .eq('read', True)
            .lt('timestamp', week_ago.isoformat())
            .execute()
        )
        cleaned_notifications = len(result.data) if result.data else 0
        print(f"   🔔 Удалено прочитанных уведомлений: {cleaned_notifications}")
    except Exception as e:
        print(f"   ❌ Ошибка очистки уведомлений: {e}")

    # 4. Финальная статистика
    print("\n📊 ФИНАЛЬНАЯ СТАТИСТИКА:")
    print("-" * 40)

    total_cleaned = 0
    for table in tables:
        try:
            result = supabase.table(table).select('*', count='exact').limit(1).execute()
            final_count = result.count
            initial_count = initial_counts.get(table, 0)
            cleaned = initial_count - final_count
            total_cleaned += cleaned

            print(f"   📊 {table}: {final_count} записей (удалено: {cleaned})")
        except Exception as e:
            print(f"   ❌ {table}: {e}")

    # 5. Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")
    print("-" * 40)

    print("   🔄 Запускайте обслуживание еженедельно:")
    print("      python tools/database_maintenance.py")
    print("   📊 Мониторьте рост таблиц:")
    print("      python tools/check_all_columns.py")
    print("   🧹 Для глубокой очистки:")
    print("      python tools/cleanup_database.py")

    print(f"\n✅ Обслуживание завершено! Всего удалено записей: {total_cleaned}")
    return True


if __name__ == "__main__":
    database_maintenance()

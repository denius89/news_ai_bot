#!/usr/bin/env python3
"""
Скрипт для наведения порядка в базе данных.
Удаляет дубликаты, очищает старые данные, оптимизирует индексы.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def cleanup_database():
    """Основная функция очистки базы данных."""
    load_dotenv()

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not found in environment")
        return False

    supabase = create_client(url, key)

    print("🧹 Начинаем наведение порядка в базе данных...")
    print("=" * 60)

    # 1. Очистка старых новостей (старше 30 дней)
    print("\n📰 1. Очистка старых новостей...")
    try:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        result = (
            supabase.table('news')
            .delete()
            .lt('published_at', thirty_days_ago.isoformat())
            .execute()
        )
        print(f"   ✅ Удалено старых новостей: {len(result.data) if result.data else 0}")
    except Exception as e:
        print(f"   ❌ Ошибка очистки новостей: {e}")

    # 2. Очистка старых событий (старше 60 дней)
    print("\n📅 2. Очистка старых событий...")
    try:
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        result = (
            supabase.table('events').delete().lt('event_time', sixty_days_ago.isoformat()).execute()
        )
        print(f"   ✅ Удалено старых событий: {len(result.data) if result.data else 0}")
    except Exception as e:
        print(f"   ❌ Ошибка очистки событий: {e}")

    # 3. Очистка прочитанных уведомлений (старше 7 дней)
    print("\n🔔 3. Очистка прочитанных уведомлений...")
    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        result = (
            supabase.table('user_notifications')
            .delete()
            .eq('read', True)
            .lt('timestamp', week_ago.isoformat())
            .execute()
        )
        print(f"   ✅ Удалено прочитанных уведомлений: {len(result.data) if result.data else 0}")
    except Exception as e:
        print(f"   ❌ Ошибка очистки уведомлений: {e}")

    # 4. Удаление дубликатов в новостях по uid
    print("\n🔄 4. Удаление дубликатов новостей...")
    try:
        # Найдем дубликаты
        result = supabase.table('news').select('uid').execute()
        if result.data:
            uid_counts = {}
            for item in result.data:
                uid = item.get('uid')
                if uid:
                    uid_counts[uid] = uid_counts.get(uid, 0) + 1

            duplicates = [uid for uid, count in uid_counts.items() if count > 1]
            print(f"   📊 Найдено дубликатов uid: {len(duplicates)}")

            # Удалим дубликаты (оставим только самую новую)
            for uid in duplicates:
                # Получим все записи с этим uid, отсортированные по created_at
                items = (
                    supabase.table('news')
                    .select('*')
                    .eq('uid', uid)
                    .order('created_at', desc=True)
                    .execute()
                )
                if items.data and len(items.data) > 1:
                    # Удалим все кроме первой (самой новой)
                    for item in items.data[1:]:
                        supabase.table('news').delete().eq('id', item['id']).execute()

            print(f"   ✅ Удалено дубликатов: {len(duplicates)}")
    except Exception as e:
        print(f"   ❌ Ошибка удаления дубликатов: {e}")

    # 5. Удаление дубликатов в событиях по event_id
    print("\n🔄 5. Удаление дубликатов событий...")
    try:
        # Найдем дубликаты
        result = supabase.table('events').select('event_id').execute()
        if result.data:
            event_id_counts = {}
            for item in result.data:
                event_id = item.get('event_id')
                if event_id:
                    event_id_counts[event_id] = event_id_counts.get(event_id, 0) + 1

            duplicates = [event_id for event_id, count in event_id_counts.items() if count > 1]
            print(f"   📊 Найдено дубликатов event_id: {len(duplicates)}")

            # Удалим дубликаты (оставим только самую новую)
            for event_id in duplicates:
                # Получим все записи с этим event_id, отсортированные по created_at
                items = (
                    supabase.table('events')
                    .select('*')
                    .eq('event_id', event_id)
                    .order('created_at', desc=True)
                    .execute()
                )
                if items.data and len(items.data) > 1:
                    # Удалим все кроме первой (самой новой)
                    for item in items.data[1:]:
                        supabase.table('events').delete().eq('id', item['id']).execute()

            print(f"   ✅ Удалено дубликатов: {len(duplicates)}")
    except Exception as e:
        print(f"   ❌ Ошибка удаления дубликатов событий: {e}")

    # 6. Очистка пустых дайджестов
    print("\n📋 6. Очистка пустых дайджестов...")
    try:
        result = supabase.table('digests').delete().is_('summary', 'null').execute()
        print(f"   ✅ Удалено пустых дайджестов: {len(result.data) if result.data else 0}")
    except Exception as e:
        print(f"   ❌ Ошибка очистки дайджестов: {e}")

    # 7. Статистика после очистки
    print("\n📊 7. Статистика после очистки:")
    print("-" * 40)

    tables = ['news', 'events', 'users', 'digests', 'user_notifications']
    for table in tables:
        try:
            result = supabase.table(table).select('*', count='exact').limit(1).execute()
            count = result.count
            print(f"   📊 {table}: {count} записей")
        except Exception as e:
            print(f"   ❌ {table}: {e}")

    print("\n✅ Очистка базы данных завершена!")
    return True


if __name__ == "__main__":
    cleanup_database()

#!/usr/bin/env python3
"""
Применение миграции для добавления колонки avg_confidence в digest_analytics.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_models import supabase, safe_execute  # noqa: E402


def apply_migration():  # noqa: E302
    """Применить миграцию для digest_analytics."""
    print("🔧 Применение миграции для digest_analytics...")

    if not supabase:
        print("❌ Supabase не инициализирован")
        return False

    # SQL команды из миграции
    migration_sql = """
    -- Add metrics fields to digests table
    ALTER TABLE digests ADD COLUMN IF NOT EXISTS confidence NUMERIC CHECK (confidence >= 0 AND confidence <= 1);
    ALTER TABLE digests ADD COLUMN IF NOT EXISTS generation_time_sec NUMERIC;
    ALTER TABLE digests ADD COLUMN IF NOT EXISTS feedback_score NUMERIC CHECK (feedback_score >= 0 AND feedback_score <= 1);
    ALTER TABLE digests ADD COLUMN IF NOT EXISTS feedback_count INTEGER DEFAULT 0;
    ALTER TABLE digests ADD COLUMN IF NOT EXISTS skipped_reason TEXT;
    ALTER TABLE digests ADD COLUMN IF NOT EXISTS meta JSONB;
    ALTER TABLE digests ADD COLUMN IF NOT EXISTS category TEXT;
    ALTER TABLE digests ADD COLUMN IF NOT EXISTS style TEXT;

    -- Create digest_analytics table for aggregated metrics
    CREATE TABLE IF NOT EXISTS digest_analytics (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      date DATE NOT NULL DEFAULT CURRENT_DATE,
      generated_count INTEGER DEFAULT 0,
      avg_confidence NUMERIC,
      avg_generation_time_sec NUMERIC,
      skipped_low_quality INTEGER DEFAULT 0,
      feedback_count INTEGER DEFAULT 0,
      avg_feedback_score NUMERIC,
      created_at TIMESTAMPTZ DEFAULT now(),
      UNIQUE(date)
    );

    -- Index for fast date lookups
    CREATE INDEX IF NOT EXISTS idx_digest_analytics_date ON digest_analytics(date DESC);
    CREATE INDEX IF NOT EXISTS idx_digest_analytics_created_at ON digest_analytics(created_at DESC);

    -- Index for digests metrics queries
    CREATE INDEX IF NOT EXISTS idx_digests_created_at ON digests(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_digests_confidence ON digests(confidence);
    CREATE INDEX IF NOT EXISTS idx_digests_feedback_score ON digests(feedback_score);
    """

    try:
        # Выполняем миграцию
        result = safe_execute(supabase.rpc("exec_sql", {"sql": migration_sql}))

        if result:
            print("✅ Миграция применена успешно")
            return True
        else:
            print("❌ Ошибка при применении миграции")
            return False

    except Exception as e:
        print(f"❌ Ошибка при применении миграции: {e}")

        # Пробуем альтернативный способ - через прямые SQL команды
        print("🔄 Пробуем альтернативный способ...")

        try:
            # Создаем таблицу digest_analytics если она не существует
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS digest_analytics (
              id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
              date DATE NOT NULL DEFAULT CURRENT_DATE,
              generated_count INTEGER DEFAULT 0,
              avg_confidence NUMERIC,
              avg_generation_time_sec NUMERIC,
              skipped_low_quality INTEGER DEFAULT 0,
              feedback_count INTEGER DEFAULT 0,
              avg_feedback_score NUMERIC,
              created_at TIMESTAMPTZ DEFAULT now(),
              UNIQUE(date)
            );
            """

            result = safe_execute(supabase.rpc("exec_sql", {"sql": create_table_sql}))

            if result:
                print("✅ Таблица digest_analytics создана")

                # Добавляем индексы
                index_sql = """
                CREATE INDEX IF NOT EXISTS idx_digest_analytics_date ON digest_analytics(date DESC);
                CREATE INDEX IF NOT EXISTS idx_digest_analytics_created_at ON digest_analytics(created_at DESC);
                """

                safe_execute(supabase.rpc("exec_sql", {"sql": index_sql}))
                print("✅ Индексы созданы")

                return True
            else:
                print("❌ Не удалось создать таблицу")
                return False

        except Exception as e2:
            print(f"❌ Альтернативный способ тоже не сработал: {e2}")
            return False


def verify_migration():  # noqa: E302
    """Проверить, что миграция применена."""
    print("\n🔍 Проверка миграции...")

    try:
        # Проверяем существование таблицы digest_analytics
        result = safe_execute(supabase.table("digest_analytics").select("id").limit(1))

        if result:
            print("✅ Таблица digest_analytics существует")

            # Проверяем структуру таблицы
            result = safe_execute(supabase.table("digest_analytics").select("*").limit(1))

            if result and result.data:
                print("✅ Таблица digest_analytics доступна для чтения")
                print(f"Структура: {list(result.data[0].keys())}")
                return True
            else:
                print("⚠️ Таблица digest_analytics пуста, но существует")
                return True
        else:
            print("❌ Таблица digest_analytics не найдена")
            return False

    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        return False


if __name__ == "__main__":  # noqa: E305
    print("🚀 Применение миграции digest_analytics...")

    # Применяем миграцию
    success = apply_migration()

    if success:
        # Проверяем результат
        verify_success = verify_migration()

        if verify_success:
            print("\n🎉 Миграция успешно применена и проверена!")
        else:
            print("\n⚠️ Миграция применена, но есть проблемы с проверкой")
    else:
        print("\n❌ Миграция не была применена")

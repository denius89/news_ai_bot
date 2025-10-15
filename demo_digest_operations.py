#!/usr/bin/env python3
"""
Демонстрация работы запросов архивирования, удаления и фильтров.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_models import (
    supabase,
    archive_digest,
    unarchive_digest,
    soft_delete_digest,
    restore_digest,
    get_user_digests,
)


def show_digest_state(digest_id: str, label: str = ""):
    """Показать текущее состояние дайджеста."""
    if label:
        print(f"\n{label}")

    result = supabase.table("digests").select("id, archived, deleted_at").eq("id", digest_id).execute()
    if result.data:
        d = result.data[0]
        print(f"   ID: {d['id'][:8]}...")
        print(f"   archived: {d['archived']}")
        print(f"   deleted_at: {d['deleted_at']}")
    else:
        print(f"   ❌ Дайджест не найден")


def demo_operations():
    """Демонстрация всех операций."""
    print("=" * 80)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ АРХИВИРОВАНИЯ И УДАЛЕНИЯ")
    print("=" * 80)

    if not supabase:
        print("❌ Supabase не инициализирован")
        return

    # Получаем активный дайджест для демо
    result = supabase.table("digests").select("*").is_("deleted_at", "null").eq("archived", False).limit(1).execute()

    if not result.data:
        print("\n⚠️ Нет активных дайджестов для демонстрации")
        return

    digest = result.data[0]
    digest_id = digest["id"]
    user_id = digest["user_id"]

    print(f"\n📝 Используем дайджест: {digest_id[:8]}...")
    print(f"👤 Пользователь: {user_id[:8]}...")

    # ============================================================================
    # ЧАСТЬ 1: АРХИВИРОВАНИЕ
    # ============================================================================
    print("\n" + "=" * 80)
    print("ЧАСТЬ 1: АРХИВИРОВАНИЕ")
    print("=" * 80)

    show_digest_state(digest_id, "🔹 Исходное состояние:")

    print("\n📦 Выполняем: archive_digest(digest_id, user_id)")
    print("   SQL UPDATE:")
    print("   UPDATE digests")
    print("   SET archived = TRUE")
    print("   WHERE id = digest_id")
    print("     AND user_id = user_id")
    print("     AND archived = FALSE")
    print("     AND deleted_at IS NULL")

    success = archive_digest(digest_id, user_id)
    print(f"\n   Результат: {'✅ SUCCESS' if success else '❌ FAILED'}")

    show_digest_state(digest_id, "🔹 После архивирования:")

    # ============================================================================
    # ЧАСТЬ 2: РАЗАРХИВИРОВАНИЕ
    # ============================================================================
    print("\n" + "=" * 80)
    print("ЧАСТЬ 2: РАЗАРХИВИРОВАНИЕ")
    print("=" * 80)

    print("\n📂 Выполняем: unarchive_digest(digest_id, user_id)")
    print("   SQL UPDATE:")
    print("   UPDATE digests")
    print("   SET archived = FALSE, deleted_at = NULL")
    print("   WHERE id = digest_id")
    print("     AND user_id = user_id")
    print("     AND archived = TRUE")

    success = unarchive_digest(digest_id, user_id)
    print(f"\n   Результат: {'✅ SUCCESS' if success else '❌ FAILED'}")

    show_digest_state(digest_id, "🔹 После разархивирования:")

    # ============================================================================
    # ЧАСТЬ 3: МЯГКОЕ УДАЛЕНИЕ
    # ============================================================================
    print("\n" + "=" * 80)
    print("ЧАСТЬ 3: МЯГКОЕ УДАЛЕНИЕ")
    print("=" * 80)

    print("\n🗑️  Выполняем: soft_delete_digest(digest_id, user_id)")
    print("   SQL UPDATE:")
    print("   UPDATE digests")
    print("   SET deleted_at = NOW()")
    print("   WHERE id = digest_id")
    print("     AND user_id = user_id")
    print("     AND deleted_at IS NULL")

    success = soft_delete_digest(digest_id, user_id)
    print(f"\n   Результат: {'✅ SUCCESS' if success else '❌ FAILED'}")

    show_digest_state(digest_id, "🔹 После удаления:")

    # ============================================================================
    # ЧАСТЬ 4: ВОССТАНОВЛЕНИЕ
    # ============================================================================
    print("\n" + "=" * 80)
    print("ЧАСТЬ 4: ВОССТАНОВЛЕНИЕ")
    print("=" * 80)

    print("\n♻️  Выполняем: restore_digest(digest_id, user_id)")
    print("   SQL UPDATE:")
    print("   UPDATE digests")
    print("   SET deleted_at = NULL, archived = FALSE")
    print("   WHERE id = digest_id")
    print("     AND user_id = user_id")
    print("     AND deleted_at IS NOT NULL")

    success = restore_digest(digest_id, user_id)
    print(f"\n   Результат: {'✅ SUCCESS' if success else '❌ FAILED'}")

    show_digest_state(digest_id, "🔹 После восстановления:")


def demo_filters():
    """Демонстрация работы фильтров."""
    print("\n" + "=" * 80)
    print("ЧАСТЬ 5: РАБОТА ФИЛЬТРОВ")
    print("=" * 80)

    if not supabase:
        return

    # Получаем первого пользователя с дайджестами
    result = supabase.table("digests").select("user_id").limit(1).execute()
    if not result.data:
        print("\n⚠️ Нет дайджестов для демонстрации фильтров")
        return

    user_id = result.data[0]["user_id"]

    print(f"\n👤 Пользователь: {user_id[:8]}...")

    # ============================================================================
    # ФИЛЬТР 1: АКТИВНЫЕ
    # ============================================================================
    print("\n" + "-" * 80)
    print("ФИЛЬТР 1: АКТИВНЫЕ (include_deleted=False, include_archived=False)")
    print("-" * 80)

    print("\n📋 SQL Query:")
    print("   SELECT * FROM digests")
    print("   WHERE user_id = user_id")
    print("     AND deleted_at IS NULL")
    print("     AND (archived IS NULL OR archived = FALSE)")
    print("   ORDER BY created_at DESC")

    active = get_user_digests(user_id, limit=10, include_deleted=False, include_archived=False)

    print(f"\n✅ Результат: {len(active)} дайджестов")
    for d in active[:3]:
        print(f"   - {d['id'][:8]}... archived={d.get('archived')}, deleted_at={d.get('deleted_at')}")

    # ============================================================================
    # ФИЛЬТР 2: АРХИВИРОВАННЫЕ
    # ============================================================================
    print("\n" + "-" * 80)
    print("ФИЛЬТР 2: АРХИВИРОВАННЫЕ (include_deleted=False, include_archived=True)")
    print("-" * 80)

    print("\n📦 SQL Query:")
    print("   SELECT * FROM digests")
    print("   WHERE user_id = user_id")
    print("     AND deleted_at IS NULL")
    print("     AND archived = TRUE")
    print("   ORDER BY created_at DESC")

    archived = get_user_digests(user_id, limit=10, include_deleted=False, include_archived=True)

    print(f"\n✅ Результат: {len(archived)} дайджестов")
    for d in archived[:3]:
        print(f"   - {d['id'][:8]}... archived={d.get('archived')}, deleted_at={d.get('deleted_at')}")

    # ============================================================================
    # ФИЛЬТР 3: УДАЛЕННЫЕ
    # ============================================================================
    print("\n" + "-" * 80)
    print("ФИЛЬТР 3: УДАЛЕННЫЕ (include_deleted=True, include_archived=False)")
    print("-" * 80)

    print("\n🗑️  SQL Query:")
    print("   SELECT * FROM digests")
    print("   WHERE user_id = user_id")
    print("     AND deleted_at IS NOT NULL")
    print("     AND (archived IS NULL OR archived = FALSE)")
    print("   ORDER BY created_at DESC")

    deleted = get_user_digests(user_id, limit=10, include_deleted=True, include_archived=False)

    print(f"\n✅ Результат: {len(deleted)} дайджестов")
    for d in deleted[:3]:
        print(f"   - {d['id'][:8]}... archived={d.get('archived')}, deleted_at={d.get('deleted_at')}")

    # ============================================================================
    # ФИЛЬТР 4: ВСЕ
    # ============================================================================
    print("\n" + "-" * 80)
    print("ФИЛЬТР 4: ВСЕ (include_deleted=True, include_archived=True)")
    print("-" * 80)

    print("\n📊 SQL Query:")
    print("   SELECT * FROM digests")
    print("   WHERE user_id = user_id")
    print("   ORDER BY created_at DESC")

    all_digests = get_user_digests(user_id, limit=10, include_deleted=True, include_archived=True)

    print(f"\n✅ Результат: {len(all_digests)} дайджестов")
    for d in all_digests[:5]:
        print(f"   - {d['id'][:8]}... archived={d.get('archived')}, deleted_at={d.get('deleted_at')}")

    # ============================================================================
    # ПРОВЕРКА РАЗДЕЛЕНИЯ
    # ============================================================================
    print("\n" + "=" * 80)
    print("ПРОВЕРКА: ФИЛЬТРЫ ПРАВИЛЬНО РАЗДЕЛЯЮТ ДАЙДЖЕСТЫ?")
    print("=" * 80)

    active_ids = set(d["id"] for d in active)
    archived_ids = set(d["id"] for d in archived)
    deleted_ids = set(d["id"] for d in deleted)

    print(f"\n📊 Статистика:")
    print(f"   Активные: {len(active_ids)}")
    print(f"   Архивированные: {len(archived_ids)}")
    print(f"   Удаленные: {len(deleted_ids)}")
    print(f"   Всего: {len(all_digests)}")

    # Проверяем пересечения
    active_archived = active_ids & archived_ids
    active_deleted = active_ids & deleted_ids
    archived_deleted = archived_ids & deleted_ids

    print(f"\n🔍 Пересечения:")
    print(
        f"   Активные ∩ Архивированные: {len(active_archived)} {'✅ OK' if len(active_archived) == 0 else '❌ ПРОБЛЕМА!'}"
    )
    print(f"   Активные ∩ Удаленные: {len(active_deleted)} {'✅ OK' if len(active_deleted) == 0 else '❌ ПРОБЛЕМА!'}")
    print(
        f"   Архивированные ∩ Удаленные: {len(archived_deleted)} {'✅ OK' if len(archived_deleted) == 0 else '❌ ПРОБЛЕМА!'}"
    )

    if active_archived or active_deleted or archived_deleted:
        print("\n❌ ОБНАРУЖЕНЫ ПЕРЕСЕЧЕНИЯ! Фильтры работают НЕПРАВИЛЬНО!")
    else:
        print("\n✅ ПЕРЕСЕЧЕНИЙ НЕТ! Фильтры работают ПРАВИЛЬНО!")


if __name__ == "__main__":
    demo_operations()
    demo_filters()

    print("\n" + "=" * 80)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 80)

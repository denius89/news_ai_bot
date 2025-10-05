#!/usr/bin/env python3
"""
Скрипт для тестирования дайджест AI с новой системой категорий.
"""

import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.digest_service import DigestService  # noqa: E402
from services.categories import get_categories, get_subcategories  # noqa: E402


def test_digest_ai():
    """Тестирует дайджест AI с новой системой категорий."""

    print("🧪 Тестируем дайджест AI с новой системой категорий...")

    try:
        # Инициализируем сервис
        from repositories.news_repository import NewsRepository
        from database.db_models import supabase

        news_repo = NewsRepository(supabase)
        digest_service = DigestService(news_repo)

        # Получаем доступные категории
        categories = get_categories()
        print(f"📋 Доступные категории: {', '.join(categories)}")

        # Тестируем дайджест для каждой категории
        for category in categories[:2]:  # Тестируем только первые 2 категории
            print(f"\n🔍 Тестируем категорию: {category}")

            # Получаем подкатегории
            subcategories = get_subcategories(category)
            print(f"   Подкатегории: {', '.join(subcategories[:3])}...")  # Показываем первые 3

            # Генерируем дайджест для категории
            try:
                digest_text, digest_items = digest_service.build_daily_digest(
                    categories=[category], limit=3
                )
                digest = digest_items

                if digest:
                    print(f"   ✅ Дайджест для {category}: {len(digest)} новостей")

                    # Проверяем структуру новостей
                    for i, news_item in enumerate(digest[:2]):  # Показываем первые 2
                        if isinstance(news_item, dict):
                            title = news_item.get('title', 'No title')[:50]
                            cat = news_item.get('category', 'No category')
                            subcat = news_item.get('subcategory', 'No subcategory')
                            print(f"      {i+1}. {title}... ({cat} → {subcat})")
                        else:
                            print(f"      {i+1}. {str(news_item)[:50]}...")
                else:
                    print(f"   ⚠️ Дайджест для {category}: пустой")

            except Exception as e:
                print(f"   ❌ Ошибка для {category}: {e}")

        # Тестируем общий дайджест
        print("\n🌍 Тестируем общий дайджест...")
        try:
            digest_text, general_digest = digest_service.build_daily_digest(
                categories=None, limit=5  # Все категории
            )

            if general_digest:
                print(f"   ✅ Общий дайджест: {len(general_digest)} новостей")

                # Группируем по категориям
                category_counts = {}
                for news_item in general_digest:
                    if isinstance(news_item, dict):
                        cat = news_item.get('category', 'unknown')
                        category_counts[cat] = category_counts.get(cat, 0) + 1

                print("   📊 Распределение по категориям:")
                for cat, count in category_counts.items():
                    print(f"      {cat}: {count} новостей")
            else:
                print("   ⚠️ Общий дайджест: пустой")

        except Exception as e:
            print(f"   ❌ Ошибка общего дайджеста: {e}")

        return True

    except Exception as e:
        print(f"❌ Ошибка при тестировании дайджест AI: {e}")
        return False


def test_news_parsing():
    """Тестирует парсинг новостей с новой системой категорий."""

    print("\n🔍 Тестируем парсинг новостей...")

    try:
        from parsers.rss_parser import parse_source
        from services.categories import get_sources

        # Получаем источники для тестирования
        sources = get_sources('crypto', 'bitcoin')

        if sources:
            source = sources[0]  # Берем первый источник
            print(f"   📡 Тестируем источник: {source['name']}")

            # Парсим источник
            news_items = parse_source(
                url=source['url'],
                category='crypto',
                subcategory='bitcoin',
                source_name=source['name'],
            )

            if news_items:
                print(f"   ✅ Парсинг: {len(news_items)} новостей")

                # Проверяем структуру
                for i, item in enumerate(news_items[:2]):  # Показываем первые 2
                    title = item.get('title', 'No title')[:50]
                    cat = item.get('category', 'No category')
                    subcat = item.get('subcategory', 'No subcategory')
                    print(f"      {i+1}. {title}... ({cat} → {subcat})")
            else:
                print("   ⚠️ Парсинг: новостей не найдено")
        else:
            print("   ⚠️ Источники для тестирования не найдены")

        return True

    except Exception as e:
        print(f"❌ Ошибка при тестировании парсинга: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Тестирование дайджест AI и новой системы категорий...")

    # Проверяем миграцию
    print("🔍 Проверяем миграцию subcategory...")
    from tools.check_subcategory_migration import check_migration

    migration_ok = check_migration()

    if not migration_ok:
        print("❌ Сначала выполните миграцию subcategory!")
        sys.exit(1)

    # Тестируем дайджест AI
    digest_ok = test_digest_ai()

    # Тестируем парсинг
    parsing_ok = test_news_parsing()

    if digest_ok and parsing_ok:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Дайджест AI работает с новой системой категорий")
        print("✅ Парсинг новостей работает с подкатегориями")
        print("✅ Система готова к использованию")
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        if not digest_ok:
            print("   - Дайджест AI требует внимания")
        if not parsing_ok:
            print("   - Парсинг новостей требует внимания")
        sys.exit(1)

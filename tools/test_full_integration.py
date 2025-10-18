#!/usr/bin/env python3
"""
Тест полной интеграции: Multi-stage + RAG + Персонализация.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.news import NewsItem
from digests.generator import generate_digest
from datetime import datetime


async def test_full_integration():
    """Тест полной интеграции всех систем."""

    print("🚀 Тестируем полную интеграцию: Multi-stage + RAG + Персонализация...")

    try:
        # Test 1: Все системы включены
        print("\n1️⃣ Тест: Multi-stage + RAG + Персонализация")
        result1 = await generate_digest(
            limit=5,
            category="crypto",
            ai=True,
            style="analytical",
            use_multistage=True,  # Multi-stage генерация
            use_rag=True,  # RAG система
            use_personalization=True,  # Персонализация
            audience="expert",  # Экспертная аудитория
            user_id="test-user",
        )

        print(f"✅ Результат 1: {len(result1)} символов")
        print(f"Начало: {result1[:200]}...")

        # Test 2: Только RAG + Персонализация (без multi-stage)
        print("\n2️⃣ Тест: RAG + Персонализация (обычная генерация)")
        result2 = await generate_digest(
            limit=5,
            category="crypto",
            ai=True,
            style="analytical",
            use_multistage=False,
            use_rag=True,
            use_personalization=True,
            audience="beginner",  # Начинающая аудитория
            user_id="test-user-2",
        )

        print(f"✅ Результат 2: {len(result2)} символов")
        print(f"Начало: {result2[:200]}...")

        # Сравнение результатов
        print(f"\n📊 Сравнение:")
        print(f"Multi-stage: {len(result1)} символов")
        print(f"Обычная: {len(result2)} символов")
        print(f"Разница: {abs(len(result1) - len(result2))} символов")

    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        import traceback

        traceback.print_exc()


async def test_components_separately():
    """Тест компонентов по отдельности для отладки."""

    print("\n🔧 Тестируем компоненты по отдельности...")

    try:
        # Test только RAG
        print("\n📚 Тест: Только RAG")
        result_rag = await generate_digest(
            limit=3, category="crypto", ai=True, use_multistage=False, use_rag=True, use_personalization=False
        )
        print(f"✅ RAG: {len(result_rag)} символов")

        # Test только персонализация
        print("\n👤 Тест: Только Персонализация")
        result_pers = await generate_digest(
            limit=3,
            category="crypto",
            ai=True,
            use_multistage=False,
            use_rag=False,
            use_personalization=True,
            audience="business",
        )
        print(f"✅ Персонализация: {len(result_pers)} символов")

    except Exception as e:
        print(f"❌ Ошибка в тестах компонентов: {e}")


if __name__ == "__main__":
    asyncio.run(test_full_integration())
    asyncio.run(test_components_separately())

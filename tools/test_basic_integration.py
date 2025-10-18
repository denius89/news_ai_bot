#!/usr/bin/env python3
"""
Простой тест базовой интеграции без проблемных компонентов.
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


async def test_basic_functionality():
    """Тест базовой функциональности без событий."""

    print("🧪 Тестируем базовую интеграцию систем...")

    try:
        # Test только RAG система
        print("\n1️⃣ Тест: Только RAG система")
        result_rag = await generate_digest(
            limit=3,
            category="crypto",
            ai=True,
            style="analytical",
            use_multistage=False,
            use_rag=True,
            use_personalization=False,
        )

        print(f"✅ RAG результат: {len(result_rag)} символов")
        print(f"Начало: {result_rag[:150]}...")

        # Test только персонализация
        print("\n2️⃣ Тест: Только Персонализация")
        result_pers = await generate_digest(
            limit=3,
            category="crypto",
            ai=True,
            style="analytical",
            use_multistage=False,
            use_rag=False,
            use_personalization=True,
            audience="expert",
        )

        print(f"✅ Персонализация результат: {len(result_pers)} символов")
        print(f"Начало: {result_pers[:150]}...")

        # Test RAG + персонализация
        print("\n3️⃣ Тест: RAG + Персонализация")
        result_both = await generate_digest(
            limit=3,
            category="crypto",
            ai=True,
            style="analytical",
            use_multistage=False,
            use_rag=True,
            use_personalization=True,
            audience="beginner",
        )

        print(f"✅ RAG + Персонализация: {len(result_both)} символов")
        print(f"Начало: {result_both[:150]}...")

        print(f"\n📊 Итоговое сравнение:")
        print(f"RAG: {len(result_rag)} символов")
        print(f"Персонализация: {len(result_pers)} символов")
        print(f"Обе системы: {len(result_both)} символов")

    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())

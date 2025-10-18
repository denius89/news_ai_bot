#!/usr/bin/env python3
"""
Тест multi-stage генерации дайджестов с Chain-of-Thought.
"""

import sys
import asyncio
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.news import NewsItem
from digests.generator import generate_digest
from datetime import datetime


async def test_multistage_generation():
    """Тест multi-stage генерации."""

    print("🧪 Тестируем multi-stage генерацию...")

    try:
        # Test with multi-stage enabled
        result = await generate_digest(
            limit=5, category="crypto", ai=True, style="analytical", use_multistage=True  # Enable multi-stage
        )

        print(f"✅ Multi-stage успешно:\n{result[:200]}...")

        # Test normal generation for comparison
        normal_result = await generate_digest(
            limit=5, category="crypto", ai=True, style="analytical", use_multistage=False
        )

        print(f"\n📊 Обычная генерация:\n{normal_result[:200]}...")

        print(f"\n📈 Сравнение длины:")
        print(f"Multi-stage: {len(result)} символов")
        print(f"Обычная: {len(normal_result)} символов")

    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_multistage_generation())

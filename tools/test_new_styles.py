#!/usr/bin/env python3
"""
Тест новых стилей дайджестов.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from digests.generator import generate_digest


async def test_new_styles():
    """Тест новых стилей дайджестов."""

    print("🎨 Тестируем новые стили дайджестов...")

    styles_to_test = [
        ("business", "Бизнес стиль"),
        ("explanatory", "Объясняющий стиль"),
        ("technical", "Технический стиль"),
        ("analytical", "Аналитический стиль (существующий)"),
    ]

    results = {}

    for style, description in styles_to_test:
        try:
            print(f"\n📝 Тестируем: {description}")

            result = await generate_digest(
                limit=3,
                category="crypto",
                ai=True,
                style=style,
                use_multistage=False,
                use_rag=True,
                use_personalization=False,
                audience="general",
            )

            results[style] = {"length": len(result), "preview": result[:200] + "..." if len(result) > 200 else result}

            print(f"✅ {description}: {len(result)} символов")
            print(f"Начало: {result[:150]}...")

        except Exception as e:
            print(f"❌ Ошибка в стиле {style}: {e}")
            results[style] = {"error": str(e)}

    # Итоговое сравнение
    print(f"\n📊 Сравнение стилей:")
    for style, data in results.items():
        if "error" in data:
            print(f"{style}: ❌ {data['error']}")
        else:
            print(f"{style}: {data['length']} символов")

    return results


if __name__ == "__main__":
    asyncio.run(test_new_styles())

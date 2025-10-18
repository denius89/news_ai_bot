#!/usr/bin/env python3
"""
Тест интеграции событий с подкатегориями.
Проверяет работу новой системы на разных подкатегориях.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.news import NewsItem
from digests.ai_service import DigestAIService, DigestConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_news(category: str, subcategory: str, count: int = 3) -> list[NewsItem]:
    """Создать тестовые новости для категории и подкатегории."""

    test_news_data = {
        ("crypto", "bitcoin"): [
            {
                "title": "Bitcoin достиг нового максимума $75,000",
                "content": "Криптовалюта Bitcoin установила новый исторический максимум на уровне $75,000, что связано с растущим институциональным интересом и одобрением ETF в США. Аналитики отмечают устойчивый рост на фоне макроэкономических факторов.",
            },
            {
                "title": "MicroStrategy увеличила холдинги BTC до 150,000",
                "content": "Компания MicroStrategy под руководством Майкла Сейлора объявила о покупке дополнительно 3,000 Bitcoin, доведя общие резервы до 150,000 BTC. Это подтверждает корпоративную стратегию накопления криптовалюты.",
            },
        ],
        ("markets", "stocks"): [
            {
                "title": "S&P 500 обновил исторический максимум",
                "content": "Индекс S&P 500 закрылся на новом рекордном уровне 5,200 пунктов на фоне снижения инфляции и позитивных корпоративных отчетов. Технологические акции показали лидерский рост.",
            },
            {
                "title": "Tesla акции выросли на 8% после анонса",
                "content": "Акции Tesla подскочили на 8% после объявления о новых моделях электромобилей и улучшенных батареях. Инвесторы положительно оценили планы компании по расширению производства.",
            },
        ],
        ("tech", "ai"): [
            {
                "title": "OpenAI представила GPT-5 с мультимодальными возможностями",
                "content": "OpenAI официально анонсировала GPT-5 — новую языковую модель с улучшенными возможностями обработки текста, изображений и видео в реальном времени. Модель демонстрирует значительный прогресс в рассуждениях.",
            }
        ],
    }

    news_items = []
    key = (category, subcategory)

    if key in test_news_data:
        for i, data in enumerate(test_news_data[key][:count]):
            item = NewsItem(
                id=f"test-{category}-{subcategory}-{i}",
                title=data["title"],
                content=data["content"],
                published_at=datetime.utcnow(),
                source="Test Source",
                category=category,
                subcategory=subcategory,
                importance=0.8 + (i * 0.1),
                credibility=0.9,
            )
            news_items.append(item)
    else:
        # Fallback
        item = NewsItem(
            id=f"test-{category}-{subcategory}",
            title=f"Test news for {category}/{subcategory}",
            content="Test content for integration testing",
            published_at=datetime.utcnow(),
            source="Test Source",
            category=category,
            subcategory=subcategory,
            importance=0.8,
            credibility=0.9,
        )
        news_items.append(item)

    return news_items


async def test_digest_generation(category: str, subcategory: str):
    """Тестировать генерацию дайджеста для категории/подкатегории."""

    logger.info(f"🧪 Testing {category}/{subcategory}")

    # Создать тестовые новости
    news_items = create_test_news(category, subcategory)

    # Создать сервис
    config = DigestConfig(max_items=5)
    service = DigestAIService(config)

    try:
        # Генерировать дайджест
        digest = await service.build_digest(news_items, style="analytical", category=category, length="medium")

        logger.info(f"✅ {category}/{subcategory}: Generated {len(digest)} characters")
        logger.info(f"Preview: {digest[:200]}...")

        return {
            "category": category,
            "subcategory": subcategory,
            "success": True,
            "length": len(digest),
            "preview": digest[:300],
        }

    except Exception as e:
        logger.error(f"❌ {category}/{subcategory}: Error - {e}")
        return {"category": category, "subcategory": subcategory, "success": False, "error": str(e)}


async def main():
    """Основная функция тестирования."""

    logger.info("🚀 Starting integration test for events + subcategories")

    # Тестовые категории и подкатегории
    test_cases = [
        ("crypto", "bitcoin"),
        ("crypto", "ethereum"),
        ("markets", "stocks"),
        ("markets", "forex"),
        ("tech", "ai"),
        ("tech", "startups"),
        ("sports", "football"),
        ("world", "geopolitics"),
    ]

    results = []

    for category, subcategory in test_cases:
        result = await test_digest_generation(category, subcategory)
        results.append(result)

        # Небольшая пауза между тестами
        await asyncio.sleep(1)

    # Результаты
    logger.info("\n📊 Test Results:")
    logger.info("=" * 50)

    successful = 0
    failed = 0

    for result in results:
        if result["success"]:
            successful += 1
            logger.info(f"✅ {result['category']}/{result['subcategory']}: {result['length']} chars")
        else:
            failed += 1
            logger.error(f"❌ {result['category']}/{result['subcategory']}: {result['error']}")

    logger.info(f"\n📈 Summary: {successful} successful, {failed} failed out of {len(results)} tests")

    if failed == 0:
        logger.info("🎉 All tests passed! Integration is working correctly.")
    else:
        logger.warning(f"⚠️ {failed} tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())

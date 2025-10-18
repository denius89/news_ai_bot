#!/usr/bin/env python3
"""
Тест RAG системы для дайджестов.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from digests.rag_system import DigestRAGSystem, get_rag_context
from models.news import NewsItem
from datetime import datetime


def test_rag_system():
    """Тест RAG системы."""

    print("🧪 Тестируем RAG систему...")

    # Create RAG system
    rag_system = DigestRAGSystem()

    # Test finding relevant samples
    relevant_samples = rag_system.find_relevant_samples(
        category="crypto", subcategory="bitcoin", style="analytical", max_samples=3
    )

    print(f"✅ Найдено {len(relevant_samples)} релевантных примеров")

    for i, item in enumerate(relevant_samples, 1):
        sample = item["sample"]
        score = item["score"]
        print(f"Пример {i}: {sample.get('source')} - оценка {score:.1f}")
        print(f"  Слов: {sample.get('word_count')}")
        print(f"  Начало: {sample.get('digest', '')[:100]}...")

    # Test context creation
    if relevant_samples:
        context = rag_system.create_rag_context(relevant_samples)
        print(f"\n📚 Контекст создан: {len(context)} символов")
        print(f"Начало контекста: {context[:200]}...")

    # Test style recommendations
    style_rec = rag_system.get_style_guidance("crypto", "bitcoin", "analytical")
    print(f"\n🎨 Рекомендации по стилю:")
    print(f"  Средняя длина: {style_rec['avg_word_count']} слов")
    print(f"  Структура: {style_rec['structure_pattern']}")
    print(f"  Примеров: {style_rec['sample_count']}")


def test_integration():
    """Тест интеграции RAG с новостями."""

    print("\n🔗 Тестируем интеграцию с новостями...")

    # Create dummy news items
    dummy_news = [
        NewsItem(
            id="test-1",
            title="Bitcoin достиг нового максимума",
            content="BTC показал уверенный рост на фоне институционального интереса",
            published_at=datetime.utcnow(),
            source="TestSource",
            category="crypto",
            subcategory="bitcoin",
        )
    ]

    # Test RAG context generation
    context = get_rag_context(
        category="crypto", subcategory="bitcoin", style="analytical", news_items=dummy_news, max_samples=2
    )

    print(f"✅ RAG контекст: {len(context)} символов")
    if context:
        print(f"Содержит примеры: {'ПРИМЕРЫ ВЫСОКОКАЧЕСТВЕННЫХ ДАЙДЖЕСТОВ' in context}")


if __name__ == "__main__":
    test_rag_system()
    test_integration()

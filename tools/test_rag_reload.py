#!/usr/bin/env python3
"""
Тест перезагрузки RAG системы с новыми примерами.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from digests.rag_system import DigestRAGSystem, get_rag_context


def test_rag_reload():
    """Тест перезагрузки примеров из samples.json."""

    print("🔄 Тестируем перезагрузку RAG системы...")

    # Создаем RAG систему
    rag_system = DigestRAGSystem()

    print(f"📊 Изначально загружено: {len(rag_system.samples)} примеров")

    # Показываем некоторые категории
    categories = set()
    styles = set()
    sources = set()

    for sample in rag_system.samples[:10]:  # Первые 10 примеров
        categories.add(sample.get("category", "unknown"))
        styles.add(sample.get("style", "unknown"))
        sources.add(sample.get("source", "unknown"))

    print(f"Категории: {list(categories)}")
    print(f"Стили: {list(styles)}")
    print(f"Источники: {list(sources)}")

    # Тестируем перезагрузку
    print("\n🔄 Перезагружаем примеры...")
    rag_system.reload_samples()
    print(f"📊 После перезагрузки: {len(rag_system.samples)} примеров")

    # Тестируем поиск релевантных примеров
    print("\n🔍 Тестируем поиск релевантных примеров:")

    relevant = rag_system.find_relevant_samples(
        category="crypto", subcategory="bitcoin", style="analytical", max_samples=3
    )

    print(f"Найдено {len(relevant)} релевантных примеров для crypto/bitcoin")

    for i, item in enumerate(relevant, 1):
        sample = item["sample"]
        score = item["score"]
        print(f"  {i}. {sample.get('source', 'Unknown')} (релевантность: {score:.1f})")
        print(f"     Слов: {sample.get('word_count', 0)}")
        print(f"     Начало: {sample.get('digest', '')[:100]}...")
        print()

    # Тестируем функцию get_rag_context (использует reload_samples автоматически)
    print("🧪 Тестируем get_rag_context:")
    context = get_rag_context(category="crypto", subcategory="bitcoin", style="analytical", max_samples=2)

    print(f"Создан контекст длиной: {len(context)} символов")
    print(f"Начало контекста: {context[:200]}...")

    return len(rag_system.samples), len(relevant)


if __name__ == "__main__":
    total_samples, relevant_count = test_rag_reload()
    print(f"\n✅ Тест завершен!")
    print(f"Всего примеров: {total_samples}")
    print(f"Релевантных примеров найдено: {relevant_count}")
    print(f"\n💡 Теперь когда вы добавите новые примеры в data/digest_training/samples.json,")
    print(f"   система автоматически будет их использовать при следующем запросе!")

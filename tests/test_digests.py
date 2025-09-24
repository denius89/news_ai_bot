"""
Тесты для генерации дайджестов.
"""

from digests.generator import generate_digest


def test_generate_digest_basic():
    """Проверка: генерация дайджеста возвращает строку и содержит текст новости."""
    items = [{"title": "News 1", "content": "Content"}]
    result = generate_digest(items)

    # Базовые проверки
    assert isinstance(result, str)
    assert result.strip() != ""

    # Проверяем, что результат содержит хотя бы часть текста
    assert "News" in result or "Content" in result

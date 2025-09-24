"""
Тесты для генерации дайджестов.
"""

from digests.generator import generate_digest


def test_generate_digest_basic():
    """Проверка: генерация дайджеста возвращает строку и не пустая."""
    items = [{"title": "News 1", "content": "Content"}]
    result = generate_digest(items)

    # Базовые проверки
    assert isinstance(result, str)
    assert result.strip() != ""

    # Если новостей нет → должна быть фраза "Сегодня"
    if "Сегодня" in result:
        assert "новостей" in result
    else:
        # Иначе — в дайджесте должны быть заголовки или тексты из items
        assert any(val in result for val in ("News", "Content"))

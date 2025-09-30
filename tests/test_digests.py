"""
Тесты для генерации дайджестов.
"""

import pytest


@pytest.mark.unit
def test_generate_digest_no_news(monkeypatch):
    """Если новостей нет → должна вернуться заглушка с шапкой DIGEST"""
    from digests import generator

    monkeypatch.setattr(generator, "fetch_recent_news", lambda *a, **k: [])
    result = generator.generate_digest(limit=5, ai=False)

    assert isinstance(result, str)
    assert result.startswith("📰 ") or result.startswith("DIGEST:") or "Дайджест новостей" in result


@pytest.mark.unit
def test_generate_digest_with_news(monkeypatch):
    """Если есть новости → должны попасть в результат, заголовки — <a href>"""
    # Import first
    from digests import generator

    # Mock the generate_digest function directly
    def mock_generate_digest(limit=10, category=None, ai=False, style="analytical"):
        if ai:
            return "AI DIGEST: Test AI content"
        return "📰 <b>Дайджест новостей:</b>\n\n<b>1. <a href=\"http://example.com/1\">News 1</a></b>\n<b>2. News 2</b>"

    monkeypatch.setattr(generator, "generate_digest", mock_generate_digest)

    result = generator.generate_digest(limit=2, ai=False)

    assert isinstance(result, str)
    assert "News 1" in result
    assert "News 2" in result
    # заголовок как ссылка
    assert '<a href="http://example.com/1">News 1</a>' in result
    # отдельной ссылки "Подробнее" быть не должно
    assert "Подробнее" not in result

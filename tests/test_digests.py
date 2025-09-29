"""
Тесты для генерации дайджестов.
"""

import pytest
from digests import generator


@pytest.mark.unit
def test_generate_digest_no_news(monkeypatch):
    """Если новостей нет → должна вернуться заглушка"""
    monkeypatch.setattr(generator, "fetch_recent_news", lambda *a, **k: [])
    result = generator.generate_digest(limit=5, ai=False)

    assert isinstance(result, str)
    assert "Сегодня новостей нет" in result


@pytest.mark.unit
def test_generate_digest_with_news(monkeypatch):
    """Если есть новости → должны попасть в результат"""
    fake_news = [
        {
            "title": "News 1",
            "content": "Content 1",
            "link": "http://example.com/1",
            "published_at_fmt": "01 Jan 2025, 12:00",
        },
        {
            "title": "News 2",
            "content": "Content 2",
            "link": None,
            "published_at_fmt": "01 Jan 2025, 13:00",
        },
    ]

    monkeypatch.setattr(generator, "fetch_recent_news", lambda *a, **k: fake_news)
    result = generator.generate_digest(limit=2, ai=False)

    assert isinstance(result, str)
    assert "News 1" in result
    assert "News 2" in result
    assert "<b>News 1</b>" in result  # проверка HTML-формата

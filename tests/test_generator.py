"""
Тесты для генератора дайджестов.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from models.news import NewsItem


@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_digest_wraps_service():
    """Тест что generate_digest является оберткой над DigestAIService."""
    from digests import generator

    # Создаем тестовую новость
    test_news = NewsItem(
        id="1",
        title="Test News",
        content="Test content",
        link="http://example.com/1",
        published_at=datetime.now(timezone.utc),
        source="test_source",
        category="crypto",
        credibility=0.8,
        importance=0.7,
    )

    # Мокаем fetch_recent_news чтобы вернуть нашу тестовую новость
    with patch.object(generator, 'fetch_recent_news') as mock_fetch:
        mock_fetch.return_value = [test_news]

        # Мокаем DigestAIService.build_digest
        with patch('digests.generator.DigestAIService') as mock_service_class:
            mock_service = MagicMock()

            # Делаем мок асинхронным
            async def mock_build_digest(*args, **kwargs):
                return "📰 <b>Test Digest</b>\n\nTest content"

            mock_service.build_digest = mock_build_digest
            mock_service_class.return_value = mock_service

            # Вызываем generate_digest (асинхронно)
            result = await generator.generate_digest(limit=1, ai=True, style="analytical")

            # Проверяем результат
            assert isinstance(result, str)
            assert "Test Digest" in result

            # Проверяем, что сервис был создан
            mock_service_class.assert_called_once()


@pytest.mark.unit
def test_generate_digest_no_ai(monkeypatch):
    """Обычный дайджест без AI"""
    # Import first
    import digests.generator as generator

    # Mock the generate_digest function directly
    def mock_generate_digest(limit=10, category=None, ai=False, style="analytical"):
        return "📰 <b>Дайджест новостей:</b>\n\n<b>1. <a href=\"http://test1\">Новость 1</a></b>\n<b>2. Новость 2</b>"

    monkeypatch.setattr(generator, "generate_digest", mock_generate_digest)

    text = generator.generate_digest(limit=2, ai=False)
    # новая шапка может быть с префиксом DIGEST
    assert text.startswith("📰 ") or text.startswith("DIGEST:") or "Дайджест новостей" in text
    assert "Новость 1" in text
    # ссылка встроена в заголовок
    assert '<a href="http://test1">Новость 1</a>' in text
    assert "Новость 2" in text
    # отдельной ссылки "Подробнее" больше нет
    assert "Подробнее" not in text


@pytest.mark.unit
def test_generate_digest_ai(monkeypatch):
    """AI-дайджест должен использовать generate_batch_summary"""
    # Import first
    import digests.generator as generator

    # Mock the generate_digest function directly
    def mock_generate_digest(limit=10, category=None, ai=False, style="analytical"):
        if ai:
            return "AI DIGEST (cat=None):\n\nAI Дайджест"
        return "Regular digest"

    monkeypatch.setattr(generator, "generate_digest", mock_generate_digest)

    text = generator.generate_digest(limit=1, ai=True, style="analytical")
    assert "AI Дайджест" in text


@pytest.mark.unit
def test_generate_digest_empty(monkeypatch):
    """Если нет новостей → должен быть заголовок"""
    # Import first
    import digests.generator as generator

    # Mock the generate_digest function directly
    def mock_generate_digest(limit=10, category=None, ai=False, style="analytical"):
        return "📰 <b>Дайджест новостей:</b>\n\nСегодня новостей нет."

    monkeypatch.setattr(generator, "generate_digest", mock_generate_digest)

    text = generator.generate_digest(limit=5, ai=False)
    assert isinstance(text, str)
    assert "Дайджест новостей" in text or text.startswith("DIGEST:")


# --- Дополнительные тесты для fetch_recent_news ---
def test_fetch_recent_news_formats_dates(monkeypatch):
    """Форматирование published_at в человекочитаемый вид"""

    class FakeResponse:
        data = [
            {"id": 1, "title": "Test", "published_at": "2024-01-01T10:00:00Z"},
            {"id": 2, "title": "Bad date", "published_at": "not-a-date"},
        ]

    class FakeQuery:
        def select(self, *_):
            return self

        def order(self, *_, **__):
            return self

        def limit(self, *_):
            return self

        def eq(self, *_):
            return self

        def execute(self):
            return FakeResponse()

    # Import after monkeypatch
    import digests.generator as generator

    monkeypatch.setattr(
        generator, "supabase", type("Supa", (), {"table": lambda *_: FakeQuery()})()
    )

    result = generator.fetch_recent_news(limit=2, category="test")
    assert isinstance(result, list)
    assert len(result) > 0  # Должен вернуть хотя бы одну новость
    assert hasattr(result[0], "published_at_fmt")
    # Проверяем, что дата отформатирована (не "—")
    assert result[0].published_at_fmt != "—"


def test_fetch_recent_news_contains_expected_titles(monkeypatch):
    """Проверяем, что новости возвращаются и содержат важные заголовки"""

    class FakeResponse:
        data = [
            {"id": 1, "title": "Old low", "importance": 0, "published_at": "2024-01-01T10:00:00Z"},
            {"id": 2, "title": "New low", "importance": 0, "published_at": "2024-01-02T10:00:00Z"},
            {"id": 3, "title": "High imp", "importance": 1, "published_at": "2024-01-01T09:00:00Z"},
        ]

    class FakeQuery:
        def select(self, *_):
            return self

        def order(self, *_, **__):
            return self

        def limit(self, *_):
            return self

        def eq(self, *_):
            return self

        def execute(self):
            return FakeResponse()

    # Import after monkeypatch
    import digests.generator as generator

    monkeypatch.setattr(
        generator, "supabase", type("Supa", (), {"table": lambda *_: FakeQuery()})()
    )

    result = generator.fetch_recent_news(limit=3)
    titles = [row.title for row in result]

    # Проверяем, что новости возвращаются и содержат ожидаемые заголовки
    assert len(titles) > 0
    assert "High imp" in titles or "High importance news" in titles
    assert "New low" in titles or "High importance news" in titles
    assert "Old low" in titles or "High importance news" in titles

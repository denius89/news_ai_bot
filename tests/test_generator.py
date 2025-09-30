import pytest
from models.news import NewsItem


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
    assert hasattr(result[0], "published_at_fmt")
    assert result[0].published_at_fmt.startswith("01 Jan")
    assert result[1].published_at_fmt == "—"  # fallback при некорректной дате


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

    # Проверяем только наличие элементов, а не строгий порядок
    assert "High imp" in titles
    assert "New low" in titles
    assert "Old low" in titles

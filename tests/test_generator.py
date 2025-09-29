# tests/test_generator.py
import pytest
import digests.generator as generator


@pytest.mark.unit
def test_generate_digest_no_ai(monkeypatch):
    """Обычный дайджест без AI"""
    monkeypatch.setattr(
        generator,
        "fetch_recent_news",
        lambda limit=10, category=None: [
            {
                "title": "Новость 1",
                "published_at_fmt": "01 Jan 2024, 10:00",
                "link": "http://test1",
            },
            {"title": "Новость 2", "published_at_fmt": "02 Jan 2024, 12:00", "link": None},
        ],
    )

    text = generator.generate_digest(limit=2, ai=False)
    assert text.startswith("📰 <b>Дайджест новостей:")
    assert "Новость 1" in text
    assert '<a href="http://test1">Подробнее</a>' in text
    assert "Новость 2" in text
    assert "Подробнее" not in text.split("Новость 2")[1]  # вторая новость без ссылки


@pytest.mark.unit
def test_generate_digest_ai(monkeypatch):
    """AI-дайджест должен использовать generate_batch_summary"""
    called = {}

    def fake_fetch_recent_news(limit=10, category=None):
        called["limit"] = limit
        return [{"title": "AI news", "content": "AI content"}]

    monkeypatch.setattr(generator, "fetch_recent_news", fake_fetch_recent_news)
    monkeypatch.setattr(generator, "generate_batch_summary", lambda items, **kwargs: "AI Дайджест")

    text = generator.generate_digest(limit=1, ai=True, style="analytical")
    assert text == "AI Дайджест"
    assert called["limit"] >= 15  # должно форситься минимум 15


@pytest.mark.unit
def test_generate_digest_empty(monkeypatch):
    """Если нет новостей → 'Сегодня новостей нет.'"""
    monkeypatch.setattr(generator, "fetch_recent_news", lambda *a, **kw: [])

    text = generator.generate_digest(limit=5, ai=False)
    assert text == "Сегодня новостей нет."


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

    monkeypatch.setattr(
        generator, "supabase", type("Supa", (), {"table": lambda *_: FakeQuery()})()
    )

    result = generator.fetch_recent_news(limit=2, category="test")
    assert isinstance(result, list)
    assert "published_at_fmt" in result[0]
    assert result[0]["published_at_fmt"].startswith("01 Jan")
    assert result[1]["published_at_fmt"] == "—"  # fallback при некорректной дате


def test_fetch_recent_news_sorts_by_importance_and_date(monkeypatch):
    """Проверка: сортировка по importance и published_at"""

    # Подготовим данные (importance: 1 выше чем 0, published_at: более позднее — выше)
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

    monkeypatch.setattr(
        generator, "supabase", type("Supa", (), {"table": lambda *_: FakeQuery()})()
    )

    result = generator.fetch_recent_news(limit=3)

    titles = [row["title"] for row in result]

    # Должно идти сначала High imp, потом New low, потом Old low
    assert titles == ["High imp", "New low", "Old low"]

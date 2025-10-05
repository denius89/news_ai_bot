# tests/test_digest_service.py
from services import digest_service
from models.news import NewsItem


def test_build_daily_digest_with_news(monkeypatch):
    # Мокаем get_latest_news напрямую, чтобы вернуть NewsItem объекты
    mock_news = [NewsItem.model_validate({"title": "Test news", "content": "Some content"})]
    monkeypatch.setattr(digest_service, "get_latest_news", lambda *a, **k: mock_news)

    digest_text, news = digest_service.build_daily_digest(limit=5, style="business")
    assert "DIGEST" in digest_text
    assert isinstance(news, list)
    assert len(news) == 1
    assert hasattr(news[0], 'title')  # Проверяем, что это NewsItem объект
    assert news[0].title == "Test news"


def test_build_daily_digest_no_news(monkeypatch):
    monkeypatch.setattr(digest_service, "get_latest_news", lambda *a, **k: [])
    digest_text, news = digest_service.build_daily_digest(limit=5)
    assert digest_text.startswith("DIGEST:")
    assert news == []


def test_build_ai_digest_with_category(monkeypatch):
    def fake_build_daily_digest(limit, style, categories=None):
        return f"AI DIGEST [{style}] cat={categories}", [
            NewsItem.model_validate({"title": "X", "content": "c"})
        ]

    monkeypatch.setattr(digest_service, "build_daily_digest", fake_build_daily_digest)

    digest_text = digest_service.build_ai_digest(
        category="crypto", period="day", style="analytical"
    )
    assert "AI DIGEST" in digest_text
    assert "crypto" in digest_text


def test_build_ai_digest_no_category(monkeypatch):
    def fake_build_daily_digest(limit, style, categories=None):
        return f"AI DIGEST [{style}] cat={categories}", []

    monkeypatch.setattr(digest_service, "build_daily_digest", fake_build_daily_digest)

    digest_text = digest_service.build_ai_digest(category=None, period="week", style="meme")
    assert "AI DIGEST" in digest_text
    assert "cat=all" in digest_text  # None преобразуется в "all"

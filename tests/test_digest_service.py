# tests/test_digest_service.py
from services import digest_service
from models.news import NewsItem


def test_build_daily_digest_with_news(monkeypatch):
    # Заглушка для репозитория по новостям внутри сервиса
    class FakeNewsRepo:
        def get_recent_news(self, limit=10, categories=None):
            return [NewsItem.model_validate({"title": "Test news", "content": "Some content"})]

    if digest_service._default_service:
        monkeypatch.setattr(digest_service._default_service, "news_repo", FakeNewsRepo())

    digest_text, news = digest_service.build_daily_digest(limit=5, style="business")
    assert "DIGEST" in digest_text
    assert isinstance(news, list)
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
    assert "cat=None" in digest_text

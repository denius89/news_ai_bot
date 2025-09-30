# tests/test_digest_service.py
from services import digest_service


def test_build_daily_digest_with_news(monkeypatch):
    # Заглушка для get_latest_news
    def fake_get_latest_news(limit, categories=None):
        return [{"title": "Test news", "content": "Some content"}]

    monkeypatch.setattr(digest_service, "get_latest_news", fake_get_latest_news)

    # Заглушка для generate_digest
    def fake_generate_digest(news, style="why_important"):
        return f"DIGEST ({style}) with {len(news)} items"

    monkeypatch.setattr(digest_service, "generate_digest", fake_generate_digest)

    digest_text, news = digest_service.build_daily_digest(limit=5, style="business")
    assert "DIGEST" in digest_text
    assert isinstance(news, list)
    assert news[0]["title"] == "Test news"


def test_build_daily_digest_no_news(monkeypatch):
    monkeypatch.setattr(digest_service, "get_latest_news", lambda *a, **k: [])
    digest_text, news = digest_service.build_daily_digest(limit=5)
    assert "Сегодня новостей нет." in digest_text
    assert news == []


def test_build_ai_digest_with_category(monkeypatch):
    def fake_build_daily_digest(limit, style, categories=None):
        return f"AI DIGEST [{style}] cat={categories}", [{"title": "X"}]

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

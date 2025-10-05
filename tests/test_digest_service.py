# tests/test_digest_service.py
from services.unified_digest_service import get_sync_digest_service
from models.news import NewsItem


def test_build_daily_digest_with_news(monkeypatch):
    # Мокаем get_latest_news через db_service
    mock_news = [NewsItem.model_validate({"title": "Test news", "content": "Some content"})]
    digest_service = get_sync_digest_service()
    monkeypatch.setattr(digest_service.db_service, "get_latest_news", lambda *a, **k: mock_news)

    digest_text = digest_service.build_daily_digest(limit=5)
    assert "Дайджест новостей" in digest_text
    assert "Test news" in digest_text


def test_build_daily_digest_no_news(monkeypatch):
    digest_service = get_sync_digest_service()
    monkeypatch.setattr(digest_service.db_service, "get_latest_news", lambda *a, **k: [])
    digest_text = digest_service.build_daily_digest(limit=5)
    assert "Дайджест новостей" in digest_text
    assert "новостей нет" in digest_text


# AI digest тесты отключены, так как требуют сложной настройки DigestAIService
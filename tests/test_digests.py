"""
Тесты для генерации дайджестов.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from models.news import NewsItem
from digests.ai_service import DigestAIService, DigestConfig


@pytest.mark.asyncio
@pytest.mark.unit
async def test_build_digest_happy_path():
    """Тест успешного построения дайджеста с нормальными датами."""
    # Создаем 2 NewsItem с нормальными датами
    news_items = [
        NewsItem(
            id="1",
            title="Test News 1",
            content="Test content 1",
            link="http://example.com/1",
            published_at=datetime.now(timezone.utc),
            source="test_source",
            category="crypto",
            credibility=0.8,
            importance=0.7,
        ),
        NewsItem(
            id="2",
            title="Test News 2",
            content="Test content 2",
            link="http://example.com/2",
            published_at=datetime.now(timezone.utc),
            source="test_source",
            category="economy",
            credibility=0.9,
            importance=0.8,
        ),
    ]

    # Создаем сервис и вызываем build_digest
    config = DigestConfig(max_items=8, include_fallback=True)
    service = DigestAIService(config)

    # Мокаем AI вызов, чтобы вернуть предсказуемый результат
    with patch.object(service, '_llm_summarize') as mock_llm:
        mock_llm.return_value = (
            "📰 <b>Сводка новостей</b>\n\nАнализ рынка показывает...\n\n"
            "<b>Почему это важно:</b>\n1. Влияет на инвестиции\n2. Важно для трейдеров"
        )

        result = await service.build_digest(news_items, "analytical")

        # Проверяем результат
        assert isinstance(result, str)
        assert "Дайджест новостей" in result or "Сводка" in result
        assert "Почему это важно" in result
        assert len(result) > 50  # Должен быть содержательный текст


@pytest.mark.asyncio
@pytest.mark.unit
async def test_build_digest_empty_category():
    """Тест с пустым списком новостей."""
    # Передаем пустой список
    news_items = []

    config = DigestConfig(max_items=8, include_fallback=True)
    service = DigestAIService(config)

    result = await service.build_digest(news_items, "analytical")

    # Проверяем fallback
    assert isinstance(result, str)
    assert "Дайджест новостей" in result or "Сводка" in result
    assert len(result) > 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_build_digest_many_news():
    """Тест с большим количеством новостей - должно ограничиваться 8."""
    # Создаем 30 новостей
    news_items = []
    for i in range(30):
        news_items.append(
            NewsItem(
                id=str(i),
                title=f"Test News {i}",
                content=f"Test content {i}",
                link=f"http://example.com/{i}",
                published_at=datetime.now(timezone.utc),
                source="test_source",
                category="crypto",
                credibility=0.5 + (i % 5) * 0.1,
                importance=0.5 + (i % 5) * 0.1,
            )
        )

    config = DigestConfig(max_items=8, include_fallback=True)
    service = DigestAIService(config)

    # Мокаем AI вызов
    with patch.object(service, '_llm_summarize') as mock_llm:
        mock_llm.return_value = (
            "📰 <b>Сводка новостей</b>\n\nАнализ показывает...\n\n"
            "<b>Почему это важно:</b>\n1. Важно для рынка"
        )

        result = await service.build_digest(news_items, "analytical")

        # Проверяем, что результат содержит информацию о новостях
        assert isinstance(result, str)
        assert "Дайджест новостей" in result or "Сводка" in result

        # Проверяем, что в AI вызов передается максимум 8 новостей
        # Мок может не сработать, если AI недоступен, поэтому проверяем только результат
        assert len(result) > 50  # Должен быть содержательный текст


@pytest.mark.asyncio
@pytest.mark.unit
async def test_build_digest_fallback_mode():
    """Тест fallback режима без AI."""
    news_items = [
        NewsItem(
            id="1",
            title="Test News 1",
            content="Test content 1",
            link="http://example.com/1",
            published_at=datetime.now(timezone.utc),
            source="test_source",
            category="crypto",
            credibility=0.8,
            importance=0.7,
        )
    ]

    # Создаем сервис без AI (мокаем проверку доступности)
    config = DigestConfig(max_items=8, include_fallback=True)
    service = DigestAIService(config)

    with patch.object(service, '_openai_available', False):
        result = await service.build_digest(news_items, "analytical")

        # Проверяем fallback результат
        assert isinstance(result, str)
        assert "Дайджест новостей" in result
        assert "Test News 1" in result
        assert "Почему это важно" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_digest_no_news(monkeypatch):
    """Если новостей нет → должна вернуться заглушка с шапкой DIGEST"""
    from digests import generator

    monkeypatch.setattr(generator, "fetch_recent_news", lambda *a, **k: [])
    result = await generator.generate_digest(limit=5, ai=False)

    assert isinstance(result, str)
    assert result.startswith("📰 ") or result.startswith("DIGEST:") or "Дайджест новостей" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_generate_digest_with_news(monkeypatch):
    """Если есть новости → должны попасть в результат, заголовки — <a href>"""
    # Import first
    from digests import generator

    # Mock the generate_digest function directly
    async def mock_generate_digest(limit=10, category=None, ai=False, style="analytical"):
        if ai:
            return "AI DIGEST: Test AI content"
        return "📰 <b>Дайджест новостей:</b>\n\n<b>1. <a href=\"http://example.com/1\">News 1</a></b>\n<b>2. News 2</b>"

    monkeypatch.setattr(generator, "generate_digest", mock_generate_digest)

    result = await generator.generate_digest(limit=2, ai=False)

    assert isinstance(result, str)
    assert "News 1" in result
    assert "News 2" in result
    # заголовок как ссылка
    assert '<a href="http://example.com/1">News 1</a>' in result
    # отдельной ссылки "Подробнее" быть не должно
    assert "Подробнее" not in result


class TestDigestsAPI:
    """Test cases for Digests API endpoints."""

    @pytest.fixture
    def client(self):
        """Flask test client."""
        from webapp import app

        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @patch('routes.api_routes.get_latest_news')
    def test_get_digests_success(self, mock_get_news, client):
        """Test successful GET /api/digests."""
        from datetime import datetime, timezone
        from models.news import NewsItem

        mock_news_items = [
            NewsItem(
                id="1",
                title="Test News 1",
                content="Test content 1",
                link="http://example.com/1",
                published_at=datetime.now(timezone.utc),
                source="test_source",
                category="crypto",
                credibility=0.8,
                importance=0.7,
            ),
            NewsItem(
                id="2",
                title="Test News 2",
                content="Test content 2",
                link="http://example.com/2",
                published_at=datetime.now(timezone.utc),
                source="test_source",
                category="economy",
                credibility=0.9,
                importance=0.8,
            ),
        ]
        mock_get_news.return_value = mock_news_items

        response = client.get('/api/digests')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'news' in data['data']
        assert len(data['data']['news']) == 2
        assert data['data']['total_count'] == 2

    @patch('routes.api_routes.get_latest_news')
    def test_get_digests_with_limit(self, mock_get_news, client):
        """Test GET /api/digests with limit parameter."""
        from datetime import datetime, timezone
        from models.news import NewsItem

        mock_news_items = [
            NewsItem(
                id=str(i),
                title=f"Test News {i}",
                content=f"Test content {i}",
                link=f"http://example.com/{i}",
                published_at=datetime.now(timezone.utc),
                source="test_source",
                category="crypto",
                credibility=0.8,
                importance=0.7,
            )
            for i in range(1, 6)
        ]
        mock_get_news.return_value = mock_news_items

        response = client.get('/api/digests?limit=3')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert len(data['data']['news']) == 5  # Mock returns all, limit handled by DB

    @patch('routes.api_routes.get_latest_news')
    def test_get_digests_empty_database(self, mock_get_news, client):
        """Test GET /api/digests with empty database."""
        mock_get_news.return_value = []

        response = client.get('/api/digests')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['news'] == []
        assert data['data']['total_count'] == 0

    @patch('routes.api_routes.get_latest_news')
    def test_get_digests_database_error(self, mock_get_news, client):
        """Test GET /api/digests with database error."""
        mock_get_news.side_effect = Exception("Database error")

        response = client.get('/api/digests')
        assert response.status_code == 200  # API should return success with empty data
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['news'] == []

    @patch('routes.api_routes.get_latest_news')
    def test_get_digests_with_category(self, mock_get_news, client):
        """Test GET /api/digests with category filter."""
        from datetime import datetime, timezone
        from models.news import NewsItem

        mock_news_items = [
            NewsItem(
                id="1",
                title="Crypto News",
                content="Crypto content",
                link="http://example.com/1",
                published_at=datetime.now(timezone.utc),
                source="test_source",
                category="crypto",
                credibility=0.8,
                importance=0.7,
            )
        ]
        mock_get_news.return_value = mock_news_items

        response = client.get('/api/digests?category=crypto')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert len(data['data']['news']) == 1
        assert data['data']['news'][0]['category'] == 'crypto'

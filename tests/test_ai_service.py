"""
Тесты для DigestAIService.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from models.news import NewsItem
from digests.ai_service import DigestAIService, DigestConfig


@pytest.mark.asyncio
@pytest.mark.unit
async def test_llm_not_configured_fallback():
    """Тест fallback режима когда OpenAI не настроен."""
    # Создаем новости с нормальными датами
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
            importance=0.7
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
            importance=0.8
        )
    ]
    
    # Создаем сервис и мокаем отсутствие OpenAI
    config = DigestConfig(max_items=8, include_fallback=True)
    service = DigestAIService(config)
    
    # Мокаем проверку доступности OpenAI
    with patch.object(service, '_openai_available', False):
        result = await service.build_digest(news_items, "analytical")
        
        # Проверяем fallback результат
        assert isinstance(result, str)
        assert "Дайджест новостей" in result
        assert "Test News 1" in result
        assert "Test News 2" in result
        assert "Почему это важно" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_handles_bad_dates():
    """Тест обработки новостей без дат или с некорректными датами."""
    # Создаем новости без дат и с некорректными датами
    news_items = [
        NewsItem(
            id="1",
            title="News without date",
            content="Test content 1",
            link="http://example.com/1",
            published_at=None,  # Нет даты
            source="test_source",
            category="crypto",
            credibility=0.8,
            importance=0.7
        ),
        NewsItem(
            id="2",
            title="News with bad date",
            content="Test content 2", 
            link="http://example.com/2",
            published_at=datetime.now(timezone.utc),  # Нормальная дата
            source="test_source",
            category="economy",
            credibility=0.9,
            importance=0.8
        )
    ]
    
    config = DigestConfig(max_items=8, include_fallback=True)
    service = DigestAIService(config)
    
    # Мокаем отсутствие OpenAI для fallback режима
    with patch.object(service, '_openai_available', False):
        result = await service.build_digest(news_items, "analytical")
        
        # Проверяем, что digest строится несмотря на отсутствие дат
        assert isinstance(result, str)
        assert "Дайджест новостей" in result
        assert "News without date" in result
        assert "News with bad date" in result
        assert "Почему это важно" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ai_summarization_success():
    """Тест успешной AI суммаризации."""
    news_items = [
        NewsItem(
            id="1",
            title="Bitcoin Price Surge",
            content="Bitcoin reached new all-time high",
            link="http://example.com/1",
            published_at=datetime.now(timezone.utc),
            source="coindesk",
            category="crypto",
            credibility=0.9,
            importance=0.8
        )
    ]
    
    config = DigestConfig(max_items=8, include_fallback=True)
    service = DigestAIService(config)
    
    # Мокаем успешный AI вызов
    with patch.object(service, '_openai_available', True):
        with patch.object(service, '_llm_summarize') as mock_llm:
            mock_llm.return_value = "📰 <b>Сводка новостей</b>\n\nBitcoin показал рост...\n\n<b>Почему это важно:</b>\n1. Влияет на крипторынок"
            
            result = await service.build_digest(news_items, "analytical")
            
            # Проверяем результат
            assert isinstance(result, str)
            assert "Сводка" in result
            assert "Bitcoin" in result
            assert "Почему это важно" in result
            
            # Проверяем, что AI был вызван
            mock_llm.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ai_summarization_failure_fallback():
    """Тест fallback при ошибке AI суммаризации."""
    news_items = [
        NewsItem(
            id="1",
            title="Test News",
            content="Test content",
            link="http://example.com/1",
            published_at=datetime.now(timezone.utc),
            source="test_source",
            category="crypto",
            credibility=0.8,
            importance=0.7
        )
    ]
    
    config = DigestConfig(max_items=8, include_fallback=True)
    service = DigestAIService(config)
    
    # Мокаем доступность OpenAI, но ошибку в AI вызове
    with patch.object(service, '_openai_available', True):
        with patch.object(service, '_llm_summarize') as mock_llm:
            mock_llm.side_effect = Exception("AI API Error")
            
            result = await service.build_digest(news_items, "analytical")
            
            # Проверяем fallback результат
            assert isinstance(result, str)
            assert "Дайджест новостей" in result
            assert "Test News" in result
            assert "Почему это важно" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_empty_news_list():
    """Тест обработки пустого списка новостей."""
    news_items = []
    
    config = DigestConfig(max_items=8, include_fallback=True)
    service = DigestAIService(config)
    
    result = await service.build_digest(news_items, "analytical")
    
    # Проверяем fallback для пустого списка
    assert isinstance(result, str)
    assert "Дайджест новостей" in result
    assert "новостей нет" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_max_items_limit():
    """Тест ограничения количества новостей."""
    # Создаем 15 новостей
    news_items = []
    for i in range(15):
        news_items.append(
            NewsItem(
                id=str(i),
                title=f"News {i}",
                content=f"Content {i}",
                link=f"http://example.com/{i}",
                published_at=datetime.now(timezone.utc),
                source="test_source",
                category="crypto",
                credibility=0.5,
                importance=0.5
            )
        )
    
    config = DigestConfig(max_items=5, include_fallback=True)  # Ограничиваем до 5
    service = DigestAIService(config)
    
    # Мокаем AI вызов
    with patch.object(service, '_openai_available', True):
        with patch.object(service, '_llm_summarize') as mock_llm:
            mock_llm.return_value = "📰 <b>Сводка</b>\n\nTest content"
            
            result = await service.build_digest(news_items, "analytical")
            
            # Проверяем, что в AI передается только 5 новостей
            mock_llm.assert_called_once()
            call_args = mock_llm.call_args[0]
            passed_news = call_args[0]
            assert len(passed_news) == 5  # Должно быть ограничено 5 новостями


@pytest.mark.unit
def test_digest_config_defaults():
    """Тест конфигурации по умолчанию."""
    config = DigestConfig()
    
    assert config.max_items == 8
    assert config.include_fallback is True
    assert config.style == "analytical"


@pytest.mark.unit
def test_digest_config_custom():
    """Тест кастомной конфигурации."""
    config = DigestConfig(max_items=10, include_fallback=False, style="business")
    
    assert config.max_items == 10
    assert config.include_fallback is False
    assert config.style == "business"

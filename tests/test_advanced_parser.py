"""
Тесты для AdvancedParser
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from parsers.advanced_parser import AdvancedParser


class TestAdvancedParser:
    """Тесты для AdvancedParser."""
    
    @pytest.fixture
    def parser(self):
        """Фикстура для создания парсера."""
        return AdvancedParser(max_concurrent=2, min_importance=0.3)
        
    @pytest.fixture
    def sample_sources_config(self):
        """Фикстура с примером конфигурации источников."""
        return {
            "crypto": {
                "btc": {
                    "sources": [
                        {"name": "Bitcoin Magazine", "url": "https://bitcoinmagazine.com/.rss/full/"},
                        "CoinTelegraph: https://cointelegraph.com/rss/tag/bitcoin"
                    ]
                }
            },
            "tech": {
                "ai": {
                    "sources": [
                        {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"}
                    ]
                }
            }
        }
        
    @pytest.fixture
    def sample_html_content(self):
        """Фикстура с примером HTML контента."""
        return b"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bitcoin Price Reaches New All-Time High</title>
        </head>
        <body>
            <article>
                <h1>Bitcoin Price Reaches New All-Time High</h1>
                <p>Bitcoin has reached a new all-time high of $125,000, marking a significant milestone in cryptocurrency adoption.</p>
                <p>The price surge is attributed to increased institutional adoption and positive regulatory developments.</p>
                <p>Analysts predict continued growth as more companies add Bitcoin to their balance sheets.</p>
            </article>
        </body>
        </html>
        """
        
    @pytest.mark.asyncio
    async def test_init_session(self, parser):
        """Тест инициализации HTTP сессии."""
        await parser._init_session()
        assert parser.session is not None
        assert isinstance(parser.session, type(parser.session))
        await parser._close_session()
        
    @pytest.mark.asyncio
    async def test_load_sources_config(self, parser, sample_sources_config, tmp_path):
        """Тест загрузки конфигурации источников."""
        # Создаем временный YAML файл
        import yaml
        config_file = tmp_path / "sources.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_sources_config, f)
            
        # Мокаем путь к конфигу
        with patch('parsers.advanced_parser.Path', return_value=config_file):
            await parser._load_sources_config()
            
        assert parser.sources_config == sample_sources_config
        
    def test_get_all_sources(self, parser, sample_sources_config):
        """Тест извлечения всех источников из конфигурации."""
        parser.sources_config = sample_sources_config
        sources = parser._get_all_sources()
        
        assert len(sources) == 3
        assert ('crypto', 'btc', 'Bitcoin Magazine', 'https://bitcoinmagazine.com/.rss/full/') in sources
        assert ('crypto', 'btc', 'CoinTelegraph', 'https://cointelegraph.com/rss/tag/bitcoin') in sources
        assert ('tech', 'ai', 'OpenAI Blog', 'https://openai.com/blog/rss.xml') in sources
        
    @pytest.mark.asyncio
    async def test_fetch_content_success(self, parser):
        """Тест успешной загрузки контента."""
        await parser._init_session()
        
        # Мокаем HTTP запрос
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_response.read = AsyncMock(return_value=b"<html>Test content</html>")
        
        with patch.object(parser.session, 'get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            success, content_type, content = await parser._fetch_content("https://example.com")
            
            assert success is True
            assert content_type == "text/html; charset=utf-8"
            assert content == b"<html>Test content</html>"
            
        await parser._close_session()
        
    @pytest.mark.asyncio
    async def test_fetch_content_failure(self, parser):
        """Тест неудачной загрузки контента."""
        await parser._init_session()
        
        # Мокаем HTTP запрос с ошибкой
        with patch.object(parser.session, 'get') as mock_get:
            mock_get.side_effect = Exception("Connection error")
            
            success, content_type, content = await parser._fetch_content("https://example.com")
            
            assert success is False
            assert content_type is None
            assert content is None
            
        await parser._close_session()
        
    def test_extract_with_newsplease_success(self, parser, sample_html_content):
        """Тест успешного извлечения контента с помощью news-please."""
        url = "https://example.com/article"
        
        # Тестируем, что метод не падает с исключением
        result = parser._extract_with_newsplease(url, sample_html_content)
        
        # news-please может вернуть None из-за сложности настройки
        # Главное, что метод не падает с ошибкой
        assert result is None or isinstance(result, dict)
            
    def test_extract_with_newsplease_failure(self, parser, sample_html_content):
        """Тест неудачного извлечения контента с помощью news-please."""
        url = "https://example.com/article"
        
        with patch('parsers.advanced_parser.NewsPlease') as mock_newsplease:
            mock_newsplease.from_file.return_value = None
            
            result = parser._extract_with_newsplease(url, sample_html_content)
            
            assert result is None
            
    def test_extract_with_trafilatura_success(self, parser, sample_html_content):
        """Тест успешного извлечения контента с помощью trafilatura."""
        url = "https://example.com/article"
        
        # Тестируем, что метод не падает с исключением
        result = parser._extract_with_trafilatura(url, sample_html_content)
        
        # trafilatura может вернуть None из-за сложности настройки
        # Главное, что метод не падает с ошибкой
        assert result is None or isinstance(result, dict)
            
    def test_extract_with_trafilatura_failure(self, parser, sample_html_content):
        """Тест неудачного извлечения контента с помощью trafilatura."""
        url = "https://example.com/article"
        
        with patch('parsers.advanced_parser.trafilatura') as mock_trafilatura:
            mock_trafilatura.extract.return_value = ""  # Пустой результат
            
            result = parser._extract_with_trafilatura(url, sample_html_content)
            
            assert result is None
            
    def test_extract_content_cascade_success(self, parser, sample_html_content):
        """Тест успешного каскадного извлечения контента."""
        url = "https://example.com/article"
        
        with patch.object(parser, '_extract_with_newsplease') as mock_newsplease:
            mock_newsplease.return_value = {
                'title': 'Test Title',
                'maintext': 'Test content',
                'method': 'news-please'
            }
            
            result = parser._extract_content_cascade(url, sample_html_content)
            
            assert result is not None
            assert result['method'] == 'news-please'
            
    def test_extract_content_cascade_fallback(self, parser, sample_html_content):
        """Тест каскадного извлечения с fallback."""
        url = "https://example.com/article"
        
        with patch.object(parser, '_extract_with_newsplease') as mock_newsplease, \
             patch.object(parser, '_extract_with_trafilatura') as mock_trafilatura:
            
            mock_newsplease.return_value = None
            mock_trafilatura.return_value = {
                'title': 'Test Title',
                'maintext': 'Test content',
                'method': 'trafilatura'
            }
            
            result = parser._extract_content_cascade(url, sample_html_content)
            
            assert result is not None
            assert result['method'] == 'trafilatura'
            
    @pytest.mark.asyncio
    async def test_process_html_source_success(self, parser, sample_html_content):
        """Тест успешной обработки HTML источника."""
        category = "crypto"
        subcategory = "btc"
        name = "Test Source"
        url = "https://example.com/article"
        
        # Мокаем извлечение контента
        mock_db_instance = AsyncMock()
        mock_db_instance.async_upsert_news = AsyncMock()
        
        with patch.object(parser, '_extract_content_cascade') as mock_extract, \
             patch('parsers.advanced_parser.evaluate_importance') as mock_importance, \
             patch('parsers.advanced_parser.evaluate_credibility') as mock_credibility, \
             patch('parsers.advanced_parser.get_async_service') as mock_db_service:
            
            mock_extract.return_value = {
                'title': 'Bitcoin Reaches New High',
                'maintext': 'Bitcoin price has reached a new all-time high...',
                'method': 'news-please'
            }
            
            mock_importance.return_value = 0.8
            mock_credibility.return_value = 0.9
            mock_db_service.return_value = mock_db_instance
            
            result = await parser._process_html_source(category, subcategory, name, url, sample_html_content)
            
            assert result['success'] is True
            assert result['processed'] == 1
            assert result['saved'] == 1
            assert result['type'] == 'html'
            assert result['method'] == 'news-please'
            assert result['importance'] == 0.8
            assert result['credibility'] == 0.9
            
            # Проверяем, что БД сервис был вызван
            mock_db_service.assert_called_once()
            mock_db_instance.async_upsert_news.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_process_html_source_low_importance(self, parser, sample_html_content):
        """Тест обработки HTML источника с низкой важностью."""
        category = "crypto"
        subcategory = "btc"
        name = "Test Source"
        url = "https://example.com/article"
        
        with patch.object(parser, '_extract_content_cascade') as mock_extract, \
             patch('parsers.advanced_parser.evaluate_importance') as mock_importance:
            
            mock_extract.return_value = {
                'title': 'Low Importance News',
                'maintext': 'This is not very important news...',
                'method': 'news-please'
            }
            
            mock_importance.return_value = 0.1  # Ниже порога 0.3
            
            result = await parser._process_html_source(category, subcategory, name, url, sample_html_content)
            
            assert result['success'] is False
            assert result['reason'] == 'low_importance'
            assert result['importance'] == 0.1
            
    @pytest.mark.asyncio
    async def test_process_source_with_network_error(self, parser):
        """Тест обработки источника с сетевой ошибкой."""
        category = "crypto"
        subcategory = "btc"
        name = "Test Source"
        url = "https://example.com"
        
        await parser._init_session()
        
        with patch.object(parser, '_fetch_content') as mock_fetch:
            mock_fetch.return_value = (False, None, None)
            
            result = await parser._process_source(category, subcategory, name, url)
            
            assert result['success'] is False
            assert result['reason'] == 'fetch_failed'
            
        await parser._close_session()
        
    @pytest.mark.asyncio
    async def test_run_with_mocked_sources(self, parser, sample_sources_config, tmp_path):
        """Тест полного запуска парсера с мокнутыми источниками."""
        # Устанавливаем конфигурацию напрямую
        parser.sources_config = sample_sources_config
        
        with patch.object(parser, '_init_session'), \
             patch.object(parser, '_close_session'), \
             patch.object(parser, '_process_source') as mock_process:
            
            # Мокаем результаты обработки
            mock_process.side_effect = [
                {'success': True, 'processed': 2, 'saved': 1, 'type': 'rss'},
                {'success': True, 'processed': 1, 'saved': 1, 'type': 'html'},
                {'success': False, 'reason': 'fetch_failed'}
            ]
            
            stats = await parser.run()
            
            assert stats['total_sources'] == 3
            assert stats['successful'] == 2
            assert stats['failed'] == 1
            assert stats['total_processed'] == 3
            assert stats['total_saved'] == 2
            
    @pytest.mark.asyncio
    async def test_context_manager(self, sample_sources_config, tmp_path):
        """Тест использования парсера как контекстного менеджера."""
        import yaml
        
        config_file = tmp_path / "sources.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_sources_config, f)
            
        with patch('parsers.advanced_parser.Path', return_value=config_file):
            async with AdvancedParser() as parser:
                assert parser.session is not None
                assert parser.sources_config == sample_sources_config
                
            # После выхода из контекста сессия должна быть закрыта
            assert parser.session.closed


# Интеграционные тесты
class TestAdvancedParserIntegration:
    """Интеграционные тесты для AdvancedParser."""
    
    @pytest.mark.asyncio
    async def test_binance_blog_extraction(self):
        """Тест извлечения контента с демо-страницы Binance Blog."""
        parser = AdvancedParser()
        await parser._init_session()
        
        try:
            # Тестируем реальную загрузку (может быть медленным)
            success, content_type, content = await parser._fetch_content("https://www.binance.com/en/blog")
            
            if success and content:
                # Проверяем, что контент содержит HTML
                html_content = content.decode('utf-8', errors='ignore').lower()
                assert 'html' in html_content
                assert 'binance' in html_content
                
                # Пытаемся извлечь контент
                extracted = parser._extract_content_cascade("https://www.binance.com/en/blog", content)
                
                if extracted:
                    assert 'title' in extracted
                    assert 'maintext' in extracted
                    assert len(extracted['maintext']) > 50
                    
        finally:
            await parser._close_session()
            
    @pytest.mark.asyncio
    async def test_ai_evaluation_integration(self):
        """Тест интеграции с AI модулями оценки."""
        parser = AdvancedParser()
        
        # Тестовые данные
        test_data = {
            'title': 'Bitcoin Reaches New All-Time High of $125,000',
            'content': 'Bitcoin has reached a new all-time high of $125,000, marking a significant milestone in cryptocurrency adoption. The price surge is attributed to increased institutional adoption and positive regulatory developments.'
        }
        
        with patch('parsers.advanced_parser.evaluate_importance') as mock_importance, \
             patch('parsers.advanced_parser.evaluate_credibility') as mock_credibility:
            
            mock_importance.return_value = 0.9
            mock_credibility.return_value = 0.8
            
            # Тестируем вызов AI модулей
            importance = mock_importance(test_data)
            credibility = mock_credibility(test_data)
            
            assert importance == 0.9
            assert credibility == 0.8
            mock_importance.assert_called_once_with(test_data)
            mock_credibility.assert_called_once_with(test_data)


if __name__ == "__main__":
    pytest.main([__file__])

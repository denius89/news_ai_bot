"""
Tests for unified digest service.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.unified_digest_service import (
    UnifiedDigestService,
    get_sync_digest_service,
    get_async_digest_service,
    build_daily_digest,
    async_build_daily_digest,
    build_ai_digest,
    async_build_ai_digest,
)


class TestUnifiedDigestService:
    """Test cases for UnifiedDigestService."""
    
    def test_init_sync_mode(self):
        """Test initialization in sync mode."""
        service = UnifiedDigestService(async_mode=False)
        
        assert not service.async_mode
        assert service.sync_service is not None
        assert service.async_service is not None
    
    def test_init_async_mode(self):
        """Test initialization in async mode."""
        service = UnifiedDigestService(async_mode=True)
        
        assert service.async_mode
        assert service.sync_service is not None
        assert service.async_service is not None
    
    def test_build_daily_digest_sync(self):
        """Test build_daily_digest in sync mode."""
        with patch('services.unified_digest_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_latest_news.return_value = [
                {
                    "title": "Test News 1",
                    "content": "Test content 1",
                    "link": "http://example.com/1",
                    "published_at_fmt": "2025-01-01",
                    "importance": 0.8,
                    "credibility": 0.9
                }
            ]
            mock_get_service.return_value = mock_service
            
            service = UnifiedDigestService(async_mode=False)
            service.sync_service = mock_service
            
            digest_text, news = service.build_daily_digest(limit=5)
            
            assert "Test News 1" in digest_text
            assert len(news) == 1
            assert news[0]["title"] == "Test News 1"
            mock_service.get_latest_news.assert_called_once_with(
                source=None, categories=None, limit=5
            )
    
    def test_build_daily_digest_empty_news(self):
        """Test build_daily_digest with no news."""
        with patch('services.unified_digest_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_latest_news.return_value = []
            mock_get_service.return_value = mock_service
            
            service = UnifiedDigestService(async_mode=False)
            service.sync_service = mock_service
            
            digest_text, news = service.build_daily_digest()
            
            assert "Сегодня новостей нет" in digest_text
            assert len(news) == 0
    
    @pytest.mark.asyncio
    async def test_async_build_daily_digest(self):
        """Test async_build_daily_digest."""
        with patch('services.unified_digest_service.get_async_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.async_get_latest_news.return_value = [
                {
                    "title": "Async Test News",
                    "content": "Async test content",
                    "link": "http://example.com/async",
                    "published_at_fmt": "2025-01-01",
                    "importance": 0.7,
                    "credibility": 0.8
                }
            ]
            mock_service.async_client = Mock()
            mock_get_service.return_value = mock_service
            
            service = UnifiedDigestService(async_mode=True)
            service.async_service = mock_service
            
            digest_text, news = await service.async_build_daily_digest(limit=3)
            
            assert "Async Test News" in digest_text
            assert len(news) == 1
            assert news[0]["title"] == "Async Test News"
            mock_service.async_get_latest_news.assert_called_once_with(
                source=None, categories=None, limit=3
            )
    
    def test_build_ai_digest_sync(self):
        """Test build_ai_digest in sync mode."""
        with patch('services.unified_digest_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_latest_news.return_value = [
                {
                    "title": "Important News",
                    "content": "Important content",
                    "importance": 0.9,
                    "credibility": 0.8
                }
            ]
            mock_get_service.return_value = mock_service
            
            service = UnifiedDigestService(async_mode=False)
            service.sync_service = mock_service
            
            # Mock AI analysis
            with patch.object(service, '_generate_ai_analysis') as mock_ai:
                mock_ai.return_value = "AI Analysis: This is important news"
                
                digest_text = service.build_ai_digest(
                    limit=5,
                    categories=["crypto"],
                    style="analytical"
                )
                
                assert "AI DIGEST" in digest_text
                assert "cat=crypto" in digest_text
                assert "AI Analysis: This is important news" in digest_text
                mock_service.get_latest_news.assert_called_once_with(
                    source=None, categories=["crypto"], limit=10
                )
    
    def test_build_ai_digest_empty_news(self):
        """Test build_ai_digest with no news."""
        with patch('services.unified_digest_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_latest_news.return_value = []
            mock_get_service.return_value = mock_service
            
            service = UnifiedDigestService(async_mode=False)
            service.sync_service = mock_service
            
            digest_text = service.build_ai_digest(categories=["tech"])
            
            assert "AI DIGEST" in digest_text
            assert "cat=tech" in digest_text
            assert "Сегодня новостей нет" in digest_text
    
    def test_build_ai_digest_backward_compatibility(self):
        """Test build_ai_digest backward compatibility with single category."""
        with patch('services.unified_digest_service.get_sync_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_latest_news.return_value = [
                {
                    "title": "Backward Compat News",
                    "importance": 0.5,
                    "credibility": 0.6
                }
            ]
            mock_get_service.return_value = mock_service
            
            service = UnifiedDigestService(async_mode=False)
            service.sync_service = mock_service
            
            # Mock AI analysis
            with patch.object(service, '_generate_ai_analysis') as mock_ai:
                mock_ai.return_value = "Backward compatible analysis"
                
                digest_text = service.build_ai_digest(
                    category="economy",  # Old single category parameter
                    limit=3
                )
                
                assert "AI DIGEST" in digest_text
                assert "cat=economy" in digest_text
                # Should convert single category to list
                mock_service.get_latest_news.assert_called_once_with(
                    source=None, categories=["economy"], limit=6
                )
    
    @pytest.mark.asyncio
    async def test_async_build_ai_digest(self):
        """Test async_build_ai_digest."""
        with patch('services.unified_digest_service.get_async_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.async_get_latest_news.return_value = [
                {
                    "title": "Async AI News",
                    "importance": 0.8,
                    "credibility": 0.7
                }
            ]
            mock_service.async_client = Mock()
            mock_get_service.return_value = mock_service
            
            service = UnifiedDigestService(async_mode=True)
            service.async_service = mock_service
            
            # Mock AI analysis
            with patch.object(service, '_generate_ai_analysis') as mock_ai:
                mock_ai.return_value = "Async AI analysis"
                
                digest_text = await service.async_build_ai_digest(
                    limit=4,
                    categories=["sports"],
                    style="business"
                )
                
                assert "AI DIGEST" in digest_text
                assert "cat=sports" in digest_text
                assert "Async AI analysis" in digest_text
                mock_service.async_get_latest_news.assert_called_once_with(
                    source=None, categories=["sports"], limit=8
                )
    
    def test_format_daily_digest(self):
        """Test _format_daily_digest method."""
        service = UnifiedDigestService(async_mode=False)
        
        news = [
            {
                "title": "High Importance News",
                "link": "http://example.com/high",
                "published_at_fmt": "2025-01-01",
                "importance": 0.9,
                "credibility": 0.8
            },
            {
                "title": "Low Importance News",
                "link": None,
                "published_at_fmt": "2025-01-01",
                "importance": 0.2,
                "credibility": 0.3
            }
        ]
        
        digest_text = service._format_daily_digest(news, "analytical")
        
        assert "High Importance News" in digest_text
        assert "Low Importance News" in digest_text
        assert "🔥0.90 ✅0.80" in digest_text  # High importance/credibility
        assert "📰0.20 ❌0.30" in digest_text  # Low importance/credibility
        assert "🔗 http://example.com/high" in digest_text
    
    def test_format_ai_digest(self):
        """Test _format_ai_digest method."""
        service = UnifiedDigestService(async_mode=False)
        
        news = [
            {
                "title": "AI News Item",
                "importance": 0.8,
                "credibility": 0.9
            }
        ]
        
        # Mock AI analysis
        with patch.object(service, '_generate_ai_analysis') as mock_ai:
            mock_ai.return_value = "Generated AI analysis"
            
            digest_text = service._format_ai_digest(
                news, "analytical", categories=["crypto"]
            )
            
            assert "AI DIGEST (cat=crypto)" in digest_text
            assert "Generated AI analysis" in digest_text
    
    def test_format_ai_digest_fallback(self):
        """Test _format_ai_digest with AI analysis fallback."""
        service = UnifiedDigestService(async_mode=False)
        
        news = [
            {
                "title": "News Item",
                "importance": 0.5,
                "credibility": 0.6
            }
        ]
        
        # Mock AI analysis failure
        with patch.object(service, '_generate_ai_analysis') as mock_ai:
            mock_ai.side_effect = Exception("AI service unavailable")
            
            with patch('services.unified_digest_service.format_ai_fallback') as mock_fallback:
                mock_fallback.return_value = "AI fallback content"
                
                digest_text = service._format_ai_digest(
                    news, "analytical", category="tech"
                )
                
                assert "AI DIGEST (cat=tech)" in digest_text
                assert "AI fallback content" in digest_text
    
    def test_generate_ai_analysis(self):
        """Test _generate_ai_analysis method."""
        service = UnifiedDigestService(async_mode=False)
        
        news = [
            {
                "title": "Test News",
                "content": "Test content",
                "importance": 0.8,
                "credibility": 0.9
            }
        ]
        
        # Mock AI summary generation
        with patch('services.unified_digest_service.generate_batch_summary') as mock_summary:
            mock_summary.return_value = "Generated AI summary"
            
            result = service._generate_ai_analysis(news, "analytical")
            
            assert result == "Generated AI summary"
            mock_summary.assert_called_once()
    
    def test_generate_ai_analysis_fallback(self):
        """Test _generate_ai_analysis with fallback."""
        service = UnifiedDigestService(async_mode=False)
        
        news = [
            {
                "title": "Test News",
                "content": "Test content",
                "importance": 0.8,
                "credibility": 0.9
            }
        ]
        
        # Mock AI summary failure
        with patch('services.unified_digest_service.generate_batch_summary') as mock_summary:
            mock_summary.side_effect = Exception("AI service error")
            
            with patch('services.unified_digest_service.format_ai_fallback') as mock_fallback:
                mock_fallback.return_value = "Fallback content"
                
                result = service._generate_ai_analysis(news, "analytical")
                
                assert result == "Fallback content"
    
    def test_get_digest_stats(self):
        """Test get_digest_stats method."""
        service = UnifiedDigestService(async_mode=False)
        
        news = [
            {"importance": 0.9, "credibility": 0.8},
            {"importance": 0.7, "credibility": 0.6},
            {"importance": 0.5, "credibility": 0.4},
        ]
        
        stats = service.get_digest_stats(news)
        
        assert stats["total_items"] == 3
        assert stats["avg_importance"] == 0.7  # (0.9 + 0.7 + 0.5) / 3
        assert stats["avg_credibility"] == 0.6  # (0.8 + 0.6 + 0.4) / 3
        assert stats["high_importance_count"] == 1  # Only 0.9 > 0.7
        assert stats["high_credibility_count"] == 1  # Only 0.8 > 0.7
    
    def test_get_digest_stats_empty(self):
        """Test get_digest_stats with empty news list."""
        service = UnifiedDigestService(async_mode=False)
        
        stats = service.get_digest_stats([])
        
        assert stats["total_items"] == 0
        assert stats["avg_importance"] == 0.0
        assert stats["avg_credibility"] == 0.0
        assert stats["high_importance_count"] == 0
        assert stats["high_credibility_count"] == 0


class TestGlobalServices:
    """Test global service instances."""
    
    def test_get_sync_digest_service(self):
        """Test get_sync_digest_service returns singleton instance."""
        # Reset global state
        import services.unified_digest_service
        services.unified_digest_service._sync_digest_service = None
        
        with patch('services.unified_digest_service.UnifiedDigestService') as mock_service:
            service1 = get_sync_digest_service()
            service2 = get_sync_digest_service()
            
            # Should return same instance
            assert service1 == service2
            mock_service.assert_called_once_with(async_mode=False)
    
    def test_get_async_digest_service(self):
        """Test get_async_digest_service returns singleton instance."""
        # Reset global state
        import services.unified_digest_service
        services.unified_digest_service._async_digest_service = None
        
        with patch('services.unified_digest_service.UnifiedDigestService') as mock_service:
            service1 = get_async_digest_service()
            service2 = get_async_digest_service()
            
            # Should return same instance
            assert service1 == service2
            mock_service.assert_called_once_with(async_mode=True)


class TestBackwardCompatibility:
    """Test backward compatibility functions."""
    
    def test_backward_compatibility_build_daily_digest(self):
        """Test backward compatibility for build_daily_digest."""
        with patch('services.unified_digest_service.get_sync_digest_service') as mock_get_service:
            mock_service = Mock()
            mock_service.build_daily_digest.return_value = ("Test digest", [{"title": "Test"}])
            mock_get_service.return_value = mock_service
            
            digest_text, news = build_daily_digest(limit=5)
            
            assert digest_text == "Test digest"
            assert len(news) == 1
            mock_service.build_daily_digest.assert_called_once_with(5, "analytical", None)
    
    @pytest.mark.asyncio
    async def test_backward_compatibility_async_build_daily_digest(self):
        """Test backward compatibility for async_build_daily_digest."""
        with patch('services.unified_digest_service.get_async_digest_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.async_build_daily_digest.return_value = ("Async digest", [{"title": "Async"}])
            mock_get_service.return_value = mock_service
            
            digest_text, news = await async_build_daily_digest(limit=3)
            
            assert digest_text == "Async digest"
            assert len(news) == 1
            mock_service.async_build_daily_digest.assert_called_once_with(3, "analytical", None)
    
    def test_backward_compatibility_build_ai_digest(self):
        """Test backward compatibility for build_ai_digest."""
        with patch('services.unified_digest_service.get_sync_digest_service') as mock_get_service:
            mock_service = Mock()
            mock_service.build_ai_digest.return_value = "AI digest text"
            mock_get_service.return_value = mock_service
            
            digest_text = build_ai_digest(
                limit=10,
                categories=["crypto"],
                style="business"
            )
            
            assert digest_text == "AI digest text"
            mock_service.build_ai_digest.assert_called_once_with(
                10, ["crypto"], None, "daily", "business"
            )
    
    @pytest.mark.asyncio
    async def test_backward_compatibility_async_build_ai_digest(self):
        """Test backward compatibility for async_build_ai_digest."""
        with patch('services.unified_digest_service.get_async_digest_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.async_build_ai_digest.return_value = "Async AI digest text"
            mock_get_service.return_value = mock_service
            
            digest_text = await async_build_ai_digest(
                limit=8,
                category="tech",
                style="analytical"
            )
            
            assert digest_text == "Async AI digest text"
            mock_service.async_build_ai_digest.assert_called_once_with(
                8, None, "tech", "daily", "analytical"
            )

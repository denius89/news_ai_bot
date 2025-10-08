"""
Tests for AI optimization modules.

This module tests the pre-filtering, caching, local prediction,
and metrics collection functionality.
"""

import pytest
import tempfile
import yaml
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from ai_modules.prefilter import Prefilter, PrefilterResult
from ai_modules.cache import AICache, CacheEntry
from ai_modules.local_predictor import LocalPredictor, PredictionResult
from ai_modules.metrics import MetricsCollector
from ai_modules.optimized_importance import evaluate_importance
from ai_modules.optimized_credibility import evaluate_credibility, evaluate_both_with_optimization


class TestPrefilter:
    """Test pre-filtering functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = {
            "features": {"prefilter_enabled": True},
            "prefilter": {
                "min_title_words": 6,
                "stop_markers": ["opinion", "advertisement", "sponsored"],
                "importance_markers": {
                    "crypto": ["SEC", "ETF", "regulation"],
                    "tech": ["release", "breach", "security"],
                },
            },
        }

        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()

        self.prefilter = Prefilter(self.temp_config.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.temp_config.name).unlink()

    def test_prefilter_pass(self):
        """Test prefilter passes valid news."""
        news_item = {
            "title": "Bitcoin ETF approved by SEC in major regulatory breakthrough",
            "content": "The SEC has approved the first Bitcoin ETF...",
            "source": "reuters.com",
            "category": "crypto",
        }

        result = self.prefilter.filter_news(news_item)

        assert result.passed is True
        assert result.reason == "pre_filter_pass"
        assert result.score > 0.3

    def test_prefilter_fail_title_too_short(self):
        """Test prefilter fails for short titles."""
        news_item = {
            "title": "Bitcoin up",
            "content": "Bitcoin price increased...",
            "source": "reuters.com",
            "category": "crypto",
        }

        result = self.prefilter.filter_news(news_item)

        assert result.passed is False
        assert result.reason == "pre_filter"
        assert result.score == 0.0

    def test_prefilter_fail_stop_marker(self):
        """Test prefilter fails for stop markers."""
        news_item = {
            "title": "Sponsored: How to buy Bitcoin for beginners",
            "content": "This is a sponsored article...",
            "source": "blog.com",
            "category": "crypto",
        }

        result = self.prefilter.filter_news(news_item)

        assert result.passed is False
        assert result.reason == "pre_filter"

    def test_prefilter_importance_scoring(self):
        """Test importance scoring based on markers."""
        # High importance news
        high_importance = {
            "title": "SEC approves Bitcoin ETF in major regulatory decision",
            "content": "The SEC has approved the first Bitcoin ETF...",
            "category": "crypto",
        }

        # Low importance news
        low_importance = {
            "title": "Bitcoin price moves slightly in weekend trading",
            "content": "Bitcoin price changed by 1%...",
            "category": "crypto",
        }

        high_result = self.prefilter.filter_news(high_importance)
        low_result = self.prefilter.filter_news(low_importance)

        assert high_result.score > low_result.score

    def test_prefilter_disabled(self):
        """Test prefilter when disabled."""
        self.test_config["features"]["prefilter_enabled"] = False
        yaml.dump(self.test_config, open(self.temp_config.name, "w"))

        prefilter = Prefilter(self.temp_config.name)
        assert prefilter.is_enabled() is False


class TestAICache:
    """Test AI cache functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = {
            "features": {"cache_enabled": True},
            "cache": {
                "max_size": 100,
                "ttl_seconds": 0,
                "dedup_key_format": "{title_norm}|{link_norm}|{source}|{date_yyyy_mm_dd}",
            },
        }

        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()

        self.cache = AICache(self.temp_config.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.temp_config.name).unlink()

    def test_cache_set_and_get(self):
        """Test setting and getting cache entries."""
        news_item = {
            "title": "Bitcoin ETF approved by SEC",
            "link": "https://example.com/bitcoin-etf",
            "source": "reuters.com",
            "published_at": "2025-01-01T10:00:00Z",
        }

        # Set cache entry
        self.cache.set(news_item, 0.8, 0.9, "AI summary", "gpt-4o-mini")

        # Get cache entry
        entry = self.cache.get(news_item)

        assert entry is not None
        assert entry.ai_importance == 0.8
        assert entry.ai_credibility == 0.9
        assert entry.ai_summary == "AI summary"
        assert entry.ai_model == "gpt-4o-mini"

    def test_cache_miss(self):
        """Test cache miss for non-existent entry."""
        news_item = {
            "title": "Non-existent news",
            "link": "https://example.com/nonexistent",
            "source": "unknown.com",
            "published_at": "2025-01-01T10:00:00Z",
        }

        entry = self.cache.get(news_item)
        assert entry is None

    def test_cache_normalization(self):
        """Test that similar news items get the same cache key."""
        news_item1 = {
            "title": "Bitcoin ETF approved by SEC",
            "link": "https://example.com/bitcoin-etf?utm_source=twitter",
            "source": "Reuters",
            "published_at": "2025-01-01T10:00:00Z",
        }

        news_item2 = {
            "title": "bitcoin etf approved by sec",  # Different case
            "link": "https://example.com/bitcoin-etf",  # No UTM params
            "source": "reuters",  # Different case
            "published_at": "2025-01-01T10:00:00Z",
        }

        # Set cache for first item
        self.cache.set(news_item1, 0.8, 0.9)

        # Should get same result for second item (normalized)
        entry = self.cache.get(news_item2)
        assert entry is not None
        assert entry.ai_importance == 0.8
        assert entry.ai_credibility == 0.9

    def test_cache_size_limit(self):
        """Test cache size limit enforcement."""
        # Fill cache beyond limit
        for i in range(150):  # More than max_size (100)
            news_item = {
                "title": f"News item {i}",
                "link": f"https://example.com/news{i}",
                "source": "test.com",
                "published_at": "2025-01-01T10:00:00Z",
            }
            self.cache.set(news_item, 0.5, 0.5)

        # Cache should not exceed max_size
        assert len(self.cache.cache) <= 100

    def test_cache_disabled(self):
        """Test cache when disabled."""
        self.test_config["features"]["cache_enabled"] = False
        yaml.dump(self.test_config, open(self.temp_config.name, "w"))

        cache = AICache(self.temp_config.name)
        assert cache.is_enabled() is False

        # Should return None when disabled
        news_item = {"title": "Test", "link": "https://test.com", "source": "test"}
        entry = cache.get(news_item)
        assert entry is None


class TestLocalPredictor:
    """Test local predictor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = {
            "features": {"local_predictor_enabled": True},
            "local_predictor": {
                "model_type": "rules",
                "weights": {"title_length": 0.2, "source_reputation": 0.3, "category_match": 0.2, "keyword_match": 0.3},
            },
        }

        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()

        self.predictor = LocalPredictor(self.temp_config.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.temp_config.name).unlink()

    def test_predict_high_quality_news(self):
        """Test prediction for high-quality news."""
        news_item = {
            "title": "Breaking: SEC approves Bitcoin ETF in major regulatory decision",
            "content": "The SEC has officially approved the first Bitcoin ETF...",
            "source": "reuters.com",
            "category": "crypto",
        }

        result = self.predictor.predict(news_item)

        assert isinstance(result, PredictionResult)
        assert 0.0 <= result.importance <= 1.0
        assert 0.0 <= result.credibility <= 1.0
        assert 0.0 <= result.confidence <= 1.0

        # Should be high scores for quality news
        assert result.importance > 0.5
        assert result.credibility > 0.5

    def test_predict_low_quality_news(self):
        """Test prediction for low-quality news."""
        news_item = {
            "title": "Bitcoin price prediction click here",
            "content": "This is a sponsored article about Bitcoin...",
            "source": "unknown-blog.com",
            "category": "crypto",
        }

        result = self.predictor.predict(news_item)

        # Should be lower scores for low-quality news
        assert result.importance < 0.5
        assert result.credibility < 0.5

    def test_source_reputation_scoring(self):
        """Test source reputation affects credibility."""
        high_reputation = {
            "title": "Standard news title about Bitcoin",
            "content": "Standard content...",
            "source": "reuters.com",
            "category": "crypto",
        }

        low_reputation = {
            "title": "Standard news title about Bitcoin",
            "content": "Standard content...",
            "source": "unknown-blog.com",
            "category": "crypto",
        }

        high_result = self.predictor.predict(high_reputation)
        low_result = self.predictor.predict(low_reputation)

        assert high_result.credibility > low_result.credibility

    def test_keyword_scoring(self):
        """Test keyword-based importance scoring."""
        breaking_news = {
            "title": "BREAKING: Major announcement from SEC",
            "content": "This is urgent breaking news...",
            "source": "reuters.com",
            "category": "crypto",
        }

        regular_news = {
            "title": "Regular news about Bitcoin price",
            "content": "Bitcoin price moved slightly...",
            "source": "reuters.com",
            "category": "crypto",
        }

        breaking_result = self.predictor.predict(breaking_news)
        regular_result = self.predictor.predict(regular_news)

        assert breaking_result.importance > regular_result.importance

    def test_predictor_disabled(self):
        """Test predictor when disabled."""
        self.test_config["features"]["local_predictor_enabled"] = False
        yaml.dump(self.test_config, open(self.temp_config.name, "w"))

        predictor = LocalPredictor(self.temp_config.name)
        assert predictor.is_enabled() is False


class TestMetricsCollector:
    """Test metrics collection functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.metrics = MetricsCollector()

    def test_increment_counters(self):
        """Test counter incrementing."""
        initial_processed = self.metrics.metrics.news_processed_total

        self.metrics.increment_news_processed()
        self.metrics.increment_ai_calls()
        self.metrics.increment_ai_skipped_prefilter()

        assert self.metrics.metrics.news_processed_total == initial_processed + 1
        assert self.metrics.metrics.ai_calls_total == 1
        assert self.metrics.metrics.ai_skipped_prefilter_total == 1

    def test_latency_recording(self):
        """Test latency recording."""
        self.metrics.record_ai_latency(100.5)
        self.metrics.record_ai_latency(200.3)

        assert len(self.metrics.metrics.ai_latency_ms) == 2
        assert self.metrics.metrics.ai_latency_ms[0] == 100.5
        assert self.metrics.metrics.ai_latency_ms[1] == 200.3

    def test_metrics_summary(self):
        """Test metrics summary generation."""
        # Add some test data
        self.metrics.increment_news_processed()
        self.metrics.increment_ai_calls()
        self.metrics.increment_ai_skipped_prefilter()
        self.metrics.record_ai_latency(100.0)

        summary = self.metrics.get_metrics_summary()

        assert summary["news_processed_total"] == 1
        assert summary["ai_calls_total"] == 1
        assert summary["ai_skipped_prefilter_total"] == 1
        assert summary["ai_avg_latency_ms"] == 100.0
        assert summary["ai_calls_saved_percentage"] == 100.0  # 1 saved out of 1 processed

    def test_reset_metrics(self):
        """Test metrics reset."""
        # Add some data
        self.metrics.increment_news_processed()
        self.metrics.increment_ai_calls()

        # Reset
        self.metrics.reset_metrics()

        # Should be back to zero
        assert self.metrics.metrics.news_processed_total == 0
        assert self.metrics.metrics.ai_calls_total == 0


class TestOptimizedEvaluation:
    """Test optimized evaluation functions."""

    @patch("ai_modules.optimized_importance.original_evaluate_importance")
    @patch("ai_modules.optimized_importance.get_cached_evaluation")
    @patch("ai_modules.optimized_importance.filter_news_item")
    def test_evaluate_importance_with_cache_hit(self, mock_filter, mock_cache, mock_original):
        """Test importance evaluation with cache hit."""
        # Setup mocks
        mock_filter.return_value = Mock(passed=True, reason="prefilter_pass")
        mock_cache.return_value = Mock(ai_importance=0.8, ai_credibility=0.9)

        news_item = {"title": "Test news", "content": "Test content"}

        result = evaluate_importance(news_item)

        assert result == 0.8
        mock_original.assert_not_called()  # Should not call original AI

    @patch("ai_modules.optimized_importance.original_evaluate_importance")
    @patch("ai_modules.optimized_importance.get_cached_evaluation")
    @patch("ai_modules.optimized_importance.filter_news_item")
    def test_evaluate_importance_with_prefilter_reject(self, mock_filter, mock_cache, mock_original):
        """Test importance evaluation with prefilter rejection."""
        # Setup mocks
        mock_filter.return_value = Mock(passed=False, reason="pre_filter")

        news_item = {"title": "Short", "content": "Test content"}

        result = evaluate_importance(news_item)

        assert result == 0.0
        mock_cache.assert_not_called()  # Should not check cache
        mock_original.assert_not_called()  # Should not call original AI

    @patch("ai_modules.optimized_importance.original_evaluate_importance")
    @patch("ai_modules.optimized_importance.get_cached_evaluation")
    @patch("ai_modules.optimized_importance.filter_news_item")
    def test_evaluate_importance_fallback_to_ai(self, mock_filter, mock_cache, mock_original):
        """Test importance evaluation fallback to AI."""
        # Setup mocks
        mock_filter.return_value = Mock(passed=True, reason="prefilter_pass")
        mock_cache.return_value = None  # Cache miss
        mock_original.return_value = 0.7

        news_item = {"title": "Test news with sufficient length", "content": "Test content"}

        result = evaluate_importance(news_item)

        assert result == 0.7
        mock_original.assert_called_once_with(news_item)

    @patch("ai_modules.optimized_credibility.original_evaluate_importance")
    @patch("ai_modules.optimized_credibility.original_evaluate_credibility")
    @patch("ai_modules.optimized_credibility.get_cached_evaluation")
    @patch("ai_modules.optimized_credibility.filter_news_item")
    def test_evaluate_both_with_optimization(self, mock_filter, mock_cache, mock_orig_imp, mock_orig_cred):
        """Test combined importance and credibility evaluation."""
        # Setup mocks
        mock_filter.return_value = Mock(passed=True, reason="prefilter_pass")
        mock_cache.return_value = Mock(ai_importance=0.8, ai_credibility=0.9)

        news_item = {"title": "Test news", "content": "Test content"}

        importance, credibility = evaluate_both_with_optimization(news_item)

        assert importance == 0.8
        assert credibility == 0.9
        mock_orig_imp.assert_not_called()  # Should not call original AI
        mock_orig_cred.assert_not_called()  # Should not call original AI


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

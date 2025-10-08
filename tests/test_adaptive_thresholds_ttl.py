"""
Tests for adaptive thresholds and TTL functionality.

This module tests the new adaptive thresholds and TTL cache features
for AI optimization.
"""

import pytest
import tempfile
import yaml
from unittest.mock import Mock, patch
from pathlib import Path
from datetime import datetime, timezone, timedelta

from ai_modules.adaptive_thresholds import AdaptiveThresholds, get_adaptive_thresholds
from ai_modules.cache import AICache, CacheEntry
from ai_modules.optimized_importance import evaluate_importance
from ai_modules.optimized_credibility import evaluate_both_with_optimization


class TestAdaptiveThresholds:
    """Test adaptive thresholds functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = {
            "features": {"adaptive_thresholds_enabled": True},
            "category_thresholds": {
                "crypto": {"importance": 0.55, "credibility": 0.65},
                "tech": {"importance": 0.6, "credibility": 0.7},
                "sports": {"importance": 0.5, "credibility": 0.6},
            },
            "default_thresholds": {"importance": 0.6, "credibility": 0.7},
        }

        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()

        self.adaptive_thresholds = AdaptiveThresholds(self.temp_config.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.temp_config.name).unlink()

    def test_get_thresholds_crypto(self):
        """Test getting thresholds for crypto category."""
        importance, credibility = self.adaptive_thresholds.get_thresholds("crypto")

        assert importance == 0.55
        assert credibility == 0.65

    def test_get_thresholds_tech(self):
        """Test getting thresholds for tech category."""
        importance, credibility = self.adaptive_thresholds.get_thresholds("tech")

        assert importance == 0.6
        assert credibility == 0.7

    def test_get_thresholds_unknown_category(self):
        """Test getting thresholds for unknown category (should use defaults)."""
        importance, credibility = self.adaptive_thresholds.get_thresholds("unknown")

        assert importance == 0.6
        assert credibility == 0.7

    def test_get_thresholds_none_category(self):
        """Test getting thresholds for None category (should use defaults)."""
        importance, credibility = self.adaptive_thresholds.get_thresholds(None)

        assert importance == 0.6
        assert credibility == 0.7

    def test_check_thresholds_pass(self):
        """Test threshold checking that passes."""
        passed, reason = self.adaptive_thresholds.check_thresholds(0.8, 0.8, "crypto")

        assert passed is True
        assert reason == "thresholds_passed"

    def test_check_thresholds_fail_importance(self):
        """Test threshold checking that fails on importance."""
        passed, reason = self.adaptive_thresholds.check_thresholds(0.5, 0.8, "crypto")

        assert passed is False
        assert reason == "importance_below_threshold"

    def test_check_thresholds_fail_credibility(self):
        """Test threshold checking that fails on credibility."""
        passed, reason = self.adaptive_thresholds.check_thresholds(0.8, 0.6, "crypto")

        assert passed is False
        assert reason == "credibility_below_threshold"

    def test_adaptive_thresholds_disabled(self):
        """Test adaptive thresholds when disabled."""
        self.test_config["features"]["adaptive_thresholds_enabled"] = False
        yaml.dump(self.test_config, open(self.temp_config.name, "w"))

        adaptive_thresholds = AdaptiveThresholds(self.temp_config.name)
        assert adaptive_thresholds.is_enabled() is False

        # Should always return default thresholds when disabled
        importance, credibility = adaptive_thresholds.get_thresholds("crypto")
        assert importance == 0.6
        assert credibility == 0.7

    def test_get_category_list(self):
        """Test getting list of categories with thresholds."""
        categories = self.adaptive_thresholds.get_category_list()

        assert "crypto" in categories
        assert "tech" in categories
        assert "sports" in categories
        assert len(categories) == 3

    def test_get_stats(self):
        """Test getting statistics."""
        stats = self.adaptive_thresholds.get_stats()

        assert stats["enabled"] is True
        assert stats["categories_with_thresholds"] == 3
        assert stats["default_thresholds"]["importance"] == 0.6
        assert "crypto" in stats["category_thresholds"]


class TestTTLCache:
    """Test TTL cache functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = {
            "features": {"cache_enabled": True, "cache_ttl_enabled": True},
            "cache": {"ttl_days": 3, "ttl_seconds": 0, "partial_update": True, "max_size": 1000},
        }

        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()

        self.cache = AICache(self.temp_config.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.temp_config.name).unlink()

    def test_ttl_enabled(self):
        """Test TTL is enabled."""
        assert self.cache.is_ttl_enabled() is True

    def test_cache_entry_with_ttl(self):
        """Test cache entry with TTL."""
        news_item = {
            "title": "Test news",
            "link": "https://example.com/test",
            "source": "test.com",
            "published_at": "2025-01-01T10:00:00Z",
        }

        # Set cache entry
        self.cache.set(news_item, 0.8, 0.9)

        # Get cache entry
        entry = self.cache.get(news_item)

        assert entry is not None
        assert entry.ai_importance == 0.8
        assert entry.ai_credibility == 0.9
        assert entry.ttl_expires_at is not None

    def test_cache_entry_expired(self):
        """Test expired cache entry."""
        news_item = {
            "title": "Test news",
            "link": "https://example.com/test",
            "source": "test.com",
            "published_at": "2025-01-01T10:00:00Z",
        }

        # Set cache entry
        self.cache.set(news_item, 0.8, 0.9)

        # Manually expire the entry
        entry = self.cache.cache[list(self.cache.cache.keys())[0]]
        entry.ttl_expires_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

        # Should return None for expired entry
        cached_entry = self.cache.get(news_item)
        assert cached_entry is None

    def test_needs_refresh(self):
        """Test cache entry needs refresh."""
        news_item = {
            "title": "Test news",
            "link": "https://example.com/test",
            "source": "test.com",
            "published_at": "2025-01-01T10:00:00Z",
        }

        # Set cache entry
        self.cache.set(news_item, 0.8, 0.9)

        # Get entry and set it close to expiration
        entry = self.cache.cache[list(self.cache.cache.keys())[0]]
        entry.ttl_expires_at = (datetime.now(timezone.utc) + timedelta(hours=12)).isoformat()

        # Should need refresh (less than 1 day remaining)
        assert self.cache.needs_refresh(entry) is True

    def test_partial_update(self):
        """Test partial cache update."""
        news_item = {
            "title": "Test news",
            "link": "https://example.com/test",
            "source": "test.com",
            "published_at": "2025-01-01T10:00:00Z",
        }

        # Set initial cache entry
        self.cache.set(news_item, 0.8, 0.9)

        # Partial update - only credibility
        self.cache.update_partial(news_item, credibility=0.95)

        # Check updated entry
        entry = self.cache.get(news_item)

        assert entry is not None
        assert entry.ai_importance == 0.8  # Unchanged
        assert entry.ai_credibility == 0.95  # Updated
        assert entry.ttl_expires_at is not None  # TTL refreshed

    def test_ttl_disabled(self):
        """Test TTL when disabled."""
        self.test_config["features"]["cache_ttl_enabled"] = False
        yaml.dump(self.test_config, open(self.temp_config.name, "w"))

        cache = AICache(self.temp_config.name)
        assert cache.is_ttl_enabled() is False

        # TTL checks should always return False when disabled
        news_item = {"title": "Test", "link": "https://test.com", "source": "test"}
        cache.set(news_item, 0.8, 0.9)
        entry = cache.get(news_item)

        assert entry is not None
        assert cache.needs_refresh(entry) is False


class TestOptimizedEvaluationWithAdaptiveThresholds:
    """Test optimized evaluation with adaptive thresholds."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = {
            "features": {
                "prefilter_enabled": True,
                "cache_enabled": True,
                "local_predictor_enabled": False,
                "adaptive_thresholds_enabled": True,
                "cache_ttl_enabled": True,
            },
            "category_thresholds": {
                "crypto": {"importance": 0.55, "credibility": 0.65},
                "tech": {"importance": 0.6, "credibility": 0.7},
            },
            "default_thresholds": {"importance": 0.6, "credibility": 0.7},
            "cache": {"ttl_days": 3, "partial_update": True},
        }

        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()

    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.temp_config.name).unlink()

    @patch("ai_modules.optimized_importance.original_evaluate_importance")
    @patch("ai_modules.optimized_importance.get_cached_evaluation")
    @patch("ai_modules.optimized_importance.filter_news_item")
    def test_importance_with_adaptive_thresholds_crypto(
            self, mock_filter, mock_cache, mock_original):
        """Test importance evaluation with adaptive thresholds for crypto."""
        # Setup mocks
        mock_filter.return_value = Mock(passed=True, reason="prefilter_pass")
        mock_cache.return_value = None  # Cache miss
        mock_original.return_value = 0.6  # Above crypto threshold (0.55)

        news_item = {
            "title": "Bitcoin ETF approved by SEC in major regulatory breakthrough",
            "content": "The SEC has approved...",
            "source": "reuters.com",
            "category": "crypto",
        }

        result = evaluate_importance(news_item)

        assert result == 0.6
        mock_original.assert_called_once_with(news_item)

    @patch("ai_modules.optimized_importance.original_evaluate_importance")
    @patch("ai_modules.optimized_importance.get_cached_evaluation")
    @patch("ai_modules.optimized_importance.filter_news_item")
    def test_importance_with_adaptive_thresholds_below_threshold(
            self, mock_filter, mock_cache, mock_original):
        """Test importance evaluation below adaptive threshold."""
        # Setup mocks
        mock_filter.return_value = Mock(passed=True, reason="prefilter_pass")
        mock_cache.return_value = None  # Cache miss
        mock_original.return_value = 0.5  # Below crypto threshold (0.55)

        news_item = {
            "title": "Bitcoin price moves slightly",
            "content": "Bitcoin price changed...",
            "source": "blog.com",
            "category": "crypto",
        }

        result = evaluate_importance(news_item)

        assert result == 0.0  # Should be filtered out by adaptive threshold
        mock_original.assert_called_once_with(news_item)

    @patch("ai_modules.optimized_credibility.original_evaluate_importance")
    @patch("ai_modules.optimized_credibility.original_evaluate_credibility")
    @patch("ai_modules.optimized_credibility.get_cached_evaluation")
    @patch("ai_modules.optimized_credibility.filter_news_item")
    def test_both_evaluation_with_adaptive_thresholds(
            self, mock_filter, mock_cache, mock_orig_imp, mock_orig_cred):
        """Test combined evaluation with adaptive thresholds."""
        # Setup mocks
        mock_filter.return_value = Mock(passed=True, reason="prefilter_pass")
        mock_cache.return_value = None  # Cache miss
        mock_orig_imp.return_value = 0.6  # Above crypto threshold (0.55)
        mock_orig_cred.return_value = 0.7  # Above crypto threshold (0.65)

        news_item = {
            "title": "Major crypto regulation announced",
            "content": "New regulations...",
            "source": "reuters.com",
            "category": "crypto",
        }

        importance, credibility = evaluate_both_with_optimization(news_item)

        assert importance == 0.6
        assert credibility == 0.7
        mock_orig_imp.assert_called_once_with(news_item)
        mock_orig_cred.assert_called_once_with(news_item)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

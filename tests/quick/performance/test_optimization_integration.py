"""
Integration tests for AI optimization system.

This module tests the complete optimization pipeline with synthetic data
to verify AI call reduction while maintaining quality.
"""

import pytest
import asyncio
import tempfile
import yaml
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from ai_modules.prefilter import Prefilter
from ai_modules.cache import AICache
from ai_modules.local_predictor import LocalPredictor
from ai_modules.metrics import MetricsCollector
from ai_modules.optimized_importance import evaluate_importance
from ai_modules.optimized_credibility import evaluate_both_with_optimization


class TestOptimizationIntegration:
    """Integration tests for the complete optimization pipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = {
            "features": {"prefilter_enabled": True, "cache_enabled": True, "local_predictor_enabled": True},
            "thresholds": {
                "ai_importance_threshold": 0.6,
                "ai_credibility_threshold": 0.7,
                "local_predictor_threshold": 0.5,
            },
            "prefilter": {
                "min_title_words": 6,
                "stop_markers": ["opinion", "advertisement", "sponsored", "click here"],
                "importance_markers": {
                    "crypto": ["SEC", "ETF", "regulation", "approval"],
                    "tech": ["release", "breach", "security", "vulnerability"],
                    "world": ["war", "conflict", "election", "government"],
                },
            },
            "cache": {"max_size": 1000, "ttl_seconds": 0},
            "local_predictor": {
                "model_type": "rules",
                "weights": {"title_length": 0.2, "source_reputation": 0.3, "category_match": 0.2, "keyword_match": 0.3},
            },
        }

        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        yaml.dump(self.test_config, self.temp_config)
        self.temp_config.close()

        # Initialize components
        self.prefilter = Prefilter(self.temp_config.name)
        self.cache = AICache(self.temp_config.name)
        self.predictor = LocalPredictor(self.temp_config.name)
        self.metrics = MetricsCollector()

    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.temp_config.name).unlink()

    def create_test_news_items(self) -> list:
        """Create a diverse set of test news items."""
        return [
            # High-quality news (should pass all filters)
            {
                "title": "SEC approves Bitcoin ETF in major regulatory breakthrough for cryptocurrency",
                "content": "The Securities and Exchange Commission has officially approved the first Bitcoin ETF...",
                "source": "reuters.com",
                "category": "crypto",
                "published_at": "2025-01-01T10:00:00Z",
                "link": "https://reuters.com/bitcoin-etf-approved",
            },
            # Medium-quality news (should pass prefilter, maybe local predictor)
            {
                "title": "Bitcoin price reaches new all-time high amid institutional adoption",
                "content": "Bitcoin has reached a new all-time high as institutional investors...",
                "source": "coindesk.com",
                "category": "crypto",
                "published_at": "2025-01-01T11:00:00Z",
                "link": "https://coindesk.com/bitcoin-ath",
            },
            # Low-quality news (should be filtered out)
            {
                "title": "Sponsored: How to buy Bitcoin click here now",
                "content": "This is a sponsored advertisement about buying Bitcoin...",
                "source": "unknown-blog.com",
                "category": "crypto",
                "published_at": "2025-01-01T12:00:00Z",
                "link": "https://unknown-blog.com/bitcoin-ad",
            },
            # Short title (should be filtered out)
            {
                "title": "Bitcoin up",
                "content": "Bitcoin price increased today...",
                "source": "twitter.com",
                "category": "crypto",
                "published_at": "2025-01-01T13:00:00Z",
                "link": "https://twitter.com/bitcoin-up",
            },
            # Tech news (should pass filters)
            {
                "title": "Major security vulnerability discovered in popular JavaScript library",
                "content": "A critical security vulnerability has been discovered in a widely used...",
                "source": "github.com",
                "category": "tech",
                "published_at": "2025-01-01T14:00:00Z",
                "link": "https://github.com/security-advisory",
            },
            # World news (should pass filters)
            {
                "title": "Government announces new policy on digital currencies and regulation",
                "content": "The government has announced a comprehensive new policy...",
                "source": "bbc.com",
                "category": "world",
                "published_at": "2025-01-01T15:00:00Z",
                "link": "https://bbc.com/digital-currency-policy",
            },
        ]

    @patch("ai_modules.optimized_importance.original_evaluate_importance")
    @patch("ai_modules.optimized_credibility.original_evaluate_credibility")
    @pytest.mark.skip(reason="Complex integration test requires full pipeline setup")
    def test_complete_optimization_pipeline(self, mock_orig_cred, mock_orig_imp):
        """Test the complete optimization pipeline with synthetic data."""
        # Setup AI mocks
        mock_orig_imp.return_value = 0.8
        mock_orig_cred.return_value = 0.9

        test_news = self.create_test_news_items()

        # Track metrics before
        initial_ai_calls = self.metrics.metrics.ai_calls_total
        initial_news_processed = self.metrics.metrics.news_processed_total

        results = []
        ai_calls_made = 0

        for news_item in test_news:
            # Test both importance and credibility evaluation
            importance, credibility = evaluate_both_with_optimization(news_item)
            results.append({"news_item": news_item, "importance": importance, "credibility": credibility})

            # Count AI calls (mock calls)
            if mock_orig_imp.called or mock_orig_cred.called:
                ai_calls_made += 1
                mock_orig_imp.reset_mock()
                mock_orig_cred.reset_mock()

        # Verify results
        assert len(results) == len(test_news)

        # High-quality news should have good scores
        high_quality = results[0]  # SEC approves Bitcoin ETF
        assert high_quality["importance"] > 0.6
        assert high_quality["credibility"] > 0.7

        # Low-quality news should be filtered out or have low scores
        low_quality = results[2]  # Sponsored content
        assert low_quality["importance"] < 0.6 or low_quality["credibility"] < 0.7

        # Short title should be filtered out
        short_title = results[3]  # Bitcoin up
        assert short_title["importance"] == 0.0 or short_title["credibility"] == 0.0

        # Check metrics
        final_metrics = self.metrics.get_metrics_summary()
        assert final_metrics["news_processed_total"] > initial_news_processed

        # Should have made fewer AI calls than news items (due to optimization)
        assert ai_calls_made < len(test_news)

        print(f"\n📊 Optimization Results:")
        print(f"   📰 News items processed: {len(test_news)}")
        print(f"   🤖 AI calls made: {ai_calls_made}")
        print(f"   💰 AI calls saved: {len(test_news) - ai_calls_made}")
        print(f"   📈 Optimization efficiency: {((len(test_news) - ai_calls_made) / len(test_news)) * 100:.1f}%")

    @pytest.mark.skip(reason="Complex integration test requires full cache setup")
    def test_cache_effectiveness(self):
        """Test cache effectiveness with duplicate news items."""
        test_news = self.create_test_news_items()

        # First pass - should call AI for each item
        with patch("ai_modules.optimized_importance.original_evaluate_importance") as mock_imp:
            with patch("ai_modules.optimized_credibility.original_evaluate_credibility") as mock_cred:
                mock_imp.return_value = 0.8
                mock_cred.return_value = 0.9

                for news_item in test_news:
                    evaluate_both_with_optimization(news_item)

                first_pass_calls = mock_imp.call_count + mock_cred.call_count

        # Second pass - should use cache for most items
        with patch("ai_modules.optimized_importance.original_evaluate_importance") as mock_imp:
            with patch("ai_modules.optimized_credibility.original_evaluate_credibility") as mock_cred:
                mock_imp.return_value = 0.8
                mock_cred.return_value = 0.9

                for news_item in test_news:
                    evaluate_both_with_optimization(news_item)

                second_pass_calls = mock_imp.call_count + mock_cred.call_count

        # Second pass should make significantly fewer AI calls due to caching
        assert second_pass_calls < first_pass_calls

        print(f"\n💾 Cache Effectiveness:")
        print(f"   📊 First pass AI calls: {first_pass_calls}")
        print(f"   📊 Second pass AI calls: {second_pass_calls}")
        print(f"   💰 Cache savings: {first_pass_calls - second_pass_calls}")

    def test_prefilter_effectiveness(self):
        """Test prefilter effectiveness with mixed quality news."""
        test_news = self.create_test_news_items()

        prefilter_results = []
        for news_item in test_news:
            result = self.prefilter.filter_news(news_item)
            prefilter_results.append(
                {"news_item": news_item, "passed": result.passed, "reason": result.reason, "score": result.score}
            )

        # Count how many items passed prefilter
        passed_count = sum(1 for r in prefilter_results if r["passed"])
        filtered_count = len(prefilter_results) - passed_count

        # Should filter out low-quality items
        assert filtered_count > 0  # At least some items should be filtered

        # High-quality items should pass
        high_quality_result = prefilter_results[0]  # SEC approves Bitcoin ETF
        assert high_quality_result["passed"] is True
        assert high_quality_result["score"] > 0.3

        # Low-quality items should be filtered
        low_quality_result = prefilter_results[2]  # Sponsored content
        assert low_quality_result["passed"] is False

        print(f"\n🔍 Prefilter Effectiveness:")
        print(f"   📰 Total items: {len(test_news)}")
        print(f"   ✅ Passed: {passed_count}")
        print(f"   🚫 Filtered: {filtered_count}")
        print(f"   📈 Filter rate: {(filtered_count / len(test_news)) * 100:.1f}%")

    def test_local_predictor_accuracy(self):
        """Test local predictor accuracy against expected patterns."""
        test_news = self.create_test_news_items()

        predictor_results = []
        for news_item in test_news:
            result = self.predictor.predict(news_item)
            predictor_results.append(
                {
                    "news_item": news_item,
                    "importance": result.importance,
                    "credibility": result.credibility,
                    "confidence": result.confidence,
                }
            )

        # High-quality news should have higher scores
        high_quality = predictor_results[0]  # SEC approves Bitcoin ETF
        low_quality = predictor_results[2]  # Sponsored content

        assert high_quality["importance"] > low_quality["importance"]
        assert high_quality["credibility"] > low_quality["credibility"]

        # News from reputable sources should have higher credibility
        reuters_news = predictor_results[0]  # reuters.com
        unknown_news = predictor_results[2]  # unknown-blog.com

        assert reuters_news["credibility"] > unknown_news["credibility"]

        print(f"\n🧠 Local Predictor Results:")
        for i, result in enumerate(predictor_results):
            news = result["news_item"]
            print(f"   {i+1}. {news['title'][:50]}...")
            print(f"      📊 Importance: {result['importance']:.2f}, Credibility: {result['credibility']:.2f}")

    @pytest.mark.skip(reason="Complex integration test requires different configs setup")
    def test_optimization_with_different_configurations(self):
        """Test optimization with different feature configurations."""
        test_news = self.create_test_news_items()

        configurations = [
            {"prefilter_enabled": False, "cache_enabled": False, "local_predictor_enabled": False},
            {"prefilter_enabled": True, "cache_enabled": False, "local_predictor_enabled": False},
            {"prefilter_enabled": True, "cache_enabled": True, "local_predictor_enabled": False},
            {"prefilter_enabled": True, "cache_enabled": True, "local_predictor_enabled": True},
        ]

        results = {}

        for config in configurations:
            # Update config
            self.test_config["features"].update(config)
            yaml.dump(self.test_config, open(self.temp_config.name, "w"))

            # Reset metrics
            self.metrics.reset_metrics()

            # Run test
            with patch("ai_modules.optimized_importance.original_evaluate_importance") as mock_imp:
                with patch("ai_modules.optimized_credibility.original_evaluate_credibility") as mock_cred:
                    mock_imp.return_value = 0.8
                    mock_cred.return_value = 0.9

                    for news_item in test_news:
                        evaluate_both_with_optimization(news_item)

                    ai_calls = mock_imp.call_count + mock_cred.call_count

            config_name = f"{config['prefilter_enabled']}-{config['cache_enabled']}-{config['local_predictor_enabled']}"
            results[config_name] = ai_calls

        # Verify that more features = fewer AI calls
        no_optimization = results["False-False-False"]
        full_optimization = results["True-True-True"]

        assert full_optimization < no_optimization

        print(f"\n⚙️ Configuration Comparison:")
        for config, calls in results.items():
            print(f"   {config}: {calls} AI calls")

        print(f"\n📈 Optimization improvement: {((no_optimization - full_optimization) / no_optimization) * 100:.1f}%")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

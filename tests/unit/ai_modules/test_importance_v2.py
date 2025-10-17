"""
Tests for ML-based Importance Evaluator v2.

Tests the improved importance evaluation using ML features.
"""

import pytest
from datetime import datetime, timezone

from ai_modules.importance_v2 import ImportanceEvaluatorV2, evaluate_event_importance


class TestImportanceEvaluatorV2:
    """Test cases for ImportanceEvaluatorV2."""

    def setup_method(self):
        """Set up test fixtures."""
        self.evaluator = ImportanceEvaluatorV2()

    def test_high_importance_crypto_event(self):
        """Test high importance crypto event with keywords."""
        event = {
            "title": "Ethereum Mainnet Upgrade Launch",
            "description": "Major hard fork upgrade for Ethereum network with significant improvements",
            "category": "crypto",
            "subcategory": "protocol",
            "importance": 0.7,
            "metadata": {"chain": "ethereum", "type": "upgrade", "impact": "high"},
            "location": "Global",
            "organizer": "Ethereum Foundation",
        }

        score = self.evaluator.evaluate_importance(event)

        # Should be high due to keywords (mainnet, upgrade, hard fork) + metadata
        assert score >= 0.8
        assert score <= 1.0

    def test_low_importance_event(self):
        """Test low importance event without keywords."""
        event = {
            "title": "Crypto Meetup",
            "description": "Small local meetup",
            "category": "crypto",
            "subcategory": "general",
            "importance": 0.3,
            "metadata": {},
        }

        score = self.evaluator.evaluate_importance(event)

        # Should be low due to no keywords and minimal metadata
        assert score < 0.6

    def test_markets_category_boost(self):
        """Test that markets events get category boost."""
        event = {
            "title": "Federal Reserve Rate Decision",
            "description": "FOMC meeting to decide on interest rates",
            "category": "markets",
            "subcategory": "economic_data",
            "importance": 0.6,
            "metadata": {"country": "US", "impact": "high"},
        }

        score = self.evaluator.evaluate_importance(event)

        # Should be boosted due to category + keywords (fed, rate)
        assert score >= 0.75

    def test_description_quality_bonus(self):
        """Test description length bonus."""
        event_short = {
            "title": "Event",
            "description": "Short description",
            "category": "tech",
            "importance": 0.5,
        }

        event_long = {
            "title": "Event",
            "description": "A" * 250,  # Long description
            "category": "tech",
            "importance": 0.5,
        }

        score_short = self.evaluator.evaluate_importance(event_short)
        score_long = self.evaluator.evaluate_importance(event_long)

        # Long description should score higher
        assert score_long > score_short

    def test_metadata_richness_bonus(self):
        """Test metadata richness bonus."""
        event_minimal = {
            "title": "Event",
            "description": "Description",
            "category": "sports",
            "importance": 0.5,
            "metadata": {},
        }

        event_rich = {
            "title": "Event",
            "description": "Description",
            "category": "sports",
            "importance": 0.5,
            "metadata": {
                "league": "Premier League",
                "teams": ["Team A", "Team B"],
                "venue": "Stadium",
                "attendance": 50000,
                "broadcast": "TV",
            },
        }

        score_minimal = self.evaluator.evaluate_importance(event_minimal)
        score_rich = self.evaluator.evaluate_importance(event_rich)

        # Rich metadata should score higher
        assert score_rich > score_minimal

    def test_keyword_counting(self):
        """Test keyword counting for different categories."""
        # Crypto keywords
        crypto_text = "mainnet launch airdrop listing"
        count = self.evaluator._count_keywords(crypto_text, "crypto", "high")
        assert count == 4

        # Markets keywords
        markets_text = "fed rate decision gdp inflation"
        count = self.evaluator._count_keywords(markets_text, "markets", "high")
        assert count == 4

        # No keywords
        no_keywords = "some random text"
        count = self.evaluator._count_keywords(no_keywords, "crypto", "high")
        assert count == 0

    def test_feature_extraction(self):
        """Test feature extraction from event."""
        event = {
            "title": "Test Event",
            "description": "Test description",
            "category": "tech",
            "subcategory": "software",
            "importance": 0.6,
            "metadata": {"key": "value"},
            "location": "Online",
            "organizer": "Test Org",
        }

        features = self.evaluator._extract_features(event)

        assert features["title_length"] == len("test event")
        assert features["description_length"] == len("test description")
        assert features["has_description"] is True
        assert features["category"] == "tech"
        assert features["subcategory"] == "software"
        assert features["source_importance"] == 0.6
        assert features["metadata_richness"] == 1
        assert features["has_location"] is True
        assert features["has_organizer"] is True

    def test_score_clamping(self):
        """Test that scores are clamped to [0.0, 1.0]."""
        # Event that might score > 1.0
        event = {
            "title": "Mainnet Launch Hard Fork Upgrade Airdrop",
            "description": "A" * 300,
            "category": "crypto",
            "importance": 0.9,
            "metadata": {f"key{i}": f"value{i}" for i in range(10)},
            "location": "Global",
            "organizer": "Major Foundation",
        }

        score = self.evaluator.evaluate_importance(event)

        # Should be clamped to 1.0
        assert score <= 1.0
        assert score >= 0.0

    def test_convenience_function(self):
        """Test convenience function."""
        event = {
            "title": "Test Event",
            "description": "Description",
            "category": "tech",
            "importance": 0.5,
        }

        score = evaluate_event_importance(event)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_error_handling(self):
        """Test error handling with invalid event."""
        # Empty event
        score = self.evaluator.evaluate_importance({})
        # Fallback score may vary slightly based on implementation
        assert 0.4 <= score <= 0.6  # Should be around neutral

        # Event with missing fields
        event = {"title": "Test"}
        score = self.evaluator.evaluate_importance(event)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_sports_championship_importance(self):
        """Test sports championship event."""
        event = {
            "title": "World Cup Final",
            "description": "FIFA World Cup final match",
            "category": "sports",
            "subcategory": "football",
            "importance": 0.7,
            "metadata": {"tournament": "World Cup", "stage": "Final"},
        }

        score = self.evaluator.evaluate_importance(event)

        # Should be high due to "world cup" and "final" keywords
        assert score >= 0.8

    def test_tech_conference_importance(self):
        """Test tech conference event."""
        event = {
            "title": "Apple WWDC Keynote",
            "description": "Annual Apple Worldwide Developers Conference keynote presentation",
            "category": "tech",
            "subcategory": "conference",
            "importance": 0.7,
            "metadata": {"company": "Apple", "type": "keynote"},
        }

        score = self.evaluator.evaluate_importance(event)

        # Should be high due to "wwdc" and "keynote" keywords
        assert score >= 0.75

"""
Local predictor module for AI optimization.

This module provides a lightweight local model for predicting
importance and credibility scores without calling external AI APIs.
Supports both rule-based scoring and self-tuning ML models.
"""

import logging
import re
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

import yaml
from pathlib import Path

logger = logging.getLogger("local_predictor")


@dataclass
class PredictionResult:
    """Result of local prediction."""

    importance: float
    credibility: float
    confidence: float


class LocalPredictor:
    """
    Lightweight local predictor for importance and credibility.

    Uses rule-based scoring with configurable weights and patterns.
    Can be extended to use actual ML models in the future.
    """

    def __init__(self, config_path: str = None):
        """Initialize local predictor with configuration."""
        self.config = self._load_config(config_path)
        self.weights = self.config.get("local_predictor", {}).get("weights", {})
        self.model_type = self.config.get("local_predictor", {}).get("model_type", "rules")
        self.self_tuning_enabled = self.config.get("features", {}).get("self_tuning_enabled", True)

        # Self-tuning model trainer
        self.self_tuning_trainer = None
        if self.self_tuning_enabled:
            try:
                from ai_modules.self_tuning_trainer import get_self_tuning_trainer

                self.self_tuning_trainer = get_self_tuning_trainer()
                self.self_tuning_trainer.load_models()
                logger.info("Self-tuning models loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load self-tuning models: {e}")
                self.self_tuning_trainer = None

        # Source reputation scores (can be expanded)
        self.source_reputation = {
            "reuters": 0.9,
            "bloomberg": 0.9,
            "wsj": 0.9,
            "ft": 0.9,
            "cnn": 0.8,
            "bbc": 0.8,
            "guardian": 0.8,
            "nytimes": 0.8,
            "coindesk": 0.7,
            "cointelegraph": 0.7,
            "bitcoinmagazine": 0.7,
            "reddit": 0.4,
            "twitter": 0.3,
            "blog": 0.5,
            "medium": 0.6,
        }

        # High-impact keywords
        self.high_impact_keywords = [
            "breaking",
            "urgent",
            "critical",
            "major",
            "significant",
            "unprecedented",
            "historic",
            "record",
            "first",
            "new",
            "exclusive",
            "confirmed",
            "official",
            "announced",
        ]

        # Credibility indicators
        self.credibility_positive = [
            "official",
            "confirmed",
            "verified",
            "announced",
            "reported",
            "according to",
            "sources say",
            "confirmed by",
            "verified by",
        ]

        self.credibility_negative = [
            "rumor",
            "alleged",
            "unconfirmed",
            "speculation",
            "possibly",
            "might be",
            "could be",
            "unverified",
            "hearsay",
        ]

    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "ai_optimization.yaml"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def predict(self, news_item: Dict) -> PredictionResult:
        """
        Predict importance and credibility scores.

        Args:
            news_item: Dictionary containing news item data

        Returns:
            PredictionResult with importance, credibility, and confidence scores
        """
        # Try self-tuning ML models first if available
        if self.self_tuning_enabled and self.self_tuning_trainer:
            try:
                return self._predict_with_ml_models(news_item)
            except Exception as e:
                logger.warning(f"ML model prediction failed, falling back to rules: {e}")

        # Fallback to rule-based prediction
        return self._predict_with_rules(news_item)

    def _predict_with_ml_models(self, news_item: Dict) -> PredictionResult:
        """
        Predict using self-tuning ML models.

        Args:
            news_item: Dictionary containing news item data

        Returns:
            PredictionResult with ML model predictions
        """
        # Extract features using the same logic as the collector
        features = self._extract_features_for_ml(news_item)

        # Make predictions using ML models
        importance_score, credibility_score = self.self_tuning_trainer.predict(features)

        # Calculate confidence based on feature completeness
        confidence = self._calculate_ml_confidence(features, news_item)

        logger.debug(
            f"ML prediction: importance={importance_score:.3f}, credibility={credibility_score:.3f}")

        return PredictionResult(
            importance=importance_score,
            credibility=credibility_score,
            confidence=confidence)

    def _extract_features_for_ml(self, news_item: Dict) -> Dict[str, float]:
        """
        Extract features for ML model prediction.

        Args:
            news_item: Dictionary containing news item data

        Returns:
            Dictionary with extracted features
        """
        features = {}

        # Basic text features
        title = news_item.get("title", "")
        content = news_item.get("content", "")
        source = news_item.get("source", "")
        category = news_item.get("category", "")

        # Title length features
        features["title_length"] = len(title)
        features["title_word_count"] = len(title.split())

        # Content features
        features["content_length"] = len(content)
        features["content_word_count"] = len(content.split())

        # Source trust score
        features["source_trust_score"] = self._score_source_reputation(source)

        # Category encoding
        category_scores = self._encode_category_for_ml(category)
        features.update(category_scores)

        # Word frequency features
        word_features = self._extract_word_features_for_ml(title, content)
        features.update(word_features)

        # Time-based features
        published_at = news_item.get("published_at", "")
        features["time_features"] = self._extract_time_features_for_ml(published_at)

        return features

    def _encode_category_for_ml(self, category: str) -> Dict[str, float]:
        """Encode category as features for ML model."""
        categories = ["crypto", "tech", "sports", "world", "markets"]

        features = {}
        for cat in categories:
            features[f"category_{cat}"] = 1.0 if category == cat else 0.0

        features["category_unknown"] = 1.0 if category not in categories else 0.0

        return features

    def _extract_word_features_for_ml(self, title: str, content: str) -> Dict[str, float]:
        """Extract word-based features for ML model."""
        features = {}

        # Combine title and content
        text = f"{title} {content}".lower()
        words = text.split()
        features["total_words"] = len(words)

        # Word frequency features
        important_words = [
            "breaking",
            "urgent",
            "exclusive",
            "analysis",
            "report",
            "official",
            "confirmed",
            "announced",
            "released",
            "launched",
        ]

        spam_words = [
            "click",
            "here",
            "free",
            "giveaway",
            "scam",
            "sponsored",
            "advertisement",
            "advertorial",
            "opinion",
            "prediction",
        ]

        # Count important and spam words
        important_count = sum(1 for word in important_words if word in text)
        spam_count = sum(1 for word in spam_words if word in text)

        features["important_words_ratio"] = important_count / max(len(words), 1)
        features["spam_words_ratio"] = spam_count / max(len(words), 1)

        # Title-specific features
        title_words = title.lower().split()
        features["title_important_words"] = sum(
            1 for word in title_words if word in important_words)
        features["title_spam_words"] = sum(1 for word in title_words if word in spam_words)

        return features

    def _extract_time_features_for_ml(self, published_at: str) -> float:
        """Extract time-based features for ML model."""
        try:
            if not published_at:
                return 0.0

            from datetime import datetime

            dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

            # Business hours vs off-hours
            if 9 <= dt.hour <= 17:
                return 1.0
            else:
                return 0.0

        except Exception:
            return 0.0

    def _calculate_ml_confidence(self, features: Dict[str, float], news_item: Dict) -> float:
        """Calculate confidence for ML model predictions."""
        confidence = 0.5  # Base confidence

        # Higher confidence if we have more data
        if news_item.get("content"):
            confidence += 0.2

        if news_item.get("source"):
            confidence += 0.1

        if news_item.get("published_at"):
            confidence += 0.1

        # Lower confidence for very short titles
        title = news_item.get("title", "")
        if len(title.split()) < 5:
            confidence -= 0.2

        # Adjust based on feature quality
        if features.get("total_words", 0) < 10:
            confidence -= 0.1

        return min(1.0, max(0.0, confidence))

    def _predict_with_rules(self, news_item: Dict) -> PredictionResult:
        """Predict using rule-based scoring."""
        title = news_item.get("title", "")
        content = news_item.get("content", "") or news_item.get("summary", "")
        source = news_item.get("source", "").lower()
        category = news_item.get("category", "").lower()

        # Calculate individual scores
        title_score = self._score_title_length(title)
        source_score = self._score_source_reputation(source)
        category_score = self._score_category_relevance(category)
        keyword_score = self._score_keywords(title, content)

        # Calculate importance using weighted combination
        importance = (
            title_score * self.weights.get("title_length", 0.2)
            + source_score * self.weights.get("source_reputation", 0.3)
            + category_score * self.weights.get("category_match", 0.2)
            + keyword_score * self.weights.get("keyword_match", 0.3)
        )

        # Calculate credibility
        credibility = self._score_credibility(title, content, source)

        # Calculate confidence based on how many signals we have
        confidence = self._calculate_confidence(news_item)

        return PredictionResult(
            importance=min(1.0, max(0.0, importance)),
            credibility=min(1.0, max(0.0, credibility)),
            confidence=min(1.0, max(0.0, confidence)),
        )

    def _score_title_length(self, title: str) -> float:
        """Score based on title length."""
        if not title:
            return 0.0

        word_count = len(title.split())

        # Optimal range is 6-15 words
        if 6 <= word_count <= 15:
            return 1.0
        elif word_count < 6:
            return word_count / 6.0
        else:
            # Penalize very long titles
            return max(0.3, 1.0 - (word_count - 15) * 0.05)

    def _score_source_reputation(self, source: str) -> float:
        """Score based on source reputation."""
        if not source:
            return 0.5  # Neutral for unknown sources

        source_lower = source.lower()

        # Check for exact matches first
        for known_source, score in self.source_reputation.items():
            if known_source in source_lower:
                return score

        # Check for partial matches
        if any(domain in source_lower for domain in [".com", ".org", ".net"]):
            return 0.6  # Generic domain

        return 0.4  # Unknown source

    def _score_category_relevance(self, category: str) -> float:
        """Score based on category relevance."""
        # All categories are considered relevant for now
        # This can be extended with category-specific scoring
        return 0.8

    def _score_keywords(self, title: str, content: str) -> float:
        """Score based on keyword presence."""
        text = f"{title} {content}".lower()

        score = 0.0
        for keyword in self.high_impact_keywords:
            if keyword in text:
                score += 0.2

        return min(1.0, score)

    def _score_credibility(self, title: str, content: str, source: str) -> float:
        """Score based on credibility indicators."""
        text = f"{title} {content}".lower()

        # Start with source reputation
        credibility = self._score_source_reputation(source)

        # Adjust based on positive indicators
        for indicator in self.credibility_positive:
            if indicator in text:
                credibility += 0.1

        # Adjust based on negative indicators
        for indicator in self.credibility_negative:
            if indicator in text:
                credibility -= 0.2

        # Check for excessive capitalization (spam indicator)
        if len(title) > 0:
            caps_ratio = sum(1 for c in title if c.isupper()) / len(title)
            if caps_ratio > 0.5:
                credibility -= 0.3

        return min(1.0, max(0.0, credibility))

    def _calculate_confidence(self, news_item: Dict) -> float:
        """Calculate confidence in the prediction."""
        confidence = 0.5  # Base confidence

        # Higher confidence if we have more data
        if news_item.get("content"):
            confidence += 0.2

        if news_item.get("source"):
            confidence += 0.1

        if news_item.get("published_at"):
            confidence += 0.1

        # Lower confidence for very short titles
        title = news_item.get("title", "")
        if len(title.split()) < 5:
            confidence -= 0.2

        return min(1.0, max(0.0, confidence))

    def is_enabled(self) -> bool:
        """Check if local predictor is enabled."""
        return self.config.get("features", {}).get("local_predictor_enabled", False)


# Global predictor instance
_predictor_instance = None


def get_predictor() -> LocalPredictor:
    """Get global predictor instance."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = LocalPredictor()
    return _predictor_instance


def predict_news_item(news_item: Dict) -> PredictionResult:
    """
    Convenience function to predict importance and credibility.

    Args:
        news_item: Dictionary containing news item data

    Returns:
        PredictionResult with importance, credibility, and confidence scores
    """
    predictor = get_predictor()
    if not predictor.is_enabled():
        # Return neutral scores if disabled
        return PredictionResult(importance=0.5, credibility=0.5, confidence=0.0)

    return predictor.predict(news_item)

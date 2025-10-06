"""
Self-Tuning Data Collector for Local Predictor.

This module collects training data from various sources to train
and improve the local predictor model.
"""

import csv
import json
import logging
import re
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import yaml

logger = logging.getLogger("self_tuning_collector")


class SelfTuningCollector:
    """
    Collects training data for self-tuning the local predictor.

    Gathers examples from database, rejected logs, and cache to create
    a comprehensive dataset for model training.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize data collector with configuration."""
        self.config = self._load_config(config_path)
        self.dataset_path = Path("data/self_tuning_dataset.csv")
        self.rejected_log_path = Path("logs/rejected.log")

        # Configuration parameters
        self.min_samples = self.config.get("self_tuning", {}).get("min_samples", 500)
        self.max_samples = self.config.get("self_tuning", {}).get("max_samples", 10000)

        # Ensure data directory exists
        self.dataset_path.parent.mkdir(exist_ok=True)

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
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

    def _extract_features(self, news_item: Dict) -> Dict[str, float]:
        """
        Extract features from a news item for model training.

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

        # Source trust score (based on historical data)
        features["source_trust_score"] = self._calculate_source_trust_score(source)

        # Category encoding (one-hot like)
        category_scores = self._encode_category(category)
        features.update(category_scores)

        # Word frequency features
        word_features = self._extract_word_features(title, content)
        features.update(word_features)

        # Time-based features
        published_at = news_item.get("published_at", "")
        features["time_features"] = self._extract_time_features(published_at)

        return features

    def _calculate_source_trust_score(self, source: str) -> float:
        """
        Calculate trust score for a source based on historical data.

        Args:
            source: News source

        Returns:
            Trust score between 0 and 1
        """
        if not source:
            return 0.5  # Neutral score for unknown sources

        # This would ideally be calculated from historical data
        # For now, use a simple heuristic based on known good/bad sources

        # Known good sources (high trust)
        good_sources = {
            "reuters.com",
            "bloomberg.com",
            "wsj.com",
            "ft.com",
            "bbc.com",
            "cnn.com",
            "techcrunch.com",
            "wired.com",
            "espn.com",
            "nfl.com",
            "nba.com",
        }

        # Known suspicious sources (low trust)
        bad_sources = {
            "cryptoblog.fake.io",
            "earnmoney.today",
            "spamcrypto.com",
            "spamtech.blog",
            "fake-tech.com",
            "sportsfake.news",
        }

        source_lower = source.lower()

        if any(good in source_lower for good in good_sources):
            return 0.9
        elif any(bad in source_lower for bad in bad_sources):
            return 0.1
        else:
            return 0.5  # Neutral for unknown sources

    def _encode_category(self, category: str) -> Dict[str, float]:
        """
        Encode category as features.

        Args:
            category: News category

        Returns:
            Dictionary with category features
        """
        categories = ["crypto", "tech", "sports", "world", "markets"]

        features = {}
        for cat in categories:
            features[f"category_{cat}"] = 1.0 if category == cat else 0.0

        # Add unknown category feature
        features["category_unknown"] = 1.0 if category not in categories else 0.0

        return features

    def _extract_word_features(self, title: str, content: str) -> Dict[str, float]:
        """
        Extract word-based features.

        Args:
            title: News title
            content: News content

        Returns:
            Dictionary with word features
        """
        features = {}

        # Combine title and content
        text = f"{title} {content}".lower()

        # Word count features
        words = text.split()
        features["total_words"] = len(words)

        # Word frequency features for common words
        word_counts = Counter(words)

        # Important words that might indicate quality
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
        important_count = sum(word_counts.get(word, 0) for word in important_words)
        spam_count = sum(word_counts.get(word, 0) for word in spam_words)

        features["important_words_ratio"] = important_count / max(len(words), 1)
        features["spam_words_ratio"] = spam_count / max(len(words), 1)

        # Title-specific features
        title_words = title.lower().split()
        features["title_important_words"] = sum(1 for word in title_words if word in important_words)
        features["title_spam_words"] = sum(1 for word in title_words if word in spam_words)

        return features

    def _extract_time_features(self, published_at: str) -> float:
        """
        Extract time-based features.

        Args:
            published_at: Publication timestamp

        Returns:
            Time-based feature value
        """
        try:
            if not published_at:
                return 0.0

            # Parse timestamp
            dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

            # Extract hour (0-23)
            hour = dt.hour

            # Business hours vs off-hours (simplified feature)
            if 9 <= hour <= 17:  # Business hours
                return 1.0
            else:
                return 0.0

        except Exception as e:
            logger.debug(f"Error parsing timestamp {published_at}: {e}")
            return 0.0

    def _collect_from_database(self) -> List[Dict]:
        """
        Collect training examples from database.

        Returns:
            List of training examples with features and labels
        """
        examples = []

        try:
            # Import here to avoid circular imports
            from database.service import get_sync_service

            db_service = get_sync_service()

            # Get recent news with AI scores
            news_items = db_service.get_latest_news(limit=self.max_samples)

            for item in news_items:
                # Convert to dict if needed
                if hasattr(item, "model_dump"):
                    item_dict = item.model_dump()
                elif hasattr(item, "dict"):
                    item_dict = item.dict()
                else:
                    item_dict = dict(item)

                # Extract features
                features = self._extract_features(item_dict)

                # Get labels (AI scores)
                importance = item_dict.get("importance", 0.0)
                credibility = item_dict.get("credibility", 0.0)

                # Create binary labels (threshold-based)
                importance_label = 1.0 if importance >= 0.6 else 0.0
                credibility_label = 1.0 if credibility >= 0.7 else 0.0

                example = {
                    "features": features,
                    "importance_label": importance_label,
                    "credibility_label": credibility_label,
                    "importance_score": importance,
                    "credibility_score": credibility,
                    "source": "database",
                    "category": item_dict.get("category", "unknown"),
                    "title": item_dict.get("title", ""),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

                examples.append(example)

            logger.info(f"Collected {len(examples)} examples from database")

        except Exception as e:
            logger.error(f"Error collecting from database: {e}")

        return examples

    def _collect_from_rejected_log(self) -> List[Dict]:
        """
        Collect negative examples from rejected log.

        Returns:
            List of negative training examples
        """
        examples = []

        if not self.rejected_log_path.exists():
            logger.warning("rejected.log not found, skipping rejected examples")
            return examples

        try:
            with open(self.rejected_log_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or not line.startswith("["):
                        continue

                    try:
                        # Parse log line (reuse logic from rejection_analyzer)
                        parsed = self._parse_rejected_log_line(line)
                        if parsed:
                            # Extract features
                            features = self._extract_features(parsed)

                            # Create negative labels
                            example = {
                                "features": features,
                                "importance_label": 0.0,  # Rejected items are low importance
                                "credibility_label": 0.0,  # Rejected items are low credibility
                                "importance_score": 0.0,
                                "credibility_score": 0.0,
                                "source": "rejected_log",
                                "category": parsed.get("category", "unknown"),
                                "title": parsed.get("title", ""),
                                "timestamp": parsed.get("timestamp", ""),
                                "rejection_reason": parsed.get("reason", "unknown"),
                            }

                            examples.append(example)

                    except Exception as e:
                        logger.warning(f"Error parsing rejected log line {line_num}: {e}")
                        continue

            logger.info(f"Collected {len(examples)} negative examples from rejected log")

        except Exception as e:
            logger.error(f"Error collecting from rejected log: {e}")

        return examples

    def _parse_rejected_log_line(self, line: str) -> Optional[Dict]:
        """
        Parse a rejected log line (reused from rejection_analyzer).

        Args:
            line: Log line string

        Returns:
            Dictionary with parsed data or None if parsing fails
        """
        try:
            # Extract timestamp
            timestamp_match = re.match(r"\[([^\]]+)\]", line)
            if not timestamp_match:
                return None

            timestamp = timestamp_match.group(1)

            # Extract key-value pairs after "REJECTED:"
            if "REJECTED:" not in line:
                return None

            data_part = line.split("REJECTED:", 1)[1].strip()

            # Parse key-value pairs
            data = {}
            for pair in data_part.split():
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    value = value.strip("\"'")
                    data[key] = value

            # Extract title from the end if present
            title_match = re.search(r'title="([^"]+)"', line)
            if title_match:
                data["title"] = title_match.group(1)

            data["timestamp"] = timestamp
            return data

        except Exception as e:
            logger.debug(f"Error parsing log line: {e}")
            return None

    def collect_training_data(self) -> Dict[str, Any]:
        """
        Collect comprehensive training dataset.

        Returns:
            Dictionary with collection results and dataset info
        """
        logger.info("Starting training data collection...")

        # Collect from different sources
        db_examples = self._collect_from_database()
        rejected_examples = self._collect_from_rejected_log()

        # Combine all examples
        all_examples = db_examples + rejected_examples

        if len(all_examples) < self.min_samples:
            logger.warning(f"Insufficient training data: {len(all_examples)} < {self.min_samples}")
            return {
                "success": False,
                "error": f"Insufficient data: {len(all_examples)} < {self.min_samples}",
                "dataset_size": len(all_examples),
                "db_examples": len(db_examples),
                "rejected_examples": len(rejected_examples),
            }

        # Limit dataset size for performance
        if len(all_examples) > self.max_samples:
            logger.info(f"Limiting dataset to {self.max_samples} examples")
            all_examples = all_examples[: self.max_samples]

        # Save dataset to CSV
        self._save_dataset(all_examples)

        # Calculate dataset statistics
        stats = self._calculate_dataset_stats(all_examples)

        result = {
            "success": True,
            "dataset_size": len(all_examples),
            "db_examples": len(db_examples),
            "rejected_examples": len(rejected_examples),
            "dataset_path": str(self.dataset_path),
            "statistics": stats,
        }

        logger.info(f"Training data collection completed: {len(all_examples)} examples")
        return result

    def _save_dataset(self, examples: List[Dict]) -> None:
        """
        Save dataset to CSV file.

        Args:
            examples: List of training examples
        """
        if not examples:
            return

        # Get all feature keys from first example
        feature_keys = list(examples[0]["features"].keys())

        # Define CSV columns
        columns = [
            "importance_label",
            "credibility_label",
            "importance_score",
            "credibility_score",
            "source",
            "category",
            "title",
            "timestamp",
        ] + feature_keys

        try:
            with open(self.dataset_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()

                for example in examples:
                    row = {
                        "importance_label": example["importance_label"],
                        "credibility_label": example["credibility_label"],
                        "importance_score": example["importance_score"],
                        "credibility_score": example["credibility_score"],
                        "source": example["source"],
                        "category": example["category"],
                        "title": example["title"],
                        "timestamp": example["timestamp"],
                    }

                    # Add features
                    row.update(example["features"])

                    writer.writerow(row)

            logger.info(f"Dataset saved to {self.dataset_path}")

        except Exception as e:
            logger.error(f"Error saving dataset: {e}")

    def _calculate_dataset_stats(self, examples: List[Dict]) -> Dict[str, Any]:
        """
        Calculate dataset statistics.

        Args:
            examples: List of training examples

        Returns:
            Dictionary with dataset statistics
        """
        stats = {
            "total_examples": len(examples),
            "importance_positive": sum(1 for ex in examples if ex["importance_label"] == 1.0),
            "credibility_positive": sum(1 for ex in examples if ex["credibility_label"] == 1.0),
            "sources": {},
            "categories": {},
            "avg_importance_score": 0.0,
            "avg_credibility_score": 0.0,
        }

        if examples:
            # Source distribution
            source_counts = Counter(ex["source"] for ex in examples)
            stats["sources"] = dict(source_counts)

            # Category distribution
            category_counts = Counter(ex["category"] for ex in examples)
            stats["categories"] = dict(category_counts)

            # Average scores
            stats["avg_importance_score"] = sum(ex["importance_score"] for ex in examples) / len(examples)
            stats["avg_credibility_score"] = sum(ex["credibility_score"] for ex in examples) / len(examples)

        return stats

    def is_enabled(self) -> bool:
        """Check if self-tuning is enabled."""
        return self.config.get("features", {}).get("self_tuning_enabled", True)

    def get_dataset_path(self) -> Path:
        """Get path to dataset file."""
        return self.dataset_path


# Global collector instance
_collector_instance: Optional[SelfTuningCollector] = None


def get_self_tuning_collector() -> SelfTuningCollector:
    """Get global self-tuning collector instance."""
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = SelfTuningCollector()
    return _collector_instance


def collect_training_data() -> Dict[str, Any]:
    """
    Convenience function to collect training data.

    Returns:
        Dictionary with collection results
    """
    collector = get_self_tuning_collector()
    if not collector.is_enabled():
        logger.info("Self-tuning is disabled, skipping data collection")
        return {"success": False, "error": "Self-tuning disabled"}

    return collector.collect_training_data()

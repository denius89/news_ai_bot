"""
Adaptive thresholds module for AI optimization.

This module provides category-specific thresholds for importance and credibility
evaluation, allowing different thresholds for different news categories.
"""

import logging
import yaml
from typing import Dict, Tuple, Optional
from pathlib import Path

logger = logging.getLogger("adaptive_thresholds")


class AdaptiveThresholds:
    """
    Manages adaptive thresholds for different news categories.

    Provides category-specific thresholds for importance and credibility
    evaluation, with fallback to default thresholds.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize adaptive thresholds with configuration."""
        self.config = self._load_config(config_path)
        self.category_thresholds = self.config.get("category_thresholds", {})
        self.default_thresholds = self.config.get("default_thresholds", {"importance": 0.6, "credibility": 0.7})

        # Override with environment variables if present
        import os

        env_importance = os.getenv("AI_IMPORTANCE_THRESHOLD")
        env_credibility = os.getenv("AI_CREDIBILITY_THRESHOLD")

        if env_importance:
            self.default_thresholds["importance"] = float(env_importance)
            logger.info(f"[THRESHOLD] Using env AI_IMPORTANCE_THRESHOLD: {env_importance}")

        if env_credibility:
            self.default_thresholds["credibility"] = float(env_credibility)
            logger.info(f"[THRESHOLD] Using env AI_CREDIBILITY_THRESHOLD: {env_credibility}")

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

    def get_thresholds(self, category: Optional[str] = None) -> Tuple[float, float]:
        """
        Get thresholds for a specific category.

        Args:
            category: News category (e.g., 'crypto', 'tech', 'world')

        Returns:
            Tuple of (importance_threshold, credibility_threshold)
        """
        if not self.is_enabled():
            return self.default_thresholds["importance"], self.default_thresholds["credibility"]

        if not category:
            return self.default_thresholds["importance"], self.default_thresholds["credibility"]

        # Normalize category name
        category_lower = category.lower().strip()

        # Check if category has specific thresholds
        if category_lower in self.category_thresholds:
            thresholds = self.category_thresholds[category_lower]
            importance = thresholds.get("importance", self.default_thresholds["importance"])
            credibility = thresholds.get("credibility", self.default_thresholds["credibility"])

            logger.debug(f"[THRESHOLD] category={category_lower} importance>{importance} credibility>{credibility}")
            return importance, credibility

        # Use default thresholds
        logger.debug(f"[THRESHOLD] category={category_lower} using default thresholds")
        return self.default_thresholds["importance"], self.default_thresholds["credibility"]

    def check_thresholds(
        self, importance: float, credibility: float, category: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Check if scores meet thresholds for the category.

        Args:
            importance: Importance score
            credibility: Credibility score
            category: News category

        Returns:
            Tuple of (passed, reason)
        """
        importance_threshold, credibility_threshold = self.get_thresholds(category)

        if importance < importance_threshold:
            return False, "importance_below_threshold"

        if credibility < credibility_threshold:
            return False, "credibility_below_threshold"

        return True, "thresholds_passed"

    def is_enabled(self) -> bool:
        """Check if adaptive thresholds are enabled."""
        return self.config.get("features", {}).get("adaptive_thresholds_enabled", True)

    def get_category_list(self) -> list:
        """Get list of categories with specific thresholds."""
        return list(self.category_thresholds.keys())

    def get_stats(self) -> Dict:
        """Get statistics about threshold usage."""
        return {
            "enabled": self.is_enabled(),
            "categories_with_thresholds": len(self.category_thresholds),
            "default_thresholds": self.default_thresholds,
            "category_thresholds": self.category_thresholds,
        }


# Global adaptive thresholds instance
_adaptive_thresholds_instance: Optional[AdaptiveThresholds] = None


def get_adaptive_thresholds() -> AdaptiveThresholds:
    """Get global adaptive thresholds instance."""
    global _adaptive_thresholds_instance
    if _adaptive_thresholds_instance is None:
        _adaptive_thresholds_instance = AdaptiveThresholds()
    return _adaptive_thresholds_instance


def get_thresholds_for_category(category: Optional[str] = None) -> Tuple[float, float]:
    """
    Convenience function to get thresholds for a category.

    Args:
        category: News category

    Returns:
        Tuple of (importance_threshold, credibility_threshold)
    """
    adaptive_thresholds = get_adaptive_thresholds()
    return adaptive_thresholds.get_thresholds(category)


def check_category_thresholds(
    importance: float, credibility: float, category: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Convenience function to check thresholds for a category.

    Args:
        importance: Importance score
        credibility: Credibility score
        category: News category

    Returns:
        Tuple of (passed, reason)
    """
    adaptive_thresholds = get_adaptive_thresholds()
    return adaptive_thresholds.check_thresholds(importance, credibility, category)

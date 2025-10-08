"""
Smart Post Selector for prioritizing digest posts.

This module implements intelligent selection of digests based on
importance, credibility, and engagement metrics.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

from ai_modules.metrics import get_metrics

logger = logging.getLogger("post_selector")


@dataclass
class SelectionResult:
    """Result of post selection process."""

    selected_digests: List[Dict[str, Any]]
    skipped_count: int
    selection_reason: str
    avg_score: float


class PostSelector:
    """
    Smart post selector for prioritizing digest posts.

    Features:
    - Importance and credibility scoring
    - Engagement score integration
    - Recent publication avoidance
    - Quality-based filtering
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize post selector with configuration."""
        self.config = self._load_config(config_path)
        self.metrics = get_metrics()

        # Configuration
        self.smart_posting_config = self.config.get("smart_posting", {})
        self.enabled = self.smart_posting_config.get("enabled", False)

        # Selection parameters
        self.max_posts_per_cycle = 3
        self.min_importance_threshold = 0.6
        self.min_credibility_threshold = 0.7
        self.engagement_weight = 0.2

        # Recently published tracking
        self.recently_published = set()

        logger.info(f"PostSelector initialized: enabled={self.enabled}")

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "ai_optimization.yaml"

        try:
            import yaml

            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def _calculate_priority_score(self, digest: Dict[str, Any]) -> float:
        """
        Calculate priority score for a digest.

        Args:
            digest: Digest data dictionary

        Returns:
            Priority score (0.0 - 1.0)
        """
        try:
            # Base scores
            importance = digest.get("importance", 0.0)
            credibility = digest.get("credibility", 0.0)

            # Engagement score (if available)
            engagement_score = digest.get("engagement_score", 0.5)

            # Calculate weighted score
            base_score = (importance * credibility) ** 0.5  # Geometric mean
            engagement_bonus = engagement_score * self.engagement_weight

            priority_score = base_score + engagement_bonus

            # Apply category bonuses
            category = digest.get("category", "").lower()
            category_bonuses = {
                "crypto": 0.05,
                "tech": 0.03,
                "world": 0.02,
                "markets": 0.04,
                "sports": 0.01}

            if category in category_bonuses:
                priority_score += category_bonuses[category]

            # Apply source reputation bonus
            source = digest.get("source", "").lower()
            if any(
                reputable in source for reputable in [
                    "reuters",
                    "bloomberg",
                    "wsj",
                    "ft",
                    "bbc",
                    "cnn"]):
                priority_score += 0.03

            # Normalize to 0.0-1.0 range
            return min(1.0, max(0.0, priority_score))

        except Exception as e:
            logger.error(f"Error calculating priority score: {e}")
            return 0.0

    def _is_digest_eligible(self, digest: Dict[str, Any]) -> bool:
        """
        Check if digest is eligible for selection.

        Args:
            digest: Digest data dictionary

        Returns:
            True if eligible, False otherwise
        """
        try:
            digest_id = digest.get("id")

            # Check if recently published
            if digest_id and digest_id in self.recently_published:
                return False

            # Check importance threshold
            importance = digest.get("importance", 0.0)
            if importance < self.min_importance_threshold:
                return False

            # Check credibility threshold
            credibility = digest.get("credibility", 0.0)
            if credibility < self.min_credibility_threshold:
                return False

            # Check if already published
            if digest.get("published", False):
                return False

            # Check status
            if digest.get("status") != "ready":
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking digest eligibility: {e}")
            return False

    def select_digests(self, digests: List[Dict[str, Any]]) -> SelectionResult:
        """
        Select best digests from available options.

        Args:
            digests: List of available digest dictionaries

        Returns:
            SelectionResult with selected digests and metadata
        """
        try:
            if not self.enabled:
                # Return first few digests if disabled
                selected = digests[: self.max_posts_per_cycle]
                return SelectionResult(
                    selected_digests=selected,
                    skipped_count=len(digests) - len(selected),
                    selection_reason="smart_selection_disabled",
                    avg_score=0.0,
                )

            # Filter eligible digests
            eligible_digests = [d for d in digests if self._is_digest_eligible(d)]

            if not eligible_digests:
                logger.info("No eligible digests found for selection")
                return SelectionResult(
                    selected_digests=[],
                    skipped_count=len(digests),
                    selection_reason="no_eligible_digests",
                    avg_score=0.0,
                )

            # Calculate priority scores
            scored_digests = []
            for digest in eligible_digests:
                score = self._calculate_priority_score(digest)
                scored_digests.append((digest, score))

            # Sort by priority score (descending)
            scored_digests.sort(key=lambda x: x[1], reverse=True)

            # Select top digests
            selected_digests = []
            total_score = 0.0

            for digest, score in scored_digests[: self.max_posts_per_cycle]:
                selected_digests.append(digest)
                total_score += score

            # Calculate average score
            avg_score = total_score / len(selected_digests) if selected_digests else 0.0

            # Update metrics
            self.metrics.update_smart_priority_avg_score(avg_score)
            self.metrics.increment_smart_priority_skipped_total(
                len(digests) - len(selected_digests))

            logger.info(
                f"Selected {len(selected_digests)} digests from {len(digests)} available (avg score: {avg_score:.3f})"
            )

            return SelectionResult(
                selected_digests=selected_digests,
                skipped_count=len(digests) - len(selected_digests),
                selection_reason="priority_based_selection",
                avg_score=avg_score,
            )

        except Exception as e:
            logger.error(f"Error selecting digests: {e}")
            return SelectionResult(
                selected_digests=[],
                skipped_count=len(digests),
                selection_reason="selection_error",
                avg_score=0.0)

    def mark_digest_published(self, digest_id: int) -> None:
        """
        Mark digest as published and add to recently published set.

        Args:
            digest_id: ID of the published digest
        """
        try:
            self.recently_published.add(digest_id)

            # Clean up old entries (keep only last 100)
            if len(self.recently_published) > 100:
                recent_list = list(self.recently_published)
                self.recently_published = set(recent_list[-100:])

            logger.debug(f"Marked digest {digest_id} as published")

        except Exception as e:
            logger.error(f"Error marking digest {digest_id} as published: {e}")

    def get_selection_stats(self) -> Dict[str, Any]:
        """Get selection statistics."""
        return {
            "enabled": self.enabled,
            "max_posts_per_cycle": self.max_posts_per_cycle,
            "min_importance_threshold": self.min_importance_threshold,
            "min_credibility_threshold": self.min_credibility_threshold,
            "engagement_weight": self.engagement_weight,
            "recently_published_count": len(self.recently_published),
        }

    def reset_recently_published(self) -> None:
        """Reset recently published set (useful for testing)."""
        self.recently_published.clear()
        logger.info("Reset recently published digests")


# Global post selector instance
_post_selector_instance: Optional[PostSelector] = None


def get_post_selector() -> PostSelector:
    """Get global post selector instance."""
    global _post_selector_instance
    if _post_selector_instance is None:
        _post_selector_instance = PostSelector()
    return _post_selector_instance


def select_best_digests(digests: List[Dict[str, Any]]) -> SelectionResult:
    """
    Convenience function to select best digests.

    Args:
        digests: List of available digest dictionaries

    Returns:
        SelectionResult with selected digests
    """
    selector = get_post_selector()
    return selector.select_digests(digests)

"""
ML-based Importance Evaluator v2 for PulseAI Events.

This module provides improved importance evaluation using multiple ML features
instead of relying solely on AI prompts.
"""

import logging
from typing import Dict

logger = logging.getLogger("importance_v2")


class ImportanceEvaluatorV2:
    """
    ML-based importance evaluator v2.
    Uses multiple features for better accuracy without expensive AI calls.
    """

    # Ключевые слова по категориям (высокая важность)
    HIGH_IMPORTANCE_KEYWORDS = {
        'crypto': [
            'mainnet', 'launch', 'upgrade', 'hard fork', 'airdrop', 'listing',
            'halving', 'merge', 'snapshot', 'token unlock', 'ipo', 'ico'
        ],
        'sports': [
            'final', 'championship', 'world cup', 'olympics', 'playoff',
            'grand slam', 'super bowl', 'champions league', 'world series'
        ],
        'markets': [
            'fed', 'rate decision', 'gdp', 'inflation', 'earnings', 'ipo',
            'fomc', 'ecb', 'central bank', 'jobs report', 'cpi', 'ppi'
        ],
        'tech': [
            'release', 'launch', 'conference', 'wwdc', 'build', 'google i/o',
            'keynote', 'announcement', 'unveil', 'reveal'
        ],
        'world': [
            'election', 'summit', 'treaty', 'crisis', 'war', 'peace',
            'referendum', 'vote', 'g7', 'g20', 'un', 'nato'
        ]
    }

    # Средняя важность
    MEDIUM_IMPORTANCE_KEYWORDS = {
        'crypto': ['update', 'partnership', 'integration', 'testnet'],
        'sports': ['semifinal', 'quarterfinal', 'derby', 'rivalry'],
        'markets': ['report', 'data', 'index', 'survey'],
        'tech': ['update', 'beta', 'preview', 'demo'],
        'world': ['meeting', 'talks', 'discussion', 'statement']
    }

    def evaluate_importance(self, event: Dict) -> float:
        """
        Evaluate event importance using ML features.

        Args:
            event: Event dictionary with title, description, category, etc.

        Returns:
            float: Importance score [0.0, 1.0]
        """
        try:
            features = self._extract_features(event)
            score = self._calculate_score(features)
            return max(0.0, min(1.0, score))
        except Exception as e:
            logger.error(f"Error evaluating importance: {e}")
            return 0.5  # Fallback to neutral

    def _extract_features(self, event: Dict) -> Dict:
        """Extract ML features from event."""
        title = event.get('title', '').lower()
        description = event.get('description', '').lower()
        category = event.get('category', '').lower()
        subcategory = event.get('subcategory', '').lower()
        metadata = event.get('metadata', {})

        # Combine text for keyword analysis
        full_text = f"{title} {description}"

        return {
            'title_length': len(title),
            'description_length': len(description),
            'has_description': bool(description),
            'high_keyword_count': self._count_keywords(full_text, category, 'high'),
            'medium_keyword_count': self._count_keywords(full_text, category, 'medium'),
            'category': category,
            'subcategory': subcategory,
            'has_metadata': bool(metadata),
            'metadata_richness': len(metadata),
            'source_importance': float(event.get('importance', 0.5)),
            'has_location': bool(event.get('location')),
            'has_organizer': bool(event.get('organizer')),
        }

    def _count_keywords(self, text: str, category: str, level: str) -> int:
        """Count importance keywords in text."""
        if level == 'high':
            keywords = self.HIGH_IMPORTANCE_KEYWORDS.get(category, [])
        else:
            keywords = self.MEDIUM_IMPORTANCE_KEYWORDS.get(category, [])

        count = sum(1 for keyword in keywords if keyword in text)
        return count

    def _calculate_score(self, features: Dict) -> float:
        """
        Calculate importance score from features.

        Uses weighted combination of multiple signals.
        """
        # Start with provider's base importance
        score = features['source_importance']

        # High importance keywords (strong signal)
        if features['high_keyword_count'] > 0:
            score += 0.15 * min(features['high_keyword_count'], 3)

        # Medium importance keywords (moderate signal)
        if features['medium_keyword_count'] > 0:
            score += 0.05 * min(features['medium_keyword_count'], 2)

        # Description quality bonus
        if features['has_description']:
            if features['description_length'] > 200:
                score += 0.1
            elif features['description_length'] > 100:
                score += 0.05

        # Metadata richness (indicates well-structured event)
        if features['metadata_richness'] >= 5:
            score += 0.08
        elif features['metadata_richness'] >= 3:
            score += 0.04

        # Location and organizer (indicates official event)
        if features['has_location'] and features['has_organizer']:
            score += 0.05

        # Category-specific adjustments
        if features['category'] in ['markets', 'world']:
            score += 0.05  # Financial and geopolitical events tend to be important
        elif features['category'] == 'crypto' and 'defi' in features['subcategory']:
            score += 0.03  # DeFi events are often significant

        # Title length penalty (very short titles might be incomplete)
        if features['title_length'] < 20:
            score -= 0.05

        return score


# Global instance for easy import
evaluator_v2 = ImportanceEvaluatorV2()


def evaluate_event_importance(event: Dict) -> float:
    """
    Convenience function to evaluate event importance.

    Args:
        event: Event dictionary

    Returns:
        float: Importance score [0.0, 1.0]
    """
    return evaluator_v2.evaluate_importance(event)


__all__ = ['ImportanceEvaluatorV2', 'evaluator_v2', 'evaluate_event_importance']

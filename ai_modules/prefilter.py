"""
Pre-filter module for AI optimization.

This module provides lightweight filtering before AI calls to reduce
unnecessary API requests while maintaining quality.
"""

import logging
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger("prefilter")


@dataclass
class PrefilterResult:
    """Result of pre-filtering."""
    passed: bool
    reason: str
    score: float = 0.0


class Prefilter:
    """
    Lightweight pre-filter for news items before AI analysis.
    
    Uses simple rules and heuristics to filter out low-quality
    or irrelevant news items without calling AI.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize prefilter with configuration."""
        self.config = self._load_config(config_path)
        self.stop_markers = set(self.config.get('prefilter', {}).get('stop_markers', []))
        self.importance_markers = self.config.get('prefilter', {}).get('importance_markers', {})
        self.min_title_words = self.config.get('prefilter', {}).get('min_title_words', 6)
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "ai_optimization.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def filter_news(self, news_item: Dict) -> PrefilterResult:
        """
        Filter a single news item.
        
        Args:
            news_item: Dictionary containing news item data
            
        Returns:
            PrefilterResult with pass/fail decision and reason
        """
        title = news_item.get('title', '').strip()
        content = news_item.get('content', '') or news_item.get('summary', '')
        source = news_item.get('source', '').lower()
        category = news_item.get('category', '').lower()
        
        # Check minimum title length
        if len(title.split()) < self.min_title_words:
            return PrefilterResult(
                passed=False,
                reason="pre_filter",
                score=0.0
            )
        
        # Check for stop markers
        title_lower = title.lower()
        content_lower = content.lower()
        
        for marker in self.stop_markers:
            if marker in title_lower or marker in content_lower:
                return PrefilterResult(
                    passed=False,
                    reason="pre_filter",
                    score=0.0
                )
        
        # Calculate relevance score based on importance markers
        score = self._calculate_relevance_score(title, content, category)
        
        # If score is too low, filter out
        if score < 0.3:  # Minimum relevance threshold
            return PrefilterResult(
                passed=False,
                reason="pre_filter",
                score=score
            )
        
        return PrefilterResult(
            passed=True,
            reason="pre_filter_pass",
            score=score
        )
    
    def _calculate_relevance_score(self, title: str, content: str, category: str) -> float:
        """
        Calculate relevance score based on importance markers.
        
        Args:
            title: News title
            content: News content
            category: News category
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        score = 0.0
        text = f"{title} {content}".lower()
        
        # Get category-specific markers
        markers = self.importance_markers.get(category, [])
        
        # Count marker matches
        matches = 0
        for marker in markers:
            if marker.lower() in text:
                matches += 1
        
        # Calculate score based on matches
        if matches > 0:
            score = min(0.8, 0.3 + (matches * 0.1))  # Base 0.3 + 0.1 per match
        
        # Boost score for certain high-impact keywords
        high_impact_keywords = [
            'breaking', 'urgent', 'critical', 'major', 'significant',
            'unprecedented', 'historic', 'record', 'first', 'new'
        ]
        
        for keyword in high_impact_keywords:
            if keyword in text:
                score = min(1.0, score + 0.2)
                break
        
        return score
    
    def is_enabled(self) -> bool:
        """Check if prefilter is enabled."""
        return self.config.get('features', {}).get('prefilter_enabled', True)


# Global prefilter instance
_prefilter_instance: Optional[Prefilter] = None


def get_prefilter() -> Prefilter:
    """Get global prefilter instance."""
    global _prefilter_instance
    if _prefilter_instance is None:
        _prefilter_instance = Prefilter()
    return _prefilter_instance


def filter_news_item(news_item: Dict) -> PrefilterResult:
    """
    Convenience function to filter a news item.
    
    Args:
        news_item: Dictionary containing news item data
        
    Returns:
        PrefilterResult with pass/fail decision and reason
    """
    prefilter = get_prefilter()
    if not prefilter.is_enabled():
        return PrefilterResult(passed=True, reason="prefilter_disabled")
    
    return prefilter.filter_news(news_item)

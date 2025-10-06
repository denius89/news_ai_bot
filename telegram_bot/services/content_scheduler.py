"""
Content Scheduler for Smart Content Posting.

This module implements intelligent scheduling based on time of day
and category optimization for maximum engagement.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

import yaml
from pathlib import Path

from ai_modules.metrics import get_metrics

logger = logging.getLogger("content_scheduler")


@dataclass
class TimeWindow:
    """Represents a time window for content publishing."""
    name: str
    start_hour: int
    end_hour: int
    categories: List[str]
    description: str


class ContentScheduler:
    """
    Intelligent content scheduler based on time of day and categories.
    
    Features:
    - Time-based category distribution
    - Window-based posting optimization
    - Metadata tracking for next post windows
    - Metrics for scheduling analytics
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize content scheduler with configuration."""
        self.config = self._load_config(config_path)
        self.metrics = get_metrics()
        
        # Configuration
        self.smart_posting_config = self.config.get('smart_posting', {})
        self.enabled = self.smart_posting_config.get('enabled', False)
        self.adaptive_schedule = self.smart_posting_config.get('adaptive_schedule', True)
        
        # Schedule configuration
        self.schedule_config = self.config.get('autopublish_schedule', {})
        
        # Initialize time windows
        self.time_windows = self._initialize_time_windows()
        
        # Track current window and recent posts
        self.current_window = None
        self.recently_published = set()
        
        logger.info(f"ContentScheduler initialized: enabled={self.enabled}")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "ai_optimization.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _initialize_time_windows(self) -> List[TimeWindow]:
        """Initialize time windows from configuration."""
        windows = []
        
        # Default schedule if not configured
        default_schedule = {
            'morning': {
                'start_hour': 6,
                'end_hour': 12,
                'categories': ['world', 'markets'],
                'description': 'Morning news and market updates'
            },
            'day': {
                'start_hour': 12,
                'end_hour': 18,
                'categories': ['tech', 'crypto'],
                'description': 'Technology and crypto developments'
            },
            'evening': {
                'start_hour': 18,
                'end_hour': 22,
                'categories': ['sports', 'world'],
                'description': 'Evening sports and world news'
            },
            'night': {
                'start_hour': 22,
                'end_hour': 6,
                'categories': ['crypto', 'tech'],
                'description': 'Late night crypto and tech updates'
            }
        }
        
        schedule = self.schedule_config if self.schedule_config else default_schedule
        
        for window_name, window_config in schedule.items():
            window = TimeWindow(
                name=window_name,
                start_hour=window_config.get('start_hour', 0),
                end_hour=window_config.get('end_hour', 23),
                categories=window_config.get('categories', []),
                description=window_config.get('description', f'{window_name} content')
            )
            windows.append(window)
            logger.info(f"Initialized time window: {window_name} ({window.start_hour}:00-{window.end_hour}:00) -> {window.categories}")
        
        return windows
    
    def _get_current_window(self) -> Optional[TimeWindow]:
        """Get the current time window based on current time."""
        now = datetime.now(timezone.utc)
        current_hour = now.hour
        
        for window in self.time_windows:
            if window.start_hour <= window.end_hour:
                # Normal window (e.g., 9-17)
                if window.start_hour <= current_hour < window.end_hour:
                    return window
            else:
                # Overnight window (e.g., 22-6)
                if current_hour >= window.start_hour or current_hour < window.end_hour:
                    return window
        
        # Fallback to first window if no match
        return self.time_windows[0] if self.time_windows else None
    
    def _is_category_in_current_window(self, category: str) -> bool:
        """Check if a category is appropriate for the current time window."""
        current_window = self._get_current_window()
        if not current_window:
            return True  # Allow all categories if no window found
        
        return category.lower() in [cat.lower() for cat in current_window.categories]
    
    def _should_skip_digest(self, digest: Dict[str, Any]) -> bool:
        """
        Check if digest should be skipped based on scheduling rules.
        
        Args:
            digest: Digest data
            
        Returns:
            True if should skip, False otherwise
        """
        try:
            # Check if already published recently
            digest_id = digest.get('id')
            if digest_id and digest_id in self.recently_published:
                logger.debug(f"Skipping digest {digest_id}: already published recently")
                return True
            
            # Check category against current window
            category = digest.get('category', 'unknown').lower()
            if not self._is_category_in_current_window(category):
                logger.debug(f"Skipping digest {digest_id}: category '{category}' not in current window")
                self.metrics.increment_autopublish_skipped_out_of_window()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if should skip digest: {e}")
            return False
    
    def filter_digests_by_schedule(self, digests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter digests based on current time window and scheduling rules.
        
        Args:
            digests: List of digest dictionaries
            
        Returns:
            Filtered list of digests appropriate for current time
        """
        if not self.enabled:
            logger.debug("Content scheduler disabled, returning all digests")
            return digests
        
        current_window = self._get_current_window()
        if not current_window:
            logger.warning("No current time window found, returning all digests")
            return digests
        
        # Update metrics
        self.current_window = current_window.name
        self.metrics.update_autopublish_window_current(current_window.name)
        
        filtered_digests = []
        skipped_count = 0
        
        for digest in digests:
            if self._should_skip_digest(digest):
                skipped_count += 1
                continue
            
            filtered_digests.append(digest)
        
        logger.info(f"Filtered digests: {len(filtered_digests)} suitable, {skipped_count} skipped for window '{current_window.name}'")
        
        return filtered_digests
    
    def mark_digest_published(self, digest_id: int) -> None:
        """
        Mark digest as published and update scheduling state.
        
        Args:
            digest_id: ID of the published digest
        """
        try:
            # Add to recently published set
            self.recently_published.add(digest_id)
            
            # Update metrics
            self.metrics.increment_autopublish_window_posts_total()
            
            # Clean up old entries (keep only last 50)
            if len(self.recently_published) > 50:
                # Convert to list, remove oldest entries
                recent_list = list(self.recently_published)
                self.recently_published = set(recent_list[-50:])
            
            logger.debug(f"Marked digest {digest_id} as published in window '{self.current_window}'")
            
        except Exception as e:
            logger.error(f"Error marking digest {digest_id} as published: {e}")
    
    def get_next_post_window(self) -> Optional[TimeWindow]:
        """
        Get the next appropriate time window for posting.
        
        Returns:
            Next time window or None if no windows available
        """
        current_window = self._get_current_window()
        if not current_window or not self.time_windows:
            return None
        
        try:
            # Find current window index
            current_index = -1
            for i, window in enumerate(self.time_windows):
                if window.name == current_window.name:
                    current_index = i
                    break
            
            if current_index == -1:
                return self.time_windows[0]
            
            # Get next window (wrap around)
            next_index = (current_index + 1) % len(self.time_windows)
            return self.time_windows[next_index]
            
        except Exception as e:
            logger.error(f"Error getting next post window: {e}")
            return None
    
    def get_schedule_info(self) -> Dict[str, Any]:
        """
        Get current schedule information for analytics.
        
        Returns:
            Dictionary with schedule information
        """
        current_window = self._get_current_window()
        next_window = self.get_next_post_window()
        
        return {
            'enabled': self.enabled,
            'current_window': current_window.name if current_window else None,
            'current_categories': current_window.categories if current_window else [],
            'next_window': next_window.name if next_window else None,
            'next_categories': next_window.categories if next_window else [],
            'recently_published_count': len(self.recently_published),
            'total_windows': len(self.time_windows)
        }
    
    def reset_recent_published(self) -> None:
        """Reset the recently published set (useful for testing)."""
        self.recently_published.clear()
        logger.info("Reset recently published digests")


# Global scheduler instance
_scheduler_instance: Optional[ContentScheduler] = None


def get_content_scheduler() -> ContentScheduler:
    """Get global content scheduler instance."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = ContentScheduler()
    return _scheduler_instance


def filter_digests_by_schedule(digests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convenience function to filter digests by schedule.
    
    Args:
        digests: List of digest dictionaries
        
    Returns:
        Filtered list of digests
    """
    scheduler = get_content_scheduler()
    return scheduler.filter_digests_by_schedule(digests)

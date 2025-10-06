"""
Feedback Tracker for monitoring user reactions and engagement.

This module tracks user reactions to posts and updates engagement scores
for better content prioritization and AI model training.
"""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

from ai_modules.metrics import get_metrics

logger = logging.getLogger("feedback_tracker")


@dataclass
class ReactionData:
    """Represents reaction data for a post."""
    digest_id: int
    likes: int = 0
    dislikes: int = 0
    fire: int = 0
    bored: int = 0
    total_reactions: int = 0
    engagement_score: float = 0.0
    last_updated: Optional[datetime] = None


class FeedbackTracker:
    """
    Tracks user reactions and calculates engagement scores.
    
    Features:
    - Reaction monitoring via Telegram API
    - Engagement score calculation
    - Database integration for feedback storage
    - AI model training data preparation
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize feedback tracker with configuration."""
        self.config = self._load_config(config_path)
        self.metrics = get_metrics()
        
        # Configuration
        self.smart_posting_config = self.config.get('smart_posting', {})
        self.enabled = self.smart_posting_config.get('reaction_tracking', False)
        
        # Bot instance
        self.bot = None
        
        # Reaction tracking
        self.tracked_posts: Dict[int, ReactionData] = {}
        self.reaction_weights = {
            'like': 1.0,
            'dislike': -0.5,
            'fire': 2.0,
            'bored': -1.0
        }
        
        # Update interval (in minutes)
        self.update_interval_min = 30
        
        logger.info(f"FeedbackTracker initialized: enabled={self.enabled}")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "ai_optimization.yaml"
        
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def set_bot(self, bot: Bot) -> None:
        """Set bot instance for accessing message reactions."""
        self.bot = bot
    
    async def start_tracking(self, digest_id: int, message_id: int, chat_id: int) -> None:
        """
        Start tracking reactions for a published digest.
        
        Args:
            digest_id: ID of the digest
            message_id: Telegram message ID
            chat_id: Telegram chat ID
        """
        try:
            if not self.enabled:
                return
            
            # Create reaction data
            reaction_data = ReactionData(
                digest_id=digest_id,
                last_updated=datetime.now(timezone.utc)
            )
            
            # Store tracking data
            self.tracked_posts[digest_id] = reaction_data
            
            # Start periodic updates
            asyncio.create_task(self._periodic_update(digest_id, message_id, chat_id))
            
            logger.info(f"Started tracking reactions for digest {digest_id}")
            
        except Exception as e:
            logger.error(f"Error starting reaction tracking: {e}")
    
    async def _periodic_update(self, digest_id: int, message_id: int, chat_id: int) -> None:
        """Periodically update reaction data."""
        try:
            # Track for 24 hours
            end_time = datetime.now(timezone.utc) + timedelta(hours=24)
            
            while datetime.now(timezone.utc) < end_time:
                # Update reactions
                await self._update_reactions(digest_id, message_id, chat_id)
                
                # Wait for next update
                await asyncio.sleep(self.update_interval_min * 60)
            
            # Final update and cleanup
            await self._finalize_tracking(digest_id)
            
        except Exception as e:
            logger.error(f"Error in periodic update for digest {digest_id}: {e}")
    
    async def _update_reactions(self, digest_id: int, message_id: int, chat_id: int) -> None:
        """Update reaction data from Telegram."""
        try:
            if not self.bot or digest_id not in self.tracked_posts:
                return
            
            # Get message reactions
            reactions = await self._get_message_reactions(message_id, chat_id)
            
            # Update reaction data
            reaction_data = self.tracked_posts[digest_id]
            reaction_data.likes = reactions.get('like', 0)
            reaction_data.dislikes = reactions.get('dislike', 0)
            reaction_data.fire = reactions.get('fire', 0)
            reaction_data.bored = reactions.get('bored', 0)
            reaction_data.total_reactions = sum(reactions.values())
            
            # Calculate engagement score
            reaction_data.engagement_score = self._calculate_engagement_score(reaction_data)
            reaction_data.last_updated = datetime.now(timezone.utc)
            
            # Save to database
            await self._save_feedback_to_database(reaction_data)
            
            logger.debug(f"Updated reactions for digest {digest_id}: {reactions}")
            
        except Exception as e:
            logger.error(f"Error updating reactions for digest {digest_id}: {e}")
    
    async def _get_message_reactions(self, message_id: int, chat_id: int) -> Dict[str, int]:
        """Get message reactions from Telegram API."""
        try:
            # This is a simplified implementation
            # In a real implementation, you would use Telegram Bot API to get reactions
            # For now, we'll return mock data
            
            # Mock reaction data (replace with actual API call)
            reactions = {
                'like': 0,
                'dislike': 0,
                'fire': 0,
                'bored': 0
            }
            
            # In real implementation, you would:
            # 1. Use bot.get_chat() to get chat info
            # 2. Use bot.get_message_reactions() to get reactions
            # 3. Parse reaction emojis and counts
            
            return reactions
            
        except Exception as e:
            logger.error(f"Error getting message reactions: {e}")
            return {}
    
    def _calculate_engagement_score(self, reaction_data: ReactionData) -> float:
        """Calculate engagement score from reaction data."""
        try:
            total_reactions = reaction_data.total_reactions
            
            if total_reactions == 0:
                return 0.5  # Neutral score for no reactions
            
            # Weighted score calculation
            weighted_score = 0.0
            
            for reaction_type, weight in self.reaction_weights.items():
                count = getattr(reaction_data, reaction_type, 0)
                weighted_score += count * weight
            
            # Normalize to 0.0-1.0 range
            max_possible_score = total_reactions * 2.0  # Maximum positive weight
            normalized_score = (weighted_score + max_possible_score) / (2 * max_possible_score)
            
            return max(0.0, min(1.0, normalized_score))
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0.5
    
    async def _save_feedback_to_database(self, reaction_data: ReactionData) -> None:
        """Save feedback data to database."""
        try:
            # This would integrate with your database service
            # For now, we'll just log the data
            
            logger.info(f"Saving feedback for digest {reaction_data.digest_id}: "
                       f"score={reaction_data.engagement_score:.3f}, "
                       f"reactions={reaction_data.total_reactions}")
            
            # In real implementation, you would:
            # 1. Use database service to upsert feedback data
            # 2. Update digest engagement_score
            # 3. Prepare data for AI model training
            
        except Exception as e:
            logger.error(f"Error saving feedback to database: {e}")
    
    async def _finalize_tracking(self, digest_id: int) -> None:
        """Finalize tracking and update metrics."""
        try:
            if digest_id not in self.tracked_posts:
                return
            
            reaction_data = self.tracked_posts[digest_id]
            
            # Update metrics
            self.metrics.increment_reactions_total(reaction_data.total_reactions)
            self.metrics.update_engagement_score_avg(reaction_data.engagement_score)
            
            # Check if we should update AI models
            if reaction_data.total_reactions > 5:  # Threshold for significant engagement
                self.metrics.increment_reactions_to_ai_updates_total()
                await self._trigger_ai_update(reaction_data)
            
            # Clean up
            del self.tracked_posts[digest_id]
            
            logger.info(f"Finalized tracking for digest {digest_id}: "
                       f"final_score={reaction_data.engagement_score:.3f}")
            
        except Exception as e:
            logger.error(f"Error finalizing tracking for digest {digest_id}: {e}")
    
    async def _trigger_ai_update(self, reaction_data: ReactionData) -> None:
        """Trigger AI model update based on feedback."""
        try:
            # This would integrate with your AI training system
            # For now, we'll just log the trigger
            
            logger.info(f"Triggering AI update for digest {reaction_data.digest_id} "
                       f"with engagement score {reaction_data.engagement_score:.3f}")
            
            # In real implementation, you would:
            # 1. Collect feedback data for training
            # 2. Update Self-Tuning Predictor models
            # 3. Adjust content selection algorithms
            
        except Exception as e:
            logger.error(f"Error triggering AI update: {e}")
    
    def get_engagement_stats(self) -> Dict[str, Any]:
        """Get engagement statistics."""
        total_posts = len(self.tracked_posts)
        total_reactions = sum(rd.total_reactions for rd in self.tracked_posts.values())
        avg_score = 0.0
        
        if total_posts > 0:
            total_score = sum(rd.engagement_score for rd in self.tracked_posts.values())
            avg_score = total_score / total_posts
        
        return {
            'enabled': self.enabled,
            'tracked_posts': total_posts,
            'total_reactions': total_reactions,
            'average_engagement_score': avg_score,
            'update_interval_min': self.update_interval_min
        }
    
    def get_top_engaging_categories(self, limit: int = 3) -> List[Tuple[str, float]]:
        """Get top engaging categories based on tracked data."""
        try:
            # This would analyze engagement by category
            # For now, return mock data
            
            mock_categories = [
                ('crypto', 0.85),
                ('tech', 0.78),
                ('sports', 0.72)
            ]
            
            return mock_categories[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top engaging categories: {e}")
            return []


# Global feedback tracker instance
_feedback_tracker_instance: Optional[FeedbackTracker] = None


def get_feedback_tracker() -> FeedbackTracker:
    """Get global feedback tracker instance."""
    global _feedback_tracker_instance
    if _feedback_tracker_instance is None:
        _feedback_tracker_instance = FeedbackTracker()
    return _feedback_tracker_instance


async def start_reaction_tracking(digest_id: int, message_id: int, chat_id: int) -> None:
    """
    Convenience function to start reaction tracking.
    
    Args:
        digest_id: ID of the digest
        message_id: Telegram message ID
        chat_id: Telegram chat ID
    """
    tracker = get_feedback_tracker()
    await tracker.start_tracking(digest_id, message_id, chat_id)

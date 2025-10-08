"""
Teaser and Hashtag Generator for Smart Content Posting.

This module generates engaging teasers and relevant hashtags
for digest posts to increase engagement and reach.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import openai
from pathlib import Path

from ai_modules.metrics import get_metrics

# from utils.ai.ai_client import get_ai_client

logger = logging.getLogger("teaser_generator")


@dataclass
class TeaserResult:
    """Result of teaser generation."""

    teaser: str
    hashtags: List[str]
    confidence: float
    category: str


class TeaserGenerator:
    """
    Generates engaging teasers and hashtags for digest posts.

    Features:
    - AI-powered teaser generation
    - Category-specific hashtag suggestions
    - Caching to reduce AI calls
    - Quality validation
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize teaser generator with configuration."""
        self.config = self._load_config(config_path)
        self.metrics = get_metrics()

        # Configuration
        self.smart_posting_config = self.config.get("smart_posting", {})
        self.enabled = self.smart_posting_config.get("teaser_generator", True)

        # AI client (placeholder for now)
        self.ai_client = None

        # Category-specific hashtag mappings
        self.category_hashtags = {
            "crypto": ["#crypto", "#blockchain", "#defi", "#bitcoin", "#ethereum"],
            "tech": ["#tech", "#AI", "#innovation", "#startup", "#software"],
            "sports": ["#sports", "#football", "#basketball", "#tennis", "#olympics"],
            "world": ["#world", "#news", "#politics", "#global", "#breaking"],
            "markets": ["#markets", "#finance", "#economy", "#trading", "#investing"],
            "unknown": ["#news", "#breaking", "#update"],
        }

        # Cache for generated teasers
        self.teaser_cache = {}

        logger.info(f"TeaserGenerator initialized: enabled={self.enabled}")

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "ai_optimization.yaml"

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

    def _generate_cache_key(self, title: str, summary: str, category: str) -> str:
        """Generate cache key for teaser generation."""
        # Create a simple hash from title and category
        import hashlib

        content = f"{title[:50]}_{category}".lower()
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _get_category_hashtags(self, category: str) -> List[str]:
        """Get hashtags for a specific category."""
        category_lower = category.lower()

        # Direct match
        if category_lower in self.category_hashtags:
            return self.category_hashtags[category_lower]

        # Partial match
        for cat, hashtags in self.category_hashtags.items():
            if cat in category_lower or category_lower in cat:
                return hashtags

        # Default hashtags
        return self.category_hashtags["unknown"]

    async def _generate_teaser_with_ai(self, title: str, summary: str, category: str) -> str:
        """
        Generate teaser using AI.

        Args:
            title: News title
            summary: News summary
            category: News category

        Returns:
            Generated teaser
        """
        try:
            # Create prompt for AI
            prompt = f"""
Напиши короткий, живой анонс новости в 1 предложении для Telegram, с лёгкой интригой и тоном медиа.

Заголовок: {title}
Краткое содержание: {summary}
Категория: {category}

Требования:
- Максимум 1 предложение
- Живой, интригующий тон
- Без эмодзи в начале
- Фокус на главной интриге новости
- Стиль медиа-анонса

Анонс:"""

            # Generate teaser using AI (placeholder for now)
            # response = await self.ai_client.generate_text(
            #     prompt=prompt,
            #     max_tokens=100,
            #     temperature=0.7
            # )

            # For now, use fallback teaser
            response = self._generate_fallback_teaser(title, category)

            teaser = response.strip()

            # Clean up the teaser
            teaser = self._clean_teaser(teaser)

            # Validate length
            if len(teaser) > 200:
                teaser = teaser[:197] + "..."

            logger.debug(f"Generated teaser for category '{category}': {teaser[:50]}...")
            return teaser

        except Exception as e:
            logger.error(f"Error generating teaser with AI: {e}")
            # Fallback teaser
            return self._generate_fallback_teaser(title, category)

    def _clean_teaser(self, teaser: str) -> str:
        """Clean and validate teaser text."""
        # Remove quotes if present
        teaser = teaser.strip("\"'")

        # Remove "Анонс:" prefix if present
        teaser = re.sub(r"^анонс:\s*", "", teaser, flags=re.IGNORECASE)

        # Ensure it ends with proper punctuation
        if not teaser.endswith((".", "!", "?")):
            teaser += "."

        return teaser.strip()

    def _generate_fallback_teaser(self, title: str, category: str) -> str:
        """Generate fallback teaser without AI."""
        # Simple template-based teaser
        templates = {
            "crypto": f"Криптовалютные новости: {title}",
            "tech": f"Технологические обновления: {title}",
            "sports": f"Спортивные новости: {title}",
            "world": f"Мировые события: {title}",
            "markets": f"Рыночные новости: {title}",
            "unknown": f"Важные новости: {title}",
        }

        category_lower = category.lower()
        for cat, template in templates.items():
            if cat in category_lower:
                return template

        return f"Актуальные новости: {title}"

    async def generate_teaser(self, title: str, summary: str, category: str) -> TeaserResult:
        """
        Generate teaser and hashtags for a digest.

        Args:
            title: News title
            summary: News summary
            category: News category

        Returns:
            TeaserResult with teaser, hashtags, and metadata
        """
        try:
            if not self.enabled:
                # Return minimal result if disabled
                return TeaserResult(
                    teaser=title[:100],
                    hashtags=self._get_category_hashtags(category)[:2],
                    confidence=0.0,
                    category=category,
                )

            # Check cache first
            cache_key = self._generate_cache_key(title, summary, category)
            if cache_key in self.teaser_cache:
                logger.debug(f"Using cached teaser for key: {cache_key}")
                return self.teaser_cache[cache_key]

            # Generate teaser with AI
            teaser = await self._generate_teaser_with_ai(title, summary, category)

            # Get hashtags
            hashtags = self._get_category_hashtags(category)

            # Calculate confidence based on teaser quality
            confidence = self._calculate_confidence(teaser, title, summary)

            # Create result
            result = TeaserResult(
                # Limit to 3 hashtags
                teaser=teaser, hashtags=hashtags[:3], confidence=confidence, category=category
            )

            # Cache the result
            self.teaser_cache[cache_key] = result

            # Update metrics
            self.metrics.increment_teaser_generated_total()

            logger.info(f"Generated teaser for category '{category}': confidence={confidence:.2f}")

            return result

        except Exception as e:
            logger.error(f"Error generating teaser: {e}")

            # Return fallback result
            return TeaserResult(
                teaser=self._generate_fallback_teaser(title, category),
                hashtags=self._get_category_hashtags(category)[:2],
                confidence=0.3,
                category=category,
            )

    def _calculate_confidence(self, teaser: str, title: str, summary: str) -> float:
        """Calculate confidence score for generated teaser."""
        confidence = 0.5  # Base confidence

        # Length check (optimal: 50-150 characters)
        length = len(teaser)
        if 50 <= length <= 150:
            confidence += 0.2
        elif length < 30 or length > 200:
            confidence -= 0.2

        # Check for engaging words
        engaging_words = [
            "новый",
            "прорыв",
            "исторический",
            "рекорд",
            "важный",
            "ключевой",
            "значимый"]
        if any(word in teaser.lower() for word in engaging_words):
            confidence += 0.1

        # Check for question or exclamation (engagement)
        if teaser.endswith("?") or teaser.endswith("!"):
            confidence += 0.1

        # Penalize if too similar to title
        if teaser.lower() == title.lower():
            confidence -= 0.3

        return min(1.0, max(0.0, confidence))

    def format_teaser_post(self, teaser_result: TeaserResult,
                           original_digest: Dict[str, any]) -> str:
        """
        Format teaser result into a complete post.

        Args:
            teaser_result: Generated teaser result
            original_digest: Original digest data

        Returns:
            Formatted post text
        """
        try:
            # Get category emoji
            category_emojis = {
                "crypto": "🪙",
                "tech": "💻",
                "sports": "🏀",
                "world": "🌍",
                "markets": "📈",
                "unknown": "📰",
            }

            emoji = category_emojis.get(teaser_result.category.lower(), "📰")

            # Format hashtags
            hashtag_text = " ".join(teaser_result.hashtags)

            # Create post
            post_parts = [
                f"🚀 {teaser_result.teaser}",
                f"",
                f"{emoji} {original_digest.get('title', '')}",
                f"",
                f"{hashtag_text}",
            ]

            post = "\n".join(post_parts)

            # Ensure length limit
            if len(post) > 1024:
                # Truncate teaser if needed
                max_teaser_length = 1024 - len("\n".join(post_parts[2:])) - 10
                teaser_result.teaser = teaser_result.teaser[:max_teaser_length] + "..."

                post_parts = [
                    f"🚀 {teaser_result.teaser}",
                    f"",
                    f"{emoji} {original_digest.get('title', '')}",
                    f"",
                    f"{hashtag_text}",
                ]
                post = "\n".join(post_parts)

            return post

        except Exception as e:
            logger.error(f"Error formatting teaser post: {e}")
            return teaser_result.teaser

    def get_hashtag_suggestions(self, category: str, limit: int = 3) -> List[str]:
        """
        Get hashtag suggestions for a category.

        Args:
            category: Content category
            limit: Maximum number of hashtags

        Returns:
            List of suggested hashtags
        """
        return self._get_category_hashtags(category)[:limit]


# Global teaser generator instance
_teaser_generator_instance: Optional[TeaserGenerator] = None


def get_teaser_generator() -> TeaserGenerator:
    """Get global teaser generator instance."""
    global _teaser_generator_instance
    if _teaser_generator_instance is None:
        _teaser_generator_instance = TeaserGenerator()
    return _teaser_generator_instance


async def generate_teaser_for_digest(title: str, summary: str, category: str) -> TeaserResult:
    """
    Convenience function to generate teaser for a digest.

    Args:
        title: News title
        summary: News summary
        category: News category

    Returns:
        TeaserResult with teaser and hashtags
    """
    generator = get_teaser_generator()
    return await generator.generate_teaser(title, summary, category)

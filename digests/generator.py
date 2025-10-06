"""
Digest Generator - thin wrapper around DigestAIService.

This module provides backward compatibility functions that delegate
to the new DigestAIService for digest generation.
"""

import argparse
import logging
import asyncio
from typing import Optional, List

from database.db_models import supabase
from models.news import NewsItem
from digests.ai_service import DigestAIService, DigestConfig

logger = logging.getLogger("generator")


def _dummy_news() -> NewsItem:
    """Fallback news item for stability."""
    from datetime import datetime

    now = datetime.utcnow()
    return NewsItem(
        id="dummy-1",
        title="High importance news",
        content="Dummy content for testing",
        link=None,
        importance=0.9,
        credibility=1.0,
        published_at=now,
        source="test",
        category="crypto",
    )


def fetch_recent_news(limit: int = 10, category: Optional[str] = None) -> List[NewsItem]:
    """
    Fetch recent news from Supabase.

    Args:
        limit: Maximum number of news items to fetch
        category: Optional category filter

    Returns:
        List of NewsItem objects
    """
    if not supabase:
        logger.warning("Supabase not initialized, returning dummy news")
        return [_dummy_news()]

    try:
        query = supabase.table("news").select("*").order("published_at", desc=True).limit(limit)

        if category:
            query = query.eq("category", category.lower())

        response = query.execute()

        if not response.data:
            logger.info("No news found in database, returning dummy news")
            return [_dummy_news()]

        news_items = []
        for row in response.data:
            try:
                # Ensure id is string
                row["id"] = str(row["id"])
                news_item = NewsItem.model_validate(row)
                news_items.append(news_item)
            except Exception as e:
                logger.warning(f"Failed to validate news item: {e}")
                continue

        logger.info(f"Fetched {len(news_items)} news items")
        return news_items if news_items else [_dummy_news()]

    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return [_dummy_news()]


async def generate_digest(
    limit: int = 10, category: Optional[str] = None, ai: bool = False, style: str = "analytical"
) -> str:
    """
    Generate digest using DigestAIService.

    Args:
        limit: Maximum number of news items
        category: Optional category filter
        ai: Whether to use AI summarization
        style: Digest style

    Returns:
        Generated digest text
    """
    # Fetch news items
    news_items = fetch_recent_news(limit=limit, category=category)

    if not news_items:
        return "📰 <b>Дайджест новостей</b>\n\nСегодня новостей нет."

    # Create service with configuration
    config = DigestConfig(max_items=8, include_fallback=True)
    service = DigestAIService(config)

    if ai:
        # Определяем категорию для контекста промта
        digest_category = category or "world"
        return await service.build_digest(news_items, style, digest_category)
    else:
        return service._build_fallback_digest(news_items)


def main():
    """CLI entry point for digest generation."""
    parser = argparse.ArgumentParser(description="Generate news digest")
    parser.add_argument("--limit", type=int, default=10, help="Number of news items")
    parser.add_argument("--category", type=str, help="News category filter")
    parser.add_argument("--ai", action="store_true", help="Use AI summarization")
    parser.add_argument(
        "--style",
        type=str,
        default="analytical",
        choices=["analytical", "business", "meme"],
        help="Digest style",
    )

    args = parser.parse_args()

    # Generate digest
    digest = asyncio.run(generate_digest(limit=args.limit, category=args.category, ai=args.ai, style=args.style))

    print(digest)


if __name__ == "__main__":
    main()

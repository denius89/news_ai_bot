"""
Digest Generator - thin wrapper around DigestAIService.

This module provides backward compatibility functions that delegate
to the new DigestAIService for digest generation.
"""

import argparse
import logging
import asyncio
import time  # noqa: F401
from typing import Optional, List

from database.db_models import supabase
from models.news import NewsItem
from digests.ai_service import DigestAIService, DigestConfig
from core.reactor import reactor, Events

logger = logging.getLogger("generator")


def _convert_v2_to_text(v2_result: dict) -> str:
    """
    Convert v2 digest result to text format for backward compatibility.

    Args:
        v2_result: Dictionary with v2 digest structure

    Returns:
        Formatted text string
    """
    if not v2_result:
        return "Ошибка конвертации v2 результата"

    # Extract main content
    title = v2_result.get("title", "Дайджест новостей")
    dek = v2_result.get("dek", "")
    summary = v2_result.get("summary", "")
    why_important = v2_result.get("why_important", [])
    context = v2_result.get("context", "")
    what_next = v2_result.get("what_next", "")
    sources_cited = v2_result.get("sources_cited", [])

    # Build text
    text_parts = [f"<b>{title}</b>"]

    if dek:
        text_parts.append(f"<i>{dek}</i>")

    if summary:
        text_parts.append(f"\n{summary}")

    if why_important:
        text_parts.append("\n<b>Почему это важно:</b>")
        for item in why_important:
            text_parts.append(f"— {item}")

    if context:
        text_parts.append(f"\n<b>Контекст:</b> {context}")

    if what_next:
        text_parts.append(f"\n<b>Что дальше:</b> {what_next}")

    if sources_cited:
        text_parts.append(f"\n<b>Источники:</b> {', '.join(sources_cited)}")

    return "\n".join(text_parts)


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
    limit: int = 10,
    category: Optional[str] = None,
    ai: bool = False,
    style: str = "analytical",
    # NEW PARAMETERS
    tone: str = "neutral",
    length: str = "medium",
    audience: str = "general",
    use_v2: bool = True,  # флаг для использования v2
    user_id: Optional[str] = None,  # для сохранения метрик
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
        return "<b>Дайджест новостей</b>\n\nСегодня новостей нет."

    # Create service with configuration
    config = DigestConfig(max_items=8, include_fallback=True)
    service = DigestAIService(config)

    try:
        if ai:
            # Определяем категорию для контекста промта
            digest_category = category or "world"

            # Try v2 generation if enabled
            if use_v2:
                try:
                    from digests.ai_summary import generate_summary_journalistic_v2

                    # Generate v2 digest
                    v2_result = generate_summary_journalistic_v2(
                        news_items=news_items,
                        category=digest_category,
                        style_profile=style,
                        tone=tone,
                        length=length,
                        audience=audience,
                        max_tokens=800,
                    )

                    # Check if v2 generation was successful
                    if "error" not in v2_result and "skipped_reason" not in v2_result:
                        # Convert v2 result to text format
                        digest_text = _convert_v2_to_text(v2_result)
                        logger.info(f"Successfully generated v2 digest with style: {style}, tone: {tone}")

                        # Save metrics to database if user_id provided
                        if user_id and "meta" in v2_result:
                            try:
                                from database.db_models import save_digest_with_metrics

                                meta = v2_result["meta"]
                                confidence = meta.get("confidence", 0.0)
                                generation_time_sec = meta.get("generation_time_sec", 0.0)

                                digest_id = save_digest_with_metrics(
                                    user_id=user_id,
                                    summary=digest_text,
                                    category=digest_category,
                                    style=style,
                                    confidence=confidence,
                                    generation_time_sec=generation_time_sec,
                                    meta=meta,
                                )

                                if digest_id:
                                    logger.info(f"✅ Digest metrics saved: {digest_id}")

                            except Exception as e:
                                logger.warning(f"Failed to save digest metrics: {e}")
                    else:
                        logger.warning(
                            f"V2 generation failed: {v2_result.get('error', v2_result.get('skipped_reason'))}"
                        )
                        # Fallback to legacy generation
                        digest_text = await service.build_digest(news_items, style, digest_category)
                except Exception as e:
                    logger.warning(f"V2 generation error, falling back to legacy: {e}")
                    digest_text = await service.build_digest(news_items, style, digest_category)
            else:
                # Use legacy generation
                digest_text = await service.build_digest(news_items, style, digest_category)
        else:
            digest_text = service._build_fallback_digest(news_items)

        # Эмитим событие о создании дайджеста
        reactor.emit_sync(
            Events.DIGEST_CREATED,
            {
                "title": f'Дайджест {digest_category or "общий"}',
                "style": style,
                "items_count": len(news_items),
                "ai_generated": ai,
                "timestamp": asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0,
            },
        )

        logger.info(f"Дайджест создан: {len(news_items)} новостей, AI={ai}")
        return digest_text

    except Exception as e:
        logger.error(f"Ошибка при создании дайджеста: {e}")
        # Эмитим событие об ошибке
        reactor.emit_sync(
            Events.DIGEST_CREATED, {"title": "Ошибка создания дайджеста", "error": str(e), "status": "error"}
        )
        raise


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
        choices=["analytical", "business", "meme", "newsroom", "magazine", "casual"],
        help="Digest style",
    )
    parser.add_argument(
        "--tone",
        type=str,
        default="neutral",
        choices=["neutral", "insightful", "critical", "optimistic"],
        help="Digest tone",
    )
    parser.add_argument(
        "--length", type=str, default="medium", choices=["short", "medium", "long"], help="Digest length"
    )
    parser.add_argument("--audience", type=str, default="general", choices=["general", "pro"], help="Target audience")
    parser.add_argument("--use-v2", action="store_true", help="Use v2 prompts")

    args = parser.parse_args()

    # Generate digest
    digest = asyncio.run(
        generate_digest(
            limit=args.limit,
            category=args.category,
            ai=args.ai,
            style=args.style,
            tone=args.tone,
            length=args.length,
            audience=args.audience,
            use_v2=args.use_v2,
        )
    )

    print(digest)


if __name__ == "__main__":
    main()

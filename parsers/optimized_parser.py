"""
Optimized parser with AI call reduction.

This module extends the AdvancedParser with optimization layers
to reduce AI API calls while maintaining quality.
"""

import asyncio
import logging
import time
from typing import List, Dict, Optional
from pathlib import Path

from parsers.advanced_parser import AdvancedParser
from ai_modules.optimized_importance import evaluate_importance
from ai_modules.optimized_credibility import evaluate_both_with_optimization
from ai_modules.metrics import get_metrics
from database.service import get_async_service
from core.reactor import reactor, Events

logger = logging.getLogger("optimized_parser")


class OptimizedParser(AdvancedParser):
    """
    Optimized version of AdvancedParser with AI call reduction.

    This parser implements the same functionality as AdvancedParser
    but with optimized AI evaluation to reduce API calls.
    """

    def __init__(self, **kwargs):
        """Initialize optimized parser."""
        super().__init__(**kwargs)
        self.metrics = get_metrics()
        self.min_importance_threshold = 0.6  # Configurable threshold
        self.min_credibility_threshold = 0.7  # Configurable threshold

    async def _evaluate_news_with_optimization(self, news_item: Dict) -> Optional[Dict]:
        """
        Evaluate news item with full optimization pipeline.

        Args:
            news_item: Dictionary containing news item data

        Returns:
            Enhanced news item with AI scores, or None if filtered out
        """
        try:
            # Use optimized evaluation that combines both importance and credibility
            importance, credibility = evaluate_both_with_optimization(news_item)

            # Apply thresholds
            if importance < self.min_importance_threshold:
                logger.debug(f"News filtered by importance threshold: {importance} < {self.min_importance_threshold}")
                self.metrics.increment_ai_skipped_local_pred()  # Count as filtered by threshold
                return None

            if credibility < self.min_credibility_threshold:
                logger.debug(
                    f"News filtered by credibility threshold: {credibility} < {self.min_credibility_threshold}"
                )
                self.metrics.increment_ai_skipped_local_pred()  # Count as filtered by threshold
                return None

            # Enhance news item with scores
            enhanced_item = news_item.copy()
            enhanced_item["importance"] = importance
            enhanced_item["credibility"] = credibility

            return enhanced_item

        except Exception as e:
            logger.error(f"Error in optimized evaluation: {e}")
            return None

    async def _process_single_source_optimized(self, source: Dict) -> List[Dict]:
        """
        Process a single source with optimization.

        Args:
            source: Dictionary containing source information

        Returns:
            List of processed news items
        """
        source_name = source.get("name", "Unknown")
        source_url = source.get("url", "")

        try:
            logger.info(f"Processing source: {source_name}")

            # Parse source content
            parsed_news = await self._parse_source_content(source_url, source_name)

            if not parsed_news:
                logger.warning(f"No news found for source: {source_name}")
                return []

            processed_items = []

            for news_item in parsed_news:
                try:
                    # Check for duplicates first
                    if await self._is_duplicate(news_item):
                        self.metrics.increment_duplicates_skipped()
                        continue

                    # Evaluate with optimization
                    enhanced_item = await self._evaluate_news_with_optimization(news_item)

                    if enhanced_item is not None:
                        processed_items.append(enhanced_item)
                        logger.debug(f"Processed news: {enhanced_item.get('title', 'No title')[:50]}...")

                except Exception as e:
                    logger.error(f"Error processing individual news item: {e}")
                    continue

            logger.info(f"Processed {len(processed_items)} news items from {source_name}")
            return processed_items

        except Exception as e:
            logger.error(f"Error processing source {source_name}: {e}")
            return []

    async def run_optimized(self, max_concurrent: int = 10) -> Dict:
        """
        Run optimized parsing with AI call reduction.

        Args:
            max_concurrent: Maximum number of concurrent source processing

        Returns:
            Dictionary with processing results and metrics
        """
        logger.info("Starting optimized news parsing...")
        start_time = time.time()

        # Load sources configuration
        await self._load_sources_config()

        # Get all sources
        sources = self._get_all_sources()
        if not sources:
            logger.error("No sources found")
            return {"success": False, "error": "No sources found"}

        logger.info(f"Loaded {len(sources)} sources")

        # Process sources with concurrency control
        processed_items = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(source):
            async with semaphore:
                return await self._process_single_source_optimized(source)

        # Process all sources concurrently
        tasks = [process_with_semaphore(source) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Source processing failed: {result}")
            elif isinstance(result, list):
                processed_items.extend(result)

        # Save to database
        saved_count = 0
        if processed_items:
            try:
                db_service = get_async_service()
                saved_count = await db_service.async_upsert_news(processed_items)
                logger.info(f"Saved {saved_count} news items to database")
                
                # Эмитим событие о обработке новостей
                reactor.emit_sync(Events.NEWS_PROCESSED, {
                    'count': saved_count,
                    'processed_total': len(processed_items),
                    'processing_time': round(time.time() - start_time, 2),
                    'timestamp': time.time()
                })
                
            except Exception as e:
                logger.error(f"Error saving to database: {e}")

        # Calculate metrics
        processing_time = time.time() - start_time
        metrics_summary = self.metrics.get_metrics_summary()

        result = {
            "success": True,
            "processed_items": len(processed_items),
            "saved_items": saved_count,
            "processing_time_seconds": round(processing_time, 2),
            "metrics": metrics_summary,
        }

        logger.info(f"Optimized parsing completed: {result}")
        return result

    def get_optimization_stats(self) -> Dict:
        """Get optimization statistics."""
        return self.metrics.get_metrics_summary()


# Convenience function for easy import
async def run_optimized_parser(max_concurrent: int = 10) -> Dict:
    """
    Run optimized parser with default settings.

    Args:
        max_concurrent: Maximum number of concurrent source processing

    Returns:
        Dictionary with processing results and metrics
    """
    parser = OptimizedParser()
    return await parser.run_optimized(max_concurrent=max_concurrent)

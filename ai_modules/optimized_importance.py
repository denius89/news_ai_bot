"""
Optimized importance evaluation with pre-filtering, caching, and local prediction.

This module wraps the original importance evaluation with optimization layers
to reduce AI API calls while maintaining quality.
"""

import logging
import time
from typing import Dict, Optional

from ai_modules.importance import evaluate_importance as original_evaluate_importance
from ai_modules.prefilter import filter_news_item
from ai_modules.cache import get_cached_evaluation, cache_evaluation, get_cache
from ai_modules.local_predictor import predict_news_item
from ai_modules.metrics import get_metrics
from ai_modules.adaptive_thresholds import get_adaptive_thresholds

logger = logging.getLogger("optimized_importance")


def evaluate_importance(news_item: Dict) -> float:
    """
    Optimized importance evaluation with pre-filtering, caching, and local prediction.

    This function implements a three-stage optimization:
    1. Pre-filter: Lightweight rules-based filtering
    2. Cache: Check for previously evaluated similar items
    3. Local predictor: Optional local model prediction

    Only if all stages pass, the original AI evaluation is called.

    Args:
        news_item: Dictionary containing news item data

    Returns:
        Importance score between 0.0 and 1.0
    """
    metrics = get_metrics()
    metrics.increment_news_processed()

    # Stage 1: Pre-filter
    try:
        prefilter_result = filter_news_item(news_item)
        if not prefilter_result.passed:
            metrics.increment_ai_skipped_prefilter()
            logger.debug(f"News filtered by prefilter: {prefilter_result.reason}")
            return 0.0  # Low importance for filtered items
    except Exception as e:
        logger.error(f"Error in prefilter: {e}")
        metrics.increment_prefilter_errors()
        # Continue to next stage on prefilter error

    # Stage 2: Cache check with TTL support
    try:
        cached_entry = get_cached_evaluation(news_item)
        if cached_entry is not None:
            cache = get_cache()

            # Check if cache entry needs refresh (partial update)
            if cache.needs_refresh(cached_entry):
                logger.info("[CACHE] entry needs refresh, performing partial update")
                metrics.increment_partial_updates()

                # Perform partial update - re-evaluate importance only
                try:
                    start_time = time.time()
                    new_importance = original_evaluate_importance(news_item)
                    latency_ms = (time.time() - start_time) * 1000

                    metrics.increment_ai_calls()
                    metrics.record_ai_latency(latency_ms)

                    # Update cache with new importance
                    cache.update_partial(news_item, importance=new_importance)
                    logger.debug(f"[CACHE] partial update completed: {new_importance}")
                    return new_importance

                except Exception as e:
                    logger.error(f"Error in partial update: {e}")
                    metrics.increment_ai_errors()
                    # Fallback to cached value
                    return cached_entry.ai_importance
            else:
                metrics.increment_ai_skipped_cache()
                logger.debug(f"Using cached importance: {cached_entry.ai_importance}")
                return cached_entry.ai_importance
    except Exception as e:
        logger.error(f"Error checking cache: {e}")
        metrics.increment_cache_errors()
        # Continue to next stage on cache error

    # Stage 3: Local predictor (if enabled)
    try:
        local_pred = predict_news_item(news_item)
        if local_pred.importance < 0.5:  # Configurable threshold
            metrics.increment_ai_skipped_local_pred()
            logger.debug(f"News filtered by local predictor: {local_pred.importance}")
            return local_pred.importance
    except Exception as e:
        logger.error(f"Error in local predictor: {e}")
        metrics.increment_local_pred_errors()
        # Continue to AI evaluation on local predictor error

    # Stage 4: Original AI evaluation with adaptive thresholds
    try:
        start_time = time.time()
        importance = original_evaluate_importance(news_item)
        latency_ms = (time.time() - start_time) * 1000

        metrics.increment_ai_calls()
        metrics.record_ai_latency(latency_ms)

        # Apply adaptive thresholds
        category = news_item.get("category")
        adaptive_thresholds = get_adaptive_thresholds()

        if adaptive_thresholds.is_enabled():
            importance_threshold, _ = adaptive_thresholds.get_thresholds(category)

            if importance >= importance_threshold:
                metrics.increment_adaptive_thresholds_applied()
                logger.debug(f"[THRESHOLD] category={category} importance>{importance_threshold} - PASSED")
            else:
                metrics.increment_adaptive_thresholds_skipped()
                logger.debug(f"[THRESHOLD] category={category} importance<{importance_threshold} - FAILED")
                return 0.0
        else:
            metrics.increment_adaptive_thresholds_skipped()

        # Cache the result for future use
        try:
            cache_evaluation(news_item, importance, 0.0)  # Credibility will be filled later
        except Exception as e:
            logger.warning(f"Failed to cache importance result: {e}")

        logger.debug(f"AI importance evaluation: {importance}")
        return importance

    except Exception as e:
        logger.error(f"Error in AI importance evaluation: {e}")
        metrics.increment_ai_errors()

        # Fallback to local prediction if available
        try:
            local_pred = predict_news_item(news_item)
            logger.warning(f"Using local predictor fallback for importance: {local_pred.importance}")
            return local_pred.importance
        except Exception:
            logger.error("Both AI and local predictor failed for importance")
            return 0.0


def evaluate_importance_with_cache(news_item: Dict, cache_importance: Optional[float] = None) -> float:
    """
    Evaluate importance with explicit cache value.

    This is used when we have a cached result but need to re-evaluate
    or when we want to bypass certain optimization stages.

    Args:
        news_item: Dictionary containing news item data
        cache_importance: Pre-calculated importance score from cache

    Returns:
        Importance score between 0.0 and 1.0
    """
    if cache_importance is not None:
        metrics = get_metrics()
        metrics.increment_ai_skipped_cache()
        return cache_importance

    return evaluate_importance(news_item)

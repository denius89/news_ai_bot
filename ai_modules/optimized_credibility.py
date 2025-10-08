"""
Optimized credibility evaluation with pre-filtering, caching, and local prediction.

This module wraps the original credibility evaluation with optimization layers
to reduce AI API calls while maintaining quality.
"""

import logging
import time
from typing import Dict, Optional

from ai_modules.credibility import evaluate_credibility as original_evaluate_credibility
from ai_modules.importance import evaluate_importance as original_evaluate_importance
from ai_modules.prefilter import filter_news_item
from ai_modules.cache import get_cached_evaluation, cache_evaluation, get_cache
from ai_modules.local_predictor import predict_news_item
from ai_modules.metrics import get_metrics
from ai_modules.adaptive_thresholds import get_adaptive_thresholds

logger = logging.getLogger("optimized_credibility")


def evaluate_credibility(news_item: Dict) -> float:
    """
    Optimized credibility evaluation with pre-filtering, caching, and local prediction.

    This function implements a three-stage optimization:
    1. Pre-filter: Lightweight rules-based filtering
    2. Cache: Check for previously evaluated similar items
    3. Local predictor: Optional local model prediction

    Only if all stages pass, the original AI evaluation is called.

    Args:
        news_item: Dictionary containing news item data

    Returns:
        Credibility score between 0.0 and 1.0
    """
    metrics = get_metrics()

    # Stage 1: Pre-filter
    try:
        prefilter_result = filter_news_item(news_item)
        if not prefilter_result.passed:
            metrics.increment_ai_skipped_prefilter()
            logger.debug(f"News filtered by prefilter: {prefilter_result.reason}")
            return 0.0  # Low credibility for filtered items
    except Exception as e:
        logger.error(f"Error in prefilter: {e}")
        metrics.increment_prefilter_errors()
        # Continue to next stage on prefilter error

    # Stage 2: Cache check
    try:
        cached_entry = get_cached_evaluation(news_item)
        if cached_entry is not None:
            metrics.increment_ai_skipped_cache()
            logger.debug(f"Using cached credibility: {cached_entry.ai_credibility}")
            return cached_entry.ai_credibility
    except Exception as e:
        logger.error(f"Error checking cache: {e}")
        metrics.increment_cache_errors()
        # Continue to next stage on cache error

    # Stage 3: Local predictor (if enabled)
    try:
        local_pred = predict_news_item(news_item)
        if local_pred.credibility < 0.5:  # Configurable threshold
            metrics.increment_ai_skipped_local_pred()
            logger.debug(f"News filtered by local predictor: {local_pred.credibility}")
            return local_pred.credibility
    except Exception as e:
        logger.error(f"Error in local predictor: {e}")
        metrics.increment_local_pred_errors()
        # Continue to AI evaluation on local predictor error

    # Stage 4: Original AI evaluation
    try:
        start_time = time.time()
        credibility = original_evaluate_credibility(news_item)
        latency_ms = (time.time() - start_time) * 1000

        metrics.increment_ai_calls()
        metrics.record_ai_latency(latency_ms)

        # Cache the result for future use
        try:
            cache_evaluation(news_item, 0.0, credibility)  # Importance will be filled later
        except Exception as e:
            logger.warning(f"Failed to cache credibility result: {e}")

        logger.debug(f"AI credibility evaluation: {credibility}")
        return credibility

    except Exception as e:
        logger.error(f"Error in AI credibility evaluation: {e}")
        metrics.increment_ai_errors()

        # Fallback to local prediction if available
        try:
            local_pred = predict_news_item(news_item)
            logger.warning(
                f"Using local predictor fallback for credibility: {local_pred.credibility}")
            return local_pred.credibility
        except Exception:
            logger.error("Both AI and local predictor failed for credibility")
            return 0.0


def evaluate_credibility_with_cache(news_item: Dict,
                                    cache_credibility: Optional[float] = None) -> float:
    """
    Evaluate credibility with explicit cache value.

    This is used when we have a cached result but need to re-evaluate
    or when we want to bypass certain optimization stages.

    Args:
        news_item: Dictionary containing news item data
        cache_credibility: Pre-calculated credibility score from cache

    Returns:
        Credibility score between 0.0 and 1.0
    """
    if cache_credibility is not None:
        metrics = get_metrics()
        metrics.increment_ai_skipped_cache()
        return cache_credibility

    return evaluate_credibility(news_item)


def evaluate_both_with_optimization(news_item: Dict) -> tuple[float, float]:
    """
    Evaluate both importance and credibility with full optimization.

    This function is more efficient when both scores are needed,
    as it can share cache lookups and local predictions.

    Args:
        news_item: Dictionary containing news item data

    Returns:
        Tuple of (importance, credibility) scores
    """
    metrics = get_metrics()
    metrics.increment_news_processed()

    # Stage 1: Pre-filter
    try:
        prefilter_result = filter_news_item(news_item)
        if not prefilter_result.passed:
            metrics.increment_ai_skipped_prefilter()
            logger.debug(f"News filtered by prefilter: {prefilter_result.reason}")
            return 0.0, 0.0  # Low scores for filtered items
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
                logger.info(
                    f"[CACHE] entry needs refresh, performing partial update (credibility only)")
                metrics.increment_partial_updates()

                # Perform partial update - re-evaluate credibility only
                try:
                    start_time = time.time()
                    new_credibility = original_evaluate_credibility(news_item)
                    latency_ms = (time.time() - start_time) * 1000

                    metrics.increment_ai_calls()
                    metrics.record_ai_latency(latency_ms)

                    # Update cache with new credibility
                    cache.update_partial(news_item, credibility=new_credibility)
                    logger.debug(f"[CACHE] partial update completed: {new_credibility}")
                    return cached_entry.ai_importance, new_credibility

                except Exception as e:
                    logger.error(f"Error in partial update: {e}")
                    metrics.increment_ai_errors()
                    # Fallback to cached values
                    return cached_entry.ai_importance, cached_entry.ai_credibility
            else:
                metrics.increment_ai_skipped_cache()
                logger.debug(
                    f"Using cached scores: {cached_entry.ai_importance}, {cached_entry.ai_credibility}")
                return cached_entry.ai_importance, cached_entry.ai_credibility
    except Exception as e:
        logger.error(f"Error checking cache: {e}")
        metrics.increment_cache_errors()
        # Continue to next stage on cache error

    # Stage 3: Local predictor (if enabled)
    try:
        local_pred = predict_news_item(news_item)
        if local_pred.importance < 0.5 or local_pred.credibility < 0.5:  # Configurable thresholds
            metrics.increment_ai_skipped_local_pred()
            logger.debug(
                f"News filtered by local predictor: {local_pred.importance}, {local_pred.credibility}")
            return local_pred.importance, local_pred.credibility
    except Exception as e:
        logger.error(f"Error in local predictor: {e}")
        metrics.increment_local_pred_errors()
        # Continue to AI evaluation on local predictor error

    # Stage 4: Original AI evaluation with adaptive thresholds
    try:
        start_time = time.time()
        importance = original_evaluate_importance(news_item)
        credibility = original_evaluate_credibility(news_item)
        latency_ms = (time.time() - start_time) * 1000

        metrics.increment_ai_calls()
        metrics.record_ai_latency(latency_ms)

        # Apply adaptive thresholds
        category = news_item.get("category")
        adaptive_thresholds = get_adaptive_thresholds()

        if adaptive_thresholds.is_enabled():
            importance_threshold, credibility_threshold = adaptive_thresholds.get_thresholds(
                category)

            if importance >= importance_threshold and credibility >= credibility_threshold:
                metrics.increment_adaptive_thresholds_applied()
                logger.debug(
                    f"[THRESHOLD] category={category} importance>{importance_threshold} credibility>{credibility_threshold} - PASSED"
                )
            else:
                metrics.increment_adaptive_thresholds_skipped()
                logger.debug(
                    f"[THRESHOLD] category={category} importance<{importance_threshold} or credibility<{credibility_threshold} - FAILED"
                )
                return 0.0, 0.0
        else:
            metrics.increment_adaptive_thresholds_skipped()

        # Cache the result for future use
        try:
            cache_evaluation(news_item, importance, credibility)
        except Exception as e:
            logger.warning(f"Failed to cache both results: {e}")

        logger.debug(f"AI evaluation: importance={importance}, credibility={credibility}")
        return importance, credibility

    except Exception as e:
        logger.error(f"Error in AI evaluation: {e}")
        metrics.increment_ai_errors()

        # Fallback to local prediction if available
        try:
            local_pred = predict_news_item(news_item)
            logger.warning(
                f"Using local predictor fallback: {local_pred.importance}, {local_pred.credibility}")
            return local_pred.importance, local_pred.credibility
        except Exception:
            logger.error("Both AI and local predictor failed")
            return 0.0, 0.0

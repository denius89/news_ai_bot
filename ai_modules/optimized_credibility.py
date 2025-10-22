"""
Optimized credibility evaluation with pre-filtering, caching, and local prediction.

This module wraps the original credibility evaluation with optimization layers
to reduce AI API calls while maintaining quality.
"""

import logging
import time
import threading
from typing import Dict, Optional

from ai_modules.credibility import evaluate_credibility as original_evaluate_credibility

# from ai_modules.importance import evaluate_importance as original_evaluate_importance  # Not used anymore with single request
from ai_modules.prefilter import filter_news_item
from ai_modules.cache import get_cached_evaluation, cache_evaluation, get_cache
from ai_modules.local_predictor import predict_news_item
from ai_modules.metrics import get_metrics
from ai_modules.adaptive_thresholds import get_adaptive_thresholds
from utils.ai.ai_client import ask

logger = logging.getLogger("optimized_credibility")

# Global lock for preventing race conditions in AI requests
_ai_request_lock = threading.Lock()
_active_requests = set()  # Track active requests to prevent duplicates


def _generate_request_key(news_item: Dict) -> str:
    """
    Generate a unique key for tracking duplicate requests.

    Args:
        news_item: Dictionary containing news item data

    Returns:
        Unique key string for the request
    """
    # Use cache mechanism to generate consistent key
    cache = get_cache()
    return cache._generate_cache_key(news_item)


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
            # Возвращаем базовую достоверность для дальнейшей обработки
            return 0.5
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
            logger.warning(f"Using local predictor fallback for credibility: {local_pred.credibility}")
            return local_pred.credibility
        except Exception:
            logger.error("Both AI and local predictor failed for credibility")
            return 0.0


def evaluate_credibility_with_cache(news_item: Dict, cache_credibility: Optional[float] = None) -> float:
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
                logger.info("[CACHE] entry needs refresh, performing partial update (credibility only)")
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
                logger.debug(f"Using cached scores: {cached_entry.ai_importance}, {cached_entry.ai_credibility}")
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
            logger.debug(f"News filtered by local predictor: {local_pred.importance}, {local_pred.credibility}")
            return local_pred.importance, local_pred.credibility
    except Exception as e:
        logger.error(f"Error in local predictor: {e}")
        metrics.increment_local_pred_errors()
        # Continue to AI evaluation on local predictor error

    # Stage 4: Thread-safe AI evaluation with duplicate prevention
    request_key = None

    try:
        request_key = _generate_request_key(news_item)

        with _ai_request_lock:
            # Check if this exact request is already being processed
            if request_key in _active_requests:
                logger.debug(f"[DUPLICATE] Request already in progress for key: {request_key[:8]}...")
                # Wait and check cache again - another thread might have finished
                time.sleep(0.1)
                cached_entry = get_cached_evaluation(news_item)
                if cached_entry is not None:
                    logger.debug(
                        f"[DUPLICATE] Found cached result after wait: {cached_entry.ai_importance}, {cached_entry.ai_credibility}"
                    )
                    metrics.increment_ai_skipped_cache()
                    return cached_entry.ai_importance, cached_entry.ai_credibility
                else:
                    logger.warning("[DUPLICATE] No cache found after wait, proceeding anyway")
            # Mark this request as active
            _active_requests.add(request_key)
            logger.debug(f"[DUPLICATE] Started processing request: {request_key[:8]}...")

        start_time = time.time()
        importance, credibility = evaluate_both_with_single_request(news_item)
        latency_ms = (time.time() - start_time) * 1000

        metrics.increment_ai_calls()  # Считаем как один запрос
        metrics.record_ai_latency(latency_ms)

        # Apply adaptive thresholds
        category = news_item.get("category")
        adaptive_thresholds = get_adaptive_thresholds()

        if adaptive_thresholds.is_enabled():
            importance_threshold, credibility_threshold = adaptive_thresholds.get_thresholds(category)

            if importance >= importance_threshold and credibility >= credibility_threshold:
                metrics.increment_adaptive_thresholds_applied()
                logger.debug(
                    f"[THRESHOLD] category={category} importance>{importance_threshold} "
                    f"credibility>{credibility_threshold} - PASSED"
                )
            else:
                metrics.increment_adaptive_thresholds_skipped()
                logger.debug(
                    f"[THRESHOLD] category={category} importance<{importance_threshold} or "
                    f"credibility<{credibility_threshold} - FAILED"
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
            logger.warning(f"Using local predictor fallback: {local_pred.importance}, {local_pred.credibility}")
            return local_pred.importance, local_pred.credibility
        except Exception:
            logger.error("Both AI and local predictor failed")
            return 0.0, 0.0
    finally:
        # Always clean up the active request tracking
        if request_key is not None:
            with _ai_request_lock:
                _active_requests.discard(request_key)
                logger.debug(f"[DUPLICATE] Completed processing request: {request_key[:8]}...")


def evaluate_both_with_single_request(news_item: Dict) -> tuple[float, float]:
    """
    Evaluate both importance and credibility with a single AI request.

    This function optimizes API usage by requesting both scores in one call.

    Args:
        news_item: Dictionary containing news item data

    Returns:
        Tuple of (importance, credibility) scores
    """
    title = news_item.get("title") or "Без названия"
    content = news_item.get("content") or news_item.get("summary") or ""

    # Объединённый промпт для обоих оценок
    prompt = f"""
Оцени следующую новость по двум критериям:

1. Важность (от 0 до 1): насколько важна эта новость для читателей финансовых новостей
2. Достоверность (от 0 до 1): насколько достоверен источник и содержание

Отвечай СТРОГО в формате: importance=X.X,credibility=Y.Y

Заголовок: {title}
Текст: {content}
"""

    try:
        raw = ask(prompt, model="gpt-4o-mini", max_tokens=30)

        # Парсим ответ
        lines = raw.strip().split("\n")
        for line in lines:
            if "importance=" in line and "credibility=" in line:
                # Извлекаем значения
                parts = line.split(",")
                importance_part = None
                credibility_part = None

                for part in parts:
                    if "importance=" in part:
                        importance_part = part.split("=")[1]
                    if "credibility=" in part:
                        credibility_part = part.split("=")[1]

                if importance_part and credibility_part:
                    importance = max(0.0, min(1.0, float(importance_part.strip())))
                    credibility = max(0.0, min(1.0, float(credibility_part.strip())))
                    return importance, credibility

        # Если парсинг не удался, пробуем найти числа в строке
        import re

        numbers = re.findall(r"0\.\d+|1\.0", raw)
        if len(numbers) >= 2:
            importance = max(0.0, min(1.0, float(numbers[0])))
            credibility = max(0.0, min(1.0, float(numbers[1])))
            return importance, credibility

        logger.warning(f"Не удалось распарсить ответ AI: {raw}")
        return 0.5, 0.5  # fallback
    except Exception as e:
        logger.error(f"Ошибка в едином AI запросе: {e}", exc_info=True)
        return 0.5, 0.5  # fallback

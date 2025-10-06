"""
Metrics module for AI optimization tracking.

This module provides metrics collection for monitoring AI call reduction
and system performance.
"""

import logging
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from threading import Lock

logger = logging.getLogger("metrics")


@dataclass
class Metrics:
    """Metrics data structure."""
    # Counters
    news_processed_total: int = 0
    ai_calls_total: int = 0
    ai_skipped_prefilter_total: int = 0
    ai_skipped_cache_total: int = 0
    ai_skipped_local_pred_total: int = 0
    ai_calls_saved_total: int = 0
    duplicates_skipped_total: int = 0
    
    # Latency tracking
    ai_latency_ms: list = field(default_factory=list)
    prefilter_latency_ms: list = field(default_factory=list)
    cache_latency_ms: list = field(default_factory=list)
    local_pred_latency_ms: list = field(default_factory=list)
    
    # Error tracking
    ai_errors_total: int = 0
    prefilter_errors_total: int = 0
    cache_errors_total: int = 0
    local_pred_errors_total: int = 0
    
    # TTL and adaptive thresholds metrics
    ai_cache_ttl_expired_total: int = 0
    ai_partial_updates_total: int = 0
    adaptive_thresholds_applied_total: int = 0
    adaptive_thresholds_skipped_total: int = 0
    
    # Auto-learning metrics
    auto_learn_runs_total: int = 0
    auto_rules_added_total: int = 0
    auto_rules_removed_total: int = 0
    auto_rules_active_total: int = 0
    auto_learn_last_success_timestamp: str = ""
    
    # Self-tuning metrics
    self_tuning_runs_total: int = 0
    self_tuning_models_trained_total: int = 0
    self_tuning_models_replaced_total: int = 0
    self_tuning_last_run_timestamp: str = ""
    self_tuning_current_model_version: int = 0
    self_tuning_dataset_size: int = 0
    
    # Dataset builder metrics
    dataset_created_total: int = 0
    
    # Telegram autopublish metrics
    digests_published_total: int = 0
    digests_published_today: int = 0
    digests_publish_errors_total: int = 0
    last_digest_published_timestamp: str = ""
    autopublish_skipped_no_content_total: int = 0
    autopublish_latency_ms: List[float] = field(default_factory=list)
    
    # Smart posting metrics
    autopublish_window_current: str = ""
    autopublish_window_posts_total: int = 0
    autopublish_skipped_out_of_window_total: int = 0
    smart_priority_avg_score: float = 0.0
    smart_priority_skipped_total: int = 0
    
    # Teaser generator metrics
    teaser_generated_total: int = 0
    avg_post_length_chars: int = 0
    avg_ai_confidence: float = 0.0
    
    # Review mode metrics
    review_approved_total: int = 0
    review_rejected_total: int = 0
    review_expired_total: int = 0
    
    # Feedback tracking metrics
    reactions_total: int = 0
    avg_reaction_score: float = 0.0
    engagement_score_avg: float = 0.0
    reactions_to_ai_updates_total: int = 0
    
    # Events metrics
    events_processed_total: int = 0
    events_upcoming_7d: int = 0
    events_by_category: Dict[str, int] = field(default_factory=dict)
    events_fetch_errors_total: int = 0
    
    # Event Intelligence metrics
    event_context_generated_total: int = 0
    event_forecasts_total: int = 0
    event_forecast_confidence_avg: float = 0.0
    events_analyzed_total: int = 0
    event_digests_generated_total: int = 0
    events_generated_total: int = 0
    event_feedback_positive_total: int = 0
    event_feedback_negative_total: int = 0
    event_feedback_to_ai_updates_total: int = 0
    
    # Lock for thread safety
    _lock: Lock = field(default_factory=Lock)


class MetricsCollector:
    """
    Thread-safe metrics collector for AI optimization.
    
    Tracks various metrics related to AI call reduction and performance.
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = Metrics()
        self.start_time = time.time()
    
    def increment_news_processed(self) -> None:
        """Increment news processed counter."""
        with self.metrics._lock:
            self.metrics.news_processed_total += 1
    
    def increment_ai_calls(self) -> None:
        """Increment AI calls counter."""
        with self.metrics._lock:
            self.metrics.ai_calls_total += 1
    
    def increment_ai_skipped_prefilter(self) -> None:
        """Increment AI skipped by prefilter counter."""
        with self.metrics._lock:
            self.metrics.ai_skipped_prefilter_total += 1
            self.metrics.ai_calls_saved_total += 1
    
    def increment_ai_skipped_cache(self) -> None:
        """Increment AI skipped by cache counter."""
        with self.metrics._lock:
            self.metrics.ai_skipped_cache_total += 1
            self.metrics.ai_calls_saved_total += 1
    
    def increment_ai_skipped_local_pred(self) -> None:
        """Increment AI skipped by local predictor counter."""
        with self.metrics._lock:
            self.metrics.ai_skipped_local_pred_total += 1
            self.metrics.ai_calls_saved_total += 1
    
    def increment_duplicates_skipped(self) -> None:
        """Increment duplicates skipped counter."""
        with self.metrics._lock:
            self.metrics.duplicates_skipped_total += 1
    
    def increment_ai_errors(self) -> None:
        """Increment AI errors counter."""
        with self.metrics._lock:
            self.metrics.ai_errors_total += 1
    
    def increment_prefilter_errors(self) -> None:
        """Increment prefilter errors counter."""
        with self.metrics._lock:
            self.metrics.prefilter_errors_total += 1
    
    def increment_cache_errors(self) -> None:
        """Increment cache errors counter."""
        with self.metrics._lock:
            self.metrics.cache_errors_total += 1
    
    def increment_local_pred_errors(self) -> None:
        """Increment local predictor errors counter."""
        with self.metrics._lock:
            self.metrics.local_pred_errors_total += 1
    
    def increment_cache_ttl_expired(self) -> None:
        """Increment cache TTL expired counter."""
        with self.metrics._lock:
            self.metrics.ai_cache_ttl_expired_total += 1
    
    def increment_partial_updates(self) -> None:
        """Increment partial updates counter."""
        with self.metrics._lock:
            self.metrics.ai_partial_updates_total += 1
    
    def increment_adaptive_thresholds_applied(self) -> None:
        """Increment adaptive thresholds applied counter."""
        with self.metrics._lock:
            self.metrics.adaptive_thresholds_applied_total += 1
    
    def increment_adaptive_thresholds_skipped(self) -> None:
        """Increment adaptive thresholds skipped counter."""
        with self.metrics._lock:
            self.metrics.adaptive_thresholds_skipped_total += 1
    
    def increment_auto_learn_runs(self) -> None:
        """Increment auto-learning runs counter."""
        with self.metrics._lock:
            self.metrics.auto_learn_runs_total += 1
    
    def increment_auto_rules_added(self, count: int = 1) -> None:
        """Increment auto rules added counter."""
        with self.metrics._lock:
            self.metrics.auto_rules_added_total += count
    
    def increment_auto_rules_removed(self, count: int = 1) -> None:
        """Increment auto rules removed counter."""
        with self.metrics._lock:
            self.metrics.auto_rules_removed_total += count
    
    def update_auto_rules_active_count(self, count: int) -> None:
        """Update active auto rules count."""
        with self.metrics._lock:
            self.metrics.auto_rules_active_total = count
    
    def update_auto_learn_last_success(self, timestamp: str) -> None:
        """Update last successful auto-learning timestamp."""
        with self.metrics._lock:
            self.metrics.auto_learn_last_success_timestamp = timestamp
    
    def increment_self_tuning_runs(self) -> None:
        """Increment self-tuning runs counter."""
        with self.metrics._lock:
            self.metrics.self_tuning_runs_total += 1
    
    def increment_self_tuning_models_trained(self, count: int = 1) -> None:
        """Increment self-tuning models trained counter."""
        with self.metrics._lock:
            self.metrics.self_tuning_models_trained_total += count
    
    def increment_self_tuning_models_replaced(self) -> None:
        """Increment self-tuning models replaced counter."""
        with self.metrics._lock:
            self.metrics.self_tuning_models_replaced_total += 1
    
    def update_self_tuning_last_run(self, timestamp: str) -> None:
        """Update last self-tuning run timestamp."""
        with self.metrics._lock:
            self.metrics.self_tuning_last_run_timestamp = timestamp
    
    def update_self_tuning_model_version(self, version: int) -> None:
        """Update current model version."""
        with self.metrics._lock:
            self.metrics.self_tuning_current_model_version = version
    
    def update_self_tuning_dataset_size(self, size: int) -> None:
        """Update dataset size."""
        with self.metrics._lock:
            self.metrics.self_tuning_dataset_size = size
    
    def increment_dataset_created_total(self) -> None:
        """Increment dataset created counter."""
        with self.metrics._lock:
            self.metrics.dataset_created_total += 1
    
    def increment_digests_published_total(self) -> None:
        """Increment digests published counter."""
        with self.metrics._lock:
            self.metrics.digests_published_total += 1
    
    def increment_digests_publish_errors_total(self) -> None:
        """Increment digests publish errors counter."""
        with self.metrics._lock:
            self.metrics.digests_publish_errors_total += 1
    
    def update_last_digest_published_timestamp(self, timestamp: str) -> None:
        """Update last digest published timestamp."""
        with self.metrics._lock:
            self.metrics.last_digest_published_timestamp = timestamp
    
    def increment_autopublish_skipped_no_content(self) -> None:
        """Increment autopublish skipped no content counter."""
        with self.metrics._lock:
            self.metrics.autopublish_skipped_no_content_total += 1
    
    def record_autopublish_latency(self, latency_ms: float) -> None:
        """Record autopublish latency."""
        with self.metrics._lock:
            self.metrics.autopublish_latency_ms.append(latency_ms)
            # Keep only last 100 measurements
            if len(self.metrics.autopublish_latency_ms) > 100:
                self.metrics.autopublish_latency_ms = self.metrics.autopublish_latency_ms[-100:]
    
    def increment_digests_published_today(self) -> None:
        """Increment digests published today counter."""
        with self.metrics._lock:
            self.metrics.digests_published_today += 1
    
    def update_autopublish_window_current(self, window: str) -> None:
        """Update current autopublish window."""
        with self.metrics._lock:
            self.metrics.autopublish_window_current = window
    
    def increment_autopublish_window_posts_total(self) -> None:
        """Increment autopublish window posts total counter."""
        with self.metrics._lock:
            self.metrics.autopublish_window_posts_total += 1
    
    def increment_autopublish_skipped_out_of_window(self) -> None:
        """Increment autopublish skipped out of window counter."""
        with self.metrics._lock:
            self.metrics.autopublish_skipped_out_of_window_total += 1
    
    def update_smart_priority_avg_score(self, score: float) -> None:
        """Update smart priority average score."""
        with self.metrics._lock:
            self.metrics.smart_priority_avg_score = score
    
    def increment_smart_priority_skipped_total(self, count: int = 1) -> None:
        """Increment smart priority skipped total counter."""
        with self.metrics._lock:
            self.metrics.smart_priority_skipped_total += count
    
    def increment_teaser_generated_total(self) -> None:
        """Increment teaser generated total counter."""
        with self.metrics._lock:
            self.metrics.teaser_generated_total += 1
    
    def update_avg_post_length_chars(self, length: int) -> None:
        """Update average post length in characters."""
        with self.metrics._lock:
            self.metrics.avg_post_length_chars = length
    
    def update_avg_ai_confidence(self, confidence: float) -> None:
        """Update average AI confidence."""
        with self.metrics._lock:
            self.metrics.avg_ai_confidence = confidence
    
    def increment_review_approved_total(self) -> None:
        """Increment review approved total counter."""
        with self.metrics._lock:
            self.metrics.review_approved_total += 1
    
    def increment_review_rejected_total(self) -> None:
        """Increment review rejected total counter."""
        with self.metrics._lock:
            self.metrics.review_rejected_total += 1
    
    def increment_review_expired_total(self) -> None:
        """Increment review expired total counter."""
        with self.metrics._lock:
            self.metrics.review_expired_total += 1
    
    def increment_reactions_total(self, count: int = 1) -> None:
        """Increment reactions total counter."""
        with self.metrics._lock:
            self.metrics.reactions_total += count
    
    def update_avg_reaction_score(self, score: float) -> None:
        """Update average reaction score."""
        with self.metrics._lock:
            self.metrics.avg_reaction_score = score
    
    def update_engagement_score_avg(self, score: float) -> None:
        """Update engagement score average."""
        with self.metrics._lock:
            self.metrics.engagement_score_avg = score
    
    def increment_reactions_to_ai_updates_total(self) -> None:
        """Increment reactions to AI updates total counter."""
        with self.metrics._lock:
            self.metrics.reactions_to_ai_updates_total += 1
    
    def increment_events_processed_total(self, count: int = 1) -> None:
        """Increment events processed total counter."""
        with self.metrics._lock:
            self.metrics.events_processed_total += count
    
    def update_events_upcoming_7d(self, count: int) -> None:
        """Update events upcoming 7 days counter."""
        with self.metrics._lock:
            self.metrics.events_upcoming_7d = count
    
    def update_events_by_category(self, category_counts: Dict[str, int]) -> None:
        """Update events by category counters."""
        with self.metrics._lock:
            self.metrics.events_by_category.update(category_counts)
    
    def increment_events_fetch_errors_total(self) -> None:
        """Increment events fetch errors total counter."""
        with self.metrics._lock:
            self.metrics.events_fetch_errors_total += 1
    
    def increment_event_context_generated_total(self) -> None:
        """Increment event context generated total counter."""
        with self.metrics._lock:
            self.metrics.event_context_generated_total += 1
    
    def increment_event_forecasts_total(self) -> None:
        """Increment event forecasts total counter."""
        with self.metrics._lock:
            self.metrics.event_forecasts_total += 1
    
    def update_event_forecast_confidence_avg(self, confidence: float) -> None:
        """Update event forecast confidence average."""
        with self.metrics._lock:
            # Simple moving average calculation
            current_avg = self.metrics.event_forecast_confidence_avg
            total_forecasts = self.metrics.event_forecasts_total
            if total_forecasts > 0:
                self.metrics.event_forecast_confidence_avg = (
                    (current_avg * (total_forecasts - 1) + confidence) / total_forecasts
                )
            else:
                self.metrics.event_forecast_confidence_avg = confidence
    
    def increment_events_analyzed_total(self, count: int = 1) -> None:
        """Increment events analyzed total counter."""
        with self.metrics._lock:
            self.metrics.events_analyzed_total += count
    
    def increment_event_digests_generated_total(self) -> None:
        """Increment event digests generated total counter."""
        with self.metrics._lock:
            self.metrics.event_digests_generated_total += 1
    
    def increment_events_generated_total(self, count: int = 1) -> None:
        """Increment events generated total counter."""
        with self.metrics._lock:
            self.metrics.events_generated_total += count
    
    def increment_event_feedback_positive_total(self) -> None:
        """Increment event feedback positive total counter."""
        with self.metrics._lock:
            self.metrics.event_feedback_positive_total += 1
    
    def increment_event_feedback_negative_total(self) -> None:
        """Increment event feedback negative total counter."""
        with self.metrics._lock:
            self.metrics.event_feedback_negative_total += 1
    
    def increment_event_feedback_to_ai_updates_total(self) -> None:
        """Increment event feedback to AI updates total counter."""
        with self.metrics._lock:
            self.metrics.event_feedback_to_ai_updates_total += 1
    
    def record_ai_latency(self, latency_ms: float) -> None:
        """Record AI call latency."""
        with self.metrics._lock:
            self.metrics.ai_latency_ms.append(latency_ms)
            # Keep only last 1000 measurements
            if len(self.metrics.ai_latency_ms) > 1000:
                self.metrics.ai_latency_ms = self.metrics.ai_latency_ms[-1000:]
    
    def record_prefilter_latency(self, latency_ms: float) -> None:
        """Record prefilter latency."""
        with self.metrics._lock:
            self.metrics.prefilter_latency_ms.append(latency_ms)
            if len(self.metrics.prefilter_latency_ms) > 1000:
                self.metrics.prefilter_latency_ms = self.metrics.prefilter_latency_ms[-1000:]
    
    def record_cache_latency(self, latency_ms: float) -> None:
        """Record cache latency."""
        with self.metrics._lock:
            self.metrics.cache_latency_ms.append(latency_ms)
            if len(self.metrics.cache_latency_ms) > 1000:
                self.metrics.cache_latency_ms = self.metrics.cache_latency_ms[-1000:]
    
    def record_local_pred_latency(self, latency_ms: float) -> None:
        """Record local predictor latency."""
        with self.metrics._lock:
            self.metrics.local_pred_latency_ms.append(latency_ms)
            if len(self.metrics.local_pred_latency_ms) > 1000:
                self.metrics.local_pred_latency_ms = self.metrics.local_pred_latency_ms[-1000:]
    
    def get_metrics_summary(self) -> Dict:
        """Get comprehensive metrics summary."""
        with self.metrics._lock:
            uptime_seconds = time.time() - self.start_time
            
            # Calculate averages
            ai_avg_latency = (
                sum(self.metrics.ai_latency_ms) / len(self.metrics.ai_latency_ms)
                if self.metrics.ai_latency_ms else 0
            )
            
            prefilter_avg_latency = (
                sum(self.metrics.prefilter_latency_ms) / len(self.metrics.prefilter_latency_ms)
                if self.metrics.prefilter_latency_ms else 0
            )
            
            cache_avg_latency = (
                sum(self.metrics.cache_latency_ms) / len(self.metrics.cache_latency_ms)
                if self.metrics.cache_latency_ms else 0
            )
            
            autopublish_avg_latency = (
                sum(self.metrics.autopublish_latency_ms) / len(self.metrics.autopublish_latency_ms)
                if self.metrics.autopublish_latency_ms else 0
            )
            
            local_pred_avg_latency = (
                sum(self.metrics.local_pred_latency_ms) / len(self.metrics.local_pred_latency_ms)
                if self.metrics.local_pred_latency_ms else 0
            )
            
            # Calculate error rates
            ai_error_rate = (
                self.metrics.ai_errors_total / max(1, self.metrics.ai_calls_total)
            )
            
            # Calculate efficiency metrics
            ai_calls_saved_percentage = (
                (self.metrics.ai_calls_saved_total / max(1, self.metrics.news_processed_total)) * 100
            )
            
            return {
                # Counters
                'news_processed_total': self.metrics.news_processed_total,
                'ai_calls_total': self.metrics.ai_calls_total,
                'ai_skipped_prefilter_total': self.metrics.ai_skipped_prefilter_total,
                'ai_skipped_cache_total': self.metrics.ai_skipped_cache_total,
                'ai_skipped_local_pred_total': self.metrics.ai_skipped_local_pred_total,
                'ai_calls_saved_total': self.metrics.ai_calls_saved_total,
                'duplicates_skipped_total': self.metrics.duplicates_skipped_total,
                
                # Error counters
                'ai_errors_total': self.metrics.ai_errors_total,
                'prefilter_errors_total': self.metrics.prefilter_errors_total,
                'cache_errors_total': self.metrics.cache_errors_total,
                'local_pred_errors_total': self.metrics.local_pred_errors_total,
                
                # TTL and adaptive thresholds metrics
                'ai_cache_ttl_expired_total': self.metrics.ai_cache_ttl_expired_total,
                'ai_partial_updates_total': self.metrics.ai_partial_updates_total,
                'adaptive_thresholds_applied_total': self.metrics.adaptive_thresholds_applied_total,
                'adaptive_thresholds_skipped_total': self.metrics.adaptive_thresholds_skipped_total,
                
                # Auto-learning metrics
                'auto_learn_runs_total': self.metrics.auto_learn_runs_total,
                'auto_rules_added_total': self.metrics.auto_rules_added_total,
                'auto_rules_removed_total': self.metrics.auto_rules_removed_total,
                'auto_rules_active_total': self.metrics.auto_rules_active_total,
                'auto_learn_last_success_timestamp': self.metrics.auto_learn_last_success_timestamp,
                
                # Self-tuning metrics
                'self_tuning_runs_total': self.metrics.self_tuning_runs_total,
                'self_tuning_models_trained_total': self.metrics.self_tuning_models_trained_total,
                'self_tuning_models_replaced_total': self.metrics.self_tuning_models_replaced_total,
                'self_tuning_last_run_timestamp': self.metrics.self_tuning_last_run_timestamp,
                'self_tuning_current_model_version': self.metrics.self_tuning_current_model_version,
                'self_tuning_dataset_size': self.metrics.self_tuning_dataset_size,
                
                # Dataset builder metrics
                'dataset_created_total': self.metrics.dataset_created_total,
                
                # Telegram autopublish metrics
                'digests_published_total': self.metrics.digests_published_total,
                'digests_publish_errors_total': self.metrics.digests_publish_errors_total,
                'last_digest_published_timestamp': self.metrics.last_digest_published_timestamp,
                'autopublish_skipped_no_content_total': self.metrics.autopublish_skipped_no_content_total,
                
                # Latency metrics
                'ai_avg_latency_ms': round(ai_avg_latency, 2),
                'prefilter_avg_latency_ms': round(prefilter_avg_latency, 2),
                'cache_avg_latency_ms': round(cache_avg_latency, 2),
                'autopublish_avg_latency_ms': round(autopublish_avg_latency, 2),
                'local_pred_avg_latency_ms': round(local_pred_avg_latency, 2),
                
                # Error rates
                'ai_error_rate': round(ai_error_rate, 4),
                
                # Efficiency metrics
                'ai_calls_saved_percentage': round(ai_calls_saved_percentage, 2),
                
                # System metrics
                'uptime_seconds': round(uptime_seconds, 2),
                'news_per_second': round(self.metrics.news_processed_total / max(1, uptime_seconds), 2),
            }
    
    def reset_metrics(self) -> None:
        """Reset all metrics to zero."""
        with self.metrics._lock:
            self.metrics = Metrics()
            self.start_time = time.time()
        logger.info("Metrics reset")


# Global metrics collector instance
_metrics_instance: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Get global metrics collector instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector()
    return _metrics_instance


# Convenience functions for common metric operations
def track_ai_call(func):
    """Decorator to track AI calls and latency."""
    def wrapper(*args, **kwargs):
        metrics = get_metrics()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            metrics.increment_ai_calls()
            latency_ms = (time.time() - start_time) * 1000
            metrics.record_ai_latency(latency_ms)
            return result
        except Exception as e:
            metrics.increment_ai_errors()
            raise e
    
    return wrapper


def track_prefilter_call(func):
    """Decorator to track prefilter calls and latency."""
    def wrapper(*args, **kwargs):
        metrics = get_metrics()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            latency_ms = (time.time() - start_time) * 1000
            metrics.record_prefilter_latency(latency_ms)
            return result
        except Exception as e:
            metrics.increment_prefilter_errors()
            raise e
    
    return wrapper


def track_cache_call(func):
    """Decorator to track cache calls and latency."""
    def wrapper(*args, **kwargs):
        metrics = get_metrics()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            latency_ms = (time.time() - start_time) * 1000
            metrics.record_cache_latency(latency_ms)
            return result
        except Exception as e:
            metrics.increment_cache_errors()
            raise e
    
    return wrapper

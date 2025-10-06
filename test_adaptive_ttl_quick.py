#!/usr/bin/env python3
"""
Quick test for adaptive thresholds and TTL functionality.

This script tests the new adaptive thresholds and TTL cache features
with synthetic data.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_modules.adaptive_thresholds import get_adaptive_thresholds
from ai_modules.cache import get_cache
from ai_modules.metrics import get_metrics


def test_adaptive_thresholds_and_ttl():
    """Test adaptive thresholds and TTL functionality."""
    print("🧠 Testing Adaptive Thresholds & TTL System")
    print("=" * 60)

    # Test adaptive thresholds
    print("🎯 Testing Adaptive Thresholds:")
    adaptive_thresholds = get_adaptive_thresholds()

    categories = ["crypto", "tech", "sports", "world", "unknown"]

    for category in categories:
        importance_thresh, credibility_thresh = adaptive_thresholds.get_thresholds(category)
        print(f"   {category}: importance>{importance_thresh}, credibility>{credibility_thresh}")

    print()

    # Test threshold checking
    print("📊 Testing Threshold Checking:")
    test_scores = [
        (0.8, 0.9, "crypto", "High scores"),
        (0.5, 0.7, "crypto", "Low importance"),
        (0.7, 0.6, "crypto", "Low credibility"),
        (0.6, 0.8, "tech", "Tech scores"),
        (0.4, 0.5, "sports", "Sports scores"),
    ]

    for importance, credibility, category, description in test_scores:
        passed, reason = adaptive_thresholds.check_thresholds(importance, credibility, category)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {description}: {importance}/{credibility} for {category} - {reason}")

    print()

    # Test TTL cache
    print("💾 Testing TTL Cache:")
    cache = get_cache()

    print(f"   TTL enabled: {cache.is_ttl_enabled()}")
    print(f"   TTL days: {cache.ttl_days}")
    print(f"   Partial update: {cache.partial_update}")

    # Test cache operations
    test_news = {
        "title": "Bitcoin ETF approved by SEC in major regulatory breakthrough",
        "link": "https://reuters.com/bitcoin-etf-approved",
        "source": "reuters.com",
        "published_at": "2025-01-01T10:00:00Z",
        "category": "crypto",
    }

    # Set cache entry
    cache.set(test_news, 0.8, 0.9, "Test summary")
    print("   ✅ Cache entry set")

    # Get cache entry
    entry = cache.get(test_news)
    if entry:
        print(f"   ✅ Cache hit: importance={entry.ai_importance}, credibility={entry.ai_credibility}")
        print(f"      TTL expires: {entry.ttl_expires_at}")

        # Test needs refresh
        needs_refresh = cache.needs_refresh(entry)
        print(f"   📋 Needs refresh: {needs_refresh}")

        # Test partial update
        cache.update_partial(test_news, credibility=0.95)
        updated_entry = cache.get(test_news)
        if updated_entry:
            print(f"   🔄 Partial update: credibility={updated_entry.ai_credibility}")
    else:
        print("   ❌ Cache miss")

    print()

    # Test metrics
    print("📈 Testing New Metrics:")
    metrics = get_metrics()

    # Simulate some operations
    metrics.increment_cache_ttl_expired()
    metrics.increment_partial_updates()
    metrics.increment_adaptive_thresholds_applied()
    metrics.increment_adaptive_thresholds_skipped()

    metrics_summary = metrics.get_metrics_summary()

    print(f"   Cache TTL expired: {metrics_summary['ai_cache_ttl_expired_total']}")
    print(f"   Partial updates: {metrics_summary['ai_partial_updates_total']}")
    print(f"   Adaptive thresholds applied: {metrics_summary['adaptive_thresholds_applied_total']}")
    print(f"   Adaptive thresholds skipped: {metrics_summary['adaptive_thresholds_skipped_total']}")

    print()

    # Test configuration
    print("⚙️ Configuration Summary:")
    stats = adaptive_thresholds.get_stats()
    cache_stats = cache.get_stats()

    print(f"   Adaptive thresholds enabled: {stats['enabled']}")
    print(f"   Categories with thresholds: {stats['categories_with_thresholds']}")
    print(f"   Cache enabled: {cache_stats['enabled']}")
    print(f"   Cache size: {cache_stats['size']}")

    print()
    print("✅ Adaptive Thresholds & TTL test completed!")
    return True


if __name__ == "__main__":
    try:
        test_adaptive_thresholds_and_ttl()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

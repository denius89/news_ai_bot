#!/usr/bin/env python3
"""
Quick test for AI optimization system.

This script tests the basic functionality of the optimization system
with a small set of synthetic news items.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_modules.prefilter import get_prefilter
from ai_modules.cache import get_cache
from ai_modules.local_predictor import get_predictor
from ai_modules.metrics import get_metrics
from ai_modules.optimized_importance import evaluate_importance
from ai_modules.optimized_credibility import evaluate_credibility


def test_optimization_system():
    """Test the optimization system with synthetic data."""
    print("🧠 Testing AI Optimization System")
    print("=" * 50)

    # Test news items
    test_news = [
        {
            "title": "SEC approves Bitcoin ETF in major regulatory breakthrough for cryptocurrency markets",
            "content": "The Securities and Exchange Commission has officially approved the first Bitcoin ETF, marking a significant milestone in cryptocurrency regulation...",
            "source": "reuters.com",
            "category": "crypto",
            "published_at": "2025-01-01T10:00:00Z",
            "link": "https://reuters.com/bitcoin-etf-approved",
        },
        {
            "title": "Bitcoin price prediction click here to buy now",
            "content": "This is a sponsored advertisement about Bitcoin price predictions...",
            "source": "unknown-blog.com",
            "category": "crypto",
            "published_at": "2025-01-01T11:00:00Z",
            "link": "https://unknown-blog.com/bitcoin-ad",
        },
        {
            "title": "Major security vulnerability discovered in popular JavaScript library",
            "content": "A critical security vulnerability has been discovered in a widely used JavaScript library, affecting millions of websites...",
            "source": "github.com",
            "category": "tech",
            "published_at": "2025-01-01T12:00:00Z",
            "link": "https://github.com/security-advisory",
        },
    ]

    # Initialize components
    prefilter = get_prefilter()
    cache = get_cache()
    predictor = get_predictor()
    metrics = get_metrics()

    print(f"📊 Configuration:")
    print(f"   Prefilter enabled: {prefilter.is_enabled()}")
    print(f"   Cache enabled: {cache.is_enabled()}")
    print(f"   Local predictor enabled: {predictor.is_enabled()}")
    print()

    # Test each component
    print("🔍 Testing Prefilter:")
    for i, news in enumerate(test_news):
        result = prefilter.filter_news(news)
        status = "✅ PASS" if result.passed else "❌ FILTERED"
        print(f"   {i+1}. {status} - {news['title'][:50]}... (score: {result.score:.2f})")
    print()

    print("💾 Testing Cache:")
    for i, news in enumerate(test_news):
        # First check (should miss)
        entry = cache.get(news)
        if entry:
            print(f"   {i+1}. Cache HIT - {news['title'][:50]}...")
        else:
            print(f"   {i+1}. Cache MISS - {news['title'][:50]}...")

        # Store in cache
        cache.set(news, 0.8, 0.9, f"Test summary {i}")

        # Second check (should hit)
        entry = cache.get(news)
        if entry:
            print(f"      → Now cached: importance={entry.ai_importance}, credibility={entry.ai_credibility}")
    print()

    print("🧠 Testing Local Predictor:")
    for i, news in enumerate(test_news):
        result = predictor.predict(news)
        print(f"   {i+1}. {news['title'][:50]}...")
        print(
            f"      Importance: {result.importance:.2f}, Credibility: {result.credibility:.2f}, Confidence: {result.confidence:.2f}"
        )
    print()

    print("🤖 Testing Optimized Evaluation:")
    for i, news in enumerate(test_news):
        print(f"   {i+1}. {news['title'][:50]}...")

        # Test importance evaluation
        try:
            importance = evaluate_importance(news)
            print(f"      Importance: {importance:.2f}")
        except Exception as e:
            print(f"      Importance: ERROR - {e}")

        # Test credibility evaluation
        try:
            credibility = evaluate_credibility(news)
            print(f"      Credibility: {credibility:.2f}")
        except Exception as e:
            print(f"      Credibility: ERROR - {e}")
    print()

    print("📊 Final Metrics:")
    metrics_summary = metrics.get_metrics_summary()
    print(f"   News processed: {metrics_summary['news_processed_total']}")
    print(f"   AI calls made: {metrics_summary['ai_calls_total']}")
    print(f"   AI calls saved: {metrics_summary['ai_calls_saved_total']}")
    print(f"   Optimization efficiency: {metrics_summary['ai_calls_saved_percentage']:.1f}%")
    print()

    print("✅ Optimization system test completed!")
    return True


if __name__ == "__main__":
    try:
        test_optimization_system()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

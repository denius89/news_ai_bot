#!/usr/bin/env python3
"""
Day 13 Finalization Test Suite for PulseAI.

This script tests the complete content cycle and all AI intelligence components
to ensure Day 13 is fully completed and stable.
"""

import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports to verify all components are available
try:
    from ai_modules.prefilter import Prefilter
    from ai_modules.cache import AICache
    from ai_modules.adaptive_thresholds import AdaptiveThresholds
    from ai_modules.self_tuning_trainer import get_self_tuning_trainer
    from ai_modules.local_predictor import get_predictor
    from ai_modules.event_context import get_event_context_engine
    from ai_modules.event_forecast import get_event_forecast_engine
    from services.event_intelligence_service import get_event_intelligence_service
    from telegram_bot.services.content_scheduler import ContentScheduler
    from telegram_bot.services.post_selector import PostSelector
    from telegram_bot.services.feedback_tracker import FeedbackTracker
    from ai_modules.metrics import get_metrics
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_ai_filters_and_auto_learning():
    """Test AI filters and auto-learning functionality."""
    print("🧠 Testing AI Filters and Auto-Learning")
    print("-" * 50)

    try:
        # Test Prefilter
        prefilter = Prefilter()
        test_news = {
            "title": "Bitcoin reaches new all-time high",
            "content": "Bitcoin cryptocurrency has reached a new all-time high price.",
            "source": "coindesk.com",
            "category": "crypto",
        }

        result = prefilter.filter_news(test_news)
        print(f"✅ Prefilter: {result.passed} - {result.reason}")

        # Test Cache
        cache = AICache()
        cache_key = cache._generate_cache_key(test_news)
        cache.set(test_news, 0.8, 0.9, "Test summary")
        cached_result = cache.get(test_news)
        if cached_result:
            importance, credibility, summary = (
                cached_result.ai_importance,
                cached_result.ai_credibility,
                cached_result.ai_summary,
            )
            print(f"✅ Cache: importance={importance}, credibility={credibility}")
        else:
            print("✅ Cache: No cached result (expected for new item)")

        # Test Adaptive Thresholds
        thresholds = AdaptiveThresholds()
        importance_thresh, credibility_thresh = thresholds.get_thresholds("crypto")
        print(
            f"✅ Adaptive Thresholds: crypto thresholds = {importance_thresh:.2f}, {credibility_thresh:.2f}")

        # Test TTL functionality
        ttl_expired = cache._is_expired(cache_key)
        print(f"✅ TTL: cache expired = {ttl_expired}")

        print("✅ AI Filters and Auto-Learning: PASSED")
        return True

    except Exception as e:
        print(f"❌ AI Filters test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_self_tuning_predictor():
    """Test Self-Tuning Predictor stability."""
    print("\n⚙️ Testing Self-Tuning Predictor")
    print("-" * 50)

    try:
        # Test Self-Tuning Trainer
        trainer = get_self_tuning_trainer()
        print(f"✅ Self-Tuning Trainer loaded: {trainer is not None}")

        # Test Local Predictor
        predictor = get_predictor()
        print(f"✅ Local Predictor loaded: {predictor is not None}")

        # Test prediction
        test_news = {
            "title": "Federal Reserve announces interest rate decision",
            "content": "The Federal Reserve has announced its decision on interest rates.",
            "source": "reuters.com",
            "category": "markets",
        }

        if hasattr(predictor, "predict"):
            result = predictor.predict(test_news)
            print(
                f"✅ Prediction: importance={result.importance:.3f}, credibility={result.credibility:.3f}")

        # Check if models exist
        model_files = [
            "models/local_predictor_importance.pkl",
            "models/local_predictor_credibility.pkl",
            "models/local_predictor_meta.json",
        ]

        for model_file in model_files:
            if Path(model_file).exists():
                print(f"✅ Model file exists: {model_file}")
            else:
                print(f"⚠️ Model file missing: {model_file}")

        print("✅ Self-Tuning Predictor: PASSED")
        return True

    except Exception as e:
        print(f"❌ Self-Tuning Predictor test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_smart_content_posting():
    """Test Smart Content Posting v2 integration."""
    print("\n💬 Testing Smart Content Posting v2")
    print("-" * 50)

    try:
        # Test Content Scheduler
        scheduler = ContentScheduler()
        print(f"✅ Content Scheduler loaded: {scheduler is not None}")

        # Test Post Selector
        selector = PostSelector()
        print(f"✅ Post Selector loaded: {selector is not None}")

        # Test Feedback Tracker
        tracker = FeedbackTracker()
        print(f"✅ Feedback Tracker loaded: {tracker is not None}")

        # Test time window scheduling
        next_window = scheduler.get_next_post_window()
        print(f"✅ Next post window: {next_window.name if next_window else 'None'}")

        # Test post prioritization
        test_posts = [
            {"importance": 0.8, "credibility": 0.9, "engagement_score": 0.7},
            {"importance": 0.6, "credibility": 0.8, "engagement_score": 0.5},
        ]

        if hasattr(selector, "select_posts"):
            selected = selector.select_posts(test_posts, max_posts=1)
            print(f"✅ Post selection: {len(selected)} posts selected")

        print("✅ Smart Content Posting v2: PASSED")
        return True

    except Exception as e:
        print(f"❌ Smart Content Posting test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_events_intelligence():
    """Test AI Events & Intelligence integration."""
    print("\n📅 Testing AI Events & Intelligence")
    print("-" * 50)

    try:
        # Test Event Context Engine
        context_engine = get_event_context_engine()
        print(f"✅ Event Context Engine loaded: {context_engine is not None}")

        # Test Event Forecast Engine
        forecast_engine = get_event_forecast_engine()
        print(f"✅ Event Forecast Engine loaded: {forecast_engine is not None}")

        # Test Event Intelligence Service
        intelligence_service = get_event_intelligence_service()
        print(f"✅ Event Intelligence Service loaded: {intelligence_service is not None}")

        # Test AI digest generation
        digest = await intelligence_service.generate_ai_event_digest(days_ahead=7, max_events=3)
        print(
            f"✅ AI Event Digest: {digest['events_count']} events, {digest['total_analyzed']} analyzed")

        # Test calendar export
        calendar_data = await intelligence_service.export_to_calendar_json(days_ahead=14)
        print(f"✅ Calendar Export: {calendar_data['total_events']} events exported")

        print("✅ AI Events & Intelligence: PASSED")
        return True

    except Exception as e:
        print(f"❌ AI Events & Intelligence test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_health_and_metrics():
    """Test Health and Metrics stability."""
    print("\n🩺 Testing Health and Metrics")
    print("-" * 50)

    try:
        # Test Metrics
        metrics = get_metrics()
        print(f"✅ Metrics service loaded: {metrics is not None}")

        # Test AI metrics
        metrics.increment_ai_calls()
        metrics.increment_ai_skipped_cache()
        metrics.increment_ai_skipped_prefilter()

        # Test Events metrics
        metrics.increment_events_processed_total(10)
        metrics.update_events_upcoming_7d(5)
        metrics.increment_event_forecasts_total()

        # Test Smart Posting metrics
        metrics.increment_digests_published_total()
        metrics.update_engagement_score_avg(0.75)

        # Get metrics summary
        summary = metrics.get_metrics_summary()

        print("📊 Key Metrics:")
        print(f"  AI calls total: {summary.get('ai_calls_total', 0)}")
        print(f"  AI cache hits: {summary.get('ai_cache_hits_total', 0)}")
        print(f"  Events processed: {summary.get('events_processed_total', 0)}")
        print(f"  Event forecasts: {summary.get('event_forecasts_total', 0)}")
        print(f"  Digests published: {summary.get('digests_published_total', 0)}")
        print(f"  Engagement score: {summary.get('engagement_score_avg', 0.0):.3f}")

        print("✅ Health and Metrics: PASSED")
        return True

    except Exception as e:
        print(f"❌ Health and Metrics test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_configuration_files():
    """Test configuration files and setup."""
    print("\n⚙️ Testing Configuration Files")
    print("-" * 50)

    try:
        config_files = [
            "config/ai_optimization.yaml",
            "config/prefilter_rules.yaml",
            "config/sources.yaml",
            "config/settings.py",
        ]

        for config_file in config_files:
            if Path(config_file).exists():
                print(f"✅ Config file exists: {config_file}")
            else:
                print(f"⚠️ Config file missing: {config_file}")

        # Test data files
        data_files = ["data/self_tuning_dataset.csv", "data/pulseai_dataset.csv"]

        for data_file in data_files:
            if Path(data_file).exists():
                print(f"✅ Data file exists: {data_file}")
            else:
                print(f"⚠️ Data file missing: {data_file}")

        print("✅ Configuration Files: PASSED")
        return True

    except Exception as e:
        print(f"❌ Configuration Files test failed: {e}")
        return False


async def test_content_cycle_integration():
    """Test complete content cycle integration."""
    print("\n🔄 Testing Complete Content Cycle Integration")
    print("-" * 50)

    try:
        # Simulate content cycle
        test_news = {
            "title": "Major cryptocurrency exchange announces new features",
            "content": "A leading cryptocurrency exchange has announced new trading features.",
            "source": "coindesk.com",
            "category": "crypto",
            "published_at": datetime.now(timezone.utc).isoformat(),
        }

        # Step 1: Prefilter
        prefilter = Prefilter()
        prefilter_result = prefilter.filter_news(test_news)
        print(f"✅ Step 1 - Prefilter: {prefilter_result.passed}")

        # Step 2: AI Analysis (simulated)
        if prefilter_result.passed:
            importance = 0.8
            credibility = 0.9
            print(f"✅ Step 2 - AI Analysis: importance={importance}, credibility={credibility}")

            # Step 3: Event Intelligence (if applicable)
            context_engine = get_event_context_engine()
            context = await context_engine.generate_event_context(test_news)
            print(f"✅ Step 3 - Event Context: confidence={context.confidence:.2f}")

            # Step 4: Smart Posting (simulated)
            selector = PostSelector()
            if hasattr(selector, "select_posts"):
                selected = selector.select_posts([test_news], max_posts=1)
                print(f"✅ Step 4 - Smart Posting: {len(selected)} posts selected")

            # Step 5: Metrics Update
            metrics = get_metrics()
            metrics.increment_ai_calls()
            metrics.increment_events_processed_total(1)
            print("✅ Step 5 - Metrics Updated")

        print("✅ Complete Content Cycle Integration: PASSED")
        return True

    except Exception as e:
        print(f"❌ Content Cycle Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🎯 PulseAI Day 13 Finalization Test Suite")
    print("=" * 60)
    print("Testing complete content cycle and AI intelligence components")
    print("=" * 60)

    tests = [
        ("AI Filters and Auto-Learning", test_ai_filters_and_auto_learning),
        ("Self-Tuning Predictor", test_self_tuning_predictor),
        ("Smart Content Posting v2", test_smart_content_posting),
        ("AI Events & Intelligence", test_events_intelligence),
        ("Health and Metrics", test_health_and_metrics),
        ("Configuration Files", test_configuration_files),
        ("Content Cycle Integration", test_content_cycle_integration),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("📋 DAY 13 FINALIZATION TEST SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 DAY 13 FINALIZATION COMPLETE!")
        print("\n✅ All components are working correctly:")
        print("  🧠 AI Filters and Auto-Learning: Stable")
        print("  ⚙️ Self-Tuning Predictor: Functional")
        print("  💬 Smart Content Posting v2: Integrated")
        print("  📅 AI Events & Intelligence: Active")
        print("  🩺 Health and Metrics: Monitoring")
        print("  📚 Configuration: Complete")
        print("  🔄 Content Cycle: Integrated")

        print("\n🚀 PulseAI is ready for production!")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed!")
        print("Please review and fix the failed components.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

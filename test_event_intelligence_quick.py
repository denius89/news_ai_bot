#!/usr/bin/env python3
"""
Quick test for Event Intelligence System functionality.

This script tests the AI Event Intelligence System components
including context generation, forecasting, and integration.
"""

from ai_modules.metrics import get_metrics
from ai_modules.event_generator import get_event_generator
from services.event_intelligence_service import get_event_intelligence_service
from ai_modules.event_forecast import get_event_forecast_engine, ImpactType
from ai_modules.event_context import get_event_context_engine
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_event_context_engine():
    """Test event context engine functionality."""
    print("🧠 Testing Event Context Engine")
    print("-" * 40)

    try:
        engine = get_event_context_engine()

        print(f"Context engine initialized")
        print(f"Context templates: {len(engine.context_templates)} categories")
        print(f"Trend keywords: {len(engine.trend_keywords)} categories")

        # Test event type classification
        test_events = [
            ("Bitcoin ETF Approval", "crypto"),
            ("FOMC Meeting", "markets"),
            ("Championship Finals", "sports"),
            ("AI Platform Launch", "tech"),
            ("Climate Summit", "world"),
        ]

        print("\nEvent type classification:")
        for title, category in test_events:
            event_type = engine._classify_event_type(title, category)
            print(f"  {title} ({category}) → {event_type}")

        print("✅ Event context engine test passed")
        return True

    except Exception as e:
        print(f"❌ Event context engine test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_event_forecast_engine():
    """Test event forecast engine functionality."""
    print("\n📈 Testing Event Forecast Engine")
    print("-" * 40)

    try:
        engine = get_event_forecast_engine()

        print(f"Forecast engine initialized")
        print(f"Impact patterns: {len(engine.impact_patterns)} categories")

        # Test impact prediction
        test_events = [
            ("Bitcoin Upgrade Launch", "crypto", 0.8),
            ("Federal Reserve Rate Cut", "markets", 0.9),
            ("Championship Victory", "sports", 0.7),
            ("Security Breach", "tech", 0.6),
            ("Peace Agreement", "world", 0.8),
        ]

        print("\nImpact prediction:")
        for title, category, importance in test_events:
            impact = engine._predict_impact(title, category, "", importance)
            confidence = engine._calculate_confidence(title, category, importance)
            print(f"  {title} ({category}) → {impact.value} (confidence: {confidence:.2f})")

        print("✅ Event forecast engine test passed")
        return True

    except Exception as e:
        print(f"❌ Event forecast engine test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_event_intelligence_service():
    """Test event intelligence service integration."""
    print("\n🔗 Testing Event Intelligence Service")
    print("-" * 40)

    try:
        service = get_event_intelligence_service()

        print("Service initialized with all components")

        # Test AI digest generation
        print("Generating AI event digest...")
        digest = await service.generate_ai_event_digest(days_ahead=7, max_events=3)

        print(f"Digest generated: {digest['events_count']} events")
        print(f"Total analyzed: {digest['total_analyzed']} events")

        if digest["content"]:
            print("Digest content preview:")
            print(f"  {digest['content'][:100]}...")

        # Test calendar export
        print("\nExporting calendar data...")
        calendar_data = await service.export_to_calendar_json(days_ahead=14)

        print(f"Calendar export: {calendar_data['total_events']} events")
        print(
            f"Date range: {calendar_data['date_range']['start']} to {calendar_data['date_range']['end']}")

        if calendar_data["categories"]:
            print(f"Categories: {', '.join(calendar_data['categories'])}")

        print("✅ Event intelligence service test passed")
        return True

    except Exception as e:
        print(f"❌ Event intelligence service test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_event_generator():
    """Test event generator (draft module)."""
    print("\n🔮 Testing Event Generator (Draft)")
    print("-" * 40)

    try:
        generator = get_event_generator()

        print("Event generator initialized (draft module)")

        # Test pattern extraction
        test_text = "The company plans to launch a new AI platform next month according to official sources."
        patterns = generator.extract_patterns_from_text(test_text)

        print(f"Pattern extraction test: {len(patterns)} patterns found")
        for pattern in patterns[:2]:  # Show first 2 patterns
            print(f"  {pattern['category']} - {pattern['type']}: {pattern['pattern']}")

        # Test event generation
        print("\nGenerating probable events...")
        generated_events = await generator.generate_probable_events(days_ahead=30)

        print(f"Generated {len(generated_events)} probable events")
        for event in generated_events[:2]:  # Show first 2 events
            print(f"  {event.title} (confidence: {event.confidence:.2f})")

        # Test generation stats
        stats = generator.get_generation_stats()
        print(f"\nGeneration stats:")
        print(f"  Patterns available: {stats['patterns_available']}")
        print(f"  Categories supported: {stats['categories_supported']}")
        print(f"  Module status: {stats['module_status']}")

        print("✅ Event generator test passed")
        return True

    except Exception as e:
        print(f"❌ Event generator test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_event_context_generation():
    """Test actual event context generation."""
    print("\n💭 Testing Event Context Generation")
    print("-" * 40)

    try:
        context_engine = get_event_context_engine()

        # Test event
        test_event = {
            "id": 1,
            "title": "Ethereum Merge Upgrade",
            "category": "crypto",
            "subcategory": "ethereum",
            "description": "Major upgrade to Ethereum network switching to Proof of Stake consensus",
            "importance": 0.9,
            "source": "ethereum.org",
            "link": "https://ethereum.org/merge",
            "starts_at": datetime.now(timezone.utc) + timedelta(days=10),
            "ends_at": None,
        }

        print(f"Generating context for: {test_event['title']}")

        # Generate context
        context = await context_engine.generate_event_context(test_event)

        print(f"Generated context: {context.context}")
        print(f"Related trends: {', '.join(context.related_trends)}")
        print(f"Significance: {context.significance_explanation}")
        print(f"Market impact: {context.market_impact}")
        print(f"Confidence: {context.confidence:.2f}")

        print("✅ Event context generation test passed")
        return True

    except Exception as e:
        print(f"❌ Event context generation test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_event_forecast_generation():
    """Test actual event forecast generation."""
    print("\n🔮 Testing Event Forecast Generation")
    print("-" * 40)

    try:
        forecast_engine = get_event_forecast_engine()

        # Test event
        test_event = {
            "id": 1,
            "title": "FOMC Interest Rate Decision",
            "category": "markets",
            "subcategory": "monetary_policy",
            "description": "Federal Open Market Committee meeting to decide on interest rates",
            "importance": 0.95,
            "source": "federalreserve.gov",
            "link": "https://federalreserve.gov/fomc",
            "starts_at": datetime.now(timezone.utc) + timedelta(days=5),
            "ends_at": None,
        }

        print(f"Generating forecast for: {test_event['title']}")

        # Generate forecast
        forecast = await forecast_engine.generate_event_forecast(test_event)

        print(f"Impact prediction: {forecast.impact.value}")
        print(f"Confidence: {forecast.confidence:.2f}")
        print(f"Summary: {forecast.summary}")
        print(f"Market reaction: {forecast.market_reaction}")

        print(f"Probability outcomes:")
        for outcome, probability in forecast.probability_outcomes:
            print(f"  {outcome}: {probability:.2f}")

        print(f"Risk factors: {', '.join(forecast.risk_factors)}")
        print(f"Opportunities: {', '.join(forecast.opportunities)}")

        print("✅ Event forecast generation test passed")
        return True

    except Exception as e:
        print(f"❌ Event forecast generation test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_event_intelligence_metrics():
    """Test event intelligence metrics integration."""
    print("\n📊 Testing Event Intelligence Metrics")
    print("-" * 40)

    try:
        metrics = get_metrics()

        # Test new metrics methods
        metrics.increment_event_context_generated_total()
        metrics.increment_event_forecasts_total()
        metrics.update_event_forecast_confidence_avg(0.85)
        metrics.increment_events_analyzed_total(5)
        metrics.increment_event_digests_generated_total()
        metrics.increment_events_generated_total(3)
        metrics.increment_event_feedback_positive_total()
        metrics.increment_event_feedback_negative_total()
        metrics.increment_event_feedback_to_ai_updates_total()

        # Get metrics summary
        summary = metrics.get_metrics_summary()

        print("Event Intelligence Metrics:")
        print(f"  Event context generated: {summary.get('event_context_generated_total', 0)}")
        print(f"  Event forecasts: {summary.get('event_forecasts_total', 0)}")
        print(f"  Forecast confidence avg: {summary.get('event_forecast_confidence_avg', 0.0):.3f}")
        print(f"  Events analyzed: {summary.get('events_analyzed_total', 0)}")
        print(f"  Event digests generated: {summary.get('event_digests_generated_total', 0)}")
        print(f"  Events generated: {summary.get('events_generated_total', 0)}")
        print(f"  Feedback positive: {summary.get('event_feedback_positive_total', 0)}")
        print(f"  Feedback negative: {summary.get('event_feedback_negative_total', 0)}")
        print(f"  Feedback to AI updates: {summary.get('event_feedback_to_ai_updates_total', 0)}")

        print("✅ Event intelligence metrics test passed")
        return True

    except Exception as e:
        print(f"❌ Event intelligence metrics test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🧠 PulseAI Event Intelligence System Test Suite")
    print("=" * 60)

    tests = [
        ("Event Context Engine", test_event_context_engine),
        ("Event Forecast Engine", test_event_forecast_engine),
        ("Event Intelligence Service", test_event_intelligence_service),
        ("Event Generator (Draft)", test_event_generator),
        ("Event Context Generation", test_event_context_generation),
        ("Event Forecast Generation", test_event_forecast_generation),
        ("Event Intelligence Metrics", test_event_intelligence_metrics),
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
    print("📋 TEST SUMMARY")
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
        print("\n🎉 All tests passed!")
        print("\n💡 Next steps:")
        print("1. Integrate with Telegram digest handler")
        print("2. Update WebApp calendar with AI insights")
        print("3. Test API endpoints with AI context")
        print("4. Implement feedback collection system")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed!")
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

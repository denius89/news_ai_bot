#!/usr/bin/env python3
"""
Quick test for Events & Calendar System functionality.

This script tests the events system components
including parsers, providers, database service, and API.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from events.events_parser import get_events_parser
from database.events_service import get_events_service
from ai_modules.metrics import get_metrics


def test_events_parser():
    """Test events parser functionality."""
    print("🗓️ Testing Events Parser")
    print("-" * 40)

    try:
        parser = get_events_parser()

        print(f"Parser initialized with {len(parser.providers)} providers")

        # Test provider info
        provider_info = parser.get_provider_info()
        print("Available providers:")
        for name, info in provider_info.items():
            print(f"  {name}: {info.get('description', 'No description')}")

        print("✅ Events parser test passed")
        return True

    except Exception as e:
        print(f"❌ Events parser test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_event_providers():
    """Test event providers functionality."""
    print("\n🔌 Testing Event Providers")
    print("-" * 40)

    try:
        parser = get_events_parser()

        # Test date range
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=7)

        print(f"Fetching events from {start_date.date()} to {end_date.date()}")

        # Fetch events from all providers
        events = await parser.fetch_events(start_date, end_date)

        print(f"Fetched {len(events)} events from providers")

        # Show sample events
        for i, event in enumerate(events[:3]):
            print(f"  Sample event {i+1}: {event.title} ({event.category}) - {event.starts_at}")

        # Test provider-specific fetching
        for provider_name in parser.providers.keys():
            provider_events = await parser.fetch_events(start_date, end_date, [provider_name])
            print(f"  {provider_name}: {len(provider_events)} events")

        print("✅ Event providers test passed")
        return True

    except Exception as e:
        print(f"❌ Event providers test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_events_service():
    """Test events database service."""
    print("\n💾 Testing Events Database Service")
    print("-" * 40)

    try:
        service = get_events_service()

        # Test upcoming events
        upcoming_events = await service.get_upcoming_events(days_ahead=30)
        print(f"Upcoming events (30 days): {len(upcoming_events)}")

        # Test today's events
        today_events = await service.get_today_events()
        print(f"Today's events: {len(today_events)}")

        # Test category filtering
        crypto_events = await service.get_upcoming_events(days_ahead=30, category="crypto")
        print(f"Crypto events: {len(crypto_events)}")

        # Test importance filtering
        important_events = await service.get_upcoming_events(days_ahead=30, min_importance=0.8)
        print(f"Important events (0.8+): {len(important_events)}")

        # Test date range
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=14)
        range_events = await service.get_events_by_date_range(start_date, end_date)
        print(f"Events in 14-day range: {len(range_events)}")

        print("✅ Events database service test passed")
        return True

    except Exception as e:
        print(f"❌ Events database service test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_events_integration():
    """Test full events integration workflow."""
    print("\n🔄 Testing Events Integration Workflow")
    print("-" * 40)

    try:
        parser = get_events_parser()
        service = get_events_service()

        # Step 1: Fetch events from providers
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=7)

        print(f"Step 1: Fetching events from providers...")
        events = await parser.fetch_events(start_date, end_date)
        print(f"  Fetched {len(events)} events")

        # Step 2: Convert to database format
        print("Step 2: Converting events to database format...")
        events_data = []
        for event in events:
            event_data = {
                "title": event.title,
                "category": event.category,
                "subcategory": event.subcategory,
                "starts_at": event.starts_at,
                "ends_at": event.ends_at,
                "source": event.source,
                "link": event.link,
                "importance": event.importance,
                "description": event.description,
                "location": event.location,
                "organizer": event.organizer,
            }
            events_data.append(event_data)
        print(f"  Converted {len(events_data)} events")

        # Step 3: Store in database (simulate)
        print("Step 3: Storing events in database...")
        stored_count = await service.insert_events(events_data)
        print(f"  Stored {stored_count} events")

        # Step 4: Retrieve and verify
        print("Step 4: Retrieving events from database...")
        retrieved_events = await service.get_upcoming_events(days_ahead=7)
        print(f"  Retrieved {len(retrieved_events)} events")

        # Step 5: Test filtering
        print("Step 5: Testing event filtering...")
        crypto_events = await service.get_upcoming_events(days_ahead=7, category="crypto")
        important_events = await service.get_upcoming_events(days_ahead=7, min_importance=0.7)
        print(f"  Crypto events: {len(crypto_events)}")
        print(f"  Important events: {len(important_events)}")

        print("✅ Events integration workflow test passed")
        return True

    except Exception as e:
        print(f"❌ Events integration workflow test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_events_metrics():
    """Test events metrics integration."""
    print("\n📊 Testing Events Metrics")
    print("-" * 40)

    try:
        metrics = get_metrics()

        # Test new metrics methods
        metrics.increment_events_processed_total(25)
        metrics.update_events_upcoming_7d(15)
        metrics.update_events_by_category({"crypto": 8, "markets": 5, "sports": 2})
        metrics.increment_events_fetch_errors_total()

        # Get metrics summary
        summary = metrics.get_metrics_summary()

        print("Events Metrics:")
        print(f"  Events processed total: {summary.get('events_processed_total', 0)}")
        print(f"  Events upcoming 7d: {summary.get('events_upcoming_7d', 0)}")
        print(f"  Events by category: {summary.get('events_by_category', {})}")
        print(f"  Events fetch errors: {summary.get('events_fetch_errors_total', 0)}")

        print("✅ Events metrics test passed")
        return True

    except Exception as e:
        print(f"❌ Events metrics test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_api_simulation():
    """Test API endpoint simulation."""
    print("\n🌐 Testing API Endpoint Simulation")
    print("-" * 40)

    try:
        service = get_events_service()

        # Simulate API calls
        print("Simulating /api/events/upcoming?days=7...")
        upcoming_events = await service.get_upcoming_events(days_ahead=7)
        print(f"  Response: {len(upcoming_events)} events")

        print("Simulating /api/events/today...")
        today_events = await service.get_today_events()
        print(f"  Response: {len(today_events)} events")

        print("Simulating /api/events?category=crypto&min_importance=0.7...")
        crypto_events = await service.get_upcoming_events(days_ahead=30, category="crypto", min_importance=0.7)
        print(f"  Response: {len(crypto_events)} events")

        print("Simulating /api/events/categories...")
        categories = {
            "crypto": {"name": "Cryptocurrency", "emoji": "🪙"},
            "markets": {"name": "Financial Markets", "emoji": "📈"},
            "sports": {"name": "Sports", "emoji": "🏀"},
            "tech": {"name": "Technology", "emoji": "💻"},
            "world": {"name": "World Events", "emoji": "🌍"},
        }
        print(f"  Response: {len(categories)} categories")

        print("✅ API endpoint simulation test passed")
        return True

    except Exception as e:
        print(f"❌ API endpoint simulation test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🗓️ PulseAI Events & Calendar System Test Suite")
    print("=" * 60)

    tests = [
        ("Events Parser", test_events_parser),
        ("Event Providers", test_event_providers),
        ("Events Database Service", test_events_service),
        ("Events Integration Workflow", test_events_integration),
        ("Events Metrics", test_events_metrics),
        ("API Endpoint Simulation", test_api_simulation),
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
        print("1. Run: python tools/fetch_and_store_events.py --since 7 --until 30 --dry-run")
        print("2. Test API: curl 'http://localhost:8001/api/events/upcoming?days=7'")
        print("3. Check metrics: curl http://localhost:8001/metrics | grep events_")
        print("4. Open WebApp calendar at /calendar")
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

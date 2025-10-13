#!/usr/bin/env python3
"""
Load test events with correct future dates for Phase 1 testing.
"""

import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from database.db_models import supabase, safe_execute
from utils.system.dates import ensure_utc_iso


def load_test_events():
    """Load test events with future dates and new fields."""
    print("🔄 Loading test events with future dates...")

    # Generate future dates
    now = datetime.now(timezone.utc)
    future_dates = [
        now + timedelta(days=1),
        now + timedelta(days=2),
        now + timedelta(days=3),
        now + timedelta(days=7),
        now + timedelta(days=14),
    ]

    test_events = []

    # Football events
    for i, date in enumerate(future_dates):
        test_events.append(
            {
                "title": f"Premier League Match {i+1}",
                "category": "sports",
                "subcategory": "football",
                "event_time": ensure_utc_iso(date.replace(hour=15, minute=0)),
                "country": "UK",
                "currency": None,
                "importance": 1,
                "fact": "Premier League match with high importance",
                "forecast": None,
                "previous": None,
                "source": "football-data",
                "event_id": f"test-football-{i+1}-{date.strftime('%Y%m%d')}",
                "group_name": "Premier League",
                "metadata": {
                    "league": "Premier League",
                    "home_team": f"Team A{i+1}",
                    "away_team": f"Team B{i+1}",
                    "stadium": f"Stadium {i+1}",
                },
                "created_at": now.isoformat(),
            }
        )

    # Crypto events
    for i, date in enumerate(future_dates):
        test_events.append(
            {
                "title": f"Bitcoin Network Upgrade {i+1}",
                "category": "crypto",
                "subcategory": "bitcoin",
                "event_time": ensure_utc_iso(date.replace(hour=12, minute=0)),
                "country": None,
                "currency": "BTC",
                "importance": 1,
                "fact": "Bitcoin network upgrade with high impact",
                "forecast": None,
                "previous": None,
                "source": "coingecko",
                "event_id": f"test-crypto-{i+1}-{date.strftime('%Y%m%d')}",
                "group_name": "Bitcoin",
                "metadata": {
                    "coin": "BTC",
                    "event_type": "upgrade",
                    "impact": "high",
                    "network": "bitcoin",
                },
                "created_at": now.isoformat(),
            }
        )

    # Market events
    for i, date in enumerate(future_dates):
        test_events.append(
            {
                "title": f"Fed Meeting {i+1}",
                "category": "markets",
                "subcategory": "interest_rates",
                "event_time": ensure_utc_iso(date.replace(hour=14, minute=0)),
                "country": "US",
                "currency": "USD",
                "importance": 1,
                "fact": "Federal Reserve meeting with interest rate decision",
                "forecast": None,
                "previous": None,
                "source": "finnhub",
                "event_id": f"test-fed-{i+1}-{date.strftime('%Y%m%d')}",
                "group_name": "Federal Reserve",
                "metadata": {
                    "institution": "Federal Reserve",
                    "event_type": "meeting",
                    "impact": "high",
                    "currency": "USD",
                },
                "created_at": now.isoformat(),
            }
        )

    try:
        # Insert test events
        result = safe_execute(supabase.table("events").insert(test_events))

        if result.data:
            print(f"✅ Successfully loaded {len(result.data)} test events")
            event_times = [event["event_time"] for event in test_events[:3]]
            print(f"📅 Events scheduled for dates: {event_times}...")
            return True
        else:
            print(f"❌ Failed to load test events: {result}")
            return False

    except Exception as e:
        print(f"❌ Error loading test events: {e}")
        return False


if __name__ == "__main__":
    success = load_test_events()
    sys.exit(0 if success else 1)

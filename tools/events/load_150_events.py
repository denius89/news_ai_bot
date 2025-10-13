#!/usr/bin/env python3
"""
Load 200 additional events into the database for comprehensive testing.

This script creates diverse events across all categories with realistic dates,
importance levels, and metadata for testing the calendar and events system.
"""

import sys
import os
import asyncio
import random
import time
from datetime import datetime, timedelta

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)

from database.db_models import supabase


def generate_sample_events():
    """Generate sample events with proper formatting."""
    events = []

    # Crypto Events (40 events)
    for _ in range(8):
        events.append(
            {
                "title": f"Bitcoin Mining Difficulty Adjustment #{random.randint(820000, 830000)}",
                "category": "crypto",
                "subcategory": "bitcoin",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(1, 90))
                ).isoformat(),
                "country": "Global",
                "source": "coingecko",
                "event_id": f"btc-diff-{random.randint(820000, 830000)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {
                    "type": "difficulty_adjustment",
                    "coin": "bitcoin",
                },
            }
        )

    for _ in range(10):
        upgrade = random.choice(["Berlin", "London", "Shanghai", "Cancun"])
        events.append(
            {
                "title": f"Ethereum Network Upgrade - {upgrade} v2.{random.randint(1, 5)}",
                "category": "crypto",
                "subcategory": "ethereum",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(5, 120))
                ).isoformat(),
                "source": "defillama",
                "event_id": f"eth-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {"type": "network_upgrade", "coin": "ethereum"},
            }
        )

    for _ in range(12):
        coin = random.choice(
            ["Solana", "Cardano", "Polkadot", "Avalanche", "Polygon"]
        )
        events.append(
            {
                "title": f"{coin} Token Unlock Event",
                "category": "crypto",
                "subcategory": "altcoins",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(1, 180))
                ).isoformat(),
                "source": "tokenunlocks",
                "event_id": f"unlock-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {
                    "type": "token_unlock",
                    "amount": random.randint(1000000, 50000000),
                },
            }
        )

    for _ in range(10):
        exchange = random.choice(["Binance", "Coinbase", "Kraken", "FTX"])
        events.append(
            {
                "title": f"{exchange} Quarterly Earnings Report",
                "category": "crypto",
                "subcategory": "exchanges",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(10, 120))
                ).isoformat(),
                "source": "fmp",
                "event_id": f"earn-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {
                    "type": "earnings",
                    "quarter": f"Q{random.randint(1, 4)}",
                },
            }
        )

    # Sports Events (35 events)
    for _ in range(15):
        league = random.choice(
            ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"]
        )
        events.append(
            {
                "title": f"{league} Matchday {random.randint(1, 38)}",
                "category": "sports",
                "subcategory": "football",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(1, 200))
                ).isoformat(),
                "source": "football_data",
                "event_id": f"football-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {
                    "type": "football_match",
                    "league": "premier_league",
                },
            }
        )

    for _ in range(10):
        game_type = random.choice(["Regular Season", "Playoffs", "Finals"])
        events.append(
            {
                "title": f"NBA {game_type} Game",
                "category": "sports",
                "subcategory": "basketball",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(1, 180))
                ).isoformat(),
                "source": "thesportsdb",
                "event_id": f"nba-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {"type": "basketball_game", "league": "NBA"},
            }
        )

    for _ in range(10):
        tournament = random.choice(
            ["Australian Open", "French Open", "Wimbledon", "US Open"]
        )
        events.append(
            {
                "title": f"{tournament} Tennis Championship",
                "category": "sports",
                "subcategory": "tennis",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(10, 300))
                ).isoformat(),
                "source": "thesportsdb",
                "event_id": f"tennis-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {"type": "tennis_tournament", "surface": "hard"},
            }
        )

    # Tech Events (30 events)
    for _ in range(10):
        company = random.choice(
            ["Apple", "Google", "Microsoft", "Amazon", "Meta"]
        )
        events.append(
            {
                "title": f"{company} Product Launch Event",
                "category": "tech",
                "subcategory": "product_launches",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(5, 180))
                ).isoformat(),
                "source": "github",
                "event_id": f"launch-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {
                    "type": "product_launch",
                    "company": company.lower(),
                },
            }
        )

    for _ in range(10):
        conf = random.choice(
            ["WWDC", "Google I/O", "Microsoft Build", "AWS re:Invent"]
        )
        events.append(
            {
                "title": f"{conf} Developer Conference",
                "category": "tech",
                "subcategory": "conferences",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(30, 300))
                ).isoformat(),
                "source": "github",
                "event_id": f"conf-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {
                    "type": "conference",
                    "attendees": random.randint(5000, 50000),
                },
            }
        )

    for _ in range(10):
        tech = random.choice(["AI", "Blockchain", "Cloud", "IoT", "5G"])
        events.append(
            {
                "title": f"{tech} Technology Summit",
                "category": "tech",
                "subcategory": "summits",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(20, 250))
                ).isoformat(),
                "source": "github",
                "event_id": f"summit-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {"type": "summit", "technology": tech.lower()},
            }
        )

    # Market Events (95 events)
    for _ in range(30):
        company = random.choice(
            ["Apple", "Tesla", "Amazon", "Microsoft", "Google"]
        )
        events.append(
            {
                "title": f"{company} Quarterly Earnings Report",
                "category": "markets",
                "subcategory": "earnings",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(5, 120))
                ).isoformat(),
                "source": "finnhub",
                "event_id": f"earn-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {
                    "type": "earnings",
                    "quarter": f"Q{random.randint(1, 4)}",
                },
            }
        )

    for _ in range(25):
        bank = random.choice(
            ["Federal Reserve", "ECB", "Bank of England", "Bank of Japan"]
        )
        events.append(
            {
                "title": f"{bank} Interest Rate Decision",
                "category": "markets",
                "subcategory": "interest_rates",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(10, 180))
                ).isoformat(),
                "source": "finnhub",
                "event_id": f"rate-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {"type": "interest_rate", "bank": bank.lower()},
            }
        )

    for _ in range(20):
        indicator = random.choice(
            ["GDP", "CPI", "Unemployment", "Retail Sales"]
        )
        events.append(
            {
                "title": f"US {indicator} Data Release",
                "category": "markets",
                "subcategory": "economic_indicators",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(3, 90))
                ).isoformat(),
                "source": "finnhub",
                "event_id": f"data-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {
                    "type": "economic_data",
                    "indicator": indicator.lower(),
                },
            }
        )

    for _ in range(20):
        company = random.choice(["Nvidia", "AMD", "Intel", "Qualcomm", "TSMC"])
        events.append(
            {
                "title": f"{company} Investor Day Presentation",
                "category": "markets",
                "subcategory": "investor_relations",
                "event_time": (
                    datetime.now() + timedelta(days=random.randint(15, 200))
                ).isoformat(),
                "source": "finnhub",
                "event_id": f"inv-{random.randint(100000, 999999)}-{int(time.time() * 1000000)}",
                "importance": 1,
                "metadata": {
                    "type": "investor_day",
                    "company": company.lower(),
                },
            }
        )

    return events


async def load_events():
    """Load events into the database."""
    print("🔄 Generating 200 test events...")

    events = generate_sample_events()

    print(f"✅ Generated {len(events)} events")
    print("📤 Inserting events into database...")

    try:
        result = supabase.table("events").insert(events).execute()

        if result.data:
            print(f"✅ Successfully loaded {len(result.data)} events")
            return True
        else:
            print(f"❌ Failed to load events: {result}")
            return False

    except Exception as e:
        print(f"❌ Error loading events: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(load_events())
    sys.exit(0 if success else 1)

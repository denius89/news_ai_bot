#!/usr/bin/env python3
"""
Load 150 additional events into the database for comprehensive testing.

This script creates diverse events across all categories with realistic dates,
importance levels, and metadata for testing the calendar and events system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
from datetime import datetime, timedelta
import random
from database.db_models import supabase

# Sample events data with diverse categories and realistic dates
SAMPLE_EVENTS = [
    # Crypto Events (40 events)
    *[
        {
            "title": f"Bitcoin Mining Difficulty Adjustment #{random.randint(820000, 830000)}",
            "description": "Automatic adjustment of Bitcoin mining difficulty based on network hash rate",
            "category": "crypto",
            "subcategory": "bitcoin",
            "starts_at": (datetime.now() + timedelta(days=random.randint(1, 90))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(1, 90), hours=1)).isoformat(),
            "location": "Global",
            "source": "coingecko",
            "link": "https://bitcoin.org",
            "importance": round(random.uniform(0.6, 0.9), 2),
            "unique_hash": f"btc-difficulty-{random.randint(820000, 830000)}",
            "metadata": {"type": "difficulty_adjustment", "coin": "bitcoin"}
        } for _ in range(8)
    ],
    *[
        {
            "title": f"Ethereum Network Upgrade - {random.choice(['Berlin', 'London', 'Shanghai', 'Cancun'])} v2.{random.randint(1, 5)}",
            "description": f"Major Ethereum network upgrade improving {random.choice(['scalability', 'security', 'efficiency', 'gas optimization'])}",
            "category": "crypto",
            "subcategory": "ethereum",
            "starts_at": (datetime.now() + timedelta(days=random.randint(5, 120))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(5, 120), hours=2)).isoformat(),
            "location": "Global",
            "source": "defillama",
            "link": "https://ethereum.org",
            "importance": round(random.uniform(0.7, 0.95), 2),
            "unique_hash": f"eth-upgrade-{random.randint(100, 999)}",
            "metadata": {"type": "network_upgrade", "coin": "ethereum"}
        } for _ in range(10)
    ],
    *[
        {
            "title": f"{random.choice(['Solana', 'Cardano', 'Polkadot', 'Avalanche', 'Polygon'])} Token Unlock Event",
            "description": f"Release of {random.randint(1000000, 50000000):,} tokens from vesting schedule",
            "category": "crypto",
            "subcategory": "altcoins",
            "starts_at": (datetime.now() + timedelta(days=random.randint(1, 180))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(1, 180), hours=1)).isoformat(),
            "location": "Global",
            "source": "tokenunlocks",
            "link": "",
            "importance": round(random.uniform(0.5, 0.8), 2),
            "unique_hash": f"token-unlock-{random.randint(1000, 9999)}",
            "metadata": {"type": "token_unlock", "amount": random.randint(1000000, 50000000)}
        } for _ in range(12)
    ],
    *[
        {
            "title": f"{random.choice(['Binance', 'Coinbase', 'Kraken', 'FTX'])} Quarterly Earnings Report",
            "description": f"Q{random.randint(1, 4)} {datetime.now().year} financial results and trading volume metrics",
            "category": "crypto",
            "subcategory": "exchanges",
            "starts_at": (datetime.now() + timedelta(days=random.randint(10, 120))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(10, 120), hours=2)).isoformat(),
            "location": "Global",
            "source": "fmp",
            "link": "",
            "importance": round(random.uniform(0.6, 0.85), 2),
            "unique_hash": f"exchange-earnings-{random.randint(100, 999)}",
            "metadata": {"type": "earnings", "quarter": f"Q{random.randint(1, 4)}"}
        } for _ in range(10)
    ],

    # Sports Events (35 events)
    *[
        {
            "title": f"{random.choice(['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1'])} Matchday {random.randint(1, 38)}",
            "description": f"Football matches featuring {random.choice(['Manchester City', 'Real Madrid', 'Bayern Munich', 'Juventus', 'PSG'])} vs {random.choice(['Arsenal', 'Barcelona', 'Borussia Dortmund', 'AC Milan', 'Marseille'])}",
            "category": "sports",
            "subcategory": "football",
            "starts_at": (datetime.now() + timedelta(days=random.randint(1, 200))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(1, 200), hours=2)).isoformat(),
            "location": random.choice(["London", "Madrid", "Munich", "Milan", "Paris"]),
            "source": "football_data",
            "link": "",
            "importance": round(random.uniform(0.4, 0.8), 2),
            "unique_hash": f"football-match-{random.randint(10000, 99999)}",
            "metadata": {"type": "football_match", "league": "premier_league"}
        } for _ in range(15)
    ],
    *[
        {
            "title": f"NBA {random.choice(['Regular Season', 'Playoffs', 'Finals'])} Game {random.randint(1, 82)}",
            "description": f"{random.choice(['Lakers', 'Warriors', 'Celtics', 'Heat', 'Bucks'])} vs {random.choice(['Nets', '76ers', 'Suns', 'Clippers', 'Nuggets'])}",
            "category": "sports",
            "subcategory": "basketball",
            "starts_at": (datetime.now() + timedelta(days=random.randint(1, 180))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(1, 180), hours=3)).isoformat(),
            "location": random.choice(["Los Angeles", "San Francisco", "Boston", "Miami", "Milwaukee"]),
            "source": "thesportsdb",
            "link": "",
            "importance": round(random.uniform(0.3, 0.7), 2),
            "unique_hash": f"nba-game-{random.randint(10000, 99999)}",
            "metadata": {"type": "basketball_game", "league": "nba"}
        } for _ in range(12)
    ],
    *[
        {
            "title": f"{random.choice(['Wimbledon', 'US Open', 'French Open', 'Australian Open'])} {random.choice(['Quarterfinals', 'Semifinals', 'Finals'])}",
            "description": f"Tennis championship featuring top seeded players",
            "category": "sports",
            "subcategory": "tennis",
            "starts_at": (datetime.now() + timedelta(days=random.randint(5, 300))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(5, 300), hours=4)).isoformat(),
            "location": random.choice(["London", "New York", "Paris", "Melbourne"]),
            "source": "pandascore",
            "link": "",
            "importance": round(random.uniform(0.5, 0.8), 2),
            "unique_hash": f"tennis-{random.randint(1000, 9999)}",
            "metadata": {"type": "tennis_match", "tournament": "grand_slam"}
        } for _ in range(8)
    ],

    # Tech Events (30 events)
    *[
        {
            "title": f"{random.choice(['Apple', 'Google', 'Microsoft', 'Amazon', 'Meta'])} {random.choice(['Developer Conference', 'Product Launch', 'Earnings Call'])}",
            "description": f"Major tech event featuring new {random.choice(['products', 'services', 'platforms', 'APIs'])} announcements",
            "category": "tech",
            "subcategory": "conferences",
            "starts_at": (datetime.now() + timedelta(days=random.randint(10, 200))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(10, 200), hours=3)).isoformat(),
            "location": random.choice(["Cupertino", "Mountain View", "Redmond", "Seattle", "Menlo Park"]),
            "source": "github_releases",
            "link": "",
            "importance": round(random.uniform(0.6, 0.9), 2),
            "unique_hash": f"tech-event-{random.randint(1000, 9999)}",
            "metadata": {"type": "tech_conference", "company": "apple"}
        } for _ in range(15)
    ],
    *[
        {
            "title": f"Open Source {random.choice(['Linux', 'Apache', 'Mozilla', 'Eclipse'])} Release v{random.randint(1, 10)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "description": f"New version release with {random.choice(['security updates', 'performance improvements', 'new features', 'bug fixes'])}",
            "category": "tech",
            "subcategory": "releases",
            "starts_at": (datetime.now() + timedelta(days=random.randint(5, 120))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(5, 120), hours=1)).isoformat(),
            "location": "Global",
            "source": "github_releases",
            "link": "",
            "importance": round(random.uniform(0.4, 0.7), 2),
            "unique_hash": f"oss-release-{random.randint(1000, 9999)}",
            "metadata": {"type": "software_release", "category": "open_source"}
        } for _ in range(15)
    ],

    # Markets Events (25 events)
    *[
        {
            "title": f"Federal Reserve {random.choice(['FOMC Meeting', 'Interest Rate Decision', 'Economic Outlook'])}",
            "description": f"Federal Reserve monetary policy decision affecting {random.choice(['interest rates', 'inflation targets', 'economic growth'])}",
            "category": "markets",
            "subcategory": "central_banks",
            "starts_at": (datetime.now() + timedelta(days=random.randint(15, 150))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(15, 150), hours=2)).isoformat(),
            "location": "Washington, D.C.",
            "source": "finnhub",
            "link": "",
            "importance": round(random.uniform(0.8, 0.95), 2),
            "unique_hash": f"fed-meeting-{random.randint(100, 999)}",
            "metadata": {"type": "central_bank", "institution": "federal_reserve"}
        } for _ in range(8)
    ],
    *[
        {
            "title": f"{random.choice(['European Central Bank', 'Bank of England', 'Bank of Japan'])} Policy Decision",
            "description": f"Monetary policy announcement affecting {random.choice(['EUR', 'GBP', 'JPY'])} currency markets",
            "category": "markets",
            "subcategory": "central_banks",
            "starts_at": (datetime.now() + timedelta(days=random.randint(10, 180))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(10, 180), hours=1)).isoformat(),
            "location": random.choice(["Frankfurt", "London", "Tokyo"]),
            "source": "finnhub",
            "link": "",
            "importance": round(random.uniform(0.7, 0.9), 2),
            "unique_hash": f"cb-policy-{random.randint(100, 999)}",
            "metadata": {"type": "central_bank", "currency": "eur"}
        } for _ in range(10)
    ],
    *[
        {
            "title": f"{random.choice(['Tesla', 'Apple', 'Microsoft', 'Amazon', 'Google'])} Earnings Call Q{random.randint(1, 4)}",
            "description": f"Quarterly earnings report and guidance for {random.choice(['revenue', 'profit margins', 'user growth', 'market expansion'])}",
            "category": "markets",
            "subcategory": "earnings",
            "starts_at": (datetime.now() + timedelta(days=random.randint(5, 120))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(5, 120), hours=2)).isoformat(),
            "location": "Global",
            "source": "fmp",
            "link": "",
            "importance": round(random.uniform(0.6, 0.85), 2),
            "unique_hash": f"earnings-{random.randint(1000, 9999)}",
            "metadata": {"type": "earnings", "quarter": f"Q{random.randint(1, 4)}"}
        } for _ in range(7)
    ],

    # World Events (20 events)
    *[
        {
            "title": f"{random.choice(['UN Security Council', 'G7 Summit', 'G20 Summit', 'World Economic Forum'])} Meeting",
            "description": f"International summit addressing {random.choice(['climate change', 'economic cooperation', 'security issues', 'trade policies'])}",
            "category": "world",
            "subcategory": "politics",
            "starts_at": (datetime.now() + timedelta(days=random.randint(20, 300))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(20, 300), hours=6)).isoformat(),
            "location": random.choice(["New York", "Geneva", "Davos", "Rome", "Tokyo"]),
            "source": "un_sc",
            "link": "",
            "importance": round(random.uniform(0.7, 0.9), 2),
            "unique_hash": f"world-summit-{random.randint(100, 999)}",
            "metadata": {"type": "international_summit", "organization": "un"}
        } for _ in range(12)
    ],
    *[
        {
            "title": f"{random.choice(['COP', 'Climate Summit', 'Environmental Conference'])} {random.randint(28, 35)}",
            "description": f"Global climate change conference focusing on {random.choice(['carbon reduction', 'renewable energy', 'sustainability goals', 'green finance'])}",
            "category": "world",
            "subcategory": "environment",
            "starts_at": (datetime.now() + timedelta(days=random.randint(30, 400))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(30, 400), hours=8)).isoformat(),
            "location": random.choice(["Dubai", "Glasgow", "Madrid", "Katowice", "Bonn"]),
            "source": "oecd",
            "link": "",
            "importance": round(random.uniform(0.6, 0.85), 2),
            "unique_hash": f"climate-{random.randint(1000, 9999)}",
            "metadata": {"type": "climate_conference", "cop_number": random.randint(28, 35)}
        } for _ in range(8)
    ]
]

async def load_events():
    """Load 150 sample events into the database."""
    try:
        print(f"🔄 Loading {len(SAMPLE_EVENTS)} events into database...")
        
        # Insert events in batches
        batch_size = 50
        total_inserted = 0
        
        for i in range(0, len(SAMPLE_EVENTS), batch_size):
            batch = SAMPLE_EVENTS[i:i + batch_size]
            
            result = supabase.table("events_new").insert(batch).execute()
            
            if result.data:
                batch_count = len(result.data)
                total_inserted += batch_count
                print(f"✅ Inserted batch {i//batch_size + 1}: {batch_count} events")
            else:
                print(f"❌ Failed to insert batch {i//batch_size + 1}")
        
        print(f"🎉 Successfully loaded {total_inserted} events!")
        
        # Verify total count
        count_result = supabase.table("events_new").select("*", count="exact").execute()
        total_events = count_result.count
        print(f"📊 Total events in database: {total_events}")
        
        return total_inserted
        
    except Exception as e:
        print(f"❌ Error loading events: {e}")
        return 0

if __name__ == "__main__":
    asyncio.run(load_events())

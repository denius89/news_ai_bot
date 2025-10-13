#!/usr/bin/env python3
"""
Load 100 additional events into the database for comprehensive calendar testing.

This script creates diverse events with more varied dates, subcategories, and
realistic scenarios for testing the full calendar functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
from datetime import datetime, timedelta
import random
from database.db_models import supabase

# Additional 100 events with more diverse dates and scenarios
ADDITIONAL_EVENTS = [
    # More Crypto Events (30 events)
    *[
        {
            "title": f"{random.choice(['DeFi Protocol', 'NFT Marketplace', 'GameFi Platform'])} {random.choice(['Launch', 'Mainnet', 'Token Sale'])}",
            "description": f"New {random.choice(['DeFi', 'NFT', 'GameFi'])} platform launch with {random.choice(['yield farming', 'NFT trading', 'play-to-earn'])} features",
            "category": "crypto",
            "subcategory": "defi",
            "starts_at": (datetime.now() + timedelta(days=random.randint(1, 90))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(1, 90), hours=random.randint(1, 4))).isoformat(),
            "location": "Global",
            "source": "coingecko",
            "link": "",
            "importance": round(random.uniform(0.4, 0.8), 2),
            "unique_hash": f"defi-launch-{random.randint(10000, 99999)}",
            "metadata": {"type": "protocol_launch", "category": "defi"}
        } for _ in range(10)
    ],
    *[
        {
            "title": f"{random.choice(['Layer 2', 'Sidechain', 'Cross-chain Bridge'])} Network Upgrade",
            "description": f"Major infrastructure upgrade improving {random.choice(['transaction speed', 'cost efficiency', 'security', 'scalability'])}",
            "category": "crypto",
            "subcategory": "infrastructure",
            "starts_at": (datetime.now() + timedelta(days=random.randint(5, 120))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(5, 120), hours=2)).isoformat(),
            "location": "Global",
            "source": "defillama",
            "link": "",
            "importance": round(random.uniform(0.5, 0.85), 2),
            "unique_hash": f"infra-upgrade-{random.randint(10000, 99999)}",
            "metadata": {"type": "infrastructure_upgrade", "layer": "l2"}
        } for _ in range(8)
    ],
    *[
        {
            "title": f"Central Bank Digital Currency (CBDC) {random.choice(['Pilot', 'Test', 'Launch'])}",
            "description": f"Digital currency initiative by {random.choice(['China', 'EU', 'UK', 'Japan', 'Brazil'])} central bank",
            "category": "crypto",
            "subcategory": "cbdc",
            "starts_at": (datetime.now() + timedelta(days=random.randint(30, 200))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(30, 200), hours=1)).isoformat(),
            "location": random.choice(["Beijing", "Brussels", "London", "Tokyo", "Brasilia"]),
            "source": "finnhub",
            "link": "",
            "importance": round(random.uniform(0.7, 0.95), 2),
            "unique_hash": f"cbdc-{random.randint(1000, 9999)}",
            "metadata": {"type": "cbdc", "country": "china"}
        } for _ in range(6)
    ],
    *[
        {
            "title": f"Regulatory {random.choice(['Guidelines', 'Framework', 'Compliance Rules'])} for {random.choice(['Crypto Exchanges', 'DeFi Protocols', 'NFT Platforms'])}",
            "description": f"New regulatory framework affecting {random.choice(['trading', 'lending', 'staking', 'mining'])} operations",
            "category": "crypto",
            "subcategory": "regulation",
            "starts_at": (datetime.now() + timedelta(days=random.randint(15, 150))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(15, 150), hours=1)).isoformat(),
            "location": random.choice(["Washington", "Brussels", "London", "Tokyo", "Singapore"]),
            "source": "fmp",
            "link": "",
            "importance": round(random.uniform(0.6, 0.9), 2),
            "unique_hash": f"crypto-reg-{random.randint(1000, 9999)}",
            "metadata": {"type": "regulation", "jurisdiction": "us"}
        } for _ in range(6)
    ],

    # More Sports Events (25 events)
    *[
        {
            "title": f"{random.choice(['Champions League', 'Europa League', 'Conference League'])} {random.choice(['Group Stage', 'Knockout', 'Final'])}",
            "description": f"European football competition featuring {random.choice(['Real Madrid', 'Manchester City', 'Bayern Munich', 'PSG'])}",
            "category": "sports",
            "subcategory": "football",
            "starts_at": (datetime.now() + timedelta(days=random.randint(1, 250))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(1, 250), hours=2)).isoformat(),
            "location": random.choice(["Madrid", "Manchester", "Munich", "Paris", "London"]),
            "source": "football_data",
            "link": "",
            "importance": round(random.uniform(0.6, 0.9), 2),
            "unique_hash": f"uefa-{random.randint(10000, 99999)}",
            "metadata": {"type": "football_tournament", "competition": "uefa"}
        } for _ in range(10)
    ],
    *[
        {
            "title": f"Olympic {random.choice(['Summer', 'Winter'])} Games {random.choice(['2026', '2028', '2030'])} - {random.choice(['Opening Ceremony', 'Closing Ceremony', 'Medal Ceremony'])}",
            "description": f"Olympic Games ceremony in {random.choice(['Milan-Cortina', 'Los Angeles', 'Salt Lake City'])}",
            "category": "sports",
            "subcategory": "olympics",
            "starts_at": (datetime.now() + timedelta(days=random.randint(100, 800))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(100, 800), hours=3)).isoformat(),
            "location": random.choice(["Milan", "Los Angeles", "Salt Lake City"]),
            "source": "thesportsdb",
            "link": "",
            "importance": round(random.uniform(0.8, 0.95), 2),
            "unique_hash": f"olympics-{random.randint(1000, 9999)}",
            "metadata": {"type": "olympic_games", "year": "2026"}
        } for _ in range(8)
    ],
    *[
        {
            "title": f"Formula 1 {random.choice(['Grand Prix', 'Qualifying', 'Race'])} - {random.choice(['Monaco', 'Silverstone', 'Spa', 'Monza'])}",
            "description": f"F1 race weekend at {random.choice(['Monaco', 'Silverstone', 'Spa-Francorchamps', 'Monza'])} circuit",
            "category": "sports",
            "subcategory": "racing",
            "starts_at": (datetime.now() + timedelta(days=random.randint(1, 200))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(1, 200), hours=3)).isoformat(),
            "location": random.choice(["Monaco", "Silverstone", "Spa", "Monza"]),
            "source": "pandascore",
            "link": "",
            "importance": round(random.uniform(0.5, 0.8), 2),
            "unique_hash": f"f1-{random.randint(10000, 99999)}",
            "metadata": {"type": "f1_race", "circuit": "monaco"}
        } for _ in range(7)
    ],

    # More Tech Events (20 events)
    *[
        {
            "title": f"{random.choice(['AI', 'Machine Learning', 'Quantum Computing'])} Conference {random.choice(['2025', '2026'])}",
            "description": f"Leading conference on {random.choice(['artificial intelligence', 'machine learning', 'quantum computing'])} technologies",
            "category": "tech",
            "subcategory": "ai",
            "starts_at": (datetime.now() + timedelta(days=random.randint(30, 300))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(30, 300), hours=8)).isoformat(),
            "location": random.choice(["San Francisco", "New York", "London", "Berlin", "Tokyo"]),
            "source": "github_releases",
            "link": "",
            "importance": round(random.uniform(0.6, 0.85), 2),
            "unique_hash": f"ai-conf-{random.randint(1000, 9999)}",
            "metadata": {"type": "tech_conference", "focus": "ai"}
        } for _ in range(8)
    ],
    *[
        {
            "title": f"{random.choice(['Cybersecurity', 'Cloud Computing', 'Edge Computing'])} Summit",
            "description": f"Industry summit on {random.choice(['cybersecurity', 'cloud infrastructure', 'edge computing'])} trends and solutions",
            "category": "tech",
            "subcategory": "security",
            "starts_at": (datetime.now() + timedelta(days=random.randint(20, 180))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(20, 180), hours=6)).isoformat(),
            "location": random.choice(["Las Vegas", "Barcelona", "Amsterdam", "Singapore"]),
            "source": "github_releases",
            "link": "",
            "importance": round(random.uniform(0.5, 0.8), 2),
            "unique_hash": f"tech-summit-{random.randint(1000, 9999)}",
            "metadata": {"type": "tech_summit", "domain": "security"}
        } for _ in range(6)
    ],
    *[
        {
            "title": f"{random.choice(['SpaceX', 'Blue Origin', 'Virgin Galactic'])} {random.choice(['Launch', 'Mission', 'Test Flight'])}",
            "description": f"Space mission featuring {random.choice(['satellite deployment', 'crew transport', 'cargo delivery'])}",
            "category": "tech",
            "subcategory": "space",
            "starts_at": (datetime.now() + timedelta(days=random.randint(10, 200))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(10, 200), hours=2)).isoformat(),
            "location": random.choice(["Cape Canaveral", "Boca Chica", "Cornwall"]),
            "source": "github_releases",
            "link": "",
            "importance": round(random.uniform(0.6, 0.9), 2),
            "unique_hash": f"space-{random.randint(1000, 9999)}",
            "metadata": {"type": "space_mission", "company": "spacex"}
        } for _ in range(6)
    ],

    # More Markets Events (15 events)
    *[
        {
            "title": f"{random.choice(['Gold', 'Silver', 'Oil', 'Gas'])} Price {random.choice(['Forecast', 'Analysis', 'Outlook'])} Update",
            "description": f"Commodity market analysis and price predictions for {random.choice(['precious metals', 'energy', 'agriculture'])}",
            "category": "markets",
            "subcategory": "commodities",
            "starts_at": (datetime.now() + timedelta(days=random.randint(1, 90))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(1, 90), hours=1)).isoformat(),
            "location": "Global",
            "source": "finnhub",
            "link": "",
            "importance": round(random.uniform(0.4, 0.7), 2),
            "unique_hash": f"commodity-{random.randint(1000, 9999)}",
            "metadata": {"type": "commodity_analysis", "asset": "gold"}
        } for _ in range(8)
    ],
    *[
        {
            "title": f"Bond Market {random.choice(['Auction', 'Settlement', 'Maturity'])} - {random.choice(['US Treasury', 'Corporate', 'Municipal'])}",
            "description": f"Fixed income market event affecting {random.choice(['yield curves', 'interest rates', 'credit spreads'])}",
            "category": "markets",
            "subcategory": "bonds",
            "starts_at": (datetime.now() + timedelta(days=random.randint(5, 120))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(5, 120), hours=1)).isoformat(),
            "location": "Global",
            "source": "fmp",
            "link": "",
            "importance": round(random.uniform(0.5, 0.8), 2),
            "unique_hash": f"bond-{random.randint(1000, 9999)}",
            "metadata": {"type": "bond_event", "category": "treasury"}
        } for _ in range(7)
    ],

    # More World Events (10 events)
    *[
        {
            "title": f"{random.choice(['Climate Change', 'Sustainable Development', 'Green Finance'])} Initiative Launch",
            "description": f"Global initiative addressing {random.choice(['carbon neutrality', 'renewable energy', 'sustainable finance'])} goals",
            "category": "world",
            "subcategory": "environment",
            "starts_at": (datetime.now() + timedelta(days=random.randint(30, 250))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(30, 250), hours=4)).isoformat(),
            "location": random.choice(["New York", "Geneva", "Nairobi", "Bonn"]),
            "source": "oecd",
            "link": "",
            "importance": round(random.uniform(0.6, 0.85), 2),
            "unique_hash": f"climate-init-{random.randint(1000, 9999)}",
            "metadata": {"type": "climate_initiative", "focus": "sustainability"}
        } for _ in range(5)
    ],
    *[
        {
            "title": f"Global {random.choice(['Trade', 'Health', 'Education'])} Summit",
            "description": f"International summit on {random.choice(['trade agreements', 'public health', 'education policies'])} cooperation",
            "category": "world",
            "subcategory": "politics",
            "starts_at": (datetime.now() + timedelta(days=random.randint(50, 300))).isoformat(),
            "ends_at": (datetime.now() + timedelta(days=random.randint(50, 300), hours=6)).isoformat(),
            "location": random.choice(["Geneva", "Vienna", "Brussels", "Tokyo"]),
            "source": "un_sc",
            "link": "",
            "importance": round(random.uniform(0.5, 0.8), 2),
            "unique_hash": f"global-summit-{random.randint(1000, 9999)}",
            "metadata": {"type": "international_summit", "topic": "trade"}
        } for _ in range(5)
    ]
]

async def load_additional_events():  # noqa: E302
    """Load 100 additional sample events into the database."""
    try:
        print(f"🔄 Loading {len(ADDITIONAL_EVENTS)} additional events into database...")

        # Insert events in batches
        batch_size = 50
        total_inserted = 0

        for i in range(0, len(ADDITIONAL_EVENTS), batch_size):
            batch = ADDITIONAL_EVENTS[i:i + batch_size]

            result = supabase.table("events_new").insert(batch).execute()

            if result.data:
                batch_count = len(result.data)
                total_inserted += batch_count
                print(f"✅ Inserted batch {i//batch_size + 1}: {batch_count} events")
            else:
                print(f"❌ Failed to insert batch {i//batch_size + 1}")

        print(f"🎉 Successfully loaded {total_inserted} additional events!")

        # Verify total count
        count_result = supabase.table("events_new").select("*", count="exact").execute()
        total_events = count_result.count
        print(f"📊 Total events in database: {total_events}")

        return total_inserted

    except Exception as e:
        print(f"❌ Error loading additional events: {e}")
        return 0

if __name__ == "__main__":
    asyncio.run(load_additional_events())

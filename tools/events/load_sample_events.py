#!/usr/bin/env python3
"""
Скрипт для загрузки примеров событий в базу данных PulseAI.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from dotenv import load_dotenv
load_dotenv()

from database.events_service import get_events_service
from datetime import datetime, timezone, timedelta
import asyncio
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def load_sample_events():  # noqa: E302
    """Загрузить примеры событий в базу данных."""

    # Получить сервис событий
    events_service = get_events_service()

    # 25 разнообразных событий
    sample_events = [
        # Crypto Events
        {
            "title": "Bitcoin Halving Event",
            "description": "Bitcoin network halving event - reduction of mining rewards",
            "category": "crypto",
            "subcategory": "bitcoin",
            "starts_at": datetime.now() + timedelta(days=30),
            "ends_at": datetime.now() + timedelta(days=30, hours=1),
            "location": "Global",
            "source": "manual",
            "link": "",
            "importance": 0.9,
            "unique_hash": "bitcoin-halving-2025",
            "metadata": {"type": "halving", "coin": "bitcoin"}
        },
        {
            "title": "Ethereum 2.0 Upgrade",
            "description": "Major Ethereum network upgrade with new features",
            "category": "crypto",
            "subcategory": "ethereum",
            "starts_at": datetime.now() + timedelta(days=45),
            "ends_at": datetime.now() + timedelta(days=45, hours=2),
            "location": "Global",
            "source": "manual",
            "link": "",
            "importance": 0.85,
            "unique_hash": "ethereum-upgrade-2025",
            "metadata": {"type": "upgrade", "coin": "ethereum"}
        },
        {
            "title": "Solana Network Upgrade",
            "description": "Solana blockchain performance and security improvements",
            "category": "crypto",
            "subcategory": "solana",
            "starts_at": datetime.now() + timedelta(days=15),
            "ends_at": datetime.now() + timedelta(days=15, hours=3),
            "location": "Global",
            "source": "manual",
            "link": "",
            "importance": 0.7,
            "unique_hash": "solana-upgrade-2025",
            "metadata": {"type": "upgrade", "coin": "solana"}
        },
        {
            "title": "Chainlink Oracle Update",
            "description": "Chainlink oracle network expansion and new data feeds",
            "category": "crypto",
            "subcategory": "chainlink",
            "starts_at": datetime.now() + timedelta(days=20),
            "ends_at": datetime.now() + timedelta(days=20, hours=1),
            "location": "Global",
            "source": "manual",
            "link": "",
            "importance": 0.6,
            "unique_hash": "chainlink-oracle-2025",
            "metadata": {"type": "oracle", "coin": "chainlink"}
        },
        {
            "title": "Cardano Hard Fork",
            "description": "Cardano network hard fork with new capabilities",
            "category": "crypto",
            "subcategory": "cardano",
            "starts_at": datetime.now() + timedelta(days=35),
            "ends_at": datetime.now() + timedelta(days=35, hours=2),
            "location": "Global",
            "source": "manual",
            "link": "",
            "importance": 0.75,
            "unique_hash": "cardano-hardfork-2025",
            "metadata": {"type": "hardfork", "coin": "cardano"}
        },

        # Sports Events
        {
            "title": "FIFA World Cup 2026",
            "description": "FIFA World Cup tournament matches",
            "category": "sports",
            "subcategory": "football",
            "starts_at": datetime.now() + timedelta(days=60),
            "ends_at": datetime.now() + timedelta(days=90),
            "location": "USA, Canada, Mexico",
            "source": "manual",
            "link": "",
            "importance": 0.8,
            "unique_hash": "fifa-world-cup-2026",
            "metadata": {"type": "tournament", "sport": "football"}
        },
        {
            "title": "NBA Finals 2025",
            "description": "NBA Championship Finals series",
            "category": "sports",
            "subcategory": "basketball",
            "starts_at": datetime.now() + timedelta(days=120),
            "ends_at": datetime.now() + timedelta(days=130),
            "location": "USA",
            "source": "manual",
            "link": "",
            "importance": 0.7,
            "unique_hash": "nba-finals-2025",
            "metadata": {"type": "finals", "sport": "basketball"}
        },
        {
            "title": "Wimbledon Championships",
            "description": "The Championships, Wimbledon tennis tournament",
            "category": "sports",
            "subcategory": "tennis",
            "starts_at": datetime.now() + timedelta(days=80),
            "ends_at": datetime.now() + timedelta(days=94),
            "location": "London, UK",
            "source": "manual",
            "link": "",
            "importance": 0.75,
            "unique_hash": "wimbledon-2025",
            "metadata": {"type": "tournament", "sport": "tennis"}
        },
        {
            "title": "Olympic Games Paris 2025",
            "description": "Summer Olympic Games in Paris",
            "category": "sports",
            "subcategory": "olympics",
            "starts_at": datetime.now() + timedelta(days=200),
            "ends_at": datetime.now() + timedelta(days=216),
            "location": "Paris, France",
            "source": "manual",
            "link": "",
            "importance": 0.95,
            "unique_hash": "olympics-paris-2025",
            "metadata": {"type": "olympics", "sport": "multi"}
        },
        {
            "title": "Formula 1 Monaco Grand Prix",
            "description": "F1 Monaco Grand Prix race",
            "category": "sports",
            "subcategory": "racing",
            "starts_at": datetime.now() + timedelta(days=50),
            "ends_at": datetime.now() + timedelta(days=52),
            "location": "Monaco",
            "source": "manual",
            "link": "",
            "importance": 0.65,
            "unique_hash": "f1-monaco-2025",
            "metadata": {"type": "race", "sport": "f1"}
        },

        # Tech Events
        {
            "title": "Apple WWDC 2025",
            "description": "Apple Worldwide Developers Conference",
            "category": "tech",
            "subcategory": "conference",
            "starts_at": datetime.now() + timedelta(days=75),
            "ends_at": datetime.now() + timedelta(days=79),
            "location": "Cupertino, CA",
            "source": "manual",
            "link": "",
            "importance": 0.75,
            "unique_hash": "apple-wwdc-2025",
            "metadata": {"type": "conference", "company": "apple"}
        },
        {
            "title": "Google I/O 2025",
            "description": "Google's annual developer conference",
            "category": "tech",
            "subcategory": "conference",
            "starts_at": datetime.now() + timedelta(days=90),
            "ends_at": datetime.now() + timedelta(days=92),
            "location": "Mountain View, CA",
            "source": "manual",
            "link": "",
            "importance": 0.8,
            "unique_hash": "google-io-2025",
            "metadata": {"type": "conference", "company": "google"}
        },
        {
            "title": "Microsoft Build 2025",
            "description": "Microsoft's developer conference",
            "category": "tech",
            "subcategory": "conference",
            "starts_at": datetime.now() + timedelta(days=105),
            "ends_at": datetime.now() + timedelta(days=107),
            "location": "Seattle, WA",
            "source": "manual",
            "link": "",
            "importance": 0.7,
            "unique_hash": "microsoft-build-2025",
            "metadata": {"type": "conference", "company": "microsoft"}
        },
        {
            "title": "CES 2025",
            "description": "Consumer Electronics Show",
            "category": "tech",
            "subcategory": "exhibition",
            "starts_at": datetime.now() + timedelta(days=10),
            "ends_at": datetime.now() + timedelta(days=13),
            "location": "Las Vegas, NV",
            "source": "manual",
            "link": "",
            "importance": 0.85,
            "unique_hash": "ces-2025",
            "metadata": {"type": "exhibition", "industry": "electronics"}
        },
        {
            "title": "AWS re:Invent 2025",
            "description": "Amazon Web Services annual conference",
            "category": "tech",
            "subcategory": "conference",
            "starts_at": datetime.now() + timedelta(days=140),
            "ends_at": datetime.now() + timedelta(days=145),
            "location": "Las Vegas, NV",
            "source": "manual",
            "link": "",
            "importance": 0.8,
            "unique_hash": "aws-reinvent-2025",
            "metadata": {"type": "conference", "company": "aws"}
        },

        # World/Politics Events
        {
            "title": "G7 Summit 2025",
            "description": "Group of Seven leaders summit meeting",
            "category": "world",
            "subcategory": "politics",
            "starts_at": datetime.now() + timedelta(days=100),
            "ends_at": datetime.now() + timedelta(days=103),
            "location": "Italy",
            "source": "manual",
            "link": "",
            "importance": 0.7,
            "unique_hash": "g7-summit-2025",
            "metadata": {"type": "summit", "organization": "g7"}
        },
        {
            "title": "UN Climate Change Conference",
            "description": "COP30 United Nations Climate Change Conference",
            "category": "world",
            "subcategory": "environment",
            "starts_at": datetime.now() + timedelta(days=180),
            "ends_at": datetime.now() + timedelta(days=190),
            "location": "Brazil",
            "source": "manual",
            "link": "",
            "importance": 0.9,
            "unique_hash": "cop30-2025",
            "metadata": {"type": "conference", "organization": "un"}
        },
        {
            "title": "World Economic Forum",
            "description": "Annual meeting in Davos",
            "category": "world",
            "subcategory": "economics",
            "starts_at": datetime.now() + timedelta(days=25),
            "ends_at": datetime.now() + timedelta(days=28),
            "location": "Davos, Switzerland",
            "source": "manual",
            "link": "",
            "importance": 0.8,
            "unique_hash": "wef-davos-2025",
            "metadata": {"type": "forum", "organization": "wef"}
        },
        {
            "title": "NATO Summit 2025",
            "description": "NATO leaders summit meeting",
            "category": "world",
            "subcategory": "politics",
            "starts_at": datetime.now() + timedelta(days=160),
            "ends_at": datetime.now() + timedelta(days=162),
            "location": "Washington, DC",
            "source": "manual",
            "link": "",
            "importance": 0.75,
            "unique_hash": "nato-summit-2025",
            "metadata": {"type": "summit", "organization": "nato"}
        },
        {
            "title": "IMF Annual Meetings",
            "description": "International Monetary Fund annual meetings",
            "category": "world",
            "subcategory": "economics",
            "starts_at": datetime.now() + timedelta(days=220),
            "ends_at": datetime.now() + timedelta(days=225),
            "location": "Marrakech, Morocco",
            "source": "manual",
            "link": "",
            "importance": 0.7,
            "unique_hash": "imf-annual-2025",
            "metadata": {"type": "meeting", "organization": "imf"}
        },

        # Markets/Finance Events
        {
            "title": "Federal Reserve Meeting",
            "description": "FOMC interest rate decision meeting",
            "category": "markets",
            "subcategory": "rates",
            "starts_at": datetime.now() + timedelta(days=12),
            "ends_at": datetime.now() + timedelta(days=12, hours=2),
            "location": "Washington, DC",
            "source": "manual",
            "link": "",
            "importance": 0.85,
            "unique_hash": "fed-meeting-2025-01",
            "metadata": {"type": "meeting", "organization": "federal_reserve"}
        },
        {
            "title": "ECB Interest Rate Decision",
            "description": "European Central Bank monetary policy meeting",
            "category": "markets",
            "subcategory": "rates",
            "starts_at": datetime.now() + timedelta(days=18),
            "ends_at": datetime.now() + timedelta(days=18, hours=1),
            "location": "Frankfurt, Germany",
            "source": "manual",
            "link": "",
            "importance": 0.8,
            "unique_hash": "ecb-meeting-2025-01",
            "metadata": {"type": "meeting", "organization": "ecb"}
        },
        {
            "title": "Earnings Season Q1 2025",
            "description": "Major companies Q1 2025 earnings reports",
            "category": "markets",
            "subcategory": "earnings",
            "starts_at": datetime.now() + timedelta(days=95),
            "ends_at": datetime.now() + timedelta(days=110),
            "location": "Global",
            "source": "manual",
            "link": "",
            "importance": 0.75,
            "unique_hash": "earnings-q1-2025",
            "metadata": {"type": "earnings", "quarter": "q1"}
        },
        {
            "title": "OPEC+ Meeting",
            "description": "OPEC and allies production decision meeting",
            "category": "markets",
            "subcategory": "oil",
            "starts_at": datetime.now() + timedelta(days=40),
            "ends_at": datetime.now() + timedelta(days=40, hours=3),
            "location": "Vienna, Austria",
            "source": "manual",
            "link": "",
            "importance": 0.7,
            "unique_hash": "opec-meeting-2025-02",
            "metadata": {"type": "meeting", "organization": "opec"}
        },
        {
            "title": "G20 Finance Ministers Meeting",
            "description": "G20 Finance Ministers and Central Bank Governors meeting",
            "category": "markets",
            "subcategory": "finance",
            "starts_at": datetime.now() + timedelta(days=65),
            "ends_at": datetime.now() + timedelta(days=67),
            "location": "São Paulo, Brazil",
            "source": "manual",
            "link": "",
            "importance": 0.75,
            "unique_hash": "g20-finance-2025",
            "metadata": {"type": "meeting", "organization": "g20"}
        }
    ]

    logger.info(f"Загружаем {len(sample_events)} событий...")

    stored_count = 0
    for event_data in sample_events:
        try:
            # Сохранить событие
            result = await events_service.insert_events([event_data])
            if result > 0:
                stored_count += 1
                logger.info(f"✅ Событие сохранено: {event_data['title']}")
            else:
                logger.error(f"❌ Ошибка сохранения: {event_data['title']}")
        except Exception as e:
            logger.error(f"❌ Ошибка при сохранении события {event_data['title']}: {e}")

    logger.info(f"📊 Всего сохранено: {stored_count} из {len(sample_events)} событий")

async def main():  # noqa: E302
    """Основная функция."""
    try:
        await load_sample_events()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

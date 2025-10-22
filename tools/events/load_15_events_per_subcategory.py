#!/usr/bin/env python3
"""
Скрипт для загрузки по 15 новых событий в каждую субкатегорию PulseAI.

Этот скрипт создает разнообразные события по всем существующим субкатегориям
с реалистичными датами, уровнями важности и метаданными.
"""

import sys
import os
import asyncio
import random
import time
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.events_service import get_events_service
from dotenv import load_dotenv

load_dotenv()

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_events_for_subcategory(category: str, subcategory: str, count: int = 15) -> list:
    """Генерирует события для конкретной субкатегории."""
    events = []

    for i in range(count):
        # Базовые поля для всех событий
        base_event = {
            "title": "",
            "category": category,
            "subcategory": subcategory,
            "starts_at": datetime.now(timezone.utc) + timedelta(days=random.randint(1, 180)),
            "ends_at": None,
            "source": "manual_load",
            "link": "",
            "importance": round(random.uniform(0.3, 0.9), 2),
            "description": "",
            "location": "Global",
            "organizer": None,
            "group_name": None,
            "metadata": {},
        }

        # Генерируем специфичные для категории события
        if category == "crypto":
            events.append(_generate_crypto_event(base_event, subcategory, i))
        elif category == "sports":
            events.append(_generate_sports_event(base_event, subcategory, i))
        elif category == "tech":
            events.append(_generate_tech_event(base_event, subcategory, i))
        elif category == "markets":
            events.append(_generate_markets_event(base_event, subcategory, i))
        elif category == "world":
            events.append(_generate_world_event(base_event, subcategory, i))
        else:
            events.append(_generate_generic_event(base_event, subcategory, i))

    return events


def _generate_crypto_event(base_event: dict, subcategory: str, index: int) -> dict:
    """Генерирует крипто события."""
    event = base_event.copy()

    crypto_templates = {
        "bitcoin": [
            "Bitcoin Network Difficulty Adjustment #{block}",
            "Bitcoin Halving Countdown Event",
            "Bitcoin Taproot Upgrade Deployment",
            "Bitcoin Layer 2 Protocol Launch",
            "Bitcoin Lightning Network Expansion",
        ],
        "ethereum": [
            "Ethereum {upgrade} Hard Fork",
            "Ethereum Shanghai Upgrade v{version}",
            "Ethereum EIP-{eip} Implementation",
            "Ethereum Gas Fee Optimization Update",
            "Ethereum Staking Reward Adjustment",
        ],
        "defi": [
            "DeFi Protocol {protocol} Mainnet Launch",
            "Yield Farming Pool {pool} Activation",
            "DeFi Insurance Protocol Launch",
            "Cross-chain Bridge Security Update",
            "DeFi Governance Token Launch",
        ],
        "nft": [
            "NFT Marketplace {marketplace} Launch",
            "NFT Collection {collection} Drop",
            "NFT Lending Protocol Beta",
            "NFT Gaming Platform Release",
            "NFT Art Auction Event",
        ],
        "regulation": [
            "Crypto Regulation Framework Update",
            "Digital Asset Compliance Guidelines",
            "CBDC Development Update",
            "Crypto Tax Policy Announcement",
            "Blockchain Legal Framework Release",
        ],
        "security": [
            "Smart Contract Security Audit Results",
            "Crypto Exchange Security Enhancement",
            "DeFi Protocol Vulnerability Patch",
            "Multi-signature Wallet Update",
            "Blockchain Security Protocol Upgrade",
        ],
        "listing": [
            "{exchange} New Token Listing",
            "Crypto Exchange Feature Update",
            "Trading Pair Addition Announcement",
            "Exchange Security Infrastructure Update",
            "Crypto Exchange Partnership",
        ],
        "mainnet": [
            "{blockchain} Mainnet Launch",
            "Layer 2 Network Activation",
            "Sidechain Protocol Release",
            "Cross-chain Network Launch",
            "Blockchain Testnet to Mainnet Migration",
        ],
        "airdrop": [
            "{token} Airdrop Distribution",
            "Community Token Reward Program",
            "DeFi Protocol Token Airdrop",
            "Governance Token Distribution",
            "Layer 2 Token Airdrop Event",
        ],
        "trending": [
            "{coin} Market Momentum Event",
            "Crypto Trending Analysis Update",
            "Market Cap Milestone Achievement",
            "Trading Volume Record Break",
            "Social Media Crypto Trend",
        ],
    }

    templates = crypto_templates.get(subcategory, ["Crypto Event {index}"])
    template = random.choice(templates)

    # Заполняем шаблон
    replacements = {
        "block": random.randint(800000, 850000),
        "upgrade": random.choice(["Berlin", "London", "Shanghai", "Cancun"]),
        "version": f"{random.randint(2, 4)}.{random.randint(0, 9)}",
        "eip": random.randint(1000, 5000),
        "protocol": random.choice(["Uniswap", "Compound", "Aave", "Maker"]),
        "pool": random.choice(["ETH-USDC", "BTC-ETH", "USDT-DAI"]),
        "marketplace": random.choice(["OpenSea", "Blur", "LooksRare"]),
        "collection": random.choice(["Bored Ape", "CryptoPunks", "Azuki"]),
        "exchange": random.choice(["Binance", "Coinbase", "Kraken"]),
        "blockchain": random.choice(["Polygon", "Arbitrum", "Optimism"]),
        "token": random.choice(["UNI", "COMP", "AAVE", "MKR"]),
        "coin": random.choice(["Bitcoin", "Ethereum", "Cardano"]),
        "index": index + 1,
    }

    event["title"] = template.format(**replacements)
    event["description"] = f"Important {subcategory} event in the crypto ecosystem"
    event["currency"] = random.choice(["BTC", "ETH", "USD", "USDT"])
    event["metadata"] = {
        "event_type": subcategory,
        "blockchain": random.choice(["bitcoin", "ethereum", "polygon"]),
        "impact_level": random.choice(["low", "medium", "high"]),
    }

    return event


def _generate_sports_event(base_event: dict, subcategory: str, index: int) -> dict:
    """Генерирует спортивные события."""
    event = base_event.copy()

    sports_templates = {
        "football": [
            "{league} Matchday {matchday}",
            "{team1} vs {team2} - {competition}",
            "Champions League {round}",
            "Europa League {round}",
            "{team} Transfer Window Update",
        ],
        "basketball": [
            "NBA {team1} vs {team2}",
            "WNBA Championship Series",
            "EuroLeague {team1} vs {team2}",
            "NCAA Tournament {round}",
            "NBA All-Star Game",
        ],
        "tennis": [
            "{tournament} Championship",
            "ATP {tournament} Final",
            "WTA {tournament} Semifinal",
            "Tennis Grand Slam {event}",
            "Davis Cup {round}",
        ],
        "racing": [
            "Formula 1 {circuit} Grand Prix",
            "NASCAR {race} Championship",
            "MotoGP {circuit} Race",
            "IndyCar {circuit} Event",
            "WRC {rally} Championship",
        ],
        "olympics": [
            "Olympic Games {sport} Qualification",
            "Paralympic Games {sport} Event",
            "Youth Olympic Games {sport}",
            "Winter Olympic Games {sport}",
            "Summer Olympic Games {sport}",
        ],
        "esports_general": [
            "{game} World Championship",
            "ESL {game} Tournament",
            "{game} Major Tournament",
            "Gaming Convention {convention}",
            "Esports Awards Ceremony",
        ],
        "dota2": [
            "Dota 2 {tournament}",
            "The International {year}",
            "DPC {region} League",
            "Dota 2 Major {major}",
            "Dota 2 Minor Tournament",
        ],
        "csgo": [
            "CS:GO {tournament}",
            "IEM {tournament}",
            "BLAST {tournament}",
            "ESL Pro League {season}",
            "CS:GO Major Championship",
        ],
    }

    templates = sports_templates.get(subcategory, ["Sports Event {index}"])
    template = random.choice(templates)

    replacements = {
        "league": random.choice(["Premier League", "La Liga", "Bundesliga", "Serie A"]),
        "matchday": random.randint(1, 38),
        "team1": random.choice(["Manchester City", "Real Madrid", "Barcelona", "Bayern Munich"]),
        "team2": random.choice(["Liverpool", "Atletico Madrid", "PSG", "Juventus"]),
        "competition": random.choice(["Champions League", "Europa League", "FA Cup"]),
        "round": random.choice(["Group Stage", "Round of 16", "Quarter Final", "Semi Final"]),
        "team": random.choice(["Manchester United", "Chelsea", "Arsenal"]),
        "tournament": random.choice(["Wimbledon", "US Open", "Australian Open", "French Open"]),
        "circuit": random.choice(["Monaco", "Silverstone", "Monza", "Spa"]),
        "race": random.choice(["Daytona 500", "Indianapolis 500"]),
        "rally": random.choice(["Monte Carlo", "Rally Finland", "Acropolis"]),
        "sport": random.choice(["Swimming", "Athletics", "Cycling", "Gymnastics"]),
        "game": random.choice(["League of Legends", "Counter-Strike", "Dota 2"]),
        "convention": random.choice(["E3", "Gamescom", "PAX"]),
        "esports_tournament": random.choice(["World Championship", "Major", "Minor"]),
        "year": "2025",
        "region": random.choice(["Europe", "North America", "Asia"]),
        "major": random.choice(["Spring", "Summer", "Fall"]),
        "season": random.randint(1, 20),
        "index": index + 1,
    }

    event["title"] = template.format(**replacements)
    event["description"] = f"Exciting {subcategory} sporting event"
    event["location"] = random.choice(["London", "New York", "Tokyo", "Paris", "Berlin"])
    event["metadata"] = {
        "sport_type": subcategory,
        "competition_level": random.choice(["amateur", "professional", "world_championship"]),
        "venue_capacity": random.randint(5000, 100000),
    }

    return event


def _generate_tech_event(base_event: dict, subcategory: str, index: int) -> dict:
    """Генерирует технологические события."""
    event = base_event.copy()

    tech_templates = {
        "conference": [
            "{company} Developer Conference {year}",
            "{tech} Summit {year}",
            "AI & Machine Learning Conference",
            "{company} Tech Talk Series",
            "Open Source Conference {year}",
        ],
        "product_launches": [
            "{company} {product} Launch Event",
            "New {tech} Product Announcement",
            "{company} Innovation Showcase",
            "Tech Product Release Event",
            "{company} Next Generation Reveal",
        ],
        "ai": [
            "AI Research Breakthrough Presentation",
            "Machine Learning Model Release",
            "AI Ethics Conference {year}",
            "Neural Network Optimization Update",
            "AI in Healthcare Summit",
        ],
        "security": [
            "Cybersecurity Threat Analysis Update",
            "Security Vulnerability Patch Release",
            "Cyber Defense Strategy Summit",
            "Information Security Conference",
            "Secure Coding Best Practices Workshop",
        ],
        "space": [
            "{company} Rocket Launch Mission",
            "Satellite Deployment Event",
            "Space Exploration Milestone",
            "Space Technology Innovation Demo",
            "Cosmic Research Mission Launch",
        ],
        "summits": [
            "Cloud Computing Summit {year}",
            "IoT Technology Innovation Summit",
            "Blockchain Technology Conference",
            "Quantum Computing Research Summit",
            "5G Network Deployment Summit",
        ],
        "exhibition": [
            "CES Technology Exhibition {year}",
            "Tech Innovation Showcase",
            "Consumer Electronics Expo",
            "Technology Trade Fair",
            "Innovation and Technology Expo",
        ],
    }

    templates = tech_templates.get(subcategory, ["Tech Event {index}"])
    template = random.choice(templates)

    replacements = {
        "company": random.choice(["Apple", "Google", "Microsoft", "Amazon", "Meta"]),
        "year": "2025",
        "tech": random.choice(["AI", "Blockchain", "IoT", "Quantum", "5G"]),
        "product": random.choice(["iPhone", "Pixel", "Surface", "Echo", "Quest"]),
        "index": index + 1,
    }

    event["title"] = template.format(**replacements)
    event["description"] = f"Important {subcategory} technology event"
    event["location"] = random.choice(["San Francisco", "New York", "Austin", "Las Vegas", "Berlin"])
    event["metadata"] = {
        "event_type": subcategory,
        "tech_domain": random.choice(["software", "hardware", "services"]),
        "attendee_estimate": random.randint(100, 50000),
    }

    return event


def _generate_markets_event(base_event: dict, subcategory: str, index: int) -> dict:
    """Генерирует финансовые события."""
    event = base_event.copy()

    markets_templates = {
        "earnings": [
            "{company} Q{quarter} {year} Earnings Report",
            "{company} Annual Earnings Call",
            "{sector} Sector Earnings Update",
            "{company} Financial Results Presentation",
            "{company} Investor Earnings Briefing",
        ],
        "rates": [
            "{bank} Interest Rate Decision",
            "Central Bank Policy Meeting",
            "Monetary Policy Committee Update",
            "Interest Rate Forecast Update",
            "Banking Sector Rate Analysis",
        ],
        "economic_data": [
            "US {indicator} Data Release",
            "EU {indicator} Monthly Update",
            "{country} Economic Indicator Report",
            "Global {indicator} Analysis",
            "Economic Data Impact Assessment",
        ],
        "forex": [
            "USD/{currency} Exchange Rate Update",
            "Major Currency Pair Analysis",
            "Forex Market Volatility Report",
            "Currency Market Outlook Update",
            "Central Bank FX Intervention",
        ],
        "bonds": [
            "{type} Bond Auction",
            "Government Bond Yield Analysis",
            "Corporate Bond Market Update",
            "Bond Market Liquidity Report",
            "Fixed Income Market Outlook",
        ],
        "commodities": [
            "{commodity} Price Forecast Update",
            "Commodity Market Analysis",
            "{commodity} Supply Chain Update",
            "Energy Market Price Review",
            "Precious Metals Market Update",
        ],
        "oil": [
            "OPEC+ Production Decision Meeting",
            "Crude Oil Price Analysis",
            "Energy Sector Market Update",
            "Oil Production Forecast Update",
            "Petroleum Market Supply Report",
        ],
        "finance": [
            "G20 Finance Ministers Meeting",
            "IMF Economic Outlook Update",
            "World Bank Development Report",
            "Global Finance Summit {year}",
            "International Finance Conference",
        ],
    }

    templates = markets_templates.get(subcategory, ["Markets Event {index}"])
    template = random.choice(templates)

    replacements = {
        "company": random.choice(["Apple", "Tesla", "Amazon", "Microsoft", "Google", "Meta"]),
        "quarter": random.randint(1, 4),
        "year": "2025",
        "sector": random.choice(["Technology", "Healthcare", "Energy", "Finance"]),
        "bank": random.choice(["Federal Reserve", "ECB", "Bank of England", "Bank of Japan"]),
        "indicator": random.choice(["GDP", "CPI", "Unemployment", "Retail Sales"]),
        "country": random.choice(["US", "EU", "China", "Japan", "UK"]),
        "currency": random.choice(["EUR", "GBP", "JPY", "CNY"]),
        "type": random.choice(["Treasury", "Corporate", "Municipal", "High Yield"]),
        "commodity": random.choice(["Gold", "Silver", "Oil", "Gas", "Wheat"]),
        "index": index + 1,
    }

    event["title"] = template.format(**replacements)
    event["description"] = f"Important {subcategory} market event"
    event["location"] = random.choice(["New York", "London", "Frankfurt", "Tokyo", "Singapore"])
    event["metadata"] = {
        "market_type": subcategory,
        "economic_impact": random.choice(["low", "medium", "high"]),
        "currency": random.choice(["USD", "EUR", "GBP", "JPY"]),
    }

    return event


def _generate_world_event(base_event: dict, subcategory: str, index: int) -> dict:
    """Генерирует мировые события."""
    event = base_event.copy()

    world_templates = {
        "politics": [
            "{organization} Summit {year}",
            "{country} Election {year}",
            "International {topic} Conference",
            "Global {topic} Agreement Signing",
            "{organization} Meeting Update",
        ],
        "environment": [
            "Climate Change Summit {year}",
            "COP{number} Climate Conference",
            "Global Environmental Initiative",
            "Sustainability Forum {year}",
            "Renewable Energy Summit",
        ],
        "economics": [
            "G{number} Economic Summit",
            "World Economic Forum {year}",
            "Global Trade Agreement Update",
            "International Finance Conference",
            "Global Economic Outlook Update",
        ],
        "health": [
            "WHO Global Health Update",
            "International Health Summit",
            "Global Health Initiative Launch",
            "Public Health Conference {year}",
            "Medical Research Breakthrough",
        ],
        "conflicts": [
            "UN Security Council Meeting",
            "International Conflict Resolution",
            "Global Peacekeeping Update",
            "Diplomatic Mission Update",
            "International Security Briefing",
        ],
    }

    templates = world_templates.get(subcategory, ["World Event {index}"])
    template = random.choice(templates)

    replacements = {
        "organization": random.choice(["UN", "NATO", "EU", "ASEAN", "African Union"]),
        "year": "2025",
        "country": random.choice(["US", "China", "Russia", "Germany", "France"]),
        "topic": random.choice(["Trade", "Climate", "Security", "Technology", "Health"]),
        "number": random.choice([7, 8, 20, 30]),
        "index": index + 1,
    }

    event["title"] = template.format(**replacements)
    event["description"] = f"Important {subcategory} world event"
    event["location"] = random.choice(["New York", "Geneva", "Brussels", "Vienna", "Nairobi"])
    event["metadata"] = {
        "event_type": subcategory,
        "global_impact": random.choice(["regional", "global"]),
        "organizations": [random.choice(["UN", "NATO", "EU", "WHO"])],
    }

    return event


def _generate_generic_event(base_event: dict, subcategory: str, index: int) -> dict:
    """Генерирует общие события для неизвестных субкатегорий."""
    event = base_event.copy()
    event["title"] = f"{subcategory.title()} Event {index + 1}"
    event["description"] = f"Important event in {subcategory} category"
    event["metadata"] = {"event_type": subcategory, "category": base_event["category"]}

    return event


# Определяем все субкатегории по категориям
EVENT_SUBCATEGORIES = {
    "crypto": [
        "bitcoin",
        "ethereum",
        "defi",
        "nft",
        "regulation",
        "security",
        "listing",
        "mainnet",
        "airdrop",
        "trending",
        "gamefi",
        "cbdc",
    ],
    "sports": [
        "football",
        "basketball",
        "tennis",
        "racing",
        "olympics",
        "esports_general",
        "dota2",
        "csgo",
        "lol",
        "valorant",
    ],
    "tech": [
        "conference",
        "product_launches",
        "ai",
        "security",
        "space",
        "summits",
        "exhibition",
        "github_releases",
        "infrastructure",
    ],
    "markets": [
        "earnings",
        "rates",
        "economic_data",
        "forex",
        "bonds",
        "commodities",
        "oil",
        "finance",
        "ipos",
        "dividends",
    ],
    "world": ["politics", "environment", "economics", "health", "conflicts", "diplomacy", "climate", "sustainability"],
}


async def load_events_per_subcategory():
    """Загружает по 15 событий в каждую субкатегорию."""
    events_service = get_events_service()

    total_loaded = 0
    total_subcategories = 0

    logger.info("🚀 Начинаем загрузку событий по субкатегориям...")

    for category, subcategories in EVENT_SUBCATEGORIES.items():
        logger.info(f"📂 Обрабатываем категорию: {category}")

        for subcategory in subcategories:
            logger.info(f"  📋 Загружаем 15 событий для субкатегории: {category}/{subcategory}")

            try:
                # Генерируем 15 событий для этой субкатегории
                events = generate_events_for_subcategory(category, subcategory, 15)

                # Вставляем события в базу данных
                inserted_count = await events_service.insert_events(events)

                if inserted_count > 0:
                    logger.info(f"    ✅ Загружено {inserted_count} событий в {category}/{subcategory}")
                    total_loaded += inserted_count
                else:
                    logger.warning(f"    ⚠️ Не удалось загрузить события в {category}/{subcategory}")

                total_subcategories += 1

                # Небольшая задержка между субкатегориями
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"    ❌ Ошибка при загрузке {category}/{subcategory}: {e}")

    logger.info(f"🎉 Загрузка завершена!")
    logger.info(f"📊 Всего обработано субкатегорий: {total_subcategories}")
    logger.info(f"📈 Всего загружено событий: {total_loaded}")

    return total_loaded


async def main():
    """Основная функция."""
    try:
        await load_events_per_subcategory()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Скрипт для распределения источников по всем подкатегориям
"""

import yaml
import shutil
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def distribute_sources_to_subcategories():
    """Распределяет источники по всем подкатегориям"""

    # Создаем резервную копию
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f'config/sources.backup.before_distribute.{timestamp}.yaml'
    shutil.copy('config/sources.yaml', backup_file)
    logger.info(f"✅ Создана резервная копия: {backup_file}")

    # Загружаем текущую конфигурацию
    with open('config/sources.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Собираем все источники из заполненных подкатегорий
    all_sources = []
    for category, subcategories in config.items():
        for subcategory, data in subcategories.items():
            sources = data.get('sources', [])
            if sources:
                for source in sources:
                    source['category'] = category
                    source['subcategory'] = subcategory
                    all_sources.append(source)

    logger.info(f"📊 Собрано {len(all_sources)} источников из заполненных подкатегорий")

    # Определяем распределение источников по подкатегориям
    distribution = {
        # Crypto
        'crypto/defi': [
            'defi',
            'defi protocol',
            'uniswap',
            'compound',
            'aave',
            'maker',
            'curve',
            'yearn',
        ],
        'crypto/ethereum': [
            'ethereum',
            'eth',
            'ethereum network',
            'eth2',
            'eth2.0',
            'shanghai',
            'merge',
        ],
        'crypto/exchanges': [
            'exchange',
            'binance',
            'coinbase',
            'kraken',
            'bitfinex',
            'kucoin',
            'huobi',
            'okx',
        ],
        'crypto/gamefi': [
            'gamefi',
            'gaming',
            'nft gaming',
            'play to earn',
            'axie',
            'sandbox',
            'decentraland',
        ],
        'crypto/market_trends': [
            'market',
            'price',
            'bull',
            'bear',
            'rally',
            'crash',
            'analysis',
            'trend',
        ],
        'crypto/nft': ['nft', 'non-fungible', 'opensea', 'blur', 'looksrare', 'nft collection'],
        # Markets
        'markets/bonds': ['bond', 'treasury', 'yield', 'fixed income', 'government bond'],
        'markets/central_banks': [
            'fed',
            'federal reserve',
            'ecb',
            'central bank',
            'interest rate',
            'monetary policy',
        ],
        'markets/commodities': [
            'gold',
            'silver',
            'oil',
            'gas',
            'commodity',
            'crude',
            'wti',
            'brent',
        ],
        'markets/earnings': ['earnings', 'quarterly', 'revenue', 'profit', 'eps', 'guidance'],
        'markets/economic_data': [
            'gdp',
            'inflation',
            'cpi',
            'ppi',
            'unemployment',
            'economic indicator',
        ],
        'markets/forex': [
            'forex',
            'fx',
            'currency',
            'dollar',
            'euro',
            'yen',
            'pound',
            'usd',
            'eur',
        ],
        'markets/funds_etfs': ['etf', 'fund', 'mutual fund', 'hedge fund', 'index fund'],
        'markets/ipos': ['ipo', 'public offering', 'listing', 'nasdaq', 'nyse'],
        'markets/stocks': ['stock', 'equity', 'share', 'trading', 'nasdaq', 'sp500', 'dow jones'],
        # Sports
        'sports/badminton': ['badminton', 'shuttlecock'],
        'sports/baseball': ['baseball', 'mlb', 'yankees', 'red sox', 'dodgers', 'world series'],
        'sports/basketball': ['basketball', 'nba', 'lakers', 'warriors', 'celtics', 'playoffs'],
        'sports/cricket': ['cricket', 'ipl', 'ashes', 'world cup cricket'],
        'sports/esports': ['esports', 'gaming', 'csgo', 'dota', 'lol', 'valorant', 'overwatch'],
        'sports/football': [
            'football',
            'soccer',
            'premier league',
            'champions league',
            'world cup',
        ],
        'sports/other': ['sports', 'athletics', 'olympics', 'championship', 'tournament'],
        'sports/table_tennis': ['table tennis', 'ping pong'],
        'sports/tennis': ['tennis', 'wimbledon', 'us open', 'french open', 'australian open'],
        'sports/ufc_mma': ['ufc', 'mma', 'mixed martial arts', 'conor mcgregor', 'khabib'],
        # Tech
        'tech/blockchain_tech': ['blockchain', 'smart contract', 'solidity', 'web3', 'dapp'],
        'tech/conferences': [
            'conference',
            'summit',
            'tech conference',
            'ces',
            'wwdc',
            'google i/o',
        ],
        'tech/hardware': ['hardware', 'cpu', 'gpu', 'intel', 'amd', 'nvidia', 'apple silicon'],
        'tech/software': ['software', 'app', 'programming', 'developer', 'coding', 'github'],
        # World
        'world/climate': [
            'climate',
            'global warming',
            'carbon',
            'renewable',
            'sustainability',
            'green',
        ],
        'world/elections': ['election', 'vote', 'presidential', 'democracy', 'campaign', 'polling'],
        'world/energy': ['energy', 'oil', 'gas', 'renewable energy', 'solar', 'wind', 'nuclear'],
        'world/geopolitics': [
            'geopolitics',
            'international relations',
            'diplomacy',
            'foreign policy',
        ],
        'world/global_risks': [
            'risk',
            'threat',
            'security',
            'terrorism',
            'cyber attack',
            'pandemic',
        ],
        'world/migration': ['migration', 'refugee', 'immigration', 'border', 'asylum'],
        'world/organizations': ['un', 'nato', 'who', 'imf', 'world bank', 'g7', 'g20'],
        'world/sanctions': ['sanctions', 'embargo', 'trade war', 'economic sanctions'],
    }

    # Распределяем источники
    distributed_sources = {}
    for category, subcategories in config.items():
        distributed_sources[category] = {}

        for subcategory, data in subcategories.items():
            key = f'{category}/{subcategory}'
            keywords = distribution.get(key, [])

            # Ищем источники по ключевым словам
            matching_sources = []
            for source in all_sources:
                source_text = f"{source.get('name', '')} {source.get('url', '')} {source.get('description', '')}".lower()

                # Проверяем совпадение с ключевыми словами
                if any(keyword in source_text for keyword in keywords):
                    matching_sources.append(source)

            # Если не нашли по ключевым словам, берем случайные источники
            if not matching_sources and key in distribution:
                # Берем источники из той же категории
                category_sources = [s for s in all_sources if s['category'] == category]
                if category_sources:
                    # Берем первые 3-5 источников
                    matching_sources = category_sources[: min(5, len(category_sources))]

            # Сохраняем источники для подкатегории
            distributed_sources[category][subcategory] = {
                'icon': data.get('icon', ''),
                'sources': matching_sources,
            }

    # Сохраняем обновленную конфигурацию
    with open('config/sources.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(
            distributed_sources, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )

    # Подсчитываем статистику
    total_sources = 0
    empty_count = 0
    for category, subcategories in distributed_sources.items():
        for subcategory, data in subcategories.items():
            source_count = len(data.get('sources', []))
            total_sources += source_count
            if source_count == 0:
                empty_count += 1

    logger.info(f"✅ Распределение завершено!")
    logger.info(f"📊 Всего источников: {total_sources}")
    logger.info(f"📊 Пустых подкатегорий: {empty_count}")

    return distributed_sources


if __name__ == "__main__":
    distribute_sources_to_subcategories()

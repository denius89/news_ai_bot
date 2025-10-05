#!/usr/bin/env python3
"""
Умное распределение источников по всем подкатегориям
"""

import yaml
import shutil
from datetime import datetime
import logging
import random

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def smart_distribute_sources():
    """Умное распределение источников по всем подкатегориям"""
    
    # Создаем резервную копию
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f'config/sources.backup.smart_distribute.{timestamp}.yaml'
    shutil.copy('config/sources.yaml', backup_file)
    logger.info(f"✅ Создана резервная копия: {backup_file}")
    
    # Загружаем текущую конфигурацию
    with open('config/sources.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Собираем все источники
    all_sources = []
    for category, subcategories in config.items():
        for subcategory, data in subcategories.items():
            sources = data.get('sources', [])
            if sources:
                for source in sources:
                    source['category'] = category
                    source['subcategory'] = subcategory
                    all_sources.append(source)
    
    logger.info(f"📊 Собрано {len(all_sources)} источников")
    
    # Определяем приоритетные источники для каждой подкатегории
    priority_sources = {
        # Crypto - приоритетные источники
        'crypto/altcoins': [
            'coindesk', 'cointelegraph', 'decrypt', 'bitcoin magazine', 'newsbtc', 'btctimes'
        ],
        'crypto/bitcoin': [
            'bitcoin magazine', 'btctimes', 'newsbtc', 'coindesk', 'cointelegraph'
        ],
        'crypto/defi': [
            'defiant', 'defi pulse', 'defi prime', 'the defiant'
        ],
        'crypto/ethereum': [
            'ethereum foundation', 'consensys', 'ethereum world news'
        ],
        'crypto/exchanges': [
            'binance', 'coinbase', 'kraken', 'bitfinex'
        ],
        'crypto/gamefi': [
            'gamefi', 'gaming', 'nft gaming'
        ],
        'crypto/market_trends': [
            'market', 'price', 'analysis', 'trading'
        ],
        'crypto/nft': [
            'nft', 'opensea', 'nft now', 'nftgators'
        ],
        'crypto/regulation': [
            'regulation', 'sec', 'cftc', 'legal'
        ],
        'crypto/security': [
            'security', 'hack', 'audit', 'vulnerability'
        ],
        
        # Markets - приоритетные источники
        'markets/bonds': [
            'treasury', 'bond', 'yield', 'fixed income'
        ],
        'markets/central_banks': [
            'federal reserve', 'fed', 'ecb', 'central bank'
        ],
        'markets/commodities': [
            'gold', 'silver', 'oil', 'gas', 'commodity'
        ],
        'markets/earnings': [
            'earnings', 'quarterly', 'revenue', 'profit'
        ],
        'markets/economic_data': [
            'gdp', 'inflation', 'cpi', 'economic data'
        ],
        'markets/forex': [
            'forex', 'fx', 'currency', 'dollar', 'euro'
        ],
        'markets/funds_etfs': [
            'etf', 'fund', 'mutual fund', 'hedge fund'
        ],
        'markets/ipos': [
            'ipo', 'public offering', 'listing'
        ],
        'markets/stocks': [
            'stock', 'equity', 'nasdaq', 'nyse', 'sp500'
        ],
        
        # Sports - приоритетные источники
        'sports/badminton': ['badminton'],
        'sports/baseball': ['baseball', 'mlb'],
        'sports/basketball': ['basketball', 'nba'],
        'sports/cricket': ['cricket', 'ipl'],
        'sports/esports': ['esports', 'gaming'],
        'sports/football': ['football', 'soccer'],
        'sports/other': ['sports', 'athletics'],
        'sports/table_tennis': ['table tennis'],
        'sports/tennis': ['tennis'],
        'sports/ufc_mma': ['ufc', 'mma'],
        
        # Tech - приоритетные источники
        'tech/ai': [
            'artificial intelligence', 'ai', 'machine learning', 'openai', 'chatgpt'
        ],
        'tech/bigtech': [
            'google', 'apple', 'microsoft', 'amazon', 'meta', 'facebook'
        ],
        'tech/blockchain_tech': [
            'blockchain', 'smart contract', 'web3'
        ],
        'tech/conferences': [
            'conference', 'summit', 'ces', 'wwdc'
        ],
        'tech/cybersecurity': [
            'cybersecurity', 'security', 'hack', 'breach'
        ],
        'tech/hardware': [
            'hardware', 'cpu', 'gpu', 'intel', 'amd'
        ],
        'tech/software': [
            'software', 'app', 'programming', 'developer'
        ],
        'tech/startups': [
            'startup', 'venture', 'funding', 'unicorn'
        ],
        
        # World - приоритетные источники
        'world/climate': [
            'climate', 'global warming', 'carbon', 'renewable'
        ],
        'world/conflicts': [
            'conflict', 'war', 'military', 'tension'
        ],
        'world/diplomacy': [
            'diplomacy', 'foreign policy', 'embassy'
        ],
        'world/elections': [
            'election', 'vote', 'presidential', 'democracy'
        ],
        'world/energy': [
            'energy', 'oil', 'gas', 'renewable energy'
        ],
        'world/geopolitics': [
            'geopolitics', 'international relations'
        ],
        'world/global_risks': [
            'risk', 'threat', 'security', 'terrorism'
        ],
        'world/migration': [
            'migration', 'refugee', 'immigration'
        ],
        'world/organizations': [
            'un', 'nato', 'who', 'imf', 'world bank'
        ],
        'world/sanctions': [
            'sanctions', 'embargo', 'trade war'
        ],
        
        # Misc
        'misc/uncategorized': [
            'news', 'general', 'breaking', 'update'
        ]
    }
    
    # Создаем новую конфигурацию
    new_config = {}
    
    for category, subcategories in config.items():
        new_config[category] = {}
        
        for subcategory, data in subcategories.items():
            key = f'{category}/{subcategory}'
            
            # Ищем источники по приоритетным ключевым словам
            matching_sources = []
            priority_keywords = priority_sources.get(key, [])
            
            for source in all_sources:
                source_text = f"{source.get('name', '')} {source.get('url', '')} {source.get('description', '')}".lower()
                
                # Проверяем точное совпадение с приоритетными ключевыми словами
                for keyword in priority_keywords:
                    if keyword.lower() in source_text:
                        matching_sources.append(source)
                        break
            
            # Если не нашли по приоритетным ключевым словам, ищем по общим
            if not matching_sources:
                general_keywords = {
                    'crypto/altcoins': ['crypto', 'cryptocurrency', 'coin'],
                    'crypto/bitcoin': ['bitcoin', 'btc'],
                    'crypto/defi': ['defi', 'decentralized'],
                    'crypto/ethereum': ['ethereum', 'eth'],
                    'crypto/exchanges': ['exchange', 'trading'],
                    'crypto/gamefi': ['game', 'gaming'],
                    'crypto/market_trends': ['market', 'price', 'analysis'],
                    'crypto/nft': ['nft', 'non-fungible'],
                    'crypto/regulation': ['regulation', 'legal', 'sec'],
                    'crypto/security': ['security', 'hack', 'audit'],
                    
                    'markets/bonds': ['bond', 'treasury', 'yield'],
                    'markets/central_banks': ['fed', 'central bank', 'monetary'],
                    'markets/commodities': ['commodity', 'gold', 'oil'],
                    'markets/earnings': ['earnings', 'revenue', 'profit'],
                    'markets/economic_data': ['economic', 'gdp', 'inflation'],
                    'markets/forex': ['forex', 'currency', 'fx'],
                    'markets/funds_etfs': ['fund', 'etf', 'investment'],
                    'markets/ipos': ['ipo', 'public offering'],
                    'markets/stocks': ['stock', 'equity', 'nasdaq'],
                    
                    'sports/badminton': ['badminton'],
                    'sports/baseball': ['baseball', 'mlb'],
                    'sports/basketball': ['basketball', 'nba'],
                    'sports/cricket': ['cricket'],
                    'sports/esports': ['esports', 'gaming'],
                    'sports/football': ['football', 'soccer'],
                    'sports/other': ['sports'],
                    'sports/table_tennis': ['table tennis'],
                    'sports/tennis': ['tennis'],
                    'sports/ufc_mma': ['ufc', 'mma'],
                    
                    'tech/ai': ['ai', 'artificial intelligence'],
                    'tech/bigtech': ['google', 'apple', 'microsoft'],
                    'tech/blockchain_tech': ['blockchain'],
                    'tech/conferences': ['conference', 'summit'],
                    'tech/cybersecurity': ['cybersecurity', 'security'],
                    'tech/hardware': ['hardware', 'cpu', 'gpu'],
                    'tech/software': ['software', 'programming'],
                    'tech/startups': ['startup', 'venture'],
                    
                    'world/climate': ['climate', 'environment'],
                    'world/conflicts': ['conflict', 'war'],
                    'world/diplomacy': ['diplomacy', 'foreign'],
                    'world/elections': ['election', 'vote'],
                    'world/energy': ['energy', 'oil', 'gas'],
                    'world/geopolitics': ['geopolitics', 'international'],
                    'world/global_risks': ['risk', 'threat'],
                    'world/migration': ['migration', 'refugee'],
                    'world/organizations': ['un', 'nato', 'organization'],
                    'world/sanctions': ['sanctions', 'embargo'],
                    
                    'misc/uncategorized': ['news', 'general']
                }
                
                general_keywords_list = general_keywords.get(key, [])
                for keyword in general_keywords_list:
                    if keyword.lower() in source_text:
                        matching_sources.append(source)
                        break
            
            # Если все еще не нашли, берем случайные источники из той же категории
            if not matching_sources:
                category_sources = [s for s in all_sources if s['category'] == category]
                if category_sources:
                    # Берем случайные источники
                    random.shuffle(category_sources)
                    matching_sources = category_sources[:min(3, len(category_sources))]
            
            # Если и это не помогло, берем любые случайные источники
            if not matching_sources:
                random.shuffle(all_sources)
                matching_sources = all_sources[:min(2, len(all_sources))]
            
            # Ограничиваем количество источников (максимум 10 на подкатегорию)
            matching_sources = matching_sources[:10]
            
            # Сохраняем источники для подкатегории
            new_config[category][subcategory] = {
                'icon': data.get('icon', ''),
                'sources': matching_sources
            }
    
    # Сохраняем обновленную конфигурацию
    with open('config/sources.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(new_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Подсчитываем статистику
    total_sources = 0
    empty_count = 0
    filled_count = 0
    
    for category, subcategories in new_config.items():
        for subcategory, data in subcategories.items():
            source_count = len(data.get('sources', []))
            total_sources += source_count
            if source_count == 0:
                empty_count += 1
            else:
                filled_count += 1
    
    logger.info(f"✅ Умное распределение завершено!")
    logger.info(f"📊 Всего источников: {total_sources}")
    logger.info(f"📊 Заполненных подкатегорий: {filled_count}")
    logger.info(f"📊 Пустых подкатегорий: {empty_count}")
    
    return new_config

if __name__ == "__main__":
    smart_distribute_sources()

#!/usr/bin/env python3
"""
Инструмент для валидации RSS источников и поиска рабочих альтернатив.
"""

import sys
from pathlib import Path
import logging
import requests
import feedparser
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.categories import get_all_sources
from parsers.universal_rss_parser import UniversalRSSParser

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, application/atom+xml, text/html, */*",
}

def check_rss_source(url: str, name: str) -> dict:
    """Проверяет один RSS источник."""
    result = {
        'url': url,
        'name': name,
        'status': 'unknown',
        'status_code': None,
        'content_type': None,
        'entries_count': 0,
        'error': None,
        'is_valid': False
    }
    
    try:
        # Проверяем доступность
        response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        result['status_code'] = response.status_code
        result['content_type'] = response.headers.get('Content-Type', '')
        
        if response.status_code == 200:
            # Проверяем, является ли это RSS
            content = response.content
            feed = feedparser.parse(content)
            
            if feed.bozo and not feed.entries:
                result['status'] = 'invalid_rss'
                result['error'] = str(feed.bozo_exception)
            elif feed.entries:
                result['status'] = 'valid'
                result['entries_count'] = len(feed.entries)
                result['is_valid'] = True
            else:
                result['status'] = 'empty'
        else:
            result['status'] = 'http_error'
            result['error'] = f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        result['status'] = 'timeout'
        result['error'] = 'Request timeout'
    except requests.exceptions.ConnectionError:
        result['status'] = 'connection_error'
        result['error'] = 'Connection error'
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result

def find_alternative_rss(base_url: str, name: str) -> list:
    """Пытается найти альтернативные RSS фиды."""
    alternatives = []
    
    # Типичные пути для RSS фидов
    rss_paths = [
        '/rss',
        '/feed',
        '/feeds',
        '/rss.xml',
        '/feed.xml',
        '/feeds/rss',
        '/feeds/all.rss',
        '/.rss',
        '/news/rss',
        '/blog/rss',
        '/atom.xml',
        '/feeds/atom',
    ]
    
    try:
        base_domain = f"{base_url.split('://')[0]}://{base_url.split('://')[1].split('/')[0]}"
        
        for path in rss_paths:
            test_url = base_domain + path
            result = check_rss_source(test_url, f"{name} ({path})")
            if result['is_valid']:
                alternatives.append(result)
                
    except Exception as e:
        logger.debug(f"Ошибка поиска альтернатив для {base_url}: {e}")
    
    return alternatives

def validate_all_sources():
    """Валидирует все RSS источники."""
    print("🔍 Валидация RSS источников...\n")
    
    all_sources = get_all_sources()
    print(f"📋 Найдено {len(all_sources)} источников для проверки\n")
    
    results = []
    valid_sources = []
    invalid_sources = []
    
    # Проверяем источники параллельно
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_source = {
            executor.submit(check_rss_source, url, name): (cat, subcat, name, url)
            for cat, subcat, name, url in all_sources
        }
        
        for future in as_completed(future_to_source):
            cat, subcat, name, url = future_to_source[future]
            try:
                result = future.result()
                result['category'] = cat
                result['subcategory'] = subcat
                results.append(result)
                
                if result['is_valid']:
                    valid_sources.append(result)
                    print(f"✅ {name}: {result['entries_count']} записей")
                else:
                    invalid_sources.append(result)
                    print(f"❌ {name}: {result['status']} - {result['error']}")
                    
            except Exception as e:
                print(f"❌ Ошибка проверки {name}: {e}")
    
    # Статистика
    print(f"\n📊 Результаты валидации:")
    print(f"   ✅ Валидных источников: {len(valid_sources)}")
    print(f"   ❌ Невалидных источников: {len(invalid_sources)}")
    print(f"   📈 Успешность: {len(valid_sources)/(len(valid_sources)+len(invalid_sources))*100:.1f}%")
    
    # Группировка по статусам
    status_counts = {}
    for result in invalid_sources:
        status = result['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\n🔍 Анализ проблем:")
    for status, count in status_counts.items():
        print(f"   {status}: {count} источников")
    
    # Поиск альтернатив для неработающих источников
    print(f"\n🔍 Поиск альтернатив для неработающих источников...")
    alternatives_found = 0
    
    for result in invalid_sources[:5]:  # Проверяем первые 5 неработающих
        if result['status'] in ['http_error', 'connection_error']:
            print(f"\n🔍 Ищем альтернативы для {result['name']}...")
            alternatives = find_alternative_rss(result['url'], result['name'])
            
            if alternatives:
                alternatives_found += len(alternatives)
                print(f"   ✅ Найдено {len(alternatives)} альтернатив:")
                for alt in alternatives:
                    print(f"      {alt['url']} - {alt['entries_count']} записей")
            else:
                print(f"   ❌ Альтернативы не найдены")
    
    if alternatives_found > 0:
        print(f"\n💡 Всего найдено {alternatives_found} рабочих альтернатив!")
    
    return results, valid_sources, invalid_sources

def test_parser_with_valid_sources():
    """Тестирует парсер с валидными источниками."""
    print(f"\n🧪 Тестирование парсера с валидными источниками...")
    
    # Получаем валидные источники
    results, valid_sources, invalid_sources = validate_all_sources()
    
    if not valid_sources:
        print("❌ Нет валидных источников для тестирования")
        return
    
    # Тестируем первые 3 валидных источника
    test_sources = valid_sources[:3]
    
    parser = UniversalRSSParser()
    total_news = 0
    
    for source in test_sources:
        print(f"\n📰 Тестируем: {source['name']}")
        try:
            news_items = parser.parse_source(
                source['url'], 
                source['category'], 
                source['subcategory'], 
                source['name']
            )
            
            if news_items:
                total_news += len(news_items)
                print(f"   ✅ Парсер: {len(news_items)} новостей")
                
                # Показываем пример
                item = news_items[0]
                print(f"   📝 Пример: {item['title'][:60]}...")
            else:
                print(f"   ❌ Парсер: нет новостей")
                
        except Exception as e:
            print(f"   ❌ Ошибка парсера: {e}")
    
    parser.close()
    print(f"\n📊 Итого новостей от парсера: {total_news}")

if __name__ == "__main__":
    validate_all_sources()
    test_parser_with_valid_sources()

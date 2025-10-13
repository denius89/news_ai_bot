# Shebang retained: /usr/bin/env python3
"""
Объединенный инструмент для валидации источников.
Объединяет функциональность update_rss_sources.py, validate_rss_sources.py
"""


# === ИЗ update_rss_sources.py ===

# Shebang (moved to file header): /usr/bin/env python3
"""
Скрипт для обновления RSS-источников в PulseAI.

Проверяет валидность существующих RSS-фидов с помощью AdvancedParser,
удаляет неработающие и добавляет новые из GitHub-репозиториев.
"""

import sys
import asyncio
import logging
import yaml
import aiohttp
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urljoin, urlparse
from database.service import get_async_service
from parsers.advanced_parser import AdvancedParser  # noqa: F401

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/rss_update.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


class RSSUpdater:
    """Класс для обновления RSS-источников."""

    def __init__(self):
        """Инициализация RSS Updater."""
        self.config_path = Path("config/data/sources.yaml")
        self.backup_path = Path(f"config/sources.backup.{datetime.now().strftime('%Y%m%d')}.yaml")
        self.sources_config = {}
        self.parser = None
        self.session = None

        # Статистика
        self.stats = {"checked": 0, "removed": 0, "added": 0, "updated_categories": set()}

        # GitHub репозитории с RSS-фидами
        self.github_sources = [
            "https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/main/README.md",
            "https://raw.githubusercontent.com/mclassy/Cryptocurrency-RSS-Feed-List/main/README.md",
            "https://raw.githubusercontent.com/chainfeeds/RSSAggregatorforWeb3/main/README.md",
            "https://raw.githubusercontent.com/tuan3w/awesome-tech-rss/main/README.md",
            "https://raw.githubusercontent.com/foorilla/allinfosecnews_sources/main/README.md",
            "https://raw.githubusercontent.com/voidfiles/awesome-rss/main/README.md",
            "https://raw.githubusercontent.com/joshuawalcher/rssfeeds/main/README.md",
            "https://raw.githubusercontent.com/mcnaveen/awesome-rss/main/README.md",
        ]

        # Маппинг ключевых слов для категоризации
        self.category_keywords = {
            "crypto": {
                "bitcoin": ["bitcoin", "btc", "bitcoinmagazine"],
                "ethereum": ["ethereum", "eth", "ethereum.org"],
                "altcoins": ["altcoin", "cryptocurrency", "coin", "crypto"],
                "defi": ["defi", "decentralized", "uniswap", "compound"],
                "nft": ["nft", "non-fungible", "opensea"],
                "gamefi": ["gamefi", "gaming", "play-to-earn"],
                "regulation": ["regulation", "sec", "cftc", "legal"],
                "exchanges": ["exchange", "binance", "coinbase"],
                "security": ["security", "hack", "exploit", "vulnerability"],
            },
            "markets": {
                "stocks": ["stock", "equity", "nasdaq", "nyse"],
                "commodities": ["commodity", "gold", "oil", "silver"],
                "forex": ["forex", "currency", "fx", "dollar"],
                "bonds": ["bond", "treasury", "yield"],
                "central_banks": ["fed", "federal reserve", "ecb", "central bank"],
                "economic_data": ["economic", "gdp", "inflation", "unemployment"],
            },
            "tech": {
                "ai": ["ai", "artificial intelligence", "machine learning", "openai"],
                "bigtech": ["google", "apple", "microsoft", "amazon", "meta"],
                "startups": ["startup", "venture", "funding", "unicorn"],
                "cybersecurity": ["security", "cyber", "hack", "breach"],
                "hardware": ["hardware", "cpu", "gpu", "chip"],
                "blockchain_tech": ["blockchain", "smart contract", "web3"],
            },
            "sports": {
                "football": ["football", "soccer", "premier league", "champions league"],
                "basketball": ["basketball", "nba", "ncaa"],
                "tennis": ["tennis", "wimbledon", "us open"],
                "esports": ["esports", "gaming", "twitch", "streaming"],
            },
            "world": {
                "elections": ["election", "vote", "presidential", "parliament"],
                "geopolitics": ["geopolitics", "diplomacy", "international"],
                "conflicts": ["conflict", "war", "military", "defense"],
                "energy": ["energy", "oil", "gas", "renewable"],
                "climate": ["climate", "environment", "carbon", "green"],
                "diplomacy": ["diplomacy", "un", "nato", "summit"],
            },
        }

    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход."""
        await self._init_session()
        await self._load_config()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход."""
        await self._close_session()

    async def _init_session(self):
        """Инициализация HTTP сессии."""
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=5)

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        self.session = aiohttp.ClientSession(timeout=timeout, connector=connector, headers=headers)

    async def _close_session(self):
        """Закрытие HTTP сессии."""
        if self.session:
            await self.session.close()

    async def _load_config(self):
        """Загрузка конфигурации источников."""
        if not self.config_path.exists():
            logger.error(f"Файл {self.config_path} не найден")
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.sources_config = yaml.safe_load(f) or {}
            logger.info(f"Загружена конфигурация из {self.config_path}")
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            self.sources_config = {}

    async def _save_config(self):
        """Сохранение конфигурации источников."""
        try:
            # Создаем резервную копию
            if self.config_path.exists():
                import shutil

                shutil.copy2(self.config_path, self.backup_path)
                logger.info(f"Создана резервная копия: {self.backup_path}")

            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.sources_config, f, default_flow_style=False, sort_keys=True)
            logger.info(f"Конфигурация сохранена в {self.config_path}")
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")

    async def _validate_rss_feed(self, url: str) -> bool:
        """
        Проверка валидности RSS-фида.

        Args:
            url: URL RSS-фида

        Returns:
            True если фид валиден, False иначе
        """
        try:
            # Простая проверка HTTP запроса
            async with self.session.get(url) as response:
                if response.status != 200:
                    return False

                content = await response.text()

                # Проверяем, что это XML/RSS
                content_lower = content.lower()

                # Должен содержать RSS или Atom структуру
                if not ("<rss" in content_lower or "<feed" in content_lower):
                    return False

                # Должен содержать элементы новостей
                if not ("<item>" in content_lower or "<entry>" in content_lower):
                    return False

                return True

        except Exception as e:
            logger.debug(f"Ошибка валидации {url}: {e}")
            return False

    async def _extract_rss_from_github(self) -> List[str]:
        """
        Извлечение RSS-ссылок из GitHub репозиториев.

        Returns:
            Список найденных RSS-ссылок
        """
        rss_urls = set()

        for github_url in self.github_sources:
            try:
                logger.info(f"Загружаем RSS-фиды из {github_url}")

                async with self.session.get(github_url) as response:
                    if response.status == 200:
                        content = await response.text()

                        # Ищем RSS-ссылки в тексте
                        rss_patterns = [
                            r"https?://[^\s\)]+\.rss",
                            r"https?://[^\s\)]+/feed",
                            r"https?://[^\s\)]+/rss\.xml",
                            r"https?://[^\s\)]+/feed\.xml",
                            r"https?://[^\s\)]+/rss",
                        ]

                        for pattern in rss_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            rss_urls.update(matches)

                        logger.info(f"Найдено {len(rss_urls)} уникальных RSS-ссылок")

            except Exception as e:
                logger.error(f"Ошибка загрузки {github_url}: {e}")

        return list(rss_urls)

    def _categorize_rss(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Определение категории и подкатегории для RSS-фида.

        Args:
            url: URL RSS-фида

        Returns:
            Кортеж (category, subcategory) или (None, None)
        """
        url_lower = url.lower()
        domain = urlparse(url).netloc.lower()

        for category, subcategories in self.category_keywords.items():
            for subcategory, keywords in subcategories.items():
                for keyword in keywords:
                    if keyword in url_lower or keyword in domain:
                        return category, subcategory

        return None, None

    async def _check_existing_sources(self) -> Dict[str, List[str]]:
        """
        Проверка существующих RSS-источников.

        Returns:
            Словарь неработающих источников по категориям
        """
        invalid_sources = {}
        all_sources = []

        # Собираем все источники
        for category, category_data in self.sources_config.items():
            if not isinstance(category_data, dict):
                continue

            for subcategory, subcategory_data in category_data.items():
                if not isinstance(subcategory_data, dict):
                    continue

                sources_list = subcategory_data.get("sources", [])
                for source in sources_list:
                    if isinstance(source, dict):
                        url = source.get("url", "")
                        name = source.get("name", "")
                    elif isinstance(source, str):
                        if ":" in source:
                            name, url = source.split(":", 1)
                            name = name.strip()
                            url = url.strip()
                        else:
                            url = source
                            name = ""
                    else:
                        continue

                    if url:
                        all_sources.append((category, subcategory, name, url))

        logger.info(f"Проверяем {len(all_sources)} существующих источников")

        # Проверяем источники асинхронно
        semaphore = asyncio.Semaphore(5)  # Максимум 5 одновременных запросов

        async def check_source(source_info):
            category, subcategory, name, url = source_info
            async with semaphore:
                is_valid = await self._validate_rss_feed(url)
                self.stats["checked"] += 1

                if not is_valid:
                    if category not in invalid_sources:
                        invalid_sources[category] = {}
                    if subcategory not in invalid_sources[category]:
                        invalid_sources[category][subcategory] = []
                    invalid_sources[category][subcategory].append({"name": name, "url": url})

                    # Логируем удаление
                    with open("logs/removed_rss.log", "a", encoding="utf-8") as f:
                        f.write(f"{datetime.now().isoformat()} - {category}/{subcategory} - {url}\n")

                    logger.warning(f"❌ Невалидный RSS: {category}/{subcategory} - {url}")
                else:
                    logger.info(f"✅ Валидный RSS: {category}/{subcategory} - {url}")

        # Запускаем проверку всех источников
        tasks = [check_source(source) for source in all_sources]
        await asyncio.gather(*tasks, return_exceptions=True)

        return invalid_sources

    async def _remove_invalid_sources(self, invalid_sources: Dict[str, List[str]]):
        """Удаление невалидных источников из конфигурации."""
        for category, subcategories in invalid_sources.items():
            if category not in self.sources_config:
                continue

            for subcategory, sources in subcategories.items():
                if subcategory not in self.sources_config[category]:
                    continue

                # Удаляем невалидные источники
                valid_sources = []
                sources_list = self.sources_config[category][subcategory].get("sources", [])

                for source in sources_list:
                    source_url = ""
                    if isinstance(source, dict):
                        source_url = source.get("url", "")
                    elif isinstance(source, str) and ":" in source:
                        source_url = source.split(":", 1)[1].strip()

                    # Проверяем, не входит ли этот источник в список невалидных
                    is_invalid = any(inv_source["url"] == source_url for inv_source in sources)

                    if not is_invalid:
                        valid_sources.append(source)

                # Обновляем список источников
                self.sources_config[category][subcategory]["sources"] = valid_sources
                self.stats["removed"] += len(sources)
                self.stats["updated_categories"].add(f"{category}/{subcategory}")

                logger.info(f"Удалено {len(sources)} невалидных источников из {category}/{subcategory}")

    async def _add_new_sources(self):
        """Добавление новых RSS-источников из GitHub."""
        logger.info("Извлекаем новые RSS-фиды из GitHub репозиториев")
        new_rss_urls = await self._extract_rss_from_github()

        logger.info(f"Найдено {len(new_rss_urls)} потенциальных RSS-фидов")

        # Проверяем валидность и категоризируем
        valid_new_sources = {}

        for url in new_rss_urls:
            try:
                # Проверяем валидность
                is_valid = await self._validate_rss_feed(url)
                if not is_valid:
                    continue

                # Определяем категорию
                category, subcategory = self._categorize_rss(url)
                if not category or not subcategory:
                    category, subcategory = "misc", "uncategorized"

                # Проверяем, что источник еще не добавлен
                if self._is_source_exists(url):
                    continue

                # Добавляем в список новых источников
                if category not in valid_new_sources:
                    valid_new_sources[category] = {}
                if subcategory not in valid_new_sources[category]:
                    valid_new_sources[category][subcategory] = []

                # Извлекаем название из URL
                name = urlparse(url).netloc.replace("www.", "")

                valid_new_sources[category][subcategory].append({"name": name, "url": url})

                # Логируем добавление
                with open("logs/added_rss.log", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.now().isoformat()} - {category}/{subcategory} - {url}\n")

                logger.info(f"🆕 Новый валидный RSS: {category}/{subcategory} - {url}")

            except Exception as e:
                logger.error(f"Ошибка обработки {url}: {e}")
                continue

        # Добавляем новые источники в конфигурацию
        for category, subcategories in valid_new_sources.items():
            if category not in self.sources_config:
                self.sources_config[category] = {}

            for subcategory, sources in subcategories.items():
                if subcategory not in self.sources_config[category]:
                    self.sources_config[category][subcategory] = {"sources": []}

                # Добавляем источники
                for source in sources:
                    self.sources_config[category][subcategory]["sources"].append(source)
                    self.stats["added"] += 1
                    self.stats["updated_categories"].add(f"{category}/{subcategory}")

        logger.info(f"Добавлено {self.stats['added']} новых валидных источников")

    def _is_source_exists(self, url: str) -> bool:
        """Проверка, существует ли источник в конфигурации."""
        for category_data in self.sources_config.values():
            if not isinstance(category_data, dict):
                continue

            for subcategory_data in category_data.values():
                if not isinstance(subcategory_data, dict):
                    continue

                sources_list = subcategory_data.get("sources", [])
                for source in sources_list:
                    source_url = ""
                    if isinstance(source, dict):
                        source_url = source.get("url", "")
                    elif isinstance(source, str) and ":" in source:
                        source_url = source.split(":", 1)[1].strip()

                    if source_url == url:
                        return True

        return False

    async def _update_supabase(self):
        """Обновление источников в Supabase."""
        try:
            # get_async_service() can be used here when DB updates are enabled
            # _db_service = get_async_service()
            logger.info("Обновляем источники в Supabase")

            # Здесь можно добавить логику обновления таблицы sources в Supabase
            # Пока что просто логируем
            logger.info("Supabase обновление запланировано")

        except Exception as e:
            logger.error(f"Ошибка обновления Supabase: {e}")

    def _print_summary(self):
        """Вывод итогового отчета."""
        print("\n" + "=" * 60)
        print("📊 ОТЧЕТ ОБНОВЛЕНИЯ RSS-ИСТОЧНИКОВ")
        print("=" * 60)
        print(f"✅ Проверено RSS-фидов: {self.stats['checked']}")
        print(f"⚠️  Удалено неработающих: {self.stats['removed']}")
        print(f"🆕 Добавлено новых: {self.stats['added']}")
        print(f"🗂  Обновлено категорий: {len(self.stats['updated_categories'])}")

        if self.stats["updated_categories"]:
            print("\n📂 Обновленные категории:")
            for category in sorted(self.stats["updated_categories"]):
                print(f"   • {category}")

        print("=" * 60)

        # Сохраняем отчет в лог
        with open("logs/rss_update_summary.log", "w", encoding="utf-8") as f:
            f.write(f"RSS Update Summary - {datetime.now().isoformat()}\n")
            f.write(f"Checked: {self.stats['checked']}\n")
            f.write(f"Removed: {self.stats['removed']}\n")
            f.write(f"Added: {self.stats['added']}\n")
            f.write(f"Updated categories: {len(self.stats['updated_categories'])}\n")
            f.write(f"Categories: {', '.join(sorted(self.stats['updated_categories']))}\n")

    async def run(self):
        """Основной метод обновления RSS-источников."""
        logger.info("🚀 Начинаем обновление RSS-источников")

        try:
            # 1. Проверяем существующие источники
            logger.info("1️⃣ Проверяем существующие RSS-фиды")
            invalid_sources = await self._check_existing_sources()

            # 2. Удаляем невалидные источники
            if invalid_sources:
                logger.info("2️⃣ Удаляем невалидные источники")
                await self._remove_invalid_sources(invalid_sources)
            else:
                logger.info("2️⃣ Все существующие источники валидны")

            # 3. Добавляем новые источники из GitHub
            logger.info("3️⃣ Ищем новые источники в GitHub репозиториях")
            await self._add_new_sources()

            # 4. Обновляем Supabase
            logger.info("4️⃣ Обновляем базу данных")
            await self._update_supabase()

            # 5. Сохраняем обновленную конфигурацию
            logger.info("5️⃣ Сохраняем обновленную конфигурацию")
            await self._save_config()

            # 6. Выводим отчет
            self._print_summary()

            logger.info("✅ Обновление RSS-источников завершено успешно")

        except Exception as e:
            logger.error(f"❌ Ошибка обновления RSS-источников: {e}")
            raise


async def main():
    """Основная функция."""
    # Создаем директорию для логов
    Path("logs").mkdir(exist_ok=True)

    async with RSSUpdater() as updater:
        await updater.run()


if __name__ == "__main__":
    asyncio.run(main())


# === ИЗ validate_rss_sources.py ===

# Shebang retained (secondary block)
"""
Инструмент для валидации RSS источников и поиска рабочих альтернатив.
"""

import sys
from pathlib import Path
import logging
import requests
import feedparser
from urllib.parse import urljoin  # noqa: F401,F811
from concurrent.futures import ThreadPoolExecutor, as_completed
import time  # noqa: F401
from parsers.unified_parser import UnifiedParser
from services.categories import get_all_sources

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, application/atom+xml, text/html, */*",
}


def check_rss_source(url: str, name: str) -> dict:
    """Проверяет один RSS источник."""
    result = {
        "url": url,
        "name": name,
        "status": "unknown",
        "status_code": None,
        "content_type": None,
        "entries_count": 0,
        "error": None,
        "is_valid": False,
    }

    try:
        # Проверяем доступность
        response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        result["status_code"] = response.status_code
        result["content_type"] = response.headers.get("Content-Type", "")

        if response.status_code == 200:
            # Проверяем, является ли это RSS
            content = response.content
            feed = feedparser.parse(content)

            if feed.bozo and not feed.entries:
                result["status"] = "invalid_rss"
                result["error"] = str(feed.bozo_exception)
            elif feed.entries:
                result["status"] = "valid"
                result["entries_count"] = len(feed.entries)
                result["is_valid"] = True
            else:
                result["status"] = "empty"
        else:
            result["status"] = "http_error"
            result["error"] = f"HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["error"] = "Request timeout"
    except requests.exceptions.ConnectionError:
        result["status"] = "connection_error"
        result["error"] = "Connection error"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def find_alternative_rss(base_url: str, name: str) -> list:
    """Пытается найти альтернативные RSS фиды."""
    alternatives = []

    # Типичные пути для RSS фидов
    rss_paths = [
        "/rss",
        "/feed",
        "/feeds",
        "/rss.xml",
        "/feed.xml",
        "/feeds/rss",
        "/feeds/all.rss",
        "/.rss",
        "/news/rss",
        "/blog/rss",
        "/atom.xml",
        "/feeds/atom",
    ]

    try:
        base_domain = f"{base_url.split('://')[0]}://{base_url.split('://')[1].split('/')[0]}"

        for path in rss_paths:
            test_url = base_domain + path
            result = check_rss_source(test_url, f"{name} ({path})")
            if result["is_valid"]:
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
                result["category"] = cat
                result["subcategory"] = subcat
                results.append(result)

                if result["is_valid"]:
                    valid_sources.append(result)
                    print(f"✅ {name}: {result['entries_count']} записей")
                else:
                    invalid_sources.append(result)
                    print(f"❌ {name}: {result['status']} - {result['error']}")

            except Exception as e:
                print(f"❌ Ошибка проверки {name}: {e}")

    # Статистика
    print("\n📊 Результаты валидации:")
    print(f"   ✅ Валидных источников: {len(valid_sources)}")
    print(f"   ❌ Невалидных источников: {len(invalid_sources)}")
    print(f"   📈 Успешность: {len(valid_sources)/(len(valid_sources)+len(invalid_sources))*100:.1f}%")

    # Группировка по статусам
    status_counts = {}
    for result in invalid_sources:
        status = result["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    print("\n🔍 Анализ проблем:")
    for status, count in status_counts.items():
        print(f"   {status}: {count} источников")

    # Поиск альтернатив для неработающих источников
    print("\n🔍 Поиск альтернатив для неработающих источников...")
    alternatives_found = 0

    for result in invalid_sources[:5]:  # Проверяем первые 5 неработающих
        if result["status"] in ["http_error", "connection_error"]:
            print(f"\n🔍 Ищем альтернативы для {result['name']}...")
            alternatives = find_alternative_rss(result["url"], result["name"])

            if alternatives:
                alternatives_found += len(alternatives)
                print(f"   ✅ Найдено {len(alternatives)} альтернатив:")
                for alt in alternatives:
                    print(f"      {alt['url']} - {alt['entries_count']} записей")
            else:
                print("   ❌ Альтернативы не найдены")

    if alternatives_found > 0:
        print(f"\n💡 Всего найдено {alternatives_found} рабочих альтернатив!")

    return results, valid_sources, invalid_sources


def test_parser_with_valid_sources():
    """Тестирует парсер с валидными источниками."""
    print("\n🧪 Тестирование парсера с валидными источниками...")

    # Получаем валидные источники
    results, valid_sources, invalid_sources = validate_all_sources()

    if not valid_sources:
        print("❌ Нет валидных источников для тестирования")
        return

    # Тестируем первые 3 валидных источника
    test_sources = valid_sources[:3]

    parser = UnifiedParser()
    total_news = 0

    for source in test_sources:
        print(f"\n📰 Тестируем: {source['name']}")
        try:
            news_items = parser.parse_source(source["url"], source["category"], source["subcategory"], source["name"])

            if news_items:
                total_news += len(news_items)
                print(f"   ✅ Парсер: {len(news_items)} новостей")

                # Показываем пример
                item = news_items[0]
                print(f"   📝 Пример: {item['title'][:60]}...")
            else:
                print("   ❌ Парсер: нет новостей")

        except Exception as e:
            print(f"   ❌ Ошибка парсера: {e}")

    parser.close()
    print(f"\n📊 Итого новостей от парсера: {total_news}")


if __name__ == "__main__":
    validate_all_sources()
    test_parser_with_valid_sources()

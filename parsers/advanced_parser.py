"""
Module: parsers.advanced_parser
Purpose: Advanced News Parser with AI-powered content extraction
Location: parsers/advanced_parser.py

Description:
    Умный универсальный парсер новостей, который объединяет лучшие решения для извлечения контента.
    Автоматически определяет тип источника (RSS/HTML/API) и применяет каскадную стратегию извлечения.

    ✅ РЕКОМЕНДУЕТСЯ: Основной парсер для production использования

Key Features:
    - Каскадная стратегия извлечения контента (4 уровня fallback)
    - AI-powered фильтрация важности и достоверности
    - Поддержка множественных источников (RSS, HTML, API)
    - Async/await архитектура для высокой производительности
    - Автоматическое определение типа источника
    - Retry logic с exponential backoff

Extraction Strategy (Priority Order):
    1. news-please (приоритет 1) - лучший для большинства сайтов
    2. Fundus (приоритет 2) - специализированный для новостей
    3. trafilatura (fallback) - универсальный extractor
    4. AutoScraper (последний шанс) - когда все остальное не работает

AI Processing:
    - evaluate_importance(): Оценка важности новости (0.1-1.0)
    - evaluate_credibility(): Оценка достоверности источника
    - Фильтрация: сохраняет только релевантные новости

Dependencies:
    External:
        - news-please: News content extraction
        - fundus: News-specific extraction
        - trafilatura: Universal content extraction
        - autoscraper: Fallback extraction
        - httpx: Async HTTP client
    Internal:
        - database.service: Database operations (modern approach)
        - ai_modules.importance: Importance scoring
        - ai_modules.credibility: Credibility scoring
        - config.data.sources: Source configuration

Usage Example:
    ```python
    from parsers.advanced_parser import AdvancedParser

    # Async context manager (recommended)
    async with AdvancedParser() as parser:
        await parser.run()

    # Manual usage
    parser = AdvancedParser()
    await parser._init_session()
    await parser._load_sources_config()
    await parser.run()
    ```

Configuration:
    Sources configuration in `config/data/sources.yaml`:
    ```yaml
    sources:
      - name: "TechCrunch"
        url: "https://techcrunch.com/feed/"
        type: "rss"
        category: "tech"
        enabled: true
    ```

Performance:
    - Async processing для высокой производительности
    - Batch processing источников
    - Connection pooling через httpx
    - Retry logic для надежности

Notes:
    - Использует современный database.service (не legacy db_models)
    - Поддерживает async context manager
    - Автоматически загружает конфигурацию источников
    - Логирует детальную информацию о процессе
    - TODO (Future): Добавить metrics и monitoring (запланировано на Week 3)

Author: PulseAI Team
Last Updated: October 2025
"""

import asyncio
import logging
import time
import random
import hashlib
import warnings
from typing import Dict, List, Optional, Tuple, Any
import yaml
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
import ssl
import feedparser
from newsplease import NewsPlease
import trafilatura
from autoscraper import AutoScraper

# Security imports for Phase 1
from defusedxml import ElementTree as SafeET
from charset_normalizer import from_bytes

# Phase 3: Parsing & Validation imports
from atoma import parse_atom_bytes
from dateutil.parser import parse as parse_date
from dateutil import tz
import validators
from urllib.parse import urljoin
import json

from database.service import get_async_service
from ai_modules.optimized_credibility import evaluate_both_with_optimization
from utils.text.clean_text import clean_text
from parsers.circuit_breaker import CircuitBreaker
from parsers.smart_cache import SmartCache

# Phase 4: Quality & Deduplication imports
from parsers.content_quality import ContentQualityScorer
from parsers.deduplication import NewsDeduplicator

# Phase 5: Browser Parser imports
from parsers.browser_parser import BrowserParser

# Import progress tracking function
try:
    from tools.news.progress_state import update_progress_state as update_progress
except ImportError:
    # Fallback if module not available
    def update_progress(**kwargs):
        pass


# Suppress fake_useragent warnings globally for this module
warnings.filterwarnings("ignore", category=UserWarning, module="fake_useragent")

# User-Agent with fallback
# Initialize logger first for error handling
logger = logging.getLogger(__name__)

try:
    from fake_useragent import UserAgent

    # Configure UserAgent with specific browsers to reduce warnings
    ua = UserAgent(browsers=["chrome", "firefox", "safari"], os=["windows", "macos"])

    def get_user_agent():
        try:
            # Additional suppression during UA generation
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                warnings.filterwarnings("ignore", message=".*fake_useragent.*")
                return ua.random
        except Exception:
            # Fallback if random generation fails
            return "Mozilla/5.0 (compatible; PulseAI/1.0; +https://pulseai.bot)"

except Exception as e:
    logger.debug(f"fake-useragent unavailable: {e}, using fallback")

    # Immutable fallback список реалистичных UA
    FALLBACK_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (compatible; PulseAI/1.0; +https://pulseai.bot)",
    ]

    def get_user_agent():
        return random.choice(FALLBACK_USER_AGENTS)


# Security constants
MAX_RESPONSE_BYTES = 8 * 1024 * 1024  # 8 MB
MAX_XML_DEPTH = 50


class AdvancedParser:
    """Продвинутый асинхронный парсер новостей с AI-фильтрацией."""

    def __init__(
        self,
        max_concurrent: int = 10,
        min_importance: float = 0.3,
        categories: Optional[List[str]] = None,
        subcategories: Optional[List[str]] = None,
    ):
        """
        Инициализация парсера.

        Args:
            max_concurrent: Максимальное количество одновременных запросов
            min_importance: Минимальный порог важности для сохранения новости
            categories: Список категорий для обработки (None = все категории)
            subcategories: Список субкатегорий для обработки (None = все субкатегории)
        """
        self.max_concurrent = max_concurrent
        self.min_importance = min_importance
        self.categories_filter = categories
        self.subcategories_filter = subcategories
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None
        self.sources_config: Dict = {}

        # Phase 1: Security and reliability components
        self.circuit_breaker = CircuitBreaker(fail_threshold=5, cool_down=300)
        self.network_config = {}
        self.rate_limits = {}
        self.parser_config = {}

        # Phase 2: Smart caching with ETag/Last-Modified support
        self.cache = SmartCache()

        # Phase 4: Content quality and deduplication (initialized after config load)
        self.quality_scorer = None
        self.deduplicator = None

        # Phase 5: Browser Parser (initialized on demand)
        self.browser_parser = None

    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход."""
        await self._init_session()
        await self._load_sources_config()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход."""
        await self._close_session()

    async def _init_session(self):
        """Инициализация HTTP сессии с безопасными настройками."""
        # Get timeout settings from config or use defaults
        total_timeout = self.network_config.get("timeout_total", 90)
        connect_timeout = self.network_config.get("timeout_connect", 20)
        read_timeout = self.network_config.get("timeout_read", 60)
        timeout = aiohttp.ClientTimeout(total=total_timeout, connect=connect_timeout, sock_read=read_timeout)
        # Настройка connector с улучшенной обработкой проблемных соединений
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            use_dns_cache=True,
            ttl_dns_cache=300,
            family=0,  # Автоматический выбор IPv4/IPv6
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )

        headers = {
            "User-Agent": get_user_agent(),  # Now uses the safe fallback system
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",  # Removed 'br' to avoid Brotli decoding error
            "Connection": "keep-alive",
            "DNT": "1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

        self.session = aiohttp.ClientSession(timeout=timeout, connector=connector, headers=headers)

    async def _close_session(self):
        """Закрытие HTTP сессии."""
        if self.session:
            await self.session.close()

        # Close Browser Parser if initialized
        if self.browser_parser:
            await self.browser_parser.close()
            self.browser_parser = None

    async def _load_sources_config(self):
        """Загрузка конфигурации источников из YAML."""
        config_path = Path("config/data/sources.yaml")
        if not config_path.exists():
            logger.error("Файл config/sources.yaml не найден")
            self.sources_config = {}
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Separate config sections as per Phase 1 plan
            self.sources_config = config
            self.network_config = config.get("network", {})
            self.rate_limits = config.get("rate_limits", {})
            self.parser_config = config.get("parser", {})

            logger.info(f"Загружена конфигурация из {config_path}")
            logger.info(f"Loaded config: {len(self.rate_limits)} domain-specific rate limits")

            # Initialize Phase 4 components with loaded config
            self._init_phase4_components()

        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            self.sources_config = {}
            self.network_config = {}
            self.rate_limits = {}
            self.parser_config = {}
            # Initialize with defaults
            self._init_phase4_components()

    def _init_phase4_components(self):
        """Инициализация Phase 4 компонентов с конфигурацией"""
        # Initialize Quality Scorer
        self.quality_scorer = ContentQualityScorer()

        # Initialize Deduplicator with config
        simhash_threshold = self.parser_config.get("simhash_threshold", 3)
        minhash_threshold = self.parser_config.get("minhash_threshold", 0.8)
        self.deduplicator = NewsDeduplicator(simhash_threshold=simhash_threshold, minhash_threshold=minhash_threshold)

        logger.info(
            f"Phase 4 components initialized: simhash_threshold={simhash_threshold}, minhash_threshold={minhash_threshold}"
        )

    def _apply_phase4_filters(
        self, title: str, content: str, url: str, category: str, subcategory: str
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Применение Phase 4 фильтров (качество + дедупликация)

        Args:
            title: Заголовок статьи
            content: Содержимое статьи
            url: URL статьи
            category: Категория новости
            subcategory: Подкатегория новости

        Returns:
            Кортеж (should_process, filter_info)
        """
        filter_info = {}

        if not self.quality_scorer or not self.deduplicator:
            return True, filter_info

        # Content quality check
        should_process, quality_info = self.quality_scorer.should_process_content(
            title, content, url, self.parser_config.get("min_content_quality", 0.4)
        )
        filter_info["quality_info"] = quality_info

        if not should_process:
            logger.debug(
                f"[{category}/{subcategory}] {title} -> SKIP (quality: {quality_info['score']:.2f}, issues: {quality_info['issues']})"
            )
            return False, filter_info

        # Generate unique ID for deduplication
        news_id = hashlib.md5(f"{title}_{url}_{category}".encode()).hexdigest()

        # Check for duplicates
        duplicate_check = self.deduplicator.add_news_item(news_id, title, content, url)
        filter_info["duplicate_check"] = duplicate_check

        if duplicate_check["is_duplicate"]:
            logger.debug(
                f"[{category}/{subcategory}] {title} -> SKIP (duplicate: {duplicate_check['duplicate_type']}, similarity: {duplicate_check['similarity_score']:.2f})"
            )
            return False, filter_info

        return True, filter_info

    async def _init_browser_parser(self) -> BrowserParser:
        """
        Инициализация Browser Parser по требованию

        Returns:
            Инициализированный BrowserParser
        """
        if not self.browser_parser:
            headless = self.parser_config.get("browser_headless", True)
            timeout = self.parser_config.get("browser_timeout", 30000)
            self.browser_parser = BrowserParser(headless=headless, timeout=timeout)
            await self.browser_parser._init_browser()
            logger.info("Browser Parser initialized")

        return self.browser_parser

    def _should_use_browser_parser(self, url: str) -> bool:
        """
        Определение нужен ли Browser Parser для URL

        Args:
            url: URL для проверки

        Returns:
            True если нужен Browser Parser
        """
        try:
            from urllib.parse import urlparse

            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()

            # Check against configured patterns
            browser_patterns = self.parser_config.get("browser_fallback_patterns", [])
            for pattern in browser_patterns:
                if pattern.startswith("*."):
                    base_domain = pattern[2:]  # Remove "*."
                    if domain.endswith(base_domain):
                        return True
                elif pattern in domain:
                    return True

            # Common domains that often need browser parsing
            browser_domains = [
                "medium.com",
                "substack.com",
                "dev.to",
                "hashnode.com",
                "wordpress.com",
                "blogspot.com",
                "tumblr.com",
            ]

            return any(domain.endswith(bd) for bd in browser_domains)

        except Exception as e:
            logger.debug(f"Error checking browser parser requirement: {e}")
            return False

    async def _parse_with_browser_fallback(
        self, url: str, category: str, subcategory: str, name: str
    ) -> Dict[str, Any]:
        """
        Fallback парсинг с использованием браузера для сложных источников

        Args:
            url: URL для парсинга
            category: Категория новости
            subcategory: Подкатегория новости
            name: Название источника

        Returns:
            Результат парсинга в стандартном формате
        """
        try:
            browser_parser = await self._init_browser_parser()

            # Parse page with browser
            result = await browser_parser.parse_page(url, enable_js=True)

            if not result["success"]:
                return {
                    "success": False,
                    "reason": f"browser_parse_failed: {result.get('error', 'unknown')}",
                    "processed": 0,
                    "saved": 0,
                }

            # Extract content
            title = result.get("title", "").strip()
            content = result.get("content", "").strip()

            if not title or not content:
                return {"success": False, "reason": "no_content_extracted", "processed": 0, "saved": 0}

            # Apply Phase 4 filters
            should_process, filter_info = self._apply_phase4_filters(title, content, url, category, subcategory)
            if not should_process:
                return {"success": True, "reason": "filtered_by_quality_or_duplicate", "processed": 1, "saved": 0}

            # AI evaluation
            text_for_ai = f"{title} {content}".strip()
            importance, credibility = evaluate_both_with_optimization(
                {"title": title, "content": text_for_ai, "category": category}
            )

            if importance < self.min_importance:
                return {"success": True, "reason": "low_importance", "processed": 1, "saved": 0}

            # Save to database
            news_item = {
                "title": title,
                "content": content,
                "link": url,
                "source": name,
                "category": category,
                "subcategory": subcategory,
                "importance": importance,
                "credibility": credibility,
                "published_at": None,
            }

            db_service = get_async_service()
            await db_service.async_upsert_news([news_item])

            return {"success": True, "processed": 1, "saved": 1, "method": "browser_parser"}

        except Exception as e:
            logger.error(f"Browser fallback parsing failed for {url}: {e}")
            return {"success": False, "reason": f"browser_fallback_error: {e}", "processed": 0, "saved": 0}

    def safe_parse_xml(self, xml_bytes: bytes):
        """
        Безопасный XML парсер:
        - Блокирует DTD/ENTITY (XXE атаки)
        - Ограничивает глубину (XML bomb)
        - Ограничивает размер
        """
        if len(xml_bytes) > MAX_RESPONSE_BYTES:
            raise ValueError("XML too large")

        # defusedxml автоматически блокирует внешние сущности
        tree = SafeET.fromstring(xml_bytes)

        # Проверка глубины
        def check_depth(elem, depth=0):
            if depth > MAX_XML_DEPTH:
                raise ValueError("XML too deep")
            for child in elem:
                check_depth(child, depth + 1)

        check_depth(tree)
        return tree

    def smart_decode(self, content: bytes) -> str:
        """
        Умное определение кодировки через charset-normalizer
        (стабильнее чем chardet)
        """
        result = from_bytes(content).best()
        return str(result) if result else content.decode("utf-8", "ignore")

    def _backoff_with_jitter(self, base: float, factor: float, attempt: int) -> float:
        """
        Экспоненциальный backoff с jitter для предотвращения
        "thundering herd" проблемы.

        Jitter рандомизирует задержку: 80-120% от базовой.
        """
        delay = base * (factor**attempt)
        jitter = random.uniform(0.8, 1.2)
        return delay * jitter

    # Phase 3: Parsing & Validation methods
    def _validate_feed_url(self, url: str) -> bool:
        """Валидация URL фида"""
        try:
            return validators.url(url) and url.startswith(("http://", "https://"))
        except Exception:
            return False

    def _detect_feed_type(self, content: bytes, content_type: str) -> str:
        """
        Определение типа фида по контенту и headers

        Returns:
            'rss', 'atom', 'json', 'wordpress_api', 'html' или 'unknown'
        """
        content_str = content.decode("utf-8", errors="ignore").lower()

        # WordPress REST API detection
        if "application/json" in content_type or content_str.strip().startswith("["):
            try:
                data = json.loads(content.decode("utf-8", errors="ignore"))
                # Check if it's WordPress API format
                if isinstance(data, list) and len(data) > 0 and "title" in data[0] and "content" in data[0]:
                    return "wordpress_api"
                return "json"
            except (json.JSONDecodeError, (KeyError, IndexError)):
                pass

        # RSS detection
        if (
            "<rss" in content_str
            or "<feed" in content_str
            or "application/rss" in content_type
            or "application/atom" in content_type
        ):
            if 'xmlns="http://www.w3.org/2005/atom"' in content_str or "<feed" in content_str:
                return "atom"
            return "rss"

        # Fallback to HTML
        if "<html" in content_str or "text/html" in content_type:
            return "html"

        return "unknown"

    def _normalize_date(self, date_str: str) -> Optional[str]:
        """
        Нормализация даты в ISO format с timezone

        Args:
            date_str: Строка даты в любом формате

        Returns:
            ISO дата или None если не удалось парсить
        """
        if not date_str:
            return None

        try:
            # Parse with dateutil (handles many formats)
            parsed = parse_date(date_str)

            # Ensure timezone awareness
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=tz.UTC)

            return parsed.isoformat()

        except Exception as e:
            logger.debug(f"Failed to parse date '{date_str}': {e}")
            return None

    def _make_absolute_url(self, url: str, base_url: str) -> str:
        """Преобразование относительных URL в абсолютные"""
        if not url:
            return ""

        try:
            # If already absolute, return as-is
            if urlparse(url).netloc:
                return url

            # Make absolute using base_url
            return urljoin(base_url, url)
        except Exception as e:
            logger.debug(f"Failed to make absolute URL from '{url}', base '{base_url}': {e}")
            return url

    def _extract_feed_links(self, html_content: str, base_url: str) -> List[str]:
        """
        Автообнаружение RSS/Atom ссылок в HTML

        Args:
            html_content: HTML контент страницы
            base_url: Базовый URL для относительных ссылок

        Returns:
            Список найденных feed URL
        """
        feed_urls = []

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, "html.parser")

            # Look for RSS/Atom link tags
            for link in soup.find_all("link", href=True):
                rel = link.get("rel", [])
                if isinstance(rel, str):
                    rel = [rel]

                # Check for RSS/Atom types
                if any(r in ["alternate", "feed"] for r in rel):
                    type_attr = link.get("type", "").lower()
                    if any(t in type_attr for t in ["rss", "atom", "xml"]):
                        feed_url = self._make_absolute_url(link["href"], base_url)
                        if self._validate_feed_url(feed_url):
                            feed_urls.append(feed_url)

        except ImportError:
            logger.debug("BeautifulSoup not available for feed discovery")
        except Exception as e:
            logger.debug(f"Error discovering feeds: {e}")

        return feed_urls

    def _parse_json_feed(self, content: bytes, base_url: str) -> Dict[str, Any]:
        """
        Парсинг JSON Feed (JSON Feed format)

        Args:
            content: Содержимое JSON фида
            base_url: Базовый URL для относительных ссылок

        Returns:
            Словарь с parsed feed данными
        """
        try:
            feed_data = json.loads(content.decode("utf-8"))

            # Extract basic feed info
            feed_info = {
                "title": feed_data.get("title", ""),
                "description": feed_data.get("description", ""),
                "home_page_url": feed_data.get("home_page_url", base_url),
                "feed_url": feed_data.get("feed_url", base_url),
            }

            items = []
            for item in feed_data.get("items", []):
                # Extract item data with normalization
                item_data = {
                    "title": item.get("title", ""),
                    "url": self._make_absolute_url(item.get("url", ""), base_url),
                    "content_html": item.get("content_html", ""),
                    "content_text": item.get("content_text", ""),
                    "summary": item.get("summary", ""),
                    "date_published": self._normalize_date(item.get("date_published")),
                    "date_modified": self._normalize_date(item.get("date_modified")),
                    "external_url": self._make_absolute_url(item.get("external_url", ""), base_url),
                }

                # Validate required fields
                if item_data["title"] and item_data["url"]:
                    items.append(item_data)

            return {"feed": feed_info, "items": items, "type": "json"}

        except Exception as e:
            logger.error(f"JSON Feed parsing failed: {e}")
            return {"feed": {}, "items": [], "type": "json", "error": str(e)}

    def _parse_wordpress_api(self, content: bytes, base_url: str) -> Dict[str, Any]:
        """
        Парсинг WordPress REST API (/wp-json/wp/v2/posts)

        Args:
            content: Содержимое JSON API ответа
            base_url: Базовый URL для относительных ссылок

        Returns:
            Словарь с parsed данными в стандартном формате
        """
        try:
            posts = json.loads(content.decode("utf-8"))

            if not isinstance(posts, list):
                return {"feed": {}, "items": [], "type": "wordpress_api", "error": "not_a_list"}

            items = []
            for post in posts:
                # Extract WordPress post data
                title = post.get("title", {})
                if isinstance(title, dict):
                    title = title.get("rendered", "")

                content_data = post.get("content", {})
                if isinstance(content_data, dict):
                    content_html = content_data.get("rendered", "")
                else:
                    content_html = ""

                excerpt_data = post.get("excerpt", {})
                if isinstance(excerpt_data, dict):
                    excerpt = excerpt_data.get("rendered", "")
                else:
                    excerpt = ""

                item_data = {
                    "title": title,
                    "url": post.get("link", ""),
                    "content_html": content_html,
                    "content_text": "",
                    "summary": excerpt,
                    "date_published": self._normalize_date(post.get("date")),
                }

                if item_data["title"] and item_data["url"]:
                    items.append(item_data)

            return {
                "feed": {"title": "WordPress API", "home_page_url": base_url},
                "items": items,
                "type": "wordpress_api",
            }

        except Exception as e:
            logger.error(f"WordPress API parsing failed: {e}")
            return {"feed": {}, "items": [], "type": "wordpress_api", "error": str(e)}

    def _parse_atom_feed(self, content: bytes, base_url: str) -> Dict[str, Any]:
        """
        Парсинг Atom фидов с помощью atoma

        Args:
            content: Содержимое Atom фида
            base_url: Базовый URL для относительных ссылок

        Returns:
            Словарь с parsed feed данными
        """
        try:
            feed = parse_atom_bytes(content)

            # Extract feed info
            feed_info = {
                "title": feed.title.value if hasattr(feed.title, "value") else str(feed.title),
                "description": getattr(feed.subtitle, "value", "") if hasattr(feed, "subtitle") else "",
                "home_page_url": base_url,
                "feed_url": base_url,
            }

            items = []
            for entry in feed.entries:
                # Extract entry data
                title = entry.title.value if hasattr(entry.title, "value") else str(entry.title)

                # Get content (prefer content over summary)
                content_html = ""
                content_text = ""
                if hasattr(entry, "content") and entry.content:
                    if hasattr(entry.content, "value"):
                        content_html = entry.content.value
                    else:
                        content_html = str(entry.content)

                if hasattr(entry, "summary") and entry.summary and not content_html:
                    content_html = entry.summary.value if hasattr(entry.summary, "value") else str(entry.summary)

                # Extract links for URL
                url = base_url
                if hasattr(entry, "links") and entry.links:
                    for link in entry.links:
                        if link.rel == "alternate" or not link.rel:
                            url = self._make_absolute_url(link.href, base_url)
                            break

                # Normalize dates
                published = None
                if hasattr(entry, "published") and entry.published:
                    published = self._normalize_date(entry.published.isoformat())

                if not published and hasattr(entry, "updated") and entry.updated:
                    published = self._normalize_date(entry.updated.isoformat())

                item_data = {
                    "title": title,
                    "url": url,
                    "content_html": content_html,
                    "content_text": content_text,
                    "summary": content_html,  # Use content as summary if no separate summary
                    "date_published": published,
                }

                if item_data["title"] and item_data["url"]:
                    items.append(item_data)

            return {"feed": feed_info, "items": items, "type": "atom"}

        except Exception as e:
            logger.error(f"Atom Feed parsing failed: {e}")
            return {"feed": {}, "items": [], "type": "atom", "error": str(e)}

    def _get_all_sources(self) -> List[Tuple[str, str, str, str]]:
        """
        Извлекает все источники из конфигурации.

        Returns:
            Список кортежей (category, subcategory, name, url)
        """
        sources = []

        if not self.sources_config:
            return sources

        for category, category_data in self.sources_config.items():
            if not isinstance(category_data, dict):
                continue

            # Применяем фильтр категорий если задан
            if self.categories_filter and category not in self.categories_filter:
                continue

            for subcategory, subcategory_data in category_data.items():
                if not isinstance(subcategory_data, dict):
                    continue

                # Применяем фильтр субкатегорий если задан
                if self.subcategories_filter and subcategory not in self.subcategories_filter:
                    continue

                sources_list = subcategory_data.get("sources", [])
                for source in sources_list:
                    if isinstance(source, dict):
                        name = source.get("name", "")
                        url = source.get("url", "")
                        if name and url:
                            sources.append((category, subcategory, name, url))
                    elif isinstance(source, str):
                        # Простой формат: "Name: URL"
                        if ":" in source:
                            name, url = source.split(":", 1)
                            sources.append((category, subcategory, name.strip(), url.strip()))

        return sources

    def get_total_sources_count(self) -> int:
        """
        Возвращает общее количество источников для отслеживания прогресса.

        Returns:
            Количество источников для парсинга
        """
        return len(self._get_all_sources())

    async def _fetch_content_safe(self, url: str) -> Tuple[bool, str, Optional[bytes]]:
        """
        Безопасная загрузка контента с ограничением размера.

        Args:
            url: URL для загрузки

        Returns:
            Кортеж (success, content_type, content_bytes)
        """
        return await self._fetch_with_conditional(url)

    async def _fetch_with_conditional(self, url: str) -> Tuple[bool, str, Optional[bytes]]:
        """
        Fetch с поддержкой HTTP 304 Not Modified и кэширования

        Workflow:
        1. Проверить свежий кэш (< 6 часов) -> вернуть
        2. Если кэша нет или устарел:
           - Добавить If-None-Match / If-Modified-Since
           - Если 304 -> взять из кэша
           - Если 200 -> обновить кэш + метаданные
        3. Если ошибка -> попробовать stale cache
        """

        # Stage 1: Свежий кэш
        cached = self.cache.get_feed(url, max_age_hours=6)
        if cached:
            return True, "text/xml", cached

        # Stage 2: Conditional request
        headers = {
            "User-Agent": get_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # Добавить conditional headers
        headers.update(self.cache.get_conditional_headers(url))

        try:
            async with self.session.get(url, headers=headers, allow_redirects=True) as resp:
                # HTTP 304 Not Modified - контент не изменился
                if resp.status == 304:
                    logger.info(f"304 Not Modified: {url}")
                    stale = self.cache.get_stale(url)
                    if stale:
                        return True, "text/xml", stale
                    else:
                        logger.error(f"304 but no stale cache for {url}")
                        return False, None, None

                # HTTP 200 OK - новый контент
                if resp.status == 200:
                    chunks, size = [], 0
                    max_bytes = self.network_config.get("max_response_bytes", MAX_RESPONSE_BYTES)

                    async for chunk in resp.content.iter_chunked(65536):
                        size += len(chunk)
                        if size > max_bytes:
                            logger.warning(f"Response too large: {url} ({size} bytes)")
                            raise ValueError(f"Response exceeds {max_bytes} bytes")
                        chunks.append(chunk)

                    content_bytes = b"".join(chunks)

                    # Сохранить с метаданными
                    etag = resp.headers.get("ETag")
                    last_modified = resp.headers.get("Last-Modified")
                    self.cache.save_feed_with_meta(url, content_bytes, etag, last_modified)

                    content_type = resp.headers.get("Content-Type", "text/xml")
                    return True, content_type, content_bytes

                # Другие статусы - ошибка
                logger.warning(f"HTTP {resp.status} для {url}")
                return False, None, None

        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")

            # Stage 3: Stale cache fallback
            stale = self.cache.get_stale(url)
            if stale:
                return True, "text/xml", stale

            return False, None, None

    async def _fetch_content(self, url: str) -> Tuple[bool, str, Optional[bytes]]:
        """
        Асинхронная загрузка контента по URL.
        Now uses safe fetch method.

        Args:
            url: URL для загрузки

        Returns:
            Кортеж (success, content_type, content_bytes)
        """
        return await self._fetch_content_safe(url)

    async def _fetch_content_with_retry(self, url: str, max_retries: int = 3) -> Tuple[bool, str, Optional[bytes]]:
        """
        Загрузка контента с retry, circuit breaker и adaptive backoff.

        Args:
            url: URL для загрузки
            max_retries: Максимальное количество попыток (по умолчанию 3)

        Returns:
            Кортеж (success, content_type, content_bytes)
        """
        domain = urlparse(url).netloc

        # Адаптивные retry для проблемных доменов
        problematic_domains = ["espn.com", "mlb.com", "nhl.com", "lolesports.com", "feeds.reuters.com"]
        if domain in problematic_domains:
            max_retries = max(max_retries, 5)  # Минимум 5 попыток для проблемных доменов

        for attempt in range(max_retries):
            # Circuit breaker check
            if not self.circuit_breaker.allow(domain):
                logger.debug(f"Domain {domain} blocked by circuit breaker")
                return False, None, None

            try:
                success, content_type, content = await self._fetch_content(url)

                if success:
                    if attempt > 0:
                        logger.info(f"Успешно загружено с попытки {attempt + 1}: {url}")
                    self.circuit_breaker.report(domain, True)
                    return success, content_type, content

                # Retry-able статусы
                if content_type in [429, 502, 503, 504]:
                    raise aiohttp.ClientError(f"HTTP {content_type}")

            except (aiohttp.ClientTimeout, aiohttp.ClientConnectionError, aiohttp.ClientError, ssl.SSLError) as e:
                error_type = type(e).__name__
                error_msg = str(e)

                # Логируем специфичные SSL ошибки для диагностики
                if isinstance(e, ssl.SSLError):
                    logger.debug(f"SSL error for {url}: {error_msg}")
                elif "nodename nor servname provided" in error_msg:
                    logger.debug(f"DNS resolution error for {url}: {error_msg}")

                if attempt < max_retries - 1:
                    wait = self._backoff_with_jitter(1.0, 2.0, attempt)
                    # Увеличиваем время ожидания для SSL ошибок
                    if isinstance(e, ssl.SSLError):
                        wait *= 1.5
                    logger.debug(
                        f"Retry {attempt+1}/{max_retries} for {url} after {wait:.2f}s ({error_type}): {error_msg}"
                    )
                    await asyncio.sleep(wait)
                else:
                    logger.error(f"Failed after {max_retries} attempts ({error_type}): {url} - {error_msg}")
                    self.circuit_breaker.report(domain, False)
                    return False, None, None

            except Exception as e:
                logger.error(f"Unexpected error for {url}: {e}")
                self.circuit_breaker.report(domain, False)
                return False, None, None

        return False, None, None

    def _extract_with_newsplease(self, url: str, content: bytes) -> Optional[Dict[str, str]]:
        """
        Извлечение контента с помощью news-please.

        Args:
            url: URL страницы
            content: HTML контент

        Returns:
            Словарь с title и maintext или None
        """
        # Сначала пробуем from_url (правильный способ для NewsPlease)
        try:
            article = NewsPlease.from_url(url, timeout=30)
            if article and article.maintext:
                return {
                    "title": clean_text(article.title or ""),
                    "maintext": clean_text(article.maintext),
                    "method": "newsplease_url",
                }
        except Exception as e:
            logger.debug(f"newsplease from_url failed for {url}: {e}")

        # Fallback на from_html если URL не сработал
        try:
            content_str = content.decode("utf-8", errors="ignore")
            article = NewsPlease.from_html(content_str, url=url)

            if article and article.maintext:
                return {
                    "title": clean_text(article.title or ""),
                    "maintext": clean_text(article.maintext),
                    "method": "newsplease_html",
                }
        except Exception as e:
            logger.debug(f"newsplease from_html failed for {url}: {e}")

        return None

    def _extract_with_trafilatura(self, url: str, content: bytes) -> Optional[Dict[str, str]]:
        """
        Извлечение контента с помощью trafilatura.

        Args:
            url: URL страницы
            content: HTML контент

        Returns:
            Словарь с title и maintext или None
        """
        try:
            html_content = content.decode("utf-8", errors="ignore")

            # Извлекаем основной текст
            maintext = trafilatura.extract(html_content)

            # Извлекаем заголовок
            title = trafilatura.extract_metadata(html_content).get("title", "")

            if maintext and len(maintext.strip()) > 100:  # Минимальная длина текста
                return {
                    "title": clean_text(title) if title else "Untitled",
                    "maintext": clean_text(maintext),
                    "method": "trafilatura",
                }

        except Exception as e:
            logger.debug(f"trafilatura failed for {url}: {e}")

        return None

    def _extract_with_autoscraper(self, url: str, content: bytes) -> Optional[Dict[str, str]]:
        """
        Извлечение контента с помощью AutoScraper.

        Args:
            url: URL страницы
            content: HTML контент

        Returns:
            Словарь с title и maintext или None
        """
        try:
            html_content = content.decode("utf-8", errors="ignore")

            # Пытаемся найти заголовок и текст с помощью AutoScraper
            scraper = AutoScraper()

            # Простые правила для извлечения
            rules = [{"title": ["h1", "h2", "title"]}, {"content": ["p", "div", "article"]}]

            for rule in rules:
                try:
                    result = scraper.build(html_content, rule)
                    if result:
                        title = ""
                        maintext = ""

                        if "title" in result and result["title"]:
                            title = (
                                str(result["title"][0]) if isinstance(result["title"], list) else str(result["title"])
                            )

                        if "content" in result and result["content"]:
                            if isinstance(result["content"], list):
                                # Первые 5 элементов
                                maintext = " ".join([str(item) for item in result["content"][:5]])
                            else:
                                maintext = str(result["content"])

                        if maintext and len(maintext.strip()) > 100:
                            return {
                                "title": clean_text(title) if title else "Untitled",
                                "maintext": clean_text(maintext),
                                "method": "autoscraper",
                            }

                except Exception as e:
                    logger.debug(f"AutoScraper rule failed: {e}")
                    continue

        except Exception as e:
            logger.debug(f"autoscraper failed for {url}: {e}")

        return None

    def _extract_content_cascade(self, url: str, content: bytes) -> Optional[Dict[str, str]]:
        """
        Каскадное извлечение контента с приоритетами.

        Args:
            url: URL страницы
            content: HTML контент

        Returns:
            Словарь с title и maintext или None
        """
        # Приоритет 1: news-please
        result = self._extract_with_newsplease(url, content)
        if result:
            return result

        # Приоритет 2: trafilatura (fundus требует сложной настройки)
        result = self._extract_with_trafilatura(url, content)
        if result:
            return result

        # Приоритет 3: AutoScraper
        result = self._extract_with_autoscraper(url, content)
        if result:
            return result

        logger.warning(f"Не удалось извлечь контент из {url}")
        return None

    async def _process_source(self, category: str, subcategory: str, name: str, url: str) -> Dict[str, Any]:
        """
        Обработка одного источника новостей.

        Args:
            category: Категория новости
            subcategory: Подкатегория новости
            name: Название источника
            url: URL источника

        Returns:
            Словарь с результатами обработки
        """
        start_time = time.time()

        async with self.semaphore:
            try:
                # Обновляем текущий источник
                print(f"DEBUG: Calling update_progress with current_source={category}/{subcategory}: {name}")
                update_progress(current_source=f"{category}/{subcategory}: {name}")
                logger.info(f"[{category}/{subcategory}] {url} -> START")

                # Phase 5: Check if URL needs browser parsing
                if self.parser_config.get("enable_browser_fallback", True) and self._should_use_browser_parser(url):
                    logger.info(f"[{category}/{subcategory}] {url} -> Using browser parser")
                    return await self._parse_with_browser_fallback(url, category, subcategory, name)

                # Загружаем контент с retry механизмом (увеличены попытки для проблемных источников)
                problematic_domains = ["espn.com", "mlb.com", "nhl.com", "lolesports.com", "feeds.reuters.com"]
                max_retries = 5 if any(domain in url for domain in problematic_domains) else 3
                success, content_type, content = await self._fetch_content_with_retry(url, max_retries=max_retries)
                if not success or not content:
                    logger.warning(f"[{category}/{subcategory}] {url} -> FAIL (fetch)")

                    # Phase 5: Browser fallback for failed HTTP requests
                    if self.parser_config.get("enable_browser_fallback", True):
                        logger.info(f"[{category}/{subcategory}] {url} -> Trying browser fallback")
                        result = await self._parse_with_browser_fallback(url, category, subcategory, name)
                        # Обновляем прогресс даже при fallback
                        if result:
                            update_progress(sources_processed_delta=1)
                        return result

                    # Обновляем прогресс при неуспешной загрузке
                    update_progress(
                        sources_processed_delta=1,
                        error={"source": name, "error_type": "fetch_failed", "message": "Failed to fetch content"},
                    )
                    return {"success": False, "reason": "fetch_failed"}

                # Phase 3: Enhanced feed type detection and validation
                feed_type = self._detect_feed_type(content, content_type)

                # Validate URL if it's supposed to be a feed
                if not self._validate_feed_url(url):
                    logger.warning(f"Invalid feed URL: {url}")

                # Обрабатываем источник в зависимости от типа
                result = None
                if feed_type == "wordpress_api":
                    # WordPress REST API processing
                    result = await self._process_wordpress_api_source(category, subcategory, name, url, content)
                elif feed_type == "json":
                    # JSON Feed processing
                    result = await self._process_json_source(category, subcategory, name, url, content)
                elif feed_type in ["rss", "atom", "xml"]:
                    # RSS/Atom XML source
                    result = await self._process_rss_source(category, subcategory, name, url, content, feed_type)
                elif feed_type == "html":
                    # HTML source - try to discover feeds first
                    result = await self._process_html_source(category, subcategory, name, url, content)
                else:
                    logger.warning(f"Unknown feed type '{feed_type}' for {url}, trying HTML processing")
                    result = await self._process_html_source(category, subcategory, name, url, content)

                # Обновляем прогресс после обработки (если методы обработки источников не делают это)
                if result and result.get("success"):
                    # Обновляем только если не было обновления в специфичных методах
                    pass  # Обновление уже происходит в методах обработки
                elif result and not result.get("success"):
                    # Обновляем при неуспешной обработке
                    update_progress(sources_processed_delta=1)

                return result

            except Exception as e:
                logger.error(f"[{category}/{subcategory}] {url} -> ERROR: {e}")
                # Обновляем прогресс при ошибке
                update_progress(
                    sources_processed_delta=1,
                    current_source=f"{category}/{subcategory}",
                    error={"source": name, "error_type": "processing_error", "message": str(e)},
                )
                return {"success": False, "reason": str(e)}
            finally:
                elapsed = time.time() - start_time
                logger.debug(f"[{category}/{subcategory}] {url} -> completed in {elapsed:.2f}s")

    async def _process_rss_source(
        self, category: str, subcategory: str, name: str, url: str, content: bytes, feed_type: str = "rss"
    ) -> Dict[str, Any]:
        """Обработка RSS/Atom источника с безопасным парсингом."""
        try:
            # Phase 3: Try specialized parsers first for better accuracy
            parsed_data = None

            if feed_type == "atom":
                # Use dedicated Atom parser
                parsed_data = self._parse_atom_feed(content, url)
            else:
                # Fallback to feedparser for RSS and general XML
                try:
                    content_str = self.smart_decode(content)
                    feed = feedparser.parse(content_str)

                    # Validate XML safely if needed
                    if feed.bozo and "xml" in content_str[:100].lower():
                        try:
                            self.safe_parse_xml(content)
                        except Exception as e:
                            logger.debug(f"XML validation failed but proceeding: {e}")

                    parsed_data = {
                        "feed": {
                            "title": getattr(feed.feed, "title", ""),
                            "description": getattr(feed.feed, "description", ""),
                            "home_page_url": getattr(feed.feed, "link", url),
                            "feed_url": url,
                        },
                        "items": [],
                        "type": "rss",
                    }

                    # Convert feedparser entries to standard format
                    for entry in feed.entries:
                        item_data = {
                            "title": entry.get("title", ""),
                            "url": entry.get("link", ""),
                            "content_html": "",
                            "content_text": "",
                            "summary": entry.get("description", entry.get("summary", "")),
                            "date_published": None,
                        }

                        # Extract content
                        if hasattr(entry, "content") and entry.content:
                            item_data["content_html"] = entry.content[0].value if entry.content else ""
                        elif hasattr(entry, "description"):
                            item_data["content_html"] = entry.description

                        # Extract and normalize date
                        if hasattr(entry, "published"):
                            item_data["date_published"] = self._normalize_date(entry.published)
                        elif hasattr(entry, "updated"):
                            item_data["date_published"] = self._normalize_date(entry.updated)

                        parsed_data["items"].append(item_data)

                except Exception as e:
                    logger.debug(f"Feedparser failed, using fallback: {e}")
                    content_str = content.decode("utf-8", errors="ignore")
                    feed = feedparser.parse(content_str)
                    parsed_data = {"feed": {}, "items": [], "type": "rss"}

            # Process parsed feed data
            if not parsed_data or not parsed_data.get("items"):
                return {"success": False, "reason": "no_entries"}

            processed_count = 0
            saved_count = 0

            # Process items from parsed_data (works for both RSS and Atom)
            max_entries = getattr(self, "max_rss_entries", 50)
            items = parsed_data.get("items", [])[:max_entries]

            for item_data in items:
                try:
                    # Extract and clean data
                    title = clean_text(item_data.get("title", ""))
                    item_url = self._make_absolute_url(item_data.get("url", ""), url)

                    if not title:
                        continue

                    # Phase 3: Get content with proper normalization
                    content_html = item_data.get("content_html", "")
                    content_text = item_data.get("content_text", "")
                    summary = item_data.get("summary", "")

                    # Use best available content
                    article_content = content_html or content_text or summary or ""
                    article_content = clean_text(article_content)

                    # Phase 3: Normalized date handling
                    pub_date = None
                    date_str = item_data.get("date_published")
                    if date_str:
                        pub_date = self._normalize_date(date_str)

                    processed_count += 1

                    # Phase 4: Apply quality and deduplication filters
                    should_process, filter_info = self._apply_phase4_filters(
                        title, article_content, item_url, category, subcategory
                    )
                    if not should_process:
                        continue

                    # Оценка важности и достоверности
                    text_for_ai = f"{title} {article_content}".strip()
                    if not text_for_ai:
                        continue

                    # Используем объединённую функцию для экономии API запросов
                    importance, credibility = evaluate_both_with_optimization(
                        {"title": title, "content": text_for_ai, "category": category}
                    )

                    if importance < self.min_importance:
                        logger.debug(f"[{category}/{subcategory}] {title} -> SKIP (importance: {importance:.2f})")
                        continue

                    # Сохраняем в БД
                    news_item = {
                        "title": title,
                        "content": article_content,
                        "link": item_url,
                        "source": name,
                        "category": category,
                        "subcategory": subcategory,
                        "importance": importance,
                        "credibility": credibility,
                        "published_at": pub_date,
                    }

                    # Используем асинхронный сервис БД
                    db_service = get_async_service()
                    await db_service.async_upsert_news([news_item])
                    saved_count += 1

                    logger.debug(f"[{category}/{subcategory}] {title} -> SAVED (importance: {importance:.2f})")

                except Exception as e:
                    logger.error(f"Ошибка обработки feed записи: {e}")
                    continue

            # Обновляем прогресс с результатами обработки источника
            update_progress(
                sources_processed_delta=1,
                news_found_delta=processed_count,
                news_saved_delta=saved_count,
                news_filtered_delta=processed_count - saved_count,
                source_stats={"name": name, "news_count": saved_count, "time_ms": 1000},  # Примерное время обработки
                category=category,
            )

            return {
                "success": True,
                "processed": processed_count,
                "saved": saved_count,
                "type": parsed_data.get("type", "rss"),
            }

        except Exception as e:
            return {"success": False, "reason": f"rss_parse_error: {e}"}

    async def _process_json_source(
        self, category: str, subcategory: str, name: str, url: str, content: bytes
    ) -> Dict[str, Any]:
        """Обработка JSON Feed источника."""
        try:
            # Parse JSON feed using dedicated parser
            parsed_data = self._parse_json_feed(content, url)

            if not parsed_data or not parsed_data.get("items"):
                return {"success": False, "reason": "no_entries"}

            if parsed_data.get("error"):
                logger.error(f"JSON Feed parsing error: {parsed_data['error']}")
                return {"success": False, "reason": f"json_parse_error: {parsed_data['error']}"}

            processed_count = 0
            saved_count = 0

            # Process items from JSON feed
            max_entries = getattr(self, "max_rss_entries", 50)
            items = parsed_data.get("items", [])[:max_entries]

            for item_data in items:
                try:
                    # Extract and clean data
                    title = clean_text(item_data.get("title", ""))
                    item_url = self._make_absolute_url(item_data.get("url", ""), url)

                    if not title:
                        continue

                    # Phase 3: Get content with proper normalization
                    content_html = item_data.get("content_html", "")
                    content_text = item_data.get("content_text", "")
                    summary = item_data.get("summary", "")

                    # Use best available content
                    article_content = content_html or content_text or summary or ""
                    article_content = clean_text(article_content)

                    # Phase 3: Normalized date handling
                    pub_date = None
                    date_str = item_data.get("date_published")
                    if date_str:
                        pub_date = self._normalize_date(date_str)

                    processed_count += 1

                    # Phase 4: Apply quality and deduplication filters
                    should_process, filter_info = self._apply_phase4_filters(
                        title, article_content, item_url, category, subcategory
                    )
                    if not should_process:
                        continue

                    # Оценка важности и достоверности
                    text_for_ai = f"{title} {article_content}".strip()
                    if not text_for_ai:
                        continue

                    # Используем объединённую функцию для экономии API запросов
                    importance, credibility = evaluate_both_with_optimization(
                        {"title": title, "content": text_for_ai, "category": category}
                    )

                    if importance < self.min_importance:
                        logger.debug(f"[{category}/{subcategory}] {title} -> SKIP (importance: {importance:.2f})")
                        continue

                    # Сохраняем в БД
                    news_item = {
                        "title": title,
                        "content": article_content,
                        "link": item_url,
                        "source": name,
                        "category": category,
                        "subcategory": subcategory,
                        "importance": importance,
                        "credibility": credibility,
                        "published_at": pub_date,
                    }

                    # Используем асинхронный сервис БД
                    db_service = get_async_service()
                    await db_service.async_upsert_news([news_item])
                    saved_count += 1

                    logger.debug(f"[{category}/{subcategory}] {title} -> SAVED (importance: {importance:.2f})")

                except Exception as e:
                    logger.error(f"Ошибка обработки JSON feed записи: {e}")
                    continue

            # Обновляем прогресс с результатами обработки JSON источника
            update_progress(
                sources_processed_delta=1,
                news_found_delta=processed_count,
                news_saved_delta=saved_count,
                news_filtered_delta=processed_count - saved_count,
                source_stats={"name": name, "news_count": saved_count, "time_ms": 1000},
                category=category,
            )

            return {
                "success": True,
                "processed": processed_count,
                "saved": saved_count,
                "type": "json",
            }

        except Exception as e:
            return {"success": False, "reason": f"json_parse_error: {e}"}

    async def _process_wordpress_api_source(
        self, category: str, subcategory: str, name: str, url: str, content: bytes
    ) -> Dict[str, Any]:
        """Обработка WordPress REST API источника."""
        try:
            # Parse WordPress API using dedicated parser
            parsed_data = self._parse_wordpress_api(content, url)

            if not parsed_data or not parsed_data.get("items"):
                return {"success": False, "reason": "no_entries"}

            if parsed_data.get("error"):
                logger.error(f"WordPress API parsing error: {parsed_data['error']}")
                return {"success": False, "reason": f"wordpress_api_parse_error: {parsed_data['error']}"}

            processed_count = 0
            saved_count = 0

            # Process items from WordPress API
            max_entries = getattr(self, "max_rss_entries", 50)
            items = parsed_data.get("items", [])[:max_entries]

            for item_data in items:
                try:
                    # Extract and clean data
                    title = clean_text(item_data.get("title", ""))
                    item_url = self._make_absolute_url(item_data.get("url", ""), url)

                    if not title:
                        continue

                    # Phase 3: Get content with proper normalization
                    content_html = item_data.get("content_html", "")
                    content_text = item_data.get("content_text", "")
                    summary = item_data.get("summary", "")

                    # Use best available content
                    article_content = content_html or content_text or summary or ""
                    article_content = clean_text(article_content)

                    # Phase 3: Normalized date handling
                    pub_date = None
                    date_str = item_data.get("date_published")
                    if date_str:
                        pub_date = self._normalize_date(date_str)

                    processed_count += 1

                    # Phase 4: Apply quality and deduplication filters
                    should_process, filter_info = self._apply_phase4_filters(
                        title, article_content, item_url, category, subcategory
                    )
                    if not should_process:
                        continue

                    # Оценка важности и достоверности
                    text_for_ai = f"{title} {article_content}".strip()
                    if not text_for_ai:
                        continue

                    # Используем объединённую функцию для экономии API запросов
                    importance, credibility = evaluate_both_with_optimization(
                        {"title": title, "content": text_for_ai, "category": category}
                    )

                    if importance < self.min_importance:
                        logger.debug(f"[{category}/{subcategory}] {title} -> SKIP (importance: {importance:.2f})")
                        continue

                    # Сохраняем в БД
                    news_item = {
                        "title": title,
                        "content": article_content,
                        "link": item_url,
                        "source": name,
                        "category": category,
                        "subcategory": subcategory,
                        "importance": importance,
                        "credibility": credibility,
                        "published_at": pub_date,
                    }

                    # Используем асинхронный сервис БД
                    db_service = get_async_service()
                    await db_service.async_upsert_news([news_item])
                    saved_count += 1

                    logger.debug(f"[{category}/{subcategory}] {title} -> SAVED (importance: {importance:.2f})")

                except Exception as e:
                    logger.error(f"Ошибка обработки WordPress API записи: {e}")
                    continue

            return {
                "success": True,
                "processed": processed_count,
                "saved": saved_count,
                "type": "wordpress_api",
            }

        except Exception as e:
            return {"success": False, "reason": f"wordpress_api_error: {e}"}

    async def _process_html_source(
        self, category: str, subcategory: str, name: str, url: str, content: bytes
    ) -> Dict[str, Any]:
        """Обработка HTML источника."""
        try:
            # Извлекаем контент каскадным методом
            extracted = self._extract_content_cascade(url, content)
            if not extracted:
                return {"success": False, "reason": "content_extraction_failed"}

            title = extracted["title"]
            maintext = extracted["maintext"]
            method = extracted["method"]

            if not title or not maintext:
                return {"success": False, "reason": "insufficient_content"}

            # Оценка важности и достоверности (объединённый запрос для экономии)
            text_for_ai = f"{title} {maintext}".strip()
            importance, credibility = evaluate_both_with_optimization(
                {"title": title, "content": text_for_ai, "category": category}
            )

            if importance < self.min_importance:
                logger.debug(f"[{category}/{subcategory}] {title} -> SKIP (importance: {importance:.2f})")
                return {"success": False, "reason": "low_importance", "importance": importance}

            # Сохраняем в БД
            news_item = {
                "title": title,
                "content": maintext,
                "link": url,
                "source": name,
                "category": category,
                "subcategory": subcategory,
                "importance": importance,
                "credibility": credibility,
            }

            # Используем асинхронный сервис БД
            db_service = get_async_service()
            await db_service.async_upsert_news([news_item])

            logger.info(f"[{category}/{subcategory}] {url} -> SUCCESS ({method}, importance: {importance:.2f})")

            return {
                "success": True,
                "processed": 1,
                "saved": 1,
                "type": "html",
                "method": method,
                "importance": importance,
                "credibility": credibility,
            }

        except Exception as e:
            return {"success": False, "reason": f"html_parse_error: {e}"}

    async def run(self, auto_retrain: bool = True) -> Dict[str, Any]:
        """
        Запуск парсинга всех источников.

        Args:
            auto_retrain: Автоматически переобучать модели после парсинга

        Returns:
            Словарь с общей статистикой
        """
        if not self.session:
            await self._init_session()

        sources = self._get_all_sources()
        if not sources:
            logger.warning("Источники не найдены в конфигурации")
            return {"error": "no_sources"}

        # Устанавливаем общее количество источников для прогресса
        update_progress(sources_total=len(sources))

        logger.info(f"Начинаем парсинг {len(sources)} источников")

        # Создаем задачи для всех источников
        tasks = []
        for category, subcategory, name, url in sources:
            task = self._process_source(category, subcategory, name, url)
            tasks.append(task)

        # Выполняем все задачи параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Анализируем результаты
        stats = {
            "total_sources": len(sources),
            "successful": 0,
            "failed": 0,
            "total_processed": 0,
            "total_saved": 0,
            "errors": [],
        }

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                stats["failed"] += 1
                stats["errors"].append(f"Source {i}: {result}")
                continue

            if result.get("success"):
                stats["successful"] += 1
                stats["total_processed"] += result.get("processed", 0)
                stats["total_saved"] += result.get("saved", 0)
            else:
                stats["failed"] += 1

        logger.info(
            f"Парсинг завершен: {stats['successful']}/{stats['total_sources']} успешно, "
            f"{stats['total_saved']} новостей сохранено"
        )

        # Автоматическое переобучение моделей после парсинга
        if auto_retrain and stats.get("total_saved", 0) > 0:
            try:
                logger.info("")
                logger.info("🤖 Запуск автоматического переобучения моделей...")

                from ai_modules.self_tuning_collector import get_self_tuning_collector
                from ai_modules.self_tuning_trainer import get_self_tuning_trainer
                from datetime import datetime, timezone, timedelta

                collector = get_self_tuning_collector()
                trainer = get_self_tuning_trainer()

                # Проверка, включено ли самообучение
                if not collector.is_enabled() or not trainer.is_enabled():
                    logger.info("⏭️ Self-tuning отключен в конфигурации")
                else:
                    # Проверка интервала переобучения
                    metadata = trainer._load_existing_metadata()
                    should_train = False

                    if not metadata:
                        should_train = True
                        logger.info("📊 Модели не найдены, требуется первое обучение")
                    else:
                        last_training_str = metadata.get("timestamp")
                        if last_training_str:
                            last_training = datetime.fromisoformat(last_training_str.replace("Z", "+00:00"))
                            interval_days = trainer.config.get("self_tuning", {}).get("interval_days", 2)
                            next_training = last_training + timedelta(days=interval_days)
                            now = datetime.now(timezone.utc)

                            if now >= next_training:
                                should_train = True
                                days_since = (now - last_training).days
                                logger.info(f"✅ Интервал переобучения достигнут ({days_since} дней)")
                            else:
                                remaining = next_training - now
                                logger.info(f"⏳ До переобучения: {remaining}")
                        else:
                            should_train = True

                    if should_train:
                        # Сбор данных
                        logger.info("📊 Сбор обучающих данных...")
                        collection_result = collector.collect_training_data()

                        if collection_result["success"]:
                            dataset_size = collection_result["dataset_size"]
                            logger.info(f"✅ Собрано {dataset_size} примеров")

                            # Обучение моделей
                            logger.info("🧠 Обучение моделей...")
                            from pathlib import Path

                            dataset_path = Path(collection_result["dataset_path"])
                            training_result = trainer.train_models(dataset_path)

                            if training_result["success"]:
                                improvements = training_result.get("improvements", {})
                                for model_name, result in improvements.items():
                                    f1_score = result.get("f1_score", 0.0)
                                    replaced = result.get("replaced", False)
                                    status = "✅ ЗАМЕНЕНА" if replaced else "⏸️ НЕ ЗАМЕНЕНА"
                                    logger.info(f"   {model_name}: F1={f1_score:.3f} ({status})")

                                logger.info("🎉 Переобучение завершено!")
                                stats["retrain_status"] = "success"
                                stats["retrain_improvements"] = improvements
                            else:
                                logger.warning(f"⚠️ Ошибка обучения: {training_result.get('error')}")
                                stats["retrain_status"] = "training_failed"
                        else:
                            logger.warning(f"⚠️ Недостаточно данных: {collection_result.get('error')}")
                            stats["retrain_status"] = "insufficient_data"
                    else:
                        logger.info("⏭️ Переобучение не требуется (интервал не достигнут)")
                        stats["retrain_status"] = "skipped_interval"

            except Exception as e:
                logger.error(f"❌ Ошибка автоматического переобучения: {e}")
                stats["retrain_status"] = "error"
                stats["retrain_error"] = str(e)

        return stats


# Пример использования
async def main():
    """Пример запуска парсера."""
    async with AdvancedParser(max_concurrent=10, min_importance=0.3) as parser:
        stats = await parser.run()
        print(f"Результаты парсинга: {stats}")


if __name__ == "__main__":
    asyncio.run(main())

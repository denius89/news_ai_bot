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
    - TODO: Добавить metrics и monitoring

Author: PulseAI Team
Last Updated: October 2025
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
import yaml
from pathlib import Path

import aiohttp
import feedparser
from newsplease import NewsPlease
import trafilatura
from autoscraper import AutoScraper

from database.service import get_async_service
from ai_modules.importance import evaluate_importance
from ai_modules.credibility import evaluate_credibility
from utils.text.clean_text import clean_text

logger = logging.getLogger(__name__)


class AdvancedParser:
    """Продвинутый асинхронный парсер новостей с AI-фильтрацией."""

    def __init__(self, max_concurrent: int = 10, min_importance: float = 0.3):
        """
        Инициализация парсера.

        Args:
            max_concurrent: Максимальное количество одновременных запросов
            min_importance: Минимальный порог важности для сохранения новости
        """
        self.max_concurrent = max_concurrent
        self.min_importance = min_importance
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None
        self.sources_config: Dict = {}

    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход."""
        await self._init_session()
        await self._load_sources_config()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход."""
        await self._close_session()

    async def _init_session(self):
        """Инициализация HTTP сессии."""
        # Увеличенный timeout для медленных источников (WEF, World Bank, IMF)
        timeout = aiohttp.ClientTimeout(total=60, connect=15, sock_read=45)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        self.session = aiohttp.ClientSession(timeout=timeout, connector=connector, headers=headers)

    async def _close_session(self):
        """Закрытие HTTP сессии."""
        if self.session:
            await self.session.close()

    async def _load_sources_config(self):
        """Загрузка конфигурации источников из YAML."""
        config_path = Path("config/data/sources.yaml")
        if not config_path.exists():
            logger.error("Файл config/sources.yaml не найден")
            self.sources_config = {}
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.sources_config = yaml.safe_load(f)
            logger.info(f"Загружена конфигурация из {config_path}")
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            self.sources_config = {}

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

            for subcategory, subcategory_data in category_data.items():
                if not isinstance(subcategory_data, dict):
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

    async def _fetch_content(self, url: str) -> Tuple[bool, str, Optional[bytes]]:
        """
        Асинхронная загрузка контента по URL.

        Args:
            url: URL для загрузки

        Returns:
            Кортеж (success, content_type, content_bytes)
        """
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    content_bytes = await response.read()
                    content_type = response.headers.get("content-type", "").lower()
                    return True, content_type, content_bytes
                else:
                    logger.warning(f"HTTP {response.status} для {url}")
                    return False, None, None

        except Exception as e:
            logger.error(f"Ошибка загрузки {url}: {e}")
            return False, None, None

    async def _fetch_content_with_retry(self, url: str, max_retries: int = 3) -> Tuple[bool, str, Optional[bytes]]:
        """
        Загрузка контента с retry и exponential backoff.

        Args:
            url: URL для загрузки
            max_retries: Максимальное количество попыток (по умолчанию 3)

        Returns:
            Кортеж (success, content_type, content_bytes)
        """
        for attempt in range(max_retries):
            try:
                success, content_type, content = await self._fetch_content(url)

                if success:
                    if attempt > 0:
                        logger.info(f"Успешно загружено с попытки {attempt + 1}: {url}")
                    return success, content_type, content

                # Если не успешно и есть еще попытки - ждем
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # 1s, 2s, 4s
                    logger.debug(f"Повтор через {wait_time}s (попытка {attempt + 2}/{max_retries}): {url}")
                    await asyncio.sleep(wait_time)

            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Не удалось загрузить после {max_retries} попыток: {url} - {e}")
                    return False, None, None

                wait_time = 2**attempt
                logger.debug(f"Ошибка, повтор через {wait_time}s: {url} - {e}")
                await asyncio.sleep(wait_time)

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
                logger.info(f"[{category}/{subcategory}] {url} -> START")

                # Загружаем контент с retry механизмом
                success, content_type, content = await self._fetch_content_with_retry(url, max_retries=3)
                if not success or not content:
                    logger.warning(f"[{category}/{subcategory}] {url} -> FAIL (fetch)")
                    return {"success": False, "reason": "fetch_failed"}

                # Определяем тип источника
                if "rss" in content_type or "xml" in content_type or url.endswith((".rss", ".xml")):
                    # RSS источник
                    return await self._process_rss_source(category, subcategory, name, url, content)
                else:
                    # HTML источник
                    return await self._process_html_source(category, subcategory, name, url, content)

            except Exception as e:
                logger.error(f"[{category}/{subcategory}] {url} -> ERROR: {e}")
                return {"success": False, "reason": str(e)}
            finally:
                elapsed = time.time() - start_time
                logger.debug(f"[{category}/{subcategory}] {url} -> completed in {elapsed:.2f}s")

    async def _process_rss_source(
        self, category: str, subcategory: str, name: str, url: str, content: bytes
    ) -> Dict[str, Any]:
        """Обработка RSS источника."""
        try:
            feed = feedparser.parse(content)

            # Проверить на ошибки парсинга RSS
            if feed.bozo:
                logger.warning(f"RSS parsing error for {url}: {feed.bozo_exception}")
                # Попробовать исправить encoding
                if "encoding" in str(feed.bozo_exception).lower():
                    try:
                        content_str = content.decode("utf-8", errors="ignore")
                        feed = feedparser.parse(content_str)
                    except Exception as e:
                        logger.debug(f"Failed to fix encoding: {e}")

            if not feed.entries:
                return {"success": False, "reason": "no_entries"}

            processed_count = 0
            saved_count = 0

            # Обрабатываем до 50 записей вместо 5
            max_entries = getattr(self, "max_rss_entries", 50)
            for entry in feed.entries[:max_entries]:
                try:
                    # Извлекаем данные из RSS
                    title = clean_text(entry.get("title", ""))
                    link = entry.get("link", "")

                    # Каскадное извлечение контента: content > description > summary
                    article_content = ""
                    if hasattr(entry, "content") and entry.content:
                        article_content = clean_text(entry.content[0].value)
                    elif hasattr(entry, "description") and entry.description:
                        article_content = clean_text(entry.description)
                    else:
                        article_content = clean_text(entry.get("summary", ""))

                    # Извлечь дату публикации
                    from datetime import datetime, timezone

                    pub_date = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        try:
                            pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                        except Exception:
                            pass
                    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                        try:
                            pub_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                        except Exception:
                            pass

                    if not title:
                        continue

                    processed_count += 1

                    # Оценка важности и достоверности
                    text_for_ai = f"{title} {article_content}".strip()
                    if not text_for_ai:
                        continue

                    importance = evaluate_importance({"title": title, "content": text_for_ai})
                    credibility = evaluate_credibility({"title": title, "content": text_for_ai})

                    if importance < self.min_importance:
                        logger.debug(f"[{category}/{subcategory}] {title} -> SKIP (importance: {importance:.2f})")
                        continue

                    # Сохраняем в БД
                    news_item = {
                        "title": title,
                        "content": article_content,
                        "link": link,
                        "source": name,
                        "category": category,
                        "subcategory": subcategory,
                        "importance": importance,
                        "credibility": credibility,
                        "published_at": pub_date,  # Сохраняем реальную дату публикации
                    }

                    # Используем асинхронный сервис БД
                    db_service = get_async_service()
                    await db_service.async_upsert_news([news_item])
                    saved_count += 1

                    logger.debug(f"[{category}/{subcategory}] {title} -> SAVED (importance: {importance:.2f})")

                except Exception as e:
                    logger.error(f"Ошибка обработки RSS записи: {e}")
                    continue

            return {
                "success": True,
                "processed": processed_count,
                "saved": saved_count,
                "type": "rss",
            }

        except Exception as e:
            return {"success": False, "reason": f"rss_parse_error: {e}"}

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

            # Оценка важности и достоверности
            text_for_ai = f"{title} {maintext}".strip()
            importance = evaluate_importance({"title": title, "content": text_for_ai})
            credibility = evaluate_credibility({"title": title, "content": text_for_ai})

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

    async def run(self) -> Dict[str, Any]:
        """
        Запуск парсинга всех источников.

        Returns:
            Словарь с общей статистикой
        """
        if not self.session:
            await self._init_session()

        sources = self._get_all_sources()
        if not sources:
            logger.warning("Источники не найдены в конфигурации")
            return {"error": "no_sources"}

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

        return stats


# Пример использования
async def main():
    """Пример запуска парсера."""
    async with AdvancedParser(max_concurrent=10, min_importance=0.3) as parser:
        stats = await parser.run()
        print(f"Результаты парсинга: {stats}")


if __name__ == "__main__":
    asyncio.run(main())

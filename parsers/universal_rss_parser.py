"""
Универсальный RSS парсер с улучшенной обработкой ошибок и различных форматов.
"""

import hashlib
import logging
import re
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse

import requests
import feedparser
from dateutil import parser as dtp
from bs4 import BeautifulSoup

from utils.clean_text import clean_text
from services.categories import get_all_sources

logger = logging.getLogger("parsers.universal_rss")

# Улучшенные заголовки для лучшей совместимости
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, application/atom+xml, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

# Настройки для retry логики
MAX_RETRIES = 3
RETRY_DELAY = 2  # секунды
TIMEOUT = 15  # секунды


class UniversalRSSParser:
    """Универсальный RSS парсер с улучшенной обработкой ошибок."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def parse_source(
        self, url: str, category: str, subcategory: str, source_name: str
    ) -> List[Dict]:
        """
        Универсальная функция для парсинга одного источника RSS.

        Args:
            url: URL RSS фида
            category: Категория новости
            subcategory: Подкатегория новости
            source_name: Название источника

        Returns:
            List[Dict]: Список новостей с полями category и subcategory
        """
        try:
            # Попытка загрузки с retry логикой
            feed = self._fetch_feed_with_retry(url)
            if not feed or not feed.entries:
                logger.warning(f"Пустой фид: {source_name} ({url})")
                return []

            news_items = []
            for entry in feed.entries:
                try:
                    news_item = self._parse_entry(entry, category, subcategory, source_name, url)
                    if news_item:
                        news_items.append(news_item)
                except Exception as e:
                    logger.warning(f"Ошибка парсинга записи из {source_name}: {e}")
                    continue

            logger.info(f"✅ Парсинг {source_name}: {len(news_items)} новостей")
            return news_items

        except Exception as e:
            logger.error(f"❌ Ошибка парсинга источника {source_name}: {e}")
            return []

    def _fetch_feed_with_retry(self, url: str) -> Optional[Any]:
        """Загружает фид с retry логикой и улучшенной обработкой Content-Type."""
        for attempt in range(MAX_RETRIES):
            try:
                logger.debug(f"Попытка {attempt + 1}/{MAX_RETRIES} загрузки: {url}")

                response = self.session.get(url, timeout=TIMEOUT, allow_redirects=True)

                # Проверяем статус код
                if response.status_code != 200:
                    logger.warning(f"HTTP {response.status_code} для {url}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY * (attempt + 1))
                        continue
                    return None

                # Улучшенная проверка Content-Type
                content_type = response.headers.get("Content-Type", "").lower()
                content = response.content

                # Проверяем, является ли контент XML/RSS
                if self._is_rss_content(content, content_type, url):
                    feed = feedparser.parse(content)
                    if feed.bozo and not feed.entries:
                        logger.warning(f"Возможные проблемы с фидом {url}: {feed.bozo_exception}")
                    return feed
                else:
                    logger.warning(f"Не RSS контент: {url} (Content-Type: {content_type})")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    return None

            except requests.exceptions.RequestException as e:
                logger.warning(f"Ошибка сети для {url} (попытка {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                return None
            except Exception as e:
                logger.error(f"Неожиданная ошибка для {url}: {e}")
                return None

        return None

    def _is_rss_content(self, content: bytes, content_type: str, url: str) -> bool:
        """Определяет, является ли контент RSS/XML фидом."""
        # Проверяем Content-Type
        if any(xml_type in content_type for xml_type in ['xml', 'rss', 'atom']):
            return True

        # Проверяем начало контента
        content_start = content[:500].decode('utf-8', errors='ignore').lower()

        # Ищем RSS/XML теги
        if any(tag in content_start for tag in ['<rss', '<feed', '<rdf:rdf', '<?xml']):
            return True

        # Проверяем URL паттерны
        if any(pattern in url.lower() for pattern in ['.rss', '.xml', 'rss', 'feed']):
            return True

        return False

    def _parse_entry(
        self, entry: Any, category: str, subcategory: str, source_name: str, base_url: str
    ) -> Optional[Dict]:
        """Парсит одну запись из RSS фида."""
        try:
            # Извлекаем и очищаем заголовок
            title = self._extract_title(entry)
            if not title:
                return None

            # Извлекаем и очищаем контент
            content = self._extract_content(entry)

            # Извлекаем ссылку
            link = self._extract_link(entry, base_url)

            # Парсим дату
            published_at = self._extract_date(entry)

            # Создаем уникальный ID
            uid = hashlib.md5(f"{link}{title}".encode()).hexdigest()

            return {
                "uid": uid,
                "title": title,
                "content": content,
                "link": link,
                "source": source_name,
                "category": category,
                "subcategory": subcategory,
                "published_at": published_at.isoformat() if published_at else None,
            }

        except Exception as e:
            logger.warning(f"Ошибка парсинга записи: {e}")
            return None

    def _extract_title(self, entry: Any) -> str:
        """Извлекает заголовок из записи."""
        # Пробуем разные поля для заголовка
        title_fields = ['title', 'title_detail', 'summary']

        for field in title_fields:
            if hasattr(entry, field):
                title = entry.get(field, '')
                if isinstance(title, dict):
                    title = title.get('value', '')
                if title:
                    return clean_text(str(title))

        return ""

    def _extract_content(self, entry: Any) -> str:
        """Извлекает контент из записи."""
        # Пробуем разные поля для контента
        content_fields = ['summary', 'content', 'description']

        for field in content_fields:
            if hasattr(entry, field):
                content = entry.get(field, '')
                if isinstance(content, dict):
                    content = content.get('value', '')
                if isinstance(content, list) and content:
                    content = (
                        content[0].get('value', '')
                        if isinstance(content[0], dict)
                        else str(content[0])
                    )

                if content:
                    # Очищаем HTML теги если нужно
                    cleaned_content = clean_text(str(content))
                    if cleaned_content and len(cleaned_content) > 10:
                        return cleaned_content

        return ""

    def _extract_link(self, entry: Any, base_url: str) -> str:
        """Извлекает ссылку из записи."""
        link = entry.get('link', '')
        if link:
            # Делаем ссылку абсолютной
            return urljoin(base_url, link)
        return ""

    def _extract_date(self, entry: Any) -> Optional[datetime]:
        """Извлекает дату из записи с улучшенным парсингом."""
        # Пробуем разные поля для даты
        date_fields = ['published', 'updated', 'created', 'pubDate']

        for field in date_fields:
            if hasattr(entry, field):
                date_str = entry.get(field, '')
                if date_str:
                    parsed_date = self._parse_date(date_str)
                    if parsed_date:
                        return parsed_date

        # Пробуем parsed даты
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            except:
                pass

        if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            try:
                return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            except:
                pass

        return None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Парсит дату из строки с улучшенной обработкой."""
        if not date_str:
            return None

        try:
            # Убираем лишние символы
            date_str = re.sub(r'[^\w\s:+-]', '', str(date_str))

            # Парсим дату
            dt = dtp.parse(date_str)

            # Устанавливаем timezone если не указан
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=timezone.utc)

            return dt.astimezone(timezone.utc)

        except Exception as e:
            logger.debug(f"Не удалось распарсить дату '{date_str}': {e}")
            return None

    def fetch_all_sources(self, per_source_limit: Optional[int] = None) -> List[Dict]:
        """Загружает новости из всех источников."""
        all_sources = get_all_sources()
        news_items = []
        seen = set()

        logger.info(f"🔄 Начинаем парсинг {len(all_sources)} источников")

        successful_sources = 0
        failed_sources = 0

        for cat, subcat, name, url in all_sources:
            logger.info(f"🔄 Обрабатываем: {name} ({url})")

            source_items = self.parse_source(url, cat, subcat, name)

            if source_items:
                successful_sources += 1

                # Применяем лимит если указан
                if per_source_limit:
                    source_items = source_items[:per_source_limit]

                # Добавляем уникальные элементы
                for item in source_items:
                    uid = item["uid"]
                    if uid not in seen:
                        seen.add(uid)
                        news_items.append(item)

                logger.info(f"✅ {name}: {len(source_items)} новостей добавлено")
            else:
                failed_sources += 1
                logger.warning(f"❌ {name}: нет новостей")

        logger.info(
            f"📊 Парсинг завершен: {successful_sources} успешных, {failed_sources} неудачных, {len(news_items)} уникальных новостей"
        )
        return news_items

    def close(self):
        """Закрывает сессию."""
        if hasattr(self, 'session'):
            self.session.close()


# Convenience functions для обратной совместимости
def parse_source(url: str, category: str, subcategory: str, source_name: str) -> List[Dict]:
    """Обратная совместимость с старым API."""
    parser = UniversalRSSParser()
    try:
        return parser.parse_source(url, category, subcategory, source_name)
    finally:
        parser.close()


def fetch_rss(urls: Dict[str, Dict], per_source_limit: Optional[int] = None) -> List[Dict]:
    """Обратная совместимость с старым API."""
    parser = UniversalRSSParser()
    try:
        all_sources = []
        for meta in urls.values():
            source_items = parser.parse_source(
                url=meta["url"],
                category=meta.get("category", ""),
                subcategory=meta.get("subcategory", ""),
                source_name=meta["name"],
            )

            if per_source_limit:
                source_items = source_items[:per_source_limit]

            all_sources.extend(source_items)

        return all_sources
    finally:
        parser.close()

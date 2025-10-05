# Этот файл устарел. Используйте parsers/unified_parser.py
# Импортируем новый унифицированный парсер для обратной совместимости
from parsers.unified_parser import (
    UnifiedParser, 
    parse_source, 
    parse_all_sources,
    get_sync_parser,
    get_async_parser
)

import logging
from typing import Dict, List, Optional

from services.categories import get_all_sources

logger = logging.getLogger("parsers.rss")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0; +https://example.com)"}


def normalize_date(date_str: str | None):
    """Парсит дату, возвращает UTC datetime или None."""
    if not date_str:
        return None
    try:
        dt = dtp.parse(date_str)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception as e:
        logger.warning(f"Не удалось распарсить дату: {date_str} ({e})")
        return None


def load_sources(
    category: Optional[str] = None, subcategory: Optional[str] = None
) -> Dict[str, Dict]:
    """Загружает список RSS-источников из services/categories."""
    all_sources = get_all_sources()
    urls: Dict[str, Dict] = {}

    for cat, subcat, name, url in all_sources:
        # Фильтруем по категории и подкатегории если указаны
        if category and cat != category:
            continue
        if subcategory and subcat != subcategory:
            continue

        urls[name] = {"name": name, "url": url, "category": cat, "subcategory": subcat}

    return urls


def parse_source(url: str, category: str, subcategory: str, source_name: str) -> List[Dict]:
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
        feed = fetch_feed(url)
        if not feed or not feed.entries:
            logger.warning(f"Пустой фид: {source_name} ({url})")
            return []

        news_items = []
        for entry in feed.entries:
            try:
                # Очистка текста
                title = clean_text(entry.get("title", ""))
                content = clean_text(entry.get("summary", ""))

                if not title:
                    continue

                # Парсинг даты
                published_at = normalize_date(entry.get("published", entry.get("updated")))
                if not published_at:
                    published_at = normalize_date(str(entry.get("published_parsed")))

                # Создание уникального ID
                uid = hashlib.md5(f"{entry.get('link', '')}{title}".encode()).hexdigest()

                news_item = {
                    "uid": uid,
                    "title": title,
                    "content": content,
                    "link": entry.get("link", ""),  # Исправлено: url -> link
                    "source": source_name,
                    "category": category,
                    "subcategory": subcategory,
                    "published_at": published_at.isoformat() if published_at else None,
                }

                news_items.append(news_item)

            except Exception as e:
                logger.warning(f"Ошибка парсинга записи из {source_name}: {e}")
                continue

        logger.info(f"✅ Парсинг {source_name}: {len(news_items)} новостей")
        return news_items

    except Exception as e:
        logger.error(f"❌ Ошибка парсинга источника {source_name}: {e}")
        return []


def fetch_feed(url: str):
    """Запрашивает фид и проверяет MIME-тип (чтобы избежать text/html)."""
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        ctype = resp.headers.get("Content-Type", "")
        if "xml" not in ctype and "rss" not in ctype:
            raise ValueError(f"Invalid content-type {ctype} for {url}")
        return feedparser.parse(resp.content)
    except Exception as e:
        logger.error(f"Ошибка при загрузке {url}: {e}")
        return None


def fetch_rss(urls: Dict[str, Dict], per_source_limit: Optional[int] = None) -> List[Dict]:
    """Загружает новости из RSS-источников с поддержкой subcategory."""
    news_items = []
    seen = set()

    for meta in urls.values():
        logger.info(f"🔄 Загружаем источник: {meta['name']} ({meta['url']})")

        # Используем новую функцию parse_source
        source_items = parse_source(
            url=meta["url"],
            category=meta.get("category", ""),
            subcategory=meta.get("subcategory", ""),
            source_name=meta["name"],
        )

        # Применяем лимит если указан
        if per_source_limit:
            source_items = source_items[:per_source_limit]

        # Добавляем уникальные элементы
        for item in source_items:
            uid = item["uid"]
            if uid not in seen:
                seen.add(uid)
                news_items.append(item)

        logger.info(f"✅ {meta['name']}: {len(source_items)} новостей добавлено")

    return news_items

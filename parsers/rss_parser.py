import feedparser
import re
import yaml
import hashlib
import logging
from bs4 import BeautifulSoup
from pathlib import Path
from dateutil import parser as dtp
from datetime import timezone

logger = logging.getLogger("parsers.rss")

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "sources.yaml"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0; +https://example.com)"
}

def clean_text(text: str) -> str:
    """Удаляет HTML-теги и нормализует пробелы."""
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"\s+", " ", text).strip()
    return text

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

def load_sources(category: str | None = None) -> dict[str, dict]:
    """Загружает список RSS-источников из sources.yaml."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        sources = yaml.safe_load(f)

    urls: dict[str, dict] = {}
    if category:
        if category not in sources:
            raise ValueError(f"Нет категории '{category}' в sources.yaml")
        group = sources[category]
        for item in group:
            urls[item["name"]] = {**item, "category": category}
    else:
        for cat, group in sources.items():
            for item in group:
                urls[item["name"]] = {**item, "category": cat}

    return urls

def fetch_rss(urls: dict[str, dict], per_source_limit: int | None = None) -> list[dict]:
    """Загружает новости из RSS-источников."""
    news_items = []
    seen = set()

    for meta in urls.values():
        feed = feedparser.parse(meta["url"], request_headers=HEADERS)
        if feed.bozo:
            logger.error(f"Ошибка при парсинге {meta['url']}: {feed.bozo_exception}")
            continue

        for entry in feed.entries[:per_source_limit]:
            url = entry.get("link") or ""
            title = clean_text(entry.get("title", ""))
            summary = clean_text(entry.get("summary") or entry.get("description") or "")
            published = normalize_date(entry.get("published") or entry.get("updated"))

            uid = hashlib.sha256(f"{url}|{title}".encode()).hexdigest()
            if uid in seen:
                continue
            seen.add(uid)

            news_items.append({
                "uid": uid,
                "title": title,
                "url": url,
                "summary": summary or title,
                "published_at": published,
                "source": meta["name"],
                "category": meta["category"],
            })

    return news_items
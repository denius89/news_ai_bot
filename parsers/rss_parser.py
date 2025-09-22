import feedparser
import json
import re
import yaml
from datetime import datetime
import dateutil.parser
from bs4 import BeautifulSoup
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "sources.yaml"


def clean_text(text: str) -> str:
    """
    Удаляет HTML-теги и нормализует пробелы.
    """
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_sources(category: str | None = None) -> dict[str, dict]:
    """
    Загружает источники из sources.yaml.
    Возвращает словарь {url: {"name": ..., "category": ...}}
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        sources = yaml.safe_load(f)

    mapping = {}
    if category:
        if category not in sources:
            raise ValueError(f"Нет категории '{category}' в sources.yaml")
        for item in sources[category]:
            mapping[item["url"]] = {"name": item["name"], "category": category}
    else:
        for cat, group in sources.items():
            for item in group:
                mapping[item["url"]] = {"name": item["name"], "category": cat}

    return mapping


def fetch_rss(urls: dict[str, dict]) -> list[dict]:
    """
    Загружает новости из RSS-источников.
    urls = {url: {"name": ..., "category": ...}}
    Возвращает список словарей: title, link, published, content, source, category.
    """
    news_items = []
    seen_links = set()

    for url, meta in urls.items():
        feed = feedparser.parse(url)

        if feed.bozo:
            print(f"[WARN] Ошибка при парсинге {url}")
            continue

        for entry in feed.entries:
            link = entry.get("link", "").strip()
            if not link or link in seen_links:
                continue
            seen_links.add(link)

            # Нормализация даты
            published_raw = entry.get("published") or entry.get("updated")
            try:
                published = dateutil.parser.parse(published_raw) if published_raw else None
            except Exception:
                published = None

            # Контент
            content = entry.get("content", [{}])
            if isinstance(content, list) and content:
                content = content[0].get("value", "")
            else:
                content = entry.get("summary", "")

            news_items.append({
                "title": clean_text(entry.get("title", "")),
                "link": link,
                "published": published,
                "content": clean_text(content),
                "source": meta["name"],
                "category": meta["category"],
            })

    return news_items


if __name__ == "__main__":
    # Загружаем только crypto
    urls = load_sources("crypto")
    items = fetch_rss(urls)
    print(f"Найдено новостей: {len(items)}")
    print(json.dumps(items[:3], ensure_ascii=False, indent=2, default=str))
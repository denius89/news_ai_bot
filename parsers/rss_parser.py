import feedparser
import re
import yaml
import dateutil.parser
from bs4 import BeautifulSoup
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "sources.yaml"

# Кастомный User-Agent (иначе Reuters, Bloomberg и др. блокируют)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0; +https://example.com)"
}


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
    Загружает список RSS-источников из sources.yaml.
    Если категория не указана → берём все источники.
    Возвращает словарь: ключ — имя источника, значение — словарь {url, name, category}.
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        sources = yaml.safe_load(f)

    urls: dict[str, dict] = {}
    if category:
        if category not in sources:
            raise ValueError(f"Нет категории '{category}' в sources.yaml")
        for item in sources[category]:
            urls[item["name"]] = {
                "url": item["url"],
                "name": item["name"],
                "category": category,
            }
    else:
        for cat, group in sources.items():
            for item in group:
                urls[item["name"]] = {
                    "url": item["url"],
                    "name": item["name"],
                    "category": cat,
                }

    return urls


def fetch_rss(urls: dict[str, dict], per_source_limit: int | None = None) -> list[dict]:
    """
    Загружает новости из словаря RSS-источников.
    Если per_source_limit указан → берём только N новостей с каждого источника.
    Возвращает список словарей: title, link, published, content, source, category.
    """
    news_items = []
    seen_links = set()

    for meta in urls.values():
        url = meta["url"]
        source_name = meta["name"]
        category = meta.get("category", "general")

        try:
            feed = feedparser.parse(url, request_headers=HEADERS)
        except Exception as e:
            print(f"[WARN] Ошибка при парсинге {url}: {e}")
            continue

        if feed.bozo:
            print(f"[WARN] Ошибка при парсинге {url}")
            continue

        count = 0
        for entry in feed.entries:
            if per_source_limit and count >= per_source_limit:
                break

            link = entry.get("link", "").strip()
            if not link or link in seen_links:
                continue
            seen_links.add(link)

            published_raw = entry.get("published") or entry.get("updated")
            try:
                published = dateutil.parser.parse(published_raw) if published_raw else None
            except Exception:
                published = None

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
                "source": source_name,
                "category": category,
            })
            count += 1

    return news_items


if __name__ == "__main__":
    from pprint import pprint

    test_sources = load_sources("world")
    items = fetch_rss(test_sources, per_source_limit=5)
    print(f"Найдено новостей: {len(items)}")
    pprint(items[:3])
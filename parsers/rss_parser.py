import feedparser
import json
from datetime import datetime
import dateutil.parser


def fetch_rss(urls: list[str]) -> list[dict]:
    """
    Загружает новости из списка RSS-источников.
    Возвращает список словарей с ключами: title, link, published, content.
    """
    news_items = []
    seen_links = set()

    for url in urls:
        feed = feedparser.parse(url)

        if feed.bozo:
            print(f"[WARN] Ошибка при парсинге {url}")
            continue

        for entry in feed.entries:
            link = entry.get("link", "").strip()
            if not link or link in seen_links:
                continue
            seen_links.add(link)

            # Нормализация даты публикации
            published_raw = entry.get("published") or entry.get("updated")
            try:
                published = dateutil.parser.parse(published_raw) if published_raw else None
            except Exception:
                published = None

            # Берём content или summary (если есть)
            content = entry.get("content", [{}])
            if isinstance(content, list) and content:
                content = content[0].get("value", "")
            else:
                content = entry.get("summary", "")

            news_items.append({
                "title": entry.get("title", "").strip(),
                "link": link,
                "published": published,
                "content": content.strip() if content else None,
            })

    return news_items


if __name__ == "__main__":
    test_urls = [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
        "https://news.yahoo.com/rss/"
    ]
    items = fetch_rss(test_urls)
    print(f"Найдено новостей: {len(items)}")
    print(json.dumps(items[:5], ensure_ascii=False, indent=2, default=str))
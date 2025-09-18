# parsers/rss_parser.py

import feedparser

def fetch_rss(urls: list[str]) -> list[dict]:
    """
    Загружает новости из списка RSS-источников.
    Возвращает список словарей с ключами: title, link, published.
    """
    news_items = []
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            news_items.append({
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", "").strip(),
                "published": entry.get("published", "") or entry.get("updated", "") or ""
            })
    return news_items


if __name__ == "__main__":
    # Пример источников (крипто + экономика)
    test_urls = [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
        "https://news.yahoo.com/rss/"
    ]
    items = fetch_rss(test_urls)
    print(f"Найдено новостей: {len(items)}")
    for i, it in enumerate(items[:5], start=1):
        print(f"{i}. {it['title']}  ({it['link']})")

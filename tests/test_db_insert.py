from parsers.rss_parser import fetch_rss
from database.db_models import upsert_news


def test_insert_news():
    sources = {
        "Yahoo": {
            "url": "https://news.yahoo.com/rss/",
            "name": "Yahoo",
            "category": "world",
        },
        "Coindesk": {
            "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "name": "Coindesk",
            "category": "crypto",
        },
    }

    items = fetch_rss(sources, per_source_limit=5)
    assert isinstance(items, list)
    assert len(items) > 0

    # добавляем по одной новости
    for item in items[:5]:
        upsert_news(item)

    print(f"✅ Добавлено {len(items[:5])} новостей в базу")


if __name__ == "__main__":
    test_insert_news()
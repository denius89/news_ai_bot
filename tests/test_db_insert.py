import pytest
from parsers.rss_parser import fetch_rss
from database.db_models import upsert_news


@pytest.mark.integration
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

    items = fetch_rss(sources, per_source_limit=2)
    assert isinstance(items, list)
    assert len(items) > 0

    # фикс: передаём одну новость, а не список
    upsert_news(items[0])
    print("✅ Новости добавлены в базу (интеграционный тест)")


if __name__ == "__main__":
    test_insert_news()

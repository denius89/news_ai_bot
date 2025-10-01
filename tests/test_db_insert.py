import pytest

from database.db_models import upsert_news
from parsers.rss_parser import fetch_rss


@pytest.mark.integration
def test_insert_news():
    """Интеграционный тест: загрузка новостей из RSS и вставка в БД"""

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

    # берём максимум по 2 новости на источник
    items = fetch_rss(sources, per_source_limit=2)
    assert isinstance(items, list)
    assert len(items) > 0

    # проверяем вставку нескольких новостей
    upsert_news(items[:3])  # ограничим до 3, чтобы не перегружать базу

    print(f"✅ Добавлено {min(len(items), 3)} новостей в базу (интеграционный тест)")


if __name__ == "__main__":
    # запуск без pytest
    test_insert_news()

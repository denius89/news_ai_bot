import pytest

from database.db_models import upsert_news
from parsers.unified_parser import parse_source


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
    items = []
    for source_name, source_info in sources.items():
        try:
            parsed_items = parse_source(source_info["url"], source_info["category"], "general", source_info["name"])
            if parsed_items:
                items.extend(parsed_items[:2])  # максимум 2 новости на источник
        except Exception as e:
            print(f"Ошибка парсинга {source_name}: {e}")
            continue
    assert isinstance(items, list)
    assert len(items) > 0

    # проверяем вставку нескольких новостей
    upsert_news(items[:3])  # ограничим до 3, чтобы не перегружать базу

    print(f"✅ Добавлено {min(len(items), 3)} новостей в базу (интеграционный тест)")


if __name__ == "__main__":
    # запуск без pytest
    test_insert_news()

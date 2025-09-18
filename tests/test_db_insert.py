from parsers.rss_parser import fetch_rss
from database.db_models import upsert_news

def test_insert_news():
    urls = [
        "https://news.yahoo.com/rss/",
        "https://www.coindesk.com/arc/outboundfeeds/rss/"
    ]
    items = fetch_rss(urls)
    upsert_news(items[:5])  # берём первые 5 для теста
    print("✅ Новости добавлены в базу")
    

if __name__ == "__main__":
    test_insert_news()

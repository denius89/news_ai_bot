"""
Тесты для парсеров rss_parser и events_parser.
"""

import pytest
from bs4 import BeautifulSoup
from datetime import datetime, timezone

from utils.clean_text import clean_text, extract_text
from parsers.unified_parser import UnifiedParser, parse_source
from parsers.events_parser import normalize_datetime, make_event_id


@pytest.mark.unit
def test_rss_clean_text():
    html = "<p>Hello <b>world</b></p>"
    result = clean_text(html)
    assert result == "Hello world"


@pytest.mark.unit
def test_rss_normalize_date():
    parser = UnifiedParser()
    iso_date = "2025-09-24T10:00:00Z"
    result = parser.normalize_date(iso_date)
    assert result.isoformat().startswith("2025-09-24")


@pytest.mark.unit
def test_events_clean_text():
    html = "<div>GDP <i>growth</i></div>"
    soup = BeautifulSoup(html, "html.parser")
    result = extract_text(soup.div).lower()
    assert "gdp" in result
    assert "growth" in result


@pytest.mark.unit
def test_events_normalize_datetime():
    day = datetime.strptime("2025-09-24", "%Y-%m-%d").date()
    time_str = "10:30"
    result = normalize_datetime(day, time_str)
    assert result.year == 2025
    assert result.month == 9
    assert result.day == 24
    assert result.hour == 10
    assert result.minute == 30


@pytest.mark.unit
def test_events_normalize_datetime_all_day():
    day = datetime.strptime("2025-09-24", "%Y-%m-%d").date()
    result = normalize_datetime(day, "All day")
    assert result.hour == 0
    assert result.minute == 0
    assert result.tzinfo == timezone.utc


@pytest.mark.unit
def test_events_normalize_datetime_tentative():
    day = datetime.strptime("2025-09-24", "%Y-%m-%d").date()
    result = normalize_datetime(day, "Tentative")
    assert result.hour == 0
    assert result.minute == 0
    assert result.tzinfo == timezone.utc


@pytest.mark.unit
def test_make_event_id_stability():
    id1 = make_event_id("2025-09-24", "GDP Growth", "US")
    id2 = make_event_id("2025-09-24", "GDP Growth", "US")
    assert id1 == id2  # одинаковые данные → одинаковый uid


@pytest.mark.unit
def test_make_event_id_difference():
    id1 = make_event_id("2025-09-24", "GDP Growth", "US")
    id2 = make_event_id("2025-09-24", "Inflation", "US")
    assert id1 != id2  # разные события → разные uid


@pytest.mark.unit
def test_fetch_rss_dedup_disabled(monkeypatch):
    """Проверка, что одинаковые новости не дублируются."""

    class FakeEntry:
        def get(self, key, default=None):
            data = {
                "link": "http://example.com/news1",
                "title": "Same News",
                "summary": "<b>Summary</b>",
                "published": "2025-09-25T12:00:00Z",
            }
            return data.get(key, default)

    class FakeFeed:
        bozo = False
        entries = [FakeEntry(), FakeEntry()]  # два одинаковых

    def fake_fetch_feed(url: str):
        return FakeFeed()

    monkeypatch.setattr("parsers.rss_parser.fetch_feed", fake_fetch_feed)

    urls = {"Example": {"name": "Example", "url": "http://example.com/rss", "category": "test"}}
    items = fetch_rss(urls)
    assert len(items) == 1  # дубль должен быть отфильтрован
    assert items[0]["title"] == "Same News"
    assert items[0]["content"] == "Summary"


@pytest.mark.unit
def test_fetch_rss_two_different_disabled(monkeypatch):
    """Проверка, что разные новости сохраняются обе."""

    class FakeEntry1:
        def get(self, key, default=None):
            data = {
                "link": "http://example.com/news1",
                "title": "News One",
                "summary": "<b>First</b>",
                "published": "2025-09-25T12:00:00Z",
            }
            return data.get(key, default)

    class FakeEntry2:
        def get(self, key, default=None):
            data = {
                "link": "http://example.com/news2",
                "title": "News Two",
                "summary": "<i>Second</i>",
                "published": "2025-09-25T13:00:00Z",
            }
            return data.get(key, default)

    class FakeFeed:
        bozo = False
        entries = [FakeEntry1(), FakeEntry2()]  # две разные

    def fake_fetch_feed(url: str):
        return FakeFeed()

    monkeypatch.setattr("parsers.rss_parser.fetch_feed", fake_fetch_feed)

    urls = {"Example": {"name": "Example", "url": "http://example.com/rss", "category": "test"}}
    items = fetch_rss(urls)
    assert len(items) == 2
    titles = {item["title"] for item in items}
    assert "News One" in titles
    assert "News Two" in titles

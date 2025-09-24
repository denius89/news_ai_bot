"""
Тесты для парсеров rss_parser и events_parser.
"""

from bs4 import BeautifulSoup
from datetime import datetime

from parsers.rss_parser import clean_text, normalize_date
from parsers.events_parser import clean_text as events_clean, normalize_datetime


def test_rss_clean_text():
    html = "<p>Hello <b>world</b></p>"
    result = clean_text(html)
    assert result == "Hello world"


def test_rss_normalize_date():
    iso_date = "2025-09-24T10:00:00Z"
    result = normalize_date(iso_date)
    assert result.isoformat().startswith("2025-09-24")


def test_events_clean_text():
    html = "<div>GDP <i>growth</i></div>"
    soup = BeautifulSoup(html, "html.parser")
    result = events_clean(soup).lower()
    assert "gdp" in result
    assert "growth" in result


def test_events_normalize_datetime():
    day = datetime.strptime("2025-09-24", "%Y-%m-%d").date()
    time_str = "10:30"
    result = normalize_datetime(day, time_str)
    assert result.year == 2025
    assert result.month == 9
    assert result.day == 24
    assert result.hour == 10
    assert result.minute == 30

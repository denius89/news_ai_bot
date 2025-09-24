from datetime import datetime, timezone

from parsers.events_parser import (
    clean_text as clean_event_text,
    make_event_id,
    normalize_datetime,
)
from parsers.rss_parser import clean_text, normalize_date


def test_clean_text_rss():
    html = "<p>Hello <b>World</b>!</p>"
    assert clean_text(html) == "Hello World!"


def test_normalize_date_to_utc():
    dt = normalize_date("2024-06-01T10:00:00+02:00")
    assert dt.tzinfo is not None
    assert dt.astimezone(timezone.utc).hour == 8


def test_clean_text_event():
    assert clean_event_text(None) is None
    assert clean_event_text(type("Obj", (), {"get_text": lambda self, **kw: "Data"})()) == "Data"


def test_normalize_datetime_event():
    d = datetime(2024, 6, 1).date()
    dt = normalize_datetime(d, "14:30")
    assert dt.hour == 14
    assert dt.tzinfo is not None


def test_make_event_id_unique():
    id1 = make_event_id("Title", "US", datetime(2024, 6, 1, 14, 0, tzinfo=timezone.utc).isoformat())
    id2 = make_event_id("Title", "US", datetime(2024, 6, 1, 14, 0, tzinfo=timezone.utc).isoformat())
    assert id1 == id2

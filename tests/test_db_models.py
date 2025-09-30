# tests/test_db_models.py
import re
from database import db_models
from models.news import NewsItem


def test_make_uid_and_event_id_are_stable():
    uid1 = db_models.make_uid("http://test.com", "Hello")
    uid2 = db_models.make_uid("http://test.com", "Hello")
    assert uid1 == uid2
    assert re.match(r"^[a-f0-9]{64}$", uid1)

    event_id1 = db_models.make_event_id("Event", "US", "2025-09-30T12:00:00Z")
    event_id2 = db_models.make_event_id("Event", "US", "2025-09-30T12:00:00Z")
    assert event_id1 == event_id2


def test_enrich_news_with_ai_adds_fields():
    item = {"title": "Test", "content": "Some content"}
    enriched = db_models.enrich_news_with_ai(item)
    assert "credibility" in enriched
    assert "importance" in enriched
    assert 0.0 <= enriched["credibility"] <= 1.0
    assert 0.0 <= enriched["importance"] <= 1.0


def test_get_latest_news_returns_list(monkeypatch):
    class FakeQuery:
        def select(self, *_):
            return self

        def order(self, *_, **__):
            return self

        def limit(self, _):
            return self

        def eq(self, *_):
            return self

        def in_(self, *_):
            return self

        def execute(self):
            return type("X", (), {"data": []})()

    monkeypatch.setattr(
        db_models,
        "supabase",
        type("Supa", (), {"table": lambda self, _: FakeQuery()})(),
    )
    result = db_models.get_latest_news(limit=5)
    assert isinstance(result, list)


def test_get_latest_events_returns_list(monkeypatch):
    class FakeQuery:
        def select(self, *_):
            return self

        def order(self, *_, **__):
            return self

        def limit(self, _):
            return self

        def execute(self):
            return type("X", (), {"data": []})()

    monkeypatch.setattr(
        db_models,
        "supabase",
        type("Supa", (), {"table": lambda self, _: FakeQuery()})(),
    )
    result = db_models.get_latest_events(limit=5)
    assert isinstance(result, list)

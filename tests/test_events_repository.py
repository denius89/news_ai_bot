import pytest
from typing import Any, List

from repositories.events_repository import EventsRepository
from models.event import EventItem


class _FakeResponse:
    def __init__(self, data: List[dict]):
        self.data = data


class _FakeQuery:
    def __init__(self, data: List[dict]):
        self._data = data

    def select(self, *_: Any):
        return self

    def order(self, *_, **__):
        return self

    def limit(self, *_: Any):
        return self

    def eq(self, *_: Any):
        return self

    def in_(self, *_: Any):
        return self

    def execute(self):
        return _FakeResponse(self._data)


class _FakeClient:
    def __init__(self, data: List[dict]):
        self._data = data

    def table(self, *_: Any):
        return _FakeQuery(self._data)


@pytest.mark.unit
def test_upcoming_returns_eventitem_list():
    data = [
        {
            "event_id": "e1",
            "title": "E1",
            "event_time": "2024-01-01T10:00:00Z",
            "importance": 1,
        }
    ]
    repo = EventsRepository(_FakeClient(data))
    result = repo.upcoming(limit=1)
    assert isinstance(result, list)
    assert all(isinstance(x, EventItem) for x in result)
    assert result[0].title == "E1"
    assert result[0].event_time_fmt is not None
    assert result[0].event_time_fmt.startswith("01 Jan 2024")


@pytest.mark.unit
def test_upcoming_category_filter_list():
    data = [
        {"event_id": "e1", "title": "A", "event_time": "2024-01-01T10:00:00Z", "category": "macro"},
        {"event_id": "e2", "title": "B", "event_time": "2024-01-01T11:00:00Z", "category": "corp"},
    ]
    repo = EventsRepository(_FakeClient(data))
    result = repo.upcoming(limit=10, categories=["macro", "corp"])  # smoke: no errors
    assert isinstance(result, list)


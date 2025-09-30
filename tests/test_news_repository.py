import pytest
from typing import Any, List

from repositories.news_repository import NewsRepository
from models.news import NewsItem


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
def test_get_recent_news_returns_newsitem_list():
    data = [
        {
            "id": 1,
            "title": "N1",
            "content": "c",
            "published_at": "2024-01-01T10:00:00Z",
            "importance": 0.5,
        }
    ]
    repo = NewsRepository(_FakeClient(data))
    result = repo.get_recent_news(limit=1)
    assert isinstance(result, list)
    assert all(isinstance(x, NewsItem) for x in result)
    assert result[0].title == "N1"
    assert result[0].published_at_fmt is not None
    assert result[0].published_at_fmt.startswith("01 Jan 2024")


@pytest.mark.unit
def test_get_recent_news_category_filter_list():
    data = [
        {"id": 1, "title": "A", "content": "c", "category": "crypto"},
        {"id": 2, "title": "B", "content": "c", "category": "economy"},
    ]
    repo = NewsRepository(_FakeClient(data))
    result = repo.get_recent_news(limit=10, categories=["crypto", "economy"])  # smoke: no errors
    assert isinstance(result, list)


import pytest
from routes import news_routes


@pytest.mark.unit
def test_routes_import():
    """Модуль news_routes должен импортироваться и содержать router."""
    assert news_routes is not None
    assert hasattr(news_routes, "router")

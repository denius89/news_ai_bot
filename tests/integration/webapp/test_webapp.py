import pytest
import importlib


@pytest.mark.unit
def test_webapp_import():
    """Модуль webapp должен успешно импортироваться и содержать app"""
    mod = importlib.import_module("src.webapp")
    assert mod is not None
    assert hasattr(mod, "app"), "В модуле webapp должен быть объект Flask-приложения"


@pytest.mark.unit
def test_webapp_routes_import():
    """Blueprint news_bp должен импортироваться из routes.news_routes"""
    routes_mod = importlib.import_module("routes.news_routes")
    assert hasattr(routes_mod, "news_bp"), "В routes.news_routes должен быть news_bp"

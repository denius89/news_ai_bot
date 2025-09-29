import pytest
import importlib


@pytest.mark.unit
def test_webapp_import():
    """Модуль webapp должен успешно импортироваться"""
    mod = importlib.import_module("webapp")
    assert mod is not None

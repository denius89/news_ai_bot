"""
Интеграционный тест для main.py — проверяет, что модуль импортируется без ошибок.
"""

import importlib
import pytest


@pytest.mark.integration
def test_main_importable():
    """webapp.py должен импортироваться без ошибок"""
    module = importlib.import_module("src.webapp")
    assert module is not None

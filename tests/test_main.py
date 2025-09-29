"""
Интеграционный тест для main.py — проверяет, что модуль импортируется без ошибок.
"""

import importlib
import pytest


@pytest.mark.integration
def test_main_importable():
    """main.py должен импортироваться без ошибок"""
    module = importlib.import_module("main")
    assert module is not None

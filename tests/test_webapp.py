import importlib


def test_webapp_import():
    mod = importlib.import_module("webapp")
    assert mod is not None

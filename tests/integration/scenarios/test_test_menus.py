import importlib


def test_menus_module_imports():
    module = importlib.import_module("tests.integration.scenarios.test_menus")
    assert module is not None

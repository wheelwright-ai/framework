"""Tests for menu generator."""

from wai.cli.lib.menu_generator import MenuGenerator


def test_menu_generator_lists_options():
    menu = MenuGenerator()
    assert menu.show_main_menu is not None

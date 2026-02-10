"""Tests for new CLI main entry point."""

from wai.cli.main import create_parser


def test_parser_has_commands():
    parser = create_parser()
    help_text = parser.format_help()
    for command in ["init", "list", "status", "teach", "learn", "registry"]:
        assert command in help_text

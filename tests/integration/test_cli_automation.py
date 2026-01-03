import pytest

from tests.integration.cli_automation import CLIAutomation


def test_cli_automation_class_exists():
    if CLIAutomation is None:
        pytest.skip("CLIAutomation not available")
    assert hasattr(CLIAutomation, "__init__")

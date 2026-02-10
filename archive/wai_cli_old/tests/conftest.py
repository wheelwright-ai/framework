"""
Pytest configuration and fixtures for CLI tests.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_skills_jsonl():
    """Mock WAI-Skills.jsonl data."""
    return [
        {
            "id": "wai.init",
            "name": "Init",
            "cli_trigger": ["init"],
            "node_types": ["hub", "spoke"],
            "description": "Initialize hub or spoke"
        },
        {
            "id": "wai.learn",
            "name": "Learn",
            "cli_trigger": ["learn"],
            "node_types": ["spoke"],
            "description": "Push signals from spoke to hub"
        },
        {
            "id": "wai.teach",
            "name": "Teach",
            "cli_trigger": ["teach"],
            "node_types": ["spoke", "hub"],
            "description": "Pull templates from hub to spoke"
        }
    ]


@pytest.fixture
def mock_wai_state():
    """Mock WAI-State.json structure."""
    return {
        "wheel": {
            "version": "3.2.0",
            "node_type": "spoke",
            "name": "TestProject",
            "hub_id": "test-hub"
        },
        "_project_foundation": {
            "completed": True,
            "tech_stack": {
                "languages": ["Python"],
                "frameworks": ["FastAPI"]
            }
        }
    }


@pytest.fixture
def mock_console():
    """Mock Rich console for testing output."""
    from unittest.mock import MagicMock
    console = MagicMock()
    console.print = MagicMock()
    console.rule = MagicMock()
    return console


@pytest.fixture(autouse=True)
def no_tty(monkeypatch):
    """Simulate non-TTY environment for testing."""
    monkeypatch.setenv("TERM", "dumb")


@pytest.fixture
def capture_output(capsys):
    """Fixture to capture CLI output."""
    class OutputCapture:
        def __init__(self):
            self.capsys = capsys
        
        def get_output(self):
            captured = self.capsys.readouterr()
            return captured.out
        
        def get_all(self):
            captured = self.capsys.readouterr()
            return (captured.out, captured.err)
    
    return OutputCapture()


@pytest.fixture
def cli_runner():
    """Typer CliRunner for testing commands."""
    try:
        from typer.testing import CliRunner
        return CliRunner()
    except ImportError:
        # Fallback for testing without typer installed yet
        from unittest.mock import MagicMock
        return MagicMock()

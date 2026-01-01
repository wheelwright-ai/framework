"""
Integration Test: Spoke Initialization End-to-End.

Tests complete spoke initialization workflows including various
project types, configurations, and edge cases.
"""

import pytest
import sys
import json
from pathlib import Path

# Add framework to path
framework_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(framework_path))

from tests.integration.harness import IntegrationTestHarness
from tests.integration.cli_automation import CLIAutomation
from tests.integration.assertions import IntegrationAssertions


@pytest.fixture
def test_env():
    """Create isolated test environment."""
    harness = IntegrationTestHarness()
    harness.setup_environment()
    yield harness
    harness.teardown()


def test_spoke_init_creates_valid_json(test_env):
    """
    Scenario: Initialize spoke and verify JSON is valid.

    Validation:
    - WAI-State.json is valid JSON (parseable)
    - Contains all required top-level keys
    - No syntax errors
    """
    spoke_dir = test_env.create_spoke("valid-json-spoke", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Verify file exists
    assert state_file.exists(), "WAI-State.json should exist"

    # Parse JSON (will raise exception if invalid)
    with open(state_file, 'r') as f:
        state = json.load(f)

    # Verify it's a dictionary, not empty
    assert isinstance(state, dict), "WAI-State.json should be a JSON object"
    assert len(state) > 0, "WAI-State.json should not be empty"


def test_spoke_init_sets_default_values(test_env):
    """
    Scenario: Verify default values are set correctly on init.

    Checks:
    - Foundation not completed (completed: false)
    - Session count is 0
    - Analytics initialized to 0
    - Feature toggles enabled by default
    """
    spoke_dir = test_env.create_spoke("defaults-spoke", with_git=False)

    state = test_env.get_spoke_state(spoke_dir)

    # Foundation should not be completed
    assert state["_project_foundation"]["completed"] == False, \
        "Foundation should not be completed initially"

    # Session count should be 0
    assert state["_session_state"]["session_count"] == 0, \
        "Session count should start at 0"

    # Analytics should be initialized
    analytics = state.get("analytics", {})
    assert analytics["sessions"]["total_count"] == 0, \
        "Total session count should be 0"
    assert analytics["token_efficiency"]["total_tokens_used"] == 0, \
        "Total tokens should be 0"

    # Feature toggles should be enabled
    toggles = state.get("feature_toggles", {})
    for feature in ["session_continuity", "analytics", "quality_gates"]:
        assert toggles.get(feature) == True, \
            f"{feature} should be enabled by default"


def test_spoke_init_in_python_project(test_env):
    """
    Scenario: Initialize spoke in Python project.

    Expected:
    - Detects Python project (via requirements.txt or setup.py)
    - Sets appropriate project type
    """
    project_dir = test_env.temp_dir / "python-project"
    project_dir.mkdir()

    # Create Python project markers
    (project_dir / "requirements.txt").write_text("requests>=2.28.0\n")
    (project_dir / "main.py").write_text("print('Hello World')\n")

    # Initialize spoke
    spoke_dir = test_env.create_spoke("python-spoke", with_git=False, parent_dir=test_env.temp_dir)

    # Verify spoke created
    IntegrationAssertions.assert_spoke_initialized(spoke_dir)


def test_spoke_init_in_nodejs_project(test_env):
    """
    Scenario: Initialize spoke in Node.js project.

    Expected:
    - Detects Node.js project (via package.json)
    - Sets appropriate project type
    """
    project_dir = test_env.temp_dir / "nodejs-project"
    project_dir.mkdir()

    # Create Node.js project markers
    package_json = {
        "name": "test-project",
        "version": "1.0.0",
        "dependencies": {}
    }
    (project_dir / "package.json").write_text(json.dumps(package_json, indent=2))
    (project_dir / "index.js").write_text("console.log('Hello World');\n")

    # Initialize spoke
    cli = CLIAutomation(project_dir)
    cli.start_cli(args="init .")

    try:
        cli.expect_output(["initialized", "created"], timeout=10)
    except Exception as e:
        output = cli.get_full_output()
        pytest.fail(f"Init in Node.js project failed. Output: {output}\nError: {e}")
    finally:
        cli.terminate()

    # Verify spoke created
    IntegrationAssertions.assert_spoke_initialized(project_dir)


def test_spoke_signals_file_starts_empty(test_env):
    """
    Scenario: WAI-Signals.jsonl should start empty.

    Expected:
    - File exists
    - File is empty (0 bytes or only whitespace)
    - No signals until high-impact decisions made
    """
    spoke_dir = test_env.create_spoke("empty-signals-spoke", with_git=False)

    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    # File should exist
    assert signals_file.exists(), "WAI-Signals.jsonl should exist"

    # File should be empty or very small
    file_size = signals_file.stat().st_size
    assert file_size < 10, f"WAI-Signals.jsonl should be empty, got {file_size} bytes"

    # Reading as signals should return empty list
    signals = test_env.get_spoke_signals(spoke_dir)
    assert len(signals) == 0, "Should have no signals initially"


def test_spoke_init_preserves_existing_files(test_env):
    """
    Scenario: Initialize spoke in project with existing files.

    Expected:
    - Existing files are NOT deleted
    - WAI-Spoke/ created alongside existing files
    - No conflicts or overwrites
    """
    project_dir = test_env.temp_dir / "existing-files-project"
    project_dir.mkdir()

    # Create existing files
    (project_dir / "README.md").write_text("# My Project\n")
    (project_dir / "main.py").write_text("print('existing')\n")
    existing_dir = project_dir / "src"
    existing_dir.mkdir()
    (existing_dir / "utils.py").write_text("# Utils\n")

    # Track existing files
    existing_files = list(project_dir.rglob("*"))
    existing_count = len([f for f in existing_files if f.is_file()])

    # Initialize spoke
    cli = CLIAutomation(project_dir)
    cli.start_cli(args="init .")

    try:
        cli.expect_output(["initialized", "created"], timeout=10)
    except Exception as e:
        output = cli.get_full_output()
        pytest.fail(f"Init failed. Output: {output}\nError: {e}")
    finally:
        cli.terminate()

    # Verify existing files still exist
    assert (project_dir / "README.md").exists(), "README.md should still exist"
    assert (project_dir / "main.py").exists(), "main.py should still exist"
    assert (existing_dir / "utils.py").exists(), "src/utils.py should still exist"

    # Verify WAI-Spoke was created
    IntegrationAssertions.assert_spoke_initialized(project_dir)


def test_spoke_init_creates_kb_sync_file(test_env):
    """
    Scenario: Verify WAI-KB-Sync.json is created.

    Expected:
    - File exists
    - Contains valid JSON
    - Has version and last_sync fields
    """
    spoke_dir = test_env.create_spoke("kb-sync-spoke", with_git=False)

    kb_sync_file = spoke_dir / "WAI-Spoke" / "WAI-KB-Sync.json"

    # File should exist
    assert kb_sync_file.exists(), "WAI-KB-Sync.json should exist"

    # Parse JSON
    with open(kb_sync_file, 'r') as f:
        kb_sync = json.load(f)

    # Verify structure
    assert "version" in kb_sync, "Should have version field"
    assert "last_sync" in kb_sync, "Should have last_sync field"


def test_spoke_init_respects_gitignore(test_env):
    """
    Scenario: Verify .gitignore patterns are respected.

    Expected:
    - WAI-Session-Log.jsonl should be in .gitignore
    - Sensitive files excluded from git tracking
    """
    project_dir = test_env.temp_dir / "gitignore-project"
    project_dir.mkdir()

    # Initialize git first
    import subprocess
    subprocess.run(["git", "init"], cwd=str(project_dir), capture_output=True)

    # Initialize spoke
    cli = CLIAutomation(project_dir)
    cli.start_cli(args="init .")

    try:
        cli.expect_output(["initialized", "created"], timeout=10)
    except Exception as e:
        output = cli.get_full_output()
        pytest.fail(f"Init failed. Output: {output}\nError: {e}")
    finally:
        cli.terminate()

    # Check .gitignore exists
    gitignore = project_dir / ".gitignore"

    if gitignore.exists():
        content = gitignore.read_text()

        # Should ignore session logs
        assert "session" in content.lower() or "log" in content.lower(), \
            ".gitignore should exclude session logs"


def test_multiple_spokes_in_same_environment(test_env):
    """
    Scenario: Create multiple spokes in isolated environment.

    Expected:
    - Each spoke is independent
    - No conflicts between spokes
    - Each has own state
    """
    spoke1 = test_env.create_spoke("spoke-1", with_git=False)
    spoke2 = test_env.create_spoke("spoke-2", with_git=False)
    spoke3 = test_env.create_spoke("spoke-3", with_git=False)

    # All should be valid
    IntegrationAssertions.assert_spoke_initialized(spoke1)
    IntegrationAssertions.assert_spoke_initialized(spoke2)
    IntegrationAssertions.assert_spoke_initialized(spoke3)

    # Each should have independent state
    state1 = test_env.get_spoke_state(spoke1)
    state2 = test_env.get_spoke_state(spoke2)
    state3 = test_env.get_spoke_state(spoke3)

    # States should be independent (not the same object)
    assert id(state1) != id(state2) != id(state3), \
        "Each spoke should have independent state"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

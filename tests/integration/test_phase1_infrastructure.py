"""
Smoke test for Phase 1 integration test infrastructure.

Validates that core test components (harness, CLI automation, assertions)
work correctly before building full test scenarios.
"""

import pytest
import sys
from pathlib import Path

# Add framework to path for imports
framework_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(framework_path))

from tests.integration.harness import IntegrationTestHarness
from tests.integration.assertions import IntegrationAssertions
from tests.integration.config import get_config


@pytest.fixture
def test_harness():
    """Create and teardown test harness."""
    harness = IntegrationTestHarness()
    harness.setup_environment()
    yield harness
    harness.teardown()


def test_harness_setup_teardown(test_harness):
    """Test basic harness lifecycle."""
    assert test_harness.temp_dir is not None
    assert test_harness.temp_dir.exists()
    assert test_harness.temp_dir.is_dir()


def test_spoke_initialization(test_harness):
    """Test spoke creation via harness."""
    spoke_dir = test_harness.create_spoke("test-spoke", with_git=False)

    assert spoke_dir.exists()
    assert (spoke_dir / "WAI-Spoke").exists()

    # Validate structure using assertions
    IntegrationAssertions.assert_spoke_initialized(spoke_dir)


def test_feature_toggles(test_harness):
    """Test feature toggle manipulation."""
    spoke_dir = test_harness.create_spoke("toggle-test", with_git=False)

    # Set a feature toggle
    test_harness.set_feature_toggles(
        spoke_dir,
        session_continuity=False,
        quality_gates=False
    )

    # Verify toggles were set
    IntegrationAssertions.assert_feature_toggle(
        spoke_dir,
        "session_continuity",
        False
    )
    IntegrationAssertions.assert_feature_toggle(
        spoke_dir,
        "quality_gates",
        False
    )

    # Other toggles should still be True (defaults)
    IntegrationAssertions.assert_feature_toggle(
        spoke_dir,
        "analytics",
        True
    )


def test_spoke_state_access(test_harness):
    """Test reading spoke state."""
    spoke_dir = test_harness.create_spoke("state-test", with_git=False)

    state = test_harness.get_spoke_state(spoke_dir)

    # Verify required sections exist
    assert "wheelwright" in state  # Updated from _wheel_metadata
    assert "_project_foundation" in state
    assert "feature_toggles" in state
    assert "analytics" in state
    assert "_session_state" in state


def test_git_repository_creation(test_harness):
    """Test spoke with git repository."""
    spoke_dir = test_harness.create_spoke("git-test", with_git=True)

    # Verify git repo was created
    assert (spoke_dir / ".git").exists()

    # Verify initial commit exists
    IntegrationAssertions.assert_git_commit_created(
        spoke_dir,
        expected_message_pattern="Initial commit"
    )


def test_config_loading():
    """Test configuration system."""
    config = get_config()

    assert config is not None
    assert config.cli_command is not None
    assert config.framework_path is not None
    assert config.default_timeout > 0


def test_assertion_file_contains(tmp_path):
    """Test file content assertion."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello Wheelwright World!")

    # Should pass
    IntegrationAssertions.assert_file_contains(test_file, "Wheelwright")

    # Should fail
    with pytest.raises(AssertionError):
        IntegrationAssertions.assert_file_contains(test_file, "NotFound")


def test_assertion_json_schema(tmp_path):
    """Test JSON schema assertion."""
    import json

    test_file = tmp_path / "test.json"
    test_file.write_text(json.dumps({
        "name": "test",
        "count": 42,
        "enabled": True
    }))

    # Should pass
    IntegrationAssertions.assert_json_schema(test_file, {
        "name": str,
        "count": int,
        "enabled": bool
    })

    # Should fail - wrong type
    with pytest.raises(AssertionError):
        IntegrationAssertions.assert_json_schema(test_file, {
            "count": str  # count is int, not str
        })


if __name__ == "__main__":
    # Allow running directly for quick validation
    pytest.main([__file__, "-v"])

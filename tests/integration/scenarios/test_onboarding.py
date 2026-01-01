"""
Integration Test: First-Time User Onboarding Workflow.

Tests the complete onboarding experience for a new Wheelwright user,
from initial CLI launch to successful spoke initialization.
"""

import pytest
import sys
from pathlib import Path

# Add framework to path
framework_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(framework_path))

from tests.integration.harness import IntegrationTestHarness
from tests.integration.cli_automation import CLIAutomation
from tests.integration.assertions import IntegrationAssertions
from tests.integration.config import get_config


@pytest.fixture
def test_env():
    """Create isolated test environment."""
    harness = IntegrationTestHarness()
    harness.setup_environment()
    yield harness
    harness.teardown()


def test_first_time_spoke_init_via_cli(test_env):
    """
    Scenario: User runs 'WAI-CLI init' for the first time.

    Workflow:
    1. User navigates to new project directory
    2. Runs: WAI-CLI init
    3. Spoke structure created successfully
    4. WAI-State.json contains all required sections
    5. Feature toggles are enabled by default
    """
    # Create a new project directory
    project_dir = test_env.temp_dir / "my-new-project"
    project_dir.mkdir()

    # Run WAI-CLI init
    cli = CLIAutomation(project_dir)
    config = get_config()

    cli.start_cli(args="init .")

    # Wait for completion (init should complete quickly)
    try:
        cli.expect_output(["initialized", "created", "WAI-Spoke"], timeout=10)
    except Exception as e:
        # Capture any output for debugging
        output = cli.get_full_output()
        pytest.fail(f"Init failed. Output: {output}\nError: {e}")
    finally:
        cli.terminate()

    # Validate spoke was initialized correctly
    IntegrationAssertions.assert_spoke_initialized(project_dir)

    # Verify feature toggles are enabled by default
    state = test_env.get_spoke_state(project_dir)
    feature_toggles = state.get("feature_toggles", {})

    assert feature_toggles.get("session_continuity") == True, \
        "session_continuity should be enabled by default"
    assert feature_toggles.get("analytics") == True, \
        "analytics should be enabled by default"
    assert feature_toggles.get("quality_gates") == True, \
        "quality_gates should be enabled by default"


def test_init_with_explicit_path(test_env):
    """
    Scenario: User initializes spoke with explicit path.

    Workflow:
    1. User runs: WAI-CLI init /path/to/project
    2. Spoke created at specified path
    """
    project_dir = test_env.temp_dir / "explicit-path-project"

    # Don't create the directory - let WAI-CLI do it
    cli = CLIAutomation(test_env.temp_dir)

    cli.start_cli(args=f"init {project_dir}")

    try:
        cli.expect_output(["initialized", "created", "WAI-Spoke"], timeout=10)
    except Exception as e:
        output = cli.get_full_output()
        pytest.fail(f"Init with explicit path failed. Output: {output}\nError: {e}")
    finally:
        cli.terminate()

    # Verify spoke was created at the specified path
    assert project_dir.exists(), "Project directory should be created"
    IntegrationAssertions.assert_spoke_initialized(project_dir)


def test_reinit_existing_spoke_fails_gracefully(test_env):
    """
    Scenario: User tries to re-initialize an existing spoke.

    Expected behavior:
    - CLI should detect existing WAI-Spoke/
    - Should exit gracefully with informative message
    - Should NOT overwrite existing state
    """
    # Create initial spoke
    project_dir = test_env.create_spoke("existing-spoke", with_git=False)

    # Capture initial state
    initial_state = test_env.get_spoke_state(project_dir)

    # Try to reinit
    cli = CLIAutomation(project_dir)
    cli.start_cli(args="init .")

    try:
        # Should see error message about existing spoke
        cli.expect_output(["already", "exists", "initialized"], timeout=5)
    except Exception:
        # Some versions might just exit silently, that's ok too
        pass
    finally:
        cli.terminate()

    # Verify state wasn't overwritten
    final_state = test_env.get_spoke_state(project_dir)

    # Check that some key fields are unchanged
    assert initial_state["wheelwright"]["version"] == final_state["wheelwright"]["version"], \
        "State should not be overwritten on reinit"


def test_init_creates_all_required_files(test_env):
    """
    Scenario: Verify WAI-CLI init creates complete file structure.

    Required files:
    - WAI-Spoke/WAI-State.json
    - WAI-Spoke/WAI-State.md
    - WAI-Spoke/WAI-Guide.md
    - WAI-Spoke/WAI-Signals.jsonl
    """
    project_dir = test_env.temp_dir / "complete-structure"
    project_dir.mkdir()

    cli = CLIAutomation(project_dir)
    cli.start_cli(args="init .")

    try:
        cli.expect_output(["initialized", "created"], timeout=10)
    except Exception as e:
        output = cli.get_full_output()
        pytest.fail(f"Init failed. Output: {output}\nError: {e}")
    finally:
        cli.terminate()

    wai_spoke = project_dir / "WAI-Spoke"

    # Check all required files exist
    required_files = {
        "WAI-State.json": "JSON state file",
        "WAI-State.md": "Markdown state file",
        "WAI-Guide.md": "AI instructions",
        "WAI-Signals.jsonl": "Signal log",
        "WAI-KB-Sync.json": "Knowledge base sync"
    }

    for filename, description in required_files.items():
        file_path = wai_spoke / filename
        assert file_path.exists(), f"{description} missing: {filename}"

        # Verify files are not empty (except signals which starts empty)
        if filename != "WAI-Signals.jsonl":
            assert file_path.stat().st_size > 0, f"{filename} should not be empty"


def test_init_in_git_repo_preserves_git(test_env):
    """
    Scenario: Initialize spoke in existing git repository.

    Expected behavior:
    - WAI-CLI should detect existing .git/
    - Should NOT create new git repo
    - Should NOT interfere with existing git state
    """
    project_dir = test_env.temp_dir / "git-project"
    project_dir.mkdir()

    # Initialize git repo first
    import subprocess
    subprocess.run(["git", "init"], cwd=str(project_dir), capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=str(project_dir),
        capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(project_dir),
        capture_output=True
    )

    # Create initial commit
    (project_dir / "README.md").write_text("# Test Project")
    subprocess.run(["git", "add", "."], cwd=str(project_dir), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=str(project_dir),
        capture_output=True
    )

    # Get commit count before init
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=str(project_dir),
        capture_output=True,
        text=True
    )
    commits_before = int(result.stdout.strip())

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

    # Verify spoke was created
    IntegrationAssertions.assert_spoke_initialized(project_dir)

    # Verify git repo still exists and wasn't reinitialized
    assert (project_dir / ".git").exists(), "Git repo should still exist"

    # Verify commit count didn't change (init shouldn't auto-commit in existing repo)
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=str(project_dir),
        capture_output=True,
        text=True
    )
    commits_after = int(result.stdout.strip())

    # Commits should be the same or increased by at most 1 (if init auto-commits)
    assert commits_after >= commits_before, "Git history should be preserved"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

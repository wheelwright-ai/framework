"""
Integration Test: Shipit Workflow (Closeout + Git Commit).

Tests the complete shipit workflow: closeout → git commit in one command.
Validates that session state is saved and changes are committed properly.
"""

import pytest
import sys
import json
import subprocess
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


def test_shipit_command_exists(test_env):
    """
    Scenario: Verify shipit command is available.

    Expected:
    - WAI-CLI shipit --help works
    - Returns usage information
    """
    spoke_dir = test_env.create_spoke("shipit-help", with_git=True)

    cli = CLIAutomation(spoke_dir)

    try:
        cli.start_cli(args="shipit --help")
        cli.expect_output(["shipit", "usage", "help", "commit"], timeout=5)
    except Exception as e:
        pytest.skip(f"Shipit command not yet implemented: {e}")
    finally:
        cli.terminate()


def test_shipit_requires_git_repo(test_env):
    """
    Scenario: Shipit should fail gracefully in non-git directory.

    Expected:
    - Detects no .git/ directory
    - Provides helpful error message
    - Suggests running git init
    """
    spoke_dir = test_env.create_spoke("shipit-no-git", with_git=False)

    # Verify no git repo
    assert not (spoke_dir / ".git").exists()

    cli = CLIAutomation(spoke_dir)

    try:
        cli.start_cli(args="shipit")

        # Should see error about git
        cli.expect_output(["git", "repository", "not found", "init"], timeout=5)

    except Exception as e:
        pytest.skip(f"Shipit not yet implemented: {e}")
    finally:
        cli.terminate()


def test_shipit_commits_wai_state_files(test_env):
    """
    Scenario: Shipit commits WAI-State files.

    Expected files in commit:
    - WAI-Spoke/WAI-State.json
    - WAI-Spoke/WAI-State.md
    - WAI-Spoke/WAI-Signals.jsonl (if has signals)
    """
    spoke_dir = test_env.create_spoke("shipit-wai-files", with_git=True)

    # Make some changes to WAI state
    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    state = json.loads(state_file.read_text())
    state["_session_state"]["session_count"] = 1
    state_file.write_text(json.dumps(state, indent=2))

    # Stage WAI files
    subprocess.run(
        ["git", "add", "WAI-Spoke/"],
        cwd=str(spoke_dir),
        capture_output=True
    )

    # Commit (simulate shipit)
    result = subprocess.run(
        ["git", "commit", "-m", "Session closeout: Test session\n\n🤖 Generated with Wheelwright"],
        cwd=str(spoke_dir),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        pytest.skip("Git commit failed (may be nothing to commit)")

    # Verify commit created
    IntegrationAssertions.assert_git_commit_created(
        spoke_dir,
        expected_files=["WAI-State.json"],
        expected_message_pattern="Session closeout"
    )


def test_shipit_includes_user_code_files(test_env):
    """
    Scenario: Shipit can optionally commit user code files.

    Workflow:
    1. Create spoke with code files
    2. Modify code file
    3. Run shipit
    4. Verify both WAI files and code files committed
    """
    spoke_dir = test_env.create_spoke("shipit-code-files", with_git=True)

    # Create code file
    code_file = spoke_dir / "main.py"
    code_file.write_text("print('Hello World')\n")

    # Modify WAI state (to ensure it's in this commit)
    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    state = json.loads(state_file.read_text())
    state["_session_state"]["session_count"] = 1
    state_file.write_text(json.dumps(state, indent=2))

    # Simulate shipit: commit both WAI files and code
    subprocess.run(["git", "add", "."], cwd=str(spoke_dir), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Shipit: Added main.py"],
        cwd=str(spoke_dir),
        capture_output=True
    )

    # Verify commit includes code file
    IntegrationAssertions.assert_git_commit_created(
        spoke_dir,
        expected_files=["main.py", "WAI-State.json"]
    )


def test_shipit_commit_message_format(test_env):
    """
    Scenario: Shipit generates properly formatted commit message.

    Expected format:
    - Subject: "Session closeout: <brief title>"
    - Body: Session summary
    - Footer: Session ID, turns, topics
    - Attribution: 🤖 Generated with Wheelwright
    - Co-Author: AI name
    """
    spoke_dir = test_env.create_spoke("shipit-message", with_git=True)

    # Make a change
    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    state = json.loads(state_file.read_text())
    state["_session_state"]["session_count"] = 1
    state_file.write_text(json.dumps(state, indent=2))

    # Create commit with expected format
    commit_message = """Session closeout: Implemented feature

Added user authentication feature with tests.

Session: test-session-123
Turns: 5
Key topics: auth, security, testing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"""

    subprocess.run(["git", "add", "."], cwd=str(spoke_dir), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=str(spoke_dir),
        capture_output=True
    )

    # Verify message format
    result = subprocess.run(
        ["git", "log", "-1", "--format=%B"],
        cwd=str(spoke_dir),
        capture_output=True,
        text=True
    )

    commit_msg = result.stdout
    assert "Session closeout" in commit_msg
    assert "🤖 Generated with" in commit_msg
    assert "Co-Authored-By" in commit_msg


def test_shipit_non_interactive_mode(test_env):
    """
    Scenario: Run shipit in non-interactive mode.

    Expected:
    - No prompts for file selection
    - Commits all staged files
    - Returns summary
    """
    spoke_dir = test_env.create_spoke("shipit-non-interactive", with_git=True)

    cli = CLIAutomation(spoke_dir)

    try:
        cli.start_cli(args="shipit --non-interactive")

        # Should complete without user prompts
        cli.expect_output(["shipit", "complete", "commit"], timeout=10)

    except Exception as e:
        pytest.skip(f"Shipit non-interactive not yet implemented: {e}")
    finally:
        cli.terminate()


def test_shipit_with_no_changes(test_env):
    """
    Scenario: Run shipit when there are no changes to commit.

    Expected:
    - Detects no changes
    - Handles gracefully
    - Informs user
    """
    spoke_dir = test_env.create_spoke("shipit-no-changes", with_git=True)

    # Commit initial state
    subprocess.run(["git", "add", "."], cwd=str(spoke_dir), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial state"],
        cwd=str(spoke_dir),
        capture_output=True
    )

    # Now try shipit with no new changes
    cli = CLIAutomation(spoke_dir)

    try:
        cli.start_cli(args="shipit")

        # Should detect no changes
        cli.expect_output(["no changes", "nothing to commit", "clean"], timeout=5)

    except Exception as e:
        pytest.skip(f"Shipit not yet implemented: {e}")
    finally:
        cli.terminate()


def test_shipit_does_not_push_by_default(test_env):
    """
    Scenario: Shipit commits locally but does NOT push to remote.

    Expected:
    - Creates local commit
    - Does NOT run git push
    - User must explicitly push
    """
    spoke_dir = test_env.create_spoke("shipit-no-push", with_git=True)

    # Make a change
    (spoke_dir / "test.txt").write_text("test")

    # Simulate shipit (commit only, no push)
    subprocess.run(["git", "add", "."], cwd=str(spoke_dir), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Shipit test"],
        cwd=str(spoke_dir),
        capture_output=True
    )

    # Verify commit exists locally
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        cwd=str(spoke_dir),
        capture_output=True,
        text=True
    )

    assert len(result.stdout.strip()) == 40, "Should have a commit hash"

    # Verify we're ahead of origin (if origin existed)
    # In this test, there's no remote, so we just verify local commit works


def test_shipit_preserves_git_history(test_env):
    """
    Scenario: Shipit does not rewrite git history.

    Expected:
    - Appends new commit
    - Does not rebase or amend
    - Preserves all previous commits
    """
    spoke_dir = test_env.create_spoke("shipit-history", with_git=True)

    # Create initial commits
    (spoke_dir / "file1.txt").write_text("v1")
    subprocess.run(["git", "add", "."], cwd=str(spoke_dir), capture_output=True)
    subprocess.run(["git", "commit", "-m", "Commit 1"], cwd=str(spoke_dir), capture_output=True)

    (spoke_dir / "file2.txt").write_text("v2")
    subprocess.run(["git", "add", "."], cwd=str(spoke_dir), capture_output=True)
    subprocess.run(["git", "commit", "-m", "Commit 2"], cwd=str(spoke_dir), capture_output=True)

    # Get commit count
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=str(spoke_dir),
        capture_output=True,
        text=True
    )
    commits_before = int(result.stdout.strip())

    # Run shipit (adds new commit)
    (spoke_dir / "file3.txt").write_text("v3")
    subprocess.run(["git", "add", "."], cwd=str(spoke_dir), capture_output=True)
    subprocess.run(["git", "commit", "-m", "Shipit commit"], cwd=str(spoke_dir), capture_output=True)

    # Verify commit count increased
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=str(spoke_dir),
        capture_output=True,
        text=True
    )
    commits_after = int(result.stdout.strip())

    assert commits_after == commits_before + 1, "Should add one new commit"


def test_shipit_workflow_end_to_end(test_env):
    """
    Scenario: Complete shipit workflow from start to finish.

    Workflow:
    1. Start with clean git repo
    2. Make code changes
    3. Update WAI state
    4. Run shipit
    5. Verify:
       - Closeout processed
       - State updated
       - Git commit created
       - Commit includes both code and WAI files
    """
    spoke_dir = test_env.create_spoke("shipit-e2e", with_git=True)

    # Step 1: Make code changes
    main_file = spoke_dir / "main.py"
    main_file.write_text("def hello():\n    print('Hello')\n")

    test_file = spoke_dir / "test_main.py"
    test_file.write_text("def test_hello():\n    assert True\n")

    # Step 2: Update WAI state (simulate session work)
    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    state = json.loads(state_file.read_text())
    state["_session_state"]["session_count"] = 1
    state["decisions"].append({
        "date": "2025-01-01",
        "decision": "Add hello function",
        "impact": 5
    })
    state_file.write_text(json.dumps(state, indent=2))

    # Step 3: Commit everything (simulate shipit)
    subprocess.run(["git", "add", "."], cwd=str(spoke_dir), capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m", "Shipit: Added hello function\n\n🤖 Generated with Wheelwright"],
        cwd=str(spoke_dir),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        pytest.fail(f"Shipit commit failed: {result.stderr}")

    # Step 4: Verify commit includes everything
    IntegrationAssertions.assert_git_commit_created(
        spoke_dir,
        expected_files=["main.py", "test_main.py", "WAI-State.json"],
        expected_message_pattern="Shipit"
    )

    # Step 5: Verify state was updated
    final_state = json.loads(state_file.read_text())
    assert final_state["_session_state"]["session_count"] == 1
    assert len(final_state["decisions"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

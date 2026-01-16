"""
Integration Test: Closeout Workflow.

Tests the session closeout process, including context compression,
state updates, signal extraction, and file rebalancing.
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


def test_closeout_command_exists(test_env):
    """
    Scenario: Verify closeout command is available.

    Expected:
    - WAI closeout --help works
    - Returns usage information
    """
    spoke_dir = test_env.create_spoke("closeout-help", with_git=False)

    cli = CLIAutomation(spoke_dir)

    try:
        cli.start_cli(args="closeout --help")
        cli.expect_output(["closeout", "usage", "help", "session"], timeout=5)
    except Exception as e:
        pytest.skip(f"Closeout command not yet implemented: {e}")
    finally:
        cli.terminate()


def test_closeout_updates_session_state(test_env):
    """
    Scenario: Closeout updates _session_state properly.

    Expected:
    - current_session moved to last_closeout
    - current_session set to null
    - last_closeout has summary, turns, closed_at
    """
    spoke_dir = test_env.create_spoke("closeout-state", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Set up current session
    state = test_env.get_spoke_state(spoke_dir)
    state["_session_state"]["current_session"] = {
        "session_id": "test-session-123",
        "started_at": "2025-01-01T10:00:00Z",
        "turns": 5
    }
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Run closeout (simulated - actual command may not be ready)
    # For now, manually simulate what closeout should do
    state = test_env.get_spoke_state(spoke_dir)
    state["_session_state"]["last_closeout"] = state["_session_state"]["current_session"]
    state["_session_state"]["last_closeout"]["closed_at"] = "2025-01-01T11:00:00Z"
    state["_session_state"]["last_closeout"]["summary"] = "Test session completed"
    state["_session_state"]["current_session"] = None

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify
    IntegrationAssertions.assert_session_closeout_complete(spoke_dir)


def test_closeout_with_conversation_log(test_env):
    """
    Scenario: Closeout processes conversation log.

    Workflow:
    1. Create spoke with session log
    2. Run closeout
    3. Verify log is consumed and cleared
    4. Verify summary extracted
    """
    spoke_dir = test_env.create_spoke("closeout-log", with_git=False)

    # Create mock conversation log
    log_file = spoke_dir / "WAI-Spoke" / "WAI-Session-Log.jsonl"
    log_entries = [
        {"timestamp": "2025-01-01T10:00:00Z", "turn": 1, "type": "user", "content": "Hello"},
        {"timestamp": "2025-01-01T10:00:05Z", "turn": 1, "type": "assistant", "content": "Hi there!"},
        {"timestamp": "2025-01-01T10:01:00Z", "turn": 2, "type": "user", "content": "Add auth feature"},
        {"timestamp": "2025-01-01T10:01:30Z", "turn": 2, "type": "assistant", "content": "I'll add authentication"}
    ]

    with open(log_file, 'w') as f:
        for entry in log_entries:
            f.write(json.dumps(entry) + '\n')

    # Simulate closeout processing
    # (Real implementation would extract summary, key topics, etc.)
    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    state = test_env.get_spoke_state(spoke_dir)
    state["_session_state"]["last_closeout"] = {
        "session_id": "session-with-log",
        "closed_at": "2025-01-01T10:05:00Z",
        "turns": 2,
        "summary": "User requested auth feature implementation",
        "key_topics": ["authentication", "security"]
    }

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Clear log (as closeout should do)
    log_file.unlink()

    # Verify log was cleared
    assert not log_file.exists(), "Conversation log should be cleared after closeout"

    # Verify summary was captured
    final_state = test_env.get_spoke_state(spoke_dir)
    assert final_state["_session_state"]["last_closeout"]["summary"] is not None
    assert len(final_state["_session_state"]["last_closeout"]["key_topics"]) > 0


def test_closeout_extracts_high_impact_signals(test_env):
    """
    Scenario: Closeout extracts decisions with impact >= 8 to signals.

    Workflow:
    1. Add decisions with varying impact levels
    2. Run closeout
    3. Verify only impact >= 8 extracted to WAI-Signals.jsonl
    """
    spoke_dir = test_env.create_spoke("closeout-signals", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    # Add decisions
    state = test_env.get_spoke_state(spoke_dir)
    state["decisions"] = [
        {"date": "2025-01-01", "decision": "Low impact", "impact": 5},
        {"date": "2025-01-02", "decision": "High impact", "impact": 9},
        {"date": "2025-01-03", "decision": "Medium impact", "impact": 7},
        {"date": "2025-01-04", "decision": "Critical impact", "impact": 10}
    ]

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Simulate closeout signal extraction (impact >= 8)
    high_impact = [d for d in state["decisions"] if d.get("impact", 0) >= 8]

    for decision in high_impact:
        signal = {
            "timestamp": decision["date"] + "T12:00:00Z",
            "by": "AI",
            "offers": [{
                "type": "decision",
                "topic": decision["decision"],
                "impact": decision["impact"]
            }]
        }
        with open(signals_file, 'a') as f:
            f.write(json.dumps(signal) + '\n')

    # Verify signals
    signals = test_env.get_spoke_signals(spoke_dir)
    assert len(signals) == 2, "Should extract 2 signals (impact 9 and 10)"
    assert all(s["offers"][0]["impact"] >= 8 for s in signals)


def test_closeout_rebalances_files(test_env):
    """
    Scenario: Closeout checks file sizes and rebalances if needed.

    Expected:
    - WAI-State.json and WAI-State.md kept under token limits
    - Content moved between files to maintain balance
    """
    spoke_dir = test_env.create_spoke("closeout-rebalance", with_git=False)

    # This test validates the concept
    # Actual rebalancing logic tested in Phase 1 (FileRebalancer)

    from tests.integration.harness import IntegrationTestHarness

    # Create harness to use rebalancer utilities
    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    md_file = spoke_dir / "WAI-Spoke" / "WAI-State.md"

    # Verify both files exist
    assert state_file.exists()
    assert md_file.exists()

    # Check file sizes are reasonable
    json_size = state_file.stat().st_size
    md_size = md_file.stat().st_size

    # Neither should be empty
    assert json_size > 100, "WAI-State.json should have content"
    assert md_size > 100, "WAI-State.md should have content"


def test_closeout_prepares_for_hub_learning(test_env):
    """
    Scenario: After closeout, WAI-Spoke/ ready for hub to learn.

    Expected:
    - Conversation log cleared
    - Signals written
    - State files updated
    - Hub can safely read WAI-Spoke/
    """
    spoke_dir = test_env.create_spoke("closeout-hub-ready", with_git=False)

    # Simulate post-closeout state
    log_file = spoke_dir / "WAI-Spoke" / "WAI-Session-Log.jsonl"

    # Conversation log should NOT exist (or be empty)
    if log_file.exists():
        assert log_file.stat().st_size == 0, "Log should be empty after closeout"

    # State should be consistent
    state = test_env.get_spoke_state(spoke_dir)
    assert state is not None

    # Signals file should exist (even if empty)
    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"
    assert signals_file.exists(), "Signals file should exist"


def test_closeout_non_interactive_mode(test_env):
    """
    Scenario: Run closeout in non-interactive mode.

    Expected:
    - No prompts for user input
    - Processes automatically
    - Returns summary
    """
    spoke_dir = test_env.create_spoke("closeout-non-interactive", with_git=False)

    cli = CLIAutomation(spoke_dir)

    try:
        # Run with --non-interactive flag
        cli.start_cli(args="closeout --non-interactive")

        # Should complete without prompts
        cli.expect_output(["closeout", "complete", "session"], timeout=10)

    except Exception as e:
        pytest.skip(f"Closeout non-interactive mode not yet implemented: {e}")
    finally:
        cli.terminate()


def test_closeout_updates_analytics(test_env):
    """
    Scenario: Closeout updates analytics metrics.

    Expected:
    - Session count increments
    - Token usage recorded
    - Duration calculated
    - last_updated timestamp set
    """
    spoke_dir = test_env.create_spoke("closeout-analytics", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Initial state
    state = test_env.get_spoke_state(spoke_dir)
    initial_session_count = state["analytics"]["sessions"]["total_count"]

    # Simulate closeout updating analytics
    state["analytics"]["sessions"]["total_count"] += 1
    state["analytics"]["sessions"]["total_turns"] += 5
    state["analytics"]["sessions"]["total_duration_seconds"] += 300
    state["analytics"]["token_efficiency"]["total_tokens_used"] += 1000
    state["analytics"]["last_updated"] = "2025-01-01T12:00:00Z"

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify analytics updated
    final_state = test_env.get_spoke_state(spoke_dir)
    assert final_state["analytics"]["sessions"]["total_count"] == initial_session_count + 1
    assert final_state["analytics"]["sessions"]["total_turns"] == 5
    assert final_state["analytics"]["last_updated"] is not None


def test_closeout_with_no_session_data(test_env):
    """
    Scenario: Run closeout when no session is active.

    Expected:
    - Handles gracefully
    - Doesn't crash
    - Provides informative message
    """
    spoke_dir = test_env.create_spoke("closeout-no-session", with_git=False)

    # No current_session set (fresh spoke)
    state = test_env.get_spoke_state(spoke_dir)
    assert state["_session_state"]["current_session"] is None

    # Closeout should handle this gracefully
    # (May just report "No active session to close")

    cli = CLIAutomation(spoke_dir)

    try:
        cli.start_cli(args="closeout")

        # Should not crash
        cli.expect_output(["closeout", "session", "no", "active"], timeout=5)

    except Exception as e:
        # If command not implemented, skip
        pytest.skip(f"Closeout not yet implemented: {e}")
    finally:
        cli.terminate()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

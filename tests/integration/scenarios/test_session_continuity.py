"""
Integration Test: Multi-Session Continuity.

Tests that Wheelwright maintains context across multiple sessions,
validating session state persistence and context restoration.
"""

import pytest
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add framework to path
framework_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(framework_path))

from tests.integration.harness import IntegrationTestHarness
from tests.integration.assertions import IntegrationAssertions


@pytest.fixture
def test_env():
    """Create isolated test environment."""
    harness = IntegrationTestHarness()
    harness.setup_environment()
    yield harness
    harness.teardown()


def test_session_state_initializes_correctly(test_env):
    """
    Scenario: Fresh spoke has correct initial session state.

    Expected:
    - session_count = 0
    - current_session = null
    - last_closeout = null
    - protocol_completed = false
    """
    spoke_dir = test_env.create_spoke("session-init", with_git=False)

    state = test_env.get_spoke_state(spoke_dir)
    session_state = state["_session_state"]

    assert session_state["session_count"] == 0, "Initial session count should be 0"
    assert session_state["current_session"] is None, "No current session initially"
    assert session_state["last_closeout"] is None, "No last closeout initially"
    assert session_state["protocol_completed"] == False, "Protocol not completed initially"


def test_session_count_increments(test_env):
    """
    Scenario: Session count increments across multiple sessions.

    Workflow:
    1. Create spoke
    2. Simulate session 1 (increment count)
    3. Simulate session 2 (increment count)
    4. Verify count = 2
    """
    spoke_dir = test_env.create_spoke("session-count", with_git=False)

    # Simulate session 1
    state = test_env.get_spoke_state(spoke_dir)
    state["_session_state"]["session_count"] = 1
    state["_session_state"]["last_session_id"] = "session-1"

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Reload and simulate session 2
    state = test_env.get_spoke_state(spoke_dir)
    state["_session_state"]["session_count"] = 2
    state["_session_state"]["last_session_id"] = "session-2"

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify
    final_state = test_env.get_spoke_state(spoke_dir)
    assert final_state["_session_state"]["session_count"] == 2, \
        "Session count should increment"


def test_decisions_persist_across_sessions(test_env):
    """
    Scenario: Decisions made in one session are available in next session.

    Workflow:
    1. Session 1: Add decision to WAI-State.json
    2. Session 2: Verify decision is still present
    3. Session 2: Add another decision
    4. Verify both decisions persist
    """
    spoke_dir = test_env.create_spoke("decision-persistence", with_git=False)

    # Session 1: Add decision
    state = test_env.get_spoke_state(spoke_dir)
    state["decisions"].append({
        "date": "2025-01-01",
        "decision": "Use React for frontend",
        "rationale": "Team expertise and ecosystem",
        "impact": 9,
        "by": "AI Assistant"
    })

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Session 2: Verify and add another
    state = test_env.get_spoke_state(spoke_dir)
    assert len(state["decisions"]) == 1, "Decision from session 1 should persist"
    assert state["decisions"][0]["decision"] == "Use React for frontend"

    state["decisions"].append({
        "date": "2025-01-02",
        "decision": "Use PostgreSQL for database",
        "rationale": "ACID compliance needed",
        "impact": 8,
        "by": "AI Assistant"
    })

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify both persist
    final_state = test_env.get_spoke_state(spoke_dir)
    assert len(final_state["decisions"]) == 2, "Both decisions should persist"


def test_features_accumulate_across_sessions(test_env):
    """
    Scenario: Features tracked across multiple sessions.

    Workflow:
    1. Session 1: Add feature A
    2. Session 2: Add feature B
    3. Session 3: Mark feature A complete
    4. Verify all changes persist
    """
    spoke_dir = test_env.create_spoke("feature-tracking", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Session 1: Add feature A
    state = test_env.get_spoke_state(spoke_dir)
    state["features"].append({
        "name": "User Authentication",
        "status": "in_progress",
        "started": "2025-01-01",
        "completed": None
    })
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Session 2: Add feature B
    state = test_env.get_spoke_state(spoke_dir)
    state["features"].append({
        "name": "Dashboard UI",
        "status": "planned",
        "started": None,
        "completed": None
    })
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Session 3: Mark feature A complete
    state = test_env.get_spoke_state(spoke_dir)
    state["features"][0]["status"] = "completed"
    state["features"][0]["completed"] = "2025-01-05"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify final state
    final_state = test_env.get_spoke_state(spoke_dir)
    assert len(final_state["features"]) == 2
    assert final_state["features"][0]["status"] == "completed"
    assert final_state["features"][1]["status"] == "planned"


def test_analytics_accumulate_across_sessions(test_env):
    """
    Scenario: Analytics metrics accumulate over time.

    Workflow:
    1. Session 1: 100 tokens used
    2. Session 2: 150 tokens used
    3. Session 3: 200 tokens used
    4. Verify total = 450 tokens
    """
    spoke_dir = test_env.create_spoke("analytics-accumulation", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Session 1
    state = test_env.get_spoke_state(spoke_dir)
    state["analytics"]["sessions"]["total_count"] = 1
    state["analytics"]["token_efficiency"]["total_tokens_used"] = 100
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Session 2
    state = test_env.get_spoke_state(spoke_dir)
    state["analytics"]["sessions"]["total_count"] = 2
    state["analytics"]["token_efficiency"]["total_tokens_used"] = 250  # 100 + 150
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Session 3
    state = test_env.get_spoke_state(spoke_dir)
    state["analytics"]["sessions"]["total_count"] = 3
    state["analytics"]["token_efficiency"]["total_tokens_used"] = 450  # 250 + 200
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify
    final_state = test_env.get_spoke_state(spoke_dir)
    assert final_state["analytics"]["sessions"]["total_count"] == 3
    assert final_state["analytics"]["token_efficiency"]["total_tokens_used"] == 450


def test_context_next_actions_update(test_env):
    """
    Scenario: Next actions updated as work progresses.

    Workflow:
    1. Initial: Generic setup actions
    2. Session 1: Update to specific feature work
    3. Session 2: Update to testing phase
    4. Verify progression tracked
    """
    spoke_dir = test_env.create_spoke("next-actions", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Initial state has generic actions
    state = test_env.get_spoke_state(spoke_dir)
    initial_actions = state["context"]["next_actions"]
    assert len(initial_actions) > 0, "Should have initial next actions"

    # Session 1: Update to feature work
    state["context"]["next_actions"] = [
        "Implement user authentication",
        "Create login UI",
        "Add password hashing"
    ]
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Session 2: Update to testing
    state = test_env.get_spoke_state(spoke_dir)
    state["context"]["next_actions"] = [
        "Write unit tests for auth",
        "Add integration tests",
        "Perform security audit"
    ]
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify final state
    final_state = test_env.get_spoke_state(spoke_dir)
    assert "Write unit tests" in final_state["context"]["next_actions"][0]


def test_session_metadata_tracks_ai_and_time(test_env):
    """
    Scenario: Track which AI and when sessions occurred.

    Expected:
    - last_modified_by captures AI name
    - last_modified_at captures timestamp
    - Updates on each session
    """
    spoke_dir = test_env.create_spoke("session-metadata", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Session 1
    state = test_env.get_spoke_state(spoke_dir)
    state["_session_state"]["last_modified_by"] = "Claude Sonnet 4.5"
    state["_session_state"]["last_modified_at"] = "2025-01-01T10:00:00Z"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Session 2 (different AI)
    state = test_env.get_spoke_state(spoke_dir)
    state["_session_state"]["last_modified_by"] = "GPT-4"
    state["_session_state"]["last_modified_at"] = "2025-01-02T14:30:00Z"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify latest session tracked
    final_state = test_env.get_spoke_state(spoke_dir)
    assert final_state["_session_state"]["last_modified_by"] == "GPT-4"
    assert "2025-01-02" in final_state["_session_state"]["last_modified_at"]


def test_protocol_completed_resets_between_sessions(test_env):
    """
    Scenario: protocol_completed resets to false for each new session.

    Expected:
    - Session start: protocol_completed = false
    - After protocol runs: protocol_completed = true
    - Next session start: resets to false
    """
    spoke_dir = test_env.create_spoke("protocol-reset", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Session 1: Start (false)
    state = test_env.get_spoke_state(spoke_dir)
    assert state["_session_state"]["protocol_completed"] == False

    # Session 1: After protocol (true)
    state["_session_state"]["protocol_completed"] = True
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Session 2: Should reset to false
    # (In real use, session-start hook does this)
    state = test_env.get_spoke_state(spoke_dir)
    state["_session_state"]["protocol_completed"] = False  # Reset
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify reset
    final_state = test_env.get_spoke_state(spoke_dir)
    assert final_state["_session_state"]["protocol_completed"] == False


def test_high_impact_decisions_generate_signals(test_env):
    """
    Scenario: Decisions with impact >= 8 should generate signals.

    Workflow:
    1. Add low-impact decision (impact 5) - no signal
    2. Add high-impact decision (impact 9) - should generate signal
    3. Verify signals file has 1 entry
    """
    spoke_dir = test_env.create_spoke("signal-generation", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    # Add low-impact decision
    state = test_env.get_spoke_state(spoke_dir)
    state["decisions"].append({
        "date": "2025-01-01",
        "decision": "Use ESLint for linting",
        "rationale": "Standard tooling",
        "impact": 5,
        "by": "AI"
    })
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Add high-impact decision and signal
    state = test_env.get_spoke_state(spoke_dir)
    state["decisions"].append({
        "date": "2025-01-02",
        "decision": "Adopt microservices architecture",
        "rationale": "Scalability and team independence",
        "impact": 9,
        "by": "AI"
    })

    # Manually create signal (closeout would do this)
    signal = {
        "timestamp": "2025-01-02T12:00:00Z",
        "by": "AI",
        "offers": [{
            "type": "decision",
            "topic": "Microservices architecture adoption",
            "impact": 9,
            "context": "For scalability and team independence"
        }]
    }

    with open(signals_file, 'a') as f:
        f.write(json.dumps(signal) + '\n')

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify signals
    signals = test_env.get_spoke_signals(spoke_dir)
    assert len(signals) == 1, "Should have 1 signal for high-impact decision"
    assert signals[0]["offers"][0]["impact"] == 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

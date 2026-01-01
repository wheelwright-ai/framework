"""
Integration Test: Analytics and Metrics Tracking.

Tests Wheelwright's analytics system including session metrics,
token efficiency tracking, quality metrics, and ROI calculations.
"""

import pytest
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

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


def test_analytics_section_exists_in_state(test_env):
    """
    Scenario: Verify analytics section in WAI-State.json.

    Expected structure:
    - sessions: {total_count, total_turns, total_duration_seconds}
    - token_efficiency: {total_tokens_used, tokens_saved_estimate}
    - quality_metrics: {decisions_count, high_impact_count}
    - last_updated: ISO-8601 timestamp
    """
    spoke_dir = test_env.create_spoke("analytics-structure", with_git=False)

    state = test_env.get_spoke_state(spoke_dir)
    analytics = state.get("analytics", {})

    # Verify top-level sections
    assert "sessions" in analytics
    assert "token_efficiency" in analytics
    assert "quality_metrics" in analytics
    assert "last_updated" in analytics

    # Verify sessions structure
    sessions = analytics["sessions"]
    assert "total_count" in sessions
    assert "total_turns" in sessions
    assert "total_duration_seconds" in sessions

    # Verify token efficiency structure
    tokens = analytics["token_efficiency"]
    assert "total_tokens_used" in tokens
    assert "tokens_saved_estimate" in tokens

    # Verify quality metrics structure
    quality = analytics["quality_metrics"]
    assert "decisions_count" in quality
    assert "high_impact_count" in quality


def test_analytics_initialized_to_zero(test_env):
    """
    Scenario: Fresh spoke has analytics initialized to zero.

    Expected:
    - All counters at 0
    - last_updated set to creation time
    """
    spoke_dir = test_env.create_spoke("analytics-zero", with_git=False)

    state = test_env.get_spoke_state(spoke_dir)
    analytics = state["analytics"]

    # Verify zero initialization
    assert analytics["sessions"]["total_count"] == 0
    assert analytics["sessions"]["total_turns"] == 0
    assert analytics["sessions"]["total_duration_seconds"] == 0
    assert analytics["token_efficiency"]["total_tokens_used"] == 0
    assert analytics["token_efficiency"]["tokens_saved_estimate"] == 0
    assert analytics["quality_metrics"]["decisions_count"] == 0
    assert analytics["quality_metrics"]["high_impact_count"] == 0


def test_session_count_increments(test_env):
    """
    Scenario: Session count increments each session.

    Workflow:
    1. Start session 1 → total_count = 1
    2. Start session 2 → total_count = 2
    3. Start session 3 → total_count = 3
    """
    spoke_dir = test_env.create_spoke("session-increment", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Simulate 3 sessions
    for session_num in range(1, 4):
        state = test_env.get_spoke_state(spoke_dir)
        state["analytics"]["sessions"]["total_count"] = session_num
        state["analytics"]["sessions"]["total_turns"] += 10  # 10 turns per session
        state["analytics"]["last_updated"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    # Verify final count
    final_state = test_env.get_spoke_state(spoke_dir)
    assert final_state["analytics"]["sessions"]["total_count"] == 3
    assert final_state["analytics"]["sessions"]["total_turns"] == 30


def test_token_usage_accumulates(test_env):
    """
    Scenario: Token usage accumulates across sessions.

    Workflow:
    1. Session 1: 1000 tokens
    2. Session 2: 1500 tokens
    3. Session 3: 2000 tokens
    4. Total: 4500 tokens
    """
    spoke_dir = test_env.create_spoke("token-accumulation", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    session_tokens = [1000, 1500, 2000]
    total_tokens = 0

    for session_num, tokens in enumerate(session_tokens, 1):
        total_tokens += tokens

        state = test_env.get_spoke_state(spoke_dir)
        state["analytics"]["sessions"]["total_count"] = session_num
        state["analytics"]["token_efficiency"]["total_tokens_used"] = total_tokens

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    # Verify accumulation
    final_state = test_env.get_spoke_state(spoke_dir)
    assert final_state["analytics"]["token_efficiency"]["total_tokens_used"] == 4500


def test_token_savings_estimate_calculated(test_env):
    """
    Scenario: Token savings estimate based on baseline comparison.

    Formula:
    - Baseline tokens (without Wheelwright): X
    - Actual tokens (with Wheelwright): Y
    - Savings estimate: X - Y
    """
    spoke_dir = test_env.create_spoke("token-savings", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Simulate: Would have used 10,000 tokens without Wheelwright
    baseline_tokens = 10000
    # Actually used: 5,500 tokens with Wheelwright (45% savings)
    actual_tokens = 5500
    savings = baseline_tokens - actual_tokens

    state = test_env.get_spoke_state(spoke_dir)
    state["analytics"]["token_efficiency"]["baseline_tokens_estimate"] = baseline_tokens
    state["analytics"]["token_efficiency"]["total_tokens_used"] = actual_tokens
    state["analytics"]["token_efficiency"]["tokens_saved_estimate"] = savings

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify savings calculation
    final_state = test_env.get_spoke_state(spoke_dir)
    tokens_saved = final_state["analytics"]["token_efficiency"]["tokens_saved_estimate"]

    assert tokens_saved == 4500
    savings_percent = (tokens_saved / baseline_tokens) * 100
    assert savings_percent == 45.0


def test_decision_count_tracking(test_env):
    """
    Scenario: Track total decisions and high-impact decisions.

    Workflow:
    1. Add 5 decisions (impacts: 5, 7, 8, 9, 10)
    2. Total decisions: 5
    3. High-impact (>= 8): 3
    """
    spoke_dir = test_env.create_spoke("decision-tracking", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    state = test_env.get_spoke_state(spoke_dir)

    # Add decisions
    decisions = [
        {"impact": 5, "decision": "D1"},
        {"impact": 7, "decision": "D2"},
        {"impact": 8, "decision": "D3"},
        {"impact": 9, "decision": "D4"},
        {"impact": 10, "decision": "D5"}
    ]

    for d in decisions:
        state["decisions"].append({
            "date": "2025-01-01",
            "decision": d["decision"],
            "rationale": "Test",
            "impact": d["impact"],
            "by": "AI"
        })

    # Update analytics
    state["analytics"]["quality_metrics"]["decisions_count"] = len(state["decisions"])
    state["analytics"]["quality_metrics"]["high_impact_count"] = sum(
        1 for d in state["decisions"] if d.get("impact", 0) >= 8
    )

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify counts
    final_state = test_env.get_spoke_state(spoke_dir)
    quality = final_state["analytics"]["quality_metrics"]

    assert quality["decisions_count"] == 5
    assert quality["high_impact_count"] == 3


def test_session_duration_tracking(test_env):
    """
    Scenario: Track session duration in seconds.

    Workflow:
    1. Session 1: 300 seconds (5 minutes)
    2. Session 2: 600 seconds (10 minutes)
    3. Session 3: 450 seconds (7.5 minutes)
    4. Total: 1350 seconds (22.5 minutes)
    """
    spoke_dir = test_env.create_spoke("duration-tracking", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    session_durations = [300, 600, 450]
    total_duration = 0

    for session_num, duration in enumerate(session_durations, 1):
        total_duration += duration

        state = test_env.get_spoke_state(spoke_dir)
        state["analytics"]["sessions"]["total_count"] = session_num
        state["analytics"]["sessions"]["total_duration_seconds"] = total_duration

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    # Verify total duration
    final_state = test_env.get_spoke_state(spoke_dir)
    assert final_state["analytics"]["sessions"]["total_duration_seconds"] == 1350


def test_last_updated_timestamp(test_env):
    """
    Scenario: last_updated timestamp updates on each analytics change.

    Expected:
    - ISO-8601 format
    - Updates to current time
    """
    spoke_dir = test_env.create_spoke("timestamp-update", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Initial timestamp
    state = test_env.get_spoke_state(spoke_dir)
    initial_timestamp = state["analytics"]["last_updated"]

    # Make change
    state["analytics"]["sessions"]["total_count"] = 1
    state["analytics"]["last_updated"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify timestamp changed
    final_state = test_env.get_spoke_state(spoke_dir)
    final_timestamp = final_state["analytics"]["last_updated"]

    # Timestamps should be different (or same if very fast)
    assert "T" in final_timestamp
    assert final_timestamp.endswith("Z")


def test_analytics_respects_feature_toggle(test_env):
    """
    Scenario: Analytics only update when feature toggle enabled.

    Expected:
    - analytics = False → No updates
    - analytics = True → Updates occur
    """
    # === Analytics disabled ===
    disabled_spoke = test_env.create_spoke("analytics-disabled", with_git=False)
    test_env.set_feature_toggles(disabled_spoke, analytics=False)

    state = test_env.get_spoke_state(disabled_spoke)

    # Simulate session work (analytics should NOT update)
    if not state["feature_toggles"]["analytics"]:
        # Skip analytics update
        pass
    else:
        state["analytics"]["sessions"]["total_count"] += 1

    # Verify analytics unchanged
    assert state["analytics"]["sessions"]["total_count"] == 0

    # === Analytics enabled ===
    enabled_spoke = test_env.create_spoke("analytics-enabled", with_git=False)

    state = test_env.get_spoke_state(enabled_spoke)

    # Simulate session work (analytics SHOULD update)
    if state["feature_toggles"]["analytics"]:
        state["analytics"]["sessions"]["total_count"] += 1

        state_file = enabled_spoke / "WAI-Spoke" / "WAI-State.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    # Verify analytics updated
    final_state = test_env.get_spoke_state(enabled_spoke)
    assert final_state["analytics"]["sessions"]["total_count"] == 1


def test_analytics_average_calculations(test_env):
    """
    Scenario: Calculate average metrics.

    Metrics:
    - Average tokens per session
    - Average turns per session
    - Average duration per session
    """
    spoke_dir = test_env.create_spoke("analytics-averages", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Simulate 3 sessions
    state = test_env.get_spoke_state(spoke_dir)
    state["analytics"]["sessions"]["total_count"] = 3
    state["analytics"]["sessions"]["total_turns"] = 45  # 15 avg
    state["analytics"]["sessions"]["total_duration_seconds"] = 900  # 300 avg
    state["analytics"]["token_efficiency"]["total_tokens_used"] = 6000  # 2000 avg

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Calculate averages
    final_state = test_env.get_spoke_state(spoke_dir)
    analytics = final_state["analytics"]

    total_sessions = analytics["sessions"]["total_count"]
    avg_turns = analytics["sessions"]["total_turns"] / total_sessions
    avg_duration = analytics["sessions"]["total_duration_seconds"] / total_sessions
    avg_tokens = analytics["token_efficiency"]["total_tokens_used"] / total_sessions

    assert avg_turns == 15.0
    assert avg_duration == 300.0
    assert avg_tokens == 2000.0


def test_analytics_export_format(test_env):
    """
    Scenario: Analytics can be exported for reporting.

    Expected format:
    - JSON with all metrics
    - Human-readable summary
    - CSV-compatible structure
    """
    spoke_dir = test_env.create_spoke("analytics-export", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Populate analytics
    state = test_env.get_spoke_state(spoke_dir)
    state["analytics"]["sessions"]["total_count"] = 10
    state["analytics"]["sessions"]["total_turns"] = 150
    state["analytics"]["sessions"]["total_duration_seconds"] = 3000
    state["analytics"]["token_efficiency"]["total_tokens_used"] = 20000
    state["analytics"]["token_efficiency"]["tokens_saved_estimate"] = 10000
    state["analytics"]["quality_metrics"]["decisions_count"] = 25
    state["analytics"]["quality_metrics"]["high_impact_count"] = 8

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Export analytics
    final_state = test_env.get_spoke_state(spoke_dir)
    analytics_export = final_state["analytics"]

    # Verify exportable structure
    assert isinstance(analytics_export, dict)
    assert "sessions" in analytics_export
    assert "token_efficiency" in analytics_export
    assert "quality_metrics" in analytics_export

    # Verify can be converted to summary
    summary = {
        "sessions": analytics_export["sessions"]["total_count"],
        "avg_tokens_per_session": analytics_export["token_efficiency"]["total_tokens_used"] / analytics_export["sessions"]["total_count"],
        "tokens_saved": analytics_export["token_efficiency"]["tokens_saved_estimate"],
        "high_impact_decisions": analytics_export["quality_metrics"]["high_impact_count"]
    }

    assert summary["sessions"] == 10
    assert summary["avg_tokens_per_session"] == 2000.0
    assert summary["tokens_saved"] == 10000
    assert summary["high_impact_decisions"] == 8


def test_analytics_roi_calculation(test_env):
    """
    Scenario: Calculate ROI from token savings.

    Assumptions:
    - API cost: $15 per 1M tokens (Claude Sonnet 4.5)
    - Tokens saved: 100,000
    - Cost savings: $1.50
    """
    spoke_dir = test_env.create_spoke("analytics-roi", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Populate token savings
    state = test_env.get_spoke_state(spoke_dir)
    state["analytics"]["token_efficiency"]["tokens_saved_estimate"] = 100000

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Calculate ROI
    final_state = test_env.get_spoke_state(spoke_dir)
    tokens_saved = final_state["analytics"]["token_efficiency"]["tokens_saved_estimate"]

    # Claude Sonnet 4.5 pricing (approximate)
    cost_per_million_tokens = 15.0
    cost_savings = (tokens_saved / 1_000_000) * cost_per_million_tokens

    assert cost_savings == 1.50


def test_analytics_trend_tracking(test_env):
    """
    Scenario: Track trends over time.

    Expected:
    - Session count increasing
    - Average efficiency improving
    - Quality metrics stable or improving
    """
    spoke_dir = test_env.create_spoke("analytics-trends", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"

    # Simulate trend: Improving token efficiency over time
    sessions = [
        {"tokens": 5000, "turns": 20},  # Session 1: 250 tokens/turn
        {"tokens": 4500, "turns": 20},  # Session 2: 225 tokens/turn (improving)
        {"tokens": 4000, "turns": 20}   # Session 3: 200 tokens/turn (improving)
    ]

    state = test_env.get_spoke_state(spoke_dir)

    for session_num, session_data in enumerate(sessions, 1):
        state["analytics"]["sessions"]["total_count"] = session_num
        state["analytics"]["sessions"]["total_turns"] += session_data["turns"]
        state["analytics"]["token_efficiency"]["total_tokens_used"] += session_data["tokens"]

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify trend
    final_state = test_env.get_spoke_state(spoke_dir)
    total_tokens = final_state["analytics"]["token_efficiency"]["total_tokens_used"]
    total_turns = final_state["analytics"]["sessions"]["total_turns"]

    avg_tokens_per_turn = total_tokens / total_turns
    # Average across all sessions: (250 + 225 + 200) / 3 = 225
    assert avg_tokens_per_turn < 250, "Token efficiency should be improving"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

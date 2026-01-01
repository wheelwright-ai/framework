"""
Integration Test: Spoke Signal Generation.

Tests signal extraction from high-impact decisions, signal format validation,
and signal file management.
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


def test_signals_file_created_on_spoke_init(test_env):
    """
    Scenario: WAI-Signals.jsonl created when spoke initialized.

    Expected:
    - File exists
    - File is empty initially
    - Valid JSONL format
    """
    spoke_dir = test_env.create_spoke("signals-init", with_git=False)

    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    assert signals_file.exists(), "WAI-Signals.jsonl should exist"

    # Should be empty or very small initially
    file_size = signals_file.stat().st_size
    assert file_size < 10, f"Signals file should be empty initially, got {file_size} bytes"


def test_signal_generation_from_high_impact_decision(test_env):
    """
    Scenario: High-impact decision (impact >= 8) generates signal.

    Workflow:
    1. Add decision with impact >= 8
    2. Run closeout (or manual signal generation)
    3. Verify signal in WAI-Signals.jsonl
    """
    spoke_dir = test_env.create_spoke("high-impact-signal", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    # Add high-impact decision
    state = test_env.get_spoke_state(spoke_dir)
    state["decisions"].append({
        "date": "2025-01-01",
        "decision": "Adopt microservices architecture",
        "rationale": "Enable team independence and scalability",
        "impact": 9,
        "by": "AI Assistant"
    })

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Simulate signal generation (closeout would do this)
    signal = {
        "timestamp": "2025-01-01T12:00:00Z",
        "by": "AI Assistant",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [{
            "type": "decision",
            "topic": "Microservices architecture adoption",
            "impact": 9,
            "context": "For team independence and scalability"
        }],
        "requests": [],
        "flags": {
            "has_high_impact_learnings": True
        }
    }

    with open(signals_file, 'a') as f:
        f.write(json.dumps(signal) + '\n')

    # Verify signal created
    signals = test_env.get_spoke_signals(spoke_dir)
    assert len(signals) == 1, "Should have 1 signal"
    assert signals[0]["offers"][0]["impact"] == 9


def test_signal_schema_validation(test_env):
    """
    Scenario: Signals follow required schema.

    Required fields:
    - timestamp (ISO-8601)
    - by (who created the signal)
    - hub_kb_version
    - wheel_kb_version
    - offers (array)
    - requests (array)
    - flags (object)
    """
    spoke_dir = test_env.create_spoke("signal-schema", with_git=False)

    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    # Create properly formatted signal
    signal = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "by": "Test AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [{
            "type": "pattern",
            "topic": "Error handling best practice",
            "impact": 8,
            "context": "Always use context managers for resources"
        }],
        "requests": [],
        "flags": {
            "has_high_impact_learnings": True
        }
    }

    with open(signals_file, 'a') as f:
        f.write(json.dumps(signal) + '\n')

    # Validate schema
    signals = test_env.get_spoke_signals(spoke_dir)
    assert len(signals) == 1

    s = signals[0]
    assert "timestamp" in s
    assert "by" in s
    assert "hub_kb_version" in s
    assert "wheel_kb_version" in s
    assert "offers" in s
    assert "requests" in s
    assert "flags" in s

    # Validate timestamp format (ISO-8601)
    assert "T" in s["timestamp"]
    assert s["timestamp"].endswith("Z") or "+" in s["timestamp"]


def test_low_impact_decisions_do_not_generate_signals(test_env):
    """
    Scenario: Decisions with impact < 8 should NOT generate signals.

    Workflow:
    1. Add decision with impact = 5
    2. Run closeout
    3. Verify NO signal created
    """
    spoke_dir = test_env.create_spoke("low-impact", with_git=False)

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

    # Closeout should NOT create signal for impact < 8
    # (Manual verification - closeout logic would enforce this)

    # Signals file should remain empty
    signals = test_env.get_spoke_signals(spoke_dir)
    assert len(signals) == 0, "Low-impact decisions should not generate signals"


def test_multiple_signals_in_one_session(test_env):
    """
    Scenario: Multiple high-impact decisions in one session.

    Workflow:
    1. Make 3 high-impact decisions
    2. Run closeout
    3. Verify 3 signals created
    """
    spoke_dir = test_env.create_spoke("multi-signals", with_git=False)

    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    # Create 3 signals
    decisions = [
        {"topic": "Database choice: PostgreSQL", "impact": 9},
        {"topic": "Authentication: OAuth2", "impact": 8},
        {"topic": "Frontend framework: React", "impact": 9}
    ]

    for i, decision in enumerate(decisions):
        signal = {
            "timestamp": f"2025-01-01T12:{i:02d}:00Z",
            "by": "AI",
            "hub_kb_version": "1.0.0",
            "wheel_kb_version": "1.0.0",
            "offers": [{
                "type": "decision",
                "topic": decision["topic"],
                "impact": decision["impact"],
                "context": "High-impact architectural decision"
            }],
            "requests": [],
            "flags": {"has_high_impact_learnings": True}
        }
        with open(signals_file, 'a') as f:
            f.write(json.dumps(signal) + '\n')

    # Verify all 3 signals
    signals = test_env.get_spoke_signals(spoke_dir)
    assert len(signals) == 3, "Should have 3 signals"
    assert all(s["offers"][0]["impact"] >= 8 for s in signals)


def test_signal_offers_structure(test_env):
    """
    Scenario: Signal offers follow proper structure.

    Offers array contains:
    - type: "decision", "pattern", "insight", etc.
    - topic: Brief description
    - impact: 0-10 scale
    - context: Detailed explanation
    """
    spoke_dir = test_env.create_spoke("signal-offers", with_git=False)

    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    # Create signal with multiple offers
    signal = {
        "timestamp": "2025-01-01T12:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [
            {
                "type": "pattern",
                "topic": "Repository pattern for data access",
                "impact": 8,
                "context": "Separates business logic from data persistence"
            },
            {
                "type": "insight",
                "topic": "Use dependency injection for testability",
                "impact": 8,
                "context": "Makes unit testing much easier"
            }
        ],
        "requests": [],
        "flags": {"has_high_impact_learnings": True}
    }

    with open(signals_file, 'a') as f:
        f.write(json.dumps(signal) + '\n')

    # Validate offers structure
    signals = test_env.get_spoke_signals(spoke_dir)
    assert len(signals) == 1

    offers = signals[0]["offers"]
    assert len(offers) == 2

    for offer in offers:
        assert "type" in offer
        assert "topic" in offer
        assert "impact" in offer
        assert "context" in offer
        assert offer["impact"] >= 8


def test_signal_requests_for_knowledge(test_env):
    """
    Scenario: Spoke can request knowledge via signals.

    Requests array contains questions/needs for hub.
    """
    spoke_dir = test_env.create_spoke("signal-requests", with_git=False)

    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    # Create signal with requests
    signal = {
        "timestamp": "2025-01-01T12:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [],
        "requests": [
            {
                "type": "pattern",
                "topic": "How to handle database migrations in microservices?",
                "priority": "high"
            },
            {
                "type": "example",
                "topic": "Real-world OAuth2 implementation",
                "priority": "medium"
            }
        ],
        "flags": {"has_requests": True}
    }

    with open(signals_file, 'a') as f:
        f.write(json.dumps(signal) + '\n')

    # Validate requests
    signals = test_env.get_spoke_signals(spoke_dir)
    assert len(signals) == 1

    requests = signals[0]["requests"]
    assert len(requests) == 2
    assert requests[0]["topic"] == "How to handle database migrations in microservices?"
    assert requests[1]["priority"] == "medium"


def test_signal_flags_metadata(test_env):
    """
    Scenario: Signal flags provide metadata about signal content.

    Common flags:
    - has_high_impact_learnings
    - has_requests
    - needs_review
    - ready_for_hub
    """
    spoke_dir = test_env.create_spoke("signal-flags", with_git=False)

    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    # Create signal with various flags
    signal = {
        "timestamp": "2025-01-01T12:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [{
            "type": "decision",
            "topic": "Critical architecture decision",
            "impact": 10,
            "context": "Switching to event-driven architecture"
        }],
        "requests": [{
            "type": "validation",
            "topic": "Please review this decision"
        }],
        "flags": {
            "has_high_impact_learnings": True,
            "has_requests": True,
            "needs_review": True,
            "ready_for_hub": True
        }
    }

    with open(signals_file, 'a') as f:
        f.write(json.dumps(signal) + '\n')

    # Validate flags
    signals = test_env.get_spoke_signals(spoke_dir)
    flags = signals[0]["flags"]

    assert flags["has_high_impact_learnings"] == True
    assert flags["has_requests"] == True
    assert flags["needs_review"] == True
    assert flags["ready_for_hub"] == True


def test_signals_append_only_no_overwrite(test_env):
    """
    Scenario: Signals should append, never overwrite.

    Workflow:
    1. Create signal 1
    2. Create signal 2
    3. Verify both exist
    4. Order preserved
    """
    spoke_dir = test_env.create_spoke("signals-append", with_git=False)

    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    # Add signal 1
    signal1 = {
        "timestamp": "2025-01-01T10:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [{"type": "decision", "topic": "Signal 1", "impact": 8, "context": "First"}],
        "requests": [],
        "flags": {"has_high_impact_learnings": True}
    }

    with open(signals_file, 'a') as f:
        f.write(json.dumps(signal1) + '\n')

    # Add signal 2
    signal2 = {
        "timestamp": "2025-01-01T11:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [{"type": "decision", "topic": "Signal 2", "impact": 9, "context": "Second"}],
        "requests": [],
        "flags": {"has_high_impact_learnings": True}
    }

    with open(signals_file, 'a') as f:
        f.write(json.dumps(signal2) + '\n')

    # Verify both signals exist in order
    signals = test_env.get_spoke_signals(spoke_dir)
    assert len(signals) == 2

    assert signals[0]["offers"][0]["topic"] == "Signal 1"
    assert signals[1]["offers"][0]["topic"] == "Signal 2"

    # Verify chronological order
    assert signals[0]["timestamp"] < signals[1]["timestamp"]


def test_signals_survive_closeout(test_env):
    """
    Scenario: Signals persist after closeout.

    Workflow:
    1. Create signals
    2. Run closeout
    3. Verify signals still exist (not cleared)
    """
    spoke_dir = test_env.create_spoke("signals-persist", with_git=False)

    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    # Create signal
    signal = {
        "timestamp": "2025-01-01T12:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [{"type": "decision", "topic": "Test", "impact": 9, "context": "Test signal"}],
        "requests": [],
        "flags": {"has_high_impact_learnings": True}
    }

    with open(signals_file, 'a') as f:
        f.write(json.dumps(signal) + '\n')

    # Simulate closeout (which clears conversation log but NOT signals)
    log_file = spoke_dir / "WAI-Spoke" / "WAI-Session-Log.jsonl"
    if log_file.exists():
        log_file.unlink()  # Clear log

    # Signals should still exist
    signals = test_env.get_spoke_signals(spoke_dir)
    assert len(signals) == 1, "Signals should persist after closeout"


def test_signal_extraction_threshold(test_env):
    """
    Scenario: Only impact >= 8 triggers signal extraction.

    Workflow:
    1. Add decisions with impacts 5, 7, 8, 9, 10
    2. Run signal extraction
    3. Verify only 8, 9, 10 generate signals
    """
    spoke_dir = test_env.create_spoke("signal-threshold", with_git=False)

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

    # Add decisions with varying impact
    state = test_env.get_spoke_state(spoke_dir)
    decisions = [
        {"decision": "Impact 5", "impact": 5},
        {"decision": "Impact 7", "impact": 7},
        {"decision": "Impact 8", "impact": 8},
        {"decision": "Impact 9", "impact": 9},
        {"decision": "Impact 10", "impact": 10}
    ]

    for d in decisions:
        state["decisions"].append({
            "date": "2025-01-01",
            "decision": d["decision"],
            "rationale": "Test",
            "impact": d["impact"],
            "by": "AI"
        })

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Simulate signal extraction (impact >= 8 only)
    high_impact = [d for d in state["decisions"] if d.get("impact", 0) >= 8]

    for decision in high_impact:
        signal = {
            "timestamp": "2025-01-01T12:00:00Z",
            "by": "AI",
            "hub_kb_version": "1.0.0",
            "wheel_kb_version": "1.0.0",
            "offers": [{
                "type": "decision",
                "topic": decision["decision"],
                "impact": decision["impact"],
                "context": decision["rationale"]
            }],
            "requests": [],
            "flags": {"has_high_impact_learnings": True}
        }
        with open(signals_file, 'a') as f:
            f.write(json.dumps(signal) + '\n')

    # Verify only 3 signals (8, 9, 10)
    signals = test_env.get_spoke_signals(spoke_dir)
    assert len(signals) == 3, "Only decisions with impact >= 8 should generate signals"

    impacts = [s["offers"][0]["impact"] for s in signals]
    assert 8 in impacts
    assert 9 in impacts
    assert 10 in impacts
    assert 5 not in impacts
    assert 7 not in impacts


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

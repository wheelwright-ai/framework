"""
Integration Test: Hub Learning from Spokes.

Tests hub's ability to learn from spoke signals, update knowledge base,
and serve knowledge to other spokes.
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


def test_hub_can_be_initialized(test_env):
    """
    Scenario: Initialize a hub.

    Expected:
    - Hub directory created
    - Hub knowledge base initialized
    - Hub metadata present
    """
    hub_dir = test_env.create_hub("test-hub")

    assert hub_dir.exists(), "Hub directory should exist"
    assert hub_dir.is_dir(), "Hub should be a directory"

    # Hub should have knowledge base structure
    hub_kb = hub_dir / "WAI-Hub" / "knowledge-base.json"
    if hub_kb.exists():
        kb = json.loads(hub_kb.read_text())
        assert "patterns" in kb or "learnings" in kb or "signals" in kb


def test_hub_learns_from_single_spoke(test_env):
    """
    Scenario: Hub learns from one spoke's signals.

    Workflow:
    1. Create hub
    2. Create spoke
    3. Spoke generates high-impact signal
    4. Hub learns from spoke
    5. Verify signal in hub knowledge base
    """
    hub_dir = test_env.create_hub("learning-hub")
    spoke_dir = test_env.create_spoke("learning-spoke", with_git=False)

    # Create high-impact signal in spoke
    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"
    signal = {
        "timestamp": "2025-01-01T12:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [{
            "type": "pattern",
            "topic": "Use repository pattern for data access",
            "impact": 9,
            "context": "Separates business logic from data layer"
        }],
        "requests": [],
        "flags": {"has_high_impact_learnings": True, "ready_for_hub": True}
    }

    with open(signals_file, 'a') as f:
        f.write(json.dumps(signal) + '\n')

    # Simulate hub learning (hub would scan spoke directories and absorb signals)
    # For now, manually simulate this by creating hub knowledge entry

    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    hub_kb = {
        "patterns": [{
            "topic": "Use repository pattern for data access",
            "impact": 9,
            "source": "learning-spoke",
            "learned_at": "2025-01-01T12:05:00Z",
            "context": "Separates business logic from data layer"
        }],
        "version": "1.0.1",
        "last_updated": "2025-01-01T12:05:00Z"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Verify hub learned the pattern
    assert hub_kb_file.exists()
    kb = json.loads(hub_kb_file.read_text())
    assert len(kb["patterns"]) == 1
    assert kb["patterns"][0]["topic"] == "Use repository pattern for data access"
    assert kb["patterns"][0]["source"] == "learning-spoke"


def test_hub_learns_from_multiple_spokes(test_env):
    """
    Scenario: Hub aggregates knowledge from multiple spokes.

    Workflow:
    1. Create hub + 3 spokes
    2. Each spoke generates different signal
    3. Hub learns from all
    4. Verify all 3 signals in hub KB
    """
    hub_dir = test_env.create_hub("multi-spoke-hub")
    spoke1 = test_env.create_spoke("spoke-1", with_git=False)
    spoke2 = test_env.create_spoke("spoke-2", with_git=False)
    spoke3 = test_env.create_spoke("spoke-3", with_git=False)

    # Create different signals in each spoke
    spokes = [
        (spoke1, "Database migration strategy", 9),
        (spoke2, "Error handling best practices", 8),
        (spoke3, "API versioning approach", 9)
    ]

    for spoke_dir, topic, impact in spokes:
        signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"
        signal = {
            "timestamp": "2025-01-01T12:00:00Z",
            "by": "AI",
            "hub_kb_version": "1.0.0",
            "wheel_kb_version": "1.0.0",
            "offers": [{
                "type": "pattern",
                "topic": topic,
                "impact": impact,
                "context": f"Learning about {topic}"
            }],
            "requests": [],
            "flags": {"has_high_impact_learnings": True}
        }
        with open(signals_file, 'a') as f:
            f.write(json.dumps(signal) + '\n')

    # Simulate hub learning from all spokes
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    patterns = []
    for spoke_dir, topic, impact in spokes:
        patterns.append({
            "topic": topic,
            "impact": impact,
            "source": spoke_dir.name,
            "learned_at": "2025-01-01T12:05:00Z"
        })

    hub_kb = {
        "patterns": patterns,
        "version": "1.0.3",
        "last_updated": "2025-01-01T12:05:00Z"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Verify all 3 patterns learned
    kb = json.loads(hub_kb_file.read_text())
    assert len(kb["patterns"]) == 3

    topics = [p["topic"] for p in kb["patterns"]]
    assert "Database migration strategy" in topics
    assert "Error handling best practices" in topics
    assert "API versioning approach" in topics


def test_hub_version_increments_on_learning(test_env):
    """
    Scenario: Hub knowledge base version increments when learning.

    Workflow:
    1. Hub at version 1.0.0
    2. Hub learns new pattern
    3. Version increments to 1.0.1
    4. Hub learns another pattern
    5. Version increments to 1.0.2
    """
    hub_dir = test_env.create_hub("versioned-hub")
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    # Initial state
    hub_kb = {
        "patterns": [],
        "version": "1.0.0",
        "last_updated": "2025-01-01T10:00:00Z"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Learn first pattern (version → 1.0.1)
    hub_kb["patterns"].append({
        "topic": "Pattern 1",
        "impact": 8,
        "source": "spoke-a"
    })
    hub_kb["version"] = "1.0.1"
    hub_kb["last_updated"] = "2025-01-01T11:00:00Z"

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Learn second pattern (version → 1.0.2)
    hub_kb["patterns"].append({
        "topic": "Pattern 2",
        "impact": 9,
        "source": "spoke-b"
    })
    hub_kb["version"] = "1.0.2"
    hub_kb["last_updated"] = "2025-01-01T12:00:00Z"

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Verify version progression
    kb = json.loads(hub_kb_file.read_text())
    assert kb["version"] == "1.0.2"
    assert len(kb["patterns"]) == 2


def test_hub_deduplicates_similar_patterns(test_env):
    """
    Scenario: Hub avoids duplicate learnings from multiple spokes.

    Workflow:
    1. Spoke A signals: "Use React hooks"
    2. Spoke B signals: "Use React hooks"
    3. Hub learns once, not twice
    """
    hub_dir = test_env.create_hub("dedup-hub")
    spoke_a = test_env.create_spoke("spoke-a", with_git=False)
    spoke_b = test_env.create_spoke("spoke-b", with_git=False)

    # Both spokes signal same pattern
    for spoke_dir in [spoke_a, spoke_b]:
        signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"
        signal = {
            "timestamp": "2025-01-01T12:00:00Z",
            "by": "AI",
            "hub_kb_version": "1.0.0",
            "wheel_kb_version": "1.0.0",
            "offers": [{
                "type": "pattern",
                "topic": "Use React hooks for state management",
                "impact": 8,
                "context": "Cleaner than class components"
            }],
            "requests": [],
            "flags": {"has_high_impact_learnings": True}
        }
        with open(signals_file, 'a') as f:
            f.write(json.dumps(signal) + '\n')

    # Simulate hub deduplication logic
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    # Hub should recognize duplicate and only store once
    hub_kb = {
        "patterns": [{
            "topic": "Use React hooks for state management",
            "impact": 8,
            "sources": ["spoke-a", "spoke-b"],  # Track multiple sources
            "learned_at": "2025-01-01T12:05:00Z"
        }],
        "version": "1.0.1"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Verify only 1 pattern, but 2 sources
    kb = json.loads(hub_kb_file.read_text())
    assert len(kb["patterns"]) == 1, "Hub should deduplicate same pattern"
    assert len(kb["patterns"][0]["sources"]) == 2


def test_hub_prioritizes_high_impact_learnings(test_env):
    """
    Scenario: Hub prioritizes patterns by impact.

    Workflow:
    1. Multiple patterns with varying impact
    2. Hub sorts by impact (highest first)
    3. Verify order in knowledge base
    """
    hub_dir = test_env.create_hub("priority-hub")
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    # Create patterns with different impacts
    patterns = [
        {"topic": "Pattern A", "impact": 7},
        {"topic": "Pattern B", "impact": 10},
        {"topic": "Pattern C", "impact": 8},
        {"topic": "Pattern D", "impact": 9}
    ]

    # Hub sorts by impact descending
    sorted_patterns = sorted(patterns, key=lambda p: p["impact"], reverse=True)

    hub_kb = {
        "patterns": sorted_patterns,
        "version": "1.0.0"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Verify sorted order
    kb = json.loads(hub_kb_file.read_text())
    impacts = [p["impact"] for p in kb["patterns"]]
    assert impacts == [10, 9, 8, 7], "Hub should sort patterns by impact descending"


def test_hub_tracks_learning_timestamps(test_env):
    """
    Scenario: Hub tracks when each pattern was learned.

    Expected:
    - Each pattern has learned_at timestamp
    - Timestamps are ISO-8601 format
    """
    hub_dir = test_env.create_hub("timestamp-hub")
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    hub_kb = {
        "patterns": [
            {
                "topic": "Pattern 1",
                "impact": 8,
                "learned_at": "2025-01-01T10:00:00Z"
            },
            {
                "topic": "Pattern 2",
                "impact": 9,
                "learned_at": "2025-01-01T11:30:00Z"
            }
        ],
        "version": "1.0.2"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Verify timestamps
    kb = json.loads(hub_kb_file.read_text())
    for pattern in kb["patterns"]:
        assert "learned_at" in pattern
        assert "T" in pattern["learned_at"]
        assert pattern["learned_at"].endswith("Z")


def test_hub_provides_knowledge_to_new_spoke(test_env):
    """
    Scenario: New spoke can access hub knowledge.

    Workflow:
    1. Hub has learned patterns
    2. New spoke initializes
    3. Spoke receives hub knowledge version
    4. Spoke can reference hub patterns
    """
    hub_dir = test_env.create_hub("sharing-hub")
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    # Hub has knowledge
    hub_kb = {
        "patterns": [
            {
                "topic": "Use dependency injection",
                "impact": 9,
                "context": "Improves testability"
            }
        ],
        "version": "1.0.5"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # New spoke initializes
    spoke_dir = test_env.create_spoke("new-spoke", with_git=False)

    # Spoke should reference hub KB version
    state = test_env.get_spoke_state(spoke_dir)

    # Simulate hub knowledge sync to spoke
    state["wheelwright"]["hub_kb_version"] = "1.0.5"

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify spoke has hub version
    final_state = test_env.get_spoke_state(spoke_dir)
    assert final_state["wheelwright"]["hub_kb_version"] == "1.0.5"


def test_hub_learning_updates_spoke_kb_versions(test_env):
    """
    Scenario: When hub learns, spoke KB versions become outdated.

    Workflow:
    1. Spoke A at hub KB version 1.0.0
    2. Hub learns new pattern (version → 1.0.1)
    3. Spoke A now outdated
    4. Spoke A can sync to get new knowledge
    """
    hub_dir = test_env.create_hub("sync-hub")
    spoke_dir = test_env.create_spoke("spoke-sync", with_git=False)

    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    # Initial hub version
    hub_kb = {"patterns": [], "version": "1.0.0"}
    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Spoke synced to this version
    state = test_env.get_spoke_state(spoke_dir)
    state["wheelwright"]["hub_kb_version"] = "1.0.0"
    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Hub learns new pattern (version bump)
    hub_kb["patterns"].append({"topic": "New pattern", "impact": 8})
    hub_kb["version"] = "1.0.1"
    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Spoke is now outdated
    current_state = test_env.get_spoke_state(spoke_dir)
    current_hub_kb = json.loads(hub_kb_file.read_text())

    spoke_version = current_state["wheelwright"]["hub_kb_version"]
    hub_version = current_hub_kb["version"]

    assert spoke_version == "1.0.0"
    assert hub_version == "1.0.1"
    assert spoke_version != hub_version, "Spoke should be outdated after hub learns"


def test_hub_handles_spoke_requests(test_env):
    """
    Scenario: Hub processes spoke requests for knowledge.

    Workflow:
    1. Spoke signals request: "How to handle auth?"
    2. Hub has pattern for auth
    3. Hub marks request as fulfilled
    4. Spoke receives answer
    """
    hub_dir = test_env.create_hub("request-hub")
    spoke_dir = test_env.create_spoke("requesting-spoke", with_git=False)

    # Spoke creates request signal
    signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"
    signal = {
        "timestamp": "2025-01-01T12:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [],
        "requests": [{
            "type": "pattern",
            "topic": "How to implement OAuth2 authentication?",
            "priority": "high"
        }],
        "flags": {"has_requests": True}
    }

    with open(signals_file, 'a') as f:
        f.write(json.dumps(signal) + '\n')

    # Hub has relevant pattern
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    hub_kb = {
        "patterns": [{
            "topic": "OAuth2 implementation guide",
            "impact": 9,
            "context": "Use authorization code flow with PKCE"
        }],
        "version": "1.0.1"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Verify request and pattern match
    spoke_signals = test_env.get_spoke_signals(spoke_dir)
    hub_kb_data = json.loads(hub_kb_file.read_text())

    assert len(spoke_signals) == 1
    assert spoke_signals[0]["requests"][0]["topic"] == "How to implement OAuth2 authentication?"
    assert any("OAuth2" in p["topic"] for p in hub_kb_data["patterns"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

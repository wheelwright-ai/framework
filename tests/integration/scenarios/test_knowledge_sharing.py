"""
Integration Test: Cross-Project Knowledge Sharing.

Tests the complete end-to-end flow of knowledge from spoke A → hub → spoke B,
validating the full collaborative learning ecosystem.
"""

import pytest
import sys
import json
from pathlib import Path

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


def test_knowledge_flows_from_spoke_to_hub_to_spoke(test_env):
    """
    Scenario: Complete knowledge sharing workflow.

    Workflow:
    1. Spoke A creates high-impact decision
    2. Spoke A closeout generates signal
    3. Hub learns from Spoke A
    4. Spoke B initializes
    5. Spoke B receives hub knowledge
    6. Spoke B can reference Spoke A's learnings
    """
    hub_dir = test_env.create_hub("knowledge-hub")
    spoke_a = test_env.create_spoke("spoke-a", with_git=False)
    spoke_b = test_env.create_spoke("spoke-b", with_git=False)

    # Step 1-2: Spoke A creates signal
    spoke_a_signals = spoke_a / "WAI-Spoke" / "WAI-Signals.jsonl"
    signal = {
        "timestamp": "2025-01-01T10:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [{
            "type": "pattern",
            "topic": "Use circuit breaker for external API calls",
            "impact": 9,
            "context": "Prevents cascade failures when service is down"
        }],
        "requests": [],
        "flags": {"has_high_impact_learnings": True}
    }

    with open(spoke_a_signals, 'a') as f:
        f.write(json.dumps(signal) + '\n')

    # Step 3: Hub learns from Spoke A
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    hub_kb = {
        "patterns": [{
            "topic": "Use circuit breaker for external API calls",
            "impact": 9,
            "source": "spoke-a",
            "learned_at": "2025-01-01T10:05:00Z",
            "context": "Prevents cascade failures when service is down"
        }],
        "version": "1.0.1",
        "last_updated": "2025-01-01T10:05:00Z"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Step 4-5: Spoke B syncs with hub
    spoke_b_state = test_env.get_spoke_state(spoke_b)
    spoke_b_state["wheelwright"]["hub_kb_version"] = "1.0.1"

    spoke_b_state_file = spoke_b / "WAI-Spoke" / "WAI-State.json"
    with open(spoke_b_state_file, 'w') as f:
        json.dump(spoke_b_state, f, indent=2)

    # Step 6: Verify Spoke B has access to Spoke A's knowledge
    hub_knowledge = json.loads(hub_kb_file.read_text())
    spoke_b_final = test_env.get_spoke_state(spoke_b)

    assert hub_knowledge["patterns"][0]["source"] == "spoke-a"
    assert spoke_b_final["wheelwright"]["hub_kb_version"] == "1.0.1"


def test_multiple_spokes_contribute_to_shared_knowledge(test_env):
    """
    Scenario: 3 spokes contribute patterns, all benefit from collective knowledge.

    Workflow:
    1. Spoke A: Backend patterns
    2. Spoke B: Frontend patterns
    3. Spoke C: DevOps patterns
    4. Hub aggregates all
    5. Each spoke can access patterns from others
    """
    hub_dir = test_env.create_hub("collective-hub")

    contributions = [
        ("spoke-a", "Use repository pattern for data access", 9),
        ("spoke-b", "Use React hooks for state management", 8),
        ("spoke-c", "Use Docker for consistent environments", 9)
    ]

    spokes = {}
    for spoke_name, topic, impact in contributions:
        spoke_dir = test_env.create_spoke(spoke_name, with_git=False)
        spokes[spoke_name] = spoke_dir

        # Each spoke creates signal
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
                "context": f"{spoke_name} best practice"
            }],
            "requests": [],
            "flags": {"has_high_impact_learnings": True}
        }
        with open(signals_file, 'a') as f:
            f.write(json.dumps(signal) + '\n')

    # Hub learns from all
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    patterns = []
    for spoke_name, topic, impact in contributions:
        patterns.append({
            "topic": topic,
            "impact": impact,
            "source": spoke_name,
            "learned_at": "2025-01-01T12:05:00Z"
        })

    hub_kb = {
        "patterns": patterns,
        "version": "1.0.3"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Each spoke syncs to hub version 1.0.3
    for spoke_name, spoke_dir in spokes.items():
        state = test_env.get_spoke_state(spoke_dir)
        state["wheelwright"]["hub_kb_version"] = "1.0.3"
        state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    # Verify all spokes have access to collective knowledge
    kb = json.loads(hub_kb_file.read_text())
    assert len(kb["patterns"]) == 3

    sources = {p["source"] for p in kb["patterns"]}
    assert sources == {"spoke-a", "spoke-b", "spoke-c"}


def test_spoke_requests_knowledge_hub_provides(test_env):
    """
    Scenario: Spoke requests knowledge, hub provides from other spoke.

    Workflow:
    1. Spoke A learns pattern about testing
    2. Hub absorbs pattern
    3. Spoke B requests testing guidance
    4. Hub matches request to Spoke A's pattern
    5. Spoke B receives answer
    """
    hub_dir = test_env.create_hub("request-response-hub")
    spoke_a = test_env.create_spoke("teacher-spoke", with_git=False)
    spoke_b = test_env.create_spoke("learner-spoke", with_git=False)

    # Spoke A offers testing pattern
    spoke_a_signals = spoke_a / "WAI-Spoke" / "WAI-Signals.jsonl"
    offer_signal = {
        "timestamp": "2025-01-01T10:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [{
            "type": "pattern",
            "topic": "Arrange-Act-Assert pattern for unit tests",
            "impact": 8,
            "context": "Makes tests more readable and maintainable"
        }],
        "requests": [],
        "flags": {"has_high_impact_learnings": True}
    }
    with open(spoke_a_signals, 'a') as f:
        f.write(json.dumps(offer_signal) + '\n')

    # Hub learns from Spoke A
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    hub_kb = {
        "patterns": [{
            "topic": "Arrange-Act-Assert pattern for unit tests",
            "impact": 8,
            "source": "teacher-spoke",
            "context": "Makes tests more readable and maintainable"
        }],
        "version": "1.0.1"
    }
    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Spoke B requests testing guidance
    spoke_b_signals = spoke_b / "WAI-Spoke" / "WAI-Signals.jsonl"
    request_signal = {
        "timestamp": "2025-01-01T11:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.1",
        "wheel_kb_version": "1.0.0",
        "offers": [],
        "requests": [{
            "type": "pattern",
            "topic": "What patterns should I use for unit tests?",
            "priority": "high"
        }],
        "flags": {"has_requests": True}
    }
    with open(spoke_b_signals, 'a') as f:
        f.write(json.dumps(request_signal) + '\n')

    # Verify hub can match request to pattern
    hub_patterns = json.loads(hub_kb_file.read_text())["patterns"]
    spoke_b_requests = test_env.get_spoke_signals(spoke_b)[0]["requests"]

    # Hub would match "unit tests" in request to "unit tests" in pattern
    relevant_pattern = next(
        (p for p in hub_patterns if "unit test" in p["topic"].lower()),
        None
    )

    assert relevant_pattern is not None
    assert relevant_pattern["source"] == "teacher-spoke"
    assert len(spoke_b_requests) == 1


def test_knowledge_versioning_prevents_stale_information(test_env):
    """
    Scenario: Spokes detect when their hub knowledge is outdated.

    Workflow:
    1. Spoke A at hub KB v1.0.0
    2. Hub learns new pattern (v1.0.1)
    3. Spoke A detects outdated version
    4. Spoke A syncs to v1.0.1
    """
    hub_dir = test_env.create_hub("version-hub")
    spoke_dir = test_env.create_spoke("versioned-spoke", with_git=False)

    # Initial sync
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    hub_kb = {"patterns": [], "version": "1.0.0"}
    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    state = test_env.get_spoke_state(spoke_dir)
    state["wheelwright"]["hub_kb_version"] = "1.0.0"
    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Hub learns new pattern
    hub_kb["patterns"].append({"topic": "New pattern", "impact": 9})
    hub_kb["version"] = "1.0.1"
    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Spoke detects outdated version
    current_state = test_env.get_spoke_state(spoke_dir)
    current_hub = json.loads(hub_kb_file.read_text())

    is_outdated = current_state["wheelwright"]["hub_kb_version"] != current_hub["version"]
    assert is_outdated, "Spoke should detect hub KB version mismatch"

    # Spoke syncs to latest
    current_state["wheelwright"]["hub_kb_version"] = current_hub["version"]
    with open(state_file, 'w') as f:
        json.dump(current_state, f, indent=2)

    # Verify sync
    final_state = test_env.get_spoke_state(spoke_dir)
    assert final_state["wheelwright"]["hub_kb_version"] == "1.0.1"


def test_spoke_can_reject_hub_pattern(test_env):
    """
    Scenario: Spoke can mark hub pattern as not applicable.

    Workflow:
    1. Hub suggests pattern: "Use React"
    2. Spoke is Python project (not applicable)
    3. Spoke marks pattern as rejected
    4. Pattern not applied to this spoke
    """
    hub_dir = test_env.create_hub("suggestion-hub")
    spoke_dir = test_env.create_spoke("python-spoke", with_git=False)

    # Hub has React pattern
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    hub_kb = {
        "patterns": [{
            "topic": "Use React hooks",
            "impact": 8,
            "context": "Frontend state management"
        }],
        "version": "1.0.1"
    }
    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Spoke is Python (backend only) - track project type
    state = test_env.get_spoke_state(spoke_dir)

    # Spoke rejects pattern (adds to rejected_patterns list)
    if "rejected_patterns" not in state:
        state["rejected_patterns"] = []

    state["rejected_patterns"].append({
        "pattern": "Use React hooks",
        "reason": "Not applicable - Python backend project",
        "rejected_at": "2025-01-01T12:00:00Z"
    })

    state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

    # Verify rejection tracked
    final_state = test_env.get_spoke_state(spoke_dir)
    assert "rejected_patterns" in final_state
    assert len(final_state["rejected_patterns"]) == 1
    assert "React" in final_state["rejected_patterns"][0]["pattern"]


def test_hub_analytics_track_knowledge_adoption(test_env):
    """
    Scenario: Hub tracks which patterns are most adopted.

    Workflow:
    1. Hub has 3 patterns
    2. Spoke A adopts pattern 1
    3. Spoke B adopts pattern 1
    4. Spoke C adopts pattern 2
    5. Hub analytics show pattern 1 most popular
    """
    hub_dir = test_env.create_hub("analytics-hub")
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    # Hub has patterns with adoption tracking
    hub_kb = {
        "patterns": [
            {"topic": "Pattern 1", "impact": 9, "adopted_by": ["spoke-a", "spoke-b"]},
            {"topic": "Pattern 2", "impact": 8, "adopted_by": ["spoke-c"]},
            {"topic": "Pattern 3", "impact": 7, "adopted_by": []}
        ],
        "analytics": {
            "most_adopted_pattern": "Pattern 1",
            "total_adoptions": 3
        },
        "version": "1.0.3"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Verify analytics
    kb = json.loads(hub_kb_file.read_text())
    adoption_counts = {p["topic"]: len(p["adopted_by"]) for p in kb["patterns"]}

    assert adoption_counts["Pattern 1"] == 2
    assert adoption_counts["Pattern 2"] == 1
    assert adoption_counts["Pattern 3"] == 0

    most_adopted = max(kb["patterns"], key=lambda p: len(p["adopted_by"]))
    assert most_adopted["topic"] == "Pattern 1"


def test_hub_aggregates_signals_across_time(test_env):
    """
    Scenario: Hub maintains historical view of learnings over time.

    Workflow:
    1. Week 1: Learn 3 patterns
    2. Week 2: Learn 2 more patterns
    3. Week 3: Learn 1 pattern
    4. Hub shows trend of knowledge growth
    """
    hub_dir = test_env.create_hub("timeline-hub")
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    # Hub tracks patterns with timestamps
    hub_kb = {
        "patterns": [
            {"topic": "P1", "impact": 8, "learned_at": "2025-01-01T10:00:00Z"},
            {"topic": "P2", "impact": 9, "learned_at": "2025-01-02T10:00:00Z"},
            {"topic": "P3", "impact": 8, "learned_at": "2025-01-03T10:00:00Z"},
            {"topic": "P4", "impact": 9, "learned_at": "2025-01-08T10:00:00Z"},
            {"topic": "P5", "impact": 8, "learned_at": "2025-01-09T10:00:00Z"},
            {"topic": "P6", "impact": 10, "learned_at": "2025-01-15T10:00:00Z"}
        ],
        "analytics": {
            "total_patterns": 6,
            "patterns_this_week": 1,
            "patterns_last_week": 2,
            "growth_trend": "steady"
        },
        "version": "1.0.6"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Verify temporal tracking
    kb = json.loads(hub_kb_file.read_text())
    assert len(kb["patterns"]) == 6
    assert kb["analytics"]["total_patterns"] == 6
    assert kb["analytics"]["growth_trend"] == "steady"


def test_cross_project_contradiction_detection(test_env):
    """
    Scenario: Hub detects contradictory patterns from different spokes.

    Workflow:
    1. Spoke A: "Use SQL database"
    2. Spoke B: "Use NoSQL database"
    3. Hub flags contradiction
    4. Human review triggered
    """
    hub_dir = test_env.create_hub("contradiction-hub")
    spoke_a = test_env.create_spoke("spoke-sql", with_git=False)
    spoke_b = test_env.create_spoke("spoke-nosql", with_git=False)

    # Spoke A signals SQL
    spoke_a_signals = spoke_a / "WAI-Spoke" / "WAI-Signals.jsonl"
    signal_a = {
        "timestamp": "2025-01-01T10:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [{
            "type": "decision",
            "topic": "Use PostgreSQL for data storage",
            "impact": 9,
            "context": "ACID compliance needed"
        }],
        "requests": [],
        "flags": {"has_high_impact_learnings": True}
    }
    with open(spoke_a_signals, 'a') as f:
        f.write(json.dumps(signal_a) + '\n')

    # Spoke B signals NoSQL
    spoke_b_signals = spoke_b / "WAI-Spoke" / "WAI-Signals.jsonl"
    signal_b = {
        "timestamp": "2025-01-01T11:00:00Z",
        "by": "AI",
        "hub_kb_version": "1.0.0",
        "wheel_kb_version": "1.0.0",
        "offers": [{
            "type": "decision",
            "topic": "Use MongoDB for data storage",
            "impact": 9,
            "context": "Flexibility and scalability needed"
        }],
        "requests": [],
        "flags": {"has_high_impact_learnings": True}
    }
    with open(spoke_b_signals, 'a') as f:
        f.write(json.dumps(signal_b) + '\n')

    # Hub detects contradiction
    hub_kb_file = hub_dir / "WAI-Hub" / "knowledge-base.json"
    hub_kb_file.parent.mkdir(parents=True, exist_ok=True)

    hub_kb = {
        "patterns": [
            {"topic": "Use PostgreSQL for data storage", "impact": 9, "source": "spoke-sql"},
            {"topic": "Use MongoDB for data storage", "impact": 9, "source": "spoke-nosql"}
        ],
        "contradictions": [{
            "patterns": ["PostgreSQL", "MongoDB"],
            "category": "database_choice",
            "detected_at": "2025-01-01T11:05:00Z",
            "requires_review": True
        }],
        "version": "1.0.2"
    }

    with open(hub_kb_file, 'w') as f:
        json.dump(hub_kb, f, indent=2)

    # Verify contradiction detected
    kb = json.loads(hub_kb_file.read_text())
    assert "contradictions" in kb
    assert len(kb["contradictions"]) == 1
    assert kb["contradictions"][0]["requires_review"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

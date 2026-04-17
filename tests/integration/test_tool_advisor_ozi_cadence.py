"""
Integration tests for Tool Advisor Ozi cadence and stale marking.

Covers: stale detection via fingerprint, advisor_schedule_eval firing on drift,
Codex-only spoke evaluation, and Gemini-only drift surfacing.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

FRAMEWORK_ROOT = Path(__file__).parent.parent.parent
TOOL_ADVISOR = FRAMEWORK_ROOT / "tools" / "tool_advisor.py"
SCHEDULE_EVAL = FRAMEWORK_ROOT / "tools" / "advisor_schedule_eval.py"
sys.path.insert(0, str(FRAMEWORK_ROOT))


def run_tool_advisor(spoke_root: Path, *args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(TOOL_ADVISOR), "--root", str(spoke_root), *args, "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def run_schedule_eval(spoke_root: Path) -> list[dict]:
    result = subprocess.run(
        [sys.executable, str(SCHEDULE_EVAL), "--json"],
        capture_output=True,
        text=True,
        cwd=str(spoke_root),
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    return json.loads(result.stdout)


@pytest.fixture
def minimal_spoke(tmp_path):
    spoke = tmp_path / "test-spoke"
    spoke.mkdir()
    wai = spoke / "WAI-Spoke"
    wai.mkdir()
    return spoke


# ── STALE MARKING ───────────────────────────────────────────────────────────

def test_stale_marking_on_config_drift(minimal_spoke):
    """Changing a watched config file should mark audit as pending."""
    (minimal_spoke / "AGENTS.md").write_text("# Agents\n")
    run_tool_advisor(minimal_spoke)  # establish clean baseline fingerprint

    # Reset stale so we can see the drift signal
    state_path = minimal_spoke / "WAI-Spoke" / "advisors" / "tool-advisor" / "scan_state.json"
    state = json.loads(state_path.read_text())
    state["audit_pending"] = False
    state_path.write_text(json.dumps(state, indent=2))

    (minimal_spoke / "AGENTS.md").write_text("# Agents\n\nNew content.\n")
    result = run_tool_advisor(minimal_spoke, "--mark-stale-if-needed", "--session-id", "s001")

    assert result["audit_pending"] is True
    assert "config drift" in result["audit_reason"]
    assert "AGENTS.md" in result["audit_reason"]


def test_stale_marking_after_10_sessions(minimal_spoke):
    """10 distinct sessions since last audit should trigger audit_pending."""
    (minimal_spoke / "AGENTS.md").write_text("# Agents\n")
    run_tool_advisor(minimal_spoke)  # clean baseline

    # Reset to clear pending state
    state_path = minimal_spoke / "WAI-Spoke" / "advisors" / "tool-advisor" / "scan_state.json"
    state = json.loads(state_path.read_text())
    state["audit_pending"] = False
    state["sessions_since_last_audit"] = 0
    state_path.write_text(json.dumps(state, indent=2))

    # Simulate 10 sessions
    for i in range(10):
        run_tool_advisor(minimal_spoke, "--mark-stale-if-needed", "--session-id", f"session-{i:03d}")

    state = json.loads(state_path.read_text())
    assert state["audit_pending"] is True
    assert "10 sessions" in state.get("audit_reason", "")


def test_full_audit_clears_stale(minimal_spoke):
    """Running a full audit should reset audit_pending to False."""
    (minimal_spoke / "AGENTS.md").write_text("# Agents\n")

    # Force stale
    run_tool_advisor(minimal_spoke)
    state_path = minimal_spoke / "WAI-Spoke" / "advisors" / "tool-advisor" / "scan_state.json"
    state = json.loads(state_path.read_text())
    state["audit_pending"] = True
    state_path.write_text(json.dumps(state, indent=2))

    run_tool_advisor(minimal_spoke)

    state = json.loads(state_path.read_text())
    assert state["audit_pending"] is False


# ── CODEX-ONLY SPOKE ────────────────────────────────────────────────────────

def test_codex_only_spoke_evaluates_cleanly(minimal_spoke):
    """A spoke with only AGENTS.md should pass Codex and skip other areas."""
    (minimal_spoke / "AGENTS.md").write_text("# Agents\n\nRead `WAI-Spoke/skills/wai/wai.md`.\n")

    result = run_tool_advisor(minimal_spoke)

    assert result["score_by_area"]["Codex"] == "pass"
    assert result["score_by_area"]["Gemini"] == "skip"
    assert result["score_by_area"]["Claude"] == "skip"
    assert result["score"] >= 1  # at least Codex + Shared


def test_gemini_drift_surfaced_without_wakeup_rescan(minimal_spoke):
    """Gemini config drift should appear in stale marking without a full audit."""
    (minimal_spoke / "GEMINI.md").write_text("# Gemini\n")
    run_tool_advisor(minimal_spoke)  # baseline

    # Reset stale state
    state_path = minimal_spoke / "WAI-Spoke" / "advisors" / "tool-advisor" / "scan_state.json"
    state = json.loads(state_path.read_text())
    state["audit_pending"] = False
    state_path.write_text(json.dumps(state, indent=2))

    # Mutate GEMINI.md
    (minimal_spoke / "GEMINI.md").write_text("# Gemini\n\nNew guidance added.\n")

    stale = run_tool_advisor(minimal_spoke, "--mark-stale-if-needed", "--session-id", "s001")
    assert stale["audit_pending"] is True
    assert "GEMINI.md" in stale["audit_reason"]


# ── FINDINGS SCHEMA ─────────────────────────────────────────────────────────

def test_findings_have_category_field(minimal_spoke):
    """All findings emitted by the advisor should carry a category field."""
    (minimal_spoke / "GEMINI.md").write_text(
        "# Gemini\n\n## Session Start\n\n1. Read integration file.\n"
    )

    result = run_tool_advisor(minimal_spoke)

    for finding in result.get("findings", []):
        assert "category" in finding, f"Finding missing category: {finding}"
        assert finding["category"] in {
            "entrypoint-quality",
            "context-thrift",
            "stale-path-hygiene",
            "official-source-coverage",
            "template-live-parity",
            "compatibility-redirects",
            "uncategorized",
        }


def test_passes_jsonl_records_per_tool_scores(minimal_spoke):
    """Each audit pass should record score_by_area in passes.jsonl."""
    (minimal_spoke / "AGENTS.md").write_text("# Agents\n")
    run_tool_advisor(minimal_spoke)

    passes_path = minimal_spoke / "WAI-Spoke" / "advisors" / "tool-advisor" / "passes.jsonl"
    assert passes_path.exists()
    lines = [l for l in passes_path.read_text().splitlines() if l.strip()]
    assert len(lines) >= 1

    record = json.loads(lines[-1])
    assert "score_by_area" in record
    assert "Codex" in record["score_by_area"]
    assert "Claude" in record["score_by_area"]
    assert "Gemini" in record["score_by_area"]

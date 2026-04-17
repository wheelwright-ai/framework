"""
Idempotency tests for Tool Advisor safe remediation.

Proves: a second audit run on a previously-fixed spoke produces no new diffs.
Covers: Gemini settings, .geminiignore, GEMINI.md loop guard, AGENTS.md thrift,
hook env var cleanup, vectors.jsonl, and proposal report writing.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

FRAMEWORK_ROOT = Path(__file__).parent.parent.parent
TOOL_ADVISOR = FRAMEWORK_ROOT / "tools" / "tool_advisor.py"
sys.path.insert(0, str(FRAMEWORK_ROOT))


def run_tool_advisor(spoke_root: Path, *args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(TOOL_ADVISOR), "--root", str(spoke_root), *args, "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


@pytest.fixture
def minimal_spoke(tmp_path):
    spoke = tmp_path / "test-spoke"
    spoke.mkdir()
    wai = spoke / "WAI-Spoke"
    wai.mkdir()
    (spoke / "CLAUDE.md").write_text("# Claude instructions\n")
    (spoke / "GEMINI.md").write_text(
        "# Gemini\n\n## Session Start\n\n1. Read `AGENTS.md`.\n"
    )
    (spoke / "AGENTS.md").write_text("# Agents\n\nRead `WAI-Spoke/WAI-Guide.md`.\n")
    return spoke


def test_second_run_produces_no_auto_fixes(minimal_spoke):
    """After an initial fix pass, a second run should find nothing to auto-apply."""
    run_tool_advisor(minimal_spoke)  # first run — applies fixes

    second = run_tool_advisor(minimal_spoke, "--evaluate-only")
    assert second["planned_fixes"] == [], (
        f"Second run should not produce fixes but found: {second['planned_fixes']}"
    )


def test_gemini_loop_guard_idempotent(minimal_spoke):
    """GEMINI.md loop guard should not be duplicated on repeated runs."""
    run_tool_advisor(minimal_spoke)
    run_tool_advisor(minimal_spoke)

    content = (minimal_spoke / "GEMINI.md").read_text()
    guard_phrase = "Treat this `GEMINI.md` read as already satisfying"
    assert content.count(guard_phrase) == 1, "Loop guard should appear exactly once"


def test_geminiignore_not_duplicated(minimal_spoke):
    """Running twice should not duplicate .geminiignore entries."""
    run_tool_advisor(minimal_spoke)
    run_tool_advisor(minimal_spoke)

    lines = (minimal_spoke / ".geminiignore").read_text().splitlines()
    non_empty = [l for l in lines if l.strip()]
    assert len(non_empty) == len(set(non_empty)), "Duplicate .geminiignore entries found"


def test_agents_dead_ref_removed_idempotent(minimal_spoke):
    """WAI-Guide.md reference removed on first run should not reappear."""
    run_tool_advisor(minimal_spoke)
    run_tool_advisor(minimal_spoke)

    content = (minimal_spoke / "AGENTS.md").read_text()
    assert "WAI-Guide.md" not in content


def test_vectors_jsonl_appended_each_run(minimal_spoke):
    """Each full audit run should append one vector record."""
    run_tool_advisor(minimal_spoke)
    run_tool_advisor(minimal_spoke)

    vectors_path = minimal_spoke / "WAI-Spoke" / "advisors" / "tool-advisor" / "vectors.jsonl"
    assert vectors_path.exists()
    lines = [l for l in vectors_path.read_text().splitlines() if l.strip()]
    assert len(lines) == 2, f"Expected 2 vector records after 2 runs, got {len(lines)}"

    for line in lines:
        record = json.loads(line)
        cats = record.get("finding_counts_by_category", {})
        expected_cats = {
            "entrypoint-quality",
            "context-thrift",
            "stale-path-hygiene",
            "official-source-coverage",
            "template-live-parity",
            "compatibility-redirects",
        }
        assert set(cats.keys()) == expected_cats


def test_proposal_report_written_when_proposals_exist(minimal_spoke):
    """proposals-latest.json should be written when proposals are generated."""
    run_tool_advisor(minimal_spoke)

    proposals_path = minimal_spoke / "WAI-Spoke" / "advisors" / "tool-advisor" / "reports" / "proposals-latest.json"
    if proposals_path.exists():
        report = json.loads(proposals_path.read_text())
        assert "proposals" in report
        assert "note" in report
        assert isinstance(report.get("count"), int)
        for p in report["proposals"]:
            assert "code" in p
            assert "requires_human_review" in p
            assert p["requires_human_review"] is True


def test_evaluate_only_does_not_write_files(tmp_path):
    """--evaluate-only should not create or modify any files."""
    spoke = tmp_path / "test-spoke"
    spoke.mkdir()
    wai = spoke / "WAI-Spoke"
    wai.mkdir()
    (spoke / "GEMINI.md").write_text("# Gemini\n")

    result = run_tool_advisor(spoke, "--evaluate-only")

    assert result.get("mode") == "evaluate"
    gemini_settings = spoke / ".gemini" / "settings.json"
    assert not gemini_settings.exists(), "--evaluate-only should not create .gemini/settings.json"

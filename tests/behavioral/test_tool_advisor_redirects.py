"""
Behavioral tests for Tool Advisor compatibility redirect checks.

Covers: legacy maximizer redirect detection, check_compatibility_redirects(),
CATEGORY_MAP classification, and proposal generation.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

FRAMEWORK_ROOT = Path(__file__).parent.parent.parent
TOOL_ADVISOR = FRAMEWORK_ROOT / "tools" / "tool_advisor.py"
sys.path.insert(0, str(FRAMEWORK_ROOT))

import tools.tool_advisor as ta


def run_tool_advisor(spoke_root: Path, *args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(TOOL_ADVISOR), "--root", str(spoke_root), *args, "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


# ── CATEGORY_MAP ────────────────────────────────────────────────────────────

def test_category_map_covers_all_check_codes():
    """All known check codes should resolve to a named category."""
    known_codes = [
        "claude-md-missing",
        "gemini-md-missing",
        "wrapper-script-missing",
        "wrapper-script-not-executable",
        "gemini-loop-guard-missing",
        "wakeup-guard-missing",
        "claude-settings-invalid",
        "claude-hook-env-vars",
        "claude-hook-script-missing",
        "codex-dead-wai-guide",
        "bootstrap-hook-env-var",
        "maximizer-not-redirected",
    ]
    for code in known_codes:
        assert code in ta.CATEGORY_MAP, f"Missing CATEGORY_MAP entry for code: {code}"
        assert ta.CATEGORY_MAP[code] != "uncategorized", f"Code {code} should have explicit category"


def test_tag_category_adds_category_field():
    findings = [
        {"area": "Claude", "level": "warn", "code": "claude-md-missing", "message": "test"},
        {"area": "Gemini", "level": "fail", "code": "gemini-loop-guard-missing", "message": "test"},
        {"area": "Codex", "level": "fail", "code": "codex-dead-wai-guide", "message": "test"},
    ]
    tagged = ta._tag_category(findings)
    assert tagged[0]["category"] == "entrypoint-quality"
    assert tagged[1]["category"] == "context-thrift"
    assert tagged[2]["category"] == "stale-path-hygiene"


def test_tag_category_unknown_code_becomes_uncategorized():
    findings = [{"area": "Shared", "level": "warn", "code": "invented-code", "message": "test"}]
    tagged = ta._tag_category(findings)
    assert tagged[0]["category"] == "uncategorized"


# ── REMEDIATION_MATRIX ──────────────────────────────────────────────────────

def test_remediation_matrix_structure():
    matrix = ta.REMEDIATION_MATRIX
    assert "safe_auto" in matrix
    assert "proposal_only" in matrix
    assert "never_auto" in matrix
    for tier, codes in matrix.items():
        assert isinstance(codes, list), f"Tier {tier} should be a list"


def test_remediation_matrix_no_overlap():
    """No code should appear in more than one tier."""
    all_codes: list[str] = []
    for codes in ta.REMEDIATION_MATRIX.values():
        all_codes.extend(codes)
    assert len(all_codes) == len(set(all_codes)), "Duplicate codes found in REMEDIATION_MATRIX"


# ── COMPATIBILITY REDIRECT CHECK ────────────────────────────────────────────

def test_check_compatibility_redirects_pass_when_redirected(tmp_spoke):
    cmd_dir = tmp_spoke / "templates" / "commands"
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "wai-claude-maximizer.md").write_text(
        "# Redirected\n\nThis skill redirects to the Tool Advisor. Run `/wai-tool-advisor`.\n"
    )
    findings, _ = ta.check_compatibility_redirects(tmp_spoke)
    assert not any(f["code"] == "maximizer-not-redirected" for f in findings)


def test_check_compatibility_redirects_warns_when_not_redirected(tmp_spoke):
    cmd_dir = tmp_spoke / "templates" / "commands"
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "wai-claude-maximizer.md").write_text(
        "# Claude Maximizer\n\nDetailed optimization guidance goes here.\n"
    )
    findings, _ = ta.check_compatibility_redirects(tmp_spoke)
    codes = [f["code"] for f in findings]
    assert "maximizer-not-redirected" in codes


# ── PROPOSAL GENERATION ─────────────────────────────────────────────────────

def test_mcp_proposal_generated_when_absent(tmp_spoke):
    (tmp_spoke / "CLAUDE.md").write_text("# Claude instructions\n")
    report = run_tool_advisor(tmp_spoke)
    proposal_codes = [p["code"] for p in report["proposals"]]
    assert "mcp-not-configured" in proposal_codes


def test_mcp_proposal_absent_when_mcp_json_present(tmp_spoke):
    (tmp_spoke / "CLAUDE.md").write_text("# Claude instructions\n")
    (tmp_spoke / ".mcp.json").write_text(json.dumps({"servers": {}}) + "\n")
    report = run_tool_advisor(tmp_spoke)
    proposal_codes = [p["code"] for p in report["proposals"]]
    assert "mcp-not-configured" not in proposal_codes


def test_cross_tool_coverage_proposal_when_agents_but_no_gemini(tmp_spoke):
    (tmp_spoke / "CLAUDE.md").write_text("# Claude\n")
    (tmp_spoke / "AGENTS.md").write_text("# Agents\n")
    report = run_tool_advisor(tmp_spoke)
    proposal_codes = [p["code"] for p in report["proposals"]]
    assert "gemini-coverage-absent" in proposal_codes


def test_cross_tool_coverage_proposal_when_gemini_but_no_agents(tmp_spoke):
    (tmp_spoke / "CLAUDE.md").write_text("# Claude\n")
    (tmp_spoke / "GEMINI.md").write_text("# Gemini\n")
    report = run_tool_advisor(tmp_spoke)
    proposal_codes = [p["code"] for p in report["proposals"]]
    assert "codex-coverage-absent" in proposal_codes


def test_no_coverage_proposal_when_all_three_present(tmp_spoke):
    (tmp_spoke / "CLAUDE.md").write_text("# Claude\n")
    (tmp_spoke / "GEMINI.md").write_text("# Gemini\n")
    (tmp_spoke / "AGENTS.md").write_text("# Agents\n")
    report = run_tool_advisor(tmp_spoke)
    proposal_codes = [p["code"] for p in report["proposals"]]
    assert "gemini-coverage-absent" not in proposal_codes
    assert "codex-coverage-absent" not in proposal_codes

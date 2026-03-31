#!/usr/bin/env python3
"""
spoke_integrity_score.py — Composite spoke integrity score (0-100)

Five dimensions (20pts each):
  1. structure  — WAI-State.json, Skills, bytype/, sessions/, seed/
  2. hooks      — all 5 hooks configured, no env vars in commands
  3. lugs       — PEV present on actionable lugs, no location violations
  4. parity     — matches hub parity head (uses spoke_parity_check)
  5. hub        — hub reachable, teachings current (0 unprocessed)

Designed for Tender, session-start.sh, and human review.
Exit codes: 0 = healthy (>=80), 1 = degraded (50-79), 2 = critical (<50)
"""

import argparse
import json
import os
import sys
from pathlib import Path


def score_structure(spoke: Path) -> tuple[int, list[str]]:
    """Max 20 pts. Each required file/dir = 4pts."""
    score = 0
    notes = []
    checks = [
        (spoke / "WAI-Spoke" / "WAI-State.json", "WAI-State.json"),
        (spoke / "WAI-Spoke" / "skills" / "WAI-Skills.jsonl", "WAI-Skills.jsonl"),
        (spoke / "WAI-Spoke" / "lugs" / "bytype", "lugs/bytype/"),
        (spoke / "WAI-Spoke" / "sessions", "sessions/"),
        (spoke / "WAI-Spoke" / "seed" / "ingest", "seed/ingest/"),
    ]
    for path, label in checks:
        if path.exists():
            score += 4
        else:
            notes.append(f"missing: {label}")
    return score, notes


def score_hooks(spoke: Path) -> tuple[int, list[str]]:
    """Max 20 pts. 5 required hooks @ 3pts, no env-var penalty (-5)."""
    score = 0
    notes = []
    settings = spoke / ".claude" / "settings.json"
    if not settings.exists():
        return 0, ["settings.json missing"]

    with open(settings) as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError:
            return 0, ["settings.json invalid JSON"]

    hooks = cfg.get("hooks", {})
    required = ["SessionStart", "UserPromptSubmit", "PreToolUse", "Stop", "PreCompact"]
    for h in required:
        if h in hooks:
            score += 3
        else:
            notes.append(f"missing hook: {h}")

    # Env var penalty
    raw = json.dumps(cfg)
    if "$CLAUDE_PROJECT_DIR" in raw:
        score = max(0, score - 5)
        notes.append("$CLAUDE_PROJECT_DIR in hook commands (use absolute paths)")

    return min(score, 20), notes


def score_lugs(spoke: Path) -> tuple[int, list[str]]:
    """Max 20 pts. Deductions for PEV violations and schema issues."""
    score = 20
    notes = []
    bytype = spoke / "WAI-Spoke" / "lugs" / "bytype"
    if not bytype.exists():
        return 0, ["lugs/bytype/ missing"]

    pev_violations = 0
    schema_violations = 0
    total_actionable = 0

    actionable_types = {"task", "bug", "feature", "implementation"}

    for ltype_dir in bytype.iterdir():
        if not ltype_dir.is_dir():
            continue
        ltype = ltype_dir.name
        for status_dir in ltype_dir.iterdir():
            if not status_dir.is_dir():
                continue
            for lug_file in status_dir.glob("*.json"):
                try:
                    with open(lug_file) as f:
                        lug = json.load(f)
                except (json.JSONDecodeError, OSError):
                    schema_violations += 1
                    continue

                # PEV check for actionable lugs
                if ltype in actionable_types and status_dir.name in ("open", "in_progress"):
                    total_actionable += 1
                    has_perceive = bool(lug.get("perceive"))
                    has_execute = bool(lug.get("execute"))
                    has_verify = bool(lug.get("verify"))
                    if not (has_perceive and has_execute and has_verify):
                        pev_violations += 1

    # Deductions: each PEV violation = -1pt (cap at -10)
    pev_deduct = min(pev_violations, 10)
    score -= pev_deduct
    if pev_violations:
        notes.append(f"{pev_violations}/{total_actionable} actionable lugs missing PEV")

    # Schema violations
    if schema_violations:
        score -= min(schema_violations * 2, 5)
        notes.append(f"{schema_violations} lug files with JSON errors")

    return max(0, score), notes


def score_parity(spoke: Path, hub_path: str) -> tuple[int, list[str]]:
    """Max 20 pts. At parity = 20, each gap = -5."""
    if not hub_path:
        return 0, ["hub_path not configured"]

    # Import and run parity check inline
    sys.path.insert(0, str(spoke / "tools"))
    try:
        from spoke_parity_check import check_spoke
        result = check_spoke(spoke, hub_path, verbose=False)
        if "error" in result:
            return 5, [f"parity check error: {result['error']}"]
        gaps = result.get("gaps", [])
        score = max(0, 20 - len(gaps) * 5)
        notes = [f"gap: {g['patch']} — {g['detail']}" for g in gaps]
        return score, notes
    except ImportError:
        return 5, ["spoke_parity_check.py not found"]
    finally:
        sys.path.pop(0)


def score_hub(spoke: Path, hub_path: str) -> tuple[int, list[str]]:
    """Max 20 pts: hub reachable (10), teachings current (10)."""
    if not hub_path:
        return 0, ["hub_path not configured"]

    hub = Path(hub_path)
    score = 0
    notes = []

    # Hub reachable
    if hub.exists():
        score += 10
    else:
        notes.append(f"hub not found: {hub_path}")
        return score, notes

    # Teachings current (no unprocessed)
    teach_dir = hub / "teachings_repo" / "spoke" / "current"
    processed_dir = spoke / "WAI-Spoke" / "seed" / "ingest" / "processed"
    if not teach_dir.exists():
        notes.append("teachings_repo/spoke/current/ missing")
    else:
        unprocessed = 0
        for f in teach_dir.glob("*.teaching"):
            if not (processed_dir / f.name).exists():
                unprocessed += 1
        if unprocessed == 0:
            score += 10
        else:
            deduct = min(unprocessed * 2, 10)
            score += max(0, 10 - deduct)
            notes.append(f"{unprocessed} unprocessed teachings")

    return score, notes


def compute_score(spoke_path: str) -> dict:
    spoke = Path(spoke_path).resolve()

    # Load hub path from state
    hub_path = ""
    state_file = spoke / "WAI-Spoke" / "WAI-State.json"
    if state_file.exists():
        try:
            with open(state_file) as f:
                state = json.load(f)
            hub_path = state.get("wheel", {}).get("hub_path", "")
        except (json.JSONDecodeError, OSError):
            pass

    dims = {}
    s1, n1 = score_structure(spoke)
    s2, n2 = score_hooks(spoke)
    s3, n3 = score_lugs(spoke)
    s4, n4 = score_parity(spoke, hub_path)
    s5, n5 = score_hub(spoke, hub_path)

    dims = {
        "structure": {"score": s1, "max": 20, "notes": n1},
        "hooks":     {"score": s2, "max": 20, "notes": n2},
        "lugs":      {"score": s3, "max": 20, "notes": n3},
        "parity":    {"score": s4, "max": 20, "notes": n4},
        "hub":       {"score": s5, "max": 20, "notes": n5},
    }

    total = s1 + s2 + s3 + s4 + s5
    grade = "healthy" if total >= 80 else ("degraded" if total >= 50 else "critical")

    return {
        "spoke": str(spoke),
        "score": total,
        "max": 100,
        "grade": grade,
        "dimensions": dims,
    }


def print_report(result: dict):
    score = result["score"]
    grade = result["grade"]
    icon = "✓" if grade == "healthy" else ("⚠" if grade == "degraded" else "✗")

    print(f"Integrity Score: {score}/100  [{icon} {grade.upper()}]")
    print(f"Spoke: {result['spoke']}")
    print()
    for dim, data in result["dimensions"].items():
        s, m = data["score"], data["max"]
        bar = "█" * (s * 5 // m) + "░" * (5 - s * 5 // m)
        print(f"  {dim:<10} {bar}  {s:>2}/{m}")
        for note in data["notes"]:
            print(f"              ↳ {note}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Compute spoke integrity score (0-100)")
    parser.add_argument("spoke_path", nargs="?", default=".", help="Path to spoke (default: .)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--quiet", action="store_true", help="Score only (no report)")
    args = parser.parse_args()

    result = compute_score(args.spoke_path)

    if args.json:
        print(json.dumps(result, indent=2))
    elif args.quiet:
        print(result["score"])
    else:
        print_report(result)

    score = result["score"]
    if score >= 80:
        sys.exit(0)
    elif score >= 50:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()

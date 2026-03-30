#!/usr/bin/env python3
"""Shared lug utilities — path resolution, blocking, execute-when evaluation.

Used by score_backlog.py, wai_ozi.py, and wai-chain.sh (via inline Python).
"""

import json
from pathlib import Path
from typing import Any

SPOKE = Path(__file__).parent.parent / "WAI-Spoke"
BYTYPE = SPOKE / "lugs" / "bytype"


def resolve_lug_path(lug_id: str) -> Path | None:
    """Find a lug file across all bytype/ folders."""
    if not BYTYPE.exists():
        return None
    for type_dir in BYTYPE.iterdir():
        if not type_dir.is_dir():
            continue
        for status_dir in type_dir.iterdir():
            if not status_dir.is_dir():
                continue
            candidate = status_dir / f"{lug_id}.json"
            if candidate.exists():
                return candidate
    return None


def is_lug_completed(lug_id: str) -> bool:
    """Check if a lug exists in any completed/ or delivered/ folder."""
    if not BYTYPE.exists():
        return False
    for type_dir in BYTYPE.iterdir():
        if not type_dir.is_dir():
            continue
        for done_dir in ("completed", "delivered"):
            candidate = type_dir / done_dir / f"{lug_id}.json"
            if candidate.exists():
                return True
    return False


def is_blocked(lug: dict) -> bool:
    """Check if a lug has unresolved blockers in its blocked_by array."""
    blocked_by = lug.get("blocked_by", [])
    if not blocked_by:
        return False
    for blocker_id in blocked_by:
        if not is_lug_completed(blocker_id):
            return True
    return False


def blocked_reason(lug: dict) -> str:
    """Return human-readable reason why a lug is blocked, or empty string."""
    blocked_by = lug.get("blocked_by", [])
    if not blocked_by:
        return ""
    unresolved = [bid for bid in blocked_by if not is_lug_completed(bid)]
    if not unresolved:
        return ""
    return f"blocked by: {', '.join(unresolved)}"


def evaluate_execute_when(lug: dict, phases: list[dict] | None = None) -> tuple[bool, str]:
    """Evaluate execute_when conditions on a lug.

    Returns (ready, reason):
        ready=True  → all conditions met, lug can dispatch
        ready=False → reason explains what's blocking

    Conditions (all must be satisfied if present):
        all_completed:    every listed lug ID must be in completed/
        any_completed:    at least one listed lug ID must be in completed/
        phase_completed:  all lugs belonging to the named phase must be completed
        manual_gate:      if true, always returns not-ready (requires user override)
    """
    ew = lug.get("execute_when")
    if not ew:
        # No gate — also check legacy blocked_by
        if is_blocked(lug):
            return False, blocked_reason(lug)
        return True, ""

    # Manual gate — always blocks unless overridden
    if ew.get("manual_gate", False):
        return False, "manual gate: requires explicit user approval"

    # all_completed — AND logic
    all_completed = ew.get("all_completed", [])
    if all_completed:
        missing = [lid for lid in all_completed if not is_lug_completed(lid)]
        if missing:
            return False, f"waiting for all: {', '.join(missing)}"

    # any_completed — OR logic
    any_completed = ew.get("any_completed", [])
    if any_completed:
        if not any(is_lug_completed(lid) for lid in any_completed):
            return False, f"waiting for any of: {', '.join(any_completed)}"

    # phase_completed — all members of named phase must be done
    phase_id = ew.get("phase_completed")
    if phase_id and phases:
        phase_members = _get_phase_members(phase_id)
        incomplete = [m for m in phase_members if not is_lug_completed(m)]
        if incomplete:
            return False, f"phase '{phase_id}' incomplete: {', '.join(incomplete[:5])}"

    # Also check legacy blocked_by
    if is_blocked(lug):
        return False, blocked_reason(lug)

    return True, ""


def _get_phase_members(phase_id: str) -> list[str]:
    """Find all lug IDs that declare membership in a given phase."""
    members: list[str] = []
    if not BYTYPE.exists():
        return members
    # Scan all lugs (any status) for phase field
    for type_dir in BYTYPE.iterdir():
        if not type_dir.is_dir():
            continue
        for status_dir in type_dir.iterdir():
            if not status_dir.is_dir():
                continue
            for lug_file in status_dir.glob("*.json"):
                try:
                    data = json.loads(lug_file.read_text())
                    if data.get("phase") == phase_id:
                        members.append(data.get("id", lug_file.stem))
                except (json.JSONDecodeError, OSError):
                    continue
    return members


def load_phases_from_state() -> list[dict[str, Any]]:
    """Load phase definitions from WAI-State.json _work_queue.phases."""
    state_file = SPOKE / "WAI-State.json"
    if not state_file.exists():
        return []
    try:
        state = json.loads(state_file.read_text())
        return state.get("_work_queue", {}).get("phases", [])
    except (json.JSONDecodeError, OSError):
        return []

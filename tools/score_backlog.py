#!/usr/bin/env python3
"""Score active lugs by ROI with vibe-aware tiebreaking.

Usage:
    python3 tools/score_backlog.py [vibe]

Where vibe is one of: build, fix, think, grind, ship
Default: no vibe filter (pure ROI ordering).
"""

import json
import sys
from pathlib import Path

SPOKE = Path(__file__).parent.parent / "WAI-Spoke"
BYTYPE = SPOKE / "lugs" / "bytype"

# Import shared lug utilities
sys.path.insert(0, str(Path(__file__).parent))
from lug_utils import is_blocked, blocked_reason, evaluate_execute_when, load_phases_from_state

# Vibe affinity: maps vibe -> type/tag -> bonus (0.0 to 1.0 added to ROI)
# Vibe affinity: multiplier applied to base ROI (1.0 = neutral)
# Values >1.0 boost, <1.0 suppress. This is multiplicative so it
# actually reorders items rather than adding tiny flat bonuses.
VIBE_AFFINITY = {
    "build": {
        "feature": 1.6, "epic": 1.3, "task": 1.0,
        "bug": 0.6, "signal": 0.5, "other": 0.8,
    },
    "fix": {
        "bug": 1.8, "task": 1.1, "feature": 0.7,
        "epic": 0.6, "signal": 0.8, "other": 0.9,
    },
    "think": {
        "epic": 1.6, "signal": 1.3, "feature": 1.2,
        "task": 0.7, "bug": 0.6, "other": 1.1,
    },
    "grind": {
        "task": 1.4, "signal": 1.2, "bug": 1.1,
        "feature": 0.6, "epic": 0.5, "other": 1.3,
    },
    "ship": {
        "in_progress": 1.8,  # strong bonus for anything already started
        "bug": 1.2, "task": 1.1, "feature": 1.1,
        "epic": 0.7, "signal": 0.6, "other": 0.9,
    },
}

# Default impact/effort by type when lug doesn't specify
TYPE_DEFAULTS = {
    "bug": {"impact": 6, "effort": 2},
    "task": {"impact": 5, "effort": 2},
    "feature": {"impact": 7, "effort": 3},
    "epic": {"impact": 8, "effort": 4},
    "signal": {"impact": 5, "effort": 1},
    "other": {"impact": 3, "effort": 1},
}


def infer_leverage(lug: dict) -> float:
    """Estimate leverage multiplier from lug content."""
    text = json.dumps(lug).lower()
    # Foundational items that unblock others
    if any(kw in text for kw in ["foundational", "unblocks", "prerequisite", "schema", "bootstrap"]):
        return 1.5
    # Items with children or dependents
    if "children" in lug or "blocks" in text:
        return 1.5
    # In-progress items (momentum)
    if lug.get("s") in ("in_progress", "in-progress", "p"):
        return 1.3
    return 1.0


def score_lug(lug: dict, lug_type: str, status: str, vibe: str | None = None) -> float:
    """Calculate ROI score with optional vibe tiebreaking."""
    defaults = TYPE_DEFAULTS.get(lug_type, TYPE_DEFAULTS["other"])
    raw_impact = lug.get("impact", defaults["impact"])
    raw_effort = lug.get("effort", defaults["effort"])
    try:
        impact = float(raw_impact)
    except (TypeError, ValueError):
        impact = float(defaults["impact"])
    try:
        effort = float(raw_effort)
    except (TypeError, ValueError):
        effort = float(defaults["effort"])
    leverage = infer_leverage(lug)

    # Base ROI
    # Signals are routing chores, not implementation — cap their ROI
    # so they don't crowd out real work
    if lug_type == "signal":
        roi = min(impact * 0.5, 5.0)  # cap at 5.0, scaled down
    else:
        roi = (impact * leverage) / max(effort, 0.5)

    # Vibe multiplier — reshapes ordering to match energy
    if vibe and vibe in VIBE_AFFINITY:
        affinity = VIBE_AFFINITY[vibe]
        multiplier = affinity.get(lug_type, 1.0)
        # Ship vibe: extra boost for in-progress items (finish what's started)
        if vibe == "ship" and status in ("in_progress", "in-progress"):
            multiplier *= affinity.get("in_progress", 1.0)
        roi *= multiplier

    return round(roi, 2)


def scan_active_lugs() -> list[dict]:
    """Scan bytype/ for open and in_progress lugs."""
    results = []
    for type_dir in sorted(BYTYPE.iterdir()):
        if not type_dir.is_dir():
            continue
        lug_type = type_dir.name
        for status_dir in ["open", "in_progress", "undelivered"]:
            status_path = type_dir / status_dir
            if not status_path.exists():
                continue
            for lug_file in sorted(status_path.glob("*.json")):
                try:
                    lug = json.loads(lug_file.read_text())
                    results.append({
                        "file": lug_file.name,
                        "type": lug_type,
                        "status": status_dir,
                        "title": lug.get("t", lug.get("title", lug_file.stem)),
                        "impact": lug.get("impact"),
                        "effort": lug.get("effort"),
                        "lug": lug,
                    })
                except (json.JSONDecodeError, OSError) as e:
                    print(f"  SKIP {lug_file.name}: {e}", file=sys.stderr)
    return results


def update_state_work_queue(scored: list[dict], phases: list[dict]) -> None:
    """Write top items back to WAI-State.json _work_queue."""
    state_file = SPOKE / "WAI-State.json"
    if not state_file.exists():
        return
    try:
        state = json.loads(state_file.read_text())
    except (json.JSONDecodeError, OSError):
        return

    wq = state.setdefault("_work_queue", {"enabled": True})
    # Only include dispatchable items (not blocked/gated)
    items = []
    for entry in scored[:15]:
        if entry.get("_blocked") or entry.get("_gated"):
            continue
        items.append({
            "id": entry["lug"].get("id", entry["file"].replace(".json", "")),
            "roi": entry["roi"],
            "type": entry["type"],
            "status": "ready",
            "title": entry["title"][:80],
            "phase": entry["lug"].get("phase"),
            "tagged_next": len(items) == 0,
        })
        if len(items) >= 10:
            break

    wq["items"] = items
    wq["last_scored_at"] = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    ).isoformat()
    if phases:
        wq["phases"] = phases

    state_file.write_text(json.dumps(state, indent=2) + "\n")
    print(f"\n  ✅ _work_queue updated ({len(items)} items written to WAI-State.json)")


def main():
    args = sys.argv[1:]
    update_state = "--update-state" in args
    if update_state:
        args.remove("--update-state")

    vibe = args[0].lower() if args else None
    if vibe and vibe not in VIBE_AFFINITY:
        print(f"Unknown vibe: {vibe}. Options: {', '.join(VIBE_AFFINITY.keys())}")
        sys.exit(1)

    phases = load_phases_from_state()
    lugs = scan_active_lugs()
    scored = []
    for entry in lugs:
        roi = score_lug(entry["lug"], entry["type"], entry["status"], vibe)
        # Check blocking/gating
        ready, gate_reason = evaluate_execute_when(entry["lug"], phases)
        scored.append({
            **entry,
            "roi": roi,
            "_blocked": is_blocked(entry["lug"]),
            "_gated": not ready,
            "_gate_reason": gate_reason,
        })

    scored.sort(key=lambda x: x["roi"], reverse=True)

    # Partition into dispatchable and gated
    dispatchable = [s for s in scored if not s["_gated"]]
    gated = [s for s in scored if s["_gated"]]

    # Display dispatchable items
    vibe_label = f" | Vibe: {vibe}" if vibe else ""
    print(f"\n{'='*80}")
    print(f"  Ozi ROI Backlog — {len(dispatchable)} ready, {len(gated)} gated{vibe_label}")
    print(f"{'='*80}\n")
    print(f"  {'#':>3}  {'ROI':>5}  {'Type':<10} {'Status':<13} {'Title'}")
    print(f"  {'─'*3}  {'─'*5}  {'─'*10} {'─'*13} {'─'*40}")

    for i, item in enumerate(dispatchable, 1):
        phase_tag = f" [{item['lug'].get('phase', '')}]" if item["lug"].get("phase") else ""
        print(f"  {i:>3}  {item['roi']:>5.1f}  {item['type']:<10} {item['status']:<13} {item['title'][:60]}{phase_tag}")
        if i == 10 and len(dispatchable) > 10:
            print(f"\n  ... and {len(dispatchable) - 10} more ready items\n")
            break

    # Display gated items
    if gated:
        print(f"\n  {'─'*78}")
        print(f"  GATED ({len(gated)} items — waiting on conditions)")
        print(f"  {'─'*78}")
        for item in gated[:5]:
            reason = item["_gate_reason"][:50] if item["_gate_reason"] else "unknown"
            print(f"  🔒 {item['roi']:>5.1f}  {item['type']:<10} {item['title'][:45]}  ← {reason}")
        if len(gated) > 5:
            print(f"  ... and {len(gated) - 5} more gated items")

    # Summary by type
    print(f"\n  {'Type':<12} {'Count':>5}  {'Avg ROI':>7}  {'Best':>5}")
    print(f"  {'─'*12} {'─'*5}  {'─'*7}  {'─'*5}")
    types: dict[str, list[float]] = {}
    for item in scored:
        t = item["type"]
        if t not in types:
            types[t] = []
        types[t].append(item["roi"])
    for t in sorted(types, key=lambda x: -(sum(types[x]) / len(types[x]))):
        vals = types[t]
        print(f"  {t:<12} {len(vals):>5}  {sum(vals)/len(vals):>7.1f}  {max(vals):>5.1f}")

    print()

    if update_state:
        update_state_work_queue(scored, phases)


if __name__ == "__main__":
    main()

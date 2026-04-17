#!/usr/bin/env python3
"""
advisor_schedule_eval.py — Evaluate which advisors should fire this session.

Reads WAI-Spoke/advisors/schedule-index.json, compares last_run_at + run_cadence
against current time, and checks event_triggers against current spoke state.

Output: JSON array of {advisor_id, should_fire, reason}

Usage:
    python3 tools/advisor_schedule_eval.py
    python3 tools/advisor_schedule_eval.py --json   # machine-readable only
"""

import json
import sys
import datetime
import os
from pathlib import Path

SCHEDULE_INDEX = "WAI-Spoke/advisors/schedule-index.json"
WAI_STATE = "WAI-Spoke/WAI-State.json"
TOOL_ADVISOR_STATE = "WAI-Spoke/advisors/tool-advisor/scan_state.json"

CADENCE_DAYS = {
    "daily": 1,
    "weekly": 7,
    "biweekly": 14,
    "monthly": 30,
    "never": None,
}


def load_spoke_state():
    try:
        return json.load(open(WAI_STATE))
    except Exception:
        return {}


def check_event_triggers(triggers: list, state: dict) -> str | None:
    """Return trigger reason if any event trigger is active, else None."""
    wq = state.get("_work_queue", {})
    items = wq.get("items", [])
    open_count = len([i for i in items if i.get("status") == "ready"])

    trigger_map = {
        "lug_created": open_count > 0,
        "lug_updated": open_count > 0,
        "open_lugs_exceed_10": open_count > 10,
        "release_candidate_exists": False,  # extend as needed
        "deploy_gate_triggered": False,
        "specialist_run_completed": False,
    }

    for trigger in triggers:
        if trigger_map.get(trigger, False):
            return f"event trigger: {trigger}"
    return None


def eval_advisor(entry: dict, now: datetime.datetime, state: dict) -> dict:
    advisor_id = entry["advisor_id"]
    cadence_key = entry.get("run_cadence") or "weekly"
    last_run_str = entry.get("last_run_at")
    triggers = entry.get("event_triggers") or []

    if advisor_id == "tool-advisor" and Path(TOOL_ADVISOR_STATE).exists():
        try:
            tool_state = json.load(open(TOOL_ADVISOR_STATE))
            if tool_state.get("audit_pending"):
                reason = tool_state.get("audit_reason") or "tool config drift"
                return {"advisor_id": advisor_id, "should_fire": True, "reason": reason}
        except Exception:
            return {"advisor_id": advisor_id, "should_fire": True, "reason": "tool-advisor state unreadable"}

    # Check event triggers first
    trigger_reason = check_event_triggers(triggers, state)
    if trigger_reason:
        return {"advisor_id": advisor_id, "should_fire": True, "reason": trigger_reason}

    # Check cadence
    days = CADENCE_DAYS.get(cadence_key)
    if days is None:
        return {"advisor_id": advisor_id, "should_fire": False, "reason": "cadence=never"}

    if last_run_str is None:
        return {"advisor_id": advisor_id, "should_fire": True, "reason": "never run"}

    try:
        last_run = datetime.datetime.fromisoformat(last_run_str.replace("Z", "+00:00"))
        if last_run.tzinfo is None:
            last_run = last_run.replace(tzinfo=datetime.timezone.utc)
        elapsed = (now - last_run).days
        if elapsed >= days:
            return {
                "advisor_id": advisor_id,
                "should_fire": True,
                "reason": f"{elapsed}d since last run (cadence: {cadence_key})",
            }
        else:
            return {
                "advisor_id": advisor_id,
                "should_fire": False,
                "reason": f"{elapsed}d since last run, next in {days - elapsed}d",
            }
    except Exception as e:
        return {"advisor_id": advisor_id, "should_fire": True, "reason": f"parse error on last_run_at: {e}"}


def main():
    machine_only = "--json" in sys.argv

    if not os.path.exists(SCHEDULE_INDEX):
        if not machine_only:
            print(f"schedule-index.json not found at {SCHEDULE_INDEX}", file=sys.stderr)
        print("[]")
        sys.exit(0)

    index = json.load(open(SCHEDULE_INDEX))
    state = load_spoke_state()
    now = datetime.datetime.now(datetime.timezone.utc)

    results = [eval_advisor(entry, now, state) for entry in index]

    if machine_only:
        print(json.dumps(results))
        return

    ready = [r for r in results if r["should_fire"]]
    not_ready = [r for r in results if not r["should_fire"]]

    if ready:
        print(f"Advisors ready to fire ({len(ready)}):")
        for r in ready:
            print(f"  {r['advisor_id']:20} {r['reason']}")
    else:
        print("No advisors scheduled to fire this session.")

    if not_ready and "--verbose" in sys.argv:
        print(f"\nNot scheduled ({len(not_ready)}):")
        for r in not_ready:
            print(f"  {r['advisor_id']:20} {r['reason']}")

    # Always write machine-readable to stdout for hook consumption
    if not machine_only:
        print(f"\n{json.dumps(results)}")


if __name__ == "__main__":
    main()

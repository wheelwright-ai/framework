#!/usr/bin/env python3
"""Generate WAI-Spoke/wakeup-brief.json.

Run before launching an AI tool to guarantee the wakeup fast path.
The wakeup protocol (wai.md Step 7) checks git_sha_at_generation against
HEAD — if they match, it skips all tool calls and displays the brief in seconds.

Usage:
    python3 tools/generate_wakeup_brief.py
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
# Default to CWD if it's a WAI spoke
if (Path.cwd() / "WAI-Spoke").exists():
    SPOKE = Path.cwd() / "WAI-Spoke"
else:
    SPOKE = PROJECT_DIR / "WAI-Spoke"

BYTYPE = SPOKE / "lugs" / "bytype"
STATE_FILE = SPOKE / "WAI-State.json"
BRIEF_FILE = SPOKE / "wakeup-brief.json"


def count_open_lugs() -> int:
    total = 0
    if not BYTYPE.exists():
        return 0
    for type_dir in BYTYPE.iterdir():
        if not type_dir.is_dir():
            continue
        for status in ("open", "in_progress"):
            status_dir = type_dir / status
            try:
                total += len(list(status_dir.glob("*.json")))
            except (FileNotFoundError, PermissionError):
                pass
    return total


def run_score_backlog() -> tuple[dict, list]:
    """Run score_backlog.py --update-state, then read updated _work_queue from state."""
    score_script = PROJECT_DIR / "tools" / "score_backlog.py"
    if not score_script.exists():
        return {"ready_count": 0, "needs_refinement_count": 0, "blocked_count": 0}, []

    subprocess.run(
        [sys.executable, str(score_script), "--update-state"],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        timeout=30,
    )

    # Reload state to get updated _work_queue
    try:
        state = json.loads(STATE_FILE.read_text())
        wq = state.get("_work_queue", {})
        queue_snapshot = wq.get(
            "queue_state",
            {"ready_count": 0, "needs_refinement_count": 0, "blocked_count": 0},
        )
        top_lugs = [
            {k: item[k] for k in ("id", "title", "roi") if k in item}
            for item in wq.get("items", [])[:5]
            if item.get("readiness") == "ready"
        ]
        return queue_snapshot, top_lugs
    except Exception:
        return {"ready_count": 0, "needs_refinement_count": 0, "blocked_count": 0}, []


def count_teachings_pending(hub_path: str) -> int:
    if not hub_path:
        return 0
    teach_dir = Path(hub_path).expanduser() / "teachings_repo" / "framework" / "current"
    processed_dir = SPOKE / "seed" / "ingest" / "processed"
    if not teach_dir.exists():
        return 0
    count = 0
    for f in teach_dir.glob("*.teaching"):
        if not (processed_dir / f.name).exists():
            count += 1
    return count


def count_hub_signals(hub_path: str) -> int:
    if not hub_path:
        return 0
    sig_dir = Path(hub_path).expanduser() / "WAI-Hub" / "signals" / "incoming" / "framework"
    if not sig_dir.exists():
        return 0
    return len([f for f in sig_dir.glob("*.json") if f.name != ".gitkeep"])


def get_git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(PROJECT_DIR),
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return ""


def main() -> None:
    if not STATE_FILE.exists():
        print("ERROR: WAI-State.json not found — not a WAI project", file=sys.stderr)
        sys.exit(1)

    state = json.loads(STATE_FILE.read_text())
    hub_path = state.get("wheel", {}).get("hub_path", "")
    spoke_version = state.get("wheel", {}).get("version", "unknown")
    last_session_id = state.get("_session_state", {}).get("last_session_id", "unknown")
    next_rec = state.get("_session_state", {}).get(
        "next_session_recommendation", "None"
    )

    open_lug_count = count_open_lugs()
    queue_snapshot, top_ready_lugs = run_score_backlog()
    teachings_pending = count_teachings_pending(hub_path)
    hub_signals_pending = count_hub_signals(hub_path)
    git_sha = get_git_sha()

    brief = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "session_id": last_session_id,
        "generation_mode": "standard",
        "chain_target_lug": None,
        "open_lug_count": open_lug_count,
        "queue_snapshot": queue_snapshot,
        "top_ready_lugs": top_ready_lugs,
        "teachings_pending": teachings_pending,
        "hub_signals_pending": hub_signals_pending,
        "next_actions": [next_rec],
        "spoke_version": spoke_version,
        "git_sha_at_generation": git_sha,
    }

    # Atomic write
    tmp = BRIEF_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(brief, indent=2) + "\n")
    os.replace(tmp, BRIEF_FILE)

    sha8 = git_sha[:8] if git_sha else "unknown"
    print(
        f"wakeup-brief.json updated | SHA {sha8} | "
        f"{open_lug_count} lugs | queue {queue_snapshot.get('ready_count', 0)} ready"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

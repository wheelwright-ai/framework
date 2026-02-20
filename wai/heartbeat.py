"""
Heartbeat Log System - Track teach/learn activity per spoke.

Logs all teach/learn operations with timestamps, session IDs, and errors.
Enables detection of failed operations on subsequent wakeup.

Usage:
    from wai.heartbeat import log_heartbeat, get_recent_errors

    # Log a learn action
    log_heartbeat(spoke_path, "learn", {"processed": 3, "failed": 0})

    # Check for recent errors
    errors = get_recent_errors(spoke_path, last_n=5)
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_session_id() -> str:
    """Get current session ID from environment or generate one."""
    return os.environ.get("WAI_SESSION_ID", f"session-{datetime.now().strftime('%Y%m%d%H%M%S')}")


def get_heartbeat_path(spoke_path: Path) -> Path:
    """Get path to heartbeat log file."""
    return spoke_path / "WAI-Spoke" / "logs" / "heartbeat.jsonl"


def log_heartbeat(
    spoke_path: Path,
    action: str,
    results: Dict[str, Any],
    session_id: Optional[str] = None
) -> bool:
    """
    Log a heartbeat entry for teach/learn action.

    Args:
        spoke_path: Path to project root
        action: Action type - "learn" or "teach"
        results: Results dict from process_inbox or distribute_outbox
        session_id: Optional session ID (auto-generated if not provided)

    Returns:
        True if logged successfully, False otherwise
    """
    heartbeat_path = get_heartbeat_path(spoke_path)
    heartbeat_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": now_iso(),
        "session_id": session_id or get_session_id(),
        "action": action,
        "items_processed": results.get("processed", results.get("distributed", 0)),
        "items_failed": results.get("failed", 0),
        "details": results.get("details", []),
        "spokes_reached": results.get("spokes_reached", []),
        "errors": results.get("errors", [])
    }

    try:
        with open(heartbeat_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return True
    except IOError:
        return False


def get_heartbeat_entries(
    spoke_path: Path,
    last_n: int = 10,
    action_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get recent heartbeat entries.

    Args:
        spoke_path: Path to project root
        last_n: Number of recent entries to return
        action_filter: Optional filter by action type ("learn" or "teach")

    Returns:
        List of heartbeat entry dicts (newest first)
    """
    heartbeat_path = get_heartbeat_path(spoke_path)

    if not heartbeat_path.exists():
        return []

    entries = []
    try:
        with open(heartbeat_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        entry = json.loads(line)
                        if action_filter is None or entry.get("action") == action_filter:
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue
    except IOError:
        return []

    # Return newest first
    entries.reverse()
    return entries[:last_n]


def get_recent_errors(
    spoke_path: Path,
    last_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Get recent heartbeat entries that have errors.

    Args:
        spoke_path: Path to project root
        last_n: Number of recent error entries to return

    Returns:
        List of error entries with timestamp and error messages
    """
    heartbeat_path = get_heartbeat_path(spoke_path)

    if not heartbeat_path.exists():
        return []

    error_entries = []
    try:
        with open(heartbeat_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        entry = json.loads(line)
                        errors = entry.get("errors", [])
                        failed = entry.get("items_failed", 0)

                        if errors or failed > 0:
                            for error in errors:
                                error_entries.append({
                                    "timestamp": entry.get("timestamp"),
                                    "action": entry.get("action"),
                                    "session_id": entry.get("session_id"),
                                    "error": error
                                })

                            # Also report generic failures
                            if failed > 0 and not errors:
                                error_entries.append({
                                    "timestamp": entry.get("timestamp"),
                                    "action": entry.get("action"),
                                    "session_id": entry.get("session_id"),
                                    "error": f"{failed} item(s) failed to process"
                                })
                    except json.JSONDecodeError:
                        continue
    except IOError:
        return []

    # Return newest first
    error_entries.reverse()
    return error_entries[:last_n]


def get_heartbeat_summary(spoke_path: Path, days: int = 7) -> Dict[str, Any]:
    """
    Get summary statistics from heartbeat log.

    Args:
        spoke_path: Path to project root
        days: Number of days to include in summary

    Returns:
        Dict with summary statistics
    """
    heartbeat_path = get_heartbeat_path(spoke_path)

    if not heartbeat_path.exists():
        return {
            "total_entries": 0,
            "learn_count": 0,
            "teach_count": 0,
            "total_processed": 0,
            "total_failed": 0,
            "error_count": 0,
            "last_activity": None
        }

    summary = {
        "total_entries": 0,
        "learn_count": 0,
        "teach_count": 0,
        "total_processed": 0,
        "total_failed": 0,
        "error_count": 0,
        "last_activity": None,
        "spokes_reached": set()
    }

    cutoff = datetime.now(timezone.utc)
    try:
        from datetime import timedelta
        cutoff = cutoff - timedelta(days=days)
    except ImportError:
        pass

    try:
        with open(heartbeat_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        entry = json.loads(line)

                        # Check if within time window
                        ts = entry.get("timestamp", "")
                        try:
                            entry_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            if entry_dt < cutoff:
                                continue
                        except (ValueError, TypeError):
                            pass

                        summary["total_entries"] += 1

                        action = entry.get("action")
                        if action == "learn":
                            summary["learn_count"] += 1
                        elif action == "teach":
                            summary["teach_count"] += 1

                        summary["total_processed"] += entry.get("items_processed", 0)
                        summary["total_failed"] += entry.get("items_failed", 0)
                        summary["error_count"] += len(entry.get("errors", []))

                        for spoke in entry.get("spokes_reached", []):
                            summary["spokes_reached"].add(spoke)

                        # Track most recent activity
                        if ts and (not summary["last_activity"] or ts > summary["last_activity"]):
                            summary["last_activity"] = ts

                    except json.JSONDecodeError:
                        continue
    except IOError:
        pass

    # Convert set to list for JSON serialization
    summary["spokes_reached"] = list(summary["spokes_reached"])

    return summary


def clear_heartbeat_log(spoke_path: Path, keep_last_n: int = 100) -> bool:
    """
    Trim heartbeat log to keep only recent entries.

    Args:
        spoke_path: Path to project root
        keep_last_n: Number of entries to keep

    Returns:
        True if successful, False otherwise
    """
    heartbeat_path = get_heartbeat_path(spoke_path)

    if not heartbeat_path.exists():
        return True

    entries = []
    try:
        with open(heartbeat_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(line)
    except IOError:
        return False

    # Keep only last N entries
    entries_to_keep = entries[-keep_last_n:] if len(entries) > keep_last_n else entries

    try:
        with open(heartbeat_path, "w", encoding="utf-8") as f:
            f.writelines(entries_to_keep)
        return True
    except IOError:
        return False


__all__ = [
    "log_heartbeat",
    "get_heartbeat_entries",
    "get_recent_errors",
    "get_heartbeat_summary",
    "clear_heartbeat_log",
]

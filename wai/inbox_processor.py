"""
Inbox Processor - Auto-learn system for WAI lugs.

Processes incoming lugs from WAI-Spoke/lugs/inbox/ on wakeup.
Handles task, signal, and phone-home lug types with graceful error handling.

Usage:
    from wai.inbox_processor import process_inbox

    result = process_inbox(Path('/path/to/project'))
    print(f"Processed {result['processed']} items, {result['failed']} failed")
"""

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def scan_inbox(inbox_path: Path) -> List[Dict[str, Any]]:
    """
    Scan inbox directory for pending lugs.

    Args:
        inbox_path: Path to WAI-Spoke/lugs/inbox/

    Returns:
        List of lug dicts with their file paths
    """
    lugs = []

    if not inbox_path.exists():
        return lugs

    for lug_file in inbox_path.glob("*.jsonl"):
        try:
            content = lug_file.read_text(encoding="utf-8").strip()
            if not content:
                continue

            lug_data = json.loads(content)
            lug_data["_file_path"] = str(lug_file)
            lugs.append(lug_data)

        except (json.JSONDecodeError, IOError) as e:
            # Log error but continue processing other lugs
            print(f"Warning: Could not read lug file {lug_file}: {e}")
            continue

    return lugs


def process_inbox(spoke_path: Path) -> Dict[str, Any]:
    """
    Process all pending lugs in spoke's inbox.

    Routes lugs by their 'category' or 'ty' field:
    - task: Add to WAI-Lugs.jsonl
    - signal: Add to signals collection
    - phone-home: Generate status report response

    Args:
        spoke_path: Path to project root (where WAI-Spoke/ lives)

    Returns:
        Dict with processing results:
        {
            'processed': int,
            'failed': int,
            'details': List[Dict],  # Per-lug results
            'errors': List[str]     # Error messages
        }
    """
    inbox_path = spoke_path / "WAI-Spoke" / "lugs" / "inbox"
    result = {
        "processed": 0,
        "failed": 0,
        "details": [],
        "errors": []
    }

    if not inbox_path.exists():
        return result

    lugs = scan_inbox(inbox_path)

    for lug in lugs:
        lug_id = lug.get("id", "unknown")
        lug_type = lug.get("category") or lug.get("ty", "unknown")
        file_path = Path(lug.get("_file_path", ""))

        try:
            success = False
            response_lug = None

            if lug_type == "task":
                success = process_task_lug(lug, spoke_path)
            elif lug_type == "signal":
                success = process_signal_lug(lug, spoke_path)
            elif lug_type == "phone-home":
                response_lug = process_phone_home_task(lug, spoke_path)
                success = response_lug is not None
            elif lug_type == "phone-home-response":
                # Hub processing a response from a spoke
                success = process_phone_home_response(lug, spoke_path)
            else:
                # Unknown type - mark as processed anyway to avoid blocking
                success = True

            if success:
                mark_processed(file_path, spoke_path)
                result["processed"] += 1
                result["details"].append({
                    "lug_id": lug_id,
                    "type": lug_type,
                    "status": "processed",
                    "response_lug": response_lug is not None
                })
            else:
                result["failed"] += 1
                result["details"].append({
                    "lug_id": lug_id,
                    "type": lug_type,
                    "status": "failed"
                })

        except Exception as e:
            result["failed"] += 1
            error_msg = f"Error processing {lug_id}: {str(e)}"
            result["errors"].append(error_msg)
            result["details"].append({
                "lug_id": lug_id,
                "type": lug_type,
                "status": "error",
                "error": str(e)
            })

    # Log heartbeat for this learn action
    try:
        from .heartbeat import log_heartbeat
        log_heartbeat(spoke_path, "learn", result)
    except ImportError:
        pass  # Heartbeat module not yet available

    return result


def process_task_lug(lug: Dict[str, Any], spoke_path: Path) -> bool:
    """
    Process a task lug by adding it to WAI-Lugs.jsonl.

    Args:
        lug: The task lug dict
        spoke_path: Path to project root

    Returns:
        True if successful, False otherwise
    """
    lugs_file = spoke_path / "WAI-Spoke" / "WAI-Lugs.jsonl"

    # Convert inbox task to WAI-Lugs format
    task_entry = {
        "i": lug.get("id"),
        "t": lug.get("content", {}).get("description", lug.get("id")),
        "ty": "task",
        "s": "o",  # Open status
        "ca": lug.get("created_at", now_iso()),
        "ua": now_iso(),
        "origin": f"inbox:{lug.get('source_wheel_id', 'unknown')}",
        "ex": {
            "inbox_lug": lug.get("id"),
            "source_wheel": lug.get("source_wheel_id"),
            "action": lug.get("content", {}).get("action")
        }
    }

    # Append to lugs file
    try:
        lugs_file.parent.mkdir(parents=True, exist_ok=True)
        with open(lugs_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(task_entry) + "\n")
        return True
    except IOError:
        return False


def process_signal_lug(lug: Dict[str, Any], spoke_path: Path) -> bool:
    """
    Process a signal lug by adding it to WAI-Signals.jsonl.

    Args:
        lug: The signal lug dict
        spoke_path: Path to project root

    Returns:
        True if successful, False otherwise
    """
    signals_file = spoke_path / "WAI-Spoke" / "WAI-Signals.jsonl"

    # Convert to signals format
    signal_entry = {
        "id": lug.get("id"),
        "type": "signal",
        "signal": lug.get("content", {}).get("signal", ""),
        "context": lug.get("content", {}).get("context", ""),
        "impact": lug.get("content", {}).get("impact", 5),
        "source_wheel_id": lug.get("source_wheel_id"),
        "received_at": now_iso(),
        "status": "received"
    }

    try:
        signals_file.parent.mkdir(parents=True, exist_ok=True)
        with open(signals_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(signal_entry) + "\n")
        return True
    except IOError:
        return False


def process_phone_home_task(lug: Dict[str, Any], spoke_path: Path) -> Optional[Dict[str, Any]]:
    """
    Process a phone-home task by generating a status report.

    Creates a response lug in the spoke's outbox destined for the hub.

    Args:
        lug: The phone-home task lug
        spoke_path: Path to project root

    Returns:
        Response lug dict if successful, None otherwise
    """
    # Check version trigger if present
    trigger = lug.get("content", {}).get("trigger_condition", {})
    if trigger.get("type") == "version_match":
        required_version = trigger.get("framework_version_gte", "0.0.0")
        current_version = get_framework_version(spoke_path)
        if not version_gte(current_version, required_version):
            # Version doesn't match trigger - skip silently
            return None

    # Generate status report
    status_report = generate_status_report(spoke_path)

    if not status_report:
        return None

    # Create response lug
    response_lug = {
        "id": f"phone-home-response-{lug.get('id', 'unknown')}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "ty": "phone-home-response",
        "source_wheel_id": status_report.get("wheel_id"),
        "destination_wheel_id": "hub",
        "created_at": now_iso(),
        "status": "pending",
        "in_response_to": lug.get("id"),
        "content": status_report
    }

    # Write to outbox
    outbox_path = spoke_path / "WAI-Spoke" / "lugs" / "outbox"
    outbox_path.mkdir(parents=True, exist_ok=True)

    response_file = outbox_path / f"{response_lug['id']}.jsonl"
    try:
        response_file.write_text(json.dumps(response_lug, indent=2), encoding="utf-8")
        return response_lug
    except IOError:
        return None


def process_phone_home_response(lug: Dict[str, Any], hub_path: Path) -> bool:
    """
    Process a phone-home response by updating hub-registry.json.

    This runs on the hub when receiving responses from spokes.

    Args:
        lug: The phone-home response lug
        hub_path: Path to hub root

    Returns:
        True if successful, False otherwise
    """
    registry_path = hub_path / "hub-registry.json"

    if not registry_path.exists():
        return False

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return False

    # Find the spoke in registry
    # The source_wheel_id might be the wheel name from WAI-State.json (e.g., "Wheelwright")
    # but the registry uses wheel_id (e.g., "framework")
    # Try to extract the spoke ID from the in_response_to field which has the original task ID
    spoke_wheel_id = lug.get("source_wheel_id")
    status_content = lug.get("content", {})

    # Also try to get the wheel_id from the original task ID
    # Format: task-phone-home-v3.1.0-{wheel_id}-{timestamp}
    in_response_to = lug.get("in_response_to", "")
    if in_response_to and "phone-home" in in_response_to:
        parts = in_response_to.split("-")
        # Find wheel_id: it's between "v{version}" and the timestamp
        try:
            version_idx = next(i for i, p in enumerate(parts) if p.startswith("v") and "." in p)
            # wheel_id is from version_idx+1 to second-to-last (timestamp is last)
            if len(parts) > version_idx + 2:
                registry_wheel_id = "-".join(parts[version_idx + 1:-1])
                # Try this first
                for wheel in registry.get("wheels", []):
                    if wheel.get("wheel_id") == registry_wheel_id:
                        spoke_wheel_id = registry_wheel_id
                        break
        except (StopIteration, ValueError):
            pass

    for wheel in registry.get("wheels", []):
        if wheel.get("wheel_id") == spoke_wheel_id:
            # Update with phone-home data
            wheel["last_phone_home"] = now_iso()
            wheel["phone_home_report"] = {
                "framework_version": status_content.get("framework_version"),
                "session_count": status_content.get("session_count"),
                "last_closeout": status_content.get("last_closeout"),
                "git_branch": status_content.get("git_status", {}).get("branch"),
                "uncommitted_files": status_content.get("git_status", {}).get("uncommitted_count", 0),
                "lugs_count": status_content.get("lugs_count"),
                "signals_generated": status_content.get("signals_generated"),
                "received_at": now_iso()
            }

            # Update statistics
            if "statistics" in registry:
                registry["statistics"]["last_phone_home_received"] = now_iso()

            break

    # Save updated registry
    try:
        registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
        return True
    except IOError:
        return False


def mark_processed(lug_path: Path, spoke_path: Path) -> bool:
    """
    Move processed lug to inbox/processed/ directory.

    Args:
        lug_path: Path to the lug file
        spoke_path: Path to project root

    Returns:
        True if successful, False otherwise
    """
    if not lug_path.exists():
        return False

    processed_dir = spoke_path / "WAI-Spoke" / "lugs" / "inbox" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    dest_path = processed_dir / lug_path.name

    try:
        shutil.move(str(lug_path), str(dest_path))
        return True
    except (IOError, shutil.Error):
        return False


def generate_status_report(spoke_path: Path) -> Optional[Dict[str, Any]]:
    """
    Generate a status report for phone-home response.

    Args:
        spoke_path: Path to project root

    Returns:
        Status report dict or None on error
    """
    state_file = spoke_path / "WAI-Spoke" / "WAI-State.json"

    if not state_file.exists():
        return None

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return None

    # Get git status
    git_status = get_git_status(spoke_path)

    # Count lugs
    lugs_count = 0
    lugs_file = spoke_path / "WAI-Spoke" / "WAI-Lugs.jsonl"
    if lugs_file.exists():
        lugs_count = sum(1 for line in lugs_file.read_text().splitlines() if line.strip())

    # Count signals
    signals_count = 0
    signals_file = spoke_path / "WAI-Spoke" / "WAI-Signals.jsonl"
    if signals_file.exists():
        signals_count = sum(1 for line in signals_file.read_text().splitlines() if line.strip())

    # Get framework version
    framework_version = get_framework_version(spoke_path)

    report = {
        "wheel_id": state.get("wheel", {}).get("name") or state.get("wheel", {}).get("abbrev"),
        "spoke_id": state.get("wheel", {}).get("spoke_id"),
        "framework_version": framework_version,
        "git_status": git_status,
        "session_count": state.get("_session_state", {}).get("session_count", 0),
        "last_closeout": state.get("_session_state", {}).get("last_closeout"),
        "lugs_count": lugs_count,
        "signals_generated": signals_count,
        "adoption_status": get_adoption_status(spoke_path),
        "reported_at": now_iso()
    }

    return report


def get_git_status(spoke_path: Path) -> Dict[str, Any]:
    """Get git status for status report."""
    try:
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(spoke_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        branch = result.stdout.strip() if result.returncode == 0 else "unknown"

        # Get last commit
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(spoke_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        commit = result.stdout.strip()[:12] if result.returncode == 0 else "unknown"

        # Get uncommitted count
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(spoke_path),
            capture_output=True,
            text=True,
            timeout=5
        )
        uncommitted_count = len([l for l in result.stdout.splitlines() if l.strip()]) if result.returncode == 0 else 0

        return {
            "branch": branch,
            "commit": commit,
            "uncommitted_count": uncommitted_count
        }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {
            "branch": "unknown",
            "commit": "unknown",
            "uncommitted_count": 0
        }


def get_framework_version(spoke_path: Path) -> str:
    """Get framework version from WAI-Guide.md or state."""
    guide_file = spoke_path / "WAI-Spoke" / "WAI-Guide.md"
    if guide_file.exists():
        try:
            content = guide_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                if "version" in line.lower() and ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        version = parts[1].strip()
                        if version and version[0].isdigit():
                            return version
        except IOError:
            pass
    return "unknown"


def get_adoption_status(spoke_path: Path) -> Dict[str, Any]:
    """Get module adoption status for status report."""
    versions_file = spoke_path / "WAI-Spoke" / "WAI-Module-Versions.json"

    if not versions_file.exists():
        return {}

    try:
        versions = json.loads(versions_file.read_text(encoding="utf-8"))
        return {
            "modules_adopted": len(versions.get("adopted_modules", {})),
            "last_adoption": versions.get("last_adoption_at")
        }
    except (json.JSONDecodeError, IOError):
        return {}


def version_gte(current: str, required: str) -> bool:
    """Compare version strings (semver-like)."""
    # Handle unknown/missing versions - assume compatible
    if not current or current == "unknown":
        return True

    try:
        def parse_version(v: str) -> Tuple[int, ...]:
            parts = v.replace("v", "").split(".")
            return tuple(int(p) for p in parts if p.isdigit())

        return parse_version(current) >= parse_version(required)
    except (ValueError, TypeError):
        return True  # Default to True if parsing fails


def distribute_outbox(spoke_path: Path, hub_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Distribute outbox items to target spokes (auto-teach).

    Only runs on framework/hub nodes. Reads hub-registry.json to find
    spoke paths and delivers lugs to their inboxes.

    Args:
        spoke_path: Path to current project root
        hub_path: Path to hub (auto-discovered if not provided)

    Returns:
        Dict with distribution results:
        {
            'distributed': int,
            'failed': int,
            'spokes_reached': List[str],
            'errors': List[str]
        }
    """
    outbox_path = spoke_path / "WAI-Spoke" / "lugs" / "outbox"
    result = {
        "distributed": 0,
        "failed": 0,
        "spokes_reached": [],
        "errors": []
    }

    if not outbox_path.exists():
        return result

    # Find outbox items
    outbox_items = list(outbox_path.glob("*.jsonl"))
    if not outbox_items:
        return result

    # Discover hub if not provided
    if not hub_path:
        try:
            from .hub import HubManager
            hub_manager = HubManager()
            hub_path = hub_manager.auto_discover_hub(spoke_path)
        except ImportError:
            pass

    if not hub_path:
        result["errors"].append("Could not find hub for distribution")
        return result

    # Load hub registry
    registry_path = hub_path / "hub-registry.json"
    if not registry_path.exists():
        result["errors"].append("hub-registry.json not found")
        return result

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        result["errors"].append(f"Could not read hub-registry.json: {e}")
        return result

    # Build spoke lookup
    spokes_by_id = {}
    for wheel in registry.get("wheels", []):
        if wheel.get("status") == "active":
            wheel_id = wheel.get("wheel_id")
            wheel_path = wheel.get("path")
            if wheel_id and wheel_path:
                spokes_by_id[wheel_id] = Path(wheel_path)

    # Create distributed directory
    distributed_dir = outbox_path / "distributed"
    distributed_dir.mkdir(parents=True, exist_ok=True)

    # Process each outbox item
    for lug_file in outbox_items:
        try:
            lug_data = json.loads(lug_file.read_text(encoding="utf-8"))
            dest_wheel_id = lug_data.get("destination_wheel_id")

            if not dest_wheel_id:
                # No destination - skip
                continue

            # Handle "all" destination (broadcast)
            if dest_wheel_id == "all":
                targets = list(spokes_by_id.items())
            elif dest_wheel_id in spokes_by_id:
                targets = [(dest_wheel_id, spokes_by_id[dest_wheel_id])]
            else:
                result["errors"].append(f"Unknown destination: {dest_wheel_id}")
                result["failed"] += 1
                continue

            # Deliver to each target
            delivered = False
            for wheel_id, wheel_path in targets:
                target_inbox = wheel_path / "WAI-Spoke" / "lugs" / "inbox"

                # Skip if target inbox doesn't exist
                if not target_inbox.parent.exists():
                    continue

                target_inbox.mkdir(parents=True, exist_ok=True)
                target_file = target_inbox / lug_file.name

                try:
                    shutil.copy2(str(lug_file), str(target_file))
                    delivered = True
                    if wheel_id not in result["spokes_reached"]:
                        result["spokes_reached"].append(wheel_id)
                except IOError as e:
                    result["errors"].append(f"Could not deliver to {wheel_id}: {e}")

            if delivered:
                # Move to distributed
                shutil.move(str(lug_file), str(distributed_dir / lug_file.name))
                result["distributed"] += 1
            else:
                result["failed"] += 1

        except (json.JSONDecodeError, IOError) as e:
            result["errors"].append(f"Error processing {lug_file.name}: {e}")
            result["failed"] += 1

    # Log heartbeat for this teach action
    try:
        from .heartbeat import log_heartbeat
        log_heartbeat(spoke_path, "teach", result)
    except ImportError:
        pass

    return result


__all__ = [
    "scan_inbox",
    "process_inbox",
    "process_task_lug",
    "process_signal_lug",
    "process_phone_home_task",
    "process_phone_home_response",
    "mark_processed",
    "generate_status_report",
    "distribute_outbox",
]

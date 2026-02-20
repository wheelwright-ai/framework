"""
Phone-Home Task Distributor - Generate and distribute phone-home tasks to all spokes.

Creates phone-home task lugs for each active spoke in hub-registry.json
and places them in hub's outbox for distribution.

Usage:
    python -m wai.phone_home_distributor

    Or programmatically:
    from wai.phone_home_distributor import distribute_phone_home_tasks
    result = distribute_phone_home_tasks()
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_framework_version() -> str:
    """Get current framework version."""
    # Try to read from a version file or default
    framework_path = Path(__file__).parent.parent
    version_file = framework_path / "VERSION"

    if version_file.exists():
        return version_file.read_text().strip()

    # Default version
    return "3.1.0"


def create_phone_home_task(
    spoke_wheel_id: str,
    min_version: str = "3.1.0"
) -> Dict[str, Any]:
    """
    Create a phone-home task lug for a specific spoke.

    Args:
        spoke_wheel_id: Target spoke's wheel_id
        min_version: Minimum framework version required to process

    Returns:
        Phone-home task lug dict
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    framework_version = get_framework_version()

    return {
        "_behavior_directive": {
            "what_this_is": "A REQUEST for inbox_processor.py to generate a status report",
            "what_this_is_NOT": "An instruction for the AI agent to execute or implement",
            "processing_agent": "wai/inbox_processor.py (automatic Python code, not AI)",
            "ai_agent_action": "NONE - processed automatically before your session starts",
            "if_you_see_this_unprocessed": "Check WAI-Spoke/logs/heartbeat.jsonl for errors"
        },
        "id": f"task-phone-home-v{framework_version}-{spoke_wheel_id}-{timestamp}",
        "ty": "phone-home",
        "category": "phone-home",
        "source_wheel_id": "hub",
        "destination_wheel_id": spoke_wheel_id,
        "created_at": now_iso(),
        "status": "pending",
        "content": {
            "request_type": "status_report",
            "description": "Inbox processor reads state files and generates report. NO AI action required.",
            "trigger_condition": {
                "type": "version_match",
                "framework_version_gte": min_version
            },
            "report_fields_to_collect": [
                "wheel_id",
                "spoke_id",
                "framework_version",
                "git_status",
                "session_count",
                "last_closeout",
                "lugs_count",
                "signals_generated",
                "adoption_status"
            ]
        }
    }


def get_active_spokes(hub_path: Path) -> List[Dict[str, Any]]:
    """
    Get list of active spokes from hub-registry.json.

    Args:
        hub_path: Path to hub

    Returns:
        List of active spoke dicts with wheel_id and path
    """
    registry_path = hub_path / "hub-registry.json"

    if not registry_path.exists():
        return []

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return []

    active_spokes = []
    for wheel in registry.get("wheels", []):
        if wheel.get("status") == "active":
            # Skip hub itself
            wheel_id = wheel.get("wheel_id")
            if wheel_id and wheel_id != "hub":
                active_spokes.append({
                    "wheel_id": wheel_id,
                    "path": wheel.get("path"),
                    "taught_version": wheel.get("taught_version")
                })

    return active_spokes


def distribute_phone_home_tasks(
    hub_path: Optional[Path] = None,
    min_version: str = "3.1.0",
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Generate and distribute phone-home tasks to all active spokes.

    Args:
        hub_path: Path to hub (auto-discovered if not provided)
        min_version: Minimum framework version required
        dry_run: If True, don't actually create files

    Returns:
        Dict with results:
        {
            'tasks_created': int,
            'spokes': List[str],
            'errors': List[str]
        }
    """
    result = {
        "tasks_created": 0,
        "spokes": [],
        "errors": []
    }

    # Find hub
    if not hub_path:
        from .hub import HubManager
        hub_manager = HubManager()
        hub_path = hub_manager.auto_discover_hub(Path.cwd())

    if not hub_path:
        result["errors"].append("Could not find hub")
        return result

    # Get active spokes
    spokes = get_active_spokes(hub_path)

    if not spokes:
        result["errors"].append("No active spokes found in hub registry")
        return result

    # Create outbox directory
    outbox = hub_path / "WAI-Spoke" / "lugs" / "outbox"
    if not dry_run:
        outbox.mkdir(parents=True, exist_ok=True)

    # Generate tasks for each spoke
    for spoke in spokes:
        wheel_id = spoke["wheel_id"]

        try:
            task = create_phone_home_task(wheel_id, min_version)

            if not dry_run:
                task_file = outbox / f"{task['id']}.jsonl"
                task_file.write_text(json.dumps(task, indent=2), encoding="utf-8")

            result["tasks_created"] += 1
            result["spokes"].append(wheel_id)

        except Exception as e:
            result["errors"].append(f"Error creating task for {wheel_id}: {e}")

    return result


def main():
    """CLI entry point for phone-home distribution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Distribute phone-home tasks to all active spokes"
    )
    parser.add_argument(
        "--hub-path",
        type=Path,
        help="Path to hub (auto-discovered if not provided)"
    )
    parser.add_argument(
        "--min-version",
        default="3.1.0",
        help="Minimum framework version required (default: 3.1.0)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without creating files"
    )

    args = parser.parse_args()

    print("Phone-Home Task Distribution")
    print("=" * 40)

    if args.dry_run:
        print("DRY RUN - no files will be created\n")

    result = distribute_phone_home_tasks(
        hub_path=args.hub_path,
        min_version=args.min_version,
        dry_run=args.dry_run
    )

    if result["errors"]:
        print("Errors:")
        for error in result["errors"]:
            print(f"  - {error}")
        print()

    print(f"Tasks created: {result['tasks_created']}")
    print(f"Spokes targeted: {len(result['spokes'])}")

    if result["spokes"]:
        print("\nSpokes:")
        for spoke in result["spokes"]:
            print(f"  - {spoke}")

    if not args.dry_run and result["tasks_created"] > 0:
        print("\nTasks placed in hub outbox.")
        print("Run closeout or /wai-teach to distribute to spoke inboxes.")


if __name__ == "__main__":
    main()

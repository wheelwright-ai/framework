"""
Lug Directory Scaffolding - Ensure inbox/outbox structure exists for all spokes.

Creates WAI-Spoke/lugs/inbox and WAI-Spoke/lugs/outbox directories for all
active spokes in the hub registry.

Per specification from lug-exec-scaffold-lug-dirs-v1:
- Read hub registry for active spokes
- Create inbox/ and outbox/ directories
- Add README.md and .gitkeep files
- Log results for verification

Usage:
    python -m wai.scaffold

    Or programmatically:
    from wai.scaffold import ensure_lug_directories
    result = ensure_lug_directories(hub_path)
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List


README_CONTENT = """# Lugs Directory Structure

## Purpose

This directory contains Wheelwright lugs for cross-spoke communication:

- **inbox/** - Incoming lugs from other wheels (hub, other spokes)
- **outbox/** - Outgoing lugs to be picked up by other wheels
- **{session-id}.jsonl** - Active session lugs

## Processing

- Inbox files are auto-processed on wakeup via `/wai-learn`
- Outbox files are distributed via automatic closeout delivery
- Session lugs are archived to `../lugs-closed.jsonl` on closeout

## File Format

All lugs use JSONL (JSON Lines) format:
- One lug per line
- Each line is valid JSON
- Minified keys for storage efficiency

## Do Not

- Do NOT manually edit these files
- Do NOT delete inbox files (auto-archived after processing)
- Do NOT move files between directories

See WAI-Guide.md for full protocol documentation.
"""


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_lug_directories(hub_path: Path) -> Dict[str, Any]:
    """
    Create lugs/inbox and lugs/outbox directory structure for all active spokes.

    Per specification from lug-exec-scaffold-lug-dirs-v1.

    Args:
        hub_path: Path to hub directory

    Returns:
        Dict with results:
        {
            'spokes_processed': int,
            'spokes_skipped': int,
            'directories_created': int,
            'errors': List[str],
            'summary': Dict[str, Any]
        }
    """
    result = {
        "timestamp": now_iso(),
        "operation": "scaffold_lug_directories",
        "spokes_processed": 0,
        "spokes_skipped": 0,
        "directories_created": 0,
        "errors": [],
        "summary": {}
    }

    # Step 1: Load hub registry
    registry_path = hub_path / "hub-registry.json"
    if not registry_path.exists():
        result["errors"].append(f"Hub registry not found at {registry_path}")
        return result

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        result["errors"].append(f"Failed to read hub registry: {e}")
        return result

    wheels = registry.get("wheels", [])
    if not wheels:
        result["errors"].append("No wheels found in hub registry")
        return result

    # Step 2: Process each active spoke
    for wheel in wheels:
        if wheel.get("status") != "active":
            continue

        wheel_id = wheel.get("wheel_id")
        spoke_path_str = wheel.get("path")

        if not wheel_id or not spoke_path_str:
            result["spokes_skipped"] += 1
            result["errors"].append(f"Wheel missing wheel_id or path: {wheel}")
            continue

        spoke_path = Path(spoke_path_str)

        # Initialize summary for this spoke
        spoke_summary = {
            "path": str(spoke_path),
            "inbox_created": False,
            "outbox_created": False,
            "status": "unknown",
            "error_message": None
        }

        # Step 2: Validate spoke paths
        if not spoke_path.exists():
            spoke_summary["status"] = "skipped"
            spoke_summary["error_message"] = "Spoke directory does not exist"
            result["spokes_skipped"] += 1
            result["summary"][wheel_id] = spoke_summary
            continue

        wai_spoke_path = spoke_path / "WAI-Spoke"
        if not wai_spoke_path.exists():
            spoke_summary["status"] = "skipped"
            spoke_summary["error_message"] = "WAI-Spoke directory missing - spoke not initialized"
            result["spokes_skipped"] += 1
            result["summary"][wheel_id] = spoke_summary
            continue

        # Step 3: Create directories
        try:
            lugs_dir = wai_spoke_path / "lugs"
            inbox_dir = lugs_dir / "inbox"
            outbox_dir = lugs_dir / "outbox"

            # Create lugs parent directory
            if not lugs_dir.exists():
                lugs_dir.mkdir(mode=0o755, parents=True, exist_ok=True)
                result["directories_created"] += 1

            # Create inbox
            if not inbox_dir.exists():
                inbox_dir.mkdir(mode=0o755, parents=True, exist_ok=True)
                spoke_summary["inbox_created"] = True
                result["directories_created"] += 1
            else:
                spoke_summary["inbox_created"] = "already_existed"

            # Create outbox
            if not outbox_dir.exists():
                outbox_dir.mkdir(mode=0o755, parents=True, exist_ok=True)
                spoke_summary["outbox_created"] = True
                result["directories_created"] += 1
            else:
                spoke_summary["outbox_created"] = "already_existed"

            # Step 4: Create README
            readme_path = lugs_dir / "README.md"
            if not readme_path.exists():
                readme_path.write_text(README_CONTENT, encoding="utf-8")
                readme_path.chmod(0o644)

            # Step 5: Create .gitkeep files
            inbox_gitkeep = inbox_dir / ".gitkeep"
            if not inbox_gitkeep.exists():
                inbox_gitkeep.write_text("", encoding="utf-8")
                inbox_gitkeep.chmod(0o644)

            outbox_gitkeep = outbox_dir / ".gitkeep"
            if not outbox_gitkeep.exists():
                outbox_gitkeep.write_text("", encoding="utf-8")
                outbox_gitkeep.chmod(0o644)

            spoke_summary["status"] = "success"
            result["spokes_processed"] += 1

        except PermissionError as e:
            spoke_summary["status"] = "error"
            spoke_summary["error_message"] = f"Permission denied: {e}"
            result["errors"].append(f"{wheel_id}: Permission denied - {e}")
            result["spokes_skipped"] += 1
        except Exception as e:
            spoke_summary["status"] = "error"
            spoke_summary["error_message"] = str(e)
            result["errors"].append(f"{wheel_id}: {e}")
            result["spokes_skipped"] += 1

        result["summary"][wheel_id] = spoke_summary

    return result


def main():
    """CLI entry point for lug directory scaffolding."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create lugs/inbox and lugs/outbox directories for all active spokes"
    )
    parser.add_argument(
        "--hub-path",
        type=Path,
        help="Path to hub (auto-discovered if not provided)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to write JSON log (optional)"
    )

    args = parser.parse_args()

    # Find hub
    hub_path = args.hub_path
    if not hub_path:
        # Try to auto-discover hub
        from .hub import HubManager
        hub_manager = HubManager()
        hub_path = hub_manager.auto_discover_hub(Path.cwd())

    if not hub_path:
        print("Error: Could not find hub. Specify --hub-path")
        return 1

    print("Lug Directory Scaffolding")
    print("=" * 60)
    print(f"Hub: {hub_path}")
    print()

    result = ensure_lug_directories(hub_path)

    # Step 6: Display results
    print(f"Spokes processed: {result['spokes_processed']}")
    print(f"Spokes skipped: {result['spokes_skipped']}")
    print(f"Directories created: {result['directories_created']}")
    print()

    if result["errors"]:
        print("Errors:")
        for error in result["errors"]:
            print(f"  - {error}")
        print()

    if result["summary"]:
        print("Summary by spoke:")
        for wheel_id, summary in result["summary"].items():
            status_icon = "✓" if summary["status"] == "success" else "✗"
            print(f"  {status_icon} {wheel_id}")
            print(f"      Path: {summary['path']}")
            print(f"      Inbox: {summary['inbox_created']}")
            print(f"      Outbox: {summary['outbox_created']}")
            print(f"      Status: {summary['status']}")
            if summary.get("error_message"):
                print(f"      Error: {summary['error_message']}")

    # Step 6: Write log file if requested
    if args.output:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        log_file = args.output if args.output.is_dir() else args.output.parent / f"scaffold-{timestamp}.json"
        log_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"\nLog written to: {log_file}")

    return 0 if result["spokes_processed"] > 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

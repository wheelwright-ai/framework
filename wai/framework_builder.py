"""
Framework Builder - Generate upgrade-adoption-plan.json for distribution.

Implements lug-exec-framework-builder-v1 specification.

Builds comprehensive upgrade adoption plan from framework templates,
signs with hub fingerprint, and creates distribution lug.

Usage:
    python -m wai.framework_builder

    Or programmatically:
    from wai.framework_builder import build_and_save
    result = build_and_save()
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from .upgrade_adoption import UpgradeAdoptionPlanBuilder, save_upgrade_plan


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_framework_version() -> str:
    """Get current framework version from VERSION file."""
    framework_path = Path(__file__).parent.parent
    version_file = framework_path / "VERSION"

    if version_file.exists():
        return version_file.read_text().strip()

    # Default version per specification
    return "3.1.0"


def get_hub_fingerprint(hub_path: Path) -> str:
    """Get hub fingerprint from hub-profile.json."""
    profile_path = hub_path / "WAI-Spoke" / "hub-profile.json"

    if not profile_path.exists():
        return None

    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        return profile.get("hub_fingerprint")
    except (json.JSONDecodeError, IOError):
        return None


def build_and_save(
    framework_path: Path = None,
    hub_path: Path = None
) -> Dict[str, Any]:
    """
    Build framework and generate upgrade adoption plan.

    Implements lug-exec-framework-builder-v1 specification exactly.

    Args:
        framework_path: Path to framework (defaults to parent of this file)
        hub_path: Path to hub (for signing)

    Returns:
        Dict with results:
        {
            'success': bool,
            'plan_path': Path,
            'lug_path': Path,
            'errors': List[str]
        }
    """
    result = {
        "success": False,
        "plan_path": None,
        "lug_path": None,
        "errors": []
    }

    # Step 1: Prerequisites - Verify required paths exist
    if not framework_path:
        framework_path = Path(__file__).parent.parent

    templates_path = framework_path / "templates" / "WAI-Spoke"
    if not templates_path.exists():
        result["errors"].append(f"Template source not found at {templates_path}")
        return result

    # Get hub fingerprint if hub path provided
    hub_fingerprint = None
    if hub_path and hub_path.exists():
        hub_fingerprint = get_hub_fingerprint(hub_path)
        if not hub_fingerprint:
            result["errors"].append("Hub fingerprint not found - will skip signing")

    # Step 2: Initialize builder
    framework_version = get_framework_version()

    builder = UpgradeAdoptionPlanBuilder(
        framework_version=framework_version,
        spoke_structure_version="3.0"
    )

    # Step 3: Add spoke template files
    # Per specification - exact file list with metadata
    spoke_files = [
        {
            "name": "WAI-Guide.md",
            "template_path": "templates/WAI-Spoke/WAI-Guide.md",
            "target_path": "WAI-Spoke/WAI-Guide.md",
            "version": "3.1.0",
            "changed_from": "3.0.0",
            "why_changed": "Enhanced session start protocol with auto-teach/learn support",
            "safe_to_auto_adopt": True,
            "requires_review": False,
            "applies_to": ["spoke", "hub"]
        },
        {
            "name": "WAI-State.json",
            "template_path": "templates/WAI-Spoke/WAI-State.json",
            "target_path": "WAI-Spoke/WAI-State.json",
            "version": "3.1.0",
            "changed_from": "3.0.0",
            "why_changed": "Added wheel.name initialization support",
            "safe_to_auto_adopt": False,
            "requires_review": True,
            "applies_to": ["spoke"]
        },
        {
            "name": "WAI-State.md",
            "template_path": "templates/WAI-Spoke/WAI-State.md",
            "target_path": "WAI-Spoke/WAI-State.md",
            "version": "3.1.0",
            "changed_from": "2.1.0",
            "why_changed": "Updated documentation for new wheel identity fields",
            "safe_to_auto_adopt": True,
            "requires_review": False,
            "applies_to": ["spoke"]
        },
        {
            "name": "wai-closeout.md",
            "template_path": "templates/commands/wai-closeout.md",
            "target_path": "WAI-Spoke/commands/wai-closeout.md",
            "version": "3.1.0",
            "changed_from": "2.0.0",
            "why_changed": "Added automatic outbox delivery as Step 1",
            "safe_to_auto_adopt": True,
            "requires_review": False,
            "applies_to": ["spoke"]
        },
        {
            "name": "wai-shipit.md",
            "template_path": "templates/commands/wai-shipit.md",
            "target_path": "WAI-Spoke/commands/wai-shipit.md",
            "version": "3.1.0",
            "changed_from": "2.0.0",
            "why_changed": "Integrated QC checks and auto-teach workflow",
            "safe_to_auto_adopt": True,
            "requires_review": False,
            "applies_to": ["spoke"]
        },
        {
            "name": "WAI-Events.json",
            "template_path": "templates/WAI-Spoke/WAI-Events.json",
            "target_path": "WAI-Spoke/WAI-Events.json",
            "version": "3.1.0",
            "changed_from": "1.0.0",
            "why_changed": "Added new event types for inbox processing",
            "safe_to_auto_adopt": True,
            "requires_review": False,
            "applies_to": ["spoke"]
        },
        {
            "name": "WAI-Startup.json",
            "template_path": "templates/WAI-Spoke/WAI-Startup.json",
            "target_path": "WAI-Spoke/WAI-Startup.json",
            "version": "3.1.0",
            "changed_from": "1.0.0",
            "why_changed": "Defined skill manifest for startup loading",
            "safe_to_auto_adopt": True,
            "requires_review": False,
            "applies_to": ["spoke"]
        },
        {
            "name": "AGENTS.md",
            "template_path": "templates/claude/AGENTS.md",
            "target_path": "AGENTS.md",
            "version": "3.1.0",
            "changed_from": "2.0.0",
            "why_changed": "Universal AI instructions for Claude Code integration",
            "safe_to_auto_adopt": False,
            "requires_review": True,
            "applies_to": ["spoke", "hub"]
        },
    ]

    for file_spec in spoke_files:
        source_path = framework_path / file_spec["template_path"]

        if source_path.exists():
            builder.add_file(
                name=file_spec["name"],
                path=file_spec["target_path"],
                source_path=str(source_path),
                version=file_spec["version"],
                changed_from=file_spec["changed_from"],
                why_changed=file_spec["why_changed"],
                safe_to_auto_adopt=file_spec["safe_to_auto_adopt"],
                requires_review=file_spec["requires_review"],
                applies_to=file_spec["applies_to"]
            )

    # Step 4: Add hub template files
    hub_files = [
        {
            "name": "hub-registry.json",
            "template_path": "templates/HUB/hub-registry.json",
            "target_path": "WAI-Spoke/hub-registry.json",
            "version": "3.1.0",
            "changed_from": "2.0.0",
            "why_changed": "Added wheel.name initialization during registration",
            "safe_to_auto_adopt": False,
            "requires_review": True,
            "applies_to": ["hub"]
        },
    ]

    for file_spec in hub_files:
        source_path = framework_path / file_spec["template_path"]

        if source_path.exists():
            builder.add_hub_file(
                name=file_spec["name"],
                path=file_spec["target_path"],
                source_path=str(source_path),
                version=file_spec["version"],
                changed_from=file_spec["changed_from"],
                why_changed=file_spec["why_changed"],
                safe_to_auto_adopt=file_spec["safe_to_auto_adopt"],
                requires_review=file_spec["requires_review"]
            )

    # Step 5: Build plan
    plan_dict = builder.build(hub_fingerprint=hub_fingerprint)

    # Step 6: Save plan
    output_path = framework_path / "upgrade-adoption-plan.json"

    if save_upgrade_plan(plan_dict, output_path):
        result["plan_path"] = output_path

        # Verify file exists and is valid
        if output_path.exists() and output_path.stat().st_size > 0:
            try:
                # Validate JSON
                test_load = json.loads(output_path.read_text(encoding="utf-8"))

                # Verify metadata
                if test_load.get("metadata", {}).get("version") != framework_version:
                    result["errors"].append("Plan version mismatch")
                    return result

                # Verify file counts
                files_count = len(test_load.get("files", []))
                hub_files_count = len(test_load.get("hub_files", []))

                # Step 7: Create outbox lug
                lug = {
                    "id": f"lug-framework-upgrade-plan-v{framework_version}",
                    "ty": "signal",
                    "signal_type": "framework_upgrade_ready",
                    "title": f"Framework Upgrade Plan v{framework_version} Ready for Distribution",
                    "ca": now_iso(),
                    "source_wheel_id": "framework",
                    "destination_wheel_id": "hub",
                    "plan_location": str(output_path),
                    "plan_version": framework_version,
                    "file_count": files_count + hub_files_count,
                    "hub_file_count": hub_files_count,
                    "spoke_file_count": files_count,
                    "safe_to_auto_adopt_count": len([f for f in spoke_files if f["safe_to_auto_adopt"]]),
                    "requires_review_count": len([f for f in spoke_files if f["requires_review"]])
                }

                # Write lug to outbox
                outbox_dir = framework_path / "WAI-Spoke" / "lugs" / "outbox"
                outbox_dir.mkdir(parents=True, exist_ok=True)

                lug_path = outbox_dir / f"{lug['id']}.jsonl"
                lug_path.write_text(json.dumps(lug), encoding="utf-8")

                result["lug_path"] = lug_path
                result["success"] = True

            except json.JSONDecodeError as e:
                result["errors"].append(f"Generated plan is not valid JSON: {e}")
        else:
            result["errors"].append("Plan file not created or empty")
    else:
        result["errors"].append("Failed to save upgrade plan")

    return result


def main():
    """CLI entry point for framework building."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Build framework and generate upgrade adoption plan"
    )
    parser.add_argument(
        "--framework-path",
        type=Path,
        help="Path to framework (auto-discovered if not provided)"
    )
    parser.add_argument(
        "--hub-path",
        type=Path,
        help="Path to hub (for signing)"
    )

    args = parser.parse_args()

    print("Framework Build & Upgrade Plan Generation")
    print("=" * 60)
    print()

    result = build_and_save(
        framework_path=args.framework_path,
        hub_path=args.hub_path
    )

    if result["success"]:
        print("✓ Success!")
        print(f"  Plan saved to: {result['plan_path']}")
        print(f"  Lug created at: {result['lug_path']}")
        print()
        print("Next steps:")
        print("  1. Run closeout to distribute lug to hub")
        print("  2. Hub will receive upgrade plan signal")
        print("  3. Hub can distribute to all spokes")
    else:
        print("✗ Failed")
        print("Errors:")
        for error in result["errors"]:
            print(f"  - {error}")
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

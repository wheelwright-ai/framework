#!/usr/bin/env python3
"""
WAI v2 Lug Schema Migration Script

Migrates WAI-Lugs.jsonl files from v1 to v2 schema:
- Adds required v2 fields: impact, created_by, node, created_at
- Maps status values to v2 format
- Preserves original values in _v1_* fields
- Adds PEV optional fields (null)
- Adds calibration fields (null)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any


# Status mapping from v1 to v2
STATUS_MAP = {
    "open": "published",
    "ready": "published",
    "active": "published",
    "in-progress": "in_progress",
    "in_progress": "in_progress",
    "closed": "resolved",
    "complete": "resolved",
    "completed": "resolved",
    "blocked": "published",  # Preserve blocker info, but status is published
}


def derive_node_from_path(file_path: Path) -> str:
    """Derive node identifier from file path."""
    parts = file_path.parts

    # Try to find project/extension pattern
    if "WAI-Spoke" in parts:
        # For now, default to "wheelwright/framework"
        # In Phase 2, we'll have proper registry paths
        return "wheelwright/framework"

    return "unknown"


def migrate_lug_v1_to_v2(lug: Dict[str, Any], node: str) -> Dict[str, Any]:
    """Migrate a single Lug from v1 to v2 schema."""

    # Handle metadata line (skip migration)
    if "_meta" in lug:
        return lug

    v2_lug = {}

    # Map v1 fields to v2
    # id: i → id
    v2_lug["id"] = lug.get("i", lug.get("id", ""))

    # type: ty → type (full name, not code)
    v2_lug["type"] = lug.get("ty", lug.get("type", "task"))

    # title: unchanged
    v2_lug["title"] = lug.get("title", lug.get("t", "Untitled"))

    # status: map from v1 to v2
    v1_status = lug.get("status", lug.get("s", "open"))
    v2_lug["status"] = STATUS_MAP.get(v1_status, "published")
    v2_lug["_v1_status"] = v1_status  # Preserve original

    # description: unchanged
    v2_lug["description"] = lug.get("description", lug.get("d", ""))

    # NEW REQUIRED FIELDS

    # impact: default to 3 for local tasks
    v2_lug["impact"] = lug.get("impact", lug.get("im", 3))
    if isinstance(v2_lug["impact"], str):
        # Convert string impact to numeric
        impact_map = {"low": 2, "medium": 5, "high": 8, "critical": 10}
        v2_lug["impact"] = impact_map.get(v2_lug["impact"], 5)

    # created_by: default to "conductor" for human-created
    v2_lug["created_by"] = lug.get("created_by", "conductor")

    # node: derived from file path
    v2_lug["node"] = lug.get("node", node)

    # created_at: use existing or default
    v2_lug["created_at"] = lug.get("created_at", lug.get("ca", "2026-02-11T00:00:00Z"))

    # OPTIONAL PEV FIELDS (null for now - available for future)
    v2_lug["perceive"] = lug.get("perceive", None)
    v2_lug["execute"] = lug.get("execute", None)
    v2_lug["verify"] = lug.get("verify", None)

    # CALIBRATION FIELDS (null until resolution)
    v2_lug["resolution"] = lug.get("resolution", None)
    v2_lug["resolution_reason"] = lug.get("resolution_reason", None)

    # PRESERVE OTHER v1 FIELDS
    for key in ["priority", "tags", "blocks", "blocked_by", "scope", "modules",
                "category", "p", "v", "si", "pt", "ex", "ua", "cla", "su", "bb"]:
        if key in lug:
            v2_lug[key] = lug[key]

    # Preserve v1 type code if different from ty
    if "t" in lug and lug["t"] != lug.get("ty"):
        v2_lug["_v1_type_code"] = lug["t"]

    # Preserve v1 status code if different from status
    if "s" in lug and lug["s"] != lug.get("status"):
        v2_lug["_v1_status_code"] = lug["s"]

    return v2_lug


def migrate_file(file_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """Migrate a single WAI-Lugs.jsonl file."""

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Migrating: {file_path}")

    node = derive_node_from_path(file_path)
    print(f"  Node: {node}")

    # Read all lugs
    lugs_v1 = []
    with open(file_path, 'r') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                lug = json.loads(line)
                lugs_v1.append(lug)
            except json.JSONDecodeError as e:
                print(f"  ⚠️  Line {i}: JSON parse error: {e}")
                continue

    print(f"  Read: {len(lugs_v1)} lugs")

    # Migrate each lug
    lugs_v2 = []
    for i, lug_v1 in enumerate(lugs_v1, 1):
        try:
            lug_v2 = migrate_lug_v1_to_v2(lug_v1, node)
            lugs_v2.append(lug_v2)
        except Exception as e:
            print(f"  ⚠️  Lug {i}: Migration error: {e}")
            print(f"       Original: {json.dumps(lug_v1)[:100]}")
            continue

    print(f"  Migrated: {len(lugs_v2)} lugs")

    # Write back
    if not dry_run:
        with open(file_path, 'w') as f:
            for lug_v2 in lugs_v2:
                f.write(json.dumps(lug_v2) + '\n')
        print(f"  ✅ Written to {file_path}")
    else:
        print(f"  🔍 DRY RUN: Would write {len(lugs_v2)} lugs")

    return {
        "file": str(file_path),
        "v1_count": len(lugs_v1),
        "v2_count": len(lugs_v2),
        "node": node
    }


def main():
    """Main migration entry point."""

    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No files will be modified")
        print("=" * 60)

    # Find all WAI-Lugs.jsonl files (excluding backups)
    root = Path.cwd()
    lug_files = [
        f for f in root.rglob("WAI-Lugs.jsonl")
        if ".v1-backup" not in str(f) and "node_modules" not in str(f)
    ]

    print(f"\nFound {len(lug_files)} Lugs files to migrate\n")

    results = []
    for lug_file in sorted(lug_files):
        result = migrate_file(lug_file, dry_run=dry_run)
        results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)

    total_v1 = sum(r["v1_count"] for r in results)
    total_v2 = sum(r["v2_count"] for r in results)

    for result in results:
        status = "✅" if result["v2_count"] == result["v1_count"] else "⚠️"
        print(f"{status} {result['file']}")
        print(f"     v1: {result['v1_count']} → v2: {result['v2_count']}")

    print(f"\nTotal Lugs: {total_v1} → {total_v2}")

    if total_v1 != total_v2:
        print("⚠️  WARNING: Some lugs failed to migrate")
        return 1

    if not dry_run:
        print("\n✅ Migration complete!")
    else:
        print("\n🔍 Dry run complete. Run without --dry-run to apply changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

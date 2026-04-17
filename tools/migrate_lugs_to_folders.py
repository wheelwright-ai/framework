#!/usr/bin/env python3
"""Migrate WAI-Lugs.jsonl from monolithic file to typed folder structure.

Creates:
  WAI-Spoke/lugs/active/WAI-Lugs-active.jsonl  (open/in_progress only)
  WAI-Spoke/lugs/{type}/{id}.json               (one file per archived lug)
  WAI-Spoke/WAI-LugIndex.jsonl                  (lightweight index of all lugs)
  WAI-Spoke/WAI-Lugs.jsonl.pre-diet-backup      (original backup)

Usage:
  python3 tools/migrate_lugs_to_folders.py [--dry-run]
"""

import json
import os
import shutil
import sys

SPOKE_DIR = "WAI-Spoke"
LUGS_FILE = os.path.join(SPOKE_DIR, "WAI-Lugs.jsonl")
LUGS_DIR = os.path.join(SPOKE_DIR, "lugs")
ACTIVE_DIR = os.path.join(LUGS_DIR, "active")
ACTIVE_FILE = os.path.join(ACTIVE_DIR, "WAI-Lugs-active.jsonl")
INDEX_FILE = os.path.join(SPOKE_DIR, "WAI-LugIndex.jsonl")
BACKUP_FILE = LUGS_FILE + ".pre-diet-backup"

ACTIVE_STATUSES = {"open", "in_progress"}

# Normalize short-form keys used by some lugs
KEY_MAP = {
    "i": "id",
    "ty": "type",
    "t": "title",
    "s": "status",
    "ca": "created_at",
    "gb": "created_by",
}

# Folders to skip (already used for other purposes)
RESERVED_DIRS = {"incoming", "outgoing", "processed", "active", "reference"}


def normalize_lug(lug):
    """Expand short-form keys to full keys for index generation."""
    normalized = {}
    for k, v in lug.items():
        full_key = KEY_MAP.get(k, k)
        normalized[full_key] = v
    return normalized


def get_lug_type(lug):
    """Extract type, handling both full and short-form keys."""
    raw_type = lug.get("type", lug.get("ty", "unknown"))
    # Some lugs have 't' as title not type — if it's too long, it's a title
    if isinstance(raw_type, str) and len(raw_type) > 30:
        return "unknown"
    return raw_type.replace(" ", "-").lower()


def get_lug_id(lug):
    return lug.get("id", lug.get("i", "unknown"))


def get_lug_status(lug):
    return lug.get("status", lug.get("s", "unknown"))


def get_lug_title(lug):
    title = lug.get("title", lug.get("t", ""))
    if isinstance(title, str) and len(title) > 120:
        return title[:117] + "..."
    return title


def get_lug_created(lug):
    return lug.get("created_at", lug.get("ca", ""))


def sanitize_dirname(name):
    """Make a string safe for use as a directory name."""
    return name.replace("/", "-").replace("\\", "-").replace(" ", "-").lower()


def main():
    dry_run = "--dry-run" in sys.argv

    if not os.path.exists(LUGS_FILE):
        print(f"ERROR: {LUGS_FILE} not found")
        sys.exit(1)

    # Read all lugs
    lugs = []
    with open(LUGS_FILE, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                lug = json.loads(line)
                lugs.append(lug)
            except json.JSONDecodeError as e:
                print(f"WARNING: Skipping malformed line {line_num}: {e}")

    print(f"Read {len(lugs)} lugs from {LUGS_FILE}")

    # Classify
    active_lugs = []
    archive_lugs = []
    type_counts = {}

    for lug in lugs:
        status = get_lug_status(lug)
        lug_type = get_lug_type(lug)
        type_counts[lug_type] = type_counts.get(lug_type, 0) + 1

        if status in ACTIVE_STATUSES:
            active_lugs.append(lug)
        else:
            archive_lugs.append((lug_type, lug))

    print(f"\nClassification:")
    print(f"  Active (open/in_progress): {len(active_lugs)}")
    print(f"  Archive: {len(archive_lugs)}")
    print(f"\nType distribution:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

    if dry_run:
        print("\n[DRY RUN] Would create:")
        print(f"  {ACTIVE_FILE} ({len(active_lugs)} lugs)")
        types_seen = set()
        for lug_type, lug in archive_lugs:
            safe_type = sanitize_dirname(lug_type)
            types_seen.add(safe_type)
        for t in sorted(types_seen):
            count = sum(1 for lt, _ in archive_lugs if sanitize_dirname(lt) == t)
            print(f"  {LUGS_DIR}/{t}/ ({count} files)")
        print(f"  {INDEX_FILE} ({len(lugs)} entries)")
        print(f"  {BACKUP_FILE}")
        return

    # Create backup
    shutil.copy2(LUGS_FILE, BACKUP_FILE)
    print(f"\nBackup: {BACKUP_FILE}")

    # Create active directory and file
    os.makedirs(ACTIVE_DIR, exist_ok=True)
    with open(ACTIVE_FILE, "w") as f:
        for lug in active_lugs:
            f.write(json.dumps(lug, ensure_ascii=False) + "\n")
    print(f"Written: {ACTIVE_FILE} ({len(active_lugs)} lugs)")

    # Create archive folders and files
    archive_counts = {}
    for lug_type, lug in archive_lugs:
        safe_type = sanitize_dirname(lug_type)
        if safe_type in RESERVED_DIRS:
            safe_type = safe_type + "-archive"
        type_dir = os.path.join(LUGS_DIR, safe_type)
        os.makedirs(type_dir, exist_ok=True)

        lug_id = get_lug_id(lug)
        safe_id = lug_id.replace("/", "-").replace("\\", "-")
        lug_file = os.path.join(type_dir, f"{safe_id}.json")

        with open(lug_file, "w") as f:
            json.dump(lug, f, ensure_ascii=False, indent=2)

        archive_counts[safe_type] = archive_counts.get(safe_type, 0) + 1

    print(f"\nArchived to folders:")
    for t, c in sorted(archive_counts.items(), key=lambda x: -x[1]):
        print(f"  {LUGS_DIR}/{t}/: {c} files")

    # Generate index
    index_entries = []
    for lug in lugs:
        status = get_lug_status(lug)
        entry = {
            "id": get_lug_id(lug),
            "type": get_lug_type(lug),
            "status": status,
            "title": get_lug_title(lug),
            "folder": "active" if status in ACTIVE_STATUSES else sanitize_dirname(get_lug_type(lug)),
            "created_at": get_lug_created(lug),
        }
        index_entries.append(entry)

    with open(INDEX_FILE, "w") as f:
        for entry in index_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    index_size = os.path.getsize(INDEX_FILE)
    original_size = os.path.getsize(BACKUP_FILE)
    active_size = os.path.getsize(ACTIVE_FILE)
    print(f"\nIndex: {INDEX_FILE} ({len(index_entries)} entries, {index_size:,} bytes)")
    print(f"\nSize comparison:")
    print(f"  Original WAI-Lugs.jsonl:    {original_size:,} bytes")
    print(f"  Active lugs file:           {active_size:,} bytes (~{active_size * 100 // original_size}%)")
    print(f"  Index file:                 {index_size:,} bytes (~{index_size * 100 // original_size}%)")
    print(f"  Wakeup load (active+index): {active_size + index_size:,} bytes (~{(active_size + index_size) * 100 // original_size}%)")
    print(f"\nSavings at wakeup: {original_size - active_size:,} bytes ({(original_size - active_size) * 100 // original_size}% reduction)")
    print(f"  (Index is available on-demand, not loaded at wakeup)")

    print(f"\nDone. Original preserved at {BACKUP_FILE}")
    print(f"Update wai.md Step 4 to read {ACTIVE_FILE} instead of {LUGS_FILE}")


if __name__ == "__main__":
    main()

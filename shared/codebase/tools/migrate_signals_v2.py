#!/usr/bin/env python3
"""
migrate_signals_v2.py — One-time migration: move signal lugs from bytype/signal/ to signals/ v2 architecture.

Architecture decision: decision-signal-architecture-v2
Signals are now risk bulletins (patch or delivery flavor) stored in WAI-Spoke/signals/,
NOT work lugs in bytype/signal/. This script moves any remaining signal lugs and cleans up.

Usage:
    python3 tools/migrate_signals_v2.py [--dry-run]
"""

import json
import os
import shutil
import sys
from pathlib import Path

SPOKE_ROOT = Path(__file__).resolve().parent.parent / "WAI-Spoke"
BYTYPE_SIGNAL = SPOKE_ROOT / "lugs" / "bytype" / "signal"
SIGNALS_V2 = SPOKE_ROOT / "signals"
REGISTRY_PATH = SIGNALS_V2 / "registry.json"


def load_registry():
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    return {"_schema": "signals-registry-v2", "applied": [], "applied_at": {}}


def save_registry(registry):
    SIGNALS_V2.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)


def migrate(dry_run=False):
    registry = load_registry()
    migrated = 0

    # Ensure v2 dirs exist
    for subdir in ["inbound", "processed"]:
        d = SIGNALS_V2 / subdir
        if not dry_run:
            d.mkdir(parents=True, exist_ok=True)

    # Find signal lugs in undelivered/
    undelivered = BYTYPE_SIGNAL / "undelivered"
    if undelivered.exists():
        for f in undelivered.glob("*.json"):
            print(f"  Migrating: {f.name}")
            if not dry_run:
                # Read the signal, record in registry, move to processed
                with open(f) as fh:
                    sig = json.load(fh)
                sig_id = sig.get("id", f.stem)
                registry["applied"].append(sig_id)
                registry["applied_at"][sig_id] = "migrated_by_script"
                shutil.move(str(f), str(SIGNALS_V2 / "processed" / f.name))
            migrated += 1

    # Find signal lugs in open/
    open_dir = BYTYPE_SIGNAL / "open"
    if open_dir.exists():
        for f in open_dir.glob("*.json"):
            print(f"  Migrating open: {f.name}")
            if not dry_run:
                with open(f) as fh:
                    sig = json.load(fh)
                sig_id = sig.get("id", f.stem)
                registry["applied"].append(sig_id)
                registry["applied_at"][sig_id] = "migrated_by_script"
                shutil.move(str(f), str(SIGNALS_V2 / "processed" / f.name))
            migrated += 1

    if not dry_run:
        save_registry(registry)

    print(f"Migration complete: {migrated} signals migrated.")
    return migrated


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("DRY RUN — no files will be moved.")
    migrate(dry_run=dry_run)

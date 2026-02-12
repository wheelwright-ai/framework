#!/usr/bin/env python3
"""
Absorb WAI-Signals.jsonl into WAI-Lugs.jsonl as v2 Lugs with impact >= 8
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def signal_to_lug(signal: dict, node: str) -> list:
    """Convert a signal and its offers into v2 Lugs."""
    lugs = []

    timestamp = signal.get("timestamp", datetime.now(timezone.utc).isoformat())
    created_by = signal.get("by", "system")

    # Each offer becomes a Lug
    for offer in signal.get("offers", []):
        lug = {
            "id": offer.get("lug_id", f"sig_{timestamp[:10]}"),
            "type": offer.get("lug_type", offer.get("type", "signal")),
            "title": offer.get("topic", "Untitled signal"),
            "status": "published",
            "description": offer.get("context", ""),
            "impact": max(offer.get("impact", 8), 8),  # Signals are high-impact
            "created_by": created_by,
            "node": node,
            "created_at": timestamp,
            "perceive": None,
            "execute": None,
            "verify": None,
            "resolution": None,
            "resolution_reason": None,
        }

        # Preserve signal metadata
        if "scope" in offer:
            lug["scope"] = offer["scope"]
        if "modules" in offer:
            lug["modules"] = offer["modules"]
        if "category" in offer:
            lug["category"] = offer["category"]

        # Mark as absorbed from signal
        lug["_absorbed_from_signal"] = True
        lug["_signal_timestamp"] = timestamp

        lugs.append(lug)

    return lugs


def main():
    root = Path.cwd()
    signal_files = [
        f for f in root.rglob("WAI-Signals.jsonl")
        if "DEPRECATED" not in str(f) and "node_modules" not in str(f)
    ]

    print(f"Found {len(signal_files)} signal files\n")

    for signal_file in signal_files:
        lug_file = signal_file.parent / "WAI-Lugs.jsonl"

        if not lug_file.exists():
            print(f"⚠️  No Lugs file found for {signal_file}, skipping")
            continue

        print(f"Processing: {signal_file}")

        # Read signals
        signals = []
        with open(signal_file, 'r') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    signal = json.loads(line)
                    signals.append(signal)
                except json.JSONDecodeError as e:
                    print(f"  ⚠️  Line {i}: JSON parse error: {e}")

        if not signals:
            print(f"  No valid signals found, skipping\n")
            continue

        print(f"  Read {len(signals)} signals")

        # Convert to Lugs
        node = "wheelwright/framework"  # Derive from path in Phase 2
        absorbed_lugs = []
        for signal in signals:
            lugs = signal_to_lug(signal, node)
            absorbed_lugs.extend(lugs)

        print(f"  Converted to {len(absorbed_lugs)} Lugs")

        # Append to Lugs file
        with open(lug_file, 'a') as f:
            for lug in absorbed_lugs:
                f.write(json.dumps(lug) + '\n')

        print(f"  ✅ Appended to {lug_file}")

        # Add tombstone to signals file
        tombstone = (
            "# RETIRED: Absorbed into WAI-Lugs.jsonl as of WAI v2 migration.\n"
            "# Do not use this file. All signals are now Lugs with impact >= 8.\n"
            f"# Absorbed {len(absorbed_lugs)} signals on {datetime.now(timezone.utc).isoformat()}\n"
        )

        # Prepend tombstone
        original_content = signal_file.read_text()
        signal_file.write_text(tombstone + "\n" + original_content)

        print(f"  ✅ Added tombstone to {signal_file}\n")

    print("✅ Signal absorption complete!")


if __name__ == "__main__":
    main()

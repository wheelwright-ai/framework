"""
Outbox Delivery Module - Automatic lug distribution during closeout.

Handles automatic distribution of lugs from outbox to their destinations.
Part of the Auto-Teach/Learn Protocol implementation.

This module replaces the manual teach/learn CLI commands with automated
delivery during the closeout cycle.

Key functions:
    - deliver_outbox_lugs: Main entry point for automatic delivery
    - resolve_destination_path: Resolve wheel_id to filesystem path
    - create_delivery_confirmation: Generate confirmation lugs for hub
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, NamedTuple


class DeliveryReport(NamedTuple):
    """Report of delivery operation results."""
    delivered: int
    skipped: int
    failed: int
    destinations: List[str]
    errors: List[str]


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def resolve_destination_path(
    destination_wheel_id: str,
    hub_path: Optional[Path],
    interactive: bool
) -> Optional[Path]:
    """
    Resolve wheel_id to filesystem path.

    Logic per specification:
    1. If destination == "hub" → return hub_path from WAI-State
    2. Else → read hub registry, lookup wheel_id
    3. If not found and interactive → ask user
    4. Return Path or None

    Args:
        destination_wheel_id: Target wheel ID (e.g., "basher", "hub", "*")
        hub_path: Path to hub (from WAI-State.json)
        interactive: If True, prompt user for unknown destinations

    Returns:
        Path to destination spoke, or None if unresolved
    """
    # Case 1: destination is hub
    if destination_wheel_id.lower() == "hub":
        return hub_path

    # Case 2: broadcast destination (handled separately)
    if destination_wheel_id == "*":
        return None  # Broadcast requires special handling

    # Case 3: lookup in hub registry
    if not hub_path:
        return None

    registry_path = hub_path / "hub-registry.json"
    if not registry_path.exists():
        return None

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return None

    # Search for wheel_id in registry
    for wheel in registry.get("wheels", []):
        if wheel.get("wheel_id") == destination_wheel_id and wheel.get("status") == "active":
            spoke_path = wheel.get("path")
            if spoke_path:
                return Path(spoke_path)

    # Case 4: not found - handle based on interactive mode
    if interactive:
        # Interactive resolution will be handled by caller using AskUserQuestion
        # Return None to signal "needs resolution"
        return None
    else:
        # Non-interactive: skip
        return None


def create_delivery_confirmation(
    source_wheel_id: str,
    delivered_lug: Dict[str, Any],
    destination_wheel_id: str,
    delivery_path: Path
) -> Dict[str, Any]:
    """
    Create delivery confirmation lug for hub.

    Per specification, required fields are:
    - id
    - ty: "signal"
    - signal_type: "delivery_confirmation"
    - source_wheel_id: spoke that received the lug
    - destination_wheel_id: "hub"
    - delivered_lug_id: ID of the delivered lug
    - delivered_at: ISO timestamp
    - delivery_path: where the lug was delivered

    Args:
        source_wheel_id: Wheel that sent the lug (for confirmation routing)
        delivered_lug: The lug that was delivered
        destination_wheel_id: Wheel that received the lug
        delivery_path: Filesystem path where lug was delivered

    Returns:
        Delivery confirmation lug dict
    """
    lug_id = delivered_lug.get("id", "unknown")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    return {
        "id": f"lug-confirm-{lug_id[:20]}-{timestamp}",
        "ty": "signal",
        "signal_type": "delivery_confirmation",
        "source_wheel_id": destination_wheel_id,  # Spoke that RECEIVED the lug
        "destination_wheel_id": "hub",
        "delivered_lug_id": lug_id,
        "delivered_at": now_iso(),
        "delivery_path": str(delivery_path)
    }


def deliver_outbox_lugs(
    project_path: Path,
    interactive: bool = True
) -> DeliveryReport:
    """
    Distribute all lugs from outbox to their destinations.

    Per specification:
    1. Read outbox lugs
    2. For each lug:
       - Resolve destination path
       - Copy to destination inbox
       - Create delivery confirmation
       - Move to outbox/distributed/
    3. Return summary report

    Args:
        project_path: Root project directory
        interactive: If True, ask user to resolve unknown destinations

    Returns:
        DeliveryReport with success/failure counts
    """
    delivered_count = 0
    skipped_count = 0
    failed_count = 0
    destinations = []
    errors = []

    # Read project's WAI-State to get hub path and wheel identity
    state_path = project_path / "WAI-Spoke" / "WAI-State.json"
    if not state_path.exists():
        errors.append("WAI-State.json not found - cannot determine hub path")
        return DeliveryReport(0, 0, 1, [], errors)

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        errors.append(f"Failed to read WAI-State.json: {e}")
        return DeliveryReport(0, 0, 1, [], errors)

    hub_path_str = state.get("wheel", {}).get("hub_path")
    if not hub_path_str:
        errors.append("hub_path not set in WAI-State.json - cannot deliver lugs")
        return DeliveryReport(0, 0, 1, [], errors)

    hub_path = Path(hub_path_str)
    source_wheel_id = state.get("wheel", {}).get("name", project_path.name)

    # Check outbox directory
    outbox_dir = project_path / "WAI-Spoke" / "lugs" / "outbox"
    if not outbox_dir.exists():
        # No outbox = nothing to deliver (not an error)
        return DeliveryReport(0, 0, 0, [], [])

    # Get all lug files from outbox
    lug_files = list(outbox_dir.glob("*.jsonl"))
    if not lug_files:
        # Empty outbox = nothing to deliver
        return DeliveryReport(0, 0, 0, [], [])

    # Create distributed directory for archiving delivered lugs
    distributed_dir = outbox_dir / "distributed"
    distributed_dir.mkdir(parents=True, exist_ok=True)

    # Process each lug
    delivery_confirmations = []

    for lug_file in lug_files:
        try:
            # Read lug
            lug_data = json.loads(lug_file.read_text(encoding="utf-8").strip())
            lug_id = lug_data.get("id", lug_file.stem)
            dest_wheel_id = lug_data.get("destination_wheel_id", "")

            if not dest_wheel_id:
                errors.append(f"Lug {lug_id} has no destination_wheel_id - skipped")
                skipped_count += 1
                continue

            # Resolve destination path
            dest_path = resolve_destination_path(dest_wheel_id, hub_path, interactive)

            if dest_path is None:
                if interactive:
                    # Unknown destination - will need user resolution
                    # For now, skip and log (AskUserQuestion integration will happen in closeout skill)
                    errors.append(f"Lug {lug_id}: destination '{dest_wheel_id}' not found in hub registry")
                    skipped_count += 1
                    continue
                else:
                    errors.append(f"Lug {lug_id}: destination '{dest_wheel_id}' not found - skipped (non-interactive)")
                    skipped_count += 1
                    continue

            # Create destination inbox if needed
            dest_inbox = dest_path / "WAI-Spoke" / "lugs" / "inbox"
            try:
                dest_inbox.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                errors.append(f"Permission denied creating inbox at {dest_inbox}")
                failed_count += 1
                continue

            # Copy lug to destination inbox
            dest_file = dest_inbox / lug_file.name
            try:
                shutil.copy2(lug_file, dest_file)
            except Exception as e:
                errors.append(f"Failed to copy {lug_id} to {dest_inbox}: {e}")
                failed_count += 1
                continue

            # Verify write succeeded
            if not dest_file.exists():
                errors.append(f"Failed to verify write for {lug_id} at {dest_file}")
                failed_count += 1
                continue

            # Success - create delivery confirmation
            confirmation = create_delivery_confirmation(
                source_wheel_id=source_wheel_id,
                delivered_lug=lug_data,
                destination_wheel_id=dest_wheel_id,
                delivery_path=dest_file
            )
            delivery_confirmations.append(confirmation)

            # Move to distributed archive
            archive_file = distributed_dir / lug_file.name
            try:
                shutil.move(str(lug_file), str(archive_file))
            except Exception as e:
                errors.append(f"Warning: Failed to archive {lug_id}: {e}")
                # Not a critical error - delivery succeeded

            delivered_count += 1
            if dest_wheel_id not in destinations:
                destinations.append(dest_wheel_id)

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in {lug_file.name}: {e}")
            skipped_count += 1
        except Exception as e:
            errors.append(f"Unexpected error processing {lug_file.name}: {e}")
            failed_count += 1

    # Write delivery confirmations to hub inbox (if not self-delivery)
    is_self = project_path.resolve() == hub_path.resolve()

    if delivery_confirmations and not is_self:
        hub_inbox = hub_path / "WAI-Spoke" / "lugs" / "inbox"
        try:
            hub_inbox.mkdir(parents=True, exist_ok=True)

            for confirmation in delivery_confirmations:
                confirm_file = hub_inbox / f"{confirmation['id']}.jsonl"
                confirm_file.write_text(
                    json.dumps(confirmation),
                    encoding="utf-8"
                )
        except Exception as e:
            errors.append(f"Failed to write delivery confirmations to hub: {e}")
            # Not a critical error - deliveries still succeeded

    return DeliveryReport(
        delivered=delivered_count,
        skipped=skipped_count,
        failed=failed_count,
        destinations=destinations,
        errors=errors
    )

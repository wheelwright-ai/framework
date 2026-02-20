"""
Cross-Spoke Lug Dropping - Create lugs for other spokes without switching projects.

Enables creating task/signal/idea lugs destined for another spoke from the current
project. Lugs are placed in hub's outbox with destination_wheel_id set.
Next teach cycle delivers them to the target spoke's inbox.

Usage:
    from wai.cross_spoke import drop_lug_for_spoke

    # Drop a task for the basher project
    success = drop_lug_for_spoke(
        target_spoke="basher",
        lug_type="task",
        title="Implement retry logic",
        content={"description": "Add exponential backoff for API calls"}
    )
"""

import json
import hashlib
import random
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def generate_lug_id(title: str, target: str) -> str:
    """Generate a unique lug ID."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    salt = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    content = f"{title}:{target}:{timestamp}:{salt}"
    hash_hex = hashlib.sha256(content.encode()).hexdigest()[:12]
    return f"cross-{hash_hex}"


def get_current_spoke_id(spoke_path: Path) -> Optional[str]:
    """Get the current spoke's wheel_id from WAI-State.json."""
    state_file = spoke_path / "WAI-Spoke" / "WAI-State.json"

    if not state_file.exists():
        return None

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
        return state.get("wheel", {}).get("name") or state.get("wheel", {}).get("abbrev")
    except (json.JSONDecodeError, IOError):
        return None


def discover_hub_path(spoke_path: Path) -> Optional[Path]:
    """Discover hub path from spoke's WAI-State.json or auto-discovery."""
    state_file = spoke_path / "WAI-Spoke" / "WAI-State.json"

    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            hub_path = state.get("wheelwright", {}).get("hub_path")
            if hub_path:
                return Path(hub_path)
        except (json.JSONDecodeError, IOError):
            pass

    # Try auto-discovery
    try:
        from .hub import HubManager
        hub_manager = HubManager()
        return hub_manager.auto_discover_hub(spoke_path)
    except ImportError:
        pass

    return None


def validate_target_spoke(target_spoke: str, hub_path: Path) -> bool:
    """Check if target spoke exists in hub registry."""
    registry_path = hub_path / "hub-registry.json"

    if not registry_path.exists():
        return False

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        for wheel in registry.get("wheels", []):
            if wheel.get("wheel_id") == target_spoke and wheel.get("status") == "active":
                return True
        return False
    except (json.JSONDecodeError, IOError):
        return False


def drop_lug_for_spoke(
    target_spoke: str,
    lug_type: str,
    title: str,
    content: Dict[str, Any],
    spoke_path: Optional[Path] = None,
    hub_path: Optional[Path] = None,
    priority: str = "medium"
) -> bool:
    """
    Create a lug destined for another spoke.

    Places the lug in hub's outbox with destination_wheel_id set.
    Next teach cycle (closeout) delivers it to the target spoke's inbox.

    Args:
        target_spoke: Target spoke name (wheel_id) e.g., "basher"
        lug_type: Type of lug - "task", "signal", "idea", etc.
        title: Brief title/description
        content: Content dict (varies by lug_type)
        spoke_path: Path to current project (auto-detected if not provided)
        hub_path: Path to hub (auto-discovered if not provided)
        priority: Priority level - "low", "medium", "high"

    Returns:
        True if lug was created successfully, False otherwise

    Example:
        drop_lug_for_spoke(
            "basher",
            "task",
            "Implement retry logic",
            {"description": "Add exponential backoff", "action": "implement"}
        )
    """
    # Auto-detect current project path
    if not spoke_path:
        spoke_path = Path.cwd()

    # Find hub
    if not hub_path:
        hub_path = discover_hub_path(spoke_path)

    if not hub_path:
        print("Error: Could not find hub for cross-spoke delivery")
        return False

    # Validate target spoke exists
    if not validate_target_spoke(target_spoke, hub_path):
        print(f"Warning: Target spoke '{target_spoke}' not found in hub registry")
        # Continue anyway - might be a new spoke not yet registered

    # Get source spoke ID
    source_spoke = get_current_spoke_id(spoke_path) or "unknown"

    # Generate lug
    lug_id = generate_lug_id(title, target_spoke)

    lug = {
        "id": lug_id,
        "ty": lug_type,
        "category": lug_type,
        "title": title,
        "source_wheel_id": source_spoke,
        "destination_wheel_id": target_spoke,
        "created_at": now_iso(),
        "status": "pending",
        "priority": priority,
        "content": content
    }

    # Write to hub's outbox (not current spoke's)
    outbox = hub_path / "WAI-Spoke" / "lugs" / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)

    lug_file = outbox / f"{lug_id}.jsonl"

    try:
        lug_file.write_text(json.dumps(lug, indent=2), encoding="utf-8")
        print(f"Created lug for {target_spoke}: {lug_id}")
        return True
    except IOError as e:
        print(f"Error writing lug: {e}")
        return False


def drop_task_for_spoke(
    target_spoke: str,
    description: str,
    action: str = "implement",
    spoke_path: Optional[Path] = None,
    hub_path: Optional[Path] = None,
    priority: str = "medium"
) -> bool:
    """
    Shorthand for dropping a task lug.

    Args:
        target_spoke: Target spoke name
        description: Task description
        action: Action type (implement, fix, review, etc.)
        spoke_path: Path to current project
        hub_path: Path to hub
        priority: Priority level

    Returns:
        True if successful
    """
    content = {
        "description": description,
        "action": action
    }

    return drop_lug_for_spoke(
        target_spoke=target_spoke,
        lug_type="task",
        title=description[:80],  # Truncate for title
        content=content,
        spoke_path=spoke_path,
        hub_path=hub_path,
        priority=priority
    )


def drop_signal_for_spoke(
    target_spoke: str,
    signal: str,
    context: str = "",
    impact: int = 5,
    spoke_path: Optional[Path] = None,
    hub_path: Optional[Path] = None
) -> bool:
    """
    Shorthand for dropping a signal lug.

    Args:
        target_spoke: Target spoke name (or "hub" for hub)
        signal: Signal message
        context: Additional context
        impact: Impact score 1-10
        spoke_path: Path to current project
        hub_path: Path to hub

    Returns:
        True if successful
    """
    content = {
        "signal": signal,
        "context": context,
        "impact": impact
    }

    return drop_lug_for_spoke(
        target_spoke=target_spoke,
        lug_type="signal",
        title=signal[:80],
        content=content,
        spoke_path=spoke_path,
        hub_path=hub_path,
        priority="high" if impact >= 8 else "medium"
    )


def drop_idea_for_spoke(
    target_spoke: str,
    idea: str,
    rationale: str = "",
    spoke_path: Optional[Path] = None,
    hub_path: Optional[Path] = None
) -> bool:
    """
    Shorthand for dropping an idea lug.

    Args:
        target_spoke: Target spoke name
        idea: The idea/suggestion
        rationale: Why this idea is worth considering
        spoke_path: Path to current project
        hub_path: Path to hub

    Returns:
        True if successful
    """
    content = {
        "idea": idea,
        "rationale": rationale
    }

    return drop_lug_for_spoke(
        target_spoke=target_spoke,
        lug_type="idea",
        title=idea[:80],
        content=content,
        spoke_path=spoke_path,
        hub_path=hub_path,
        priority="low"
    )


def list_pending_cross_spoke_lugs(hub_path: Optional[Path] = None) -> list:
    """
    List pending cross-spoke lugs in hub's outbox.

    Args:
        hub_path: Path to hub (auto-discovered if not provided)

    Returns:
        List of pending lug summaries
    """
    if not hub_path:
        hub_path = discover_hub_path(Path.cwd())

    if not hub_path:
        return []

    outbox = hub_path / "WAI-Spoke" / "lugs" / "outbox"

    if not outbox.exists():
        return []

    lugs = []
    for lug_file in outbox.glob("*.jsonl"):
        try:
            lug = json.loads(lug_file.read_text(encoding="utf-8"))
            lugs.append({
                "id": lug.get("id"),
                "type": lug.get("ty"),
                "title": lug.get("title"),
                "source": lug.get("source_wheel_id"),
                "destination": lug.get("destination_wheel_id"),
                "created_at": lug.get("created_at")
            })
        except (json.JSONDecodeError, IOError):
            continue

    return lugs


__all__ = [
    "drop_lug_for_spoke",
    "drop_task_for_spoke",
    "drop_signal_for_spoke",
    "drop_idea_for_spoke",
    "list_pending_cross_spoke_lugs",
]

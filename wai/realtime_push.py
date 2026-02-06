"""
Real-time lug push from spokes to hub.

Enables immediate knowledge distribution without waiting for learn cycles.
Critical lugs trigger immediate notifications, high-impact lugs queue for next opportunity.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


def push_lug_to_hub(lug_data: Dict[str, Any], spoke_id: str, hub_path: Optional[Path] = None) -> bool:
    """
    Push a high-impact lug to hub immediately when created/closed.

    Args:
        lug_data: Lug dictionary (minified format)
        spoke_id: ID of source spoke
        hub_path: Path to hub (auto-discovered if not provided)

    Returns:
        True if pushed successfully
    """
    if not hub_path:
        # Auto-discover hub
        from .hub import discover_hub
        hub_path = discover_hub()
        if not hub_path:
            return False  # No hub connected, silent fail

    # Check if spoke is active (has recent sessions)
    if not is_spoke_active(spoke_id, hub_path):
        return False  # Don't push to inactive spokes, avoid noise

    # Only push high-impact lugs
    impact = lug_data.get('im', lug_data.get('impact', 0))
    if isinstance(impact, str):
        impact_map = {'small': 2, 'medium': 5, 'large': 8, 'critical': 10}
        impact = impact_map.get(impact, 0)

    if impact < 8:
        return False  # Low impact, let normal learn cycle handle it

    # Write to hub inbound queue
    inbound_dir = hub_path / 'WAI-Hub' / 'inbound' / spoke_id
    inbound_dir.mkdir(parents=True, exist_ok=True)

    lug_id = lug_data.get('i', lug_data.get('id', 'unknown'))
    lug_file = inbound_dir / f"{lug_id}.jsonl"

    # Add push metadata
    push_metadata = {
        'pushed_at': datetime.now().isoformat(),
        'impact': impact,
        'source_spoke': spoke_id
    }
    lug_data['_push'] = push_metadata

    try:
        with open(lug_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(lug_data) + '\n')

        # Set notification flag in hub state
        set_hub_notification(hub_path, spoke_id, lug_id, impact)
        return True
    except Exception:
        return False


def is_spoke_active(spoke_id: str, hub_path: Path) -> bool:
    """
    Check if spoke has had recent activity (session within last 7 days).

    Args:
        spoke_id: Spoke ID to check
        hub_path: Path to hub

    Returns:
        True if spoke is active
    """
    registry_path = hub_path / 'hub-registry.json'
    if not registry_path.exists():
        return True  # Assume active if no registry

    try:
        registry = json.loads(registry_path.read_text())
        for spoke in registry.get('spokes', []):
            if spoke.get('spoke_id') == spoke_id or spoke.get('path', '').endswith(spoke_id):
                last_session = spoke.get('last_session_at', '1970-01-01')
                # Parse and check if within 7 days
                from datetime import datetime, timedelta
                try:
                    last_dt = datetime.fromisoformat(last_session.replace('Z', '+00:00'))
                    cutoff = datetime.now() - timedelta(days=7)
                    return last_dt > cutoff
                except:
                    return True  # Default to active if can't parse
        return True  # Not in registry, assume active
    except:
        return True  # Error, default to active


def set_hub_notification(hub_path: Path, spoke_id: str, lug_id: str, impact: int):
    """
    Set notification flag in hub state for agent to pick up.

    Critical (impact 10): immediate alert
    High (impact 8-9): present at next closeout/wake

    Args:
        hub_path: Path to hub
        spoke_id: Source spoke
        lug_id: Lug ID
        impact: Impact level
    """
    state_file = hub_path / 'hub-state.json'

    # Load or create state
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text())
        except:
            state = {}
    else:
        state = {}

    # Initialize notifications structure
    if 'notifications' not in state:
        state['notifications'] = {}

    if spoke_id not in state['notifications']:
        state['notifications'][spoke_id] = {
            'pending_critical': [],
            'pending_high': []
        }

    # Add notification by impact level
    notification = {
        'lug_id': lug_id,
        'impact': impact,
        'timestamp': datetime.now().isoformat()
    }

    if impact >= 10:
        state['notifications'][spoke_id]['pending_critical'].append(notification)
    else:  # impact 8-9
        state['notifications'][spoke_id]['pending_high'].append(notification)

    # Save state
    try:
        state_file.write_text(json.dumps(state, indent=2))
    except:
        pass  # Fail silently


def check_hub_notifications(spoke_id: str, hub_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Check if hub has pending notifications for this spoke.
    Called at wakeup/closeout.

    Args:
        spoke_id: Spoke ID to check
        hub_path: Path to hub

    Returns:
        Dict with pending_critical and pending_high lists
    """
    if not hub_path:
        from .hub import discover_hub
        hub_path = discover_hub()
        if not hub_path:
            return {'pending_critical': [], 'pending_high': []}

    state_file = hub_path / 'hub-state.json'
    if not state_file.exists():
        return {'pending_critical': [], 'pending_high': []}

    try:
        state = json.loads(state_file.read_text())
        notifications = state.get('notifications', {}).get(spoke_id, {})
        return {
            'pending_critical': notifications.get('pending_critical', []),
            'pending_high': notifications.get('pending_high', [])
        }
    except:
        return {'pending_critical': [], 'pending_high': []}


def clear_hub_notification(spoke_id: str, lug_id: str, hub_path: Optional[Path] = None):
    """
    Clear a notification after it's been processed by agent.

    Args:
        spoke_id: Spoke ID
        lug_id: Lug ID to clear
        hub_path: Path to hub
    """
    if not hub_path:
        from .hub import discover_hub
        hub_path = discover_hub()
        if not hub_path:
            return

    state_file = hub_path / 'hub-state.json'
    if not state_file.exists():
        return

    try:
        state = json.loads(state_file.read_text())
        notifications = state.get('notifications', {}).get(spoke_id, {})

        # Remove from both lists
        for level in ['pending_critical', 'pending_high']:
            notifications[level] = [
                n for n in notifications.get(level, [])
                if n.get('lug_id') != lug_id
            ]

        state['notifications'][spoke_id] = notifications
        state_file.write_text(json.dumps(state, indent=2))
    except:
        pass  # Fail silently

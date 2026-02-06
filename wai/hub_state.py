"""
Hub State API for just-in-time agent context.

Provides current state: tool quotas, IDE preferences, notifications.
Spokes query on-demand (wakeup/closeout) to get fresh context.
Hub can push critical updates to notify all spokes.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Sentinel value to detect when expires_at was not provided
_NOT_PROVIDED = object()


def get_hub_state(hub_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Get current hub state for agent context.

    Returns:
        Dict with token usage, credits, preferences, recommendations, flags
    """
    if not hub_path:
        from .hub import discover_hub
        hub_path = discover_hub()
        if not hub_path:
            return {}  # No hub, return empty

    state_file = hub_path / 'hub-state.json'
    if not state_file.exists():
        # Initialize with defaults
        return initialize_hub_state(hub_path)

    try:
        state = json.loads(state_file.read_text())
        return state
    except:
        return initialize_hub_state(hub_path)


def initialize_hub_state(hub_path: Path) -> Dict[str, Any]:
    """
    Initialize hub state with default structure.

    Args:
        hub_path: Path to hub

    Returns:
        Initial state dict
    """
    state = {
        'tool_quotas': {
            '_schema': 'Each tool entry has: used, limit, expires_at (ISO or null for no expiry), message',
            '_example': {
                'amp': {
                    'used': 50,
                    'limit': 100,
                    'unit': 'requests',
                    'expires_at': '2026-02-06T11:00:00Z',
                    'message': 'Add credits or wait until next hour'
                }
            }
        },
        'ide_preferences': {
            '_note': 'Ordered list - no expiry, persists across sessions',
            'tools': [
                'Antigravity',
                'VS Code with AMP',
                'Claude Code Pro',
                'KiloCLI with Together.AI',
                'VS Code & Copilot',
                'VS Code & Cline'
            ],
            'last_updated': datetime.now().isoformat()
        },
        'tool_recommendations': {
            '_note': 'Context-aware tool suggestions',
            'recommendations': []
        },
        'pending_actions': {
            'ingest_ready': False,
            'high_priority_lugs': 0,
            'critical_lugs': 0
        },
        'notifications': {
            '_note': 'Hub broadcasts to all spokes when critical updates occur',
            'pending': []
        },
        'last_updated': datetime.now().isoformat()
    }

    # Save initial state
    state_file = hub_path / 'hub-state.json'
    try:
        state_file.write_text(json.dumps(state, indent=2))
    except:
        pass

    return state


def update_hub_state(updates: Dict[str, Any], hub_path: Optional[Path] = None):
    """
    Update hub state with new values.

    Args:
        updates: Dict of updates to apply (nested updates supported)
        hub_path: Path to hub
    """
    if not hub_path:
        from .hub import discover_hub
        hub_path = discover_hub()
        if not hub_path:
            return

    state = get_hub_state(hub_path)

    # Deep merge updates
    def deep_merge(base, updates):
        for key, value in updates.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                deep_merge(base[key], value)
            else:
                base[key] = value

    deep_merge(state, updates)
    state['last_updated'] = datetime.now().isoformat()

    # Save
    state_file = hub_path / 'hub-state.json'
    try:
        state_file.write_text(json.dumps(state, indent=2))
    except:
        pass


def format_hub_context_for_agent(hub_path: Optional[Path] = None) -> str:
    """
    Format hub state as human-readable context for agent display.

    Args:
        hub_path: Path to hub

    Returns:
        Formatted string for agent briefing (None if no relevant info)
    """
    state = get_hub_state(hub_path)
    if not state:
        return None

    # Clean up expired quotas first
    _cleanup_expired_quotas(state, hub_path)

    lines = []

    # Tool quotas (with expiry awareness)
    quotas = state.get('tool_quotas', {})
    for tool_name, quota_info in quotas.items():
        if tool_name.startswith('_'):  # Skip schema/example entries
            continue
        
        used = quota_info.get('used', 0)
        limit = quota_info.get('limit', 0)
        unit = quota_info.get('unit', 'units')
        expires_at = quota_info.get('expires_at')
        message = quota_info.get('message', '')

        if used > 0 or limit > 0:
            pct = int((used / limit * 100)) if limit > 0 else 0
            quota_str = f"{tool_name.upper()}: {used}/{limit} {unit} ({pct}%)"
            
            # Add expiry info if present
            if expires_at:
                try:
                    exp_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    now = datetime.now(exp_dt.tzinfo) if exp_dt.tzinfo else datetime.now()
                    time_left = exp_dt - now
                    if time_left.total_seconds() > 0:
                        hours = int(time_left.total_seconds() // 3600)
                        mins = int((time_left.total_seconds() % 3600) // 60)
                        if hours > 0:
                            quota_str += f" - resets in {hours}h {mins}m"
                        else:
                            quota_str += f" - resets in {mins}m"
                except:
                    pass

            # Add warning indicators
            if pct >= 90:
                quota_str = f"🚨 {quota_str}"
            elif pct >= 70:
                quota_str = f"⚠️  {quota_str}"
            
            # Add message if present
            if message:
                quota_str += f"\n   → {message}"
            
            lines.append(quota_str)

    # Pending notifications
    notifications = state.get('notifications', {}).get('pending', [])
    for notif in notifications:
        msg = notif.get('message', '')
        priority = notif.get('priority', 'normal')
        icon = '🚨' if priority == 'critical' else '📢'
        lines.append(f"{icon} {msg}")

    # Pending actions
    actions = state.get('pending_actions', {})
    if actions.get('ingest_ready'):
        lines.append("⚠️  Ingest folder ready for processing")
    if actions.get('critical_lugs', 0) > 0:
        lines.append(f"🚨 {actions['critical_lugs']} critical lug(s) pending")
    if actions.get('high_priority_lugs', 0) > 0:
        lines.append(f"📌 {actions['high_priority_lugs']} high-priority lug(s) pending")

    return "\n".join(lines) if lines else None


def check_ingest_pending(hub_path: Optional[Path] = None) -> bool:
    """
    Check if ingest folder has pending teachings.

    Args:
        hub_path: Path to hub

    Returns:
        True if ingest has .teaching files
    """
    if not hub_path:
        from .hub import discover_hub
        hub_path = discover_hub()
        if not hub_path:
            return False

    ingest_dir = hub_path / 'WAI-Spoke' / 'seed' / 'ingest'
    if not ingest_dir.exists():
        return False

    # Check for .teaching files
    teaching_files = list(ingest_dir.glob('*.teaching'))
    return len(teaching_files) > 0


def update_tool_quota(
    tool_name: str,
    used: Optional[int] = None,
    limit: Optional[int] = None,
    unit: str = 'requests',
    expires_at: Optional[str] = _NOT_PROVIDED,  # type: ignore
    message: Optional[str] = None,
    hub_path: Optional[Path] = None,
    notify_spokes: bool = True
) -> bool:
    """
    Update tool quota and optionally notify all spokes.

    Args:
        tool_name: Tool identifier (e.g., 'amp', 'claude_code')
        used: Current usage count
        limit: Maximum allowed usage
        unit: Unit of measurement (requests, tokens, etc.)
        expires_at: ISO timestamp when quota resets (None for no expiry, omit to keep current)
        message: Optional message to display (e.g., "Add credits or wait")
        hub_path: Path to hub
        notify_spokes: If True, push notification to all spokes

    Returns:
        True if updated successfully
    """
    if not hub_path:
        from .hub import discover_hub
        hub_path = discover_hub()
        if not hub_path:
            return False

    state = get_hub_state(hub_path)
    if not state:
        return False

    # Ensure tool_quotas exists
    if 'tool_quotas' not in state:
        state['tool_quotas'] = {}

    # Get existing quota or create new
    if tool_name not in state['tool_quotas']:
        state['tool_quotas'][tool_name] = {}

    quota = state['tool_quotas'][tool_name]

    # Update fields (only if provided, but allow None for expires_at)
    if used is not None:
        quota['used'] = used
    if limit is not None:
        quota['limit'] = limit
    if unit:
        quota['unit'] = unit
    # Set expires_at if explicitly provided (including None for non-expiring)
    if expires_at is not _NOT_PROVIDED:
        quota['expires_at'] = expires_at
    if message is not None:
        quota['message'] = message

    quota['last_updated'] = datetime.now().isoformat()

    # Save state
    state['last_updated'] = datetime.now().isoformat()
    state_file = hub_path / 'hub-state.json'
    try:
        state_file.write_text(json.dumps(state, indent=2))
    except:
        return False

    # Push notification if requested and quota is critical (>= 70%)
    if notify_spokes and used is not None and limit is not None and limit > 0:
        pct = (used / limit) * 100
        if pct >= 70:
            priority = 'critical' if pct >= 90 else 'high'
            notif_msg = f"{tool_name.upper()} quota: {used}/{limit} {unit} ({int(pct)}%)"
            if message:
                notif_msg += f" - {message}"
            push_notification(notif_msg, priority, hub_path)

    return True


def push_notification(message: str, priority: str = 'normal', hub_path: Optional[Path] = None):
    """
    Push notification to all spokes via hub-state.json.
    Spokes will see this on next wakeup/closeout.

    Args:
        message: Notification message
        priority: 'critical', 'high', or 'normal'
        hub_path: Path to hub
    """
    if not hub_path:
        from .hub import discover_hub
        hub_path = discover_hub()
        if not hub_path:
            return

    state = get_hub_state(hub_path)
    if not state:
        return

    # Ensure notifications structure exists
    if 'notifications' not in state:
        state['notifications'] = {}
    if 'pending' not in state['notifications']:
        state['notifications']['pending'] = []

    # Add notification
    notification = {
        'message': message,
        'priority': priority,
        'timestamp': datetime.now().isoformat(),
        'id': datetime.now().strftime('%Y%m%d%H%M%S')
    }

    state['notifications']['pending'].append(notification)
    state['last_updated'] = datetime.now().isoformat()

    # Save
    state_file = hub_path / 'hub-state.json'
    try:
        state_file.write_text(json.dumps(state, indent=2))
    except:
        pass


def clear_notification(notification_id: str, hub_path: Optional[Path] = None):
    """
    Clear a notification after spoke has acknowledged it.

    Args:
        notification_id: Notification ID to clear
        hub_path: Path to hub
    """
    if not hub_path:
        from .hub import discover_hub
        hub_path = discover_hub()
        if not hub_path:
            return

    state = get_hub_state(hub_path)
    if not state:
        return

    notifications = state.get('notifications', {}).get('pending', [])
    state['notifications']['pending'] = [
        n for n in notifications if n.get('id') != notification_id
    ]

    # Save
    state_file = hub_path / 'hub-state.json'
    try:
        state_file.write_text(json.dumps(state, indent=2))
    except:
        pass


def _cleanup_expired_quotas(state: Dict[str, Any], hub_path: Optional[Path] = None):
    """
    Remove expired quota entries from state.

    Args:
        state: Hub state dict (modified in place)
        hub_path: Path to hub (for saving)
    """
    quotas = state.get('tool_quotas', {})
    now = datetime.now()
    expired = []

    for tool_name, quota_info in quotas.items():
        if tool_name.startswith('_'):  # Skip schema entries
            continue
        
        expires_at = quota_info.get('expires_at')
        if expires_at:
            try:
                exp_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                exp_dt_naive = exp_dt.replace(tzinfo=None) if exp_dt.tzinfo else exp_dt
                if exp_dt_naive < now:
                    expired.append(tool_name)
            except:
                pass

    # Remove expired quotas
    if expired:
        for tool_name in expired:
            del state['tool_quotas'][tool_name]
        
        # Save if hub_path provided
        if hub_path:
            state_file = hub_path / 'hub-state.json'
            try:
                state['last_updated'] = datetime.now().isoformat()
                state_file.write_text(json.dumps(state, indent=2))
            except:
                pass

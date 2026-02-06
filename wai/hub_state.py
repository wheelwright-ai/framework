"""
Hub State API for just-in-time agent context.

Provides current state: token usage, credits, IDE preferences, tool recommendations, pending actions.
Spokes query on-demand (wakeup/closeout) to get fresh context.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


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
        'claude_code': {
            'used_pct': 0,
            'used_tokens': 0,
            'limit': 200000,
            'resets_at': None,
            'timezone': 'America/Los_Angeles',
            'timestamp': datetime.now().isoformat()
        },
        'antigravity': {
            'used_today': 0,
            'daily_limit': 10,
            'timestamp': datetime.now().isoformat()
        },
        'ide_preferences': [
            'Antigravity',
            'VS Code with AMP',
            'Claude Code Pro',
            'KiloCLI with Together.AI',
            'VS Code & Copilot',
            'VS Code & Cline'
        ],
        'tool_recommendations': {
            'kilo_cli': 'strong paid performance alternative recently'
        },
        'pending_actions': {
            'ingest_ready': False,
            'high_priority_lugs': 0,
            'critical_lugs': 0
        },
        'notifications': {},
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
        Formatted string for agent briefing
    """
    state = get_hub_state(hub_path)
    if not state:
        return ""

    lines = []

    # Token usage
    cc = state.get('claude_code', {})
    if cc.get('used_pct', 0) > 0:
        resets = cc.get('resets_at', 'unknown')
        lines.append(f"Claude Code: {cc['used_pct']}% used (resets {resets})")

    # Antigravity credits
    ag = state.get('antigravity', {})
    if ag.get('used_today', 0) > 0 or ag.get('daily_limit', 0) > 0:
        lines.append(f"Antigravity: ${ag['used_today']}/${ag['daily_limit']} daily credits used")

    # Pending actions
    actions = state.get('pending_actions', {})
    if actions.get('ingest_ready'):
        lines.append("⚠ Ingest folder ready for processing")
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

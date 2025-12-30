"""
Status Command

Display spoke status information.
"""

import json
from pathlib import Path
from typing import Optional


def show_status(path: str = '.') -> None:
    """
    Show spoke status.

    Args:
        path: Path to spoke project (default: current directory)
    """
    project_path = Path(path).expanduser().resolve()
    wai_dir = project_path / 'WAI-Spoke'

    if not wai_dir.exists():
        print(f"\n    No spoke found at: {project_path}")
        print(f"   Run 'WAI init' to create one")
        return

    # Load state
    state_path = wai_dir / 'WAI-State.json'
    if not state_path.exists():
        print(f"    Spoke directory exists but WAI-State.json missing")
        return

    try:
        with open(state_path, encoding='utf-8') as f:
            state = json.load(f)
    except Exception as e:
        print(f"    Error loading WAI-State.json: {e}")
        return

    # Display status
    wheel = state.get('wheel', {})
    foundation = state.get('_project_foundation', {})
    session = state.get('_session_state', {})
    wai_meta = state.get('wheelwright', {})

    print(f"\n    Wheelwright Status")
    print(f"   " + "=" * 50)

    print(f"\n    Spoke: {wheel.get('name', project_path.name)}")
    if wheel.get('type'):
        print(f"   Type: {wheel['type']}")
    if foundation.get('identity', {}).get('one_liner'):
        print(f"   Description: {foundation['identity']['one_liner']}")

    print(f"\n    Foundation:")
    if foundation.get('completed'):
        print(f"   ✓ Complete")
    else:
        print(f"   ⚠ Incomplete - needs setup")

    print(f"\n    Session State:")
    print(f"   Last modified by: {session.get('last_modified_by', 'Unknown')}")
    print(f"   Sessions: {session.get('session_count', 0)}")

    if wai_meta.get('hub_path'):
        print(f"\n    Hub: {wai_meta['hub_path']}")
    else:
        print(f"\n    Hub: Not connected")

    # Check signals
    signals_path = wai_dir / 'WAI-Signals.jsonl'
    if signals_path.exists():
        try:
            signal_count = sum(1 for line in open(signals_path, encoding='utf-8') if line.strip())
            if signal_count > 0:
                print(f"\n    Signals: {signal_count} high-impact learnings recorded")
        except:
            pass

    print()  # Final newline

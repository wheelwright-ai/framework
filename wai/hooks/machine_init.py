"""
Session Initialization Hook - Machine Optimization Check

This hook runs at session start to ensure the IDE is optimized for the current machine.

Called from:
- wai wakeup
- wai init
- Session start in CLI
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime, timezone

from ..skills.machine_detect import MachineDetector
from ..skills.ide_optimize import IDEOptimizationAdvisor


def check_machine_optimization(project_root: Path, silent: bool = False) -> Dict[str, Any]:
    """Check and apply machine optimizations at session start.

    Args:
        project_root: Root directory of the project
        silent: If True, suppress output messages

    Returns:
        dict with status information
    """
    result = {
        'machine_id': None,
        'classification': None,
        'optimized': False,
        'applied': False,
        'message': None
    }

    try:
        detector = MachineDetector()
        advisor = IDEOptimizationAdvisor(project_root)

        # Load or create machine profile
        profile = advisor.load_machine_profile()

        if not profile:
            if not silent:
                print("⚡ First time on this machine - creating profile...")
            profile = detector.create_lug()
            result['message'] = "New machine profile created"

        result['machine_id'] = profile['machine']['id']
        result['classification'] = profile['machine']['classification']

       # Check and auto-apply optimizations
        if advisor.check_and_auto_apply(silent=silent):
            result['applied'] = True
            result['optimized'] = True
            result['message'] = f"IDE optimized for {result['classification']} machine"
        else:
            result['optimized'] = True
            result['message'] = "IDE already optimized"

    except Exception as e:
        result['message'] = f"Optimization check failed: {str(e)}"
        if not silent:
            print(f"⚠️  {result['message']}")

    return result


def get_machine_status(project_root: Path) -> Optional[Dict[str, Any]]:
    """Get current machine optimization status for briefing/display.

    Returns:
        dict with machine info and optimization status, or None if unavailable
    """
    try:
        detector = MachineDetector()
        hub_path = project_root.parent / 'hub' / 'machines' / f'{detector.hostname}.lug.json'

        if not hub_path.exists():
            return None

        with open(hub_path, 'r') as f:
            profile = json.load(f)

        # Check last optimization
        history = profile.get('optimization_history', {})
        last_check = history.get('last_check')
        last_applied = history.get('last_applied')

        # Calculate time since last check
        time_since = None
        if last_check:
            last_dt = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
            delta = datetime.now(timezone.utc) - last_dt
            hours = delta.total_seconds() / 3600
            if hours < 1:
                time_since = f"{int(delta.total_seconds() / 60)} minutes ago"
            elif hours < 24:
                time_since = f"{int(hours)} hours ago"
            else:
                time_since = f"{int(hours / 24)} days ago"

        return {
            'machine_id': profile['machine']['id'],
            'classification': profile['machine']['classification'],
            'cpu_model': profile['machine']['specs']['cpu']['model'],
            'ram_gb': profile['machine']['specs']['memory']['total_gb'],
            'gpu_available': profile['machine']['specs']['gpu']['available'],
            'last_check': last_check,
            'last_applied': last_applied,
            'time_since_check': time_since,
            'projects_optimized': history.get('projects_optimized', []),
            'total_optimizations': history.get('total_optimizations', 0)
        }

    except Exception:
        return None


def format_machine_status_brief() -> str:
    """Format machine status for session briefing.

    Returns:
        Markdown-formatted machine status section
    """
    try:
        project_root = Path.cwd()
        status = get_machine_status(project_root)

        if not status:
            return "🖥️  **Machine:** Not profiled yet\n"

        lines = []
        lines.append(f"🖥️  **Machine:** {status['machine_id']} ({status['classification'].upper()})")
        lines.append(f"   RAM: {status['ram_gb']} GB | CPU: {status['cpu_model'][:40]}...")

        if status['last_check']:
            time_str = status['time_since_check'] or 'recently'
            lines.append(f"   Last optimized: {time_str}")

        if status['total_optimizations'] > 0:
            lines.append(f"   Projects optimized: {len(status['projects_optimized'])}")

        return '\n'.join(lines)

    except Exception:
        return "🖥️  **Machine:** Status unavailable\n"


def format_machine_status_detail() -> str:
    """Format detailed machine status for CLI display.

    Returns:
        Formatted machine status with full details
    """
    try:
        project_root = Path.cwd()
        status = get_machine_status(project_root)

        if not status:
            return "\n🖥️  Machine profile not found. Run 'wai detect-machine --save-to-hub'\n"

        lines = []
        lines.append("\n" + "=" * 60)
        lines.append("🖥️  MACHINE STATUS")
        lines.append("=" * 60)
        lines.append(f"Machine ID: {status['machine_id']}")
        lines.append(f"Classification: {status['classification'].upper()}")
        lines.append(f"CPU: {status['cpu_model']}")
        lines.append(f"RAM: {status['ram_gb']} GB")
        lines.append(f"GPU: {'Available' if status['gpu_available'] else 'Not available'}")
        lines.append("")
        lines.append("OPTIMIZATION STATUS:")

        if status['last_check']:
            time_str = status['time_since_check'] or 'just now'
            lines.append(f"  Last check: {time_str}")
        else:
            lines.append(f"  Last check: Never")

        lines.append(f"  Projects optimized: {len(status['projects_optimized'])}")
        lines.append(f"  Total optimizations: {status['total_optimizations']}")

        if status['projects_optimized']:
            lines.append("")
            lines.append("  Optimized projects:")
            for proj in status['projects_optimized'][:5]:
                lines.append(f"    • {proj}")
            if len(status['projects_optimized']) > 5:
                lines.append(f"    ... and {len(status['projects_optimized']) - 5} more")

        lines.append("=" * 60)
        lines.append("")

        return '\n'.join(lines)

    except Exception as e:
        return f"\n⚠️  Error getting machine status: {e}\n"

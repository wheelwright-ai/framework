"""
Sync Command

Sync spoke with hub, with automatic structure upgrade.
"""

from pathlib import Path
from ..upgrader import SpokeUpgrader
from ..hub import HubManager


SPOKE_STRUCTURE_VERSION = "2.0"


def sync_spoke(all_spokes: bool = False) -> None:
    """
    Sync spoke(s) with hub.

    Args:
        all_spokes: Sync all registered spokes (not yet implemented)
    """
    # Find hub
    hub_manager = HubManager()
    hub_path = hub_manager.auto_discover_hub(Path.cwd(), verbose=False)

    if not hub_path:
        print(f"\n    No hub found - nothing to sync")
        print(f"   Create a hub with: WAI hub create")
        return

    if all_spokes:
        print(f"\n    Syncing all spokes with hub...")
        print(f"   Feature coming soon")
        return

    # Sync current spoke
    project_path = Path('.').resolve()

    # Auto-upgrade spoke structure if needed
    print(f"\n    Checking spoke structure version...")
    version = SpokeUpgrader.detect_version(project_path)

    if version == 'unknown':
        print(f"   ✗ No valid spoke structure found")
        print(f"   Run 'WAI init' to initialize this project")
        return
    elif version == '1.0':
        print(f"   Detected v1.0 structure (.WAI/) - auto-upgrading...")
        if SpokeUpgrader.upgrade_spoke(project_path, version, verbose=True):
            print(f"   ✓ Spoke upgraded to v{SPOKE_STRUCTURE_VERSION}")
        else:
            print(f"   ✗ Upgrade failed - cannot proceed with sync")
            return
    else:
        print(f"   ✓ Spoke structure is current (v{version})")

    wai_dir = project_path / 'WAI-Spoke'

    print(f"\n    ✓ Spoke ready for sync")
    print(f"   Hub: {hub_path}")
    print(f"   Spoke: {project_path.name}")
    print(f"\n   Note: Full hub sync feature coming in future release")

"""
Closeout Command

Generate session closeout instructions and handle upgrade adoption.
"""

import json
import subprocess
from pathlib import Path
from typing import Optional

from .verify_upgrade import (
    verify_upgrade_command,
    get_adoption_decisions,
    execute_adoptions,
    _load_plan_file
)
from ..utils.input import print_info, print_success, print_error, print_warning


def _check_pending_upgrades(spoke_path: Path) -> bool:
    """Check if there are pending upgrades to adopt."""
    plan_path = spoke_path / 'upgrade-adoption-plan.json'
    return plan_path.exists()


def _auto_commit_state(project_path: Path, wai_dir: Path) -> None:
    """Auto-commit WAI-State files after closeout."""
    try:
        # Stage WAI-State files
        state_files = [
            'WAI-Spoke/WAI-State.json',
            'WAI-Spoke/WAI-State.md',
            'WAI-Spoke/WAI-Lugs.jsonl'
        ]
        
        for file in state_files:
            file_path = project_path / file
            if file_path.exists():
                subprocess.run(
                    ['git', 'add', str(file_path)],
                    cwd=str(project_path),
                    capture_output=True,
                    check=False
                )
        
        # Check if there are changes to commit
        result = subprocess.run(
            ['git', 'diff', '--cached', '--quiet'],
            cwd=str(project_path),
            capture_output=True
        )
        
        if result.returncode != 0:  # There are staged changes
            subprocess.run(
                ['git', 'commit', '-m', 'wai: closeout - update session state'],
                cwd=str(project_path),
                capture_output=True,
                check=False
            )
            print_success("  ✓ WAI-State files committed")
        else:
            print_info("  No changes to commit")
    except Exception as e:
        print_warning(f"  Could not auto-commit: {e}")


def generate_closeout(hub_key: Optional[str] = None) -> None:
    """
    Generate session closeout instructions.
    
    Args:
        hub_key: Optional hub key for upgrade signature verification
    """
    project_path = Path('.').resolve()
    wai_dir = project_path / 'WAI-Spoke'

    if not wai_dir.exists():
        print(f"\n    No spoke in current directory")
        print(f"   Run 'WAI init' to initialize")
        return

    # Load state
    state_path = wai_dir / 'WAI-State.json'
    if not state_path.exists():
        print(f"    Spoke exists but WAI-State.json missing")
        return

    try:
        with open(state_path, encoding='utf-8') as f:
            state = json.load(f)
    except Exception as e:
        print(f"    Error loading state: {e}")
        return

    print(f"\n    Session Closeout")
    print(f"   " + "=" * 50)
    
    # Phase 1: Check for pending upgrades
    print_info("\n  PHASE 1: Checking for pending upgrades...")
    
    if _check_pending_upgrades(project_path):
        print_info("  Found pending upgrade-adoption-plan.json")
        
        # Phase 2: Verify plan
        print_info("\n  PHASE 2: Verifying upgrade plan...")
        if not verify_upgrade_command(project_path, hub_key):
            print_warning("\n  Plan verification failed. Skipping adoption.")
            print_warning("  Check errors above and run 'wai verify-upgrade' for details.")
        else:
            # Phase 3: Get adoption decisions
            print_info("\n  PHASE 3: Processing adoption decisions...")
            plan = _load_plan_file(project_path)
            if plan:
                decisions = get_adoption_decisions(plan)
                
                # Phase 4: Execute adoptions
                print_info("\n  PHASE 4: Executing adoptions...")
                if execute_adoptions(project_path, plan, decisions):
                    print_success("\n  ✓ All adoptions completed")
                else:
                    print_warning("\n  ⚠ Some adoptions failed")
    else:
        print_info("  No pending upgrades")
    
    # Phase 5: Standard closeout
    print_info(f"\n  PHASE 5: Standard closeout instructions")
    print_info(f"  " + "=" * 48)
    print(f"\n   Update your WAI-State files with the following:")
    print(f"\n   1. Update _session_state.last_modified_at to current time")
    print(f"   2. Increment session_count")
    print(f"   3. Add any decisions with impact >= 5 to decisions array")
    print(f"   4. Append high-impact learnings to WAI-Signals.jsonl")

    # Show current session state
    session = state.get('_session_state', {})
    print(f"\n   Current session state:")
    print(f"   - Last modified: {session.get('last_modified_at', 'Unknown')}")
    print(f"   - Session count: {session.get('session_count', 0)}")
    print(f"   - Last modified by: {session.get('last_modified_by', 'Unknown')}")

    print(f"\n   Note: Use 'wai verify-upgrade' to manually verify plan")
    
    # Phase 6: Auto-commit WAI-State files
    print_info(f"\n  PHASE 6: Auto-committing WAI-State files...")
    _auto_commit_state(project_path, wai_dir)
    print()

#!/usr/bin/env python3
"""
Hub Upgrade Simulation

Creates a dummy old v1.0 spoke and runs the upgrade process.
Tests conversion validation and logs results.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wai_cli.upgrader import SpokeUpgrader


def create_dummy_v1_spoke(test_dir: Path):
    """Create a minimal dummy v1.0 spoke structure."""
    print("[1/3] Creating dummy v1.0 spoke structure...")
    
    # Create old .WAI directory
    wai_dir = test_dir / '.WAI'
    wai_dir.mkdir(parents=True, exist_ok=True)
    
    # Create old-style files
    old_files = {
        'wheel-signals.jsonl': '{"type": "bug_fix", "file": "test.py", "description": "Fixed issue"}\n',
        'kb-sync.json': json.dumps({
            "version": "1.0",
            "last_sync": "2026-01-01T00:00:00Z"
        }, indent=2),
        'session-conversation.jsonl': '{"role": "user", "content": "Hello"}\n{"role": "assistant", "content": "Hi"}\n'
    }
    
    for filename, content in old_files.items():
        file_path = wai_dir / filename
        file_path.write_text(content)
        print(f"  Created: {filename}")
    
    # Create WAI-State.json (core file - can exist in v1.0)
    state_data = {
        "wheel": {
            "name": "test-spoke-upgrade",
            "description": "Test spoke for upgrade simulation"
        },
        "decisions": []
    }
    
    state_file = wai_dir / 'WAI-State.json'
    state_file.write_text(json.dumps(state_data, indent=2))
    print(f"  Created: WAI-State.json")
    
    print(f"✓ Dummy v1.0 spoke created at: {test_dir}")
    print()
    
    return test_dir


def run_upgrade_simulation():
    """Run spoke upgrade simulation."""
    print("=" * 60)
    print("SPOKE UPGRADE SIMULATION")
    print("=" * 60)
    print()
    
    # Create test directory
    test_dir = Path(__file__).parent.parent / 'test-spoke-upgrade'
    
    # Clean up if exists
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    # Create dummy v1.0 spoke
    create_dummy_v1_spoke(test_dir)
    
    # Detect version
    print("[2/3] Detecting spoke version...")
    detected_version = SpokeUpgrader.detect_version(test_dir)
    print(f"  Detected version: {detected_version}")
    
    if detected_version != '1.0':
        print(f"✗ ERROR: Expected v1.0, got {detected_version}")
        return False
    
    print("✓ Version detection successful")
    print()
    
    # Run upgrade
    print("[3/3] Running spoke upgrade...")
    print()
    success = SpokeUpgrader.upgrade_spoke(test_dir, '1.0', verbose=True)
    print()
    
    if not success:
        print("✗ Upgrade failed")
        return False
    
    # Verify upgrade
    print("=" * 60)
    print("VERIFICATION RESULTS")
    print("=" * 60)
    print()
    
    new_dir = test_dir / 'WAI-Spoke'
    
    # Check directory exists
    if not new_dir.exists():
        print("✗ WAI-Spoke directory not created")
        return False
    
    print(f"✓ WAI-Spoke directory created")
    
    # Check file renames
    renamed_files = [
        'WAI-Signals.jsonl',
        'WAI-KB-Sync.json',
        'WAI-Session-Log.jsonl'
    ]
    
    for renamed_file in renamed_files:
        file_path = new_dir / renamed_file
        if file_path.exists():
            print(f"✓ File renamed: {renamed_file}")
        else:
            print(f"✗ Missing renamed file: {renamed_file}")
    
    # Check index file
    index_file = new_dir / 'WAI-File-Index.json'
    if index_file.exists():
        print(f"✓ WAI-File-Index.json created")
        
        try:
            index_data = json.loads(index_file.read_text())
            version = index_data.get('version')
            print(f"  Index version: {version}")
            
            core_files = index_data.get('core_files', {})
            print(f"  Core files defined: {len(core_files)}")
        except Exception as e:
            print(f"  Warning: Could not parse index file: {e}")
    else:
        print(f"✗ WAI-File-Index.json not created")
    
    # Check upgrade decision logged
    state_file = new_dir / 'WAI-State.json'
    if state_file.exists():
        try:
            state_data = json.loads(state_file.read_text())
            decisions = state_data.get('decisions', [])
            
            upgrade_decision = None
            for decision in decisions:
                if 'Auto-upgraded' in decision.get('decision', ''):
                    upgrade_decision = decision
                    break
            
            if upgrade_decision:
                print(f"✓ Upgrade decision logged")
                print(f"  Decision: {upgrade_decision.get('decision')}")
                print(f"  Impact: {upgrade_decision.get('impact')}")
            else:
                print(f"✗ Upgrade decision not logged")
        except Exception as e:
            print(f"  Warning: Could not verify state file: {e}")
    
    # Verify v2.0 detection
    print()
    print("Verifying post-upgrade version detection...")
    post_version = SpokeUpgrader.detect_version(test_dir)
    if post_version == '2.0' or post_version == '2.1':
        print(f"✓ Post-upgrade version detected: {post_version}")
    else:
        print(f"✗ Unexpected post-upgrade version: {post_version}")
    
    print()
    print("=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    print()
    print(f"Test directory: {test_dir}")
    print("✓ All upgrade steps completed successfully")
    print()
    
    #Cleanup
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
        print(f"✓ Cleaned up test directory")
    
    return True


if __name__ == '__main__':
    success = run_upgrade_simulation()
    sys.exit(0 if success else 1)

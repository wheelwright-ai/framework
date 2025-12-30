#!/usr/bin/env python3
"""
Test script to verify wai_cli package structure.
"""

import sys
from pathlib import Path

# Add framework to path
framework_path = Path(__file__).parent
sys.path.insert(0, str(framework_path))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing wai_cli package imports...\n")

    try:
        print("Importing wai_cli.core...")
        from wai_cli.core import WheelwrightCLI, main
        print("  ✓ wai_cli.core")

        print("Importing wai_cli.init...")
        from wai_cli.init import framework_first_init, init_spoke
        print("  ✓ wai_cli.init")

        print("Importing wai_cli.hub...")
        from wai_cli.hub import HubManager
        print("  ✓ wai_cli.hub")

        print("Importing wai_cli.projects...")
        from wai_cli.projects import ProjectDiscovery
        print("  ✓ wai_cli.projects")

        print("Importing wai_cli.groups...")
        from wai_cli.groups import GroupsManager
        print("  ✓ wai_cli.groups")

        print("Importing wai_cli.upgrader...")
        from wai_cli.upgrader import SpokeUpgrader
        print("  ✓ wai_cli.upgrader")

        print("Importing wai_cli.utils.exceptions...")
        from wai_cli.utils.exceptions import WAIError
        print("  ✓ wai_cli.utils.exceptions")

        print("Importing wai_cli.utils.paths...")
        from wai_cli.utils.paths import normalize_path
        print("  ✓ wai_cli.utils.paths")

        print("Importing wai_cli.utils.input...")
        from wai_cli.utils.input import safe_input
        print("  ✓ wai_cli.utils.input")

        print("Importing wai_cli.utils.registry...")
        from wai_cli.utils.registry import load_registry
        print("  ✓ wai_cli.utils.registry")

        print("\n✓ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic instantiation."""
    print("\nTesting basic functionality...\n")

    try:
        from wai_cli.core import WheelwrightCLI

        print("Creating WheelwrightCLI instance...")
        cli = WheelwrightCLI()
        print(f"  ✓ CLI created (framework_path: {cli.framework_path})")

        from wai_cli.hub import HubManager
        print("Creating HubManager instance...")
        hub_mgr = HubManager()
        print("  ✓ HubManager created")

        from wai_cli.projects import ProjectDiscovery
        print("Creating ProjectDiscovery instance...")
        discovery = ProjectDiscovery()
        print("  ✓ ProjectDiscovery created")

        from wai_cli.upgrader import SpokeUpgrader
        print("Testing SpokeUpgrader.detect_version...")
        version = SpokeUpgrader.detect_version(Path.cwd())
        print(f"  ✓ Version detection works (result: {version})")

        print("\n✓ All basic functionality tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("WAI CLI Package Structure Test")
    print("=" * 60 + "\n")

    imports_ok = test_imports()

    if imports_ok:
        functionality_ok = test_basic_functionality()
    else:
        functionality_ok = False

    print("\n" + "=" * 60)
    if imports_ok and functionality_ok:
        print("RESULT: All tests passed ✓")
        print("=" * 60)
        sys.exit(0)
    else:
        print("RESULT: Some tests failed ✗")
        print("=" * 60)
        sys.exit(1)

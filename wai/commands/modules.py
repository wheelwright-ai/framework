"""
Module version management commands.

Provides CLI commands for viewing and managing module versions,
checking adoption state, and identifying modules needing attention.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple


def load_module_versions(framework_dir: Path) -> Dict[str, Any]:
    """Load framework module version definitions"""
    versions_path = framework_dir / "wai" / "module_versions.json"
    if not versions_path.exists():
        return {}
    with open(versions_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_spoke_module_versions(spoke_dir: Path) -> Dict[str, Any]:
    """Load spoke's module adoption state"""
    versions_path = spoke_dir / "WAI-Module-Versions.json"
    if not versions_path.exists():
        return {}
    with open(versions_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_dirty_modules(spoke_versions: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    """Get modules with pending changes (dirty status)"""
    adopted = spoke_versions.get("adopted_modules", {})
    dirty = []
    for module_name, info in adopted.items():
        if info.get("status") == "dirty":
            dirty.append((module_name, info))
    return dirty


def get_clean_modules(spoke_versions: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    """Get modules with no pending changes (clean status)"""
    adopted = spoke_versions.get("adopted_modules", {})
    clean = []
    for module_name, info in adopted.items():
        if info.get("status") == "clean":
            clean.append((module_name, info))
    return clean


def get_behind_modules(spoke_versions: Dict[str, Any], framework_versions: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """Get modules where spoke is behind framework version"""
    adopted = spoke_versions.get("adopted_modules", {})
    framework_modules = framework_versions.get("modules", {})
    behind = []

    for module_name, info in adopted.items():
        spoke_version = info.get("clean_version", info.get("version", "0.0"))
        if "-" in spoke_version:
            spoke_version = spoke_version.split("-")[0]  # Get clean version

        framework_module = framework_modules.get(module_name, {})
        framework_version = framework_module.get("version", spoke_version)

        if spoke_version != framework_version:
            behind.append((module_name, spoke_version, framework_version))

    return behind


def cmd_modules_status(spoke_dir: Path, framework_dir: Path):
    """Show module adoption status for this spoke"""
    spoke_versions = load_spoke_module_versions(spoke_dir)
    framework_versions = load_module_versions(framework_dir)

    if not spoke_versions:
        print("⚠️  No module versions file found (WAI-Module-Versions.json)")
        print("   Run 'wai init' or create file manually")
        return

    spoke_id = spoke_versions.get("spoke_id", "unknown")
    spoke_name = spoke_versions.get("spoke_name", "Unknown Spoke")
    framework_version = spoke_versions.get("framework_version", "unknown")

    print(f"\n{'=' * 60}")
    print(f"Module Versions - {spoke_name}")
    print(f"{'=' * 60}")
    print(f"Spoke ID: {spoke_id}")
    print(f"Framework: {framework_version}")
    print()

    # Show dirty modules first (need attention)
    dirty = get_dirty_modules(spoke_versions)
    if dirty:
        print("🟡 DIRTY MODULES (Pending Changes - Need Attention)")
        print("-" * 60)
        for module_name, info in dirty:
            version = info.get("version", "unknown")
            local_changes = info.get("local_changes", 0)
            pending_count = len(info.get("pending_lugs", []))
            print(f"  {module_name}: {version}")
            print(f"    Local changes: {local_changes}")
            print(f"    Pending lugs: {pending_count}")
        print()

    # Show behind modules (updates available)
    behind = get_behind_modules(spoke_versions, framework_versions)
    if behind:
        print("🔵 BEHIND (Updates Available)")
        print("-" * 60)
        for module_name, spoke_ver, framework_ver in behind:
            print(f"  {module_name}: {spoke_ver} → {framework_ver} available")
        print()

    # Show clean modules
    clean = get_clean_modules(spoke_versions)
    if clean:
        print("✅ CLEAN (Up-to-Date)")
        print("-" * 60)
        for module_name, info in clean:
            version = info.get("version", "unknown")
            print(f"  {module_name}: {version}")
        print()

    # Summary
    total = len(spoke_versions.get("adopted_modules", {}))
    print(f"Summary: {len(dirty)} dirty, {len(behind)} behind, {len(clean)} clean (of {total} total)")
    print()

    if dirty:
        print("💡 Tip: Run 'wai closeout' to submit pending changes to hub")
    if behind:
        print("💡 Tip: Run 'wai teach' to receive latest module updates")


def cmd_modules_list(spoke_dir: Path, framework_dir: Path):
    """List all tracked modules with versions"""
    framework_versions = load_module_versions(framework_dir)

    if not framework_versions:
        print("⚠️  No module versions found in framework")
        return

    modules = framework_versions.get("modules", {})

    print(f"\n{'=' * 60}")
    print("Available Modules")
    print(f"{'=' * 60}")
    print()

    for module_name, info in sorted(modules.items()):
        version = info.get("version", "unknown")
        released = info.get("released", "unknown")
        description = info.get("description", "No description")

        print(f"📦 {module_name} v{version}")
        print(f"   Released: {released}")
        print(f"   {description}")

        breaking = info.get("breaking_changes", [])
        if breaking:
            print(f"   ⚠️  Breaking changes: {len(breaking)}")
        print()


def cmd_modules_show(module_name: str, spoke_dir: Path, framework_dir: Path):
    """Show detailed information about a specific module"""
    framework_versions = load_module_versions(framework_dir)
    spoke_versions = load_spoke_module_versions(spoke_dir)

    framework_module = framework_versions.get("modules", {}).get(module_name)
    if not framework_module:
        print(f"❌ Module '{module_name}' not found in framework")
        return

    spoke_module = spoke_versions.get("adopted_modules", {}).get(module_name)

    print(f"\n{'=' * 60}")
    print(f"Module: {module_name}")
    print(f"{'=' * 60}")
    print()

    # Framework version
    print(f"Framework Version: {framework_module.get('version', 'unknown')}")
    print(f"Released: {framework_module.get('released', 'unknown')}")
    print(f"Description: {framework_module.get('description', 'No description')}")
    print()

    # Breaking changes
    breaking = framework_module.get("breaking_changes", [])
    if breaking:
        print("Breaking Changes:")
        for change in breaking:
            print(f"  - {change}")
        print()

    # Files
    files = framework_module.get("files", [])
    if files:
        print("Files:")
        for file in files:
            print(f"  - {file}")
        print()

    # Git commits
    commits = framework_module.get("git_commits", [])
    if commits:
        print(f"Git Commits: {', '.join(commits)}")
        print()

    # Spoke adoption state
    if spoke_module:
        print("Spoke Adoption:")
        print(f"  Version: {spoke_module.get('version', 'not adopted')}")
        print(f"  Status: {spoke_module.get('status', 'unknown')}")
        print(f"  Adopted: {spoke_module.get('adopted_at', 'unknown')}")

        if spoke_module.get("status") == "dirty":
            local_changes = spoke_module.get("local_changes", 0)
            pending_lugs = spoke_module.get("pending_lugs", [])
            print(f"  Local changes: {local_changes}")
            print(f"  Pending lugs: {len(pending_lugs)}")
            if pending_lugs:
                print("  Lug IDs:")
                for lug_id in pending_lugs[:5]:  # Show first 5
                    print(f"    - {lug_id[:12]}...")
                if len(pending_lugs) > 5:
                    print(f"    ... and {len(pending_lugs) - 5} more")
    else:
        print("Spoke Adoption: Not yet adopted")

    print()


def cmd_modules_pending(spoke_dir: Path):
    """Show all pending lugs awaiting hub submission"""
    spoke_versions = load_spoke_module_versions(spoke_dir)

    if not spoke_versions:
        print("⚠️  No module versions file found")
        return

    dirty = get_dirty_modules(spoke_versions)

    if not dirty:
        print("✅ No pending changes - all modules clean!")
        return

    print(f"\n{'=' * 60}")
    print("Pending Changes (Awaiting Hub Submission)")
    print(f"{'=' * 60}")
    print()

    total_changes = 0
    total_lugs = 0

    for module_name, info in dirty:
        version = info.get("version", "unknown")
        local_changes = info.get("local_changes", 0)
        pending_lugs = info.get("pending_lugs", [])

        total_changes += local_changes
        total_lugs += len(pending_lugs)

        print(f"📦 {module_name} ({version})")
        print(f"   Changes: {local_changes}")
        print(f"   Pending lugs: {len(pending_lugs)}")

        if pending_lugs:
            print("   Lug IDs:")
            for lug_id in pending_lugs[:3]:  # Show first 3
                print(f"     - {lug_id[:12]}...")
            if len(pending_lugs) > 3:
                print(f"     ... and {len(pending_lugs) - 3} more")
        print()

    print(f"Total: {total_changes} changes across {len(dirty)} modules ({total_lugs} lugs)")
    print()
    print("💡 Run 'wai closeout' to submit these changes to the hub")


def main():
    """CLI entry point for module commands"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: wai modules <command>")
        print()
        print("Commands:")
        print("  status              Show module adoption status")
        print("  list                List all available modules")
        print("  show <module>       Show detailed module information")
        print("  pending             Show pending changes awaiting hub submission")
        return

    command = sys.argv[1]
    spoke_dir = Path.cwd() / "WAI-Spoke"
    framework_dir = Path(__file__).parent.parent.parent  # Go up to framework root

    if command == "status":
        cmd_modules_status(spoke_dir, framework_dir)
    elif command == "list":
        cmd_modules_list(spoke_dir, framework_dir)
    elif command == "show":
        if len(sys.argv) < 3:
            print("Error: Module name required")
            print("Usage: wai modules show <module_name>")
            return
        module_name = sys.argv[2]
        cmd_modules_show(module_name, spoke_dir, framework_dir)
    elif command == "pending":
        cmd_modules_pending(spoke_dir)
    else:
        print(f"Unknown command: {command}")
        print("Run 'wai modules' for usage")


if __name__ == "__main__":
    main()

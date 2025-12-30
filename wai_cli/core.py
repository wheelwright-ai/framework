"""
WAI CLI Core

Main CLI entry point with command routing and error handling.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from .init import framework_first_init, init_spoke_interactive, check_spoke_initialized
from .hub import HubManager
from .projects import ProjectDiscovery
from .groups import GroupsManager
from .utils.input import print_info, print_success, print_error, safe_menu_choice
from .utils.exceptions import WAIError
from .utils.paths import normalize_path


# Framework version
FRAMEWORK_VERSION = "2.0.0"
SPOKE_STRUCTURE_VERSION = "2.0"


class WheelwrightCLI:
    """Main CLI class for Wheelwright."""

    def __init__(self):
        """Initialize CLI."""
        self.framework_path = Path(__file__).parent.parent.resolve()

    def run(self):
        """Main entry point with command routing."""
        parser = self._create_parser()
        args = parser.parse_args()

        # Handle no command - context detection
        if not args.command:
            self._handle_no_command()
            return

        # Route to command handlers
        try:
            self._route_command(args, parser)
        except KeyboardInterrupt:
            print_info("\n\nOperation cancelled by user.")
            sys.exit(130)
        except WAIError as e:
            print_error(str(e))
            sys.exit(1)
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            sys.exit(1)

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with all commands."""
        parser = argparse.ArgumentParser(
            description='Wheelwright Framework - Build AI wheels that roll forward forever',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
  WAI                         Auto-detect context and initialize
  WAI init                    Initialize spoke in current directory
  WAI status                  Show spoke status
  WAI group create <name>     Create a project group
  WAI group list              List all groups

"We aren't reinventing the wheel - we're evolving it faster than one person ever could."
            '''
        )

        subparsers = parser.add_subparsers(dest='command', help='Commands')

        # Init command
        init_parser = subparsers.add_parser('init', help='Initialize spoke')
        init_parser.add_argument('path', nargs='?', default=None, help='Project path (default: interactive)')

        # Status command
        status_parser = subparsers.add_parser('status', help='Show spoke status')
        status_parser.add_argument('path', nargs='?', default='.', help='Project path (default: current directory)')

        # Hub commands
        hub_parser = subparsers.add_parser('hub', help='Hub management')
        hub_subparsers = hub_parser.add_subparsers(dest='hub_command')

        hub_create = hub_subparsers.add_parser('create', help='Create a new hub')
        hub_create.add_argument('path', nargs='?', default=None, help='Hub location')

        hub_locate = hub_subparsers.add_parser('locate', help='Find hub location')

        # Projects commands
        projects_parser = subparsers.add_parser('projects', help='Project management')
        projects_subparsers = projects_parser.add_subparsers(dest='projects_command')

        projects_add = projects_subparsers.add_parser('add', help='Add projects to hub')
        projects_add.add_argument('--scan', nargs='+', help='Paths to scan for projects')

        projects_list = projects_subparsers.add_parser('list', help='List registered projects')
        projects_list.add_argument('--group', help='Filter by group')

        # Group commands
        group_parser = subparsers.add_parser('group', help='Group management')
        group_subparsers = group_parser.add_subparsers(dest='group_command')

        # group create
        group_create = group_subparsers.add_parser('create', help='Create a new group')
        group_create.add_argument('name', help='Group name')
        group_create.add_argument('--description', '-d', help='Group description')

        # group list
        group_list = group_subparsers.add_parser('list', help='List all groups')
        group_list.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')

        # group add-spoke
        group_add_spoke = group_subparsers.add_parser('add-spoke', help='Add spoke to group')
        group_add_spoke.add_argument('group', help='Group name')
        group_add_spoke.add_argument('spoke', help='Spoke name or path')

        # group remove-spoke
        group_remove_spoke = group_subparsers.add_parser('remove-spoke', help='Remove spoke from group')
        group_remove_spoke.add_argument('group', help='Group name')
        group_remove_spoke.add_argument('spoke', help='Spoke name or path')

        # group delete
        group_delete = group_subparsers.add_parser('delete', help='Delete a group')
        group_delete.add_argument('name', help='Group name')
        group_delete.add_argument('--force', '-f', action='store_true', help='Skip confirmation')

        # Sync command (placeholder - will be implemented in commands/)
        sync_parser = subparsers.add_parser('sync', help='Sync spoke with hub')
        sync_parser.add_argument('--all', action='store_true', help='Sync all spokes')

        # Closeout command (placeholder)
        closeout_parser = subparsers.add_parser('closeout', help='Generate session closeout')

        # Context command (placeholder)
        context_parser = subparsers.add_parser('context', help='Output context for LLM paste')
        context_parser.add_argument('path', nargs='?', default='.', help='Project path')

        # Version command
        version_parser = subparsers.add_parser('version', help='Show version info')

        return parser

    def _handle_no_command(self):
        """
        Handle no command - interactive menu based on context.

        Logic:
        1. If in framework folder → framework menu
        2. If in spoke folder → spoke menu
        3. Otherwise → initialization menu
        """
        from .utils.input import safe_choice

        cwd = Path.cwd()

        # Check if current directory is the framework
        if self._is_framework_directory(cwd):
            self._show_framework_menu(cwd)

        # Check if current directory has a spoke
        elif check_spoke_initialized(cwd):
            self._show_spoke_menu(cwd)

        else:
            # No spoke detected
            self._show_init_menu(cwd)

    def _show_framework_menu(self, framework_path: Path):
        """Show interactive menu for framework directory."""
        print_info("\n" + "=" * 60)
        print_info("          Wheelwright Framework")
        print_info("=" * 60)
        print_info("Build projects with the help of AI that roll forward")
        print_info("faster and more efficiently with each iteration.\n")

        is_initialized = check_spoke_initialized(framework_path)

        if not is_initialized:
            while True:
                print_info("\n⚠️  Framework not initialized yet.\n")
                print_info("  1/i - ✨ Initialize      Set up framework (recommended)")
                print_info("  2/? - ❓ Help           Getting started")
                print_info("  q   - 👋 Quit")
                print_info("")

                options = [
                    ('1', 'i', '✨ Initialize', 'init'),
                    ('2', '?', '❓ Help', 'help'),
                    ('q', 'q', '👋 Quit', 'quit')
                ]

                choice = safe_menu_choice("Select option", options, default='1')

                if choice == "init":
                    framework_first_init(framework_path, verbose=True)
                    # After init, break to reload menu
                    break
                elif choice == "help":
                    self._create_parser().print_help()
                elif choice == "quit" or choice is None:
                    return
            # After init, show initialized menu
            is_initialized = True

        if is_initialized:
            while True:
                print_info("\n" + "=" * 60)
                print_info("                Main Menu")
                print_info("=" * 60)
                print_info("")
                print_info("  1/h - 🏢 Hub          Central knowledge repository")
                print_info("  2/s - 🎡 Spokes       Registered projects")
                print_info("  3/t - 📊 Statistics   Insights & recommendations")
                print_info("  4/? - ❓ Help         Getting started & commands")
                print_info("  v   - ℹ️  Version      Show version info")
                print_info("  q   - 👋 Quit")
                print_info("")

                options = [
                    ('1', 'h', '🏢 Hub', 'hub'),
                    ('2', 's', '🎡 Spokes', 'spokes'),
                    ('3', 't', '📊 Statistics', 'statistics'),
                    ('4', '?', '❓ Help', 'help'),
                    ('v', 'v', 'ℹ️  Version', 'version'),
                    ('q', 'q', '👋 Quit', 'quit')
                ]

                choice = safe_menu_choice("Select option", options, default='2')

                if choice == "hub":
                    self._show_hub_actions_menu()
                elif choice == "spokes":
                    self._show_spokes_menu(framework_path)
                elif choice == "statistics":
                    self._show_statistics_menu()
                elif choice == "help":
                    self._show_help_menu()
                elif choice == "version":
                    self._cmd_version()
                elif choice == "quit" or choice is None:
                    return

    def _show_spoke_menu(self, spoke_path: Path):
        """Show interactive menu for spoke directory."""
        while True:
            print_info("\n" + "=" * 60)
            print_info(f"Spoke: {spoke_path.name}")
            print_info("=" * 60)
            print_info("")
            print_info("  Spoke-specific actions")
            print_info("")
            print_info("  1/s - ℹ️  Status          View spoke status")
            print_info("  2/y - 🔄 Sync            Sync with hub")
            print_info("  3/c - 📝 Closeout        Session closeout")
            print_info("  4/o - 📄 Context         Export for LLM")
            print_info("  5/? - ❓ Help            Show all commands")
            print_info("  q   - 👋 Quit")
            print_info("")

            options = [
                ('1', 's', 'ℹ️  Status', 'status'),
                ('2', 'y', '🔄 Sync', 'sync'),
                ('3', 'c', '📝 Closeout', 'closeout'),
                ('4', 'o', '📄 Context', 'context'),
                ('5', '?', '❓ Help', 'help'),
                ('q', 'q', '👋 Quit', 'quit')
            ]

            choice = safe_menu_choice("Select option", options, default='1')

            if choice == "status":
                self._cmd_status(type('Args', (), {'path': '.'})())
            elif choice == "sync":
                self._cmd_sync(type('Args', (), {'all': False})())
            elif choice == "closeout":
                self._cmd_closeout(type('Args', (), {})())
            elif choice == "context":
                self._cmd_context(type('Args', (), {'path': '.'})())
            elif choice == "help":
                self._create_parser().print_help()
            elif choice == "quit" or choice is None:
                return

    def _show_init_menu(self, cwd: Path):
        """Show menu for uninitialized directory."""
        while True:
            print_info("\n" + "=" * 60)
            print_info("Wheelwright Framework")
            print_info("=" * 60)
            print_info("\nBuild projects with the help of AI that roll forward")
            print_info("faster and more efficiently with each iteration.\n")
            print_info(f"Current directory: {cwd}\n")
            print_info("⚠️  No spoke detected in this directory.\n")
            print_info("  1/i - ✨ Initialize      Create spoke here")
            print_info("  2/? - ❓ Help           Getting started")
            print_info("  q   - 👋 Exit")
            print_info("")

            options = [
                ('1', 'i', '✨ Initialize', 'init'),
                ('2', '?', '❓ Help', 'help'),
                ('q', 'q', '👋 Exit', 'quit')
            ]

            choice = safe_menu_choice("Select option", options, default='1')

            if choice == "init":
                init_spoke_interactive(verbose=True)
                # After init, could break and show spoke menu, but for now just continue
            elif choice == "help":
                self._create_parser().print_help()
            elif choice == "quit" or choice is None:
                return

    def _show_spokes_menu(self, framework_path: Path):
        """Show Spokes menu with registry listing and management."""
        import json
        from datetime import datetime

        while True:
            # Check for hub first
            hub_manager = HubManager()
            hub_path = hub_manager.auto_discover_hub(Path.cwd(), verbose=False)

            if not hub_path:
                print_info("\n" + "=" * 60)
                print_info("              Spokes Menu │ No Hub")
                print_info("=" * 60)
                print_info("")
                print_info("  ⚠️  No hub configured. Please set up a hub first.")
                print_info("")
                print_info("  A hub is required to manage spokes.")
                print_info("  Go to: Main Menu → Hub → Locate or Create")
                print_info("")
                input("  Press Enter to continue...")
                return

            # Load registry
            from .utils.registry import load_registry
            try:
                registry = load_registry(hub_path)
                projects = registry.get('projects', [])
            except Exception:
                # Registry doesn't exist yet or is corrupt
                projects = []
            spoke_count = len(projects)

            # Show menu with stats
            print_info("\n" + "=" * 60)
            print_info(f"              Spokes Menu │ {spoke_count} Projects")
            print_info("=" * 60)
            print_info("")

            # Display project listing by default
            if projects:
                print_info("  Registered Projects:")
                print_info("")
                for i, project in enumerate(projects, 1):
                    # Extract project info
                    name = project.get('name', 'Unknown')
                    desc = project.get('description', 'No description')
                    path = project.get('path', '')

                    # Try to get additional details
                    state_data = self._get_spoke_details(Path(path))
                    tech_stack = state_data.get('tech_stack', 'Unknown')
                    last_teach = state_data.get('last_teach', 'Never')
                    signal_count = state_data.get('signal_count', 0)
                    last_update = state_data.get('last_update', 'Unknown')
                    status = state_data.get('status', 'Unknown')

                    # Format display
                    status_icon = "🟢" if status == "active" else "🔴"
                    print_info(f"  [{i}] {status_icon} {name}")
                    print_info(f"      {desc[:60]}...")
                    print_info(f"      Tech: {tech_stack} │ Signals: {signal_count} │ Last teach: {last_teach}")
                    print_info(f"      Status: {status} │ Updated: {last_update}")
                    print_info("")
            else:
                print_info("  No projects registered yet.")
                print_info("")

            # Menu options
            print_info("  1/a - ➕ Add Projects    Register new spokes")
            print_info("  2/g - 📁 Groups          Organize spokes")
            print_info("  3/r - 🔄 Refresh         Reload project list")
            print_info("  b   - ⬅️  Back")
            print_info("")

            options = [
                ('1', 'a', '➕ Add Projects', 'add'),
                ('2', 'g', '📁 Groups', 'groups'),
                ('3', 'r', '🔄 Refresh', 'refresh'),
                ('b', 'b', '⬅️  Back', 'back')
            ]

            choice = safe_menu_choice("Select", options, default='b')

            if choice == "add":
                from .utils.input import safe_input
                print_info("\nAdd Projects - Scan for projects in a directory\n")
                scan_path = safe_input("  Folder to scan (default: parent of hub)", default="", allow_empty=True)

                if scan_path:
                    args = type('Args', (), {'scan': [scan_path]})()
                else:
                    args = type('Args', (), {'scan': None})()

                self._projects_add(args)
                input("\n  Press Enter to continue...")
            elif choice == "groups":
                self._show_groups_menu()
            elif choice == "refresh":
                continue  # Reload
            elif choice == "back" or choice is None:
                return

    def _get_spoke_details(self, spoke_path: Path):
        """Get detailed information about a spoke."""
        import json
        from datetime import datetime

        details = {
            'tech_stack': 'Unknown',
            'last_teach': 'Never',
            'signal_count': 0,
            'last_update': 'Unknown',
            'status': 'inactive'
        }

        if not spoke_path.exists():
            return details

        # Check for WAI-Spoke directory
        wai_spoke = spoke_path / 'WAI-Spoke'
        if not wai_spoke.exists():
            return details

        # Load WAI-State.json for details
        state_file = wai_spoke / 'WAI-State.json'
        if state_file.exists():
            try:
                state = json.loads(state_file.read_text())

                # Get tech stack from foundation
                foundation = state.get('_project_foundation', {})
                tech = foundation.get('tech_stack', {})
                if tech:
                    tech_list = []
                    if tech.get('languages'): tech_list.extend(tech['languages'][:2])
                    if tech.get('frameworks'): tech_list.extend(tech['frameworks'][:1])
                    details['tech_stack'] = ', '.join(tech_list) if tech_list else 'Unknown'

                # Get last teach date (placeholder - to be implemented)
                details['last_teach'] = 'Not synced'

                # Check modification time for status
                mtime = datetime.fromtimestamp(state_file.stat().st_mtime)
                days_ago = (datetime.now() - mtime).days
                details['last_update'] = f"{days_ago}d ago" if days_ago > 0 else "Today"
                details['status'] = 'active' if days_ago < 30 else 'inactive'

            except Exception:
                pass

        # Count signals
        signals_file = wai_spoke / 'WAI-Signals.jsonl'
        if signals_file.exists():
            try:
                lines = signals_file.read_text().strip().split('\n')
                details['signal_count'] = len([l for l in lines if l.strip()])
            except Exception:
                pass

        return details

    def _show_groups_menu(self):
        """Show Groups menu (child of Spokes)."""
        from .utils.input import safe_input

        while True:
            print_info("\n" + "=" * 60)
            print_info("              Groups Menu")
            print_info("=" * 60)
            print_info("")
            print_info("  Organize your spokes into logical collections")
            print_info("")
            print_info("  1/l - 📋 List            View all groups")
            print_info("  2/c - ➕ Create          New group")
            print_info("  3/a - ➕ Add Spoke       Add spoke to group")
            print_info("  4/r - ➖ Remove Spoke    Remove spoke from group")
            print_info("  5/d - 🗑️  Delete         Delete group")
            print_info("  b   - ⬅️  Back")
            print_info("")

            options = [
                ('1', 'l', '📋 List', 'list'),
                ('2', 'c', '➕ Create', 'create'),
                ('3', 'a', '➕ Add Spoke', 'add'),
                ('4', 'r', '➖ Remove Spoke', 'remove'),
                ('5', 'd', '🗑️  Delete', 'delete'),
                ('b', 'b', '⬅️  Back', 'back')
            ]

            choice = safe_menu_choice("Select option", options, default='1')

            if choice == "back" or choice is None:
                return

            # Find hub first
            hub_manager = HubManager()
            hub_path = hub_manager.auto_discover_hub(Path.cwd(), verbose=False)

            if not hub_path:
                print_error("\n  No hub found. Create a hub first (Main Menu -> Hub -> Create).")
                continue

            groups_manager = GroupsManager(hub_path)

            if choice == "list":
                groups_manager.list_groups(verbose=True)
            elif choice == "create":
                name = safe_input("  Group name", allow_empty=False)
                if name:
                    description = safe_input("  Description (optional)", allow_empty=True)
                    groups_manager.create_group(name, description=description or None)
            elif choice == "add":
                group_name = safe_input("  Group name", allow_empty=False)
                spoke_id = safe_input("  Spoke name or path", allow_empty=False)
                if group_name and spoke_id:
                    groups_manager.add_spoke_to_group(group_name, spoke_id)
            elif choice == "remove":
                group_name = safe_input("  Group name", allow_empty=False)
                spoke_id = safe_input("  Spoke name or path", allow_empty=False)
                if group_name and spoke_id:
                    groups_manager.remove_spoke_from_group(group_name, spoke_id)
            elif choice == "delete":
                group_name = safe_input("  Group name", allow_empty=False)
                if group_name:
                    from .utils.input import safe_confirm
                    confirm = safe_confirm(f"  Delete group '{group_name}'?", default=False)
                    if confirm:
                        groups_manager.delete_group(group_name, force=True)

    def _show_spoke_actions_menu(self, spoke_path: Path):
        """Show actions for Spoke object."""
        while True:
            print_info("\n" + "=" * 60)
            print_info("           This Project Actions")
            print_info("=" * 60)
            print_info("")
            print_info("  Actions for the current spoke project")
            print_info("")
            print_info("  1/s - ℹ️  Status          View spoke status & foundation")
            print_info("  2/y - 🔄 Sync            Sync with hub")
            print_info("  3/c - 📝 Closeout        Generate session closeout")
            print_info("  4/o - 📄 Output Context  Export for LLM paste")
            print_info("  b   - ⬅️  Back")
            print_info("")

            options = [
                ('1', 's', 'ℹ️  Status', 'status'),
                ('2', 'y', '🔄 Sync', 'sync'),
                ('3', 'c', '📝 Closeout', 'closeout'),
                ('4', 'o', '📄 Output Context', 'context'),
                ('b', 'b', '⬅️  Back', 'back')
            ]

            choice = safe_menu_choice("Select action", options, default='1')

            if choice == "status":
                self._cmd_status(type('Args', (), {'path': str(spoke_path)})())
            elif choice == "sync":
                self._cmd_sync(type('Args', (), {'all': False})())
            elif choice == "closeout":
                self._cmd_closeout(type('Args', (), {})())
            elif choice == "context":
                self._cmd_context(type('Args', (), {'path': str(spoke_path)})())
            elif choice == "back" or choice is None:
                return

    def _show_hub_actions_menu(self):
        """Show actions for Hub object with stats and enhanced features."""
        import json

        while True:
            # Get hub info for stats
            hub_manager = HubManager()
            hub_path = hub_manager.auto_discover_hub(Path.cwd(), verbose=False)

            hub_stats = ""
            if hub_path:
                try:
                    # Load hub profile for stats
                    profile_path = hub_path / 'hub-profile.json'
                    if profile_path.exists():
                        profile = json.loads(profile_path.read_text())
                        version = profile.get('version', 'unknown')
                        last_learn = profile.get('last_learn_run', 'never')
                        hub_stats = f" │ Version: {version} │ Last learn: {last_learn}"
                except:
                    hub_stats = f" │ {hub_path.name}"
            else:
                hub_stats = " │ No hub configured"

            print_info("\n" + "=" * 60)
            print_info(f"               Hub Menu{hub_stats}")
            print_info("=" * 60)
            print_info("")
            print_info("  Central knowledge repository for all spokes")
            print_info("")

            if hub_path:
                print_info("  1/l - 🔍 Locate          Show hub location & candidates")
                print_info("  2/t - 🎓 Teach           Trigger teach event (hub learns)")
                print_info("  3/s - 📚 Share           Trigger share event (hub teaches)")
                print_info("  4/c - ✨ Create          Initialize new hub")
                print_info("  b   - ⬅️  Back")
                print_info("")

                options = [
                    ('1', 'l', '🔍 Locate', 'locate'),
                    ('2', 't', '🎓 Teach', 'teach'),
                    ('3', 's', '📚 Share', 'share'),
                    ('4', 'c', '✨ Create', 'create'),
                    ('b', 'b', '⬅️  Back', 'back')
                ]
            else:
                print_info("  1/l - 🔍 Locate          Find hub (scan for candidates)")
                print_info("  2/c - ✨ Create          Initialize new hub")
                print_info("  b   - ⬅️  Back")
                print_info("")

                options = [
                    ('1', 'l', '🔍 Locate', 'locate'),
                    ('2', 'c', '✨ Create', 'create'),
                    ('b', 'b', '⬅️  Back', 'back')
                ]

            choice = safe_menu_choice("Select", options, default='1')

            if choice == "locate":
                self._hub_locate_with_candidates()
                input("\n  Press Enter to continue...")
            elif choice == "teach":
                self._hub_trigger_teach()
                input("\n  Press Enter to continue...")
            elif choice == "share":
                self._hub_trigger_share()
                input("\n  Press Enter to continue...")
            elif choice == "create":
                self._hub_create(type('Args', (), {'path': None})())
                input("\n  Press Enter to continue...")
            elif choice == "back" or choice is None:
                return

    def _show_statistics_menu(self):
        """Show statistics with insights and recommendations."""
        from .utils.input import safe_choice
        import json

        while True:
            print_info("\n" + "=" * 60)
            print_info("             Statistics & Insights")
            print_info("=" * 60)

            # Find hub
            hub_manager = HubManager()
            hub_path = hub_manager.auto_discover_hub(Path.cwd(), verbose=False)

            if not hub_path:
                print_info("\n  No hub found. Statistics require a hub.")
                print_info("\n  1. Create hub")
                print_info("  2. Back")
                print_info("")

                choice = safe_choice("Select option", choices=["1", "2"], default="2")
                if choice == "1":
                    self._hub_create(type('Args', (), {'path': None})())
                else:
                    return
                continue

            # Load hub and spoke data
            from .utils.registry import load_registry
            try:
                registry = load_registry(hub_path)
                spoke_count = len(registry.get('projects', []))
                group_count = len(registry.get('groups', {}))
            except:
                spoke_count = 0
                group_count = 0

            # Display statistics
            print_info("\n  Hub Overview:")
            print_info(f"    Location: {hub_path}")
            print_info(f"    Registered Spokes: {spoke_count}")
            print_info(f"    Groups: {group_count}")

            # Recommendations with impact values
            print_info("\n  Recommendations:")
            recommendations = []

            if spoke_count == 0:
                recommendations.append({
                    'id': 1,
                    'impact': 10,
                    'action': 'Add your first spoke',
                    'description': 'Register projects to start tracking development',
                    'command': 'spokes_add'
                })

            if spoke_count > 0 and group_count == 0:
                recommendations.append({
                    'id': 2,
                    'impact': 7,
                    'action': 'Create project groups',
                    'description': 'Organize spokes by type or client',
                    'command': 'groups_create'
                })

            if spoke_count > 5 and group_count == 0:
                recommendations.append({
                    'id': 3,
                    'impact': 9,
                    'action': 'Create groups for better organization',
                    'description': 'With 5+ spokes, groups help manage complexity',
                    'command': 'groups_create'
                })

            # Always show maintenance recommendation
            recommendations.append({
                'id': 4,
                'impact': 5,
                'action': 'Run sync on all spokes',
                'description': 'Keep hub knowledge base current',
                'command': 'sync_all'
            })

            if recommendations:
                for rec in sorted(recommendations, key=lambda x: x['impact'], reverse=True):
                    print_info(f"\n    [{rec['id']}] Impact: {rec['impact']}/10 - {rec['action']}")
                    print_info(f"        {rec['description']}")
            else:
                print_info("\n    No recommendations at this time.")

            print_info("")
            print_info("  1/e - ⚡ Enact           Execute a recommendation")
            print_info("  2/r - 🔄 Refresh         Update statistics")
            print_info("  b   - ⬅️  Back")
            print_info("")

            options = [
                ('1', 'e', '⚡ Enact', 'enact'),
                ('2', 'r', '🔄 Refresh', 'refresh'),
                ('b', 'b', '⬅️  Back', 'back')
            ]

            choice = safe_menu_choice("Select option", options, default='b')

            if choice == "enact" and recommendations:
                rec_id = safe_choice(
                    "  Select recommendation",
                    choices=[str(r['id']) for r in recommendations],
                    default="1"
                )
                if rec_id:
                    rec = next((r for r in recommendations if str(r['id']) == rec_id), None)
                    if rec:
                        if rec['command'] == 'spokes_add':
                            self._projects_add(type('Args', (), {'scan': None})())
                        elif rec['command'] == 'groups_create':
                            self._show_groups_menu()
                        elif rec['command'] == 'sync_all':
                            print_info("\n  Sync all feature coming soon.")
            elif choice == "refresh":
                continue  # Refresh
            elif choice == "back" or choice is None:
                return

    def _show_help_menu(self):
        """Show help menu with structured options."""
        while True:
            print_info("\n" + "=" * 60)
            print_info("               Help Menu")
            print_info("=" * 60)
            print_info("")
            print_info("  1/c - 🖥️  CLI Usage        Navigate interactive menus")
            print_info("  2/p - 📦 Project Use      Initialize & manage spokes")
            print_info("  3/m - 💻 Command Line     Quick reference guide")
            print_info("  b   - ⬅️  Back")
            print_info("")

            options = [
                ('1', 'c', '🖥️  CLI Usage', 'cli'),
                ('2', 'p', '📦 Project Use', 'project'),
                ('3', 'm', '💻 Command Line', 'commands'),
                ('b', 'b', '⬅️  Back', 'back')
            ]

            choice = safe_menu_choice("Select option", options, default='1')

            if choice == "cli":
                print_info("\n" + "=" * 60)
                print_info("           Using WAI CLI")
                print_info("=" * 60)
                print_info("\n  The WAI CLI provides interactive menus to:")
                print_info("")
                print_info("  • Manage your hub (central repository)")
                print_info("  • Register and organize spokes (projects)")
                print_info("  • View statistics and recommendations")
                print_info("  • Access project context and status")
                print_info("")
                print_info("  Navigation:")
                print_info("  - Use numbers OR letter shortcuts (e.g., 1/h for Hub)")
                print_info("  - Press Enter to use default (shown in brackets)")
                print_info("  - Press 'b' for Back, 'q' for Quit")
                print_info("  - Ctrl+C to cancel current operation")
                print_info("")
                input("  Press Enter to continue...")

            elif choice == "project":
                print_info("\n" + "=" * 60)
                print_info("        Using WAI Within a Project")
                print_info("=" * 60)
                print_info("\n  Each project can have its own spoke:")
                print_info("")
                print_info("  1. Initialize spoke in project:")
                print_info("     $ cd /path/to/project")
                print_info("     $ WAI init")
                print_info("")
                print_info("  2. Key files created (WAI-Spoke/):")
                print_info("     • WAI-Guide.md - AI instructions")
                print_info("     • WAI-State.json - Project state")
                print_info("     • WAI-State.md - Strategic context")
                print_info("     • WAI-Signals.jsonl - Learning signals")
                print_info("")
                print_info("  3. During development:")
                print_info("     - AI assistants read WAI-Guide.md")
                print_info("     - Track decisions in WAI-State.json")
                print_info("     - Sync learnings to hub periodically")
                print_info("")
                input("  Press Enter to continue...")

            elif choice == "commands":
                print_info("\n" + "=" * 60)
                print_info("        Using WAI via Command Line")
                print_info("=" * 60)
                print_info("\n  Quick commands (bypass menus):")
                print_info("")
                print_info("  Status & Info:")
                print_info("    WAI status              Show spoke status")
                print_info("    WAI version             Show version")
                print_info("")
                print_info("  Hub:")
                print_info("    WAI hub locate          Find hub")
                print_info("    WAI hub create [path]   Create hub")
                print_info("")
                print_info("  Groups:")
                print_info("    WAI group create <name> [--description TEXT]")
                print_info("    WAI group list [--verbose]")
                print_info("    WAI group add-spoke <group> <spoke>")
                print_info("    WAI group remove-spoke <group> <spoke>")
                print_info("    WAI group delete <name>")
                print_info("")
                print_info("  See 'WAI --help' for complete list")
                print_info("")
                input("  Press Enter to continue...")

            elif choice == "back" or choice is None:
                return

    def _show_projects_actions_menu(self):
        """Show actions for Projects object."""
        from .utils.input import safe_choice

        while True:
            print_info("\n--- Projects Actions ---\n")
            print_info("1. List all projects")
            print_info("2. Add new projects")
            print_info("3. List by group")
            print_info("4. Back\n")

            choice = safe_choice(
                "Select action",
                choices=["1", "2", "3", "4"],
                default="1"
            )

            if choice == "1":
                self._projects_list(type('Args', (), {'group': None})())
            elif choice == "2":
                self._projects_add(type('Args', (), {'scan': None})())
            elif choice == "3":
                from .utils.input import safe_input
                group_name = safe_input("Group name", allow_empty=False)
                if group_name:
                    self._projects_list(type('Args', (), {'group': group_name})())
            elif choice == "4" or choice is None:
                return

    def _show_groups_actions_menu(self):
        """Show actions for Groups object."""
        from .utils.input import safe_choice, safe_input

        while True:
            print_info("\n--- Groups Actions ---\n")
            print_info("1. List all groups")
            print_info("2. Create new group")
            print_info("3. Add spoke to group")
            print_info("4. Remove spoke from group")
            print_info("5. Delete group")
            print_info("6. Back\n")

            choice = safe_choice(
                "Select action",
                choices=["1", "2", "3", "4", "5", "6"],
                default="1"
            )

            if choice == "6" or choice is None:
                return

            # Find hub first
            hub_manager = HubManager()
            hub_path = hub_manager.auto_discover_hub(Path.cwd(), verbose=False)

            if not hub_path:
                print_error("No hub found. Create a hub first (select Hub -> Create new hub).")
                continue

            groups_manager = GroupsManager(hub_path)

            if choice == "1":
                groups_manager.list_groups(verbose=True)

            elif choice == "2":
                name = safe_input("Group name", allow_empty=False)
                if name:
                    description = safe_input("Description (optional)", allow_empty=True)
                    groups_manager.create_group(name, description=description or None)

            elif choice == "3":
                group_name = safe_input("Group name", allow_empty=False)
                spoke_id = safe_input("Spoke name or path", allow_empty=False)
                if group_name and spoke_id:
                    groups_manager.add_spoke_to_group(group_name, spoke_id)

            elif choice == "4":
                group_name = safe_input("Group name", allow_empty=False)
                spoke_id = safe_input("Spoke name or path", allow_empty=False)
                if group_name and spoke_id:
                    groups_manager.remove_spoke_from_group(group_name, spoke_id)

            elif choice == "5":
                group_name = safe_input("Group name", allow_empty=False)
                if group_name:
                    from .utils.input import safe_confirm
                    confirm = safe_confirm(f"Delete group '{group_name}'?", default=False)
                    if confirm:
                        groups_manager.delete_group(group_name, force=True)

    def _is_framework_directory(self, path: Path) -> bool:
        """
        Check if path is the framework directory.

        Checks:
        - Has WAI script
        - Has templates/ directory
        - Has wai_cli/ package

        Args:
            path: Path to check

        Returns:
            True if framework directory
        """
        return (
            (path / 'WAI').exists() and
            (path / 'templates').exists() and
            (path / 'wai_cli').exists()
        )

    def _route_command(self, args, parser):
        """Route command to appropriate handler."""
        if args.command == 'init':
            self._cmd_init(args)
        elif args.command == 'status':
            self._cmd_status(args)
        elif args.command == 'hub':
            self._cmd_hub(args)
        elif args.command == 'projects':
            self._cmd_projects(args)
        elif args.command == 'group':
            self._cmd_group(args)
        elif args.command == 'sync':
            self._cmd_sync(args)
        elif args.command == 'closeout':
            self._cmd_closeout(args)
        elif args.command == 'context':
            self._cmd_context(args)
        elif args.command == 'version':
            self._cmd_version()
        else:
            parser.print_help()

    # Command handlers

    def _cmd_init(self, args):
        """Handle init command."""
        if args.path:
            # Initialize specific path
            try:
                spoke_path = normalize_path(args.path)
                from .init import init_spoke
                init_spoke(spoke_path, is_framework=False, verbose=True)
                print_success(f"\nSpoke initialized at {spoke_path}")
            except Exception as e:
                print_error(f"Initialization failed: {e}")
        else:
            # Interactive initialization
            init_spoke_interactive(verbose=True)

    def _cmd_status(self, args):
        """Handle status command."""
        from .commands.status import show_status
        show_status(args.path)

    def _cmd_hub(self, args):
        """Handle hub commands."""
        if args.hub_command == 'create':
            self._hub_create(args)
        elif args.hub_command == 'locate':
            self._hub_locate()
        else:
            print_info("Hub commands: create, locate")

    def _hub_create(self, args):
        """Create new hub."""
        hub_manager = HubManager()

        if args.path:
            try:
                hub_path = normalize_path(args.path)
                hub_manager.prompt_create_hub(default_path=hub_path)
            except Exception as e:
                print_error(f"Hub creation failed: {e}")
        else:
            # Interactive with default ../hub
            try:
                cwd = Path.cwd()
                default_path = (cwd.parent / 'hub').resolve()
                hub_manager.prompt_create_hub(default_path=default_path, framework_path=cwd)
            except Exception as e:
                print_error(f"Hub creation failed: {e}")

    def _hub_locate(self):
        """Locate hub."""
        hub_manager = HubManager()
        cwd = Path.cwd()

        hub_path = hub_manager.auto_discover_hub(cwd, verbose=True)

        if hub_path:
            print_success(f"\nHub found at: {hub_path}")
        else:
            print_info("\nNo hub found.")
            print_info("Run 'WAI hub create' to create a new hub.")

    def _hub_locate_with_candidates(self):
        """Locate hub and show all candidates with selection options."""
        from .utils.input import safe_input, safe_confirm

        hub_manager = HubManager()
        cwd = Path.cwd()

        print_info("\n🔍 Scanning for hub candidates...\n")

        # Get all candidates (modify auto_discover to return all)
        candidates = self._get_all_hub_candidates(cwd)

        if not candidates:
            print_info("  No hub candidates found.")
            print_info("  Run 'Create' to initialize a new hub.")
            return

        # Show all candidates
        print_info(f"  Found {len(candidates)} hub candidate(s):\n")
        for i, candidate in enumerate(candidates, 1):
            print_info(f"  [{i}] {candidate.path} (score: {candidate.score})")
            for reason in candidate.reasons[:3]:  # Show top 3 reasons
                print_info(f"      {reason}")
            print_info("")

        if len(candidates) == 1:
            print_success(f"  Using hub: {candidates[0].path}")
            return

        # Multiple candidates - prompt for selection
        print_info("  Multiple hub candidates found. What would you like to do?\n")
        print_info("  1. Use highest-scored hub (recommended)")
        print_info("  2. Select specific hub")
        print_info("  3. Cancel\n")

        choice = safe_input("  Choice", default="1")

        if choice == "1":
            selected = candidates[0]
            print_success(f"\n  Selected: {selected.path}")
        elif choice == "2":
            idx = safe_input(f"  Select hub (1-{len(candidates)})", default="1")
            try:
                selected = candidates[int(idx) - 1]
                print_success(f"\n  Selected: {selected.path}")
            except (ValueError, IndexError):
                print_info("\n  Invalid selection.")
                return
        else:
            return

        # Ask about other candidates
        if len(candidates) > 1:
            print_info(f"\n  Other candidates found:")
            for candidate in candidates[1:]:
                print_info(f"    - {candidate.path}")

            action = safe_input("\n  Action for other hubs? (ignore/subsume/skip)", default="skip")

            if action == "ignore":
                print_info("\n  Ignoring other hubs...")
                self._hub_ignore_candidates([c.path for c in candidates[1:]], selected.path)
            elif action == "subsume":
                print_info("\n  Subsuming other hubs into primary...")
                for candidate in candidates[1:]:
                    self._hub_subsume(source_hub=candidate.path, target_hub=selected.path)

    def _get_all_hub_candidates(self, current_path: Path):
        """Get all hub candidates with scoring."""
        hub_manager = HubManager()

        # Use internal methods to get all candidates
        candidates = []

        # Environment variable
        import os
        env_hub = os.environ.get('WHEELWRIGHT_HUB_PATH')
        if env_hub:
            try:
                from .utils.paths import normalize_path
                env_path = normalize_path(env_hub)
                if env_path.exists():
                    from .hub import HubCandidate
                    candidate = HubCandidate(env_path)
                    candidate.add_score(15, "From $WHEELWRIGHT_HUB_PATH")
                    candidates.append(candidate)
            except Exception:
                pass

        # Parent folder scan
        parent_candidates = hub_manager._scan_parent_folder(current_path)
        candidates.extend(parent_candidates)

        # Score all candidates
        for candidate in candidates:
            hub_manager._score_candidate(candidate)

        # Sort by score
        candidates.sort(key=lambda c: c.score, reverse=True)

        # Return ALL candidates (not filtered by score)
        # This allows user to see and choose even low-scored options
        return candidates

    def _hub_trigger_teach(self):
        """Trigger teach event - hub learns from spokes."""
        print_info("\n🎓 Teach Event - Hub Learning from Spokes\n")
        print_info("  This will:")
        print_info("  • Scan all registered spokes for signals")
        print_info("  • Extract high-impact learnings")
        print_info("  • Update hub knowledge base")
        print_info("  • Record teach timestamp\n")

        from .utils.input import safe_confirm
        if not safe_confirm("  Trigger teach event?", default=False):
            print_info("  Cancelled.")
            return

        print_info("\n  Teaching...")
        print_info("  (Teach functionality to be implemented)")
        print_success("  Teach event complete!")

    def _hub_trigger_share(self):
        """Trigger share event - hub teaches spokes."""
        print_info("\n📚 Share Event - Hub Teaching Spokes\n")
        print_info("  This will:")
        print_info("  • Share hub knowledge with registered spokes")
        print_info("  • Update spoke guidance based on learnings")
        print_info("  • Propagate best practices")
        print_info("  • Record share timestamp\n")

        from .utils.input import safe_confirm
        if not safe_confirm("  Trigger share event?", default=False):
            print_info("  Cancelled.")
            return

        print_info("\n  Sharing...")
        print_info("  (Share functionality to be implemented)")
        print_success("  Share event complete!")

    def _hub_ignore_candidates(self, ignore_paths: list, primary_hub: Path):
        """Add hub paths to ignore list in primary hub profile."""
        import json

        try:
            profile_path = primary_hub / 'hub-profile.json'
            if not profile_path.exists():
                print_error("  Hub profile not found.")
                return

            profile = json.loads(profile_path.read_text())

            # Add ignore list to profile
            if 'hub_config' not in profile:
                profile['hub_config'] = {}

            if 'ignored_hubs' not in profile['hub_config']:
                profile['hub_config']['ignored_hubs'] = []

            # Add new ignore paths
            for path in ignore_paths:
                path_str = str(path)
                if path_str not in profile['hub_config']['ignored_hubs']:
                    profile['hub_config']['ignored_hubs'].append(path_str)
                    print_success(f"  Added to ignore list: {path}")

            # Save updated profile
            profile_path.write_text(json.dumps(profile, indent=2))
            print_success("\n  Ignore list updated!")

        except Exception as e:
            print_error(f"  Failed to update ignore list: {e}")

    def _hub_subsume(self, source_hub: Path, target_hub: Path):
        """Merge source hub into target hub."""
        import json
        import shutil
        from .utils.input import safe_confirm

        print_info(f"\n🔄 Subsuming {source_hub.name} → {target_hub.name}\n")

        # Load both registries
        try:
            source_registry_path = source_hub / 'registry' / 'wheel-projects.json'
            target_registry_path = target_hub / 'registry' / 'wheel-projects.json'

            if not source_registry_path.exists():
                print_warning(f"  Source registry not found: {source_registry_path}")
                return

            source_registry = json.loads(source_registry_path.read_text())
            target_registry = json.loads(target_registry_path.read_text()) if target_registry_path.exists() else {"version": "2.0", "projects": [], "groups": {}}

            # Merge projects
            source_projects = source_registry.get('projects', [])
            target_projects = target_registry.get('projects', [])
            target_paths = {p['path'] for p in target_projects}

            added_count = 0
            duplicate_count = 0

            for project in source_projects:
                if project['path'] not in target_paths:
                    target_projects.append(project)
                    added_count += 1
                    print_success(f"  ✓ Added: {project.get('name', 'Unknown')}")
                else:
                    duplicate_count += 1
                    print_info(f"  ⊙ Skipped duplicate: {project.get('name', 'Unknown')}")

            # Merge groups
            source_groups = source_registry.get('groups', {})
            target_groups = target_registry.get('groups', {})

            for group_name, group_data in source_groups.items():
                if group_name not in target_groups:
                    target_groups[group_name] = group_data
                    print_success(f"  ✓ Added group: {group_name}")
                else:
                    # Merge spokes in existing group
                    existing_spokes = set(target_groups[group_name].get('spokes', []))
                    new_spokes = group_data.get('spokes', [])
                    for spoke in new_spokes:
                        if spoke not in existing_spokes:
                            target_groups[group_name].setdefault('spokes', []).append(spoke)

            # Update target registry
            target_registry['projects'] = target_projects
            target_registry['groups'] = target_groups

            # Save merged registry
            target_registry_path.parent.mkdir(parents=True, exist_ok=True)
            target_registry_path.write_text(json.dumps(target_registry, indent=2))

            print_info(f"\n  Summary:")
            print_info(f"    Projects added: {added_count}")
            print_info(f"    Duplicates skipped: {duplicate_count}")
            print_info(f"    Groups merged: {len(source_groups)}")

            # Ask about deleting source hub
            if safe_confirm(f"\n  Delete source hub ({source_hub})?", default=False):
                try:
                    shutil.rmtree(source_hub)
                    print_success(f"  ✓ Deleted: {source_hub}")
                except Exception as e:
                    print_error(f"  Failed to delete source hub: {e}")
            else:
                print_info(f"  Source hub preserved: {source_hub}")

            print_success("\n  ✓ Subsume complete!")

        except Exception as e:
            print_error(f"  Subsume failed: {e}")
            import traceback
            traceback.print_exc()

    def _cmd_projects(self, args):
        """Handle projects commands."""
        if args.projects_command == 'add':
            self._projects_add(args)
        elif args.projects_command == 'list':
            self._projects_list(args)
        else:
            print_info("Projects commands: add, list")

    def _projects_add(self, args):
        """Add projects to hub."""
        # Find hub
        hub_manager = HubManager()
        hub_path = hub_manager.auto_discover_hub(Path.cwd())

        if not hub_path:
            print_error("No hub found. Run 'WAI hub create' first.")
            return

        # Scan paths
        scan_paths = [normalize_path(p) for p in args.scan] if args.scan else None

        # Discover and add
        discovery = ProjectDiscovery()
        count = discovery.discover_and_add_projects(
            hub_path=hub_path,
            scan_paths=scan_paths,
            auto_add=False
        )

        if count > 0:
            print_success(f"\nAdded {count} project(s) to hub.")

    def _projects_list(self, args):
        """List registered projects."""
        # Find hub
        hub_manager = HubManager()
        hub_path = hub_manager.auto_discover_hub(Path.cwd())

        if not hub_path:
            print_error("No hub found.")
            return

        # Load and display projects
        from .utils.registry import list_projects

        try:
            projects = list_projects(hub_path, group_filter=args.group)

            if not projects:
                print_info("No projects registered.")
                return

            print_info(f"\nRegistered projects ({len(projects)}):\n")

            for project in projects:
                name = project.get('name', 'Unknown')
                path = project.get('path', '')
                description = project.get('description', '')

                print_info(f"  {name}")
                if description:
                    print_info(f"    Description: {description}")
                print_info(f"    Path: {path}\n")

        except Exception as e:
            print_error(f"Failed to list projects: {e}")

    def _cmd_group(self, args):
        """Handle group commands."""
        # Find hub
        hub_manager = HubManager()
        hub_path = hub_manager.auto_discover_hub(Path.cwd())

        if not hub_path:
            print_error("No hub found. Run 'WAI hub create' first.")
            return

        groups_manager = GroupsManager(hub_path)

        if args.group_command == 'create':
            groups_manager.create_group(args.name, description=args.description)

        elif args.group_command == 'list':
            groups_manager.list_groups(verbose=args.verbose)

        elif args.group_command == 'add-spoke':
            groups_manager.add_spoke_to_group(args.group, args.spoke)

        elif args.group_command == 'remove-spoke':
            groups_manager.remove_spoke_from_group(args.group, args.spoke)

        elif args.group_command == 'delete':
            groups_manager.delete_group(args.name, force=args.force)

        else:
            print_info("Group commands: create, list, add-spoke, remove-spoke, delete")

    def _cmd_sync(self, args):
        """Handle sync command."""
        from .commands.sync import sync_spoke
        sync_spoke(all_spokes=args.all)

    def _cmd_closeout(self, args):
        """Handle closeout command."""
        from .commands.closeout import generate_closeout
        generate_closeout()

    def _cmd_context(self, args):
        """Handle context command."""
        from .commands.context import output_context
        output_context(args.path)

    def _cmd_version(self):
        """Show version information."""
        print_info(f"\nWheelwright Framework v{FRAMEWORK_VERSION}")
        print_info(f"Spoke structure version: {SPOKE_STRUCTURE_VERSION}\n")


def main():
    """CLI entry point with error handling."""
    try:
        cli = WheelwrightCLI()
        cli.run()
    except KeyboardInterrupt:
        print_info("\n\nOperation cancelled by user.")
        sys.exit(130)
    except WAIError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

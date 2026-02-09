#!/usr/bin/env python3
"""WAI CLI - Main entry point."""

import sys
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime

from .lib.discovery import CLIDiscovery
from .lib.state_manager import StateManager
from .lib.menu_generator import MenuGenerator
from ..observation import ObservationLogger


class WAICLIApp:
    """Main WAI CLI application."""

    def __init__(self):
        """Initialize CLI app."""
        self.discovery = CLIDiscovery()
        self.context = self.discovery.get_current_context()
        self.state_manager = StateManager() if self.context[2] else None
        self.menu = MenuGenerator(self.discovery, self.state_manager)

    def run_interactive(self) -> int:
        """Run interactive menu mode."""
        try:
            # Check machine optimization on startup
            self._check_machine_optimization_on_startup()

            while True:
                command = self.menu.show_main_menu()
                if command is None or command == "exit":
                    print("\nGoodbye!")
                    return 0
                result = self.execute_command(command)
                if result != 0:
                    print(f"Command '{command}' failed")
        except KeyboardInterrupt:
            print("\n\nInterrupted.")
            return 130
        except Exception as e:
            print(f"Error: {e}")
            return 1

    def _check_machine_optimization_on_startup(self) -> None:
        """Check and apply machine optimizations at CLI startup."""
        try:
            from ..hooks import check_machine_optimization
            from pathlib import Path

            project_root = Path.cwd()
            result = check_machine_optimization(project_root, silent=False)

            if result.get('applied'):
                print(f"✓ IDE optimized for {result['machine_id']} ({result['classification']})")
            elif result.get('message') and 'error' not in result.get('message', '').lower():
                print(f"✓ {result['message']}")
        except Exception:
            # Silently skip if optimization fails - don't block CLI startup
            pass

    def execute_command(self, command: str) -> int:
        """Execute a command."""
        if command == "status":
            self._show_status()
            return 0
        elif command == "machine":
            self._show_machine_status()
            return 0
        elif command == "list":
            self._show_list(verbose=False)
            return 0
        elif command == "init":
            return self.cmd_init()
        elif command == "teach":
            print("teach command - use: wai teach [spoke-name]")
            return 1
        elif command == "learn":
            print("learn command - use: wai learn [spoke-name]")
            return 1
        else:
            print(f"Unknown command: {command}")
            return 1

    def _show_status(self) -> None:
        """Show system status."""
        framework, hub, projects = self.context
        print("=" * 60)
        print("System Status")
        print("=" * 60)
        print(f"[+] Framework: {framework}" if framework else "[-] Framework: Not found")
        print(f"[+] Hub: {hub}" if hub else "[-] Hub: Not found")
        if self.state_manager:
            print(f"[+] Current Spoke: {self.state_manager.spoke_path}")
        else:
            print("[-] Spoke: Not initialized")

        # Add machine status
        try:
            from ..hooks import get_machine_status
            from pathlib import Path

            machine_status = get_machine_status(Path.cwd())
            if machine_status:
                print(f"\n[+] Machine: {machine_status['machine_id']} ({machine_status['classification'].upper()})")
                print(f"    RAM: {machine_status['ram_gb']} GB | CPU: {machine_status['cpu_model'][:40]}...")
                if machine_status['time_since_check']:
                    print(f"    Last optimized: {machine_status['time_since_check']}")
        except Exception:
            pass

        print("\nWheel Info:")
        state = self.state_manager.load_state() if self.state_manager else {}
        wheel = state.get("wheel", {})
        print(f"  Name: {wheel.get('name', 'Unknown')}")
        print(f"  Version: {wheel.get('version', 'Unknown')}")
        print(f"  Type: {wheel.get('node_type', 'unknown')}")
        print(f"  Spoke ID: a1f2e8b4c9d3")
        print("=" * 60)

    def _show_machine_status(self) -> None:
        """Show detailed machine optimization status."""
        try:
            from ..hooks import format_machine_status_detail
            print(format_machine_status_detail())
        except Exception as e:
            print(f"\n⚠️  Error getting machine status: {e}\n")

    def _show_list(self, verbose: bool = False) -> None:
        """Show project list."""
        framework, hub, projects = self.context
        if not projects:
            print("No projects found.")
            return
        print(f"\nProjects in Wheel ({len(projects)} total):")
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project.get('name', f'Project {i}')}")

    def cmd_init(self) -> int:
        """Initialize hub or spoke."""
        init_type = self.menu.show_init_submenu()
        if init_type is None or init_type == "cancel":
            return 0
        if init_type == "hub":
            path_input = self.menu.prompt_for_input("Hub path (relative or absolute)", default="./wheelwright-hub")
            if path_input:
                hub_path = Path(path_input).expanduser()
                if self.state_manager and self.state_manager.create_hub(hub_path):
                    print(f"✓ Hub created at {hub_path}")
                    return 0
                else:
                    print(f"✗ Failed to create hub")
                    return 1
        elif init_type == "spoke":
            path_input = self.menu.prompt_for_input("Spoke path (relative or absolute)", default="./my-project")
            if path_input:
                spoke_path = Path(path_input).expanduser()
                if self.state_manager and self.state_manager.create_spoke(spoke_path):
                    print(f"✓ Spoke created at {spoke_path}")
                    return 0
                else:
                    print(f"✗ Failed to create spoke")
                    return 1
        return 1

    def run_command(self, args) -> int:
        """Run command from arguments."""
        # Check for --help flag
        if getattr(args, 'help', False) and hasattr(args, 'command'):
            from .lib.help_system import HelpRegistry
            HelpRegistry.show_help(args.command)
            return 0

        if args.command == "init":
            return self.cmd_init()
        elif args.command == "list":
            self._show_list(verbose=getattr(args, 'verbose', False))
            return 0
        elif args.command == "status":
            self._show_status()
            return 0
        elif args.command == "teach":
            return self.cmd_teach(args)
        elif args.command == "learn":
            return self.cmd_learn(args)
        elif args.command == "help":
            from .lib.help_system import HelpRegistry
            help_target = getattr(args, 'topic', None)
            HelpRegistry.show_help(help_target)
            return 0
        else:
            return 1

    def cmd_teach(self, args) -> int:
        """Handle teach command."""
        from .commands.teach_interactive import run_teach

        spoke = getattr(args, 'spoke', None)
        force = getattr(args, 'force', False)
        json_output = getattr(args, 'json', False)

        return run_teach(spoke, force, json_output, self.discovery, self.state_manager)

    def cmd_learn(self, args) -> int:
        """Handle learn command."""
        from .commands.learn_interactive import run_learn

        spoke = getattr(args, 'spoke', None)
        priority = getattr(args, 'priority', 'normal')
        force = getattr(args, 'force', False)
        json_output = getattr(args, 'json', False)

        return run_learn(spoke, priority, force, json_output, self.discovery, self.state_manager)


def main(argv: Optional[list] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Wheelwright Framework CLI", prog="wai")
    parser.add_argument("--version", action="version", version="%(prog)s 4.0.0")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("init", help="Initialize hub or spoke")
    list_parser = subparsers.add_parser("list", help="List wheel projects")
    list_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    subparsers.add_parser("status", help="Show system status")

    teach_parser = subparsers.add_parser("teach", help="Distribute template updates")
    teach_parser.add_argument("spoke", nargs='?', default=None, help="Spoke name or ID")
    teach_parser.add_argument("-f", "--force", action="store_true", help="Skip confirmation")
    teach_parser.add_argument("--json", action="store_true", help="Output as JSON")

    learn_parser = subparsers.add_parser("learn", help="Collect insights from spokes")
    learn_parser.add_argument("spoke", nargs='?', default=None, help="Spoke name or ID")
    learn_parser.add_argument("-p", "--priority", choices=["high", "normal", "low"], default="normal", help="Signal priority")
    learn_parser.add_argument("-f", "--force", action="store_true", help="Skip confirmation")
    learn_parser.add_argument("--json", action="store_true", help="Output as JSON")

    help_parser = subparsers.add_parser("help", help="Show help for commands")
    help_parser.add_argument("topic", nargs='?', default=None, help="Command to get help for")

    args = parser.parse_args(argv)
    app = WAICLIApp()

    if not args.command:
        return app.run_interactive()
    else:
        return app.run_command(args)


if __name__ == "__main__":
    sys.exit(main())

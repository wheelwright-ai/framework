#!/usr/bin/env python3
"""WAI CLI - Main entry point."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any

from wai.cli.lib.discovery import CLIDiscovery
from wai.cli.lib.menu_generator import MenuGenerator
from wai.cli.lib.state_manager import StateManager
from wai.cli.visuals import get_formatter
from wai.utils.input import safe_confirm, safe_input

TEMPLATE_SPOKE_ROOT = Path("templates") / "WAI-Spoke"


@dataclass
class CommandResult:
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None


class WAICLIApp:
    """Main WAI CLI application."""

    def __init__(self):
        self.discovery = CLIDiscovery()
        self.context = self.discovery.get_current_context()
        self.state_manager = StateManager() if self.context[2] else None
        self.menu = MenuGenerator(self.discovery, self.state_manager)
        self.fmt = get_formatter()

    def run_interactive(self) -> int:
        """Run interactive menu mode."""
        try:
            while True:
                command = self.menu.show_main_menu()
                if command in (None, "quit", "exit"):
                    self.fmt.print_info("Goodbye!")
                    return 0
                result = self.execute_command(command)
                if result != 0:
                    self.fmt.print_warning(f"Command '{command}' failed")
        except KeyboardInterrupt:
            self.fmt.print_info("\nInterrupted.")
            return 130
        except Exception as exc:
            self.fmt.print_error(f"Error: {exc}")
            return 1

    def execute_command(self, command: str) -> int:
        """Execute a command from interactive menu."""
        if command == "status":
            return self.cmd_status()
        if command == "list":
            return self.cmd_list(verbose=True)
        if command == "teach":
            return self.cmd_teach(None, force=False, json_output=False)
        if command == "learn":
            return self.cmd_learn(None, priority="normal", force=False, json_output=False)
        if command == "registry":
            return self.cmd_registry()
        if command == "init":
            return self.cmd_init()
        if command == "help":
            self._show_help()
            return 0

        self.fmt.print_warning(f"Unknown command: {command}")
        return 1

    def cmd_status(self) -> int:
        """Show system status."""
        framework, hub, projects = self.context
        self.fmt.print_header("System Status", width=60)
        self.fmt.print_info(f"Framework: {framework or 'Not found'}")
        self.fmt.print_info(f"Hub: {hub or 'Not found'}")
        if self.state_manager:
            self.fmt.print_info(f"Current Spoke: {self.state_manager.spoke_path}")
        else:
            self.fmt.print_warning("Spoke not initialized")
        self.fmt.print_info(f"Projects in registry: {len(projects)}")
        return 0

    def cmd_list(self, verbose: bool) -> int:
        """List projects in registry."""
        projects = self.discovery.get_wheel_projects()
        if not projects:
            self.fmt.print_warning("No projects found in hub registry")
            return 1

        self.menu.display_project_list(verbose=verbose)
        return 0

    def cmd_registry(self) -> int:
        """Interactive registry maintenance."""
        while True:
            action = self.menu.show_registry_menu()
            if action in (None, "back"):
                return 0
            if action == "validate":
                self._registry_validate()
            elif action == "disable-missing":
                self._registry_disable_missing()
            elif action == "list":
                self.cmd_list(verbose=True)
            else:
                self.fmt.print_warning(f"Unknown registry action: {action}")

    def cmd_init(self) -> int:
        """Initialize hub or spoke (interactive only)."""
        selection = self.menu.show_init_submenu()
        if not selection or selection == "cancel":
            return 0
        if selection == "hub":
            path_value = safe_input("Hub path", default="./hub")
            name = safe_input("Hub name", default="wheelwright-hub")
            if not path_value or not name:
                return 1
            hub_path = Path(path_value).expanduser()
            manager = self.state_manager or StateManager()
            if manager.create_hub(hub_path, name, description=""):
                self.fmt.print_success(f"Hub created at {hub_path}")
                return 0
            self.fmt.print_error("Failed to create hub")
            return 1
        if selection == "spoke":
            path_value = safe_input("Spoke path", default=str(Path.cwd()))
            name = safe_input("Spoke name", default=Path(path_value).name)
            hub = safe_input("Hub id", default="wheelwright-hub")
            manager = self.state_manager or StateManager()
            if manager.create_spoke(Path(path_value).expanduser(), name, hub, description=""):
                self.fmt.print_success(f"Spoke created at {path_value}")
                return 0
            self.fmt.print_error("Failed to create spoke")
            return 1

        return 1

    def cmd_teach(self, spoke: Optional[str], force: bool, json_output: bool) -> int:
        """Teach templates to spokes."""
        projects = self._resolve_projects(spoke)
        if not projects:
            self._print_json_or_message(json_output, CommandResult("failed", "No projects found"))
            return 1

        results = []
        for project in projects:
            results.append(self._teach_project(project, force))

        failures = [res for res in results if res.status != "success"]
        if json_output:
            payload = {
                "results": [self._result_to_dict(res) for res in results],
                "failures": len(failures),
            }
            print(json.dumps(payload, indent=2))
        return 0 if not failures else 1

    def cmd_learn(self, spoke: Optional[str], priority: str, force: bool, json_output: bool) -> int:
        """Learn signals from spokes."""
        projects = self._resolve_projects(spoke)
        if not projects:
            self._print_json_or_message(json_output, CommandResult("failed", "No projects found"))
            return 1

        results = []
        for project in projects:
            results.append(self._learn_project(project, priority))

        failures = [res for res in results if res.status != "success"]
        if json_output:
            payload = {
                "results": [self._result_to_dict(res) for res in results],
                "failures": len(failures),
            }
            print(json.dumps(payload, indent=2))
        return 0 if not failures else 1

    def _resolve_projects(self, spoke: Optional[str]) -> List[Dict[str, Any]]:
        projects = self.discovery.get_wheel_projects()
        if not projects:
            return []
        if not spoke:
            return projects

        spoke_lower = spoke.lower()
        matches = []
        for project in projects:
            name = str(project.get("name", "")).lower()
            if name == spoke_lower:
                matches.append(project)
        return matches

    def _teach_project(self, project: Dict[str, Any], force: bool) -> CommandResult:
        path_value = project.get("path")
        if not path_value:
            return CommandResult("failed", "Missing project path", {"project": project.get("name")})

        project_path = Path(path_value).expanduser()
        if not project_path.exists():
            return CommandResult("failed", "Project path missing", {"path": path_value})

        if not TEMPLATE_SPOKE_ROOT.exists():
            return CommandResult("failed", "Template directory missing", {"template": str(TEMPLATE_SPOKE_ROOT)})

        if not force:
            proceed = safe_confirm(f"Teach templates to {project.get('name')}?", default=True)
            if not proceed:
                return CommandResult("skipped", "Teach cancelled", {"project": project.get("name")})

        updated: List[str] = []
        for source in TEMPLATE_SPOKE_ROOT.rglob("*"):
            if source.is_dir():
                continue
            relative = source.relative_to(TEMPLATE_SPOKE_ROOT)
            destination = project_path / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            updated.append(str(relative))

        return CommandResult("success", "Templates updated", {"updated": updated})

    def _learn_project(self, project: Dict[str, Any], priority: str) -> CommandResult:
        path_value = project.get("path")
        if not path_value:
            return CommandResult("failed", "Missing project path", {"project": project.get("name")})

        project_path = Path(path_value).expanduser()
        if not project_path.exists():
            return CommandResult("failed", "Project path missing", {"path": path_value})

        signals_path = project_path / "WAI-Spoke" / "observations.jsonl"
        if not signals_path.exists():
            return CommandResult("success", "No observations found", {"signals": 0})

        signals = [line for line in signals_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return CommandResult(
            "success",
            f"Collected {len(signals)} {priority} signals",
            {"signals": len(signals)},
        )

    def _registry_validate(self) -> None:
        projects = self.discovery.get_wheel_projects()
        missing = []
        for project in projects:
            path_value = project.get("path")
            if not path_value:
                missing.append(project)
                continue
            if not Path(path_value).expanduser().exists():
                missing.append(project)
        if not missing:
            self.fmt.print_success("All registry paths exist")
            return
        self.fmt.print_warning(f"Missing paths: {len(missing)}")
        for project in missing:
            self.fmt.print_info(f"  - {project.get('name')} ({project.get('path')})")

    def _registry_disable_missing(self) -> None:
        registry_path = self.discovery.find_hub_registry()
        if not registry_path:
            self.fmt.print_error("Hub registry not found")
            return

        registry_data = self.discovery.load_hub_registry()
        projects = registry_data.get("projects", [])
        changed = False
        for project in projects:
            path_value = project.get("path")
            if not path_value:
                project["status"] = "missing"
                changed = True
                continue
            if not Path(path_value).expanduser().exists():
                project["status"] = "missing"
                changed = True

        if not changed:
            self.fmt.print_info("No missing paths to update")
            return

        with open(registry_path, 'w') as f:
            json.dump(registry_data, f, indent=2)
        self.fmt.print_success("Registry updated with missing statuses")

    def _show_help(self) -> None:
        self.fmt.print_info("Use: wai <command> [options]")
        self.fmt.print_info("Commands: init, teach, learn, status, list, registry")

    def _result_to_dict(self, result: CommandResult) -> Dict[str, Any]:
        payload = {"status": result.status, "message": result.message}
        if result.details:
            payload.update(result.details)
        return payload

    def _print_json_or_message(self, json_output: bool, result: CommandResult) -> None:
        if json_output:
            print(json.dumps(self._result_to_dict(result), indent=2))
        else:
            self.fmt.print_warning(result.message)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Wheelwright Framework CLI", prog="wai")
    parser.add_argument("--version", action="version", version="%(prog)s 4.0.0")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("init", help="Initialize hub or spoke")

    list_parser = subparsers.add_parser("list", help="List wheel projects")
    list_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    subparsers.add_parser("status", help="Show system status")

    teach_parser = subparsers.add_parser("teach", help="Distribute template updates")
    teach_parser.add_argument("spoke", nargs='?', default=None, help="Spoke name")
    teach_parser.add_argument("-f", "--force", action="store_true", help="Skip confirmation")
    teach_parser.add_argument("--json", action="store_true", help="Output as JSON")

    learn_parser = subparsers.add_parser("learn", help="Collect insights from spokes")
    learn_parser.add_argument("spoke", nargs='?', default=None, help="Spoke name")
    learn_parser.add_argument("-p", "--priority", choices=["high", "normal", "low"], default="normal")
    learn_parser.add_argument("-f", "--force", action="store_true", help="Skip confirmation")
    learn_parser.add_argument("--json", action="store_true", help="Output as JSON")

    subparsers.add_parser("registry", help="Manage hub registry")
    subparsers.add_parser("help", help="Show help")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    app = WAICLIApp()

    if not args.command:
        return app.run_interactive()

    if args.command == "help":
        app._show_help()
        return 0

    if args.command == "init":
        return app.cmd_init()
    if args.command == "list":
        return app.cmd_list(verbose=getattr(args, "verbose", False))
    if args.command == "status":
        return app.cmd_status()
    if args.command == "teach":
        return app.cmd_teach(getattr(args, "spoke", None), getattr(args, "force", False), getattr(args, "json", False))
    if args.command == "learn":
        return app.cmd_learn(
            getattr(args, "spoke", None),
            getattr(args, "priority", "normal"),
            getattr(args, "force", False),
            getattr(args, "json", False),
        )
    if args.command == "registry":
        return app.cmd_registry()

    return 1


if __name__ == "__main__":
    sys.exit(main())

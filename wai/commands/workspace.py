"""
Workspace command helpers.

Refreshes workspace launcher files from templates and prints shortcut guidance.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..init import check_spoke_initialized
from ..utils.input import print_info, print_success, print_warning, print_error


def refresh_workspace(spoke_path: Path, verbose: bool = True) -> None:
    spoke_path = spoke_path.resolve()
    if not check_spoke_initialized(spoke_path):
        print_warning("WAI-Spoke not found in this project.")
        print_info("Run 'WAI init' to initialize the spoke first.")
        return

    templates_dir = _get_templates_dir()
    if not templates_dir.exists():
        print_error(f"Templates directory not found: {templates_dir}")
        return

    spoke_dir = spoke_path / "WAI-Spoke"
    workspace_files = ["WAI-Workspace.cmd", "wai-shell.sh", "wai-cli-launch.sh"]

    for filename in workspace_files:
        src = templates_dir / filename
        dst = spoke_dir / filename
        if not src.exists():
            if verbose:
                print_warning(f"Template not found: {filename}")
            continue
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        if verbose:
            print_info(f"Updated {filename}")

    if verbose:
        print_success("Workspace launchers refreshed.")
        _print_shortcut_help(spoke_dir)


def _get_templates_dir() -> Path:
    framework_root = Path(__file__).resolve().parents[2]
    templates_dir = framework_root / "templates" / "WAI"
    if templates_dir.exists():
        return templates_dir
    return Path.cwd() / "templates" / "WAI"


def _print_shortcut_help(spoke_dir: Path) -> None:
    state_file = spoke_dir / "WAI-State.json"
    if not state_file.exists():
        print_warning("WAI-State.json not found; shortcut guidance unavailable.")
        return

    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print_warning("WAI-State.json is invalid JSON; shortcut guidance unavailable.")
        return

    paths = state.get("wheel", {}).get("workspace", {}).get("paths", {})
    primary = paths.get("primary") or ""
    win_root = paths.get("windows", {}).get("root")
    wsl_root = paths.get("wsl", {}).get("root")

    print_info("Windows shortcut (no extra repo files):")
    if primary.lower() == "wsl":
        path = wsl_root or "<path>"
        print_info(f'  Target: cmd.exe /c "call \\\\wsl$\\<Distro>{path}\\WAI-Spoke\\WAI-Workspace.cmd"')
        print_info("  Start in: C:\\ (any local folder to avoid UNC warning)")
    elif primary.lower() == "windows":
        path = win_root or "<path>"
        print_info(f'  Target: cmd.exe /c "call {path}\\WAI-Spoke\\WAI-Workspace.cmd"')
    else:
        print_info("  Set wheel.workspace.paths.primary to windows or wsl for tailored guidance.")

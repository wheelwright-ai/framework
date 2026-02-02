"""
Spoke health checks and upgrade helpers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .upgrader import SpokeUpgrader
from .commands.sync import SPOKE_STRUCTURE_VERSION


def check_spoke_health(spoke_root: Path, templates_dir: Path) -> Dict[str, object]:
    spoke_root = spoke_root.resolve()
    wai_spoke_dir = spoke_root / "WAI-Spoke"
    issues: List[Dict[str, str]] = []

    seed_pending = _has_seed_files(wai_spoke_dir)
    if seed_pending:
        issues.append({
            "key": "seed_pending",
            "label": "Seed folders have files waiting to be absorbed"
        })

    workspace_status = _workspace_status(wai_spoke_dir, templates_dir)
    if workspace_status["missing"]:
        issues.append({
            "key": "workspace_missing",
            "label": f"Workspace launchers missing: {', '.join(workspace_status['missing'])}"
        })
    if workspace_status["outdated"]:
        issues.append({
            "key": "workspace_outdated",
            "label": f"Workspace launchers out of date: {', '.join(workspace_status['outdated'])}"
        })

    version_status = _spoke_version_status(spoke_root)
    if version_status["outdated"]:
        issues.append({
            "key": "spoke_outdated",
            "label": f"Spoke structure is {version_status['current']} (latest {version_status['target']})"
        })

    return {
        "issues": issues,
        "seed_pending": seed_pending,
        "workspace_missing": workspace_status["missing"],
        "workspace_outdated": workspace_status["outdated"],
        "spoke_version": version_status["current"],
        "spoke_target": version_status["target"],
        "spoke_version_outdated": version_status["outdated"]
    }


def _has_seed_files(wai_spoke_dir: Path) -> bool:
    seed_dir = wai_spoke_dir / "seed"
    if not seed_dir.exists():
        return False
    for folder in ("ingest", "reference"):
        target = seed_dir / folder
        if not target.exists():
            continue
        for item in target.iterdir():
            if item.name == "README.md":
                continue
            return True
    return False


def _workspace_status(wai_spoke_dir: Path, templates_dir: Path) -> Dict[str, List[str]]:
    files = ["WAI-Workspace.cmd", "wai-shell.sh", "wai-cli-launch.sh"]
    missing: List[str] = []
    outdated: List[str] = []

    for name in files:
        current = wai_spoke_dir / name
        template = templates_dir / name
        if not current.exists():
            missing.append(name)
            continue
        if not template.exists():
            continue
        try:
            if current.read_text(encoding="utf-8") != template.read_text(encoding="utf-8"):
                outdated.append(name)
        except Exception:
            outdated.append(name)

    return {"missing": missing, "outdated": outdated}


def _spoke_version_status(spoke_root: Path) -> Dict[str, str]:
    current = SpokeUpgrader.detect_version(spoke_root)
    target = SPOKE_STRUCTURE_VERSION
    outdated = False

    if current == "unknown":
        outdated = True
    else:
        current_tuple = _parse_version(current)
        target_tuple = _parse_version(target)
        if current_tuple and target_tuple and current_tuple < target_tuple:
            outdated = True

    return {"current": current, "target": target, "outdated": outdated}


def _parse_version(version: str) -> tuple:
    cleaned = "".join(ch if ch.isdigit() or ch == "." else "" for ch in version)
    if not cleaned:
        return ()
    parts = []
    for part in cleaned.split("."):
        if part.isdigit():
            parts.append(int(part))
        else:
            parts.append(0)
    return tuple(parts)

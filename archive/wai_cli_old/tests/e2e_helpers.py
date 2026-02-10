"""E2E CLI testing helpers."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class E2EPaths:
    workspace: Path
    hub: Path
    spoke: Path
    registry: Path


def setup_workspace(root: Path) -> E2EPaths:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    hub = root / "hub"
    spoke = root / "spokes" / "alpha"
    hub_registry = hub / "registry"
    hub_registry.mkdir(parents=True, exist_ok=True)

    registry_path = hub_registry / "wheel-projects.json"
    registry_data = {
        "version": "2.0",
        "projects": [
            {
                "name": "alpha",
                "path": str(spoke),
                "description": "E2E test spoke",
                "status": "active",
            }
        ]
    }
    registry_path.write_text(json.dumps(registry_data, indent=2))

    (spoke / "WAI-Spoke").mkdir(parents=True, exist_ok=True)
    (spoke / "WAI-Spoke" / "observations.jsonl").write_text(
        json.dumps({"id": "obs-1", "status": "complete"}) + "\n"
    )

    return E2EPaths(workspace=root, hub=hub, spoke=spoke, registry=registry_path)

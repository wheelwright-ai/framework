import json
from pathlib import Path

from wai.projects import ProjectDiscovery, ProjectInfo
from wai.utils.registry import load_registry


def _init_hub(hub_path: Path) -> None:
    registry_dir = hub_path / "registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    registry = {"version": "2.0", "projects": [], "groups": {}}
    (registry_dir / "wheel-projects.json").write_text(json.dumps(registry))


def test_register_selected_projects_initializes_spoke(tmp_path: Path) -> None:
    hub_path = tmp_path / "hub"
    hub_path.mkdir()
    _init_hub(hub_path)

    project_dir = tmp_path / "demo-project"
    project_dir.mkdir()

    project = ProjectInfo(
        path=project_dir,
        name="demo-project",
        project_type=["Git"]
    )

    discovery = ProjectDiscovery()
    count = discovery.register_selected_projects([project], hub_path)

    assert count == 1
    assert (project_dir / "WAI-Spoke").is_dir()
    assert (project_dir / "WAI-Spoke" / "seed" / "ingest").is_dir()

    registry = load_registry(hub_path)
    paths = [p["path"] for p in registry["projects"]]
    assert str(project_dir.resolve()) in paths

from pathlib import Path

from wai.hub import HubManager


def _write_hub(hub_path: Path, project_path: Path, include_registry: bool) -> None:
    (hub_path / "registry").mkdir(parents=True, exist_ok=True)
    (hub_path / "hub-profile.json").write_text("{}\n")
    if include_registry:
        (hub_path / "registry" / "wheel-projects.json").write_text(
            "{\n"
            '  "version": "2.0",\n'
            '  "projects": [\n'
            f'    {{"path": "{project_path}"}}\n'
            "  ]\n"
            "}\n"
        )


def test_auto_discover_prefers_hub_with_project_registry(tmp_path: Path) -> None:
    project_path = tmp_path / "condoshield-crm"
    project_path.mkdir()

    default_hub = tmp_path / "wheelwright-hub"
    default_hub.mkdir()
    _write_hub(default_hub, project_path, include_registry=False)

    preferred_hub = tmp_path / "wheelwright-ai" / "hub"
    _write_hub(preferred_hub, project_path, include_registry=True)

    manager = HubManager()
    discovered = manager.auto_discover_hub(project_path, verbose=False)

    assert discovered == preferred_hub

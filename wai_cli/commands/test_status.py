from pathlib import Path

from wai_cli.commands.status import show_status


def _write_state(path: Path, hub_path: str) -> None:
    path.write_text(
        "{\n"
        '  "wheelwright": {\n'
        f'    "hub_path": "{hub_path}"\n'
        "  },\n"
        '  "_project_foundation": {\n'
        "    \"completed\": false\n"
        "  }\n"
        "}\n"
    )


def _write_hub(hub_path: Path, project_path: Path) -> None:
    (hub_path / "registry").mkdir(parents=True)
    (hub_path / "hub-profile.json").write_text("{}\n")
    (hub_path / "registry" / "wheel-projects.json").write_text(
        "{\n"
        '  "version": "2.0",\n'
        '  "projects": [\n'
        f'    {{"path": "{project_path}"}}\n'
        "  ]\n"
        "}\n"
    )


def test_status_updates_hub_path(tmp_path: Path) -> None:
    project_path = tmp_path / "condoshield-crm"
    spoke_dir = project_path / "WAI-Spoke"
    spoke_dir.mkdir(parents=True)

    bad_hub = tmp_path / "wheelwright-hub"
    bad_hub.mkdir()
    (bad_hub / "hub-profile.json").write_text("{}\n")

    good_hub = tmp_path / "wheelwright-ai" / "hub"
    _write_hub(good_hub, project_path)

    state_path = spoke_dir / "WAI-State.json"
    _write_state(state_path, str(bad_hub))

    show_status(str(project_path))

    updated = state_path.read_text()
    assert str(good_hub) in updated

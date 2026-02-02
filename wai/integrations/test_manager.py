from pathlib import Path

from wai.integrations.manager import IDEManager


def test_manager_lists_integrations(tmp_path: Path) -> None:
    root = tmp_path
    wai_spoke = root / "WAI-Spoke"
    wai_spoke.mkdir()
    (wai_spoke / "WAI-State.json").write_text("{}")

    manager = IDEManager(root)
    integrations = manager.all_integrations

    assert isinstance(integrations, list)

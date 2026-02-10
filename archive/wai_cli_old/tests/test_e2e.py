"""End-to-end tests for new CLI workflows."""

from wai.cli.main import main
from wai.cli.tests.e2e_helpers import setup_workspace


def test_e2e_registry_teach_learn(tmp_path, monkeypatch):
    workspace = tmp_path / "e2e"
    paths = setup_workspace(workspace)

    monkeypatch.chdir(paths.workspace)
    monkeypatch.setenv("WHEELWRIGHT_HUB", str(paths.hub))

    assert main(["list"]) == 0
    assert main(["registry"]) == 0
    assert main(["teach", "alpha", "--force"]) == 0
    assert main(["learn", "alpha", "--force"]) == 0

    assert (paths.spoke / "WAI-Guide.md").exists()
    assert (paths.spoke / "WAI-Spoke" / "observations.jsonl").exists()

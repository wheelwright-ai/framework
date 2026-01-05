from pathlib import Path

from wai_cli.integrations.vscode import VSCodeIntegration


def test_vscode_generate_config_recovers_from_invalid_json(tmp_path: Path) -> None:
    root = tmp_path
    (root / "WAI-Spoke").mkdir()
    vscode_dir = root / ".vscode"
    vscode_dir.mkdir()
    settings = vscode_dir / "settings.json"
    settings.write_text("{ invalid json\n")

    integration = VSCodeIntegration(root)
    content = integration.generate_config()

    backups = list(vscode_dir.glob("settings.json.bak-*"))
    assert backups, "Expected backup for invalid settings.json"
    assert "wai.integration" in content

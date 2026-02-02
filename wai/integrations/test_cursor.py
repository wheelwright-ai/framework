from pathlib import Path

from wai.integrations.cursor import CursorIntegration


def test_cursor_generate_config(tmp_path: Path) -> None:
    root = tmp_path
    wai_spoke = root / "WAI-Spoke"
    wai_spoke.mkdir()
    (wai_spoke / "WAI-State.json").write_text('{"wheel": {"name": "Demo", "description": "Desc"}}')

    integration = CursorIntegration(root)
    content = integration.generate_config()

    assert "WAI-Spoke" in content

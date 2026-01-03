from pathlib import Path

from wai_cli.integrations.web_llm import WebLLMIntegration


def test_web_llm_generate_instructions(tmp_path: Path) -> None:
    root = tmp_path
    wai_spoke = root / "WAI-Spoke"
    wai_spoke.mkdir()
    (wai_spoke / "WAI-State.json").write_text('{"wheel": {"name": "Demo", "description": "Desc"}}')

    integration = WebLLMIntegration(root)
    content = integration.generate_config()

    assert "WAI-Spoke" in content

from pathlib import Path

from wai_cli.bootstrap import refresh_bootstrap


def test_refresh_bootstrap_writes_files(tmp_path):
    assert refresh_bootstrap(tmp_path, verbose=False) is True
    readme = tmp_path / "bootstrap" / "README.md"
    template = tmp_path / "bootstrap" / "WAI-Minimal.template.md"
    assert readme.exists()
    assert template.exists()
    assert readme.read_text().strip() != ""
    assert template.read_text().strip() != ""

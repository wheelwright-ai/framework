from pathlib import Path

from wai.init import init_spoke


def test_init_spoke_creates_seed_folders_and_snapshot(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    init_spoke(project_dir, is_framework=False, verbose=False)

    wai_spoke = project_dir / "WAI-Spoke"
    assert (wai_spoke / "seed" / "ingest").is_dir()
    assert (wai_spoke / "seed" / "reference").is_dir()
    assert (wai_spoke / "reference").is_dir()
    assert (wai_spoke / "seed" / "README.md").exists()
    assert (wai_spoke / "WAI-Workspace.cmd").exists()

    state_md = wai_spoke / "WAI-State.md"
    content = state_md.read_text()
    assert "Project Discovery Snapshot" in content


def test_init_spoke_snapshot_includes_readme_preview(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "README.md").write_text("Hello world\nSecond line\n")

    init_spoke(project_dir, is_framework=False, verbose=False)

    state_md = project_dir / "WAI-Spoke" / "WAI-State.md"
    content = state_md.read_text()
    assert "README preview" in content
    assert "Hello world" in content

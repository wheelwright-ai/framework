from pathlib import Path

from wai_cli.closeout import CloseoutProcessor
from wai_cli.init import init_spoke


def test_closeout_processes_seed_cleanup(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    init_spoke(project_dir, is_framework=False, verbose=False)

    wai_spoke = project_dir / "WAI-Spoke"
    seed_ingest = wai_spoke / "seed" / "ingest"
    seed_ingest.mkdir(parents=True, exist_ok=True)
    (seed_ingest / "notes.md").write_text("Seeded notes")

    processor = CloseoutProcessor(project_dir)
    results = processor.process_closeout(interactive=False)

    assert "steps_completed" in results
    assert not (seed_ingest / "notes.md").exists()

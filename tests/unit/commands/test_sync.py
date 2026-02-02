from pathlib import Path

from wai.commands.sync import sync_spoke


def test_sync_spoke_handles_missing_hub(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    sync_spoke(all_spokes=False)

from pathlib import Path

from wai.rebalancer import FileRebalancer


def test_scan_unknown_files_ignores_known_dirs(tmp_path: Path) -> None:
    wai_spoke = tmp_path / "WAI-Spoke"
    wai_spoke.mkdir()

    (wai_spoke / "hooks").mkdir()
    (wai_spoke / "seed").mkdir()
    (wai_spoke / "reference").mkdir()

    rebalancer = FileRebalancer(wai_spoke)
    unknown = rebalancer.scan_unknown_files()

    assert unknown == []

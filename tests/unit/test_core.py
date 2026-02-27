import json
from pathlib import Path

import pytest

try:
    from wai.core import WheelwrightCLI
    HAS_GITPYTHON = True
except ImportError:
    HAS_GITPYTHON = False

pytestmark = pytest.mark.skipif(not HAS_GITPYTHON, reason="GitPython not installed")


def test_get_latest_baseline_summary(tmp_path: Path) -> None:
    spoke_dir = tmp_path / "spoke"
    wai_spoke = spoke_dir / "WAI-Spoke"
    wai_spoke.mkdir(parents=True)

    log_entry = {
        "timestamp": "2026-01-02T00:00:00Z",
        "ide": "Codex CLI",
        "model": "GPT-5",
        "savings": {"percent_saved": 68.6}
    }
    log_path = wai_spoke / "WAI-Baseline-Log.jsonl"
    log_path.write_text(json.dumps(log_entry) + "\n")

    cli = WheelwrightCLI()
    summary = cli._get_latest_baseline_summary(spoke_dir)

    assert "Codex CLI" in summary
    assert "GPT-5" in summary
    assert "68.6%" in summary


def test_is_within_path(tmp_path: Path) -> None:
    cli = WheelwrightCLI()
    parent = tmp_path / "parent"
    child = parent / "child" / "deep"
    parent.mkdir()
    child.mkdir(parents=True)

    assert cli._is_within_path(child, parent) is True
    assert cli._is_within_path(parent, child) is False


def test_is_within_path_unrelated(tmp_path: Path) -> None:
    cli = WheelwrightCLI()
    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"
    dir_a.mkdir()
    dir_b.mkdir()

    assert cli._is_within_path(dir_a, dir_b) is False


def test_format_datetime_iso() -> None:
    cli = WheelwrightCLI()
    result = cli._format_datetime("2026-02-27T22:00:00+00:00")
    assert "2026-02-27" in result
    assert "22:00 UTC" in result


def test_format_datetime_z_suffix() -> None:
    cli = WheelwrightCLI()
    result = cli._format_datetime("2026-02-27T22:00:00Z")
    assert "2026-02-27" in result


def test_format_datetime_empty() -> None:
    cli = WheelwrightCLI()
    assert cli._format_datetime("") == "Unknown"
    assert cli._format_datetime(None) == "Unknown"


def test_format_datetime_invalid() -> None:
    cli = WheelwrightCLI()
    result = cli._format_datetime("not-a-date")
    assert result == "not-a-date"  # Returns input on parse failure


def test_get_latest_baseline_summary_no_log(tmp_path: Path) -> None:
    spoke_dir = tmp_path / "spoke"
    wai_spoke = spoke_dir / "WAI-Spoke"
    wai_spoke.mkdir(parents=True)

    cli = WheelwrightCLI()
    summary = cli._get_latest_baseline_summary(spoke_dir)

    assert summary is None or "No baseline" in str(summary) or summary == ""

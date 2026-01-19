from pathlib import Path

from wai_cli.metrics import MetricsTracker


def test_metrics_tracker_baseline_toggle(tmp_path: Path) -> None:
    wai_spoke = tmp_path / "WAI-Spoke"
    wai_spoke.mkdir()
    (wai_spoke / "WAI-State.json").write_text("{}")

    tracker = MetricsTracker(wai_spoke)
    enabled = tracker.enable_baseline_mode()
    disabled = tracker.disable_baseline_mode()

    assert enabled.get("enabled") is True
    assert disabled.get("disabled") is True

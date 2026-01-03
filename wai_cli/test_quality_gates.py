from pathlib import Path

from wai_cli.quality_gates import QualityGates


def test_quality_gates_run_all_gates(tmp_path: Path) -> None:
    spoke_dir = tmp_path / "spoke"
    wai_spoke = spoke_dir / "WAI-Spoke"
    wai_spoke.mkdir(parents=True)
    (wai_spoke / "WAI-State.json").write_text("{}")

    gates = QualityGates(spoke_dir)
    result = gates.run_all_gates(skip_minor=True)

    assert "passed" in result
    assert "gates" in result

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from wai.closeout import CloseoutWorkflow


def test_generate_session_id() -> None:
    with patch('wai.closeout.get_logger'), \
         patch('wai.closeout.get_config'), \
         patch('wai.closeout.create_git_ops'):
        workflow = CloseoutWorkflow(repo_path="/tmp/fake")
    assert workflow.session_id.startswith("closeout-")
    assert len(workflow.session_id) > len("closeout-")


def test_find_spoke_path(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    wai_spoke = project_dir / "WAI-Spoke"
    wai_spoke.mkdir(parents=True)

    with patch('wai.closeout.get_logger'), \
         patch('wai.closeout.get_config'), \
         patch('wai.closeout.create_git_ops'):
        workflow = CloseoutWorkflow(repo_path=str(project_dir))
    result = workflow._find_spoke_path()
    assert result == wai_spoke


def test_find_spoke_path_not_found(tmp_path: Path) -> None:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with patch('wai.closeout.get_logger'), \
         patch('wai.closeout.get_config'), \
         patch('wai.closeout.create_git_ops'):
        workflow = CloseoutWorkflow(repo_path=str(empty_dir))
    try:
        workflow._find_spoke_path()
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "WAI-Spoke not found" in str(e)

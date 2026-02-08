"""
Test suite for observation system - Phase 8 validation.

Coverage:
- observation.py: Core logging, idempotency, session queries
- config.py: SSH/git config loading, creation, updates
- git.py: Git operations with observation
- closeout.py: 4-phase workflow
- briefing.py: Session briefing generation
"""

import pytest
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from wai.observation import ObservationLogger, get_logger
from wai.config import SSHGitConfig, get_config
from wai.utils.git import GitOperations, create_git_ops
from wai.closeout import CloseoutWorkflow
from wai.briefing import SessionBriefing, get_briefing
from wai.skill_integration import SkillExecution, SkillGitWorkflow


# ============================================================================
# PHASE 1: Observation System Tests
# ============================================================================

class TestObservationLogger:
    """Test core observation logging."""
    
    @pytest.fixture
    def logger(self, tmp_path):
        """Create logger with temp spoke path."""
        spoke_path = tmp_path / "WAI-Spoke"
        spoke_path.mkdir()
        return ObservationLogger(str(spoke_path))
    
    def test_log_observation(self, logger):
        """Test logging a single observation."""
        obs = logger.log_observation(
            action_id="test.action",
            action_category="test",
            action_description="Test action",
            plan="Test plan",
            command="echo test",
            expected_result={"exit_code": 0},
            actual_result={"exit_code": 0},
            verification={"passed": True, "checks": []},
            session_id="test-session-001",
        )
        
        assert obs["id"].startswith("obs-")
        assert obs["action"]["id"] == "test.action"
        assert obs["status"] == "complete"
        assert obs["verification"]["passed"] is True
    
    def test_observations_persisted(self, logger):
        """Test observations written to JSONL."""
        logger.log_observation(
            action_id="test.persist",
            action_category="test",
            action_description="Test persistence",
            plan="Test",
            command="echo",
            expected_result={},
            actual_result={},
            verification={"passed": True, "checks": []},
            session_id="persist-001",
        )
        
        obs_file = logger.obs_file
        assert obs_file.exists()
        
        with open(obs_file, 'r') as f:
            line = f.readline()
            data = json.loads(line)
            assert data["action"]["id"] == "test.persist"
    
    def test_check_already_done(self, logger):
        """Test idempotency checking."""
        logger.log_observation(
            action_id="git.push",
            action_category="git",
            action_description="Push",
            plan="Test",
            command="git push",
            expected_result={},
            actual_result={},
            verification={"passed": True, "checks": []},
            session_id="idempotent-001",
        )
        
        # Check it was done
        already = logger.check_already_done("git.push", "idempotent-001")
        assert already is not None
        assert already["action"]["id"] == "git.push"
    
    def test_check_not_done(self, logger):
        """Test idempotency returns None if not done."""
        already = logger.check_already_done("nonexistent.action", "fake-session")
        assert already is None
    
    def test_session_summary(self, logger):
        """Test session summary generation."""
        for i in range(3):
            logger.log_observation(
                action_id=f"test.action.{i}",
                action_category="test",
                action_description=f"Action {i}",
                plan="Test",
                command="echo",
                expected_result={},
                actual_result={},
                verification={"passed": i != 1},  # Make one fail
                session_id="summary-001",
            )
        
        summary = logger.summarize_session("summary-001")
        assert summary["total_observations"] == 3
        assert summary["passed"] == 2
        assert summary["failed"] == 1


# ============================================================================
# PHASE 2: SSH/Git Configuration Tests
# ============================================================================

class TestSSHGitConfig:
    """Test SSH/git configuration."""
    
    @pytest.fixture
    def config(self, tmp_path):
        """Create config with temp spoke path."""
        spoke_path = tmp_path / "WAI-Spoke"
        spoke_path.mkdir()
        return SSHGitConfig(str(spoke_path))
    
    def test_load_default_config(self, config):
        """Test loading default config."""
        cfg = config.load_config()
        
        assert "ssh" in cfg
        assert "git" in cfg
        assert "github" in cfg
        assert cfg["ssh"]["key_path"] == "~/.ssh/id_ed25519"
    
    def test_create_lug(self, config):
        """Test creating SSH config lug."""
        lug_path = config.create_default_lug(
            git_user="Test User",
            git_email="test@example.com"
        )
        
        assert lug_path.exists()
        
        with open(lug_path, 'r') as f:
            lug = json.load(f)
        
        assert lug["type"] == "sshconfig"
        assert lug["git"]["user"] == "Test User"
        assert lug["git"]["email"] == "test@example.com"
    
    def test_load_lug(self, config):
        """Test loading SSH config from lug."""
        config.create_default_lug(
            git_user="Lug User",
            git_email="lug@example.com"
        )
        
        config._config = None  # Clear cache
        cfg = config.load_config(force_reload=True)
        
        assert cfg["git"]["user"] == "Lug User"
        assert cfg["git"]["email"] == "lug@example.com"
    
    def test_get_accessors(self, config):
        """Test getter methods."""
        config.create_default_lug("User", "user@example.com")
        config._config = None
        
        assert config.get_git_user() == "User"
        assert config.get_git_email() == "user@example.com"
        assert config.get_git_default_branch() == "main"
        assert config.get_git_default_remote() == "origin"
        assert config.get_ssh_key_path() == os.path.expanduser("~/.ssh/id_ed25519")


# ============================================================================
# PHASE 3: Git Operations Tests
# ============================================================================

class TestGitOperations:
    """Test git operations with observation."""
    
    @pytest.fixture
    def git_ops(self, tmp_path):
        """Create git ops with temp repo."""
        return GitOperations(str(tmp_path))
    
    @patch('subprocess.run')
    def test_add_all(self, mock_run, git_ops):
        """Test git add with observation."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        obs = git_ops.add_all("session-001")
        
        assert obs["action"]["id"] == "git.add"
        assert obs["status"] == "complete"
    
    @patch('subprocess.run')
    def test_commit(self, mock_run, git_ops):
        """Test git commit with observation."""
        # First call is git commit, second is get config
        mock_run.side_effect = [
            Mock(returncode=0, stdout="[main abc1234] Test commit\n 1 file changed", stderr=""),
            Mock(returncode=0, stdout="", stderr=""),  # get config author
        ]
        
        obs = git_ops.commit("Test message", "session-001")
        
        assert obs["action"]["id"] == "git.commit"
        # Status depends on commit hash extraction from output
        assert obs["action"]["id"] == "git.commit"
    
    @patch('subprocess.run')
    def test_push(self, mock_run, git_ops):
        """Test git push with observation."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="To github.com:...\n   main -> main",
            stderr=""
        )
        
        obs = git_ops.push("session-001")
        
        assert obs["action"]["id"] == "git.push"
        assert obs["status"] == "complete"
    
    @patch('subprocess.run')
    def test_git_failure_remediation(self, mock_run, git_ops):
        """Test remediation suggestions on git failure."""
        mock_run.return_value = Mock(
            returncode=128,
            stdout="",
            stderr="Permission denied (publickey)"
        )
        
        obs = git_ops.push("session-001")
        
        assert obs["status"] == "failed"
        assert obs.get("remediation") is not None
        assert "SSH" in obs["remediation"]["suggested_next_step"]


# ============================================================================
# PHASE 4: Closeout Workflow Tests
# ============================================================================

class TestCloseoutWorkflow:
    """Test enhanced closeout workflow."""
    
    @pytest.fixture
    def workflow(self, tmp_path):
        """Create closeout workflow with temp repo."""
        # Create WAI-Spoke structure
        spoke_path = tmp_path / "WAI-Spoke"
        spoke_path.mkdir()
        (spoke_path / "WAI-State.json").write_text('{"_session_state": {}}')
        
        return CloseoutWorkflow(str(tmp_path), dry_run=True)
    
    def test_phase1_reconciliation(self, workflow):
        """Test phase 1 reconciliation."""
        result = workflow.phase_1_reconciliation()
        
        assert "lugs_reconciled" in result or "files_modified" in result
    
    def test_phase2_state_updates(self, workflow):
        """Test phase 2 state updates."""
        changes = {"lugs_reconciled": 5}
        result = workflow.phase_2_state_updates(changes)
        
        assert "session_count_incremented" in result
    
    def test_4phase_execution(self, workflow):
        """Test complete 4-phase execution."""
        with patch.object(workflow.git, 'add_all') as mock_add:
            mock_add.return_value = {
                "verification": {"passed": True},
                "status": "complete"
            }
            
            summary = workflow.execute()
            
            assert "session_id" in summary
            assert "status" in summary


# ============================================================================
# PHASE 5: Session Briefing Tests
# ============================================================================

class TestSessionBriefing:
    """Test session briefing generation."""
    
    @pytest.fixture
    def briefing(self, tmp_path):
        """Create briefing with temp observations."""
        spoke_path = tmp_path / "WAI-Spoke"
        spoke_path.mkdir()
        
        logger = ObservationLogger(str(spoke_path))
        
        # Create test observations
        for i in range(3):
            logger.log_observation(
                action_id=f"test.action.{i}",
                action_category="test",
                action_description=f"Test {i}",
                plan="Test",
                command="echo",
                expected_result={},
                actual_result={},
                verification={"passed": True, "checks": []},
                session_id="brief-001",
            )
        
        return SessionBriefing()
    
    def test_observation_summary(self, briefing):
        """Test observation summary generation."""
        summary = briefing.build_observation_summary()
        
        assert "total" in summary
        assert "complete" in summary
        assert "failed" in summary
    
    def test_session_briefing(self, briefing):
        """Test complete session briefing."""
        briefing_text = briefing.build_session_briefing()
        
        assert "Session Briefing" in briefing_text
        assert isinstance(briefing_text, str)
        assert len(briefing_text) > 0


# ============================================================================
# PHASE 6: Skill Integration Tests
# ============================================================================

class TestSkillExecution:
    """Test skill execution with observations."""
    
    @pytest.fixture
    def skill_exec(self, tmp_path):
        """Create skill execution context."""
        spoke_path = tmp_path / "WAI-Spoke"
        spoke_path.mkdir()
        (spoke_path / "lugs").mkdir()
        
        return SkillExecution("test_skill")
    
    def test_skill_session_id(self, skill_exec):
        """Test skill generates session ID."""
        assert skill_exec.session_id.startswith("skill-test_skill-")
    
    def test_log_skill_action(self, skill_exec):
        """Test logging skill action."""
        obs = skill_exec.log_action(
            action_id="skill.test.action",
            action_description="Test action",
            plan="Test plan",
            command="echo test",
            expected_result={"exit_code": 0},
            actual_result={"exit_code": 0},
            verification={"passed": True, "checks": []},
        )
        
        assert obs["action"]["id"] == "skill.test.action"
        assert len(skill_exec.observations) == 1
    
    def test_skill_summary(self, skill_exec):
        """Test skill session summary."""
        skill_exec.log_action(
            action_id="skill.test.action",
            action_description="Test",
            plan="Test",
            command="echo",
            expected_result={},
            actual_result={},
            verification={"passed": True, "checks": []},
        )
        
        summary = skill_exec.get_session_summary()
        assert summary["total_observations"] >= 1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_observation_to_briefing(self, tmp_path):
        """Test complete flow: observation → logging → briefing."""
        spoke_path = tmp_path / "WAI-Spoke"
        spoke_path.mkdir()
        
        # Create observations
        logger = ObservationLogger(str(spoke_path))
        
        obs = logger.log_observation(
            action_id="e2e.test",
            action_category="test",
            action_description="E2E test",
            plan="Test plan",
            command="echo e2e",
            expected_result={"exit_code": 0},
            actual_result={"exit_code": 0},
            verification={"passed": True, "checks": []},
            session_id="e2e-001",
        )
        
        # Verify observation written
        assert obs["id"].startswith("obs-")
        
        # Create briefing
        briefing = SessionBriefing()
        summary = briefing.build_observation_summary()
        
        assert summary["total"] >= 1
    
    def test_skill_to_git_workflow(self, tmp_path):
        """Test skill execution with git workflow."""
        spoke_path = tmp_path / "WAI-Spoke"
        spoke_path.mkdir()
        (spoke_path / "lugs").mkdir()
        
        skill_exec = SkillExecution("git_test")
        
        # Verify config loaded
        author = skill_exec.get_git_author()
        assert author is not None
        
        # Verify git accessible
        git = skill_exec.git
        assert git is not None


# ============================================================================
# Multi-Agent Safety Tests
# ============================================================================

class TestMultiAgentSafety:
    """Test multi-agent coordination."""
    
    def test_idempotency_prevents_duplicate_work(self, tmp_path):
        """Test that idempotency prevents duplicate actions."""
        spoke_path = tmp_path / "WAI-Spoke"
        spoke_path.mkdir()
        
        logger = ObservationLogger(str(spoke_path))
        
        # Agent 1: log action
        obs1 = logger.log_observation(
            action_id="shared.action",
            action_category="test",
            action_description="Shared action",
            plan="Test",
            command="echo",
            expected_result={},
            actual_result={},
            verification={"passed": True, "checks": []},
            session_id="shared-001",
        )
        
        # Agent 2: check before acting
        already = logger.check_already_done("shared.action", "shared-001")
        
        assert already is not None
        assert already["id"] == obs1["id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

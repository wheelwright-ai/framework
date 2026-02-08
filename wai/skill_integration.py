"""
Skill Integration Framework - Standardize observation logging across all skills.

Skills use this to consistently log observations, load config, and check idempotency.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from wai.observation import get_logger
from wai.config import get_config
from wai.utils.git import create_git_ops


class SkillExecution:
    """Execution context for a skill with observation support."""
    
    def __init__(self, skill_name: str, skill_action: str = None):
        """
        Initialize skill execution.
        
        Args:
            skill_name: Name of skill (e.g., "init", "sync", "teach")
            skill_action: Specific action within skill
        """
        self.skill_name = skill_name
        self.skill_action = skill_action or skill_name
        self.session_id = self._generate_session_id()
        self.logger = get_logger()
        self.config = get_config()
        self.git = create_git_ops()
        self.observations = []

    def _generate_session_id(self) -> str:
        """Generate session ID: {skill}-{timestamp}."""
        now = datetime.now(timezone.utc)
        return f"skill-{self.skill_name}-{now.strftime('%Y%m%d-%H%M%S')}"

    def get_git_author(self) -> str:
        """Get git author from config."""
        return self.config.get_git_author()

    def get_git_branch(self) -> str:
        """Get default git branch from config."""
        return self.config.get_git_default_branch()

    def get_git_remote(self) -> str:
        """Get default git remote from config."""
        return self.config.get_git_default_remote()

    def check_idempotency(self, action_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if action already completed (idempotency).
        
        Args:
            action_id: Action to check
        
        Returns:
            Previous observation if completed, None otherwise
        """
        return self.logger.check_already_done(action_id, self.session_id)

    def log_action(
        self,
        action_id: str,
        action_description: str,
        plan: str,
        command: str,
        expected_result: Dict[str, Any],
        actual_result: Dict[str, Any],
        verification: Dict[str, Any],
        remediation: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Log a skill action with observation.
        
        Args:
            action_id: Unique action (e.g., "skill.init.create_dirs")
            action_description: Human description
            plan: What we intended to do
            command: Command executed
            expected_result: Expected outcome
            actual_result: Actual outcome
            verification: Verification checks
            remediation: Remediation steps if failed
            tags: Labels
        
        Returns:
            Observation dict
        """
        obs = self.logger.log_observation(
            action_id=action_id,
            action_category="skill",
            action_description=action_description,
            plan=plan,
            command=command,
            expected_result=expected_result,
            actual_result=actual_result,
            verification=verification,
            session_id=self.session_id,
            agent=f"Skill: {self.skill_name}",
            remediation=remediation,
            tags=tags or [self.skill_name],
        )
        
        self.observations.append(obs)
        return obs

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of all observations in this session."""
        return self.logger.summarize_session(self.session_id)

    def get_failed_actions(self) -> List[Dict[str, Any]]:
        """Get all failed observations in this session."""
        all_failed = self.logger.get_failed_observations()
        return [obs for obs in all_failed if obs["session_id"] == self.session_id]

    def display_summary(self):
        """Display session summary to user."""
        summary = self.get_session_summary()
        
        print(f"\n{'='*60}")
        print(f"Skill: {self.skill_name}")
        print(f"Session: {self.session_id}")
        print(f"{'='*60}")
        print(f"Total actions: {summary.get('total_observations', 0)}")
        print(f"Passed: {summary.get('passed', 0)}")
        print(f"Failed: {summary.get('failed', 0)}")
        
        failed = self.get_failed_actions()
        if failed:
            print(f"\n⚠️  Failed Actions:")
            for obs in failed:
                print(f"  - {obs['action']['id']}: {obs['action']['description']}")
                if obs.get("remediation"):
                    print(f"    → {obs['remediation'].get('suggested_next_step', 'See logs')}")
        
        print()


class SkillGitWorkflow:
    """Workflow helper for skills that use git operations."""
    
    def __init__(self, skill_exec: SkillExecution):
        """
        Initialize git workflow.
        
        Args:
            skill_exec: SkillExecution context
        """
        self.skill_exec = skill_exec
        self.git = skill_exec.git
        self.logger = skill_exec.logger

    def add_commit_push(
        self,
        message: str,
        check_idempotency: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute git add → commit → push with observation.
        
        Args:
            message: Commit message
            check_idempotency: If True, skip if already done
        
        Returns:
            Summary dict with all observations
        """
        session_id = self.skill_exec.session_id
        
        # Check idempotency
        if check_idempotency:
            already = self.skill_exec.check_idempotency("git.workflow")
            if already and already["idempotency"]["safe_to_retry"]:
                return {"skipped": True, "reason": "Already completed"}
        
        # Stage
        obs_add = self.git.add_all(session_id, agent=self.skill_exec.skill_name)
        if not obs_add["verification"]["passed"]:
            return {
                "success": False,
                "phase": "add",
                "obs": obs_add,
                "remediation": obs_add.get("remediation")
            }
        
        # Commit
        obs_commit = self.git.commit(message, session_id, agent=self.skill_exec.skill_name)
        if not obs_commit["verification"]["passed"]:
            return {
                "success": False,
                "phase": "commit",
                "obs": obs_commit,
                "remediation": obs_commit.get("remediation")
            }
        
        # Push
        obs_push = self.git.push(session_id=session_id, agent=self.skill_exec.skill_name)
        if not obs_push["verification"]["passed"]:
            return {
                "success": False,
                "phase": "push",
                "obs": obs_push,
                "remediation": obs_push.get("remediation")
            }
        
        # All succeeded
        return {
            "success": True,
            "phase": "complete",
            "observations": [obs_add, obs_commit, obs_push],
        }

    def display_result(self, result: Dict[str, Any]):
        """Display git workflow result to user."""
        if result.get("skipped"):
            print(f"✓ Git workflow already completed, skipping")
            return
        
        if result.get("success"):
            print(f"✓ Git workflow complete")
            print(f"  - Added files")
            print(f"  - Committed: {result['observations'][1]['verification'].get('commit_hash', '?')}")
            print(f"  - Pushed to remote")
        else:
            phase = result.get("phase", "unknown")
            print(f"✗ Git workflow failed at: {phase}")
            
            if result.get("remediation"):
                rem = result["remediation"]
                print(f"  Issue: {rem.get('issue', 'Unknown')}")
                print(f"  Fix: {rem.get('suggested_next_step', 'See logs')}")
                
                if rem.get("recovery_steps"):
                    print(f"  Recovery steps:")
                    for step in rem["recovery_steps"]:
                        print(f"    - {step}")


def create_skill_execution(skill_name: str) -> SkillExecution:
    """Create skill execution context."""
    return SkillExecution(skill_name)


def create_git_workflow(skill_exec: SkillExecution) -> SkillGitWorkflow:
    """Create git workflow helper for skill."""
    return SkillGitWorkflow(skill_exec)

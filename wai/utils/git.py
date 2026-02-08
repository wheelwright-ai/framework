"""
Git operations with observation logging - All git commands observed for reliability.
"""

import subprocess
import os
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime, timezone

from wai.observation import get_logger
from wai.config import get_config


class GitOperations:
    """Execute git operations with observation logging."""

    def __init__(self, repo_path: str = "."):
        """
        Initialize git operations.
        
        Args:
            repo_path: Path to git repository root
        """
        self.repo_path = repo_path
        self.config = get_config()
        self.logger = get_logger()

    def _run_command(
        self,
        command: List[str],
        cwd: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """
        Run a command and capture output.
        
        Returns:
            (exit_code, stdout, stderr)
        """
        import time
        start = time.time()
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            duration_ms = int((time.time() - start) * 1000)
            return result.returncode, result.stdout, result.stderr, duration_ms
        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start) * 1000)
            return 124, "", "Command timeout after 30s", duration_ms
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            return 255, "", str(e), duration_ms

    def add_all(self, session_id: str, agent: str = "Unknown") -> Dict[str, Any]:
        """
        Stage all changes (git add -A) with observation.
        
        Args:
            session_id: Session this action belongs to
            agent: Name of agent performing action
        
        Returns:
            Observation dict
        """
        command = ["git", "add", "-A"]
        
        exit_code, stdout, stderr, duration_ms = self._run_command(command)
        
        # Verify by checking git status
        status_code, status_out, status_err, _ = self._run_command(["git", "status", "--porcelain"])
        
        expected = {
            "exit_code": 0,
            "output_contains": [],
        }
        
        actual = {
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "duration_ms": duration_ms,
            "has_staged_changes": status_code == 0,
        }
        
        verification = {
            "passed": exit_code == 0,
            "checks": [
                {
                    "name": "exit_code_zero",
                    "passed": exit_code == 0,
                }
            ]
        }
        
        obs = self.logger.log_observation(
            action_id="git.add",
            action_category="git",
            action_description="Stage all changes (git add -A)",
            plan="Prepare all modified files for commit",
            command=" ".join(command),
            expected_result=expected,
            actual_result=actual,
            verification=verification,
            session_id=session_id,
            agent=agent,
            tags=["git-ops", "closeout"],
        )
        
        return obs

    def commit(
        self,
        message: str,
        session_id: str,
        agent: str = "Unknown",
    ) -> Dict[str, Any]:
        """
        Commit staged changes with observation.
        
        Args:
            message: Commit message
            session_id: Session this action belongs to
            agent: Name of agent performing action
        
        Returns:
            Observation dict
        """
        git_author = self.config.get_git_author()
        command = [
            "git",
            "commit",
            "-m",
            message,
            "--author",
            git_author,
        ]
        
        exit_code, stdout, stderr, duration_ms = self._run_command(command)
        
        expected = {
            "exit_code": 0,
            "output_contains": ["create mode", "changed", "insertion"],
        }
        
        actual = {
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "duration_ms": duration_ms,
        }
        
        # Extract commit hash if successful
        commit_hash = None
        if exit_code == 0 and stdout:
            parts = stdout.split()
            for part in parts:
                if len(part) == 7 and all(c in "0123456789abcdef" for c in part):
                    commit_hash = part
                    break
        
        verification = {
            "passed": exit_code == 0 and commit_hash is not None,
            "checks": [
                {
                    "name": "exit_code_zero",
                    "passed": exit_code == 0,
                },
                {
                    "name": "commit_hash_found",
                    "passed": commit_hash is not None,
                }
            ],
            "commit_hash": commit_hash,
        }
        
        remediation = None
        if exit_code != 0:
            if "nothing to commit" in stderr.lower():
                remediation = {
                    "issue": "Nothing to commit",
                    "suggested_next_step": "Check git status - there may be no staged changes",
                }
            elif "Author identity unknown" in stderr:
                remediation = {
                    "issue": "Git author not configured",
                    "suggested_next_step": "Run: git config user.name 'Name' && git config user.email 'email@example.com'",
                }
        
        obs = self.logger.log_observation(
            action_id="git.commit",
            action_category="git",
            action_description=f"Commit changes: {message[:50]}",
            plan="Create commit with all staged changes",
            command=" ".join(command),
            expected_result=expected,
            actual_result=actual,
            verification=verification,
            session_id=session_id,
            agent=agent,
            remediation=remediation,
            tags=["git-ops", "closeout"],
        )
        
        return obs

    def push(
        self,
        remote: Optional[str] = None,
        branch: Optional[str] = None,
        session_id: str = "",
        agent: str = "Unknown",
    ) -> Dict[str, Any]:
        """
        Push commits to remote with observation.
        
        Args:
            remote: Remote name (default: origin)
            branch: Branch name (default: main from config)
            session_id: Session this action belongs to
            agent: Name of agent performing action
        
        Returns:
            Observation dict
        """
        remote = remote or self.config.get_git_default_remote()
        branch = branch or self.config.get_git_default_branch()
        
        command = ["git", "push", remote, branch]
        
        exit_code, stdout, stderr, duration_ms = self._run_command(command)
        
        expected = {
            "exit_code": 0,
            "output_contains": [remote, branch],
        }
        
        actual = {
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "duration_ms": duration_ms,
        }
        
        verification = {
            "passed": exit_code == 0,
            "checks": [
                {
                    "name": "exit_code_zero",
                    "passed": exit_code == 0,
                }
            ]
        }
        
        # If successful, verify remote
        if exit_code == 0:
            verify_code, _, _, _ = self._run_command(
                ["git", "log", "-1", "--format=%H", f"{remote}/{branch}"]
            )
            verification["checks"].append({
                "name": "remote_verified",
                "passed": verify_code == 0,
            })
            verification["passed"] = verify_code == 0
        
        remediation = None
        if exit_code != 0:
            if "Permission denied" in stderr or "publickey" in stderr:
                remediation = {
                    "issue": "SSH authentication failed",
                    "suggested_next_step": "Verify SSH key: ssh -T git@github.com",
                    "recovery_steps": [
                        "1. Check SSH key exists: ls ~/.ssh/id_ed25519",
                        "2. Test SSH: ssh -T git@github.com",
                        "3. If needed: ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519",
                        "4. Add public key to GitHub Settings > SSH Keys",
                        "5. Retry: git push origin main",
                    ]
                }
            elif "non-fast-forward" in stderr:
                remediation = {
                    "issue": "Remote has newer commits",
                    "suggested_next_step": "Pull changes first: git pull --rebase origin main",
                }
        
        obs = self.logger.log_observation(
            action_id="git.push",
            action_category="git",
            action_description=f"Push to {remote}/{branch}",
            plan=f"Push commits to {remote}/{branch}",
            command=" ".join(command),
            expected_result=expected,
            actual_result=actual,
            verification=verification,
            session_id=session_id,
            agent=agent,
            idempotent=False,  # Push is not idempotent (duplicate push fails)
            remediation=remediation,
            tags=["git-ops", "closeout", "critical"],
        )
        
        return obs

    def get_status(self) -> Dict[str, Any]:
        """Get current git status."""
        exit_code, stdout, stderr, _ = self._run_command(["git", "status", "--porcelain"])
        
        return {
            "exit_code": exit_code,
            "clean": exit_code == 0 and not stdout,
            "modified_files": [line[3:] for line in stdout.split('\n') if line],
            "output": stdout,
        }

    def get_log(self, count: int = 1, format_str: str = "%H %s") -> List[str]:
        """Get commit log."""
        command = ["git", "log", f"-{count}", f"--format={format_str}"]
        exit_code, stdout, stderr, _ = self._run_command(command)
        
        if exit_code == 0:
            return [line for line in stdout.split('\n') if line]
        return []


def create_git_ops(repo_path: str = ".") -> GitOperations:
    """Create GitOperations instance."""
    return GitOperations(repo_path)

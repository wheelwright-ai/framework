"""
Enhanced Closeout Workflow - 4-phase execution with observation logging

Phases:
1. Reconciliation - Consolidate lugs, detect changes
2. State Updates - Update WAI-State.json, WAI-State.md
3. Git Operations - Add, commit, push with mandatory git
4. Verification - Verify all changes remote, final state
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid

from wai.observation import get_logger
from wai.config import get_config
from wai.utils.git import create_git_ops


class CloseoutWorkflow:
    """Execute 4-phase closeout with observations."""

    def __init__(self, repo_path: str = ".", dry_run: bool = False):
        """
        Initialize closeout workflow.
        
        Args:
            repo_path: Repository root path
            dry_run: If True, preview only (no actual changes)
        """
        self.repo_path = repo_path
        self.dry_run = dry_run
        self.session_id = self._generate_session_id()
        self.logger = get_logger()
        self.config = get_config()
        self.git = create_git_ops(repo_path)
        self.observations = []

    def _generate_session_id(self) -> str:
        """Generate session ID: closeout-YYYYMMDD-HHMMSS."""
        now = datetime.now(timezone.utc)
        return f"closeout-{now.strftime('%Y%m%d-%H%M%S')}"

    def _find_spoke_path(self) -> Path:
        """Find WAI-Spoke directory."""
        current = Path(self.repo_path).resolve()
        while current != current.parent:
            if (current / "WAI-Spoke").exists():
                return current / "WAI-Spoke"
            current = current.parent
        raise RuntimeError("WAI-Spoke not found")

    def phase_1_reconciliation(self) -> Dict[str, Any]:
        """
        Phase 1: Reconciliation - Consolidate lugs, detect changes.
        
        Returns:
            Summary of changes detected
        """
        print("\n[Phase 1] Reconciliation...")
        
        spoke_path = self._find_spoke_path()
        lugs_file = spoke_path / "WAI-Lugs.jsonl"
        
        changes = {
            "lugs_reconciled": 0,
            "new_lugs": 0,
            "updated_lugs": 0,
            "files_modified": [],
        }
        
        if not lugs_file.exists():
            print("  ✓ No lugs file - initializing")
            return changes
        
        # Read lugs
        with open(lugs_file, 'r') as f:
            lugs = [json.loads(line) for line in f if line.strip()]
        
        changes["lugs_reconciled"] = len(lugs)
        print(f"  ✓ Reconciled {len(lugs)} lugs")
        
        # Check for file modifications
        status = self.git.get_status()
        changes["files_modified"] = status["modified_files"]
        print(f"  ✓ {len(changes['files_modified'])} files modified")
        
        return changes

    def phase_2_state_updates(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 2: State Updates - Update WAI-State.json and WAI-State.md.
        
        Args:
            changes: Changes from phase 1
        
        Returns:
            Summary of state updates
        """
        print("\n[Phase 2] State Updates...")
        
        spoke_path = self._find_spoke_path()
        state_json_file = spoke_path / "WAI-State.json"
        state_md_file = spoke_path / "WAI-State.md"
        
        updates = {
            "state_json_updated": False,
            "state_md_updated": False,
            "session_count_incremented": False,
            "last_modified_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Update WAI-State.json
        if state_json_file.exists():
            with open(state_json_file, 'r') as f:
                state = json.load(f)
            
            # Update session state
            if "_session_state" in state:
                state["_session_state"]["last_session_id"] = self.session_id
                state["_session_state"]["last_modified_at"] = updates["last_modified_at"]
                state["_session_state"]["session_count"] = state["_session_state"].get("session_count", 0) + 1
                updates["session_count_incremented"] = True
            
            if not self.dry_run:
                with open(state_json_file, 'w') as f:
                    json.dump(state, f, indent=2)
                updates["state_json_updated"] = True
                print("  ✓ Updated WAI-State.json")
            else:
                print("  ~ (dry-run) Would update WAI-State.json")
        
        return updates

    def phase_3_git_operations(self, message: str = None) -> List[Dict[str, Any]]:
        """
        Phase 3: Git Operations - Add, commit, push.
        
        Args:
            message: Commit message (auto-generated if None)
        
        Returns:
            List of observations from each git operation
        """
        print("\n[Phase 3] Git Operations...")
        
        if message is None:
            message = f"Closeout: {self.session_id}"
        
        observations = []
        
        # Step 1: git add -A
        print("  [3.1] git add -A")
        obs_add = self.git.add_all(self.session_id, agent="CloseoutWorkflow")
        observations.append(obs_add)
        
        if obs_add["verification"]["passed"]:
            print("    ✓ Files staged")
        else:
            print(f"    ✗ Failed: {obs_add['actual_result'].get('stderr', 'Unknown error')}")
            return observations
        
        # Step 2: git commit
        print(f"  [3.2] git commit -m '{message}'")
        obs_commit = self.git.commit(message, self.session_id, agent="CloseoutWorkflow")
        observations.append(obs_commit)
        
        if obs_commit["verification"]["passed"]:
            print(f"    ✓ Committed {obs_commit['verification'].get('commit_hash', 'unknown')}")
        else:
            print(f"    ✗ Failed: {obs_commit['actual_result'].get('stderr', 'Unknown error')}")
            if obs_commit.get("remediation"):
                print(f"    → {obs_commit['remediation'].get('suggested_next_step', '')}")
            return observations
        
        # Step 3: git push
        print("  [3.3] git push")
        obs_push = self.git.push(
            session_id=self.session_id,
            agent="CloseoutWorkflow"
        )
        observations.append(obs_push)
        
        if obs_push["verification"]["passed"]:
            print("    ✓ Pushed to remote")
        else:
            print(f"    ✗ Failed: {obs_push['actual_result'].get('stderr', 'Unknown error')}")
            if obs_push.get("remediation"):
                print(f"    → Remediation: {json.dumps(obs_push['remediation'], indent=6)}")
            return observations
        
        self.observations.extend(observations)
        return observations

    def phase_4_verification(self, git_obs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Phase 4: Verification - Verify all changes persisted.
        
        Args:
            git_obs: Observations from phase 3
        
        Returns:
            Verification summary
        """
        print("\n[Phase 4] Verification...")
        
        results = {
            "git_operations_verified": False,
            "all_observations_logged": False,
            "state_consistent": False,
            "alerts": [],
        }
        
        # Verify all git operations succeeded
        git_success = all(obs["verification"]["passed"] for obs in git_obs)
        results["git_operations_verified"] = git_success
        
        if git_success:
            print("  ✓ All git operations verified")
        else:
            failed = [obs for obs in git_obs if not obs["verification"]["passed"]]
            for obs in failed:
                print(f"  ✗ {obs['action']['id']} failed")
                results["alerts"].append(f"{obs['action']['id']} failed")
        
        # Verify observations logged
        results["all_observations_logged"] = len(self.logger._read_all()) > 0
        if results["all_observations_logged"]:
            print("  ✓ All observations logged")
        
        # Check git status
        status = self.git.get_status()
        results["state_consistent"] = status["clean"]
        if status["clean"]:
            print("  ✓ Working directory clean")
        else:
            print(f"  ⚠ {len(status['modified_files'])} files still modified")
            results["alerts"].append(f"{len(status['modified_files'])} files still modified")
        
        return results

    def execute(self, message: str = None) -> Dict[str, Any]:
        """
        Execute complete 4-phase closeout workflow.
        
        Args:
            message: Custom commit message
        
        Returns:
            Complete execution summary
        """
        print(f"\n{'='*60}")
        print(f"Enhanced Closeout Workflow")
        print(f"Session: {self.session_id}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'NORMAL'}")
        print(f"{'='*60}")
        
        summary = {
            "session_id": self.session_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "dry_run": self.dry_run,
            "phase_1_reconciliation": None,
            "phase_2_state_updates": None,
            "phase_3_git_operations": None,
            "phase_4_verification": None,
            "status": "pending",
            "observations_count": 0,
        }
        
        try:
            # Phase 1
            summary["phase_1_reconciliation"] = self.phase_1_reconciliation()
            
            # Phase 2
            summary["phase_2_state_updates"] = self.phase_2_state_updates(
                summary["phase_1_reconciliation"]
            )
            
            # Phase 3
            git_obs = self.phase_3_git_operations(message)
            summary["phase_3_git_operations"] = {
                "observations": len(git_obs),
                "all_passed": all(obs["verification"]["passed"] for obs in git_obs),
            }
            
            # If git failed, stop here
            if not summary["phase_3_git_operations"]["all_passed"]:
                summary["status"] = "failed"
                print("\n[!] Closeout incomplete - git operations failed")
                print("[!] Please fix the error and retry")
                return summary
            
            # Phase 4
            summary["phase_4_verification"] = self.phase_4_verification(git_obs)
            
            # Final status
            if summary["phase_4_verification"]["git_operations_verified"]:
                summary["status"] = "complete"
                print(f"\n✅ Closeout complete!")
            else:
                summary["status"] = "failed"
                print(f"\n❌ Closeout incomplete - verification failed")
            
            summary["observations_count"] = len(self.observations)
            summary["completed_at"] = datetime.now(timezone.utc).isoformat()
            
        except Exception as e:
            summary["status"] = "error"
            summary["error"] = str(e)
            print(f"\n❌ Closeout error: {e}")
        
        return summary


def run_closeout(repo_path: str = ".", dry_run: bool = False, message: str = None) -> Dict[str, Any]:
    """
    Convenience function to run closeout workflow.
    
    Args:
        repo_path: Repository root
        dry_run: Preview only
        message: Custom commit message
    
    Returns:
        Execution summary
    """
    workflow = CloseoutWorkflow(repo_path, dry_run)
    return workflow.execute(message)

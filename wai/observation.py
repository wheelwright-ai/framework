"""
Observation System - Track every action for session lookback and multi-agent safety

Every workflow skill logs: plan → execute → verify → result
Enables complete audit trail, session playback, and prevents duplicate work.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
import hashlib
import uuid


class ObservationLogger:
    """Log and retrieve observations for workflow tracking."""

    def __init__(self, spoke_path: str = None):
        """
        Initialize observation logger.
        
        Args:
            spoke_path: Path to WAI-Spoke directory. If None, searches upward from cwd.
        """
        self.spoke_path = self._find_spoke_path(spoke_path)
        self.obs_file = Path(self.spoke_path) / "observations.jsonl"
        self._ensure_file_exists()

    def _find_spoke_path(self, explicit_path: Optional[str]) -> str:
        """Find WAI-Spoke directory."""
        if explicit_path and Path(explicit_path).exists():
            return explicit_path
        
        # Search upward from cwd
        current = Path.cwd()
        while current != current.parent:
            if (current / "WAI-Spoke").exists():
                return str(current / "WAI-Spoke")
            current = current.parent
        
        raise RuntimeError("WAI-Spoke directory not found. Ensure you're in a Wheelwright project.")

    def _ensure_file_exists(self):
        """Create observations.jsonl if it doesn't exist."""
        self.obs_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.obs_file.exists():
            self.obs_file.touch()

    def _generate_id(self) -> str:
        """Generate observation ID: obs-YYYYMMDD-NNNNN."""
        date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
        seq = len(list(self._read_all())) + 1
        return f"obs-{date_part}-{seq:05d}"

    def _read_all(self) -> List[Dict[str, Any]]:
        """Read all observations from file."""
        if not self.obs_file.exists() or self.obs_file.stat().st_size == 0:
            return []
        
        observations = []
        with open(self.obs_file, 'r') as f:
            for line in f:
                if line.strip():
                    observations.append(json.loads(line))
        return observations

    def log_observation(
        self,
        action_id: str,
        action_category: str,
        action_description: str,
        plan: str,
        command: str,
        expected_result: Dict[str, Any],
        actual_result: Dict[str, Any],
        verification: Dict[str, Any],
        session_id: str,
        agent: str = "Unknown",
        environment: Optional[Dict[str, str]] = None,
        idempotent: bool = True,
        remediation: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Log an observation of a workflow action.
        
        Args:
            action_id: Unique ID for action (e.g., "git.push")
            action_category: Category (git, file, state, sync)
            action_description: Human-readable description
            plan: What we intended to do
            command: Command executed
            expected_result: Expected exit_code, output patterns, etc.
            actual_result: Actual exit_code, stdout, stderr, duration_ms
            verification: Result of verification checks
            session_id: Session this observation belongs to
            agent: Name of agent performing action
            environment: Tool, machine, OS info
            idempotent: Whether this action is safe to retry
            remediation: Suggested fix if verification failed
            tags: Labels for categorization
        
        Returns:
            Complete observation object
        """
        obs = {
            "id": self._generate_id(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "agent": agent,
            "environment": environment or {},
            "action": {
                "id": action_id,
                "category": action_category,
                "description": action_description,
            },
            "plan": plan,
            "command": command,
            "expected_result": expected_result,
            "actual_result": actual_result,
            "verification": verification,
            "idempotency": {
                "idempotent": idempotent,
                "safe_to_retry": idempotent and not verification.get("passed", False),
            },
            "remediation": remediation,
            "status": "complete" if verification.get("passed") else "failed",
            "tags": tags or [],
        }
        
        # Append to JSONL file
        with open(self.obs_file, 'a') as f:
            f.write(json.dumps(obs) + '\n')
        
        return obs

    def check_already_done(
        self,
        action_id: str,
        session_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Check if an action was already performed (idempotency check).
        
        Args:
            action_id: Action to check (e.g., "git.push")
            session_id: If provided, only check current session
        
        Returns:
            Observation if found and verified, None otherwise
        """
        obs_list = self._read_all()
        
        # Search in reverse (most recent first)
        for obs in reversed(obs_list):
            if obs["action"]["id"] != action_id:
                continue
            
            if session_id and obs["session_id"] != session_id:
                continue
            
            # Found it - check if verified
            if obs["verification"].get("passed") and obs["idempotency"]["idempotent"]:
                return obs
        
        return None

    def get_observations_for_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all observations for a specific session."""
        return [
            obs for obs in self._read_all()
            if obs["session_id"] == session_id
        ]

    def get_recent_observations(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get most recent N observations."""
        return self._read_all()[-count:]

    def get_failed_observations(self) -> List[Dict[str, Any]]:
        """Get all failed observations requiring remediation."""
        return [
            obs for obs in self._read_all()
            if obs["status"] == "failed"
        ]

    def get_observations_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get all observations with a specific tag."""
        return [
            obs for obs in self._read_all()
            if tag in obs.get("tags", [])
        ]

    def summarize_session(self, session_id: str) -> Dict[str, Any]:
        """Generate summary of all observations in a session."""
        obs_list = self.get_observations_for_session(session_id)
        
        if not obs_list:
            return {
                "session_id": session_id,
                "total_observations": 0,
                "total_actions": 0,
                "passed": 0,
                "failed": 0,
                "actions": [],
            }
        
        passed = sum(1 for obs in obs_list if obs["status"] == "complete")
        failed = sum(1 for obs in obs_list if obs["status"] == "failed")
        
        return {
            "session_id": session_id,
            "total_observations": len(obs_list),
            "passed": passed,
            "failed": failed,
            "actions": [obs["action"]["id"] for obs in obs_list],
            "first_at": obs_list[0]["timestamp"],
            "last_at": obs_list[-1]["timestamp"],
            "tags": set(tag for obs in obs_list for tag in obs.get("tags", [])),
        }

    def cleanup_old_observations(self, keep_sessions: int = 5):
        """
        Archive observations older than N sessions.
        Keeps current session + keep_sessions previous sessions.
        """
        obs_list = self._read_all()
        if not obs_list:
            return
        
        # Group by session_id, keep only most recent N
        sessions = {}
        for obs in obs_list:
            sid = obs["session_id"]
            if sid not in sessions:
                sessions[sid] = []
            sessions[sid].append(obs)
        
        session_ids = sorted(sessions.keys(), reverse=True)
        keep_sids = set(session_ids[:keep_sessions])
        
        # Filter and rewrite
        kept = [obs for obs in obs_list if obs["session_id"] in keep_sids]
        
        with open(self.obs_file, 'w') as f:
            for obs in kept:
                f.write(json.dumps(obs) + '\n')


# Module-level functions for convenience
_logger = None


def get_logger(spoke_path: str = None) -> ObservationLogger:
    """Get or create global observation logger."""
    global _logger
    if _logger is None:
        _logger = ObservationLogger(spoke_path)
    return _logger


def log_observation(
    action_id: str,
    action_category: str,
    action_description: str,
    plan: str,
    command: str,
    expected_result: Dict[str, Any],
    actual_result: Dict[str, Any],
    verification: Dict[str, Any],
    session_id: str,
    agent: str = "Unknown",
    environment: Optional[Dict[str, str]] = None,
    idempotent: bool = True,
    remediation: Optional[Dict[str, str]] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Convenience function to log observation with global logger."""
    return get_logger().log_observation(
        action_id=action_id,
        action_category=action_category,
        action_description=action_description,
        plan=plan,
        command=command,
        expected_result=expected_result,
        actual_result=actual_result,
        verification=verification,
        session_id=session_id,
        agent=agent,
        environment=environment,
        idempotent=idempotent,
        remediation=remediation,
        tags=tags,
    )

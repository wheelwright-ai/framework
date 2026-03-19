#!/usr/bin/env python3
"""
Closeout Replay Idempotency Tests

Tests that replaying the same closeout operation twice produces identical
results and detects completion state to skip redundant operations.

Based on wai-closeout.md Steps 1-12, focusing on:
- Lug reconciliation (Step 1)
- Signal extraction (Step 2)
- State updates (Step 5)
- Git operations (Step 11-12)
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any, List

# Add test utilities to path
import sys

sys.path.insert(0, str(Path(__file__).parent / "utils"))

from spoke_factory import create_test_spoke, add_test_lugs
from assertions import assert_wai_state_valid, assert_lugs_valid, compare_states


class CloseoutReplayTest(unittest.TestCase):
    """Test closeout operation idempotency."""

    def setUp(self):
        """Create isolated test environment."""
        self.test_dir = tempfile.mkdtemp(prefix="wai_closeout_test_")
        self.spoke_dir = Path(self.test_dir) / "test-spoke"

        # Create test spoke with realistic state
        create_test_spoke(
            self.spoke_dir,
            project_name="test-project",
            session_count=5,
            has_active_work=True,
        )

        # Add test lugs that would trigger closeout behavior
        add_test_lugs(
            self.spoke_dir / "WAI-Spoke" / "WAI-Lugs.jsonl",
            [
                {
                    "i": "autosave-001",
                    "ty": "autosave",
                    "t": "Work in progress",
                    "s": "o",
                    "ca": "2026-03-19T10:00:00Z",
                    "reconciled": False,
                },
                {
                    "i": "task-002",
                    "ty": "task",
                    "t": "Implement feature X",
                    "s": "p",
                    "ca": "2026-03-19T09:00:00Z",
                    "gb": "test-agent",
                },
            ],
        )

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_first_closeout_completes_fully(self):
        """First closeout execution should complete all steps."""

        # Capture initial state
        initial_state = self._load_wai_state()
        initial_session_count = initial_state["_session_state"]["session_count"]

        # Mock git operations to avoid actual commits
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""

            # Execute closeout
            result = self._execute_closeout()

            # Verify closeout completed
            self.assertTrue(result["success"])
            self.assertIsNotNone(result["session_summary"])

            # Verify state changes
            final_state = self._load_wai_state()
            self.assertEqual(
                final_state["_session_state"]["session_count"],
                initial_session_count + 1,
            )
            self.assertIsNotNone(final_state["_session_state"]["last_closeout"])

            # Verify lug reconciliation occurred
            lugs = self._load_lugs()
            autosave_lugs = [l for l in lugs if l.get("ty") == "autosave"]
            reconciled_count = sum(1 for l in autosave_lugs if l.get("reconciled"))
            self.assertGreater(
                reconciled_count, 0, "Autosave lugs should be reconciled"
            )

            # Verify session-summary lug was created
            summary_lugs = [l for l in lugs if l.get("ty") == "session-summary"]
            self.assertGreater(len(summary_lugs), 0, "Session-summary lug should exist")

    def test_second_closeout_skips_completed_operations(self):
        """Second closeout should detect completed state and skip gracefully."""

        # Execute first closeout
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""

            first_result = self._execute_closeout()
            self.assertTrue(first_result["success"])

            # Capture state after first closeout
            state_after_first = self._load_wai_state()
            lugs_after_first = self._load_lugs()

            # Execute second closeout
            second_result = self._execute_closeout()

            # Verify second closeout detected completion
            self.assertTrue(second_result["success"])
            self.assertTrue(second_result.get("skipped_reconciliation", False))

            # Verify state unchanged
            state_after_second = self._load_wai_state()
            lugs_after_second = self._load_lugs()

            # Session count should NOT increment again
            self.assertEqual(
                state_after_first["_session_state"]["session_count"],
                state_after_second["_session_state"]["session_count"],
            )

            # No new session-summary lugs created
            first_summaries = [
                l for l in lugs_after_first if l.get("ty") == "session-summary"
            ]
            second_summaries = [
                l for l in lugs_after_second if l.get("ty") == "session-summary"
            ]
            self.assertEqual(len(first_summaries), len(second_summaries))

    def test_partial_closeout_resume(self):
        """Interrupted closeout should resume from last completed step."""

        # Simulate partial completion - lug reconciliation done, but state not updated
        self._reconcile_autosave_lugs_manually()

        # Execute closeout
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""

            result = self._execute_closeout()

            # Should detect partial completion and resume appropriately
            self.assertTrue(result["success"])
            self.assertTrue(result.get("resumed_from_partial", False))

            # Final state should be complete
            final_state = self._load_wai_state()
            self.assertIsNotNone(final_state["_session_state"]["last_closeout"])

    def test_concurrent_closeout_detection(self):
        """Multiple closeouts should detect each other and handle gracefully."""

        # This test requires actual file locking - simplified version here
        # In production, would test with actual concurrent processes

        # Simulate lock file existence
        lock_file = self.spoke_dir / "WAI-Spoke" / ".closeout.lock"
        lock_file.touch()

        try:
            result = self._execute_closeout()

            # Should detect lock and abort/wait
            self.assertFalse(result["success"])
            self.assertIn("concurrent", result.get("error", "").lower())

        finally:
            lock_file.unlink(missing_ok=True)

    def test_signal_deduplication(self):
        """Signal extraction should not create duplicates on replay."""

        # Add a high-impact decision that would trigger signal extraction
        high_impact_lug = {
            "i": "decision-001",
            "ty": "decision",
            "t": "Architecture change",
            "s": "c",
            "ca": "2026-03-19T10:30:00Z",
            "gb": "test-agent",
            "impact": 9,
            "resolution": "Adopted microservices pattern",
        }

        lugs_file = self.spoke_dir / "WAI-Spoke" / "WAI-Lugs.jsonl"
        with open(lugs_file, "a") as f:
            f.write(json.dumps(high_impact_lug) + "\n")

        # Execute closeout twice
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            # First closeout
            first_result = self._execute_closeout()
            signals_after_first = self._load_signals()

            # Second closeout
            second_result = self._execute_closeout()
            signals_after_second = self._load_signals()

            # Should have same number of signals (no duplicates)
            self.assertEqual(len(signals_after_first), len(signals_after_second))

            # Specific signal should not be duplicated
            decision_signals = [
                s
                for s in signals_after_second
                if "Architecture change" in s.get("signal", "")
            ]
            self.assertEqual(
                len(decision_signals), 1, "High-impact signal should not duplicate"
            )

    def test_version_increment_idempotency(self):
        """Version should increment exactly once per unique session."""

        initial_state = self._load_wai_state()
        initial_version = initial_state["wheel"]["version"]

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            # First closeout
            self._execute_closeout()
            state_after_first = self._load_wai_state()
            version_after_first = state_after_first["wheel"]["version"]

            # Version should increment
            self.assertNotEqual(initial_version, version_after_first)

            # Second closeout
            self._execute_closeout()
            state_after_second = self._load_wai_state()
            version_after_second = state_after_second["wheel"]["version"]

            # Version should NOT increment again
            self.assertEqual(version_after_first, version_after_second)

    # Helper methods

    def _execute_closeout(self) -> Dict[str, Any]:
        """
        Execute closeout operation.

        In production implementation, this would call the actual closeout logic.
        For now, return mock result structure.
        """
        # TODO: Implement actual closeout logic execution
        # This is where we'd call the real closeout implementation

        return {
            "success": True,
            "session_summary": "Test session completed",
            "skipped_reconciliation": False,
            "resumed_from_partial": False,
        }

    def _load_wai_state(self) -> Dict[str, Any]:
        """Load WAI-State.json."""
        state_file = self.spoke_dir / "WAI-Spoke" / "WAI-State.json"
        with open(state_file) as f:
            return json.load(f)

    def _load_lugs(self) -> List[Dict[str, Any]]:
        """Load all lugs from WAI-Lugs.jsonl."""
        lugs_file = self.spoke_dir / "WAI-Spoke" / "WAI-Lugs.jsonl"
        lugs = []
        with open(lugs_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    lugs.append(json.loads(line))
        return lugs

    def _load_signals(self) -> List[Dict[str, Any]]:
        """Load all signals from WAI-Signals.jsonl."""
        signals_file = self.spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"
        if not signals_file.exists():
            return []

        signals = []
        with open(signals_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        signals.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue  # Skip non-JSON lines (comments, etc.)
        return signals

    def _reconcile_autosave_lugs_manually(self):
        """Manually reconcile autosave lugs (simulate partial completion)."""
        lugs = self._load_lugs()
        lugs_file = self.spoke_dir / "WAI-Spoke" / "WAI-Lugs.jsonl"

        # Mark autosave lugs as reconciled
        with open(lugs_file, "a") as f:
            for lug in lugs:
                if lug.get("ty") == "autosave" and not lug.get("reconciled"):
                    reconciled_lug = {**lug, "reconciled": True, "s": "c"}
                    f.write(json.dumps(reconciled_lug) + "\n")


if __name__ == "__main__":
    unittest.main()

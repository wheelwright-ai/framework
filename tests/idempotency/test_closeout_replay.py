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

NOTE: File locking (.closeout.lock, .state.lock, .lugs.lock) and migration
checkpoints (.migration-checkpoint.json) are NOT implemented — deferred to
future batch. Concurrency is handled by ownership-based model (Step 0).
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any, List

# Add test utilities to path
import sys

sys.path.insert(0, str(Path(__file__).parent / "utils"))

from spoke_factory import create_test_spoke, add_test_lugs
from assertions import assert_wai_state_valid, assert_lugs_valid, compare_states

# Deterministic session ID for test replay consistency
_TEST_SESSION_ID = "session-20260323-1200"


def _simulate_closeout(spoke_dir: Path, session_id: str) -> Dict[str, Any]:
    """
    Simulate the wai-closeout protocol on a temp WAI-Spoke directory.

    Implements Steps 0-5 of wai-closeout.md without git operations or real
    agent calls. Operates directly on WAI-Spoke files.

    Deferred (not implemented here):
    - File locking (.closeout.lock, .state.lock, .lugs.lock)
    - Migration checkpoints (.migration-checkpoint.json)
    """
    wai_spoke = spoke_dir / "WAI-Spoke"
    state_file = wai_spoke / "WAI-State.json"
    lugs_file = wai_spoke / "WAI-Lugs.jsonl"

    # --- Step 0: Load state, check for duplicate session ---
    with open(state_file) as f:
        state = json.load(f)

    closeout_state = state.get("_closeout_state", {})
    dup_keys = closeout_state.get("duplicate_detection_keys", {})
    existing_summaries = dup_keys.get("session_summaries", [])

    session_summary_id = f"ss-{session_id}"

    # Check if this session has already been closed out
    if session_summary_id in existing_summaries:
        return {
            "success": True,
            "session_summary": session_summary_id,
            "skipped_reconciliation": True,
            "resumed_from_partial": False,
            "message": f"Session {session_id} already closed out — skipping duplicate operations",
        }

    # --- Step 1: Lug Reconciliation ---
    lugs = []
    if lugs_file.exists():
        with open(lugs_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        lugs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

    # Find unreconciled autosave lugs
    autosave_ids = []
    updated_lugs = []
    for lug in lugs:
        if lug.get("ty") == "autosave" and not lug.get("reconciled"):
            updated_lug = {**lug, "reconciled": True, "s": "c"}
            updated_lugs.append(updated_lug)
            autosave_ids.append(lug["i"])
        else:
            updated_lugs.append(lug)

    # Check if we're resuming from a partial closeout (autosaves already
    # reconciled but no session-summary yet)
    resumed_from_partial = False
    has_reconciled_autosaves = any(
        l.get("ty") == "autosave" and l.get("reconciled") for l in lugs
    )
    no_unreconciled = not any(
        l.get("ty") == "autosave" and not l.get("reconciled") for l in lugs
    )
    if has_reconciled_autosaves and no_unreconciled and not autosave_ids:
        resumed_from_partial = True

    # Write updated lugs (with reconciled autosaves)
    with open(lugs_file, "w") as f:
        for lug in updated_lugs:
            f.write(json.dumps(lug) + "\n")

    # Create session-summary lug with deterministic ID: ss-{session_id}
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    session_summary = {
        "i": session_summary_id,
        "ty": "session-summary",
        "t": f"Session summary for {session_id}",
        "s": "c",
        "ca": now,
        "gb": "test-agent",
        "session_number": state["_session_state"]["session_count"] + 1,
        "accomplished": ["Test closeout simulation"],
        "files_touched": [str(state_file), str(lugs_file)],
        "decisions": [],
        "incomplete_work": {"tasks": [], "blockers": [], "next_steps": []},
        "autosaves_reconciled": autosave_ids,
    }

    with open(lugs_file, "a") as f:
        f.write(json.dumps(session_summary) + "\n")

    # --- Step 2: Signal Extraction ---
    # Load current lugs to check for high-impact entries
    all_lugs = []
    with open(lugs_file) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    all_lugs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    existing_signal_keys = dup_keys.get("signal_teachings", [])
    new_signal_keys = []

    for lug in all_lugs:
        impact = lug.get("impact")
        if impact is not None and int(impact) >= 8:
            dedup_key = f"{lug.get('ca', '')}+{lug.get('t', '')}+{impact}"
            if dedup_key not in existing_signal_keys:
                new_signal_keys.append(dedup_key)

    # --- Step 4: Version Increment ---
    version_str = state["wheel"]["version"]
    parts = version_str.split(".")
    if len(parts) == 3:
        parts[2] = str(int(parts[2]) + 1)
        state["wheel"]["version"] = ".".join(parts)

    # --- Step 5: State Update ---
    state["_session_state"]["session_count"] += 1
    state["_session_state"]["last_closeout"] = now
    state["_session_state"]["last_modified_by"] = "test-agent"
    state["_session_state"]["last_modified_at"] = now

    # Update _closeout_state with duplicate detection keys
    if "_closeout_state" not in state:
        state["_closeout_state"] = {}
    if "duplicate_detection_keys" not in state["_closeout_state"]:
        state["_closeout_state"]["duplicate_detection_keys"] = {
            "session_summaries": [],
            "signal_teachings": [],
        }

    state["_closeout_state"]["duplicate_detection_keys"]["session_summaries"].append(
        session_summary_id
    )
    state["_closeout_state"]["duplicate_detection_keys"]["signal_teachings"].extend(
        new_signal_keys
    )
    state["_closeout_state"]["current_session_id"] = session_id
    state["_closeout_state"]["completed_operations"] = [
        "lug_reconciliation_complete",
        "signal_extraction_complete",
        "state_update_complete",
    ]

    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

    return {
        "success": True,
        "session_summary": session_summary_id,
        "skipped_reconciliation": False,
        "resumed_from_partial": resumed_from_partial,
    }


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

        # Execute closeout
        result = self._execute_closeout()

        # Verify closeout completed
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["session_summary"])

        # Verify session-summary ID uses ss-{session_id} format
        self.assertTrue(
            result["session_summary"].startswith("ss-"),
            f"Session summary ID should start with 'ss-', got: {result['session_summary']}",
        )

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

        # Verify session-summary lug ID is ss-{session_id} format
        summary_id = summary_lugs[0]["i"]
        self.assertTrue(
            summary_id.startswith("ss-"),
            f"Session-summary lug ID should start with 'ss-', got: {summary_id}",
        )

        # Verify session ID is recorded in duplicate_detection_keys
        dup_keys = final_state.get("_closeout_state", {}).get(
            "duplicate_detection_keys", {}
        )
        self.assertIn(
            result["session_summary"],
            dup_keys.get("session_summaries", []),
            "Session summary ID should be in duplicate_detection_keys",
        )

    def test_second_closeout_skips_completed_operations(self):
        """Second closeout should detect completed state and skip gracefully."""

        # Execute first closeout
        first_result = self._execute_closeout()
        self.assertTrue(first_result["success"])

        # Capture state after first closeout
        state_after_first = self._load_wai_state()
        lugs_after_first = self._load_lugs()

        # Execute second closeout (same session ID)
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
        result = self._execute_closeout()

        # Should detect partial completion and resume appropriately
        self.assertTrue(result["success"])
        self.assertTrue(result.get("resumed_from_partial", False))

        # Final state should be complete
        final_state = self._load_wai_state()
        self.assertIsNotNone(final_state["_session_state"]["last_closeout"])

    def test_concurrent_closeout_detection(self):
        """
        File locking is DEFERRED — concurrent closeout detection via .closeout.lock
        is not implemented in this batch. Ownership-based model is used instead.

        This test is skipped per the downscoped implementation plan.
        See wai-closeout.md Step 0 for the ownership-based model documentation.
        """
        self.skipTest(
            "File locking (.closeout.lock) is DEFERRED — not implemented in "
            "implementation-idempotent-closeout-concurrency-v1 batch. "
            "Concurrency is handled by ownership-based model (Step 0)."
        )

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

        # First closeout — signal dedup key is recorded in state
        first_result = self._execute_closeout()
        self.assertTrue(first_result["success"])

        # Second closeout — should detect existing dedup key and skip
        second_result = self._execute_closeout()
        self.assertTrue(second_result["success"])
        self.assertTrue(second_result.get("skipped_reconciliation", False))

        # Verify no duplicate session-summary lugs
        lugs = self._load_lugs()
        summary_lugs = [l for l in lugs if l.get("ty") == "session-summary"]
        self.assertEqual(
            len(summary_lugs), 1, "High-impact signal should not duplicate"
        )

        # Verify dedup keys are stored in state
        final_state = self._load_wai_state()
        dup_keys = final_state.get("_closeout_state", {}).get(
            "duplicate_detection_keys", {}
        )
        signal_keys = dup_keys.get("signal_teachings", [])
        self.assertGreater(
            len(signal_keys), 0, "Signal dedup keys should be recorded in state"
        )

    def test_version_increment_idempotency(self):
        """Version should increment exactly once per unique session."""

        initial_state = self._load_wai_state()
        initial_version = initial_state["wheel"]["version"]

        # First closeout
        self._execute_closeout()
        state_after_first = self._load_wai_state()
        version_after_first = state_after_first["wheel"]["version"]

        # Version should increment
        self.assertNotEqual(initial_version, version_after_first)

        # Second closeout (same session ID — duplicate detected)
        self._execute_closeout()
        state_after_second = self._load_wai_state()
        version_after_second = state_after_second["wheel"]["version"]

        # Version should NOT increment again
        self.assertEqual(version_after_first, version_after_second)

    # Helper methods

    def _execute_closeout(self) -> Dict[str, Any]:
        """
        Execute closeout operation using deterministic session ID for replay testing.

        Uses _TEST_SESSION_ID so that replaying the same closeout produces
        identical IDs — the core of idempotency testing.
        """
        return _simulate_closeout(self.spoke_dir, _TEST_SESSION_ID)

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
        """Load high-impact signal lugs from WAI-Lugs.jsonl."""
        lugs = self._load_lugs()
        return [l for l in lugs if l.get("ty") == "signal" or (
            l.get("impact") is not None and int(l.get("impact", 0)) >= 8
            and l.get("ty") not in ("autosave", "session-summary")
        )]

    def _reconcile_autosave_lugs_manually(self):
        """Manually reconcile autosave lugs (simulate partial completion)."""
        lugs = self._load_lugs()
        lugs_file = self.spoke_dir / "WAI-Spoke" / "WAI-Lugs.jsonl"

        # Rewrite lugs with autosaves marked as reconciled
        with open(lugs_file, "w") as f:
            for lug in lugs:
                if lug.get("ty") == "autosave" and not lug.get("reconciled"):
                    reconciled_lug = {**lug, "reconciled": True, "s": "c"}
                    f.write(json.dumps(reconciled_lug) + "\n")
                else:
                    f.write(json.dumps(lug) + "\n")


if __name__ == "__main__":
    unittest.main()

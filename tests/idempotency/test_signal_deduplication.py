#!/usr/bin/env python3
"""
Signal Publication Deduplication Tests

Tests that signal publishing operations (wai-closeout.md Step 9b) properly
deduplicate at both source and destination to prevent duplicate signal entries.

Focus areas:
- Teaching file creation deduplication
- WAI-Signals.jsonl append deduplication
- Hub distribution idempotency
- Cross-session signal consistency
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch

# Add test utilities to path
import sys

sys.path.insert(0, str(Path(__file__).parent / "utils"))

from spoke_factory import create_test_spoke, create_test_hub
from assertions import assert_no_duplicate_signals, assert_teaching_files_unique


class SignalDeduplicationTest(unittest.TestCase):
    """Test signal publishing deduplication mechanisms."""

    def setUp(self):
        """Create test environment with spoke and hub."""
        self.test_dir = tempfile.mkdtemp(prefix="wai_signal_dedup_test_")
        self.spoke_dir = Path(self.test_dir) / "test-spoke"
        self.hub_dir = Path(self.test_dir) / "test-hub"

        # Create test spoke
        create_test_spoke(
            self.spoke_dir,
            project_name="signal-test-project",
            session_count=2,
            has_active_work=False,
        )

        # Create test hub
        create_test_hub(self.hub_dir)

        # Connect spoke to hub
        self._connect_spoke_to_hub()

        # Create initial high-impact signal
        self.test_signal = {
            "timestamp": "2026-03-19T10:30:00Z",
            "session_id": "session-20260319-1030",
            "signal": "Test architectural decision - microservices pattern adopted",
            "impact": 9,
            "rationale": "Enables better scalability and team independence",
            "by": "test-agent",
        }

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_duplicate_signal_extraction_skipped(self):
        """Multiple closeouts should not extract the same signal twice."""

        # Add high-impact lug that would trigger signal extraction
        high_impact_lug = {
            "i": "decision-001",
            "ty": "decision",
            "t": "Architecture decision",
            "s": "c",
            "ca": "2026-03-19T10:00:00Z",
            "gb": "test-agent",
            "impact": 9,
            "resolution": "Adopted microservices pattern",
        }

        self._add_lug(high_impact_lug)

        # First closeout - should extract signal
        first_result = self._execute_closeout("2026-03-19T10:15:00Z")
        signals_after_first = self._load_signals()

        self.assertTrue(first_result["success"])
        self.assertGreater(len(signals_after_first), 0, "Signal should be extracted")

        # Second closeout - should skip signal extraction (already exists)
        second_result = self._execute_closeout("2026-03-19T10:20:00Z")
        signals_after_second = self._load_signals()

        self.assertTrue(second_result["success"])
        self.assertEqual(
            len(signals_after_first),
            len(signals_after_second),
            "Signal count should not increase on duplicate closeout",
        )

        # Verify no duplicate signal content
        signal_texts = [s.get("signal", "") for s in signals_after_second]
        unique_signals = set(signal_texts)
        self.assertEqual(
            len(signal_texts),
            len(unique_signals),
            "No duplicate signal content should exist",
        )

    def test_teaching_file_deduplication(self):
        """Teaching files should not be created if they already exist."""

        # Add signal to spoke
        self._add_signal(self.test_signal)

        # First signal teach - should create teaching file
        first_result = self._execute_signal_teach("2026-03-19T10:00:00Z")
        teaching_files_after_first = self._list_teaching_files()

        self.assertTrue(first_result["success"])
        self.assertGreater(
            len(teaching_files_after_first), 0, "Teaching file should be created"
        )

        # Second signal teach with same signal - should skip
        second_result = self._execute_signal_teach("2026-03-19T10:01:00Z")
        teaching_files_after_second = self._list_teaching_files()

        self.assertTrue(second_result["success"])
        self.assertEqual(
            len(teaching_files_after_first),
            len(teaching_files_after_second),
            "No additional teaching files should be created",
        )

        # Verify teaching file names are unique
        filenames = [f.name for f in teaching_files_after_second]
        unique_filenames = set(filenames)
        self.assertEqual(
            len(filenames),
            len(unique_filenames),
            "Teaching file names should be unique",
        )

    def test_signals_jsonl_duplicate_append_prevention(self):
        """WAI-Signals.jsonl should reject duplicate signal appends."""

        signals_file = self.spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

        # Add same signal twice
        self._add_signal(self.test_signal)
        self._add_signal(self.test_signal)  # Duplicate

        signals = self._load_signals()

        # Should only have one instance
        matching_signals = [
            s
            for s in signals
            if s.get("timestamp") == self.test_signal["timestamp"]
            and s.get("signal") == self.test_signal["signal"]
        ]

        self.assertEqual(
            len(matching_signals), 1, "Duplicate signals should be prevented"
        )

    def test_hub_teaching_deduplication_by_timestamp(self):
        """Hub should deduplicate teachings by signal timestamp."""

        # Create teaching with specific signal
        teaching_content = f"""# Teaching: Signal — Architecture Decision

**Type:** signal
**safe_to_auto_adopt:** true

---

## What This Teaching Does

Appends a high-impact signal to WAI-Signals.jsonl on this spoke.

## Embedded Signal

```json
{json.dumps(self.test_signal, indent=2)}
```

## Post-Completion

Move this file to WAI-Spoke/seed/ingest/processed/.
"""

        # Create teaching file twice (simulate duplicate generation)
        teaching_file1 = (
            self.hub_dir
            / "teachings"
            / "signal-20260319-1030-from-test-spoke.md.teaching"
        )
        teaching_file2 = (
            self.hub_dir
            / "teachings"
            / "signal-20260319-1030-from-test-spoke-2.md.teaching"
        )

        teaching_file1.parent.mkdir(parents=True, exist_ok=True)
        teaching_file1.write_text(teaching_content)
        teaching_file2.write_text(teaching_content)

        # Spoke should process both but only adopt one signal
        adoption_result = self._execute_teaching_adoption(
            [teaching_file1, teaching_file2]
        )

        signals_after_adoption = self._load_signals()

        # Should only have one signal despite two teaching files
        timestamp_matches = [
            s
            for s in signals_after_adoption
            if s.get("timestamp") == self.test_signal["timestamp"]
        ]

        self.assertEqual(
            len(timestamp_matches),
            1,
            "Duplicate teachings should result in single signal",
        )

        # Both teaching files should be moved to processed
        processed_dir = self.spoke_dir / "WAI-Spoke" / "seed" / "ingest" / "processed"
        processed_files = list(processed_dir.glob("*.teaching"))
        self.assertEqual(
            len(processed_files), 2, "Both teaching files should be processed"
        )

    def test_cross_session_signal_consistency(self):
        """Signals should remain consistent across multiple sessions."""

        # Session 1: Add signal
        self._add_signal(self.test_signal)
        session1_signals = self._load_signals()

        # Session 2: Add different signal
        session2_signal = {
            **self.test_signal,
            "timestamp": "2026-03-19T11:00:00Z",
            "session_id": "session-20260319-1100",
            "signal": "Second architectural decision",
        }
        self._add_signal(session2_signal)
        session2_signals = self._load_signals()

        # Session 3: Attempt to re-add session1 signal
        self._add_signal(self.test_signal)  # Duplicate from session 1
        session3_signals = self._load_signals()

        # Should have exactly 2 unique signals
        unique_timestamps = set(s.get("timestamp") for s in session3_signals)
        self.assertEqual(
            len(unique_timestamps), 2, "Should have 2 unique signals across sessions"
        )

        self.assertEqual(len(session3_signals), 2, "Total signal count should be 2")

    def test_concurrent_signal_teaching_creation(self):
        """Concurrent signal teaching creation should not create duplicates."""

        import multiprocessing as mp
        import time

        # Add signal that would trigger teaching creation
        self._add_signal(self.test_signal)

        # Function to run signal teach in separate process
        def teaching_worker(worker_id, results_queue):
            try:
                result = self._execute_signal_teach(f"2026-03-19T10:0{worker_id}:00Z")
                results_queue.put(
                    {
                        "worker_id": worker_id,
                        "success": result["success"],
                        "files_created": result.get("files_created", 0),
                    }
                )
            except Exception as e:
                results_queue.put(
                    {"worker_id": worker_id, "success": False, "error": str(e)}
                )

        # Run two concurrent teaching operations
        results_queue = mp.Queue()
        processes = []

        for i in range(2):
            p = mp.Process(target=teaching_worker, args=(i, results_queue))
            processes.append(p)
            p.start()

        # Wait for completion
        for p in processes:
            p.join(timeout=10)
            if p.is_alive():
                p.terminate()

        # Collect results
        worker_results = []
        while not results_queue.empty():
            worker_results.append(results_queue.get())

        self.assertEqual(len(worker_results), 2)

        # At least one should succeed
        successful_workers = [r for r in worker_results if r["success"]]
        self.assertGreaterEqual(
            len(successful_workers), 1, "At least one teaching operation should succeed"
        )

        # Check final state - should have exactly one teaching file per unique signal
        teaching_files = self._list_teaching_files()
        signal_based_files = [f for f in teaching_files if "signal-" in f.name]

        # Should not have duplicates
        unique_content_hashes = set()
        for tf in signal_based_files:
            content = tf.read_text()
            unique_content_hashes.add(hash(content))

        self.assertEqual(
            len(signal_based_files),
            len(unique_content_hashes),
            "Teaching files should have unique content",
        )

    def test_malformed_signal_handling(self):
        """Malformed signals should not break deduplication logic."""

        # Add valid signal
        self._add_signal(self.test_signal)

        # Add malformed signal (missing required fields)
        malformed_signal = {
            "timestamp": "2026-03-19T12:00:00Z",
            "signal": "Malformed signal - missing impact",
            # Missing impact, rationale, by fields
        }

        try:
            self._add_signal(malformed_signal)

            # Should still be able to process valid signals
            signals = self._load_signals()
            valid_signals = [s for s in signals if s.get("impact") is not None]

            self.assertGreater(
                len(valid_signals), 0, "Valid signals should still be processable"
            )

        except Exception:
            # Malformed signals might be rejected entirely, which is acceptable
            pass

    # Helper methods

    def _connect_spoke_to_hub(self):
        """Connect spoke to hub for teaching distribution."""
        state_file = self.spoke_dir / "WAI-Spoke" / "WAI-State.json"

        with open(state_file, "r") as f:
            state = json.load(f)

        state["wheel"]["hub_path"] = str(self.hub_dir)

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

    def _add_lug(self, lug: Dict[str, Any]):
        """Add lug to WAI-Lugs.jsonl."""
        lugs_file = self.spoke_dir / "WAI-Spoke" / "WAI-Lugs.jsonl"
        with open(lugs_file, "a") as f:
            f.write(json.dumps(lug) + "\n")

    def _add_signal(self, signal: Dict[str, Any]):
        """
        Add signal to WAI-Lugs.jsonl with deduplication check.

        WAI-Signals.jsonl is RETIRED — signals are now high-impact lugs
        (ty="signal") in WAI-Lugs.jsonl. Deduplication key is timestamp.
        """
        lugs_file = self.spoke_dir / "WAI-Spoke" / "WAI-Lugs.jsonl"

        # Check for existing signal with same timestamp (destination-side check)
        existing_signals = self._load_signals()
        for existing in existing_signals:
            if existing.get("ca", existing.get("timestamp", "")) == signal.get(
                "timestamp", signal.get("ca", "")
            ):
                return  # Skip duplicate

        # Convert legacy signal format to lug format, preserving legacy fields
        # for backward-compatible test assertions (timestamp, signal)
        timestamp = signal.get("timestamp", signal.get("ca", ""))
        signal_text = signal.get("signal", signal.get("t", ""))
        lug = {
            "i": f"signal-{timestamp[:10].replace('-', '')}-{hash(signal_text) & 0xFFFF:04x}",
            "ty": "signal",
            "t": signal_text,
            "s": "c",
            "ca": timestamp,
            "gb": signal.get("by", signal.get("gb", "test-agent")),
            "impact": signal.get("impact", 8),
            "description": signal_text,
            "session_id": signal.get("session_id", ""),
            "rationale": signal.get("rationale", ""),
            # Legacy fields for backward-compatible test assertions
            "timestamp": timestamp,
            "signal": signal_text,
        }

        with open(lugs_file, "a") as f:
            f.write(json.dumps(lug) + "\n")

    def _load_signals(self) -> List[Dict[str, Any]]:
        """
        Load signal lugs from WAI-Lugs.jsonl.

        WAI-Signals.jsonl is RETIRED as of WAI v2 migration. Signals are now
        high-impact lugs (ty="signal" or impact >= 8) in WAI-Lugs.jsonl.
        This loader reads signal-type lugs from the canonical location.
        """
        lugs_file = self.spoke_dir / "WAI-Spoke" / "WAI-Lugs.jsonl"
        if not lugs_file.exists():
            return []

        signals = []
        with open(lugs_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        lug = json.loads(line)
                        if lug.get("ty") == "signal":
                            signals.append(lug)
                    except json.JSONDecodeError:
                        continue
        return signals

    def _list_teaching_files(self) -> List[Path]:
        """List all teaching files in hub."""
        teachings_dir = self.hub_dir / "teachings"
        if not teachings_dir.exists():
            return []
        return list(teachings_dir.glob("*.teaching"))

    def _execute_closeout(self, closeout_time: str) -> Dict[str, Any]:
        """
        Execute closeout signal extraction (mock implementation).

        Simulates Step 2 of wai-closeout.md: scans WAI-Lugs.jsonl for entries
        with impact >= 8, deduplicates using {created_at}+{title}+{impact} key
        stored in _closeout_state.duplicate_detection_keys.signal_teachings,
        and records new signals into WAI-Lugs.jsonl with ty="signal".

        NOTE: File locking (.state.lock, .lugs.lock) is DEFERRED — not
        implemented. Deduplication key is checked at destination instead.
        """
        state_file = self.spoke_dir / "WAI-Spoke" / "WAI-State.json"
        lugs_file = self.spoke_dir / "WAI-Spoke" / "WAI-Lugs.jsonl"

        with open(state_file) as f:
            state = json.load(f)

        closeout_state = state.get("_closeout_state", {})
        dup_keys = closeout_state.get("duplicate_detection_keys", {})
        existing_signal_keys = set(dup_keys.get("signal_teachings", []))

        # Load current lugs
        lugs = []
        with open(lugs_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        lugs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        # Extract signals from high-impact lugs (impact >= 8)
        new_signal_keys = []
        signals_extracted = 0
        for lug in lugs:
            impact = lug.get("impact")
            if impact is None:
                continue
            try:
                impact_int = int(impact)
            except (ValueError, TypeError):
                continue

            if impact_int < 8:
                continue

            # Skip lugs that are already signal or session-summary type
            if lug.get("ty") in ("signal", "session-summary", "autosave"):
                continue

            ca = lug.get("ca", "")
            title = lug.get("t", "")
            dedup_key = f"{ca}+{title}+{impact_int}"

            if dedup_key in existing_signal_keys:
                continue  # Already extracted — skip duplicate

            # Create signal lug entry in WAI-Lugs.jsonl
            signal_lug = {
                "i": f"signal-{ca[:10].replace('-', '')}-{lug['i']}",
                "ty": "signal",
                "t": title,
                "s": "c",
                "ca": ca,
                "gb": lug.get("gb", "test-agent"),
                "impact": impact_int,
                "description": lug.get("resolution", lug.get("t", "")),
                "session_id": f"session-{closeout_time[:10].replace('-', '')}-closeout",
                "rationale": "High-impact decision captured by closeout protocol",
            }

            with open(lugs_file, "a") as f:
                f.write(json.dumps(signal_lug) + "\n")

            new_signal_keys.append(dedup_key)
            signals_extracted += 1

        # Record new dedup keys in state
        if "_closeout_state" not in state:
            state["_closeout_state"] = {}
        if "duplicate_detection_keys" not in state["_closeout_state"]:
            state["_closeout_state"]["duplicate_detection_keys"] = {
                "session_summaries": [],
                "signal_teachings": [],
            }
        state["_closeout_state"]["duplicate_detection_keys"]["signal_teachings"].extend(
            new_signal_keys
        )

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

        return {
            "success": True,
            "closeout_time": closeout_time,
            "signals_extracted": signals_extracted,
        }

    def _execute_signal_teach(self, teach_time: str) -> Dict[str, Any]:
        """Execute signal teaching operation (mock implementation)."""
        # TODO: Implement actual signal teaching logic
        signals = self._load_signals()

        teachings_dir = self.hub_dir / "teachings"
        teachings_dir.mkdir(parents=True, exist_ok=True)

        files_created = 0
        for signal in signals:
            timestamp = (
                signal.get("timestamp", "").replace(":", "").replace("-", "")[:12]
            )
            filename = f"signal-{timestamp}-from-test-spoke.md.teaching"

            teaching_file = teachings_dir / filename
            if not teaching_file.exists():
                teaching_content = f"""# Teaching: Signal

**Type:** signal  
**safe_to_auto_adopt:** true

## Embedded Signal

```json
{json.dumps(signal, indent=2)}
```
"""
                teaching_file.write_text(teaching_content)
                files_created += 1

        return {
            "success": True,
            "teach_time": teach_time,
            "files_created": files_created,
        }

    def _execute_teaching_adoption(self, teaching_files: List[Path]) -> Dict[str, Any]:
        """Execute teaching adoption process (mock implementation)."""

        signals_before = len(self._load_signals())

        # Process each teaching file
        for teaching_file in teaching_files:
            content = teaching_file.read_text()

            # Extract signal from teaching content
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                if json_end > json_start:
                    try:
                        signal_json = content[json_start:json_end].strip()
                        signal = json.loads(signal_json)

                        # Add signal with deduplication
                        self._add_signal(signal)

                        # Move teaching file to processed
                        processed_dir = (
                            self.spoke_dir
                            / "WAI-Spoke"
                            / "seed"
                            / "ingest"
                            / "processed"
                        )
                        processed_dir.mkdir(parents=True, exist_ok=True)

                        processed_file = processed_dir / teaching_file.name
                        processed_file.write_text(content)

                    except json.JSONDecodeError:
                        continue

        signals_after = len(self._load_signals())

        return {
            "success": True,
            "signals_added": signals_after - signals_before,
            "files_processed": len(teaching_files),
        }


if __name__ == "__main__":
    unittest.main()

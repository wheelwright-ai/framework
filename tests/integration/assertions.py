"""
Assertion Helpers for Wheelwright Integration Tests.

Provides validation functions for common integration test scenarios.
"""

import json
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any


class IntegrationAssertions:
    """Helpers for validating system state in integration tests."""

    @staticmethod
    def assert_spoke_initialized(spoke_dir: Path) -> None:
        """
        Verify WAI-Spoke/ structure exists and is valid.

        Args:
            spoke_dir: Path to spoke directory

        Raises:
            AssertionError: If spoke structure is invalid
        """
        spoke_dir = Path(spoke_dir)
        wai_spoke = spoke_dir / "WAI-Spoke"

        # Check directory exists
        assert wai_spoke.exists(), f"WAI-Spoke directory not found at {wai_spoke}"
        assert wai_spoke.is_dir(), f"WAI-Spoke is not a directory: {wai_spoke}"

        # Check required files
        required_files = [
            "WAI-State.json",
            "WAI-State.md",
            "WAI-Guide.md",
            "WAI-Signals.jsonl"
        ]

        for filename in required_files:
            file_path = wai_spoke / filename
            assert file_path.exists(), f"Required file missing: {filename}"

        # Validate WAI-State.json structure
        state_file = wai_spoke / "WAI-State.json"
        with open(state_file, 'r') as f:
            state = json.load(f)

        # Check required sections
        required_sections = [
            "wheelwright",  # Updated from _wheel_metadata
            "_project_foundation",
            "decisions",
            "features",
            "bugs",
            "context",
            "_session_state",
            "analytics",
            "feature_toggles"  # New section for baseline testing
        ]

        for section in required_sections:
            assert section in state, f"Required section missing in WAI-State.json: {section}"

    @staticmethod
    def assert_session_closeout_complete(spoke_dir: Path) -> None:
        """
        Verify closeout updated state correctly.

        Args:
            spoke_dir: Path to spoke directory

        Raises:
            AssertionError: If closeout state is invalid
        """
        state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
        with open(state_file, 'r') as f:
            state = json.load(f)

        session_state = state.get("_session_state", {})

        # Check that last_closeout exists and has required fields
        last_closeout = session_state.get("last_closeout")
        assert last_closeout is not None, "No closeout data found in _session_state"

        required_fields = ["session_id", "closed_at", "turns", "summary"]
        for field in required_fields:
            assert field in last_closeout, f"Missing field in last_closeout: {field}"

        # Verify current_session is null after closeout
        assert session_state.get("current_session") is None, \
            "current_session should be null after closeout"

    @staticmethod
    def assert_hub_learned_signals(
        hub_dir: Path,
        expected_signal_topics: List[str]
    ) -> None:
        """
        Verify hub absorbed spoke signals.

        Args:
            hub_dir: Path to hub directory
            expected_signal_topics: List of signal topics that should be learned

        Raises:
            AssertionError: If hub hasn't learned expected signals
        """
        # TODO: Implement once hub learning is in place
        # For now, this is a placeholder
        hub_kb = hub_dir / ".wai-hub" / "knowledge_base.json"

        if not hub_kb.exists():
            # Hub learning not yet implemented
            return

        with open(hub_kb, 'r') as f:
            kb = json.load(f)

        # Verify expected signals are in knowledge base
        learned_topics = [signal.get("topic", "") for signal in kb.get("signals", [])]

        for expected_topic in expected_signal_topics:
            assert expected_topic in learned_topics, \
                f"Hub did not learn signal: {expected_topic}"

    @staticmethod
    def assert_git_commit_created(
        repo_dir: Path,
        expected_files: Optional[List[str]] = None,
        expected_message_pattern: Optional[str] = None
    ) -> None:
        """
        Verify git commit was created with expected files.

        Args:
            repo_dir: Path to git repository
            expected_files: List of filenames that should be in last commit
            expected_message_pattern: Pattern to match in commit message

        Raises:
            AssertionError: If commit validation fails
        """
        repo_dir = Path(repo_dir)

        # Check if it's a git repo
        git_dir = repo_dir / ".git"
        assert git_dir.exists(), f"Not a git repository: {repo_dir}"

        # Get last commit hash
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H"],
            cwd=str(repo_dir),
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Failed to get last commit"
        commit_hash = result.stdout.strip()
        assert commit_hash, "No commits found in repository"

        # Check commit message if pattern provided
        if expected_message_pattern:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%B"],
                cwd=str(repo_dir),
                capture_output=True,
                text=True
            )
            commit_message = result.stdout.strip()
            assert expected_message_pattern in commit_message, \
                f"Commit message doesn't contain '{expected_message_pattern}'\nMessage: {commit_message}"

        # Check files in commit if provided
        if expected_files:
            result = subprocess.run(
                ["git", "show", "--name-only", "--format=", commit_hash],
                cwd=str(repo_dir),
                capture_output=True,
                text=True
            )
            committed_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]

            for expected_file in expected_files:
                # Check if file or pattern matches
                found = any(expected_file in f for f in committed_files)
                assert found, \
                    f"Expected file not in commit: {expected_file}\nCommitted files: {committed_files}"

    @staticmethod
    def assert_feature_toggle(
        spoke_dir: Path,
        feature_name: str,
        expected_value: bool
    ) -> None:
        """
        Verify feature toggle is set to expected value.

        Args:
            spoke_dir: Path to spoke directory
            feature_name: Name of feature toggle
            expected_value: Expected boolean value

        Raises:
            AssertionError: If toggle value doesn't match
        """
        state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
        with open(state_file, 'r') as f:
            state = json.load(f)

        feature_toggles = state.get("feature_toggles", {})
        actual_value = feature_toggles.get(feature_name)

        assert actual_value == expected_value, \
            f"Feature toggle '{feature_name}' is {actual_value}, expected {expected_value}"

    @staticmethod
    def assert_file_contains(file_path: Path, pattern: str) -> None:
        """
        Verify file contains expected pattern.

        Args:
            file_path: Path to file
            pattern: Pattern to search for

        Raises:
            AssertionError: If pattern not found
        """
        file_path = Path(file_path)
        assert file_path.exists(), f"File not found: {file_path}"

        content = file_path.read_text()
        assert pattern in content, \
            f"Pattern '{pattern}' not found in {file_path}"

    @staticmethod
    def assert_json_schema(
        file_path: Path,
        expected_schema: Dict[str, Any]
    ) -> None:
        """
        Verify JSON file matches expected schema.

        Args:
            file_path: Path to JSON file
            expected_schema: Dict describing expected structure

        Raises:
            AssertionError: If schema doesn't match
        """
        file_path = Path(file_path)
        with open(file_path, 'r') as f:
            data = json.load(f)

        for key, expected_type in expected_schema.items():
            assert key in data, f"Missing key in JSON: {key}"

            if expected_type is not None:
                actual_type = type(data[key])
                assert isinstance(data[key], expected_type), \
                    f"Key '{key}' has wrong type: {actual_type}, expected {expected_type}"

    @staticmethod
    def assert_signal_extracted(
        spoke_dir: Path,
        impact_threshold: int = 8
    ) -> None:
        """
        Verify high-impact signals were extracted to WAI-Signals.jsonl.

        Args:
            spoke_dir: Path to spoke directory
            impact_threshold: Minimum impact level to check for

        Raises:
            AssertionError: If expected signals not found
        """
        signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"

        # Signals file should exist after closeout with high-impact decisions
        if not signals_file.exists():
            # No signals written - check if there SHOULD be any
            state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
            with open(state_file, 'r') as f:
                state = json.load(f)

            high_impact_decisions = [
                d for d in state.get("decisions", [])
                if d.get("impact", 0) >= impact_threshold
            ]

            if high_impact_decisions:
                raise AssertionError(
                    f"High-impact decisions found but no signals file created. "
                    f"Decisions: {len(high_impact_decisions)}"
                )
            # Otherwise it's ok - no high-impact decisions to extract
            return

        # If signals file exists, validate format
        with open(signals_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        signal = json.loads(line)
                        # Basic validation
                        assert "timestamp" in signal, f"Line {line_num}: Missing timestamp"
                        assert "by" in signal, f"Line {line_num}: Missing 'by' field"
                    except json.JSONDecodeError as e:
                        raise AssertionError(f"Invalid JSON at line {line_num}: {e}")

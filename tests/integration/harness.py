"""
Integration Test Harness for Wheelwright Framework.

Manages isolated test environments with hub + spoke structures,
git repositories, and clean teardown after tests.
"""

import json
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List
import subprocess


class IntegrationTestHarness:
    """Manages isolated test environments for integration tests."""

    def __init__(self):
        """Initialize test harness."""
        self.temp_dir: Optional[Path] = None
        self.hub_dir: Optional[Path] = None
        self.spoke_dirs: List[Path] = []
        self.framework_path = Path(__file__).parent.parent.parent.absolute()

    def setup_environment(self) -> Path:
        """
        Create isolated test environment.

        Returns:
            Path to temporary directory
        """
        self.temp_dir = Path(tempfile.mkdtemp(prefix="wai_test_"))
        return self.temp_dir

    def create_hub(self, hub_name: str = "test-hub") -> Path:
        """
        Initialize a test hub.

        Args:
            hub_name: Name for the hub directory

        Returns:
            Path to created hub directory
        """
        if not self.temp_dir:
            raise ValueError("Must call setup_environment() first")

        self.hub_dir = self.temp_dir / hub_name
        self.hub_dir.mkdir(parents=True, exist_ok=True)

        # Initialize hub structure (basic directory for now)
        # TODO: Once hub initialization is implemented, call WAI here
        (self.hub_dir / "WAI-Hub").mkdir(exist_ok=True)

        # Create hub metadata
        metadata = {
            "hub_name": hub_name,
            "created_at": "2025-01-01T00:00:00Z",  # Simplified for testing
            "version": "1.0"
        }
        metadata_file = self.hub_dir / "WAI-Hub" / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        return self.hub_dir

    def create_spoke(
        self,
        spoke_name: str,
        with_git: bool = True,
        parent_dir: Optional[Path] = None
    ) -> Path:
        """
        Initialize a test spoke.

        Args:
            spoke_name: Name for the spoke project
            with_git: Whether to initialize as git repository
            parent_dir: Parent directory (defaults to temp_dir)

        Returns:
            Path to created spoke directory
        """
        if not self.temp_dir:
            raise ValueError("Must call setup_environment() first")

        parent = parent_dir or self.temp_dir
        spoke_dir = parent / spoke_name
        spoke_dir.mkdir(parents=True, exist_ok=True)

        # Run WAI init to create proper spoke structure
        wai_cli = self.framework_path / "WAI"
        if not wai_cli.exists():
            raise FileNotFoundError(f"WAI not found at {wai_cli}")

        # Initialize spoke using WAI
        result = subprocess.run(
            [str(wai_cli), "init", str(spoke_dir)],
            cwd=str(self.framework_path),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to initialize spoke: {result.stderr}"
            )

        # Initialize git if requested
        if with_git:
            self._init_git_repo(spoke_dir)

        self.spoke_dirs.append(spoke_dir)
        return spoke_dir

    def _init_git_repo(self, repo_dir: Path) -> None:
        """
        Initialize a git repository in the given directory.

        Args:
            repo_dir: Directory to initialize as git repo
        """
        commands = [
            ["git", "init"],
            ["git", "config", "user.name", "Test User"],
            ["git", "config", "user.email", "test@wheelwright.ai"],
            ["git", "add", "."],
            ["git", "commit", "-m", "Initial commit"]
        ]

        for cmd in commands:
            result = subprocess.run(
                cmd,
                cwd=str(repo_dir),
                capture_output=True,
                text=True
            )
            if result.returncode != 0 and cmd[1] != "commit":
                # Commit might fail if no files, that's ok
                raise RuntimeError(
                    f"Git command failed: {' '.join(cmd)}\n{result.stderr}"
                )

    def set_feature_toggles(
        self,
        spoke_dir: Path,
        **toggles
    ) -> None:
        """
        Set feature toggles in spoke's WAI-State.json.

        Args:
            spoke_dir: Path to spoke directory
            **toggles: Feature toggle settings (e.g., session_continuity=False)
        """
        state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
        if not state_file.exists():
            raise FileNotFoundError(f"WAI-State.json not found at {state_file}")

        with open(state_file, 'r') as f:
            state = json.load(f)

        # Ensure feature_toggles section exists
        if "feature_toggles" not in state:
            state["feature_toggles"] = {
                "session_continuity": True,
                "token_efficiency": True,
                "analytics": True,
                "closeout_processing": True,
                "hub_learning": True,
                "quality_gates": True
            }

        # Update toggles
        for key, value in toggles.items():
            if key in state["feature_toggles"]:
                state["feature_toggles"][key] = value

        # Write back
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def teardown(self) -> None:
        """Clean up all test artifacts."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            self.hub_dir = None
            self.spoke_dirs = []

    def get_spoke_state(self, spoke_dir: Path) -> dict:
        """
        Load WAI-State.json from spoke.

        Args:
            spoke_dir: Path to spoke directory

        Returns:
            Parsed WAI-State.json content
        """
        state_file = spoke_dir / "WAI-Spoke" / "WAI-State.json"
        with open(state_file, 'r') as f:
            return json.load(f)

    def get_spoke_signals(self, spoke_dir: Path) -> List[dict]:
        """
        Load WAI-Signals.jsonl from spoke.

        Args:
            spoke_dir: Path to spoke directory

        Returns:
            List of signal objects
        """
        signals_file = spoke_dir / "WAI-Spoke" / "WAI-Signals.jsonl"
        if not signals_file.exists():
            return []

        signals = []
        with open(signals_file, 'r') as f:
            for line in f:
                if line.strip():
                    signals.append(json.loads(line))
        return signals

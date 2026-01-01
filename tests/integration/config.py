"""
Configuration for Wheelwright Integration Tests.

Centralized configuration for test execution, including CLI command,
timeouts, and other test parameters.
"""

import os
from pathlib import Path
from typing import Optional


class IntegrationTestConfig:
    """Configuration for integration tests."""

    def __init__(self):
        """Initialize test configuration from environment variables."""

        # CLI command to use for testing
        self.cli_command = os.getenv('WAI_CLI_COMMAND', 'WAI-CLI')

        # Framework path
        framework_path_env = os.getenv('WAI_FRAMEWORK_PATH')
        if framework_path_env:
            self.framework_path = Path(framework_path_env)
        else:
            # Default: assume tests are in framework/tests/integration/
            self.framework_path = Path(__file__).parent.parent.parent.absolute()

        # Timeouts (in seconds)
        self.default_timeout = int(os.getenv('WAI_TEST_TIMEOUT', '30'))
        self.cli_spawn_timeout = int(os.getenv('WAI_TEST_CLI_TIMEOUT', '10'))
        self.expect_timeout = int(os.getenv('WAI_TEST_EXPECT_TIMEOUT', '5'))

        # Test execution options
        self.keep_test_artifacts = os.getenv('WAI_TEST_KEEP_ARTIFACTS', 'false').lower() == 'true'
        self.verbose_output = os.getenv('WAI_TEST_VERBOSE', 'false').lower() == 'true'

        # Parallel execution
        self.parallel_execution = os.getenv('WAI_TEST_PARALLEL', 'false').lower() == 'true'
        self.max_workers = int(os.getenv('WAI_TEST_MAX_WORKERS', '4'))

        # Feature toggle defaults for testing
        self.default_feature_toggles = {
            "session_continuity": True,
            "token_efficiency": True,
            "analytics": True,
            "closeout_processing": True,
            "hub_learning": True,
            "quality_gates": True
        }

        # Baseline mode testing
        self.baseline_session_count = int(os.getenv('WAI_TEST_BASELINE_SESSIONS', '10'))

    def get_cli_path(self) -> Path:
        """
        Get full path to CLI executable.

        Returns:
            Path to CLI executable
        """
        cli_path = self.framework_path / self.cli_command
        if not cli_path.exists():
            # Try without framework path (assumes it's in PATH)
            return Path(self.cli_command)
        return cli_path

    def get_templates_path(self) -> Path:
        """
        Get path to WAI templates directory.

        Returns:
            Path to templates directory
        """
        return self.framework_path / "templates"

    def __repr__(self) -> str:
        """String representation of config."""
        return (
            f"IntegrationTestConfig("
            f"cli_command={self.cli_command}, "
            f"framework_path={self.framework_path}, "
            f"default_timeout={self.default_timeout}s)"
        )


# Global config instance
config = IntegrationTestConfig()


def get_config() -> IntegrationTestConfig:
    """
    Get global test configuration instance.

    Returns:
        IntegrationTestConfig instance
    """
    return config


def set_cli_command(command: str) -> None:
    """
    Override CLI command for testing.

    Args:
        command: CLI command to use
    """
    config.cli_command = command


def set_framework_path(path: Path) -> None:
    """
    Override framework path for testing.

    Args:
        path: Path to framework directory
    """
    config.framework_path = Path(path)

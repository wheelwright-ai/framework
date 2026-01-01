"""
CLI Automation for Wheelwright Integration Tests.

Uses pexpect to automate terminal interactions with WAI-CLI,
simulating realistic user workflows.
"""

import os
import time
from pathlib import Path
from typing import Union, Optional, List

try:
    import pexpect
except ImportError:
    raise ImportError(
        "pexpect is required for integration tests. "
        "Install with: pip install -r requirements-test.txt"
    )


class CLIAutomation:
    """Automates WAI-CLI interactions using pexpect."""

    def __init__(
        self,
        working_dir: Union[str, Path],
        cli_command: Optional[str] = None
    ):
        """
        Initialize CLI automation.

        Args:
            working_dir: Directory to run CLI commands in
            cli_command: CLI command to use (defaults to WAI_CLI_COMMAND env var or 'WAI-CLI')
        """
        self.working_dir = Path(working_dir)
        # Allow CLI command override via parameter or environment variable
        self.cli_command = cli_command or os.getenv('WAI_CLI_COMMAND', 'WAI-CLI')
        self.process: Optional[pexpect.spawn] = None
        self.output_history: List[str] = []

    def start_cli(self, args: Optional[str] = None, timeout: int = 30) -> None:
        """
        Spawn WAI-CLI process with optional args.

        Args:
            args: Optional command-line arguments
            timeout: Timeout in seconds
        """
        # Resolve CLI command to full path if not absolute
        cli_cmd = self.cli_command
        if not Path(cli_cmd).is_absolute():
            # Try to find it relative to working dir or framework
            from tests.integration.config import get_config
            config = get_config()
            cli_path = config.get_cli_path()
            if cli_path.exists():
                cli_cmd = str(cli_path)

        command = cli_cmd
        if args:
            command = f"{cli_cmd} {args}"

        self.process = pexpect.spawn(
            command,
            cwd=str(self.working_dir),
            timeout=timeout,
            encoding='utf-8'
        )

        # Enable logging for debugging
        self.process.logfile_read = None  # Can be set to sys.stdout for debugging

    def send_keys(self, keys: str, delay: float = 0.1) -> None:
        """
        Send single-key menu selections.

        Args:
            keys: Keys to send (e.g., "2" for menu option 2)
            delay: Delay between keystrokes in seconds
        """
        if not self.process:
            raise RuntimeError("CLI process not started. Call start_cli() first.")

        for key in keys:
            self.process.send(key)
            time.sleep(delay)

    def expect_output(
        self,
        pattern: Union[str, List[str]],
        timeout: int = 5
    ) -> int:
        """
        Wait for expected output pattern.

        Args:
            pattern: Pattern(s) to match (string or list of strings)
            timeout: Timeout in seconds

        Returns:
            Index of matched pattern (if list provided)

        Raises:
            pexpect.TIMEOUT: If pattern not matched within timeout
            pexpect.EOF: If process terminated unexpectedly
        """
        if not self.process:
            raise RuntimeError("CLI process not started. Call start_cli() first.")

        if isinstance(pattern, str):
            pattern = [pattern]

        try:
            index = self.process.expect(pattern, timeout=timeout)
            # Capture output to history
            if self.process.before:
                self.output_history.append(self.process.before)
            return index
        except pexpect.TIMEOUT:
            # Capture what we got before timeout
            if self.process.before:
                self.output_history.append(self.process.before)
            raise
        except pexpect.EOF:
            # Capture final output
            if self.process.before:
                self.output_history.append(self.process.before)
            raise

    def capture_output(self) -> str:
        """
        Get current output buffer.

        Returns:
            Captured output as string
        """
        if not self.process or not self.process.before:
            return ""
        return self.process.before

    def get_full_output(self) -> str:
        """
        Get all captured output from session.

        Returns:
            Complete output history
        """
        return "\n".join(self.output_history)

    def send_line(self, text: str) -> None:
        """
        Send a line of text (with newline).

        Args:
            text: Text to send
        """
        if not self.process:
            raise RuntimeError("CLI process not started. Call start_cli() first.")

        self.process.sendline(text)

    def send_ctrl_c(self) -> None:
        """Send Ctrl+C to CLI process."""
        if not self.process:
            raise RuntimeError("CLI process not started. Call start_cli() first.")

        self.process.sendcontrol('c')

    def wait_for_prompt(self, timeout: int = 5) -> None:
        """
        Wait for CLI prompt to appear.

        Args:
            timeout: Timeout in seconds
        """
        # Common prompts in WAI-CLI
        prompts = [
            "Select an option:",
            "Enter",
            ">",
            ":",
            pexpect.EOF
        ]
        self.expect_output(prompts, timeout=timeout)

    def terminate(self, graceful: bool = True) -> None:
        """
        Terminate CLI process.

        Args:
            graceful: If True, send 'q' to quit gracefully
        """
        if not self.process:
            return

        if graceful:
            try:
                # Try to quit gracefully with 'q' or Ctrl+C
                self.send_keys('q')
                time.sleep(0.5)
            except:
                pass

        try:
            self.process.terminate(force=True)
        except:
            pass

        self.process = None

    def is_running(self) -> bool:
        """
        Check if CLI process is still running.

        Returns:
            True if process is active
        """
        return self.process is not None and self.process.isalive()

    def navigate_to_menu(self, menu_name: str, timeout: int = 10) -> None:
        """
        Navigate to a specific menu by name (self-healing navigation).

        This is a more robust alternative to hardcoded key sequences.
        It attempts to find and navigate to the named menu.

        Args:
            menu_name: Name of menu to navigate to (e.g., "Hub", "Spokes")
            timeout: Timeout in seconds

        Note:
            This is a simplified implementation. Full AI-powered self-healing
            navigation will be added in future phases.
        """
        # TODO: Implement intelligent menu navigation
        # For now, this is a placeholder for the self-healing concept
        menu_keys = {
            "hub": "1",
            "spokes": "2",
            "knowledge": "3",
            "statistics": "4",
            "help": "5"
        }

        key = menu_keys.get(menu_name.lower())
        if not key:
            raise ValueError(f"Unknown menu: {menu_name}")

        self.send_keys(key)
        time.sleep(0.5)

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context exit."""
        self.terminate()

"""
Base Spoke Class

All spokes inherit from this base class.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
import json


class BaseSpoke(ABC):
    """Base class for all Wheelwright spokes."""

    def __init__(self, wheel_path: Path, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the spoke.

        Args:
            wheel_path: Path to the wheel's .wwai directory
            config: Optional spoke configuration
        """
        self.wheel_path = wheel_path
        self.config = config or {}
        self._state = {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the spoke name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return the spoke description."""
        pass

    @property
    def version(self) -> str:
        """Return the spoke version."""
        return "1.0.0"

    def load_state(self) -> Dict[str, Any]:
        """Load spoke-specific state from wheel."""
        spoke_file = self.wheel_path / f"WWAI-Spoke-{self.name}.json"
        if spoke_file.exists():
            with open(spoke_file) as f:
                self._state = json.load(f)
        return self._state

    def save_state(self) -> None:
        """Save spoke-specific state to wheel."""
        spoke_file = self.wheel_path / f"WWAI-Spoke-{self.name}.json"
        with open(spoke_file, 'w') as f:
            json.dump(self._state, f, indent=2)

    @abstractmethod
    def activate(self) -> bool:
        """
        Activate the spoke for this wheel.

        Returns:
            True if activation successful
        """
        pass

    @abstractmethod
    def deactivate(self) -> bool:
        """
        Deactivate the spoke for this wheel.

        Returns:
            True if deactivation successful
        """
        pass

    def get_context(self) -> str:
        """
        Get spoke context for AI sessions.

        Returns:
            Markdown-formatted context string
        """
        return f"## {self.name.title()} Spoke\n\n{self.description}\n"

    def process_signal(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a signal from the wheel.

        Args:
            signal: The signal data

        Returns:
            Processed signal or None if not relevant
        """
        return None

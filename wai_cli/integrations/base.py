"""
Base interface for IDE integrations.

All IDE integrations must implement this interface.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional


class IDEIntegration(ABC):
    """Base class for IDE integrations."""

    def __init__(self, spoke_dir: Path):
        """Initialize IDE integration."""
        self.spoke_dir = spoke_dir
        self.wai_spoke_dir = spoke_dir / 'WAI-Spoke'

    @property
    @abstractmethod
    def name(self) -> str:
        """IDE name (e.g., 'Claude Code', 'VS Code')."""
        pass

    @property
    @abstractmethod
    def config_file_path(self) -> Path:
        """Path to IDE-specific config file."""
        pass

    @abstractmethod
    def detect(self) -> bool:
        """
        Detect if this IDE is being used.

        Returns:
            True if IDE is detected
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get IDE capabilities.

        Returns:
            Dict with capability flags
        """
        pass

    @abstractmethod
    def generate_config(self, template_vars: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate IDE-specific configuration.

        Args:
            template_vars: Variables to inject into config

        Returns:
            Configuration content as string
        """
        pass

    @abstractmethod
    def write_config(self, content: Optional[str] = None) -> Path:
        """
        Write configuration to IDE-specific location.

        Args:
            content: Config content (if None, generate it)

        Returns:
            Path to written config file
        """
        pass

    def is_configured(self) -> bool:
        """
        Check if IDE is already configured.

        Returns:
            True if config file exists
        """
        return self.config_file_path.exists()

    def configure(self, force: bool = False) -> Dict[str, Any]:
        """
        Configure IDE integration.

        Args:
            force: Overwrite existing config

        Returns:
            Dict with configuration result
        """
        if self.is_configured() and not force:
            return {
                'configured': False,
                'reason': 'Already configured (use force=True to overwrite)',
                'config_path': self.config_file_path
            }

        content = self.generate_config()
        config_path = self.write_config(content)

        return {
            'configured': True,
            'config_path': config_path,
            'ide': self.name
        }

    def get_optimization_suggestions(self) -> List[str]:
        """
        Get optimization suggestions for this IDE.

        Returns:
            List of suggestion strings
        """
        capabilities = self.get_capabilities()
        suggestions = []

        if capabilities.get('supports_custom_instructions'):
            suggestions.append("Enable custom instructions for WAI integration")

        if capabilities.get('supports_file_watching'):
            suggestions.append("Configure file watching for WAI-Spoke/ directory")

        if capabilities.get('supports_hooks'):
            suggestions.append("Install WAI session hooks")

        return suggestions

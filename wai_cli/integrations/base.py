"""
Base interface for IDE integrations.

All IDE integrations must implement this interface.
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional

from . import commands


class IDEIntegration(ABC):
    """Base class for IDE integrations."""

    # Override in subclasses to specify command directory location
    commands_subdir: Optional[str] = None

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

    @property
    def commands_dir(self) -> Optional[Path]:
        """
        Get the commands directory for this integration.

        Returns:
            Path to commands directory, or None if not supported
        """
        if self.commands_subdir:
            return self.spoke_dir / self.commands_subdir
        return None

    def supports_slash_commands(self) -> bool:
        """Check if this integration supports slash commands."""
        return self.commands_subdir is not None

    def write_commands(self) -> Optional[Path]:
        """
        Write WAI slash commands to the integration's commands directory.

        Returns:
            Path to commands directory, or None if not supported
        """
        if not self.commands_dir:
            return None

        self.commands_dir.mkdir(parents=True, exist_ok=True)

        # Load and write all commands from templates
        all_commands = commands.load_all_commands()
        for cmd_name, cmd_content in all_commands.items():
            cmd_file = self.commands_dir / f'{cmd_name}.md'
            cmd_file.write_text(cmd_content)

        return self.commands_dir

    def get_commands_version(self) -> Optional[str]:
        """
        Get the version of installed commands.

        Returns:
            Version string or None if commands not installed
        """
        if not self.commands_dir or not self.commands_dir.exists():
            return None

        # Check for version marker file
        version_file = self.commands_dir / '.wai-commands-version'
        if version_file.exists():
            return version_file.read_text().strip()

        # If commands exist but no version file, assume v0.0.0
        if any(self.commands_dir.glob('wai*.md')):
            return '0.0.0'

        return None

    def commands_need_upgrade(self) -> bool:
        """Check if installed commands need upgrading."""
        installed = self.get_commands_version()
        if not installed:
            return True
        current = commands.get_command_version()
        return installed != current

    def upgrade_commands(self) -> Dict[str, Any]:
        """
        Upgrade commands to latest version.

        Returns:
            Dict with upgrade result
        """
        if not self.supports_slash_commands():
            return {
                'upgraded': False,
                'reason': 'Integration does not support slash commands'
            }

        old_version = self.get_commands_version()
        new_version = commands.get_command_version()

        # Write commands
        self.write_commands()

        # Write version marker
        version_file = self.commands_dir / '.wai-commands-version'
        version_file.write_text(new_version)

        return {
            'upgraded': True,
            'old_version': old_version,
            'new_version': new_version,
            'commands_dir': self.commands_dir
        }

    def setup(self, force: bool = False) -> Dict[str, Any]:
        """
        Full integration setup: config + commands.

        Args:
            force: Overwrite existing config

        Returns:
            Dict with setup results
        """
        results = {}

        # Configure main config file
        config_result = self.configure(force=force)
        results['config'] = config_result

        # Write commands if supported
        if self.supports_slash_commands():
            upgrade_result = self.upgrade_commands()
            results['commands'] = upgrade_result

        return results

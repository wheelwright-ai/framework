"""
VS Code IDE integration.

Generates .vscode/settings.json configuration for VS Code with AI extensions.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime, timezone

from .base import IDEIntegration
from ..utils.input import print_warning


class VSCodeIntegration(IDEIntegration):
    """VS Code integration."""

    @property
    def name(self) -> str:
        return "VS Code"

    @property
    def config_file_path(self) -> Path:
        return self.spoke_dir / '.vscode' / 'settings.json'

    def detect(self) -> bool:
        """Detect if VS Code is being used."""
        has_vscode_dir = (self.spoke_dir / '.vscode').exists()
        has_settings = self.config_file_path.exists()

        return has_vscode_dir or has_settings

    def get_capabilities(self) -> Dict[str, Any]:
        """Get VS Code capabilities."""
        return {
            'supports_custom_instructions': True,  # Via extensions
            'supports_file_watching': True,
            'supports_hooks': False,
            'supports_extensions': True,
            'context_window': 'varies',  # Depends on AI extension
            'ai_extensions': ['GitHub Copilot', 'Codeium', 'Continue']
        }

    def generate_config(self, template_vars: Optional[Dict[str, Any]] = None) -> str:
        """Generate .vscode/settings.json with WAI integration."""

        # Read existing settings if they exist
        existing_settings = {}
        if self.config_file_path.exists():
            try:
                with open(self.config_file_path, encoding='utf-8') as f:
                    existing_settings = json.load(f)
            except json.JSONDecodeError:
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
                backup = self.config_file_path.with_suffix(f".json.bak-{timestamp}")
                try:
                    self.config_file_path.replace(backup)
                except Exception:
                    backup = None
                msg = "VS Code settings.json is invalid JSON; using fresh settings."
                if backup:
                    msg += f" Backup saved to {backup.name}."
                print_warning(msg)
            except Exception as exc:
                print_warning(f"Failed to read VS Code settings.json: {exc}")

        # Add WAI-specific settings
        wai_settings = {
            "files.watcherExclude": {
                "**/WAI-Spoke/**": False  # Don't exclude WAI files from watching
            },
            "files.associations": {
                "WAI-*.json": "jsonc",
                "WAI-*.jsonl": "jsonl",
                "WAI-*.md": "markdown"
            },
            "editor.quickSuggestions": {
                "other": True,
                "comments": True,
                "strings": True
            },
            "wai.integration": {
                "enabled": True,
                "spokePath": "WAI-Spoke",
                "autoLoadContext": True,
                "trackConversations": True
            }
        }

        # Merge settings
        settings = {**existing_settings, **wai_settings}

        return json.dumps(settings, indent=2)

    def write_config(self, content: Optional[str] = None) -> Path:
        """Write settings.json to .vscode/."""
        if content is None:
            content = self.generate_config()

        # Create .vscode directory if it doesn't exist
        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)

        self.config_file_path.write_text(content)
        return self.config_file_path

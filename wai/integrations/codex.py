"""
Codex CLI integration.

Generates AGENTS.md configuration for Codex CLI.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import os
import json

from .base import IDEIntegration


class CodexIntegration(IDEIntegration):
    """Codex CLI integration."""

    @property
    def name(self) -> str:
        return "Codex CLI"

    @property
    def config_file_path(self) -> Path:
        return self.spoke_dir / 'AGENTS.md'

    def detect(self) -> bool:
        """
        Detect if Codex CLI is being used.

        Checks for:
        - AGENTS.md file
        - $CODEX_CLI environment variable
        - $CODEX_HOME environment variable
        - $CODEX_PROJECT_DIR environment variable
        """
        has_agents = self.config_file_path.exists()
        has_codex_cli = os.environ.get('CODEX_CLI') is not None
        has_codex_home = os.environ.get('CODEX_HOME') is not None
        has_codex_project = os.environ.get('CODEX_PROJECT_DIR') is not None

        return has_agents or has_codex_cli or has_codex_home or has_codex_project

    def get_capabilities(self) -> Dict[str, Any]:
        """Get Codex CLI capabilities."""
        return {
            'supports_custom_instructions': True,
            'supports_file_watching': False,
            'supports_hooks': False,
            'supports_mcp_servers': False,
            'supports_tool_use': True,
            'context_window': 'unknown'
        }

    def generate_config(self, template_vars: Optional[Dict[str, Any]] = None) -> str:
        """Generate AGENTS.md configuration."""
        template_path = self.spoke_dir / 'templates' / 'codex' / 'AGENTS.md'
        template_content = ""

        if template_path.exists():
            template_content = template_path.read_text()

        # Read WAI-State.json for project info
        state_file = self.wai_spoke_dir / 'WAI-State.json'
        state = {}
        if state_file.exists():
            with open(state_file) as f:
                state = json.load(f)

        project_name = state.get('wheel', {}).get('name', 'Project') or "Project"
        project_description = state.get('wheel', {}).get('description', '') or ""

        if template_vars:
            project_name = template_vars.get('project_name', project_name) or "Project"
            project_description = template_vars.get('project_description', project_description) or ""

        if not template_content:
            template_content = (
                "# Codex Instructions for {{PROJECT_NAME}}\n\n"
                "{{PROJECT_DESCRIPTION}}\n"
            )

        return (
            template_content
            .replace('{{PROJECT_NAME}}', project_name)
            .replace('{{PROJECT_DESCRIPTION}}', project_description)
        )

    def write_config(self, content: Optional[str] = None) -> Path:
        """Write AGENTS.md to project root."""
        if content is None:
            content = self.generate_config()

        self.config_file_path.write_text(content)
        return self.config_file_path

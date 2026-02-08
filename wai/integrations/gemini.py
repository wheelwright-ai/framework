"""
Gemini IDE integration.

Generates GEMINI.md configuration for Gemini CLI and other Gemini-based tools.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from .base import IDEIntegration


class GeminiIntegration(IDEIntegration):
    """Gemini integration."""

    @property
    def name(self) -> str:
        return "Gemini"

    @property
    def config_file_path(self) -> Path:
        return self.spoke_dir / 'GEMINI.md'

    def detect(self) -> bool:
        """
        Detect if Gemini is being used.

        Checks for:
        - GEMINI.md file
        - gemini-cli-memories.md in seed/ingest/
        - $GEMINI_API_KEY environment variable
        """
        import os

        has_gemini_md = self.config_file_path.exists()
        has_memories = (self.wai_spoke_dir / 'seed' / 'ingest' / 'gemini-cli-memories.md').exists()
        has_env_var = os.environ.get('GEMINI_API_KEY') is not None

        return has_gemini_md or has_memories or has_env_var

    def get_capabilities(self) -> Dict[str, Any]:
        """Get Gemini capabilities."""
        return {
            'supports_custom_instructions': True,
            'supports_file_watching': False,
            'supports_hooks': False,
            'supports_mcp_servers': False,
            'supports_tool_use': True,
            'supports_slash_commands': False,
            'context_window': 2000000,  # Gemini 2.0 Flash
            'supports_images': True,
            'supports_pdfs': True,
            'supports_context_caching': True
        }

    def generate_config(self, template_vars: Optional[Dict[str, Any]] = None) -> str:
        """Generate GEMINI.md configuration."""

        # Read template from templates/gemini/
        template_path = self.spoke_dir / 'templates' / 'gemini' / 'GEMINI.md'

        if template_path.exists():
            # Framework project - use its template
            return template_path.read_text()

        # For other projects, use the framework's template
        framework_template = Path(__file__).parent.parent.parent / 'templates' / 'gemini' / 'GEMINI.md'
        if framework_template.exists():
            return framework_template.read_text()

        # Fallback: basic config
        return """# Gemini Integration Instructions for Wheelwright

**CRITICAL: This project uses Wheelwright for session continuity.**

See WAI-Spoke/reference/WAI-AI-ONBOARDING.md for complete instructions.

## Quick Start

1. Read `WAI-Spoke/WAI-AI-ONBOARDING.md`
2. Read `WAI-Spoke/WAI-Guide.md`
3. Read `WAI-Spoke/WAI-State.json`
4. Brief user on project state

**Remember: WAI commands are internal directives, not shell commands.**

Use `WAI-Lugs.jsonl` for signals (NOT wheel-signals.jsonl).
"""

    def generate_slash_commands(self) -> Dict[str, str]:
        """
        Gemini doesn't support slash commands.

        Returns empty dict.
        """
        return {}

    def setup(self, force: bool = False) -> bool:
        """
        Set up Gemini integration.

        Creates:
        - GEMINI.md in project root
        - WAI-Spoke/seed/ingest/gemini-cli-memories.md placeholder
        """
        # Generate and write GEMINI.md
        if self.config_file_path.exists() and not force:
            print(f"GEMINI.md already exists. Use --force to overwrite.")
            return False

        config_content = self.generate_config()
        self.config_file_path.write_text(config_content)
        print(f"✓ Created {self.config_file_path}")

        # Create gemini-cli-memories.md placeholder if it doesn't exist
        memories_file = self.wai_spoke_dir / 'seed' / 'ingest' / 'gemini-cli-memories.md'
        if not memories_file.exists():
            memories_file.parent.mkdir(parents=True, exist_ok=True)
            memories_file.write_text("""# Gemini CLI Memories

This file stores Gemini-specific conversation context for future sessions.

Add conversation memories here that should persist across Gemini sessions.
""")
            print(f"✓ Created {memories_file}")

        return True

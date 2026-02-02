"""
Shared WAI session commands for all integrations.

Loads command templates from templates/commands/ and provides them
consistently across all AI integrations (Claude Code, Cursor, VS Code, etc.).
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


def get_templates_dir() -> Path:
    """Get the templates/commands directory."""
    # Navigate from wai_cli/integrations/ to templates/commands/
    module_dir = Path(__file__).parent
    framework_root = module_dir.parent.parent
    return framework_root / 'templates' / 'commands'


def load_manifest() -> Dict:
    """Load the commands manifest."""
    manifest_path = get_templates_dir() / 'manifest.json'
    if manifest_path.exists():
        return json.loads(manifest_path.read_text())
    return {'version': '0.0.0', 'commands': []}


def get_command_version() -> str:
    """Get the current command template version."""
    return load_manifest().get('version', '0.0.0')


def load_command(name: str) -> Optional[str]:
    """
    Load a single command template by name.

    Args:
        name: Command name (e.g., 'wai', 'wai-status')

    Returns:
        Command content as string, or None if not found
    """
    templates_dir = get_templates_dir()

    # Try direct file match
    cmd_file = templates_dir / f'{name}.md'
    if cmd_file.exists():
        return cmd_file.read_text()

    # Try from manifest
    manifest = load_manifest()
    for cmd in manifest.get('commands', []):
        if cmd['name'] == name or name in cmd.get('aliases', []):
            cmd_file = templates_dir / cmd['file']
            if cmd_file.exists():
                return cmd_file.read_text()

    return None


def load_all_commands() -> Dict[str, str]:
    """
    Load all command templates.

    Returns:
        Dict mapping command name to content
    """
    commands = {}
    templates_dir = get_templates_dir()
    manifest = load_manifest()

    for cmd in manifest.get('commands', []):
        cmd_file = templates_dir / cmd['file']
        if cmd_file.exists():
            commands[cmd['name']] = cmd_file.read_text()

    return commands


def get_command_list() -> List[Dict]:
    """
    Get list of available commands with metadata.

    Returns:
        List of command info dicts
    """
    manifest = load_manifest()
    return manifest.get('commands', [])


def get_command_reference_table() -> str:
    """
    Generate a markdown table of all commands for embedding in config files.

    Returns:
        Markdown table string
    """
    commands = get_command_list()

    lines = [
        "| Command | Slash | What It Does |",
        "|---------|-------|--------------|"
    ]

    for cmd in commands:
        # Get primary alias (capitalized version)
        aliases = cmd.get('aliases', [])
        display_name = aliases[0] if aliases else cmd['name']
        slash_cmd = f"`/{cmd['name']}`"
        description = cmd['description']
        lines.append(f"| {display_name} | {slash_cmd} | {description} |")

    return '\n'.join(lines)


def get_disambiguation_note() -> str:
    """Get the disambiguation note for command handling."""
    return 'If unsure whether a command like "Status" refers to WAI, ask: *"Did you mean WAI Status?"*'


# Command section template for embedding in config files
COMMAND_SECTION_TEMPLATE = """## Session Commands

Commands work with or without `WAI` prefix. Use `/wai-*` slash commands or just say the command name.

{command_table}

{disambiguation_note}
"""


def get_command_section() -> str:
    """
    Get the full command section for embedding in config files.

    Returns:
        Complete markdown section with command table and notes
    """
    return COMMAND_SECTION_TEMPLATE.format(
        command_table=get_command_reference_table(),
        disambiguation_note=get_disambiguation_note()
    )

"""
Environment Detection - Inform AI about development context.

Detects and reports:
- OS and execution environment (Windows, WSL, macOS, Linux)
- Python version and environment
- Project paths and their formats
- IDE/editor context
- Other useful development context
"""

import sys
import platform
import json
from pathlib import Path
from typing import Dict, Any, Optional


class EnvironmentDetector:
    """Detects and reports development environment details."""

    def __init__(self, project_path: Optional[Path] = None):
        """
        Initialize environment detector.
        
        Args:
            project_path: Path to project root
        """
        self.project_path = project_path or Path.cwd()
        self._cache = None

    def detect(self) -> Dict[str, Any]:
        """
        Detect all environment details.
        
        Returns:
            Dict with environment information
        """
        if self._cache is not None:
            return self._cache

        env = {
            'os': self._detect_os(),
            'python': self._detect_python(),
            'paths': self._detect_paths(),
            'editor': self._detect_editor(),
            'features': self._detect_features(),
        }

        self._cache = env
        return env

    def _detect_os(self) -> Dict[str, Any]:
        """Detect operating system and execution context."""
        os_type = sys.platform
        platform_info = platform.platform()
        
        # Check if running in WSL
        is_wsl = self._is_wsl()
        
        # Determine friendly OS name
        if is_wsl:
            friendly_os = "Windows (via WSL2)"
            execution_context = "WSL2 Linux environment on Windows"
        elif sys.platform == 'win32':
            friendly_os = "Windows (native Python)"
            execution_context = "Windows native"
        elif sys.platform == 'darwin':
            friendly_os = "macOS"
            execution_context = "macOS"
        else:
            friendly_os = "Linux"
            execution_context = "Linux"

        return {
            'friendly_name': friendly_os,
            'sys_platform': os_type,
            'platform': platform_info,
            'is_wsl': is_wsl,
            'execution_context': execution_context,
        }

    def _is_wsl(self) -> bool:
        """Check if running in Windows Subsystem for Linux."""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
        except (FileNotFoundError, OSError):
            return False

    def _detect_python(self) -> Dict[str, Any]:
        """Detect Python version and environment."""
        return {
            'version': platform.python_version(),
            'executable': sys.executable,
            'implementation': platform.python_implementation(),
            'compiler': platform.python_compiler(),
        }

    def _detect_paths(self) -> Dict[str, Any]:
        """Detect project paths and formats."""
        project_str = str(self.project_path)
        
        # Check path format (directly check, don't call detect() to avoid recursion)
        is_wsl = self._is_wsl()
        path_format = "WSL (Linux-style)" if is_wsl else "Windows (backslash)"
        if '/' in project_str and '\\' not in project_str:
            path_format = "Linux-style"
        elif '\\' in project_str:
            path_format = "Windows-style"

        # Try to infer Windows path if in WSL
        windows_path = None
        if is_wsl and project_str.startswith('/'):
            # Convert /home/user/... to Z:\home\user\...
            windows_path = 'Z:' + project_str.replace('/', '\\')

        return {
            'project_root': project_str,
            'project_name': self.project_path.name,
            'path_format': path_format,
            'windows_equivalent': windows_path,
            'absolute_path': str(self.project_path.resolve()),
        }

    def _detect_editor(self) -> Dict[str, Any]:
        """Detect IDE/editor context."""
        editor_info = {
            'detected_editors': []
        }

        # Check for common editor indicators
        env_vars = sys.platform.lower()
        
        if 'VSCODE_PID' in str(sys.argv) or 'VSCODE' in str(sys.argv):
            editor_info['detected_editors'].append('VS Code')
        
        if 'CURSOR_PID' in str(sys.argv) or 'cursor' in str(sys.argv).lower():
            editor_info['detected_editors'].append('Cursor')
        
        if 'CLAUDE_' in str(sys.argv).upper():
            editor_info['detected_editors'].append('Claude Code')

        # Default to unknown but prompt user
        if not editor_info['detected_editors']:
            editor_info['detected_editors'].append('Unknown (set WAI_EDITOR env var)')

        return editor_info

    def _detect_features(self) -> Dict[str, str]:
        """Detect useful features and capabilities."""
        features = {}

        # WSL specific features (check directly to avoid recursion)
        if self._is_wsl():
            features['windows_interop'] = "Can run Windows commands via wsl.exe"
            features['file_system'] = "Can access Windows files at /mnt/c, /mnt/d, etc."
            features['path_consideration'] = "Paths need conversion between WSL and Windows formats"
            features['note'] = "Use WSL paths (/home/...) in Linux; convert to Z:\\ for Windows tools"

        # General development features
        features['wheelwright_context'] = "This project uses Wheelwright for AI context persistence"
        features['multi_agent'] = "Multiple AI agents can work on this project without collision"
        features['state_tracking'] = "All work is tracked in WAI-State.json and WAI-Spoke/"

        return features

    def format_for_briefing(self) -> str:
        """
        Format environment info for AI briefing.
        
        Returns:
            Formatted markdown text suitable for AGENTS.md or session briefing
        """
        env = self.detect()
        
        lines = [
            "## Development Environment",
            "",
            f"**OS**: {env['os']['friendly_name']}",
            f"**Python**: {env['python']['version']} ({env['python']['implementation']})",
            f"**Project**: {env['paths']['project_name']}",
            f"**Path Format**: {env['paths']['path_format']}",
        ]

        # WSL specific info
        if env['os']['is_wsl']:
            lines.append("")
            lines.append("### Windows + WSL Setup")
            lines.append(f"- Running in WSL2 Linux environment on Windows")
            lines.append(f"- Linux path: {env['paths']['project_root']}")
            lines.append(f"- Windows path: {env['paths']['windows_equivalent']}")
            lines.append(f"- Can access Windows files at: /mnt/c, /mnt/d, etc.")
            lines.append(f"- Use WSL paths for Linux tools, convert for Windows tools")

        # Features
        if env['features']:
            lines.append("")
            lines.append("### Key Features")
            for key, value in env['features'].items():
                if key != 'note':
                    lines.append(f"- {value}")
            if 'note' in env['features']:
                lines.append(f"\n> **Note**: {env['features']['note']}")

        return '\n'.join(lines)

    def format_for_json(self) -> Dict[str, Any]:
        """Format environment info for JSON storage."""
        return self.detect()

    def print_report(self) -> None:
        """Print environment report to console."""
        env = self.detect()
        
        print("\n" + "=" * 60)
        print("DEVELOPMENT ENVIRONMENT")
        print("=" * 60 + "\n")
        
        print(f"OS: {env['os']['friendly_name']}")
        print(f"   Platform: {env['os']['platform']}")
        print(f"   Execution: {env['os']['execution_context']}\n")
        
        print(f"Python: {env['python']['version']}")
        print(f"   Implementation: {env['python']['implementation']}")
        print(f"   Executable: {env['python']['executable']}\n")
        
        print(f"Project: {env['paths']['project_name']}")
        print(f"   Root: {env['paths']['project_root']}")
        print(f"   Format: {env['paths']['path_format']}")
        if env['paths']['windows_equivalent']:
            print(f"   Windows: {env['paths']['windows_equivalent']}\n")
        
        if env['os']['is_wsl']:
            print("WSL Configuration:")
            print("   ✓ Running in WSL2")
            print("   ✓ Can run Linux tools natively")
            print("   ✓ Can access Windows files at /mnt/c, /mnt/d, etc.")
            print("   ✓ Path conversion needed for Windows interop\n")
        
        print("Detected Editors:")
        for editor in env['editor']['detected_editors']:
            print(f"   • {editor}")
        
        print("\nKey Features:")
        for key, value in env['features'].items():
            if key != 'note':
                print(f"   • {value}")
        
        print("\n" + "=" * 60 + "\n")


def get_environment_briefing(project_path: Optional[Path] = None) -> str:
    """
    Get environment briefing for AI agents.
    
    Args:
        project_path: Path to project
        
    Returns:
        Markdown-formatted environment briefing
    """
    detector = EnvironmentDetector(project_path)
    return detector.format_for_briefing()


def get_environment_json(project_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Get environment info as JSON.
    
    Args:
        project_path: Path to project
        
    Returns:
        JSON-serializable environment dict
    """
    detector = EnvironmentDetector(project_path)
    return detector.format_for_json()

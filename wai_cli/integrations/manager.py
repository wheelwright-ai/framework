"""
IDE Integration Manager.

Coordinates IDE detection, capability discovery, and configuration.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Type

from .base import IDEIntegration
from .claude_code import ClaudeCodeIntegration
from .codex import CodexIntegration
from .vscode import VSCodeIntegration
from .cursor import CursorIntegration
from .web_llm import WebLLMIntegration


class IDEManager:
    """Manages IDE integrations."""

    # Registry of available integrations
    INTEGRATIONS: List[Type[IDEIntegration]] = [
        ClaudeCodeIntegration,
        CodexIntegration,
        VSCodeIntegration,
        CursorIntegration,
        WebLLMIntegration
    ]

    def __init__(self, spoke_dir: Path):
        """Initialize IDE manager."""
        self.spoke_dir = spoke_dir
        self.detected_ides: List[IDEIntegration] = []
        self.all_integrations: List[IDEIntegration] = []

        # Initialize all integrations
        for integration_class in self.INTEGRATIONS:
            integration = integration_class(spoke_dir)
            self.all_integrations.append(integration)

            # Detect
            if integration.detect():
                self.detected_ides.append(integration)

    def detect_ides(self) -> List[Dict[str, Any]]:
        """
        Detect all IDEs being used.

        Returns:
            List of dicts with IDE info
        """
        results = []

        for ide in self.detected_ides:
            results.append({
                'name': ide.name,
                'detected': True,
                'configured': ide.is_configured(),
                'config_path': ide.config_file_path,
                'capabilities': ide.get_capabilities()
            })

        return results

    def get_integration(self, ide_name: str) -> Optional[IDEIntegration]:
        """
        Get integration by name.

        Args:
            ide_name: IDE name (e.g., 'Claude Code', 'VS Code')

        Returns:
            Integration instance or None
        """
        for integration in self.all_integrations:
            if integration.name.lower() == ide_name.lower():
                return integration
        return None

    def list_supported(self) -> List[Dict[str, Any]]:
        """
        List all supported IDE integrations with details.

        Returns:
            List of dicts with IDE info and capabilities
        """
        results = []
        for integration in self.all_integrations:
            results.append({
                'name': integration.name,
                'config_path': integration.config_file_path,
                'capabilities': integration.get_capabilities()
            })
        return results

    def configure_ide(self, ide_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Configure specific IDE.

        Args:
            ide_name: IDE to configure
            force: Overwrite existing config

        Returns:
            Configuration result
        """
        integration = self.get_integration(ide_name)

        if integration is None:
            return {
                'success': False,
                'error': f"Unknown IDE: {ide_name}",
                'available': [i.name for i in self.all_integrations]
            }

        result = integration.configure(force=force)
        result['success'] = result.get('configured', False)

        return result

    def configure_all_detected(self, force: bool = False) -> Dict[str, Any]:
        """
        Configure all detected IDEs.

        Args:
            force: Overwrite existing configs

        Returns:
            Dict with results for each IDE
        """
        results = {}

        for ide in self.detected_ides:
            result = ide.configure(force=force)
            results[ide.name] = result

        return {
            'configured_count': sum(1 for r in results.values() if r.get('configured')),
            'results': results
        }

    def get_optimization_report(self) -> Dict[str, Any]:
        """
        Get optimization report for all detected IDEs.

        Returns:
            Dict with optimization suggestions
        """
        report = {
            'detected_ides': [],
            'suggestions_by_ide': {},
            'overall_suggestions': []
        }

        for ide in self.detected_ides:
            report['detected_ides'].append(ide.name)

            suggestions = ide.get_optimization_suggestions()
            report['suggestions_by_ide'][ide.name] = suggestions

            # Add to overall if not already there
            for suggestion in suggestions:
                if suggestion not in report['overall_suggestions']:
                    report['overall_suggestions'].append(suggestion)

        return report

    def probe_capabilities(self, ide_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Probe IDE capabilities.

        Args:
            ide_name: Specific IDE to probe (None for all detected)

        Returns:
            Dict with capability information
        """
        if ide_name:
            integration = self.get_integration(ide_name)
            if integration is None:
                return {'error': f"Unknown IDE: {ide_name}"}

            return {
                'ide': ide_name,
                'capabilities': integration.get_capabilities()
            }

        # Probe all detected IDEs
        capabilities_map = {}
        for ide in self.detected_ides:
            capabilities_map[ide.name] = ide.get_capabilities()

        return {
            'detected_count': len(self.detected_ides),
            'capabilities': capabilities_map
        }

    def generate_comparison_matrix(self) -> str:
        """
        Generate comparison matrix of all IDE capabilities.

        Returns:
            Markdown table comparing IDEs
        """
        # Collect all capability keys
        all_caps = set()
        for integration in self.all_integrations:
            caps = integration.get_capabilities()
            all_caps.update(caps.keys())

        # Build matrix
        lines = []
        lines.append("# IDE Capability Comparison\n")

        # Header
        header = "| Capability | " + " | ".join([i.name for i in self.all_integrations]) + " |"
        lines.append(header)

        # Separator
        sep = "|" + "|".join(["-" * 12] * (len(self.all_integrations) + 1)) + "|"
        lines.append(sep)

        # Rows
        for cap in sorted(all_caps):
            row = [cap]
            for integration in self.all_integrations:
                caps = integration.get_capabilities()
                value = caps.get(cap, '-')

                # Format value
                if isinstance(value, bool):
                    value = '✓' if value else '✗'
                elif isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                else:
                    value = str(value)

                row.append(value)

            lines.append("| " + " | ".join(row) + " |")

        return "\n".join(lines)

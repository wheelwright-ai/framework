"""
Version Tracking for Wheelwright Framework

Multi-tier versioning system:
1. Root Version: Framework version (e.g., 3.1.0)
2. File/Module Version: Template/module version (e.g., 2.0)
3. Local Edit Sub-version: Pending local changes (e.g., 2.0-3 = 3 uncommitted improvements)

Format: ROOT.FILE.LOCAL-EDITS (e.g., 3.1.0.2.0.3 = Root 3.1.0, File v2.0, 3 local edits)
Simplified format: FILE+LOCAL-EDITS when root is fixed (e.g., 2.0-3)
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


class VersionTracker:
    """Tracks multi-tier versioning for framework components."""

    def __init__(self, spoke_path: Path):
        """Initialize version tracker."""
        self.spoke_path = spoke_path
        self.wai_spoke_dir = spoke_path / 'WAI-Spoke'
        self.version_file = self.wai_spoke_dir / 'WAI-Version.json'

    def parse_version(self, version_str: str) -> Tuple[str, str, int]:
        """
        Parse version string into components.

        Supported formats:
        - "3.1.0.2.0.3" → root=3.1.0, file=2.0, edits=3
        - "2.0-3" → file=2.0, edits=3
        - "2.0" → file=2.0, edits=0

        Returns:
            Tuple of (root_version, file_version, local_edits)
        """
        parts = version_str.split('.')
        
        # Full format: ROOT.FILE.LOCAL (e.g., 3.1.0.2.0.3)
        if len(parts) >= 6:
            root = f"{parts[0]}.{parts[1]}.{parts[2]}"
            file_v = f"{parts[3]}.{parts[4]}"
            edits = int(parts[5]) if len(parts) > 5 else 0
            return root, file_v, edits
        
        # Short format with dash: FILE-EDITS (e.g., 2.0-3)
        if '-' in version_str:
            base, edit_str = version_str.rsplit('-', 1)
            try:
                edits = int(edit_str)
            except ValueError:
                edits = 0
            return "", base, edits
        
        # Simple format: FILE only (e.g., 2.0)
        return "", version_str, 0

    def format_version(
        self,
        root: Optional[str] = None,
        file_version: Optional[str] = None,
        local_edits: int = 0
    ) -> str:
        """
        Format version into standard string.

        Returns:
        - Full format if root provided: "3.1.0.2.0.3"
        - Short format if only file: "2.0" or "2.0-3" if edits > 0
        """
        if root and file_version:
            # Full format
            return f"{root}.{file_version}.{local_edits}"
        
        if file_version:
            # Short format
            if local_edits > 0:
                return f"{file_version}-{local_edits}"
            return file_version
        
        return "unknown"

    def track_file_adoption(
        self,
        file_name: str,
        file_version: str,
        changed_from: str,
        why_changed: str,
        is_auto_adopted: bool = False
    ) -> None:
        """
        Track adoption of a file/module during teach cycle.

        Args:
            file_name: Name of file being adopted (e.g., WAI-State.json)
            file_version: Version of the file (e.g., 2.0)
            changed_from: Previous version (e.g., 1.9)
            why_changed: Description of changes
            is_auto_adopted: Whether auto-adopted vs manual review
        """
        version_state = self._load_version_state()
        
        if 'adoptions' not in version_state:
            version_state['adoptions'] = []
        
        adoption = {
            'file_name': file_name,
            'file_version': file_version,
            'changed_from': changed_from,
            'why_changed': why_changed,
            'adopted_at': datetime.utcnow().isoformat() + 'Z',
            'adoption_type': 'auto' if is_auto_adopted else 'manual',
            'adoption_timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Remove previous entry for same file if exists
        version_state['adoptions'] = [
            a for a in version_state.get('adoptions', [])
            if a.get('file_name') != file_name
        ]
        
        version_state['adoptions'].append(adoption)
        self._save_version_state(version_state)

    def increment_local_edits(self, module_name: str) -> str:
        """
        Increment local edit counter for a module.

        Returns the new version string (e.g., 2.0-1 → 2.0-2).
        """
        version_state = self._load_version_state()
        
        if 'module_versions' not in version_state:
            version_state['module_versions'] = {}
        
        if module_name not in version_state['module_versions']:
            # No previous version, start at -1
            version_state['module_versions'][module_name] = {
                'file_version': '1.0',
                'local_edits': 0
            }
        
        module_v = version_state['module_versions'][module_name]
        module_v['local_edits'] += 1
        module_v['last_edited'] = datetime.utcnow().isoformat() + 'Z'
        
        self._save_version_state(version_state)
        
        return self.format_version(
            file_version=module_v['file_version'],
            local_edits=module_v['local_edits']
        )

    def finalize_adoptions(self, root_version: str) -> Dict[str, Any]:
        """
        Finalize adoptions after teach/closeout cycle.

        Resets local edit counters and updates root version.

        Returns:
            Summary of finalized adoptions
        """
        version_state = self._load_version_state()
        summary = {
            'root_version': root_version,
            'finalized_at': datetime.utcnow().isoformat() + 'Z',
            'module_updates': {}
        }
        
        # Reset all local edit counters
        if 'module_versions' in version_state:
            for module_name, module_v in version_state['module_versions'].items():
                if module_v.get('local_edits', 0) > 0:
                    # Track that this module's changes were included in new root version
                    summary['module_updates'][module_name] = {
                        'previous_version': self.format_version(
                            file_version=module_v.get('file_version'),
                            local_edits=module_v.get('local_edits', 0)
                        ),
                        'new_version': module_v.get('file_version'),
                        'edits_submitted': module_v.get('local_edits', 0)
                    }
                    # Reset local edits
                    module_v['local_edits'] = 0
                    module_v['finalized_at'] = datetime.utcnow().isoformat() + 'Z'
        
        version_state['root_version'] = root_version
        version_state['last_finalized'] = datetime.utcnow().isoformat() + 'Z'
        self._save_version_state(version_state)
        
        return summary

    def get_current_versions(self) -> Dict[str, Any]:
        """Get current version state for all modules."""
        return self._load_version_state()

    def get_module_version(self, module_name: str) -> str:
        """Get formatted version string for a module."""
        state = self._load_version_state()
        module_v = state.get('module_versions', {}).get(module_name, {})
        
        return self.format_version(
            file_version=module_v.get('file_version', '1.0'),
            local_edits=module_v.get('local_edits', 0)
        )

    def _load_version_state(self) -> Dict[str, Any]:
        """Load version tracking state from file."""
        if self.version_file.exists():
            try:
                return json.loads(self.version_file.read_text(encoding='utf-8'))
            except Exception:
                pass
        
        # Default structure
        return {
            'structure_version': '1.0',
            'root_version': 'unknown',
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'module_versions': {},
            'adoptions': []
        }

    def _save_version_state(self, state: Dict[str, Any]) -> None:
        """Save version tracking state to file."""
        try:
            self.version_file.parent.mkdir(parents=True, exist_ok=True)
            self.version_file.write_text(
                json.dumps(state, indent=2, ensure_ascii=False) + '\n',
                encoding='utf-8'
            )
        except Exception as e:
            # Non-blocking - version tracking failure doesn't stop operations
            pass

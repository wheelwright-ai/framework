"""
Changelog generation from closed Lugs.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from .lugs import LugManager

class ChangelogGenerator:
    """Generates CHANGELOG.md content from archived Lugs."""

    def __init__(self, spoke_dir: Path):
        self.spoke_dir = spoke_dir
        self.lug_manager = LugManager(spoke_dir)

    def generate_changelog_content(self, since_last_shipit: bool = True) -> str:
        """
        Produce a markdown summary of closed tasks.
        
        Args:
            since_last_shipit: If True, only include Lugs closed in the current session.
        """
        closed_lugs = self.lug_manager.get_closed_lugs()
        
        if not closed_lugs:
            return ""

        # Filter if requested (placeholder: current session filter)
        # In a real scenario, we might track the last shipit timestamp or commit
        
        # Group by type
        groups = {
            'feat': [],
            'bug': [],
            'work': [],
            'epic': [],
            'other': []
        }
        
        for lug in closed_lugs:
            ltype = lug.type
            if ltype in groups:
                groups[ltype].append(lug)
            else:
                groups['other'].append(lug)

        lines = [f"## Release {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
        
        type_labels = {
            'feat': '[SHIPIT] Features',
            'bug': '[PROCESS] Bug Fixes',
            'work': '[PROCESS] Refactoring & Improvements',
            'epic': '[SHIPIT] Epics Completed',
            'other': '[PACKAGE] Other Changes'
        }

        has_any = False
        for ltype, label in type_labels.items():
            if groups[ltype]:
                lines.append(f"### {label}")
                for lug in groups[ltype]:
                    lines.append(f"- {lug.title} ([{lug.id}])")
                lines.append("")
                has_any = True

        if not has_any:
            return ""

        return "\n".join(lines)

    def update_changelog_file(self, target_file: Path = None):
        """Append the new changelog entry to CHANGELOG.md."""
        if target_file is None:
            target_file = self.spoke_dir / "CHANGELOG.md"
            
        new_content = self.generate_changelog_content()
        if not new_content:
            return
            
        if target_file.exists():
            existing = target_file.read_text()
            target_file.write_text(new_content + "\n\n" + existing)
        else:
            target_file.write_text("# Changelog\n\n" + new_content)

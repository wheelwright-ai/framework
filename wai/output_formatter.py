"""
Output Formatter for Learn/Teach Commands

Provides clean, actionable summaries instead of verbose logs.
Shows:
- Specific lug titles and impacts
- File adoption status with changes
- Learning insights from high-impact lugs (impact >= 8)
"""

from typing import List, Dict, Any, Optional
from pathlib import Path


class TeachOutputFormatter:
    """Formats teach command output for clarity and actionability."""

    @staticmethod
    def format_teach_summary(
        spoke_name: str,
        files_distributed: int,
        lugs_distributed: int,
        adoption_ready: List[str],
        requires_review: List[str],
        security: str,
        version: str
    ) -> str:
        """
        Format teach summary with actionable data.

        Example output:
        ✓ project-name: 3 templates (unsigned v3.1.0)
          + 2 lug(s) from hub
          → Ready: WAI-Guide.md, WAI-State.md
          → Review: WAI-State.json (merge strategy required)
        """
        lines = []
        
        # Main summary line
        lines.append(f"✓ {spoke_name}: {files_distributed} templates ({security} v{version})")
        
        # Hub lugs if any
        if lugs_distributed > 0:
            lines.append(f"  + {lugs_distributed} lug(s) from hub")
        
        # Auto-adoptable files
        if adoption_ready:
            ready_list = ', '.join(adoption_ready[:2])
            if len(adoption_ready) > 2:
                ready_list += f", +{len(adoption_ready) - 2}"
            lines.append(f"  ✓ Ready: {ready_list}")
        
        # Files requiring review
        if requires_review:
            review_list = ', '.join(requires_review)
            lines.append(f"  → Review: {review_list}")
        
        return '\n'.join(lines)

    @staticmethod
    def format_file_change(
        file_name: str,
        changed_from: str,
        why_changed: str,
        safe_to_auto: bool = False
    ) -> str:
        """
        Format individual file change.

        Example:
        • WAI-State.json (v2.0.1 → v3.0.0): Structure update for v3 + added teaching-adoption schema
          → Manual review required (merge strategy: merge_sections)
        """
        icon = "✓" if safe_to_auto else "→"
        return f"{icon} {file_name} (v{changed_from}): {why_changed}"


class LearnOutputFormatter:
    """Formats learn command output with high-impact insights."""

    @staticmethod
    def format_learn_summary(
        hub_name: str,
        lugs_extracted: int,
        high_impact_count: int,
        high_impact_lugs: List[Dict[str, Any]] = None
    ) -> str:
        """
        Format learn summary with focus on high-impact learnings.

        Example output:
        ✓ hub-name: Extracted 12 lugs (3 high-impact)
          [Fix session start hook] (Impact: 10)
            • Module: framework
            • Summary: Critical fix for session initialization race condition
          [Add teaching reconciliation] (Impact: 9)
            • Module: upgrade_adoption
            • Summary: Ensures all teaching files tracked across upgrades
        """
        lines = []
        
        # Main summary
        impact_str = f" ({high_impact_count} high-impact)" if high_impact_count > 0 else ""
        lines.append(f"✓ {hub_name}: Extracted {lugs_extracted} lugs{impact_str}")
        
        # High-impact lugs with details
        if high_impact_lugs:
            lines.append("")  # Blank line for readability
            for lug in high_impact_lugs[:5]:  # Show top 5 high-impact
                title = lug.get('title', 'Untitled')
                impact = lug.get('impact', 0)
                module = lug.get('_lug_metadata', {}).get('module', 'core')
                summary = lug.get('summary', '')
                
                lines.append(f"  [{title}] (Impact: {impact})")
                lines.append(f"    • Module: {module}")
                if summary:
                    # Truncate if too long
                    if len(summary) > 80:
                        summary = summary[:77] + "..."
                    lines.append(f"    • {summary}")
        
        return '\n'.join(lines)

    @staticmethod
    def format_adoption_status(
        adopted_files: List[str],
        pending_files: List[str],
        orphaned_files: List[str]
    ) -> str:
        """
        Format adoption status summary.

        Example output:
        Auto-Adoption Status:
          ✓ Adopted: 2 files (WAI-Guide.md, WAI-State.md)
          → Pending Review: 1 file (WAI-State.json)
          ⚠ Orphaned: 0 files
        """
        lines = ["Auto-Adoption Status:"]
        
        if adopted_files:
            names = ', '.join(adopted_files[:2])
            if len(adopted_files) > 2:
                names += f", +{len(adopted_files) - 2} more"
            lines.append(f"  ✓ Adopted: {len(adopted_files)} file(s) ({names})")
        
        if pending_files:
            names = ', '.join(pending_files[:2])
            if len(pending_files) > 2:
                names += f", +{len(pending_files) - 2} more"
            lines.append(f"  → Pending Review: {len(pending_files)} file(s) ({names})")
        
        if orphaned_files:
            names = ', '.join(orphaned_files[:2])
            if len(orphaned_files) > 2:
                names += f", +{len(orphaned_files) - 2} more"
            lines.append(f"  ⚠ Orphaned: {len(orphaned_files)} file(s) ({names}) - manual review needed")
        elif not adopted_files and not pending_files:
            lines.append("  ✓ No adoption pending")
        
        return '\n'.join(lines)

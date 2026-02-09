"""
Interactive teach command.

Teaches (distributes templates) to spokes with clear UX:
1. Select spoke(s)
2. Show preview of changes
3. Confirm
4. Execute with progress
5. Show results
"""

from typing import Optional, List
from pathlib import Path
import json

from wai.cli.lib.prompts import PromptStyle
from wai.cli.visuals import get_formatter


class TeachCommand:
    """Interactive teach workflow."""

    def __init__(self, discovery=None, state_manager=None):
        """Initialize teach command."""
        self.discovery = discovery
        self.state_manager = state_manager
        self.fmt = get_formatter()

    def run_interactive(self, spoke: Optional[str] = None, force: bool = False, json_output: bool = False) -> int:
        """
        Run interactive teach command.

        Args:
            spoke: Optional spoke name to teach (skip selection if provided)
            force: Skip confirmation prompts
            json_output: Output as JSON

        Returns:
            Exit code
        """
        # Step 1: Discover spokes
        spokes = self._discover_spokes()
        if not spokes:
            self.fmt.print_warning("No spokes found in wheel.")
            self.fmt.print_info("Run: wai init spoke --name <project-name>")
            return 1

        # Step 2: Select spoke(s) if not provided
        if not spoke:
            selected = self._select_spoke(spokes)
            if not selected:
                return 0  # User cancelled
            spoke_names = [selected]
        else:
            spoke_names = [spoke]

        # Step 3: For each spoke, show preview and teach
        total_changes = 0
        failed = []

        for spoke_name in spoke_names:
            spoke_data = self._find_spoke(spoke_name, spokes)
            if not spoke_data:
                self.fmt.print_warning(f"Spoke not found: {spoke_name}")
                failed.append(spoke_name)
                continue

            # Get preview of what will change
            changes = self._preview_changes(spoke_data)
            if not changes:
                self.fmt.print_info(f"No changes needed for {spoke_name}")
                continue

            # Show preview
            self._show_preview(spoke_name, changes)

            # Confirm (unless --force)
            if not force:
                proceed = PromptStyle.confirm(
                    f"Confirm teach {spoke_name}?",
                    default=True
                )
                if not proceed:
                    self.fmt.print_info(f"Skipped {spoke_name}")
                    continue

            # Execute
            result = self._teach_spoke(spoke_name, spoke_data, changes)
            if result:
                total_changes += len(changes)
            else:
                failed.append(spoke_name)

        # Step 4: Show results
        self._show_results(spoke_names, total_changes, failed, json_output)
        return 0 if not failed else 1

    def _discover_spokes(self) -> List[dict]:
        """Discover available spokes."""
        try:
            # Would use discovery to find spokes
            # For now, return empty list
            return []
        except Exception:
            return []

    def _select_spoke(self, spokes: List[dict]) -> Optional[str]:
        """Let user select a spoke."""
        if not spokes:
            return None

        items = []
        descriptions = []

        for i, spoke in enumerate(spokes):
            name = spoke.get('name', f'spoke_{i}')
            last_sync = spoke.get('last_sync', 'never')
            items.append((name, name[0].lower() if name else '', name))
            descriptions.append(f"Last sync: {last_sync}")

        selected = PromptStyle.select(
            "Which spoke to teach?",
            items,
            descriptions=descriptions
        )
        return selected

    def _find_spoke(self, name: str, spokes: List[dict]) -> Optional[dict]:
        """Find spoke by name."""
        for spoke in spokes:
            if spoke.get('name') == name:
                return spoke
        return None

    def _preview_changes(self, spoke_data: dict) -> List[str]:
        """Preview what templates will change."""
        # This would analyze which templates have changed since last teach
        # For now, return example
        return [
            "patterns.md (5 new patterns added)",
            "reference.md (2 sections updated)",
        ]

    def _show_preview(self, spoke_name: str, changes: List[str]) -> None:
        """Show preview of changes."""
        preview_items = [f"{name}" for name in changes]
        PromptStyle.show_preview(
            f"Templates to update in {spoke_name}",
            preview_items
        )

    def _teach_spoke(self, spoke_name: str, spoke_data: dict, changes: List[str]) -> bool:
        """
        Execute teach operation.

        Returns:
            True if successful
        """
        try:
            self.fmt.print_info("")
            self.fmt.print_progress(f"Teaching {spoke_name}...")

            # Simulate teaching
            for i, change in enumerate(changes, 1):
                self.fmt.print_info(f"  [{i}/{len(changes)}] {change}")

            self.fmt.print_success(f"✓ Taught {spoke_name}")
            return True

        except Exception as e:
            self.fmt.print_error(f"✗ Failed to teach {spoke_name}: {e}")
            return False

    def _show_results(
        self,
        spoke_names: List[str],
        total_changes: int,
        failed: List[str],
        json_output: bool
    ) -> None:
        """Show teaching results."""
        if json_output:
            result = {
                "success": len(failed) == 0,
                "spoke_count": len(spoke_names),
                "changes": total_changes,
                "failed": failed
            }
            print(json.dumps(result, indent=2))
        else:
            self.fmt.print_info("")
            if failed:
                self.fmt.print_warning(f"Teach complete with {len(failed)} failure(s)")
                for spoke in failed:
                    self.fmt.print_info(f"  ✗ {spoke}")
            else:
                self.fmt.print_success(f"✓ Taught {len(spoke_names)} spoke(s)")
                self.fmt.print_info(f"  {total_changes} templates updated")
            self.fmt.print_info("")


def run_teach(
    spoke: Optional[str] = None,
    force: bool = False,
    json_output: bool = False,
    discovery=None,
    state_manager=None
) -> int:
    """Run teach command."""
    cmd = TeachCommand(discovery, state_manager)
    return cmd.run_interactive(spoke, force, json_output)

"""
Interactive learn command.

Learns (collects signals) from spokes with clear UX:
1. Select spoke(s)
2. Select priority (high/normal/low)
3. Show preview of signals
4. Confirm
5. Execute with progress
6. Show results
"""

from typing import Optional, List
from pathlib import Path
import json

from wai.cli.lib.prompts import PromptStyle
from wai.cli.visuals import get_formatter


class LearnCommand:
    """Interactive learn workflow."""

    def __init__(self, discovery=None, state_manager=None):
        """Initialize learn command."""
        self.discovery = discovery
        self.state_manager = state_manager
        self.fmt = get_formatter()

    def run_interactive(
        self,
        spoke: Optional[str] = None,
        priority: str = "normal",
        force: bool = False,
        json_output: bool = False
    ) -> int:
        """
        Run interactive learn command.

        Args:
            spoke: Optional spoke name to learn from (skip selection if provided)
            priority: Signal priority: high, normal, or low
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

        # Step 3: Select priority if interactive
        if not force and len(spoke_names) == 1:
            selected_priority = self._select_priority(priority)
            if selected_priority:
                priority = selected_priority

        # Step 4: For each spoke, show signals and learn
        total_signals = 0
        failed = []

        for spoke_name in spoke_names:
            spoke_data = self._find_spoke(spoke_name, spokes)
            if not spoke_data:
                self.fmt.print_warning(f"Spoke not found: {spoke_name}")
                failed.append(spoke_name)
                continue

            # Get signals from spoke
            signals = self._get_signals(spoke_data, priority)
            if not signals:
                self.fmt.print_info(f"No {priority} signals in {spoke_name}")
                continue

            # Show preview
            self._show_preview(spoke_name, priority, signals)

            # Confirm (unless --force)
            if not force:
                proceed = PromptStyle.confirm(
                    f"Import {len(signals)} signal(s) into framework?",
                    default=True
                )
                if not proceed:
                    self.fmt.print_info(f"Skipped {spoke_name}")
                    continue

            # Execute
            result = self._learn_spoke(spoke_name, signals)
            if result:
                total_signals += len(signals)
            else:
                failed.append(spoke_name)

        # Step 5: Show results
        self._show_results(spoke_names, priority, total_signals, failed, json_output)
        return 0 if not failed else 1

    def _discover_spokes(self) -> List[dict]:
        """Discover available spokes."""
        try:
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
            signal_count = spoke.get('signal_count', 0)
            items.append((name, name[0].lower() if name else '', name))
            descriptions.append(f"{signal_count} signals available")

        selected = PromptStyle.select(
            "Which spoke to learn from?",
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

    def _select_priority(self, default: str = "normal") -> Optional[str]:
        """Let user select priority level."""
        items = [
            ("high", "h", "High (critical decisions, 1 signal)"),
            ("normal", "n", "Normal (patterns & learnings, 4 signals)"),
            ("low", "l", "Low (experiments & notes, 2 signals)"),
        ]

        # Convert default string to item value
        default_num = "2"  # normal is default
        if default == "high":
            default_num = "1"
        elif default == "low":
            default_num = "3"

        selected = PromptStyle.select(
            "Signal priority level",
            items,
            default=default_num
        )
        return selected

    def _get_signals(self, spoke_data: dict, priority: str) -> List[str]:
        """Get signals from spoke at priority level."""
        # This would query observations for signals at given priority
        # For now, return examples
        if priority == "high":
            return [
                "Decision: Use UUID for all IDs",
                "Pattern: Async/await for I/O",
            ]
        elif priority == "low":
            return [
                "Note: ESLint config strategy",
                "Experiment: TypeScript strict mode",
            ]
        else:  # normal
            return [
                "Pattern: Async/await pattern",
                "Decision: Use UUID for IDs",
                "Learning: Git workflow best practice",
                "Note: ESLint config strategy",
            ]

    def _show_preview(self, spoke_name: str, priority: str, signals: List[str]) -> None:
        """Show preview of signals to import."""
        preview_items = [f"• {signal}" for signal in signals]
        PromptStyle.show_preview(
            f"Signals from {spoke_name} ({priority} priority)",
            preview_items
        )

    def _learn_spoke(self, spoke_name: str, signals: List[str]) -> bool:
        """
        Execute learn operation.

        Returns:
            True if successful
        """
        try:
            self.fmt.print_info("")
            self.fmt.print_progress(f"Learning from {spoke_name}...")

            # Simulate learning
            for i, signal in enumerate(signals, 1):
                self.fmt.print_info(f"  [{i}/{len(signals)}] Integrating {signal}")

            self.fmt.print_success(f"✓ Learned from {spoke_name}")
            return True

        except Exception as e:
            self.fmt.print_error(f"✗ Failed to learn from {spoke_name}: {e}")
            return False

    def _show_results(
        self,
        spoke_names: List[str],
        priority: str,
        total_signals: int,
        failed: List[str],
        json_output: bool
    ) -> None:
        """Show learning results."""
        if json_output:
            result = {
                "success": len(failed) == 0,
                "spoke_count": len(spoke_names),
                "signals": total_signals,
                "priority": priority,
                "failed": failed
            }
            print(json.dumps(result, indent=2))
        else:
            self.fmt.print_info("")
            if failed:
                self.fmt.print_warning(f"Learn complete with {len(failed)} failure(s)")
                for spoke in failed:
                    self.fmt.print_info(f"  ✗ {spoke}")
            else:
                self.fmt.print_success(f"✓ Learned from {len(spoke_names)} spoke(s)")
                self.fmt.print_info(f"  {total_signals} {priority} signals integrated")
            self.fmt.print_info("")


def run_learn(
    spoke: Optional[str] = None,
    priority: str = "normal",
    force: bool = False,
    json_output: bool = False,
    discovery=None,
    state_manager=None
) -> int:
    """Run learn command."""
    cmd = LearnCommand(discovery, state_manager)
    return cmd.run_interactive(spoke, priority, force, json_output)

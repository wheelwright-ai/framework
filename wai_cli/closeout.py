"""
Smart closeout processor for Wheelwright sessions.

Handles end-of-session processing including:
- File scanning and reconciliation
- Content rebalancing
- Signal extraction
- Analytics recording
- Log cleanup
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .session import SessionManager
from .rebalancer import FileRebalancer
from .metrics import MetricsTracker
from .quality_gates import QualityGates
from .utils.input import print_success, print_error, print_info, print_warning, safe_confirm


class CloseoutProcessor:
    """Processes session closeout comprehensively."""

    def __init__(self, spoke_dir: Path):
        """Initialize closeout processor."""
        self.spoke_dir = spoke_dir
        self.wai_spoke_dir = spoke_dir / 'WAI-Spoke'

        # Initialize components
        self.session = SessionManager(spoke_dir)
        self.rebalancer = FileRebalancer(self.wai_spoke_dir)
        self.metrics = MetricsTracker(self.wai_spoke_dir)
        self.quality_gates = QualityGates(spoke_dir)

    def process_closeout(self, interactive: bool = True) -> Dict[str, Any]:
        """
        Execute complete closeout workflow.

        Args:
            interactive: If True, prompts user for confirmations

        Returns:
            Dict with closeout summary
        """
        print_info("\n🔄 Processing Session Closeout...\n")

        results = {
            'steps_completed': [],
            'warnings': [],
            'errors': [],
            'session_summary': {},
            'quality_gates': {}
        }

        # Step 0: Run Quality Gates (unless truly minor changes)
        print_info("  Step 0/8: Running quality gates...")
        gate_results = self.quality_gates.run_all_gates(skip_minor=True)
        results['quality_gates'] = gate_results

        if gate_results.get('skip_reason'):
            print_info(f"    ⚠️  {gate_results['skip_reason']}")
            results['steps_completed'].append(f"Quality gates: {gate_results['skip_reason']}")
        elif not gate_results['passed']:
            # Quality gates failed
            print_warning("    ⚠️  Quality gates failed!")

            for blocker in gate_results.get('blockers', []):
                print_error(f"      ✗ BLOCKER: {blocker}")

            for warning in gate_results.get('warnings', []):
                print_warning(f"      ⚠️  {warning}")

            if interactive and gate_results.get('blockers'):
                print_info("\n  Quality gate blockers detected. Continue anyway?")
                if not safe_confirm("Proceed with closeout despite blockers?", default=False):
                    results['errors'].append("Closeout aborted due to quality gate failures")
                    return results

            results['steps_completed'].append(f"Quality gates: Failed with {len(gate_results.get('blockers', []))} blockers")
        else:
            print_success("    ✓ All quality gates passed")
            results['steps_completed'].append("Quality gates: Passed")

        # Step 1: Scan for unknown files
        print_info("  Step 1/8: Scanning for unknown files...")
        unknown_files = self._scan_unknown_files(interactive)
        if unknown_files:
            results['warnings'].append(f"Found {len(unknown_files)} unknown files")
            results['steps_completed'].append(f"Scanned files: {len(unknown_files)} unknown")
        else:
            results['steps_completed'].append("Scanned files: all known")

        # Step 2: Reconcile WAI-Hub-Learnings.md if exists
        print_info("  Step 2/8: Reconciling hub learnings...")
        learnings_reconciled = self._reconcile_hub_learnings()
        if learnings_reconciled:
            results['steps_completed'].append("Reconciled hub learnings into WAI-Guide.md")

        # Step 3: Run file rebalancer
        print_info("  Step 3/8: Rebalancing file content...")
        rebalance_result = self.rebalancer.rebalance()
        if rebalance_result['rebalanced']:
            results['steps_completed'].append(f"Rebalanced files: {len(rebalance_result['actions'])} actions")
        else:
            results['steps_completed'].append("Files balanced: no action needed")

        # Step 4: Extract session summary
        print_info("  Step 4/8: Extracting session summary...")
        session_summary = self.session.extract_session_summary()
        results['session_summary'] = session_summary
        results['steps_completed'].append(f"Extracted summary: {session_summary['turns']} turns")

        # Step 5: Extract high-impact signals
        print_info("  Step 5/8: Extracting high-impact signals...")
        signals_extracted = self._extract_signals()
        if signals_extracted > 0:
            results['steps_completed'].append(f"Extracted {signals_extracted} high-impact signals")
        else:
            results['steps_completed'].append("No new signals to extract")

        # Step 6: Record analytics
        print_info("  Step 6/8: Recording session analytics...")
        self._record_analytics(session_summary)
        results['steps_completed'].append("Recorded session analytics")

        # Step 7: Update session state and clear log
        print_info("  Step 7/8: Finalizing closeout...")
        self._finalize_closeout(session_summary)
        results['steps_completed'].append("Finalized: state updated, log cleared")

        print_success("\n✓ Closeout Complete!\n")

        return results

    def _scan_unknown_files(self, interactive: bool) -> List[Path]:
        """Scan for and handle unknown files."""
        unknown_files = self.rebalancer.scan_unknown_files()

        if not unknown_files:
            return []

        print_warning(f"\n  ⚠️  Found {len(unknown_files)} unknown file(s) in WAI-Spoke/:\n")

        for file in unknown_files:
            print_info(f"      - {file.name}")

        if interactive:
            print_info("\n  What should we do with these files?")
            print_info("    1. Keep them (manual reconciliation later)")
            print_info("    2. Show file contents (review before deciding)")
            print_info("    3. Delete them")

            choice = input("\n  Choice [1]: ").strip() or "1"

            if choice == "2":
                for file in unknown_files:
                    print_info(f"\n  Contents of {file.name}:")
                    print_info(f"  {'-' * 60}")
                    if file.is_file():
                        content = file.read_text()[:500]  # First 500 chars
                        print_info(f"  {content}")
                        if len(file.read_text()) > 500:
                            print_info("  ... (truncated)")
                    print_info(f"  {'-' * 60}")

                # Ask again after showing
                if safe_confirm("Delete these files?", default=False):
                    for file in unknown_files:
                        if file.is_file():
                            file.unlink()
                        else:
                            import shutil
                            shutil.rmtree(file)
                    print_success(f"\n  ✓ Deleted {len(unknown_files)} unknown files")
                    return []

            elif choice == "3":
                for file in unknown_files:
                    if file.is_file():
                        file.unlink()
                    else:
                        import shutil
                        shutil.rmtree(file)
                print_success(f"\n  ✓ Deleted {len(unknown_files)} unknown files")
                return []

        return unknown_files

    def _reconcile_hub_learnings(self) -> bool:
        """
        Reconcile WAI-Hub-Learnings.md into WAI-Guide.md.

        Returns:
            True if learnings were reconciled
        """
        learnings_file = self.wai_spoke_dir / 'WAI-Hub-Learnings.md'
        guide_file = self.wai_spoke_dir / 'WAI-Guide.md'

        if not learnings_file.exists():
            return False

        # Read learnings content
        learnings_content = learnings_file.read_text()

        # Read existing guide
        guide_content = guide_file.read_text()

        # Add hub learnings section if not exists
        hub_section_header = "\n## Hub Learnings\n\n"
        if hub_section_header not in guide_content:
            guide_content += hub_section_header

        # Extract just the patterns (skip header and instructions)
        import re
        pattern_sections = re.findall(r'## (Pattern|Decision|Insight|Warning).*?(?=##|$)', learnings_content, re.DOTALL)

        # Append new patterns to guide
        for section in pattern_sections:
            guide_content += f"\n## {section}\n"

        # Write updated guide
        guide_file.write_text(guide_content)

        # Delete learnings file (reconciled)
        learnings_file.unlink()

        print_success("  ✓ Reconciled hub learnings into WAI-Guide.md")

        return True

    def _extract_signals(self) -> int:
        """
        Extract high-impact signals from session.

        Returns:
            Number of signals extracted
        """
        # For now, return 0 - this will be enhanced in Phase 4
        # to actually analyze conversation log for patterns
        return 0

    def _record_analytics(self, session_summary: Dict[str, Any]) -> None:
        """Record session completion in analytics."""
        # Calculate session duration (placeholder - will be real in session tracking)
        session_data = {
            'session_id': 'manual-closeout',  # Will be real session ID
            'turns': session_summary.get('turns', 0),
            'tokens_estimate': 0,  # Will be calculated from log
            'duration_seconds': 0,  # Will be real duration
            'time_together_seconds': 0,  # Placeholder
            'time_ai_alone_seconds': 0,  # Placeholder
        }

        self.metrics.record_session_end(session_data)

    def _finalize_closeout(self, session_summary: Dict[str, Any]) -> None:
        """Finalize closeout by updating state and clearing log."""
        state_file = self.wai_spoke_dir / 'WAI-State.json'

        with open(state_file, 'r') as f:
            state = json.load(f)

        # Move current_session to last_closeout
        current_session = state.get('_session_state', {}).get('current_session')

        if current_session:
            state['_session_state']['last_closeout'] = {
                **current_session,
                'closed_at': datetime.now().isoformat(),
                'summary': session_summary.get('summary', 'Session complete'),
                'key_topics': session_summary.get('key_topics', []),
                'files_modified': session_summary.get('files_modified', [])
            }

        # Clear current session
        state['_session_state']['current_session'] = None
        state['_session_state']['protocol_completed'] = False
        state['_session_state']['requires_review'] = False

        # Save state
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

        # Clear conversation log
        self.session.clear_log()

    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print closeout summary."""
        print_info("\n" + "=" * 60)
        print_success("  Session Closeout Summary")
        print_info("=" * 60 + "\n")

        session_summary = results['session_summary']

        print_info(f"  Turns: {session_summary.get('turns', 0)}")
        print_info(f"  Summary: {session_summary.get('summary', 'N/A')[:100]}...")

        if session_summary.get('key_topics'):
            print_info(f"  Key topics: {', '.join(session_summary['key_topics'])}")

        if session_summary.get('files_modified'):
            print_info(f"  Files modified: {len(session_summary['files_modified'])}")

        print_info("\n  Steps completed:")
        for step in results['steps_completed']:
            print_success(f"    ✓ {step}")

        if results['warnings']:
            print_info("\n  Warnings:")
            for warning in results['warnings']:
                print_warning(f"    ⚠️  {warning}")

        if results['errors']:
            print_info("\n  Errors:")
            for error in results['errors']:
                print_error(f"    ✗ {error}")

        print_info("\n" + "=" * 60)
        print_info("  WAI-Spoke/ folder ready for hub learning")
        print_info("  Start new session with fresh context")
        print_info("=" * 60 + "\n")


def generate_closeout() -> None:
    """Generate session closeout (legacy function for backward compatibility)."""
    print_warning("\n⚠️  Using legacy closeout stub.")
    print_info("Use CloseoutProcessor for full functionality.\n")

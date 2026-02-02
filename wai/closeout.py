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
import subprocess

from .session import SessionManager
from .sessions import MultiEnvSessionManager
from .rebalancer import FileRebalancer
from .metrics import MetricsTracker
from .quality_gates import QualityGates
from .utils.input import print_success, print_error, print_info, print_warning, safe_confirm, safe_menu_choice
from .integrations.manager import IDEManager
from .lugs import LugManager
from .point import PointManager
from .agents_integration import AgentsIntegration
import os
from git import Repo, exc as git_exc


class CloseoutProcessor:
    """Processes session closeout comprehensively."""

    def __init__(self, spoke_dir: Path):
        """Initialize closeout processor."""
        self.spoke_dir = spoke_dir
        self.wai_spoke_dir = spoke_dir / 'WAI-Spoke'

        # Initialize components
        self.session = SessionManager(spoke_dir)
        self.multi_session = MultiEnvSessionManager(spoke_dir)
        self.rebalancer = FileRebalancer(self.wai_spoke_dir)
        self.metrics = MetricsTracker(self.wai_spoke_dir)
        self.quality_gates = QualityGates(spoke_dir)
        self.quality_gates = QualityGates(spoke_dir)
        self.lug_manager = LugManager(self.wai_spoke_dir)
        self.point_manager = PointManager(spoke_dir)
        self.point_manager = PointManager(spoke_dir)

    def process_closeout(self, interactive: bool = True, skip_quality_gates: bool = False) -> Dict[str, Any]:
        """
        Execute complete closeout workflow.

        Args:
            interactive: If True, prompts user for confirmations
            skip_quality_gates: If True, skip quality gate execution

        Returns:
            Dict with closeout summary
        """
        print_info("\n[PROCESS] Processing Session Closeout...\n")

        results = {
            'steps_completed': [],
            'warnings': [],
            'errors': [],
            'session_summary': {},
            'quality_gates': {}
        }

        # Step 0: Run Quality Gates (unless truly minor changes)
        if skip_quality_gates:
            print_info("  Step 0/10: Skipping quality gates (remote upgrade)")
            results['steps_completed'].append("Quality gates: Skipped (remote upgrade)")
            results['quality_gates'] = {"skipped": True, "skip_reason": "remote upgrade"}
        else:
            print_info("")
            print_info("-" * 30)
            print_info("[PROCESS] [1/13] Quality Gates")
            print_info("-" * 30)
            gate_results = self.quality_gates.run_all_gates(skip_minor=True)
            results['quality_gates'] = gate_results

            if gate_results.get('skip_reason'):
                print_info(f"    {gate_results['skip_reason']}")
                results['steps_completed'].append(f"Quality gates: Skipped (recent pass)")
            elif not gate_results['passed']:
                # Quality gates failed
                print_warning("    [WARN] Quality gates failed!")

                for blocker in gate_results.get('blockers', []):
                    print_error(f"      [ERROR] BLOCKER: {blocker}")

                for warning in gate_results.get('warnings', []):
                    print_warning(f"      [WARN] {warning}")

                if interactive and gate_results.get('blockers'):
                    print_info("\n  Quality gate blockers detected. Continue anyway?")
                    if not safe_confirm("Proceed with closeout despite blockers?", default=False):
                        results['errors'].append("Closeout aborted due to quality gate failures")
                        return results

                results['steps_completed'].append(f"Quality gates: Failed with {len(gate_results.get('blockers', []))} blockers")
            else:
                print_success("    [OK] All quality gates passed")
                results['steps_completed'].append("Quality gates: Passed")

        # Step 2: Lug Policy Validation (Blocker check)
        print_info("")
        print_info("-" * 30)
        print_info("[PROCESS] [2/13] Lug Policy Validation")
        print_info("-" * 30)
        session_state = self.session.get_state()
        session_id = session_state.get('session_id')
        
        if session_id:
            # Pass 1: Interactive Resolution Loop
            while True:
                session_lugs = self.lug_manager.get_session_lugs(session_id)
                if not session_lugs:
                    break
                    
                violations_found = False
                unresolved = False
                
                for lug in session_lugs:
                    violations = self.lug_manager.validate_policies(lug)
                    if violations:
                        violations_found = True
                        print_warning(f"    [WARN] Policy violations for Lug {lug.id} ({lug.title}):")
                        for v in violations:
                            print_error(f"      [ERROR] {v}")
                            
                        if not interactive:
                            unresolved = True
                            continue
                            
                        # Interactive menu
                        print_info("")
                        print_info(f"    Actions for '{lug.title}':")
                        print_info("      [f] Force Close (archive despite violation)")
                        print_info("      [u] Unlink from Session (keep open, remove from scope)")
                        print_info("      [d] Delete Lug (permanently remove)")
                        print_info("      [i] Ignore for now")
                        
                        choice = safe_menu_choice(
                            "    Select action",
                            [
                                ('f', 'f', 'Force Close', 'force'),
                                ('u', 'u', 'Unlink', 'unlink'),
                                ('d', 'd', 'Delete Lug', 'delete'),
                                ('i', 'i', 'Ignore', 'ignore')
                            ],
                            default='i'
                        )
                        
                        if choice == 'force':
                            self.lug_manager.close_lug(lug.id, summary="Force closed during shipit", skip_policy_check=True)
                            print_success(f"      [OK] Force closed {lug.id}")
                        elif choice == 'unlink':
                            self.lug_manager.update_lug(lug.id, extras={'session_id': None})
                            print_success(f"      [OK] Unlinked {lug.id} from session")
                        elif choice == 'delete':
                            self.lug_manager.delete_lug(lug.id)
                            print_success(f"      [OK] Deleted {lug.id}")
                        else:
                            unresolved = True
                
                if not violations_found:
                    break
                    
                # If we have violations but solved them all? No, logical flow:
                # Iterate all. If we solve one, loop continues to next lug.
                # After loop, if 'unresolved' is False, we are good.
                # If 'unresolved' is True, we check if user wants to proceed anyway or abort.
                
                if unresolved:
                    if interactive and safe_confirm("\nUnresolved violations remain. Review again?", default=True):
                        continue # Loop again
                    break # Break loop, handle unresolved below
                else:
                    break # All resolved
            
            # Final check (post-resolution)
            session_lugs = self.lug_manager.get_session_lugs(session_id)
            final_violations = False
            for lug in session_lugs:
                if self.lug_manager.validate_policies(lug):
                    final_violations = True
                    break
            
            if final_violations:
                if interactive:
                    if not safe_confirm("\nProceed despite remaining Lug policy violations?", default=False):
                        results['errors'].append("Closeout aborted due to Lug policy violations")
                        return results
                else:
                    # Non-interactive: fail on violations
                    results['errors'].append("Closeout aborted due to Lug policy violations") 
                    return results

            results['steps_completed'].append(f"Lug policies: Validated {len(session_lugs)} Lugs")
            
            if not session_lugs:
                 # Suggest inferring Lugs if none found/remaining for session
                try:
                    repo = Repo(self.spoke_dir, search_parent_directories=True)
                    suggestions = self.lug_manager.infer_lugs_from_git(repo)
                    if suggestions:
                        print_info(f"    [NOTE] Found {len(suggestions)} possible Lugs in your changes.")
                        if interactive and safe_confirm("Create suggested Lugs?", default=False):
                            for sug in suggestions:
                                self.lug_manager.create_lug(
                                    title=sug['title'],
                                    lug_type=sug['type'],
                                    priority=sug['priority'],
                                    from_file=sug['from_file'],
                                    extras={'session_id': session_id, 'inferred_reason': sug['reason']}
                                )
                            results['steps_completed'].append(f"Lugs: Inferred and created {len(suggestions)} Lugs")
                except Exception:
                    pass


        # Step 3: Process seed folders and clean up sprawl
        print_info("")
        print_info("-" * 30)
        print_info("[PROCESS] [3/13] Seed Folders & Cleanup")
        print_info("-" * 30)
        seed_result = self._process_seed_and_cleanup(interactive)
        results['steps_completed'].append(seed_result['summary'])
        results['warnings'].extend(seed_result.get('warnings', []))

        # Step 4: Reconcile WAI-Hub-Learnings.md if exists
        print_info("")
        print_info("-" * 30)
        print_info("[PROCESS] [4/13] Hub Learnings Reconciliation")
        print_info("-" * 30)
        learnings_reconciled = self._reconcile_hub_learnings()
        if learnings_reconciled:
            results['steps_completed'].append("Reconciled hub learnings into WAI-Guide.md")

        # Step 5: Run file rebalancer
        print_info("")
        print_info("-" * 30)
        print_info("[PROCESS] [5/13] File Content Rebalancing")
        print_info("-" * 30)
        rebalance_result = self.rebalancer.rebalance()
        if rebalance_result['rebalanced']:
            results['steps_completed'].append(f"Rebalanced files: {len(rebalance_result['actions'])} actions")
        else:
            results['steps_completed'].append("Files balanced: no action needed")

        # Step 6: Extract session summary
        print_info("")
        print_info("-" * 30)
        print_info("[PROCESS] [6/13] Session Summary Extraction")
        print_info("-" * 30)
        session_summary = self.session.extract_session_summary()
        results['session_summary'] = session_summary
        results['steps_completed'].append(f"Extracted summary: {session_summary['turns']} turns")

        # Step 7: Extract high-impact signals
        print_info("")
        print_info("-" * 30)
        print_info("[PROCESS] [7/13] Signal Extraction")
        print_info("-" * 30)
        signals_extracted = self._extract_signals()
        if signals_extracted > 0:
            results['steps_completed'].append(f"Extracted {signals_extracted} high-impact signals")
        else:
            results['steps_completed'].append("No new signals to extract")

        # Step 8: Record analytics
        print_info("")
        print_info("-" * 30)
        print_info("[PROCESS] [8/13] Recording Analytics")
        print_info("-" * 30)
        self._record_analytics(session_summary)
        results['steps_completed'].append("Recorded session analytics")

        # Step 9: Update session state and clear log
        print_info("")
        print_info("-" * 30)
        print_info("[PROCESS] [9/13] Finalizing Closeout")
        print_info("-" * 30)
        self._finalize_closeout(session_summary)
        results['steps_completed'].append("Finalized: state updated, log cleared")

        # Step 10: Reconcile multi-environment sessions
        print_info("")
        print_info("-" * 30)
        print_info("[PROCESS] [10/13] Multi-Environment Reconciliation")
        print_info("-" * 30)
        reconcile_result = self.multi_session.reconcile_sessions()
        results['session_reconciliation'] = reconcile_result
        if reconcile_result['sessions_processed'] > 0:
            results['steps_completed'].append(
                f"Sessions reconciled: {reconcile_result['entries_reconciled']} entries, "
                f"{reconcile_result['decisions_extracted']} decisions"
            )
        else:
            results['steps_completed'].append("No environment sessions to reconcile")

        # Step 11: Refresh integrations and optionally re-brief active session
        print_info("")
        print_info("-" * 30)
        print_info("[PROCESS] [11/13] Refreshing Integrations")
        print_info("-" * 30)
        integration_status = self._refresh_integrations()
        results['integration_status'] = integration_status
        results['steps_completed'].append(f"Integrations refreshed: {integration_status['updated']} updated")

        # Step 12: Update WAI-Point bootstrap
        print_info("")
        print_info("-" * 30)
        print_info("[PROCESS] [12/13] WAI-Point Bootstrap")
        print_info("-" * 30)
        self.point_manager.update_from_state()
        results['steps_completed'].append("Updated WAI-Point bootstrap")

        # Step 13: Update Website Content (if exists)
        # [REFACTORED] Added as rule - update website content on each closeout
        print_info("")
        print_info("-" * 30)
        print_info("[PROCESS] [13/13] Website Content Update")
        print_info("-" * 30)
        website_updated = self._update_website_content(session_summary)
        if website_updated:
            results['steps_completed'].append("Updated website content")
        else:
            results['steps_completed'].append("No website content to update")

        print_success("\n[OK] Closeout Complete!\n")

        return results

    def _process_seed_and_cleanup(self, interactive: bool) -> Dict[str, Any]:
        """Process seed folders and auto-archive unknown items."""
        from .spoke_update import SpokeUpdateProcessor

        updater = SpokeUpdateProcessor(self.spoke_dir)
        plan = updater.plan_update()

        ingest_count = len(plan.get("ingest_files", []))
        ref_count = len(plan.get("reference_files", []))
        unknown_count = len(plan.get("unknown_items", []))

        if interactive and (ingest_count or ref_count or unknown_count):
            print_info(f"    Seed ingest: {ingest_count} file(s)")
            print_info(f"    Seed reference: {ref_count} file(s)")
            print_info(f"    Unknown items: {unknown_count}")
            print_info("    Running update to ingest and archive.")

        results = updater.run_update()
        summary_parts = []
        if results["ingested"]:
            summary_parts.append(f"ingested {len(results['ingested'])}")
            if interactive and results.get("ingest_notes"):
                print_info("    Ingested files:")
                for note in results["ingest_notes"]:
                    targets = ", ".join(note.get("applied_to", []))
                    preview = note.get("preview", "")
                    print_info(f"      - {note.get('file')} [DEFER] {targets}")
                    if preview:
                        print_info(f"        preview: {preview}")
        if results["archived_reference"]:
            summary_parts.append(f"archived {len(results['archived_reference'])} reference")
        if results["archived_unknown"]:
            summary_parts.append(f"archived {len(results['archived_unknown'])} unknown")

        summary = "Seed/update: " + (", ".join(summary_parts) if summary_parts else "no changes")
        return {
            "summary": summary,
            "warnings": results.get("warnings", [])
        }

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

        return True

    def _extract_signals(self) -> int:
        """Extract high-impact signals from session log."""
        signals = self.session.extract_high_impact_signals()

        if not signals:
            return 0

        # Append signals to WAI-Signals.jsonl
        signals_file = self.wai_spoke_dir / 'WAI-Signals.jsonl'
        with open(signals_file, 'a') as f:
            for signal in signals:
                f.write(json.dumps(signal) + '\n')

        return len(signals)

    def _record_analytics(self, session_summary: Dict[str, Any]) -> None:
        """Record session analytics."""
        session_data = {
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

        # Record session bead (Phase 0)
        try:
            parent_bead_id = None
            # Ideally we'd track the actual bead hash, but for now we link to the previous session_id
            # In a full implementation, state would track 'last_bead_id'
            if state.get('_session_state', {}).get('last_closeout'):
                 # Use the session_id as a proxy for the bead chain parent if real bead tracking isn't in state yet
                 parent_bead_id = state['_session_state']['last_closeout'].get('session_id')

            self.lug_manager.record_session_bead(
                session_id=current_session.get('session_id', 'unknown'),
                summary=session_summary.get('summary', 'Session complete'),
                parent_id=parent_bead_id,
                files_modified=session_summary.get('files_modified', [])
            )
            print_info("    recorded session bead")
        except Exception as e:
            print_warning(f"Failed to record session bead: {e}")

        # Clear conversation log
        self.session.clear_log()

        # Auto-commit WAI-State files
        self._auto_commit_state_files()

    def _auto_commit_state_files(self) -> None:
        """Auto-commit all modified files from closeout process."""
        try:
            # Stage all modified files (not just state)
            state_files = [
                'WAI-Spoke/WAI-State.json',
                'WAI-Spoke/WAI-State.md',
                'WAI-Spoke/WAI-Lugs.jsonl',
                'WAI-Spoke/WAI-Point.json',
                'WAI-Spoke/WAI-Guide.md',
                'AGENTS.md',
                '.claude/settings.json'
            ]
            
            for file_path in state_files:
                full_path = self.spoke_dir / file_path
                if full_path.exists():
                    subprocess.run(
                        ['git', 'add', str(full_path)],
                        cwd=str(self.spoke_dir),
                        capture_output=True,
                        check=False
                    )
            
            # Check if there are changes to commit
            result = subprocess.run(
                ['git', 'diff', '--cached', '--quiet'],
                cwd=str(self.spoke_dir),
                capture_output=True
            )
            
            if result.returncode != 0:  # There are staged changes
                subprocess.run(
                    ['git', 'commit', '-m', 'wai: closeout - update session state'],
                    cwd=str(self.spoke_dir),
                    capture_output=True,
                    check=False
                )
                print_success("    [OK] WAI-State files committed to git")
        except Exception as e:
            print_warning(f"    [WARN] Could not auto-commit state files: {e}")

    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print closeout summary."""
        print_info("\n" + "=" * 60)
        print_success("  [OK] Session Closeout Summary")
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
            print_success(f"    [OK] {step}")

        if results['warnings']:
            print_info("\n  Warnings:")
            for warning in results['warnings']:
                print_warning(f"    [WARN] {warning}")

        if results['errors']:
            print_info("\n  Errors:")
            for error in results['errors']:
                print_error(f"    [ERROR] {error}")

        print_info("\n" + "=" * 60)
        print_info("  WAI-Spoke/ folder ready for hub learning")

        integration_status = results.get('integration_status')
        if integration_status:
            print_info("  Integrations verified and refreshed")
            updated = integration_status.get('updated', 0)
            print_info(f"  Integration files updated: {updated}")

            statuses = integration_status.get('statuses', {})
            if statuses:
                print_info("  Integration status:")
    def _update_website_content(self, session_summary: Dict[str, Any]) -> bool:
        """
        Update website content file with session changes (if file exists).
        
        [REFACTORED] Added as closeout rule - updates WAI-Website-Content.md
        with latest project state, features, and updates from session.
        
        Returns:
            True if website content was updated
        """
        # Check for website content file
        website_file = self.wai_spoke_dir / 'WAI-Website-Content.md'
        if not website_file.exists():
            return False
        
        try:
            content = website_file.read_text()
            
            # Add session summary to "Recent Updates" section
            update_entry = f"\n### {datetime.now().strftime('%Y-%m-%d')}\n"
            update_entry += f"{session_summary.get('summary', 'Session update')}\n"
            
            # Check if "Recent Updates" section exists
            if "## Recent Updates" in content:
                # Insert at beginning of Recent Updates section
                parts = content.split("## Recent Updates")
                content = parts[0] + "## Recent Updates\n" + update_entry + parts[1]
            else:
                # Add section at end
                content += "\n\n## Recent Updates\n" + update_entry
            
            # Write updated content
            website_file.write_text(content)
            return True
            
        except Exception:
            # Non-blocking - website update failure doesn't stop closeout
            return False

    def _refresh_integrations(self) -> Dict[str, Any]:
        """Refresh integration files and optionally re-brief active session."""
        manager = IDEManager(self.spoke_dir)
        updated = 0
        statuses = {}

        for ide in manager.all_integrations:
            config_path = ide.config_file_path
            generated = ide.generate_config()
            current = config_path.read_text() if config_path.exists() else None

            if current != generated:
                ide.write_config(generated)
                updated += 1
                statuses[ide.name] = "updated"
            else:
                statuses[ide.name] = "up_to_date"

        # Refresh AGENTS.md with latest state (IDE context discovery)
        agents = AgentsIntegration(self.spoke_dir)
        agents_refreshed = agents.refresh_agents_md()
        if agents_refreshed:
            updated += 1
            statuses['AGENTS.md'] = 'updated'
            print_info("    [OK] AGENTS.md refreshed - next session will load with fresh context")
        else:
            if (self.spoke_dir / 'AGENTS.md').exists():
                statuses['AGENTS.md'] = 'up_to_date'

        session_refreshed = False
        hook_output = ""
        hook_path = self.spoke_dir / "WAI-Spoke" / "hooks" / "session-start.sh"
        if hook_path.exists():
            try:
                env = os.environ.copy()
                env["WAI_PROJECT_DIR"] = str(self.spoke_dir)
                result = subprocess.run(
                    [str(hook_path)],
                    cwd=self.spoke_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                hook_output = (result.stdout or "").strip()
                session_refreshed = True
            except (OSError, subprocess.TimeoutExpired) as e:
                # On Windows or if bash not available, skip hook execution
                print_warning(f"    Skipped hook execution (bash not available): {type(e).__name__}")

        return {
            "updated": updated,
            "statuses": statuses,
            "session_refreshed": session_refreshed,
            "briefing_emitted": bool(hook_output)
        }


def generate_closeout() -> None:
     """Generate session closeout (legacy function for backward compatibility)."""
     print_warning("\n[WARN] Using legacy closeout stub.")
     print_info("Use CloseoutProcessor for full functionality.\n")

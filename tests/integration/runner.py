#!/usr/bin/env python3
"""
Integration Test Runner for Wheelwright Framework.

Orchestrates test execution, baseline comparisons, and reporting.
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import argparse


class IntegrationTestRunner:
    """Orchestrates integration test execution and reporting."""

    def __init__(self, framework_path: Optional[Path] = None):
        """
        Initialize test runner.

        Args:
            framework_path: Path to framework root (auto-detected if None)
        """
        if framework_path is None:
            self.framework_path = Path(__file__).parent.parent.parent.absolute()
        else:
            self.framework_path = Path(framework_path)

        self.scenarios_dir = self.framework_path / "tests" / "integration" / "scenarios"
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "framework_path": str(self.framework_path),
            "phases": {},
            "summary": {}
        }

    def discover_tests(self) -> Dict[str, List[Path]]:
        """
        Discover all test files organized by phase.

        Returns:
            Dict mapping phase names to test file paths
        """
        phases = {
            "Phase 1: Infrastructure": [],
            "Phase 2: Basic Scenarios": [],
            "Phase 3: Core Features": [],
            "Phase 4: Hub-Spoke": [],
            "Phase 5: Analytics & Baseline": []
        }

        # Phase 1
        infra_test = self.framework_path / "tests" / "integration" / "test_phase1_infrastructure.py"
        if infra_test.exists():
            phases["Phase 1: Infrastructure"].append(infra_test)

        # Phase 2: Basic scenarios
        phase2_tests = [
            "test_onboarding.py",
            "test_menus.py",
            "test_spoke_init.py"
        ]
        for test_name in phase2_tests:
            test_path = self.scenarios_dir / test_name
            if test_path.exists():
                phases["Phase 2: Basic Scenarios"].append(test_path)

        # Phase 3: Core features
        phase3_tests = [
            "test_session_continuity.py",
            "test_closeout.py",
            "test_shipit.py",
            "test_quality_gates.py"
        ]
        for test_name in phase3_tests:
            test_path = self.scenarios_dir / test_name
            if test_path.exists():
                phases["Phase 3: Core Features"].append(test_path)

        # Phase 4: Hub-spoke
        phase4_tests = [
            "test_spoke_signals.py",
            "test_hub_learning.py",
            "test_knowledge_sharing.py"
        ]
        for test_name in phase4_tests:
            test_path = self.scenarios_dir / test_name
            if test_path.exists():
                phases["Phase 4: Hub-Spoke"].append(test_path)

        # Phase 5: Analytics & baseline
        phase5_tests = [
            "test_baseline_mode.py",
            "test_analytics.py",
            "test_token_efficiency.py"
        ]
        for test_name in phase5_tests:
            test_path = self.scenarios_dir / test_name
            if test_path.exists():
                phases["Phase 5: Analytics & Baseline"].append(test_path)

        return phases

    def run_phase(self, phase_name: str, test_files: List[Path], verbose: bool = False) -> Dict[str, Any]:
        """
        Run all tests in a phase.

        Args:
            phase_name: Name of the phase
            test_files: List of test file paths
            verbose: Show verbose output

        Returns:
            Phase results dict
        """
        if not test_files:
            return {
                "name": phase_name,
                "status": "skipped",
                "reason": "No test files found"
            }

        print(f"\n{'='*70}")
        print(f"  {phase_name}")
        print(f"{'='*70}")

        cmd = [
            sys.executable, "-m", "pytest",
            *[str(f) for f in test_files],
            "-v" if verbose else "-q",
            "-s",  # Don't capture stdout (allow prints)
            "--timeout=60",
            "--tb=short"
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.framework_path),
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse pytest output - look for summary line
            import re
            output = result.stdout + result.stderr
            passed = failed = skipped = 0

            # Look for patterns like "8 passed in 0.32s" or "10 passed, 2 failed in 1.5s"
            summary_match = re.search(r'(\d+)\s+passed', output)
            if summary_match:
                passed = int(summary_match.group(1))

            failed_match = re.search(r'(\d+)\s+failed', output)
            if failed_match:
                failed = int(failed_match.group(1))

            skipped_match = re.search(r'(\d+)\s+skipped', output)
            if skipped_match:
                skipped = int(skipped_match.group(1))

            status = "passed" if result.returncode == 0 else "failed"

            return {
                "name": phase_name,
                "status": status,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "total": passed + failed + skipped,
                "duration": "N/A",  # Could parse from output
                "output": result.stdout if verbose else ""
            }

        except subprocess.TimeoutExpired:
            return {
                "name": phase_name,
                "status": "timeout",
                "error": "Phase timed out after 300 seconds"
            }
        except Exception as e:
            return {
                "name": phase_name,
                "status": "error",
                "error": str(e)
            }

    def run_all_phases(self, verbose: bool = False, stop_on_failure: bool = False) -> Dict[str, Any]:
        """
        Run all test phases in sequence.

        Args:
            verbose: Show verbose output
            stop_on_failure: Stop if any phase fails

        Returns:
            Complete results dict
        """
        print("\n" + "="*70)
        print("  Wheelwright Integration Test Suite")
        print("="*70)
        print(f"  Framework: {self.framework_path}")
        print(f"  Timestamp: {self.results['timestamp']}")
        print("="*70)

        phases = self.discover_tests()
        total_passed = total_failed = total_skipped = 0

        for phase_name, test_files in phases.items():
            phase_result = self.run_phase(phase_name, test_files, verbose)
            self.results["phases"][phase_name] = phase_result

            if phase_result.get("status") == "passed":
                total_passed += phase_result.get("passed", 0)
                total_skipped += phase_result.get("skipped", 0)
            elif phase_result.get("status") == "failed":
                total_passed += phase_result.get("passed", 0)
                total_failed += phase_result.get("failed", 0)
                total_skipped += phase_result.get("skipped", 0)

                if stop_on_failure:
                    print(f"\n❌ Phase failed: {phase_name}")
                    print("   Stopping execution (--stop-on-failure)")
                    break

        # Generate summary
        self.results["summary"] = {
            "total_tests": total_passed + total_failed + total_skipped,
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
            "pass_rate": round((total_passed / (total_passed + total_failed) * 100), 2) if (total_passed + total_failed) > 0 else 0
        }

        return self.results

    def run_baseline_comparison(self, verbose: bool = False) -> Dict[str, Any]:
        """
        Run baseline comparison: tests with features OFF vs ON.

        Returns:
            Comparison results dict
        """
        print("\n" + "="*70)
        print("  Baseline Comparison Mode")
        print("="*70)
        print("  Running comparative simulations (Baseline vs Optimized)...")

        # Run Phase 5 tests which contain the comparison logic
        baseline_tests = [
            self.scenarios_dir / "test_baseline_mode.py"
        ]

        # The test_baseline_mode.py script itself runs both baseline and optimized 
        # scenarios and asserts the savings. We capture its output to show the user.
        result = self.run_phase(
            "Comparative Simulation",
            baseline_tests,
            verbose=True # Force verbose to see the assertions/print statements if any
        )

        comparison = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "test_results": result,
            "summary": "Executed comparative simulations."
        }
        
        # Print the detailed output (which contains the comparative table)
        if result.get('output'):
            print("\n" + result['output'])
            
        return comparison

    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """
        Generate test report.

        Args:
            output_file: Optional file to write report to

        Returns:
            Report as string
        """
        report_lines = [
            "",
            "="*70,
            "  WHEELWRIGHT INTEGRATION TEST REPORT",
            "="*70,
            f"  Timestamp: {self.results['timestamp']}",
            f"  Framework: {self.results['framework_path']}",
            "="*70,
            ""
        ]

        # Phase results
        for phase_name, phase_data in self.results["phases"].items():
            status_symbol = "✅" if phase_data.get("status") == "passed" else "❌"
            report_lines.append(f"{status_symbol} {phase_name}")

            if phase_data.get("status") in ["passed", "failed"]:
                report_lines.append(
                    f"   Passed: {phase_data.get('passed', 0)} | "
                    f"Failed: {phase_data.get('failed', 0)} | "
                    f"Skipped: {phase_data.get('skipped', 0)}"
                )
            else:
                report_lines.append(f"   Status: {phase_data.get('status')}")

            report_lines.append("")

        # Summary
        summary = self.results.get("summary", {})
        report_lines.extend([
            "="*70,
            "  SUMMARY",
            "="*70,
            f"  Total Tests: {summary.get('total_tests', 0)}",
            f"  ✅ Passed: {summary.get('passed', 0)}",
            f"  ❌ Failed: {summary.get('failed', 0)}",
            f"  ⏭️  Skipped: {summary.get('skipped', 0)}",
            f"  Pass Rate: {summary.get('pass_rate', 0)}%",
            "="*70,
            ""
        ])

        report = "\n".join(report_lines)

        if output_file:
            output_file.write_text(report)
            print(f"\n📄 Report written to: {output_file}")

        return report

    def save_json_results(self, output_file: Path) -> None:
        """
        Save results as JSON.

        Args:
            output_file: Path to JSON file
        """
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"📊 JSON results saved to: {output_file}")


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="Wheelwright Integration Test Runner"
    )
    parser.add_argument(
        "--mode",
        choices=["all", "baseline-comparison", "phase"],
        default="all",
        help="Test execution mode"
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Run specific phase only (requires --mode=phase)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Stop on first phase failure"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output report file"
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Output JSON results file"
    )

    args = parser.parse_args()

    runner = IntegrationTestRunner()

    try:
        if args.mode == "baseline-comparison":
            results = runner.run_baseline_comparison(verbose=args.verbose)
            print(json.dumps(results, indent=2))

        elif args.mode == "phase" and args.phase:
            phases = runner.discover_tests()
            phase_names = list(phases.keys())
            target_phase = phase_names[args.phase - 1]
            test_files = phases[target_phase]

            phase_result = runner.run_phase(target_phase, test_files, args.verbose)
            print(f"\n{target_phase}: {phase_result['status']}")

        else:  # mode == "all"
            runner.run_all_phases(
                verbose=args.verbose,
                stop_on_failure=args.stop_on_failure
            )

            # Generate report
            report = runner.generate_report(output_file=args.output)
            print(report)

            # Save JSON if requested
            if args.json:
                runner.save_json_results(args.json)

            # Exit with appropriate code
            summary = runner.results.get("summary", {})
            if summary.get("failed", 0) > 0:
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

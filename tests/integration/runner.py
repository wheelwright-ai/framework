#!/usr/bin/env python3
"""
WAI Integration Test Report Generator

Reads results.json produced by run-integration-tests.sh and writes
a human-readable text report. Falls back to running the e2e suite
directly if results.json is not present.

Usage:
    python3 tests/integration/runner.py --mode=all --output=report.txt
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_tests_directly() -> tuple[str, dict]:
    """Run benchmarks/e2e/test_skills.py and return (output, summary)."""
    result = subprocess.run(
        [sys.executable, "benchmarks/e2e/test_skills.py"],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr

    # Parse summary line
    total = passed = failed = 0
    for line in output.splitlines():
        if "Total:" in line and "Passed:" in line and "Failed:" in line:
            import re
            m = re.search(r"Total:\s*(\d+).*Passed:\s*(\d+).*Failed:\s*(\d+)", line)
            if m:
                total, passed, failed = int(m.group(1)), int(m.group(2)), int(m.group(3))

    summary = {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "skipped": 0,
    }
    return output, summary


def main():
    parser = argparse.ArgumentParser(description="WAI integration test report generator")
    parser.add_argument("--mode", default="all", help="Test mode")
    parser.add_argument("--output", default="report.txt", help="Output file path")
    args = parser.parse_args()

    results_file = Path("results.json")
    if results_file.exists():
        with open(results_file) as f:
            data = json.load(f)
        output = data.get("output", "")
        summary = data.get("summary", {})
    else:
        output, summary = run_tests_directly()

    total   = summary.get("total_tests", 0)
    passed  = summary.get("passed", 0)
    failed  = summary.get("failed", 0)
    skipped = summary.get("skipped", 0)
    status  = "PASS" if failed == 0 else "FAIL"

    report_lines = [
        "WAI Integration Test Report",
        "=" * 60,
        f"Mode:    {args.mode}",
        f"Status:  {status}",
        "",
        "Summary:",
        f"  Total:   {total}",
        f"  Passed:  {passed}",
        f"  Failed:  {failed}",
        f"  Skipped: {skipped}",
        "",
        "Output:",
        "-" * 60,
        output,
    ]

    report = "\n".join(report_lines)
    Path(args.output).write_text(report)
    print(f"Report written to {args.output}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

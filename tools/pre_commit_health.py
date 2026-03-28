#!/usr/bin/env python3
"""
Pre-commit health gate for WAI spokes.

Runs a quick health check and exits non-zero if critical drift is detected.
Designed to be fast (<100ms) and catch only FAIL-level findings.

Usage:
  python3 tools/pre_commit_health.py          # check current dir
  python3 tools/pre_commit_health.py /path     # check specific spoke

Exit codes:
  0 = healthy (or no WAI-Spoke found — not a WAI project)
  1 = drift detected — fix before committing
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.spoke_health_check import run_health_check


def main():
    spoke_path = sys.argv[1] if len(sys.argv) > 1 else "."

    # Skip silently if not a WAI project
    wai_spoke = Path(spoke_path) / "WAI-Spoke"
    if not wai_spoke.exists():
        sys.exit(0)

    report = run_health_check(spoke_path, mode="quick")

    if report.failed > 0:
        print(f"WAI pre-commit: {report.failed} issue(s) found")
        for c in report.checks:
            if c.status == "FAIL":
                print(f"  FAIL: {c.id} — {c.detail}")
        print("Fix these before committing. Run: python3 tools/spoke_health_check.py . --quick")
        sys.exit(1)

    # Healthy — exit silently for clean pre-commit experience
    sys.exit(0)


if __name__ == "__main__":
    main()

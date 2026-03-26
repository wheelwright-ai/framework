#!/usr/bin/env bash
# WAI Framework — integration test runner
# Wraps benchmarks/e2e/test_skills.py and outputs structured JSON results.
set -euo pipefail

MODE="all"
JSON_OUT=""

for arg in "$@"; do
    case "$arg" in
        --mode=*)  MODE="${arg#--mode=}" ;;
        --json=*)  JSON_OUT="${arg#--json=}" ;;
    esac
done

echo "WAI Integration Tests — mode: $MODE"
echo "======================================"

TMPOUT=$(mktemp)
trap 'rm -f "$TMPOUT"' EXIT

# Run the e2e test suite
set +e
python3 benchmarks/e2e/test_skills.py 2>&1 | tee "$TMPOUT"
EXIT_CODE=${PIPESTATUS[0]}
set -e

# Parse summary line: "Total: N | Passed: N | Failed: N | Nms"
TOTAL=$(grep -oP 'Total: \K[0-9]+' "$TMPOUT" | tail -1 || echo "0")
PASSED=$(grep -oP 'Passed: \K[0-9]+' "$TMPOUT" | tail -1 || echo "0")
FAILED=$(grep -oP 'Failed: \K[0-9]+' "$TMPOUT" | tail -1 || echo "0")

if [ -n "$JSON_OUT" ]; then
    python3 - <<PYEOF
import json

with open("$TMPOUT") as f:
    output = f.read()

total   = int("$TOTAL")  if "$TOTAL"  else 0
passed  = int("$PASSED") if "$PASSED" else 0
failed  = int("$FAILED") if "$FAILED" else 0

data = {
    "mode": "$MODE",
    "summary": {
        "total_tests": total,
        "passed":      passed,
        "failed":      failed,
        "skipped":     0,
    },
    # baseline-comparison job looks for comparison_summary
    "comparison_summary": {
        "baseline_tests_passed": passed,
        "conclusion": "PASS" if failed == 0 else "FAIL",
    },
    "output": output,
}

with open("$JSON_OUT", "w") as f:
    json.dump(data, f, indent=2)

print(f"Results written to $JSON_OUT  (total={total}, passed={passed}, failed={failed})")
PYEOF
fi

exit $EXIT_CODE

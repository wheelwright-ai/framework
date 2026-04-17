#!/usr/bin/env bash
# WAI Framework — integration test runner
# Runs the stable public integration suite and outputs structured JSON results.
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

# Run the public integration suite
set +e
python3 -m pytest \
  tests/behavioral/test_public_reorg_structure.py \
  tests/behavioral/test_spoke_structure.py \
  tests/behavioral/test_tool_advisor.py \
  tests/behavioral/test_teaching_adoption.py \
  -q 2>&1 | tee "$TMPOUT"
EXIT_CODE=${PIPESTATUS[0]}
set -e

# Parse pytest summary line
PASSED=$(python3 - <<PYEOF
import re
from pathlib import Path
text = Path("$TMPOUT").read_text()
m = re.search(r"(\d+)\s+passed", text)
print(m.group(1) if m else "0")
PYEOF
)
FAILED=$(python3 - <<PYEOF
import re
from pathlib import Path
text = Path("$TMPOUT").read_text()
m = re.search(r"(\d+)\s+failed", text)
print(m.group(1) if m else "0")
PYEOF
)
SKIPPED=$(python3 - <<PYEOF
import re
from pathlib import Path
text = Path("$TMPOUT").read_text()
m = re.search(r"(\d+)\s+skipped", text)
print(m.group(1) if m else "0")
PYEOF
)
TOTAL=$((PASSED + FAILED + SKIPPED))

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
        "skipped":     int("$SKIPPED") if "$SKIPPED" else 0,
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

#!/bin/bash
# Smoke tests for Phase 1 & 2 features
# Session infrastructure, closeout, analytics, metrics

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
TOTAL=0

pass() {
    PASSED=$((PASSED + 1))
    TOTAL=$((TOTAL + 1))
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    FAILED=$((FAILED + 1))
    TOTAL=$((TOTAL + 1))
    echo -e "${RED}✗${NC} $1"
}

info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Setup test environment
setup_test_env() {
    TEST_DIR=$(mktemp -d)
    cd "$TEST_DIR"

    # Initialize a test spoke
    "$SCRIPT_DIR/WAI-CLI" init "$TEST_DIR" >/dev/null 2>&1

    echo "$TEST_DIR"
}

cleanup_test_env() {
    local test_dir=$1
    rm -rf "$test_dir"
}

echo "=========================================="
echo "Phase 1 & 2 Smoke Tests"
echo "=========================================="
echo ""

# Test 1: Module imports
info "Testing module imports..."

if python3 -c "from wai_cli.session import SessionManager" 2>/dev/null; then
    pass "SessionManager imports"
else
    fail "SessionManager imports"
fi

if python3 -c "from wai_cli.rebalancer import FileRebalancer" 2>/dev/null; then
    pass "FileRebalancer imports"
else
    fail "FileRebalancer imports"
fi

if python3 -c "from wai_cli.metrics import MetricsTracker" 2>/dev/null; then
    pass "MetricsTracker imports"
else
    fail "MetricsTracker imports"
fi

if python3 -c "from wai_cli.closeout import CloseoutProcessor" 2>/dev/null; then
    pass "CloseoutProcessor imports"
else
    fail "CloseoutProcessor imports"
fi

echo ""
info "Testing CLI commands availability..."

# Test 2: Stats command exists
if ./WAI-CLI stats --help >/dev/null 2>&1; then
    pass "stats command available"
else
    fail "stats command available"
fi

# Test 3: Baseline command exists
if ./WAI-CLI baseline --help >/dev/null 2>&1; then
    pass "baseline command available"
else
    fail "baseline command available"
fi

# Test 4: Closeout command exists
if ./WAI-CLI closeout --help >/dev/null 2>&1; then
    pass "closeout command available"
else
    fail "closeout command available"
fi

echo ""
info "Testing analytics schema in templates..."

# Test 5: Analytics in template
if grep -q '"analytics"' templates/WAI/WAI-State.json; then
    pass "Analytics schema in template"
else
    fail "Analytics schema in template"
fi

# Test 6: Analytics structure
if grep -q '"sessions"' templates/WAI/WAI-State.json && \
   grep -q '"token_efficiency"' templates/WAI/WAI-State.json && \
   grep -q '"time_tracking"' templates/WAI/WAI-State.json && \
   grep -q '"baseline_mode"' templates/WAI/WAI-State.json; then
    pass "Analytics schema complete"
else
    fail "Analytics schema complete"
fi

echo ""
info "Testing with test spoke..."

# Create test environment
TEST_DIR=$(setup_test_env)

# Test 7: Stats command on new spoke
if ./WAI-CLI stats "$TEST_DIR" 2>&1 | grep -q "Session Analytics"; then
    pass "Stats command runs on spoke"
else
    fail "Stats command runs on spoke"
fi

# Test 8: Stats shows zero sessions initially
if ./WAI-CLI stats "$TEST_DIR" 2>&1 | grep -q "Total: 0"; then
    pass "Stats shows zero sessions initially"
else
    fail "Stats shows zero sessions initially"
fi

# Test 9: Baseline status command
if ./WAI-CLI baseline status "$TEST_DIR" 2>&1 | grep -q "Baseline Mode Status"; then
    pass "Baseline status command works"
else
    fail "Baseline status command works"
fi

# Test 10: Baseline initially disabled
if ./WAI-CLI baseline status "$TEST_DIR" 2>&1 | grep -q "DISABLED"; then
    pass "Baseline initially disabled"
else
    fail "Baseline initially disabled"
fi

# Test 11: Enable baseline mode
if ./WAI-CLI baseline enable "$TEST_DIR" 2>&1 | grep -q "enabled"; then
    pass "Baseline enable works"
else
    fail "Baseline enable works"
fi

# Test 12: Baseline status shows enabled
if ./WAI-CLI baseline status "$TEST_DIR" 2>&1 | grep -q "ENABLED"; then
    pass "Baseline status shows enabled"
else
    fail "Baseline status shows enabled"
fi

# Test 13: Disable baseline mode
if ./WAI-CLI baseline disable "$TEST_DIR" 2>&1 | grep -q "disabled"; then
    pass "Baseline disable works"
else
    fail "Baseline disable works"
fi

# Test 14: Baseline status shows disabled after disable
if ./WAI-CLI baseline status "$TEST_DIR" 2>&1 | grep -q "DISABLED"; then
    pass "Baseline status shows disabled after disable"
else
    fail "Baseline status shows disabled after disable"
fi

echo ""
info "Testing session infrastructure..."

# Test 15: SessionManager initialization
TEST_RESULT=$(python3 <<EOF
from wai_cli.session import SessionManager
from pathlib import Path
import sys

try:
    sm = SessionManager(Path("$TEST_DIR"))
    print("PASS" if sm.spoke_dir.exists() else "FAIL")
except Exception as e:
    print(f"FAIL: {e}")
EOF
)

if [ "$TEST_RESULT" = "PASS" ]; then
    pass "SessionManager initializes"
else
    fail "SessionManager initializes"
fi

# Test 16: Session ID generation
TEST_RESULT=$(python3 <<EOF
from wai_cli.session import SessionManager
from pathlib import Path

try:
    sm = SessionManager(Path("$TEST_DIR"))
    session_id = sm._generate_session_id()
    print("PASS" if len(session_id) == 12 else "FAIL")
except Exception as e:
    print("FAIL")
EOF
)

if [ "$TEST_RESULT" = "PASS" ]; then
    pass "Session ID generation works"
else
    fail "Session ID generation works"
fi

# Test 17: Token estimation
TEST_RESULT=$(python3 <<EOF
from wai_cli.session import SessionManager
from pathlib import Path

try:
    sm = SessionManager(Path("$TEST_DIR"))
    capacity = sm.get_capacity_estimate()
    print("PASS" if 'tokens_used' in capacity else "FAIL")
except Exception as e:
    print("FAIL")
EOF
)

if [ "$TEST_RESULT" = "PASS" ]; then
    pass "Token capacity estimation works"
else
    fail "Token capacity estimation works"
fi

echo ""
info "Testing file rebalancer..."

# Test 18: FileRebalancer initialization
TEST_RESULT=$(python3 <<EOF
from wai_cli.rebalancer import FileRebalancer
from pathlib import Path

try:
    wai_spoke_dir = Path("$TEST_DIR") / 'WAI-Spoke'
    rb = FileRebalancer(wai_spoke_dir)
    print("PASS")
except Exception as e:
    print("FAIL")
EOF
)

if [ "$TEST_RESULT" = "PASS" ]; then
    pass "FileRebalancer initializes"
else
    fail "FileRebalancer initializes"
fi

# Test 19: Balance check
TEST_RESULT=$(python3 <<EOF
from wai_cli.rebalancer import FileRebalancer
from pathlib import Path

try:
    wai_spoke_dir = Path("$TEST_DIR") / 'WAI-Spoke'
    rb = FileRebalancer(wai_spoke_dir)
    result = rb.check_balance()
    print("PASS" if 'json' in result and 'md' in result else "FAIL")
except Exception as e:
    print("FAIL")
EOF
)

if [ "$TEST_RESULT" = "PASS" ]; then
    pass "Balance check works"
else
    fail "Balance check works"
fi

# Test 20: Scan unknown files
TEST_RESULT=$(python3 <<EOF
from wai_cli.rebalancer import FileRebalancer
from pathlib import Path

try:
    wai_spoke_dir = Path("$TEST_DIR") / 'WAI-Spoke'
    rb = FileRebalancer(wai_spoke_dir)
    unknown = rb.scan_unknown_files()
    print("PASS" if isinstance(unknown, list) else "FAIL")
except Exception as e:
    print("FAIL")
EOF
)

if [ "$TEST_RESULT" = "PASS" ]; then
    pass "Scan unknown files works"
else
    fail "Scan unknown files works"
fi

echo ""
info "Testing metrics tracker..."

# Test 21: MetricsTracker initialization
TEST_RESULT=$(python3 <<EOF
from wai_cli.metrics import MetricsTracker
from pathlib import Path

try:
    wai_spoke_dir = Path("$TEST_DIR") / 'WAI-Spoke'
    mt = MetricsTracker(wai_spoke_dir)
    print("PASS")
except Exception as e:
    print("FAIL")
EOF
)

if [ "$TEST_RESULT" = "PASS" ]; then
    pass "MetricsTracker initializes"
else
    fail "MetricsTracker initializes"
fi

# Test 22: Get session stats
TEST_RESULT=$(python3 <<EOF
from wai_cli.metrics import MetricsTracker
from pathlib import Path

try:
    wai_spoke_dir = Path("$TEST_DIR") / 'WAI-Spoke'
    mt = MetricsTracker(wai_spoke_dir)
    stats = mt.get_session_stats()
    print("PASS" if 'sessions' in stats and 'tokens' in stats else "FAIL")
except Exception as e:
    print("FAIL")
EOF
)

if [ "$TEST_RESULT" = "PASS" ]; then
    pass "Get session stats works"
else
    fail "Get session stats works"
fi

# Test 23: Token savings calculation
TEST_RESULT=$(python3 <<EOF
from wai_cli.metrics import MetricsTracker
from pathlib import Path

try:
    wai_spoke_dir = Path("$TEST_DIR") / 'WAI-Spoke'
    mt = MetricsTracker(wai_spoke_dir)
    savings = mt.calculate_token_savings()
    print("PASS" if 'has_baseline' in savings else "FAIL")
except Exception as e:
    print("FAIL")
EOF
)

if [ "$TEST_RESULT" = "PASS" ]; then
    pass "Token savings calculation works"
else
    fail "Token savings calculation works"
fi

# Test 24: Enable/disable baseline via API
TEST_RESULT=$(python3 <<EOF
from wai_cli.metrics import MetricsTracker
from pathlib import Path
import json

try:
    wai_spoke_dir = Path("$TEST_DIR") / 'WAI-Spoke'
    mt = MetricsTracker(wai_spoke_dir)

    # Enable
    result = mt.enable_baseline_mode()
    if not result.get('enabled'):
        print("FAIL: enable")
        exit(1)

    # Check state
    with open(wai_spoke_dir / 'WAI-State.json') as f:
        state = json.load(f)
    if not state['analytics']['baseline_mode']['enabled']:
        print("FAIL: state not updated")
        exit(1)

    # Disable
    result = mt.disable_baseline_mode()
    if not result.get('disabled'):
        print("FAIL: disable")
        exit(1)

    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")
EOF
)

if [ "$TEST_RESULT" = "PASS" ]; then
    pass "Baseline enable/disable API works"
else
    fail "Baseline enable/disable API works"
fi

echo ""
info "Testing closeout processor..."

# Test 25: CloseoutProcessor initialization
TEST_RESULT=$(python3 <<EOF
from wai_cli.closeout import CloseoutProcessor
from pathlib import Path

try:
    cp = CloseoutProcessor(Path("$TEST_DIR"))
    print("PASS")
except Exception as e:
    print("FAIL")
EOF
)

if [ "$TEST_RESULT" = "PASS" ]; then
    pass "CloseoutProcessor initializes"
else
    fail "CloseoutProcessor initializes"
fi

# Test 26: Closeout with no session data
TEST_RESULT=$(python3 <<EOF 2>/dev/null
from wai_cli.closeout import CloseoutProcessor
from pathlib import Path
import sys

try:
    cp = CloseoutProcessor(Path("$TEST_DIR"))
    results = cp.process_closeout(interactive=False)
    print("PASS" if 'steps_completed' in results else "FAIL")
    sys.exit(0)
except Exception as e:
    print(f"FAIL")
    sys.exit(1)
EOF
)

if echo "$TEST_RESULT" | grep -q "PASS"; then
    pass "Closeout processes (no session data)"
else
    fail "Closeout processes (no session data)"
fi

# Test 27: Closeout creates proper summary
TEST_RESULT=$(python3 <<EOF 2>/dev/null
from wai_cli.closeout import CloseoutProcessor
from pathlib import Path
import sys

try:
    cp = CloseoutProcessor(Path("$TEST_DIR"))
    results = cp.process_closeout(interactive=False)

    has_summary = 'session_summary' in results
    has_steps = len(results.get('steps_completed', [])) > 0

    print("PASS" if has_summary and has_steps else "FAIL")
    sys.exit(0)
except Exception as e:
    print("FAIL")
    sys.exit(1)
EOF
)

if echo "$TEST_RESULT" | grep -q "PASS"; then
    pass "Closeout creates summary"
else
    fail "Closeout creates summary"
fi

# Test 28: Unknown file detection
# Create an unknown file
touch "$TEST_DIR/WAI-Spoke/unknown-test-file.txt"

TEST_RESULT=$(python3 <<EOF
from wai_cli.rebalancer import FileRebalancer
from pathlib import Path

try:
    wai_spoke_dir = Path("$TEST_DIR") / 'WAI-Spoke'
    rb = FileRebalancer(wai_spoke_dir)
    unknown = rb.scan_unknown_files()

    has_unknown = any('unknown-test-file.txt' in str(f) for f in unknown)
    print("PASS" if has_unknown else "FAIL")
except Exception as e:
    print("FAIL")
EOF
)

if [ "$TEST_RESULT" = "PASS" ]; then
    pass "Unknown file detection works"
else
    fail "Unknown file detection works"
fi

# Test 29: Analytics schema in new spoke
if grep -q '"analytics"' "$TEST_DIR/WAI-Spoke/WAI-State.json"; then
    pass "New spoke has analytics schema"
else
    fail "New spoke has analytics schema"
fi

# Test 30: Session state structure in new spoke
if grep -q '"current_session"' "$TEST_DIR/WAI-Spoke/WAI-State.json" && \
   grep -q '"last_closeout"' "$TEST_DIR/WAI-Spoke/WAI-State.json" && \
   grep -q '"protocol_completed"' "$TEST_DIR/WAI-Spoke/WAI-State.json"; then
    pass "New spoke has session state structure"
else
    fail "New spoke has session state structure"
fi

echo ""
echo -e "${YELLOW}→${NC} Testing critical priority features..."

# Test 31: Time command works
TEST_RESULT=$(./WAI-CLI time "$TEST_DIR" 2>&1)
if echo "$TEST_RESULT" | grep -q "Token Usage Estimate" && \
   echo "$TEST_RESULT" | grep -q "Estimated usage:"; then
    pass "Time command runs on spoke"
else
    fail "Time command runs on spoke"
fi

# Test 32: Time command shows capacity info
if echo "$TEST_RESULT" | grep -q "Tokens used:" && \
   echo "$TEST_RESULT" | grep -q "Capacity:"; then
    pass "Time command shows capacity info"
else
    fail "Time command shows capacity info"
fi

# Test 33: Quality gates module imports
TEST_RESULT=$(python3 <<EOF
try:
    from wai_cli.quality_gates import QualityGates
    print("PASS")
except Exception as e:
    print("FAIL")
EOF
)

if echo "$TEST_RESULT" | grep -q "PASS"; then
    pass "QualityGates module imports"
else
    fail "QualityGates module imports"
fi

# Test 34: Quality gates integration in closeout
TEST_RESULT=$(python3 <<EOF
from wai_cli.closeout import CloseoutProcessor
from pathlib import Path
import inspect

try:
    # Check if quality_gates attribute exists
    processor = CloseoutProcessor(Path("$TEST_DIR"))
    has_quality_gates = hasattr(processor, 'quality_gates')

    # Check if process_closeout mentions quality gates
    source = inspect.getsource(processor.process_closeout)
    has_step_0 = 'Step 0' in source and 'quality gates' in source.lower()

    print("PASS" if (has_quality_gates and has_step_0) else "FAIL")
except Exception as e:
    print("FAIL")
EOF
)

if echo "$TEST_RESULT" | grep -q "PASS"; then
    pass "Quality gates integrated in closeout"
else
    fail "Quality gates integrated in closeout"
fi

# Test 35: Quality gates run_all_gates method works
TEST_RESULT=$(python3 <<EOF
from wai_cli.quality_gates import QualityGates
from pathlib import Path

try:
    gates = QualityGates(Path("$TEST_DIR"))
    result = gates.run_all_gates(skip_minor=True)

    # Check result structure
    has_structure = (
        'passed' in result and
        'gates' in result and
        'warnings' in result and
        'blockers' in result
    )

    print("PASS" if has_structure else "FAIL")
except Exception as e:
    print("FAIL")
EOF
)

if echo "$TEST_RESULT" | grep -q "PASS"; then
    pass "Quality gates run_all_gates works"
else
    fail "Quality gates run_all_gates works"
fi

# Test 36: Shipit command checks git repository
# Create a git repo in test dir
cd "$TEST_DIR"
git init > /dev/null 2>&1
git config user.name "Test User" > /dev/null 2>&1
git config user.email "test@example.com" > /dev/null 2>&1
cd - > /dev/null 2>&1

# Make a change to test shipit
echo "test" > "$TEST_DIR/test.txt"

TEST_RESULT=$(./WAI-CLI shipit "$TEST_DIR" --non-interactive 2>&1)
if echo "$TEST_RESULT" | grep -q "Shipit: Closeout + Git Commit" && \
   echo "$TEST_RESULT" | grep -q "Git Commit Workflow"; then
    pass "Shipit command runs workflow"
else
    fail "Shipit command runs workflow"
fi

# Cleanup
cleanup_test_env "$TEST_DIR"

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Total:  ${TOTAL}"
echo -e "${GREEN}Passed: ${PASSED}${NC}"
echo -e "${RED}Failed: ${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi

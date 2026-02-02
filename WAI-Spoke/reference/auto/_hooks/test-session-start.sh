#!/usr/bin/env bash
#
# Unit tests for session-start.sh hook
#
# Usage: ./test-session-start.sh
#

# Don't use set -e so tests continue even if one fails
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Get absolute path to the hook script before changing directories
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_HOOK="$SCRIPT_DIR/session-start.sh"

# Test fixtures directory
FIXTURES_DIR="/tmp/WAI-test-$$"
TEST_HOOK="$FIXTURES_DIR/session-start.sh"

# Setup test environment
setup() {
    mkdir -p "$FIXTURES_DIR/WAI-Spoke/hooks"

    # Copy the hook script to test location using absolute path
    cp "$SOURCE_HOOK" "$TEST_HOOK"
    chmod +x "$TEST_HOOK"

    # Initialize git repo for tests
    cd "$FIXTURES_DIR"
    git init -q
    git config user.email "test@example.com"
    git config user.name "Test User"
}

# Teardown test environment
teardown() {
    cd /
    rm -rf "$FIXTURES_DIR"
}

# Create a valid WAI-State.json fixture
create_state_fixture() {
    local protocol_completed="${1:-false}"
    cat > "$FIXTURES_DIR/WAI-Spoke/WAI-State.json" <<EOF
{
  "wheel": {
    "name": "Test Project",
    "version": "1.0.0"
  },
  "_session_state": {
    "last_session_id": "test-session-1",
    "last_modified_by": "Test AI",
    "last_modified_at": "2025-12-29T00:00:00Z",
    "protocol_completed": $protocol_completed,
    "session_count": 1
  },
  "context": {
    "current_phase": "Testing Phase",
    "next_actions": [
      "Test action 1",
      "Test action 2",
      "Test action 3",
      "Test action 4",
      "Test action 5",
      "Test action 6"
    ]
  },
  "decisions": [
    {
      "date": "2025-12-29",
      "decision": "High impact decision 1",
      "impact": 10
    },
    {
      "date": "2025-12-28",
      "decision": "High impact decision 2",
      "impact": 9
    },
    {
      "date": "2025-12-27",
      "decision": "Low impact decision",
      "impact": 5
    },
    {
      "date": "2025-12-26",
      "decision": "High impact decision 3",
      "impact": 8
    },
    {
      "date": "2025-12-25",
      "decision": "High impact decision 4",
      "impact": 8
    }
  ]
}
EOF
}

# Assertion helpers
assert_exit_code() {
    local expected=$1
    local actual=$2
    local test_name=$3

    ((TESTS_RUN++))

    if [ "$expected" -eq "$actual" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  Expected exit code: $expected, got: $actual"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_contains() {
    local haystack=$1
    local needle=$2
    local test_name=$3

    ((TESTS_RUN++))

    if echo "$haystack" | grep -q "$needle"; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  Expected output to contain: '$needle'"
        echo -e "  Actual output:"
        echo "$haystack" | head -20
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_not_contains() {
    local haystack=$1
    local needle=$2
    local test_name=$3

    ((TESTS_RUN++))

    if echo "$haystack" | grep -q "$needle"; then
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  Expected output NOT to contain: '$needle'"
        ((TESTS_FAILED++))
        return 1
    else
        echo -e "${GREEN}✓${NC} $test_name"
        ((TESTS_PASSED++))
        return 0
    fi
}

assert_file_contains() {
    local file=$1
    local pattern=$2
    local test_name=$3

    ((TESTS_RUN++))

    if [ ! -f "$file" ]; then
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  File not found: $file"
        ((TESTS_FAILED++))
        return 1
    fi

    if grep -q "$pattern" "$file"; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $test_name"
        echo -e "  Expected file to contain: '$pattern'"
        echo -e "  File contents:"
        cat "$file" | head -20
        ((TESTS_FAILED++))
        return 1
    fi
}

# Test cases
test_exits_when_no_state_file() {
    echo ""
    echo "Test: Exit silently when WAI-Spoke/WAI-State.json doesn't exist"

    cd "$FIXTURES_DIR"
    OUTPUT=$(CLAUDE_PROJECT_DIR="$FIXTURES_DIR" "$TEST_HOOK" 2>&1)
    EXIT_CODE=$?

    assert_exit_code 0 $EXIT_CODE "Should exit with code 0"

    # Check for empty output
    ((TESTS_RUN++))
    if [ -z "$OUTPUT" ]; then
        echo -e "${GREEN}✓${NC} Should produce no output (empty string)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} Should produce no output (empty string)"
        echo -e "  Expected empty output, got: $OUTPUT"
        ((TESTS_FAILED++))
    fi
}

test_exits_when_protocol_completed() {
    echo ""
    echo "Test: Exit early when protocol_completed is true"

    create_state_fixture "true"

    cd "$FIXTURES_DIR"
    OUTPUT=$(CLAUDE_PROJECT_DIR="$FIXTURES_DIR" "$TEST_HOOK" 2>&1)
    EXIT_CODE=$?

    assert_exit_code 0 $EXIT_CODE "Should exit with code 0"
    # Should produce no output when already completed
    if [ -z "$OUTPUT" ]; then
        echo -e "${GREEN}✓${NC} Should produce no output when protocol already completed"
        ((TESTS_PASSED++))
        ((TESTS_RUN++))
    else
        echo -e "${RED}✗${NC} Should produce no output when protocol already completed"
        echo -e "  Got output: $OUTPUT"
        ((TESTS_FAILED++))
        ((TESTS_RUN++))
    fi
}

test_generates_briefing_correctly() {
    echo ""
    echo "Test: Generate correct briefing message"

    create_state_fixture "false"

    cd "$FIXTURES_DIR"
    OUTPUT=$(CLAUDE_PROJECT_DIR="$FIXTURES_DIR" "$TEST_HOOK" 2>&1)
    EXIT_CODE=$?

    assert_exit_code 0 $EXIT_CODE "Should exit with code 0"
    assert_contains "$OUTPUT" "Wheelwright Context Loaded" "Should contain title"
    assert_contains "$OUTPUT" "Test Project" "Should contain project name"
    assert_contains "$OUTPUT" "Testing Phase" "Should contain current phase"
    assert_contains "$OUTPUT" "Test AI" "Should contain last modified by"
}

test_filters_high_impact_decisions() {
    echo ""
    echo "Test: Filter and show only high-impact decisions (>= 8)"

    create_state_fixture "false"

    cd "$FIXTURES_DIR"
    set +e
    OUTPUT=$(CLAUDE_PROJECT_DIR="$FIXTURES_DIR" "$TEST_HOOK" 2>&1)

    assert_contains "$OUTPUT" "High impact decision 1" "Should show decision with impact 10"
    assert_contains "$OUTPUT" "High impact decision 2" "Should show decision with impact 9"
    assert_contains "$OUTPUT" "High impact decision 3" "Should show decision with impact 8"
    assert_not_contains "$OUTPUT" "Low impact decision" "Should NOT show decision with impact 5"
}

test_shows_next_actions() {
    echo ""
    echo "Test: Show next actions (up to 5)"

    create_state_fixture "false"

    cd "$FIXTURES_DIR"
    set +e
    OUTPUT=$(CLAUDE_PROJECT_DIR="$FIXTURES_DIR" "$TEST_HOOK" 2>&1)

    assert_contains "$OUTPUT" "Test action 1" "Should show action 1"
    assert_contains "$OUTPUT" "Test action 5" "Should show action 5"
    assert_not_contains "$OUTPUT" "Test action 6" "Should NOT show action 6 (limit is 5)"
}

test_detects_uncommitted_changes() {
    echo ""
    echo "Test: Detect uncommitted changes"

    create_state_fixture "false"

    # Create some uncommitted files
    echo "test" > "$FIXTURES_DIR/test-file.txt"
    mkdir -p "$FIXTURES_DIR/new-dir"
    echo "test" > "$FIXTURES_DIR/new-dir/test.txt"

    cd "$FIXTURES_DIR"
    set +e
    OUTPUT=$(CLAUDE_PROJECT_DIR="$FIXTURES_DIR" "$TEST_HOOK" 2>&1)

    assert_contains "$OUTPUT" "Uncommitted Changes Detected" "Should detect uncommitted files"
    assert_contains "$OUTPUT" "test-file.txt" "Should list uncommitted files"
}

test_shows_clean_tree_message() {
    echo ""
    echo "Test: Show clean tree message when no uncommitted changes"

    create_state_fixture "false"

    cd "$FIXTURES_DIR"
    # Commit everything to have clean tree
    git add -A
    git commit -m "Initial commit" -q 2>/dev/null || true

    set +e
    OUTPUT=$(CLAUDE_PROJECT_DIR="$FIXTURES_DIR" "$TEST_HOOK" 2>&1)

    assert_contains "$OUTPUT" "Working tree clean" "Should show clean tree message"
    assert_not_contains "$OUTPUT" "Uncommitted Changes Detected" "Should NOT show uncommitted warning"
}

test_updates_session_state() {
    echo ""
    echo "Test: Update session state with protocol completion"

    create_state_fixture "false"

    cd "$FIXTURES_DIR"
    set +e
    CLAUDE_PROJECT_DIR="$FIXTURES_DIR" "$TEST_HOOK" >/dev/null 2>&1

    STATE_FILE="$FIXTURES_DIR/WAI-Spoke/WAI-State.json"

    assert_file_contains "$STATE_FILE" '"protocol_completed": true' "Should set protocol_completed to true"
    assert_file_contains "$STATE_FILE" '"briefing_provided": true' "Should set briefing_provided to true"
    assert_file_contains "$STATE_FILE" '"protocol_last_run"' "Should set protocol_last_run timestamp"
}

test_handles_missing_fields_gracefully() {
    echo ""
    echo "Test: Handle missing fields gracefully"

    # Create minimal state file with missing optional fields
    cat > "$FIXTURES_DIR/WAI-Spoke/WAI-State.json" <<EOF
{
  "wheel": {
    "name": "Minimal Project"
  },
  "_session_state": {
    "protocol_completed": false
  },
  "context": {
    "next_actions": []
  },
  "decisions": []
}
EOF

    cd "$FIXTURES_DIR"
    OUTPUT=$(CLAUDE_PROJECT_DIR="$FIXTURES_DIR" "$TEST_HOOK" 2>&1)
    EXIT_CODE=$?

    assert_exit_code 0 $EXIT_CODE "Should exit successfully even with minimal state"
    assert_contains "$OUTPUT" "Minimal Project" "Should still show project name"
    assert_contains "$OUTPUT" "Wheelwright Context Loaded" "Should still generate briefing"
}

# Run all tests
run_tests() {
    echo -e "${YELLOW}Running session-start.sh tests...${NC}"

    setup

    test_exits_when_no_state_file

    teardown
    setup
    test_exits_when_protocol_completed

    teardown
    setup
    test_generates_briefing_correctly

    teardown
    setup
    test_filters_high_impact_decisions

    teardown
    setup
    test_shows_next_actions

    teardown
    setup
    test_detects_uncommitted_changes

    teardown
    setup
    test_shows_clean_tree_message

    teardown
    setup
    test_updates_session_state

    teardown
    setup
    test_handles_missing_fields_gracefully

    teardown

    # Print summary
    echo ""
    echo "========================================"
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
    else
        echo -e "${RED}Some tests failed!${NC}"
    fi
    echo "Tests run: $TESTS_RUN"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    if [ $TESTS_FAILED -gt 0 ]; then
        echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    fi
    echo "========================================"

    if [ $TESTS_FAILED -gt 0 ]; then
        exit 1
    fi
}

# Main execution
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    run_tests
fi

#!/bin/bash
#
# Wheelwright Framework - Smoke Tests
# Verifies core framework functionality after changes
#

set +e  # Don't exit on errors - we want to see all test results

echo "========================================="
echo "Wheelwright Framework - Smoke Tests"
echo "========================================="
echo ""

PASSED=0
FAILED=0
TOTAL=0

# Test helper
test_condition() {
    local description=$1
    local command=$2
    local expected_result=$3  # "success" or "failure"

    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] $description... "

    eval "$command" > /dev/null 2>&1
    result=$?

    if [[ "$expected_result" == "success" && $result -eq 0 ]] || \
       [[ "$expected_result" == "failure" && $result -ne 0 ]]; then
        echo "✓ PASS"
        PASSED=$((PASSED + 1))
    else
        echo "✗ FAIL (exit code: $result)"
        FAILED=$((FAILED + 1))
    fi
}

# Test file existence
test_file_exists() {
    local description=$1
    local filepath=$2

    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] $description... "

    if [[ -f "$filepath" ]]; then
        echo "✓ PASS"
        PASSED=$((PASSED + 1))
    else
        echo "✗ FAIL (file not found: $filepath)"
        FAILED=$((FAILED + 1))
    fi
}

# Test JSON validity
test_json_valid() {
    local description=$1
    local filepath=$2

    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] $description... "

    if jq empty "$filepath" 2>/dev/null; then
        echo "✓ PASS"
        PASSED=$((PASSED + 1))
    else
        echo "✗ FAIL (invalid JSON)"
        FAILED=$((FAILED + 1))
    fi
}

# Test JSONL validity
test_jsonl_valid() {
    local description=$1
    local filepath=$2

    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] $description... "

    valid=true
    while IFS= read -r line; do
        if ! echo "$line" | jq empty 2>/dev/null; then
            valid=false
            break
        fi
    done < "$filepath"

    if [[ "$valid" == "true" ]]; then
        echo "✓ PASS"
        PASSED=$((PASSED + 1))
    else
        echo "✗ FAIL (invalid JSONL)"
        FAILED=$((FAILED + 1))
    fi
}

# Test content match
test_content_contains() {
    local description=$1
    local filepath=$2
    local pattern=$3

    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] $description... "

    if grep -q "$pattern" "$filepath" 2>/dev/null; then
        echo "✓ PASS"
        PASSED=$((PASSED + 1))
    else
        echo "✗ FAIL (pattern not found: $pattern)"
        FAILED=$((FAILED + 1))
    fi
}

echo "=== SECTION 1: Naming Migration (WWAI → WAI) ==="
echo ""

test_file_exists "WAI-CLI tool exists" "./WAI-CLI"
test_condition "WAI-CLI is executable" "[[ -x ./WAI-CLI ]]" "success"
test_condition "WAI-Spoke directory exists" "[[ -d ./WAI-Spoke ]]" "success"
test_file_exists "WAI-Spoke/WAI-State.json exists" "./WAI-Spoke/WAI-State.json"
test_file_exists "WAI-Spoke/WAI-State.md exists" "./WAI-Spoke/WAI-State.md"
test_file_exists "WAI-Spoke/WAI-Guide.md exists" "./WAI-Spoke/WAI-Guide.md"
test_file_exists "WAI-Spoke/WAI-Signals.jsonl exists" "./WAI-Spoke/WAI-Signals.jsonl"
test_condition "Old .wwai directory does NOT exist" "[[ ! -d ./.wwai ]]" "success"
test_condition "Old wwai tool does NOT exist" "[[ ! -f ./wwai ]]" "success"

echo ""
echo "=== SECTION 2: No WWAI References (Should be WAI) ==="
echo ""

test_condition "CLAUDE.md has no WWAI references" "! grep -q 'WWAI' ./CLAUDE.md" "success"
test_condition "README.md has no WWAI references" "! grep -q 'WWAI' ./README.md" "success"
test_condition "WAI-Guide.md has no WWAI references" "! grep -q 'WWAI' ./WAI-Spoke/WAI-Guide.md" "success"
test_condition "WAI-State.md has no WWAI references" "! grep -q 'WWAI' ./WAI-Spoke/WAI-State.md" "success"

echo ""
echo "=== SECTION 3: Correct Spelling (Wheelwright not 'Wheel Wright') ==="
echo ""

test_condition "README.md has no 'Wheel Wright'" "! grep -q 'Wheel Wright' ./README.md" "success"
test_condition "CLAUDE.md has no 'Wheel Wright'" "! grep -q 'Wheel Wright' ./CLAUDE.md" "success"
test_condition "WAI-Guide.md has no 'Wheel Wright'" "! grep -q 'Wheel Wright' ./WAI-Spoke/WAI-Guide.md" "success"

echo ""
echo "=== SECTION 4: WAI File Validity ==="
echo ""

test_json_valid "WAI-State.json is valid JSON" "./WAI-Spoke/WAI-State.json"
test_jsonl_valid "WAI-Signals.jsonl is valid JSONL" "./WAI-Spoke/WAI-Signals.jsonl"

echo ""
echo "=== SECTION 5: Session Start Hook ==="
echo ""

test_file_exists "session-start.sh exists" "./WAI-Spoke/hooks/session-start.sh"
test_condition "session-start.sh is executable" "[[ -x ./WAI-Spoke/hooks/session-start.sh ]]" "success"
test_condition "session-start.sh has no CRLF line endings" "! file ./WAI-Spoke/hooks/session-start.sh | grep -q 'CRLF'" "success"
test_content_contains "session-start hook uses WAI-Spoke/ paths" "./WAI-Spoke/hooks/session-start.sh" "WAI-Spoke/WAI-State.json"
test_content_contains "session-start hook initializes conversation log" "./WAI-Spoke/hooks/session-start.sh" "WAI-Session-Log.jsonl"

echo ""
echo "=== SECTION 6: Claude Code Hook Configuration ==="
echo ""

test_file_exists ".claude/settings.json exists" "./.claude/settings.json"
test_json_valid ".claude/settings.json is valid JSON" "./.claude/settings.json"
test_content_contains ".claude/settings.json uses WAI-Spoke/ path" "./.claude/settings.json" "WAI-Spoke/hooks/session-start.sh"

echo ""
echo "=== SECTION 7: Unit Tests ==="
echo ""

test_file_exists "test-session-start.sh exists" "./WAI-Spoke/hooks/test-session-start.sh"
test_condition "test-session-start.sh is executable" "[[ -x ./WAI-Spoke/hooks/test-session-start.sh ]]" "success"
test_condition "Unit tests pass" "./WAI-Spoke/hooks/test-session-start.sh" "success"

echo ""
echo "=== SECTION 8: Conversation Logging Feature ==="
echo ""

test_content_contains "CLAUDE.md documents conversation logging" "./CLAUDE.md" "Conversation Logging"
test_content_contains "CLAUDE.md has closeout command" "./CLAUDE.md" "Command: 'Closeout'"
test_content_contains "CLAUDE.md has shipit command" "./CLAUDE.md" "Command: 'Shipit'"
test_content_contains "WAI-Guide.md documents conversation logging" "./WAI-Spoke/WAI-Guide.md" "Conversation Logging"
test_content_contains ".gitignore excludes conversation log" "./.gitignore" "session-conversation.jsonl"

echo ""
echo "=== SECTION 9: Hub Learning Dependency ==="
echo ""

test_content_contains "CLAUDE.md mentions hub learning dependency" "./CLAUDE.md" "Hub learning cannot proceed"
test_content_contains "WAI-Guide.md mentions hub learning dependency" "./WAI-Spoke/WAI-Guide.md" "Hub learning cannot proceed"

echo ""
echo "=== SECTION 10: WAI Branding ==="
echo ""

test_content_contains "README has 'This is the WAI' tagline" "./README.md" "This is the WAI"
test_content_contains "README explains WAI stands for Wheelwright AI" "./README.md" "Wheelwright AI"
test_content_contains "README has wheel metaphor explanation" "./README.md" "\*\*Hub\*\*"
test_content_contains "README clarifies wheelwright-ai branding" "./README.md" "wheelwright-ai"

echo ""
echo "=== SECTION 11: Token Efficiency Protocols ==="
echo ""

test_content_contains "WAI-Guide.md has Token Efficiency section" "./WAI-Spoke/WAI-Guide.md" "Token Efficiency & Multi-Stage Workflow"
test_content_contains "WAI-Guide.md has ADAPTIVE workflow" "./WAI-Spoke/WAI-Guide.md" "ADAPTIVE Workflow Mode"
test_content_contains "WAI-Guide.md has standardized plan template" "./WAI-Spoke/WAI-Guide.md" "Standardized Plan Template"
test_content_contains "WAI-Guide.md has checkpointing protocol" "./WAI-Spoke/WAI-Guide.md" "Checkpointing Protocol"
test_content_contains "WAI-Guide.md has context hygiene rules" "./WAI-Spoke/WAI-Guide.md" "Context Hygiene Rules"
test_content_contains "WAI-Guide.md has Compact command" "./WAI-Spoke/WAI-Guide.md" "Command: 'Compact'"

test_content_contains "CLAUDE.md has PRIORITY 1.5 section" "./CLAUDE.md" "PRIORITY 1.5: TOKEN EFFICIENCY"
test_content_contains "CLAUDE.md has complexity assessment" "./CLAUDE.md" "Assess task complexity"
test_content_contains "CLAUDE.md has Compact command" "./CLAUDE.md" "Command: 'Compact'"

test_file_exists "Cursor template exists" "./templates/cursor/.cursorrules"
test_file_exists "VS Code template exists" "./templates/vscode/settings.json"
test_file_exists "Generic template exists" "./templates/generic/AI-INSTRUCTIONS.md"

echo ""
echo "========================================="
echo "SMOKE TEST RESULTS"
echo "========================================="
echo "Total tests: $TOTAL"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo "✓ ALL SMOKE TESTS PASSED!"
    echo ""
    exit 0
else
    echo "✗ SOME TESTS FAILED"
    echo ""
    exit 1
fi

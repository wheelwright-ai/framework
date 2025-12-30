#!/bin/bash
#
# Wheelwright Spoke - Smoke Tests
# Verifies this spoke's WAI files are correctly configured
#

set +e  # Don't exit on errors - we want to see all test results

echo "========================================="
echo "Wheelwright Spoke - WAI Files Smoke Tests"
echo "========================================="
echo ""

PASSED=0
FAILED=0
TOTAL=0

# Test helper
test_jq_query() {
    local description=$1
    local filepath=$2
    local jq_query=$3
    local expected_value=$4

    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] $description... "

    actual_value=$(jq -r "$jq_query" "$filepath" 2>/dev/null)

    if [[ "$actual_value" == "$expected_value" ]]; then
        echo "✓ PASS"
        PASSED=$((PASSED + 1))
    else
        echo "✗ FAIL (expected: '$expected_value', got: '$actual_value')"
        FAILED=$((FAILED + 1))
    fi
}

test_jq_exists() {
    local description=$1
    local filepath=$2
    local jq_query=$3

    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] $description... "

    value=$(jq -r "$jq_query" "$filepath" 2>/dev/null)

    if [[ "$value" != "null" && -n "$value" ]]; then
        echo "✓ PASS"
        PASSED=$((PASSED + 1))
    else
        echo "✗ FAIL (field missing or null)"
        FAILED=$((FAILED + 1))
    fi
}

test_jq_array_not_empty() {
    local description=$1
    local filepath=$2
    local jq_query=$3

    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] $description... "

    count=$(jq -r "$jq_query | length" "$filepath" 2>/dev/null)

    if [[ "$count" -gt 0 ]]; then
        echo "✓ PASS (count: $count)"
        PASSED=$((PASSED + 1))
    else
        echo "✗ FAIL (array is empty)"
        FAILED=$((FAILED + 1))
    fi
}

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

echo "=== SECTION 1: WAI-State.json Structure ==="
echo ""

test_json_valid "WAI-State.json is valid JSON" "./WAI-Spoke/WAI-State.json"
test_jq_exists "wheelwright section exists" "./WAI-Spoke/WAI-State.json" ".wheelwright"
test_jq_exists "_project_foundation section exists" "./WAI-Spoke/WAI-State.json" "._project_foundation"
test_jq_exists "_session_state section exists" "./WAI-Spoke/WAI-State.json" "._session_state"
test_jq_exists "wheel section exists" "./WAI-Spoke/WAI-State.json" ".wheel"
test_jq_exists "context section exists" "./WAI-Spoke/WAI-State.json" ".context"
test_jq_exists "decisions array exists" "./WAI-Spoke/WAI-State.json" ".decisions"

echo ""
echo "=== SECTION 2: Project Foundation ==="
echo ""

test_jq_query "Foundation is complete" "./WAI-Spoke/WAI-State.json" "._project_foundation.completed" "true"
test_jq_exists "Foundation has identity" "./WAI-Spoke/WAI-State.json" "._project_foundation.identity"
test_jq_exists "Foundation has boundaries" "./WAI-Spoke/WAI-State.json" "._project_foundation.boundaries"
test_jq_exists "Foundation has approach" "./WAI-Spoke/WAI-State.json" "._project_foundation.approach"
test_jq_exists "Foundation has philosophy" "./WAI-Spoke/WAI-State.json" "._project_foundation.philosophy"
test_jq_query "AI collaboration style is YOLO" "./WAI-Spoke/WAI-State.json" "._project_foundation.approach.ai_collaboration_style" "yolo"

echo ""
echo "=== SECTION 3: Session State Schema ==="
echo ""

test_jq_exists "Session state has last_session_id" "./WAI-Spoke/WAI-State.json" "._session_state.last_session_id"
test_jq_exists "Session state has last_modified_by" "./WAI-Spoke/WAI-State.json" "._session_state.last_modified_by"
test_jq_exists "Session state has last_modified_at" "./WAI-Spoke/WAI-State.json" "._session_state.last_modified_at"
test_jq_exists "Session state has protocol_completed" "./WAI-Spoke/WAI-State.json" "._session_state.protocol_completed"
test_jq_exists "Session state has current_session field" "./WAI-Spoke/WAI-State.json" "._session_state | has(\"current_session\")"
test_jq_exists "Session state has last_closeout field" "./WAI-Spoke/WAI-State.json" "._session_state | has(\"last_closeout\")"

echo ""
echo "=== SECTION 4: Decisions Log ==="
echo ""

test_jq_array_not_empty "Decisions array has entries" "./WAI-Spoke/WAI-State.json" ".decisions"
test_jq_exists "Has conversation logging decision" "./WAI-Spoke/WAI-State.json" ".decisions[] | select(.decision | contains(\"Conversation logging\"))"
test_jq_exists "Has shipit command decision" "./WAI-Spoke/WAI-State.json" ".decisions[] | select(.decision | contains(\"Shipit\"))"
test_jq_exists "Has WWAI → WAI naming decision" "./WAI-Spoke/WAI-State.json" ".decisions[] | select(.decision | contains(\"WAI naming\"))"
test_jq_exists "Has unit test suite decision" "./WAI-Spoke/WAI-State.json" ".decisions[] | select(.decision | contains(\"unit test\"))"
test_jq_exists "Has dual-layer testing policy decision" "./WAI-Spoke/WAI-State.json" ".decisions[] | select(.decision | contains(\"Dual-layer testing\"))"

echo ""
echo "=== SECTION 5: Evolution Log ==="
echo ""

test_jq_array_not_empty "Evolution log has entries" "./WAI-Spoke/WAI-State.json" "._project_foundation.evolution_log"
test_jq_exists "Has conversation logging evolution entry" "./WAI-Spoke/WAI-State.json" "._project_foundation.evolution_log[] | select(.change | contains(\"conversation logging\"))"

echo ""
echo "=== SECTION 6: Wheel Signals ==="
echo ""

TOTAL=$((TOTAL + 1))
echo -n "[$TOTAL] wheel-signals.jsonl is valid JSONL... "
valid=true
line_count=0
while IFS= read -r line; do
    line_count=$((line_count + 1))
    if ! echo "$line" | jq empty 2>/dev/null; then
        valid=false
        echo "✗ FAIL (invalid JSON on line $line_count)"
        FAILED=$((FAILED + 1))
        break
    fi
done < "./WAI-Spoke/wheel-signals.jsonl"

if [[ "$valid" == "true" ]]; then
    echo "✓ PASS ($line_count entries)"
    PASSED=$((PASSED + 1))
fi

TOTAL=$((TOTAL + 1))
echo -n "[$TOTAL] wheel-signals.jsonl has conversation logging signal... "
if grep -q "conversation logging" "./WAI-Spoke/wheel-signals.jsonl"; then
    echo "✓ PASS"
    PASSED=$((PASSED + 1))
else
    echo "✗ FAIL"
    FAILED=$((FAILED + 1))
fi

TOTAL=$((TOTAL + 1))
echo -n "[$TOTAL] wheel-signals.jsonl has naming standardization signal... "
if grep -q "Capitalized WAI-Spoke/" "./WAI-Spoke/wheel-signals.jsonl"; then
    echo "✓ PASS"
    PASSED=$((PASSED + 1))
else
    echo "✗ FAIL"
    FAILED=$((FAILED + 1))
fi

TOTAL=$((TOTAL + 1))
echo -n "[$TOTAL] wheel-signals.jsonl has unit test signal... "
if grep -q "unit test suite" "./WAI-Spoke/wheel-signals.jsonl"; then
    echo "✓ PASS"
    PASSED=$((PASSED + 1))
else
    echo "✗ FAIL"
    FAILED=$((FAILED + 1))
fi

TOTAL=$((TOTAL + 1))
echo -n "[$TOTAL] wheel-signals.jsonl has dual-layer testing policy... "
if grep -q "Dual-layer testing" "./WAI-Spoke/wheel-signals.jsonl"; then
    echo "✓ PASS"
    PASSED=$((PASSED + 1))
else
    echo "✗ FAIL"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "=== SECTION 7: WAI Naming Consistency ==="
echo ""

test_jq_query "Wheel name uses 'Wheelwright'" "./WAI-Spoke/WAI-State.json" ".wheel.name" "Wheelwright Framework"
test_jq_query "GitHub repo is wheelwright-ai/framework" "./WAI-Spoke/WAI-State.json" ".wheelwright.github_repo" "wheelwright-ai/framework"

TOTAL=$((TOTAL + 1))
echo -n "[$TOTAL] No 'Wheel Wright' (two words) in WAI-State.json... "
if ! grep -q "Wheel Wright" "./WAI-Spoke/WAI-State.json"; then
    echo "✓ PASS"
    PASSED=$((PASSED + 1))
else
    echo "✗ FAIL (found incorrect spelling)"
    FAILED=$((FAILED + 1))
fi

TOTAL=$((TOTAL + 1))
echo -n "[$TOTAL] No WWAI references outside historical logs... "
# Exclude evolution_log and decisions where historical "WWAI → WAI" references are expected
if jq -r 'del(._project_foundation.evolution_log) | del(.decisions) | tostring' "./WAI-Spoke/WAI-State.json" | grep -q "WWAI"; then
    echo "✗ FAIL (found WWAI references outside historical context)"
    FAILED=$((FAILED + 1))
else
    echo "✓ PASS"
    PASSED=$((PASSED + 1))
fi

echo ""
echo "=== SECTION 8: High-Impact Decisions (impact >= 8) ==="
echo ""

TOTAL=$((TOTAL + 1))
echo -n "[$TOTAL] At least 5 high-impact decisions from this session... "
high_impact_count=$(jq -r '[.decisions[] | select(.impact >= 8)] | length' "./WAI-Spoke/WAI-State.json" 2>/dev/null)
if [[ "$high_impact_count" -ge 5 ]]; then
    echo "✓ PASS (found $high_impact_count total)"
    PASSED=$((PASSED + 1))
else
    echo "✗ FAIL (found only $high_impact_count)"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "=== SECTION 9: Current Session State ==="
echo ""

test_jq_query "protocol_completed is true" "./WAI-Spoke/WAI-State.json" "._session_state.protocol_completed" "true"
test_jq_exists "protocol_last_run timestamp exists" "./WAI-Spoke/WAI-State.json" "._session_state.protocol_last_run"

echo ""
echo "=== SECTION 10: Token Efficiency Schema ==="
echo ""

test_jq_exists "complexity_thresholds field exists" "./WAI-Spoke/WAI-State.json" ".context.complexity_thresholds"
test_jq_exists "capacity_management field exists" "./WAI-Spoke/WAI-State.json" ".context.capacity_management"
test_jq_query "Multi-file threshold is 2" "./WAI-Spoke/WAI-State.json" ".context.complexity_thresholds.multi_file_threshold" "2"
test_jq_query "Step count threshold is 6" "./WAI-Spoke/WAI-State.json" ".context.complexity_thresholds.step_count_threshold" "6"
test_jq_query "Checkpoint interval is 3" "./WAI-Spoke/WAI-State.json" ".context.complexity_thresholds.checkpoint_interval" "3"
test_jq_query "Warning threshold is 0.80" "./WAI-Spoke/WAI-State.json" ".context.capacity_management.warning_threshold" "0.80"
test_jq_query "Critical threshold is 0.90" "./WAI-Spoke/WAI-State.json" ".context.capacity_management.critical_threshold" "0.90"
test_jq_query "Workflow mode is ADAPTIVE" "./WAI-Spoke/WAI-State.json" ".ai_context.workflow_mode" "ADAPTIVE"
test_jq_query "Plan template version is v1.0" "./WAI-Spoke/WAI-State.json" ".ai_context.plan_template_version" "v1.0"
test_jq_query "Token efficiency protocols is v1.0" "./WAI-Spoke/WAI-State.json" ".ai_context.token_efficiency_protocols" "v1.0"

echo ""
echo "========================================="
echo "SPOKE SMOKE TEST RESULTS"
echo "========================================="
echo "Total tests: $TOTAL"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo "✓ ALL SPOKE SMOKE TESTS PASSED!"
    echo ""
    exit 0
else
    echo "✗ SOME TESTS FAILED"
    echo ""
    exit 1
fi

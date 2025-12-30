#!/bin/bash
# Comprehensive Menu Testing Script

echo "=========================================="
echo "WAI CLI Comprehensive Menu Test"
echo "=========================================="
echo ""

# Test counter
total_tests=0
passed_tests=0

run_test() {
    local test_name="$1"
    local input="$2"
    local expected_pattern="$3"

    total_tests=$((total_tests + 1))
    echo "Test $total_tests: $test_name"

    # Run command and capture output
    output=$(echo -e "$input" | python3 WAI 2>&1)

    # Check if expected pattern is in output
    if echo "$output" | grep -q "$expected_pattern"; then
        echo "  ✓ PASS"
        passed_tests=$((passed_tests + 1))
    else
        echo "  ✗ FAIL - Expected: $expected_pattern"
        echo "  Output snippet:"
        echo "$output" | tail -10 | sed 's/^/    /'
    fi
    echo ""
}

# Framework Menu Tests
run_test "Framework Menu -> Exit" "6" "Framework Menu"
run_test "Framework Menu -> Help" "5\n6" "usage: WAI"
run_test "Framework Menu -> Spoke -> Status" "1\n1\n5\n6" "Wheelwright Status"
run_test "Framework Menu -> Spoke -> Back" "1\n5\n6" "Spoke Actions"
run_test "Framework Menu -> Hub -> Locate" "2\n1\n3\n6" "Hub"
run_test "Framework Menu -> Hub -> Back" "2\n3\n6" "Hub Actions"
run_test "Framework Menu -> Projects -> List" "3\n1\n4\n6" "Projects Actions"
run_test "Framework Menu -> Projects -> Back" "3\n4\n6" "Projects Actions"
run_test "Framework Menu -> Groups -> List" "4\n1\n6\n6" "Groups Actions"
run_test "Framework Menu -> Groups -> Back" "4\n6\n6" "Groups Actions"

# Spoke Actions Tests
run_test "Spoke -> Status" "1\n1\n5\n6" "Wheelwright Status"
run_test "Spoke -> Sync" "1\n2\n5\n6" "Checking spoke structure"
run_test "Spoke -> Closeout" "1\n3\n5\n6" "Session Closeout"
run_test "Spoke -> Context" "1\n4\n5\n6" "WAI-Guide.md"

# Hub Actions Tests
run_test "Hub -> Locate" "2\n1\n3\n6" "Hub"
# run_test "Hub -> Create" "2\n2\nn\n3\n6" "Hub"  # Skip actual creation

# Projects Actions Tests
run_test "Projects -> List all" "3\n1\n4\n6" "projects"

# Groups Actions Tests
run_test "Groups -> List" "4\n1\n6\n6" "Groups"

# Command Line Tests
run_test "CLI: status" "" "Wheelwright Status"
python3 WAI status > /dev/null 2>&1
if [ $? -eq 0 ]; then
    total_tests=$((total_tests + 1))
    passed_tests=$((passed_tests + 1))
    echo "Test $total_tests: CLI: WAI status"
    echo "  ✓ PASS"
else
    total_tests=$((total_tests + 1))
    echo "Test $total_tests: CLI: WAI status"
    echo "  ✗ FAIL"
fi
echo ""

python3 WAI version > /dev/null 2>&1
if [ $? -eq 0 ]; then
    total_tests=$((total_tests + 1))
    passed_tests=$((passed_tests + 1))
    echo "Test $total_tests: CLI: WAI version"
    echo "  ✓ PASS"
else
    total_tests=$((total_tests + 1))
    echo "Test $total_tests: CLI: WAI version"
    echo "  ✗ FAIL"
fi
echo ""

python3 WAI --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    total_tests=$((total_tests + 1))
    passed_tests=$((passed_tests + 1))
    echo "Test $total_tests: CLI: WAI --help"
    echo "  ✓ PASS"
else
    total_tests=$((total_tests + 1))
    echo "Test $total_tests: CLI: WAI --help"
    echo "  ✗ FAIL"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Total tests: $total_tests"
echo "Passed: $passed_tests"
echo "Failed: $((total_tests - passed_tests))"
if [ $passed_tests -eq $total_tests ]; then
    echo ""
    echo "✓ ALL TESTS PASSED!"
    exit 0
else
    echo ""
    echo "✗ Some tests failed"
    exit 1
fi

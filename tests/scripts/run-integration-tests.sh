#!/bin/bash
#
# Wheelwright Integration Test Runner
#
# Usage:
#   ./run-integration-tests.sh [OPTIONS]
#
# Options:
#   --mode=MODE          Test mode: all, baseline-comparison, phase (default: all)
#   --phase=N            Run specific phase (1-5)
#   -v, --verbose        Verbose output
#   --stop-on-failure    Stop on first phase failure
#   --output=FILE        Write report to file
#   --json=FILE          Write JSON results to file
#   --help               Show this help message
#

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_ROOT="$(cd "$SCRIPT_DIR/../../" && pwd)"

# Default values
MODE="all"
VERBOSE=""
STOP_ON_FAILURE=""
OUTPUT_FILE=""
JSON_FILE=""
PHASE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode=*)
            MODE="${1#*=}"
            shift
            ;;
        --phase=*)
            PHASE="${1#*=}"
            MODE="phase"
            shift
            ;;
        -v|--verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --stop-on-failure)
            STOP_ON_FAILURE="--stop-on-failure"
            shift
            ;;
        --output=*)
            OUTPUT_FILE="${1#*=}"
            shift
            ;;
        --json=*)
            JSON_FILE="${1#*=}"
            shift
            ;;
        --help)
            echo "Wheelwright Integration Test Runner"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --mode=MODE          Test mode: all, baseline-comparison, phase (default: all)"
            echo "  --phase=N            Run specific phase (1-5)"
            echo "  -v, --verbose        Verbose output"
            echo "  --stop-on-failure    Stop on first phase failure"
            echo "  --output=FILE        Write report to file"
            echo "  --json=FILE          Write JSON results to file"
            echo "  --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run all tests"
            echo "  $0 --mode=baseline-comparison         # Run baseline comparison"
            echo "  $0 --phase=3                          # Run Phase 3 only"
            echo "  $0 --verbose --output=report.txt      # Verbose with report file"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Header
echo -e "${BLUE}"
echo "======================================================================"
echo "  Wheelwright Integration Test Suite"
echo "======================================================================"
echo -e "${NC}"

# Check if pytest is installed
if ! python3 -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Warning: pytest not found${NC}"
    echo "Installing test dependencies..."
    pip install -q -r "$FRAMEWORK_ROOT/requirements-test.txt"
fi

# Build command
CMD="python3 $FRAMEWORK_ROOT/tests/integration/runner.py"
CMD="$CMD --mode=$MODE"

if [ -n "$PHASE" ]; then
    CMD="$CMD --phase=$PHASE"
fi

if [ -n "$VERBOSE" ]; then
    CMD="$CMD $VERBOSE"
fi

if [ -n "$STOP_ON_FAILURE" ]; then
    CMD="$CMD $STOP_ON_FAILURE"
fi

if [ -n "$OUTPUT_FILE" ]; then
    CMD="$CMD --output=$OUTPUT_FILE"
fi

if [ -n "$JSON_FILE" ]; then
    CMD="$CMD --json=$JSON_FILE"
fi

# Run tests
echo -e "${BLUE}Executing: $CMD${NC}"
echo ""

if $CMD; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    EXIT_CODE=$?
    echo ""
    echo -e "${RED}❌ Tests failed (exit code: $EXIT_CODE)${NC}"
    exit $EXIT_CODE
fi

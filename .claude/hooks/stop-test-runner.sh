#!/bin/bash
#
# WAI Stop Hook — Test Runner
# Runs pytest after Claude finishes a response that modified Python or test files.
# Only fires when relevant files changed (not on pure conversation turns).
#

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Check if any Python files were modified in the working tree since last commit
CHANGED=$(git -C "$PROJECT_DIR" diff --name-only HEAD 2>/dev/null | grep -E '\.py$' | head -1)
STAGED=$(git -C "$PROJECT_DIR" diff --cached --name-only 2>/dev/null | grep -E '\.py$' | head -1)

# Skip if no Python files changed
[[ -z "$CHANGED" && -z "$STAGED" ]] && exit 0

# Run tests (fast fail, quiet output)
cd "$PROJECT_DIR"
RESULT=$(python3 -m pytest tests/ -x -q --tb=short 2>&1)
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "<test-failure>"
  echo "Tests failed after your last change. Fix before continuing."
  echo ""
  echo "$RESULT" | tail -20
  echo "</test-failure>"
  exit 1
fi

# Success — silent (don't clutter output)
exit 0

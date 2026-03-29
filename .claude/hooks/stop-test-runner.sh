#!/bin/bash
#
# WAI Stop Hook — Test Runner
# Runs pytest after Claude finishes a response that modified Python or test files.
# Only fires when relevant files changed (not on pure conversation turns).
#
# Must exit 0 on success or no-op. Exit 1 only for actual test failures.
# Never exit non-zero for infrastructure errors — that blocks Claude.
#

set -o pipefail 2>/dev/null || true

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Bail early if not a git repo
git -C "$PROJECT_DIR" rev-parse --git-dir >/dev/null 2>&1 || exit 0

# Check if any Python files were modified in the working tree since last commit
CHANGED=$(git -C "$PROJECT_DIR" diff --name-only HEAD 2>/dev/null | grep -E '\.py$' || true)
STAGED=$(git -C "$PROJECT_DIR" diff --cached --name-only 2>/dev/null | grep -E '\.py$' || true)

# Skip if no Python files changed
[[ -z "$CHANGED" && -z "$STAGED" ]] && exit 0

# Skip if no tests directory
[[ ! -d "$PROJECT_DIR/tests" ]] && exit 0

# Run tests (fast fail, quiet output)
cd "$PROJECT_DIR" || exit 0
RESULT=$(python3 -m pytest tests/ -x -q --tb=short 2>&1) || true
EXIT_CODE=${PIPESTATUS[0]:-$?}

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

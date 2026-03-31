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

# ── CC Advisor: log session_end event ────────────────────────────────────────
CC_ADVISOR_LOGS="$PROJECT_DIR/WAI-Spoke/advisors/cc-advisor/logs"
STATE_FILE="$PROJECT_DIR/WAI-Spoke/WAI-State.json"
if [[ -f "$STATE_FILE" && -d "$CC_ADVISOR_LOGS" ]]; then
  SESSION_NAME=$(jq -r '._session_state.last_session_id // ""' "$STATE_FILE" 2>/dev/null)
  SPOKE_NAME=$(jq -r '.wheel.name // "unknown"' "$STATE_FILE" 2>/dev/null)
  printf '{"ts":"%s","session":"%s","spoke":"%s","event":"session_end","data":{"duration_minutes":0,"tokens_used":0,"context_pct_at_end":0,"compact_count":0,"permission_prompts":0}}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "${SESSION_NAME}" \
    "${SPOKE_NAME}" \
    >> "$CC_ADVISOR_LOGS/session-events.jsonl"
  printf '{"ts":"%s","session":"%s","spoke":"%s","event":"hook_fire","data":{"hook_name":"stop-test-runner","result":"ok","duration_ms":0,"error":null}}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "${SESSION_NAME}" \
    "${SPOKE_NAME}" \
    >> "$CC_ADVISOR_LOGS/hook-events.jsonl"
fi

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

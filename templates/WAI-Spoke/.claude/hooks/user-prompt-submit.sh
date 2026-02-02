#!/bin/bash
#
# Wheelwright Session Start Hook for Claude Code
# Enforces automatic session briefing on first turn
#
# This hook runs BEFORE Claude sees the user's message
# It injects a mandatory session briefing requirement
#

set -e

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
STATE_FILE="$PROJECT_DIR/WAI-Spoke/WAI-State.json"
LUGS_FILE="$PROJECT_DIR/WAI-Spoke/WAI-Lugs.jsonl"

# Exit silently if WAI-Spoke doesn't exist (not a wheel project)
[[ ! -f "$STATE_FILE" ]] && exit 0

# Detect if this is a new session and reset protocol flag if needed
LAST_SESSION_ID=$(jq -r '._session_state.last_session_id // ""' "$STATE_FILE")
CURRENT_SESSION_ID=$(jq -r '._session_state.current_session.session_id // ""' "$STATE_FILE" 2>/dev/null || echo "")

# If no current session OR current matches last (closeout synced them), this is a new session
if [[ -z "$CURRENT_SESSION_ID" || "$LAST_SESSION_ID" == "$CURRENT_SESSION_ID" ]]; then
  # New session detected - reset protocol flag
  TMP_RESET=$(mktemp)
  jq '._session_state.protocol_completed = false' "$STATE_FILE" > "$TMP_RESET"
  mv "$TMP_RESET" "$STATE_FILE"
fi

# Check if protocol already completed this session
PROTOCOL_COMPLETED=$(jq -r '._session_state.protocol_completed // false' "$STATE_FILE" 2>/dev/null || echo "false")
if [[ "$PROTOCOL_COMPLETED" == "true" ]]; then
  exit 0  # Already ran this session, skip
fi

# Use unified WAI briefing (shared across hooks, commands, and natural language)
BRIEFING_SCRIPT="$PROJECT_DIR/WAI-Spoke/_framework/wai-briefing.sh"
generate_session_focus() {
  if [[ -f "$BRIEFING_SCRIPT" ]]; then
    bash "$BRIEFING_SCRIPT"
  else
    # Fallback if script not found
    echo "## Session Focus"
    echo ""
    echo "WAI briefing script not found at: $BRIEFING_SCRIPT"
    echo "Run: /wai-status to diagnose"
  fi
}

# Build the injected message
INJECTED_MESSAGE="CRITICAL: This is your first turn in this session.

BEFORE responding to the user's message below, you MUST:

1. Load WAI Context files (use Read tool):
   - WAI-Spoke/_framework/WAI-Guide.md
   - WAI-Spoke/WAI-State.json
   - WAI-Spoke/WAI-Lugs.jsonl (filter: load_always=true or s='o'/'p')

2. Provide this Session Focus briefing as part of your response:

$(generate_session_focus)

3. Detect Pending Teachings:
   If teaching files shown in briefing (Pending Teachings section):
   - Review manifest at WAI-Spoke/seed/ingest/manifest.json
   - Examine .teaching files in seed/ingest/
   - Propose adoption plan:
     * Files to adopt immediately
     * Files needing customization
     * Files to defer
   - Create implementation checklist
   - Prioritize teaching adoption before other work

4. Offer Session Goal Setting (Policy: Session Goal Setting - Define Work Cycle Focus):
   After showing recommendations, ask:

   \"What specific goal(s) would you like to focus on for this work cycle?\"

   Based on discussion:
   - Create epic lug (ty='epic', priority='session_focus')
   - Define scope, success criteria, out-of-scope, constraints
   - Set verify_on_closeout=true
   - Work within epic scope - say what we do, do what we say
   - When complete: recommend closeout + new thread

5. Then respond to the user's message.

This protocol is MANDATORY and enforces the automatic briefing specified in AGENTS.md.

---

User's message follows:
"

# Update session state to mark protocol completed
TMP_STATE=$(mktemp)
jq '._session_state.protocol_completed = true |
    ._session_state.protocol_last_run = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))' "$STATE_FILE" > "$TMP_STATE"
mv "$TMP_STATE" "$STATE_FILE"

# Output the injected message
echo "$INJECTED_MESSAGE"

exit 0

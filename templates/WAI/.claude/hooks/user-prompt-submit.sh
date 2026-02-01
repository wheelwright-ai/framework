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

# Check if protocol already completed this session
PROTOCOL_COMPLETED=$(jq -r '._session_state.protocol_completed // false' "$STATE_FILE" 2>/dev/null || echo "false")
if [[ "$PROTOCOL_COMPLETED" == "true" ]]; then
  exit 0  # Already ran this session, skip
fi

# Generate Session Focus briefing following AGENTS.md specification
generate_session_focus() {
  local project_name=$(jq -r '.wheel.name // "Unknown Project"' "$STATE_FILE")
  local last_teach=$(jq -r '.wheelwright.sync_history[-1].date // "never"' "$STATE_FILE" 2>/dev/null || echo "never")
  local token_pct=$(jq -r '._session_state.context_usage_at_closeout // 0 | . * 100 | floor' "$STATE_FILE" 2>/dev/null || echo "0")

  echo "## Session Focus"
  echo ""
  echo "### Active Work (Prioritized)"
  echo ""

  # Apply backlog prioritization logic from AGENTS.md
  # Priority order:
  # 1. Hub guidance from last teach
  # 2. Flagged items (priority='before_next_epic')
  # 3. Bugs (ty='b', s='open')
  # 4. Stories/tasks with verify_on_closeout=true
  # 5. In-progress work (s='p')
  # 6. Open tasks (s='o')
  # 7. Epics (ty='e') - ONLY after above are clear

  if [[ -f "$LUGS_FILE" ]]; then
    # Count lugs by priority
    local flagged_count=$(jq -r 'select(.priority == "before_next_epic" and .s == "open") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)
    local bugs_count=$(jq -r 'select(.ty == "bug" and .s == "open") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)
    local verify_count=$(jq -r 'select(.verify_on_closeout == true and .s == "open") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)
    local in_progress_count=$(jq -r 'select(.s == "p") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)
    local open_count=$(jq -r 'select(.s == "o" and .ty != "epic") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)
    local epic_count=$(jq -r 'select(.ty == "epic" and .s == "open") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)

    echo "**🚨 Flagged Priority (Must Complete First):** $flagged_count items"
    echo "**🐛 Bugs:** $bugs_count open"
    echo "**✓ Stories/Tasks (Verification Needed):** $verify_count items"
    echo "**⏳ In Progress:** $in_progress_count items"
    echo "**📋 Open Tasks:** $open_count items"
    echo "**🎪 Epics (Blocked Until Above Clear):** $epic_count epics"
    echo ""

    # Show top priority item
    local top_priority=$(jq -r '
      select(.priority == "before_next_epic" and .s == "open") |
      "\(.i): \(.t)"
    ' "$LUGS_FILE" 2>/dev/null | head -1)

    if [[ -n "$top_priority" ]]; then
      echo "**Top Priority:** $top_priority"
    fi
  fi

  echo ""
  echo "### Verification Status"
  if [[ -f "$LUGS_FILE" ]]; then
    jq -r 'select(.verify_on_closeout == true) |
      "- \(.t): \(.verification_count // 0)/\(.verification_target // 5) verified"
    ' "$LUGS_FILE" 2>/dev/null | head -5
  fi

  echo ""
  echo "### Context Health"
  echo "- Token usage: ${token_pct}% of 200K"

  local lugs_loaded=$(jq -r 'select(.load_always == true or .s == "o" or .s == "p") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)
  echo "- Lugs loaded: $lugs_loaded"
  echo "- Last teach: $last_teach"

  echo ""
  echo "### Recommended Next Action"
  echo "Review the prioritized backlog above and choose your next task."
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

3. Offer Session Goal Setting (Policy: Session Goal Setting - Define Work Cycle Focus):
   After showing recommendations, ask:

   \"What specific goal(s) would you like to focus on for this work cycle?\"

   Based on discussion:
   - Create epic lug (ty='epic', priority='session_focus')
   - Define scope, success criteria, out-of-scope, constraints
   - Set verify_on_closeout=true
   - Work within epic scope - say what we do, do what we say
   - When complete: recommend closeout + new thread

4. Then respond to the user's message.

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

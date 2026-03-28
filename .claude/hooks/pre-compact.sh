#!/bin/bash
#
# WAI PreCompact Hook — State Preservation
# Saves critical context before Claude compacts the conversation.
# Ensures track, active work summary, and session state survive compaction.
#

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
STATE_FILE="$PROJECT_DIR/WAI-Spoke/WAI-State.json"
GUARD_FILE="$PROJECT_DIR/WAI-Spoke/runtime/session-guard.json"

# Exit silently if not a WAI project
[[ ! -f "$STATE_FILE" ]] && exit 0

# Get current session track path
TRACK_PATH=$(jq -r '._session_state.track_path // ""' "$STATE_FILE" 2>/dev/null)

# Count track entries for the compaction note
TRACK_TURNS=0
if [[ -n "$TRACK_PATH" && -f "$PROJECT_DIR/$TRACK_PATH" ]]; then
  TRACK_TURNS=$(wc -l < "$PROJECT_DIR/$TRACK_PATH" 2>/dev/null || echo 0)
fi

# Count active lugs
ACTIVE_LUGS=$(ls "$PROJECT_DIR"/WAI-Spoke/lugs/bytype/*/open/*.json "$PROJECT_DIR"/WAI-Spoke/lugs/bytype/*/in_progress/*.json 2>/dev/null | wc -l)

# Emit compaction context that survives into the compressed conversation
cat << COMPACT
<wai-pre-compact>
Context compaction occurring. Key state preserved:
- Track: $TRACK_PATH ($TRACK_TURNS turns recorded)
- Active lugs: $ACTIVE_LUGS items across bytype/
- State: WAI-Spoke/WAI-State.json (last session: $(jq -r '._session_state.last_session_id // "unknown"' "$STATE_FILE" 2>/dev/null))
- Next actions: $(jq -r '._session_state.next_session_recommendation // "none"' "$STATE_FILE" 2>/dev/null | head -c 200)

After compaction: Re-read WAI-State.json and recent track entries to rebuild context.
Rules still active: P1-Persist, P2-Verify, P3-Steward, P10-Autonomy, P11-Lug-First.
</wai-pre-compact>
COMPACT

exit 0

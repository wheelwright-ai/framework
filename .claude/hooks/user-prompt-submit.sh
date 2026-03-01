#!/bin/bash
#
# WAI Session Hook — thin trigger for wakeup protocol
# Runs BEFORE Claude sees the user's message on first turn.
# Injects directive to run /wai skill. All logic lives in wai.md.
#

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
STATE_FILE="$PROJECT_DIR/WAI-Spoke/WAI-State.json"

# Exit silently if not a WAI project
[[ ! -f "$STATE_FILE" ]] && exit 0

# Detect new session: compare last_session_id vs current_session_id
LAST_SESSION_ID=$(jq -r '._session_state.last_session_id // ""' "$STATE_FILE" 2>/dev/null || echo "")
CURRENT_SESSION_ID=$(jq -r '._session_state.current_session.session_id // ""' "$STATE_FILE" 2>/dev/null || echo "")

# If no current session OR current matches last, this is a new session — reset protocol flag
if [[ -z "$CURRENT_SESSION_ID" || "$LAST_SESSION_ID" == "$CURRENT_SESSION_ID" ]]; then
  TMP=$(mktemp)
  jq '._session_state.protocol_completed = false' "$STATE_FILE" > "$TMP" && mv "$TMP" "$STATE_FILE"
fi

# Skip if protocol already ran this session
PROTOCOL_COMPLETED=$(jq -r '._session_state.protocol_completed // false' "$STATE_FILE" 2>/dev/null || echo "false")
[[ "$PROTOCOL_COMPLETED" == "true" ]] && exit 0

# Mark protocol as triggered
TMP=$(mktemp)
jq '._session_state.protocol_completed = true |
    ._session_state.protocol_last_run = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))' "$STATE_FILE" > "$TMP" && mv "$TMP" "$STATE_FILE"

# Inject wakeup directive — agent follows /wai skill (wai.md), no bash script needed
cat << 'EOF'
<wai-session-start>
CRITICAL: This is your first turn in a new session. Before responding to the user:

1. Run your WAI wakeup protocol by following the /wai skill (templates/commands/wai.md).
   Produce the full WAI Point briefing: project identity, active work, context health, next actions.

2. If briefing shows autosave checkpoints (incomplete work from previous session):
   Ask: Resume [task]? (Green Light to resume / Red Light to inspect / skip)

3. If briefing shows pending teachings in seed/ingest/:
   Prioritize review before other work. Follow /wai-learn skill.

4. Then respond to the user's message.
</wai-session-start>
EOF

exit 0

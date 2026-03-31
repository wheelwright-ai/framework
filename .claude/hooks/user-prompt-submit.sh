#!/bin/bash
#
# WAI Session Hook — thin trigger for wakeup protocol
# Runs BEFORE Claude sees the user's message on first turn.
# Injects directive to run /wai skill. All logic lives in wai.md.
#

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
STATE_FILE="$PROJECT_DIR/WAI-Spoke/WAI-State.json"

# Auto-init: if no WAI-State.json but template exists, bootstrap
TEMPLATE_FILE="$PROJECT_DIR/templates/spoke/WAI-State.json.template"
if [[ ! -f "$STATE_FILE" && -f "$TEMPLATE_FILE" ]]; then
  mkdir -p "$PROJECT_DIR/WAI-Spoke"
  cp "$TEMPLATE_FILE" "$STATE_FILE"
fi

# Exit silently if still no state file (not a WAI project)
[[ ! -f "$STATE_FILE" ]] && exit 0

# Session guard uses a runtime file (gitignored) to avoid dirtying WAI-State.json
RUNTIME_DIR="$PROJECT_DIR/WAI-Spoke/runtime"
GUARD_FILE="$RUNTIME_DIR/session-guard.json"
mkdir -p "$RUNTIME_DIR"

# Read guard state (if exists)
GUARD_SESSION_ID=""
GUARD_COMPLETED="false"
if [[ -f "$GUARD_FILE" ]]; then
  GUARD_SESSION_ID=$(jq -r '.session_id // ""' "$GUARD_FILE" 2>/dev/null || echo "")
  GUARD_COMPLETED=$(jq -r '.protocol_completed // false' "$GUARD_FILE" 2>/dev/null || echo "false")
fi

# Detect new session: compare guard's session_id vs state's last_session_id
LAST_SESSION_ID=$(jq -r '._session_state.last_session_id // ""' "$STATE_FILE" 2>/dev/null || echo "")

# New session if guard is empty or matches the last committed session
if [[ -z "$GUARD_SESSION_ID" || "$GUARD_SESSION_ID" == "$LAST_SESSION_ID" ]]; then
  # Generate a fresh session ID for this session
  NEW_SESSION_ID="session-$(date +%Y%m%d-%H%M)"
  printf '{"session_id":"%s","protocol_completed":false,"started_at":"%s"}\n' \
    "$NEW_SESSION_ID" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$GUARD_FILE"
  GUARD_COMPLETED="false"
fi

# If protocol already ran, emit compact WAI essentials (survives /compact)
if [[ "$GUARD_COMPLETED" == "true" ]]; then
  TRACK_PATH=$(jq -r '._session_state.track_path // ""' "$STATE_FILE" 2>/dev/null)

  # Post-compaction recovery: inject once after a compaction event, then clear the flag
  GUARD_COMPACTED=$(jq -r '.compacted // false' "$GUARD_FILE" 2>/dev/null || echo "false")
  if [[ "$GUARD_COMPACTED" == "true" ]]; then
    TMP=$(mktemp)
    jq 'del(.compacted) | del(.compacted_at)' "$GUARD_FILE" > "$TMP" && mv "$TMP" "$GUARD_FILE"
    cat << POST_COMPACT
<wai-post-compact>
WARNING: Context was compacted this session. Skill knowledge may have been lost.

BEFORE closing out: Read templates/commands/wai-closeout.md — do not attempt from memory.
BEFORE any skill: Read templates/commands/wai-{skill}.md — do not reconstruct from context.

State files still intact:
  WAI-Spoke/WAI-State.json — identity, session state, work queue
  WAI-Spoke/lugs/bytype/ — all active lugs
  ${TRACK_PATH} — session track (append every turn)
</wai-post-compact>
POST_COMPACT
  fi

  cat << ESSENTIALS
<wai-essentials>
WAI project: Wheelwright Framework. State: WAI-Spoke/WAI-State.json
Active lugs: WAI-Spoke/lugs/bytype/{type}/{open,in_progress}/*.json
Signals: WAI-Spoke/lugs/bytype/signal/undelivered/*.json
Track: ${TRACK_PATH} (append every turn)

Rules: P1-Persist (save or lose), P2-Verify (check don't assume), P3-Steward (flag drift),
P10-Autonomy (proceed don't pause for safe ops), P11-Lug-First (lugs survive, tasks don't).
Deny: rm -rf /, git push --force. Closeout: /wai-closeout. Status: /wai-status.
Skills: templates/commands/wai-*.md. Read skill file when in doubt.
</wai-essentials>
ESSENTIALS
  exit 0
fi

# Mark protocol as triggered (in runtime file only — WAI-State.json stays clean)
TMP=$(mktemp)
jq '.protocol_completed = true |
    .protocol_last_run = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))' "$GUARD_FILE" > "$TMP" && mv "$TMP" "$GUARD_FILE"

# ── CC Advisor: log hook_fire for user-prompt-submit ─────────────────────────
_CC_LOGS="$PROJECT_DIR/WAI-Spoke/advisors/cc-advisor/logs"
_CC_SESSION=$(jq -r '._session_state.last_session_id // ""' "$STATE_FILE" 2>/dev/null)
_CC_SPOKE=$(jq -r '.wheel.name // "unknown"' "$STATE_FILE" 2>/dev/null)
if [[ -d "$_CC_LOGS" && -n "$_CC_SESSION" ]]; then
  printf '{"ts":"%s","session":"%s","spoke":"%s","event":"hook_fire","data":{"hook_name":"user-prompt-submit","result":"ok","duration_ms":0,"error":null}}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$_CC_SESSION" "$_CC_SPOKE" \
    >> "$_CC_LOGS/hook-events.jsonl"
fi

# Inject wakeup directive — agent follows /wai skill (wai.md), no bash script needed
cat << 'EOF'
<wai-session-start>
CRITICAL: This is your first turn in a new session. Before responding to the user:

1. Run your WAI wakeup protocol by following the /wai skill (templates/commands/wai.md).
   Produce the full WAI Point briefing: project identity, active work, context health, next actions.

2. If briefing shows autosave checkpoints (incomplete work from previous session):
   Ask: Resume [task]? (Green Light to resume / Red Light to inspect / skip)

3. If briefing shows pending teachings in seed/ingest/:
   Prioritize review before other work. Follow (deprecated - auto-discovery on wakeup) skill.

4. Then respond to the user's message.

EXCEPTION: If the user's message is a closeout command ("closeout", "/wai-closeout", "/wai-shipit"),
skip the wakeup briefing entirely and proceed directly to closeout. Do NOT say "Wake complete."
</wai-session-start>
EOF

exit 0

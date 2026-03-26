#!/bin/bash
#
# WAI Session Start Hook
# Runs at Claude Code session start — before first user message.
# Pre-computes wakeup data so Claude doesn't need tool calls for init work.
#
# Outputs: <wai-session-init> block injected into session context
#

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
STATE_FILE="$PROJECT_DIR/WAI-Spoke/WAI-State.json"

# Exit silently if not a WAI project
[[ ! -f "$STATE_FILE" ]] && exit 0

# ── 1. Create session directory ──────────────────────────────────────────────
SESSION_NAME="session-$(date +%Y%m%d-%H%M)"
SESSION_DIR="$PROJECT_DIR/WAI-Spoke/sessions/$SESSION_NAME"
mkdir -p "$SESSION_DIR"
touch "$SESSION_DIR/track.jsonl"

# ── 2. Update WAI-State.json with new session ────────────────────────────────
# NOTE: session_count is incremented at closeout only (not here).
# Agent-initiated sessions must not inflate the count.
TMP=$(mktemp)
jq --arg sid "$SESSION_NAME" \
   '._session_state.last_session_id = $sid |
    ._session_state.track_path = ("WAI-Spoke/sessions/" + $sid + "/track.jsonl")' \
   "$STATE_FILE" > "$TMP" && mv "$TMP" "$STATE_FILE"

# ── 3. Lug scan ──────────────────────────────────────────────────────────────
LUGS_DIR="$PROJECT_DIR/WAI-Spoke/lugs/bytype"

count_lugs() {
  local pattern="$1"
  ls $pattern 2>/dev/null | wc -l | tr -d ' '
}

EPICS_OPEN=$(count_lugs "$LUGS_DIR/epic/open/*.json")
EPICS_IP=$(count_lugs "$LUGS_DIR/epic/in_progress/*.json")
TASKS_OPEN=$(count_lugs "$LUGS_DIR/task/open/*.json")
BUGS_IP=$(count_lugs "$LUGS_DIR/bug/in_progress/*.json")
FEATURES_IP=$(count_lugs "$LUGS_DIR/feature/in_progress/*.json")
OTHER_OPEN=$(count_lugs "$LUGS_DIR/other/open/*.json")
SIGNALS=$(count_lugs "$LUGS_DIR/signal/undelivered/*.json")

# Get epic names (open + in_progress)
EPIC_LIST=$(ls "$LUGS_DIR/epic/open/"*.json "$LUGS_DIR/epic/in_progress/"*.json 2>/dev/null \
  | xargs -I{} basename {} .json 2>/dev/null | sort | head -15 | sed 's/^/  - /' | tr '\n' '\n')

# Get in-progress lug names (non-epic)
IP_LIST=$(ls "$LUGS_DIR/bug/in_progress/"*.json "$LUGS_DIR/feature/in_progress/"*.json 2>/dev/null \
  | xargs -I{} basename {} .json 2>/dev/null | sort | sed 's/^/  - /' | tr '\n' '\n')

# ── 4. Hub + teaching check ───────────────────────────────────────────────────
HUB_PATH=$(jq -r '.wheel.hub_path // ""' "$STATE_FILE" 2>/dev/null)
TEACH_DIR="$HUB_PATH/teachings_repo/framework/current"
PROCESSED_DIR="$PROJECT_DIR/WAI-Spoke/seed/ingest/processed"

HUB_STATUS="MISSING"
TEACH_STATUS="MISSING"
TEACH_TOTAL=0
TEACH_ADOPTED=0
TEACH_NEW=0
NEW_TEACHINGS=""

if [[ -n "$HUB_PATH" && -d "$HUB_PATH" ]]; then
  HUB_STATUS="OK"
  if [[ -d "$TEACH_DIR" ]]; then
    TEACH_STATUS="OK"
    for f in "$TEACH_DIR"/*.teaching; do
      [[ -f "$f" ]] || continue
      TEACH_TOTAL=$((TEACH_TOTAL + 1))
      fname=$(basename "$f")
      if [[ -f "$PROCESSED_DIR/$fname" ]]; then
        TEACH_ADOPTED=$((TEACH_ADOPTED + 1))
      else
        TEACH_NEW=$((TEACH_NEW + 1))
        NEW_TEACHINGS="$NEW_TEACHINGS\n  - $fname"
        # Read safe_to_auto_adopt flag
        AUTO=$(grep -m1 'safe_to_auto_adopt' "$f" 2>/dev/null | grep -c 'true')
        if [[ "$AUTO" -eq 1 ]]; then
          NEW_TEACHINGS="$NEW_TEACHINGS [auto-adoptable]"
        else
          NEW_TEACHINGS="$NEW_TEACHINGS [manual review]"
        fi
      fi
    done
  fi
fi

# ── 5. Hub signals bulletin count ────────────────────────────────────────────
HUB_SIGNALS=0
if [[ -d "$HUB_PATH/WAI-Hub/Signals/incoming" ]]; then
  HUB_SIGNALS=$(ls "$HUB_PATH/WAI-Hub/Signals/incoming/"*.json 2>/dev/null | grep -v '.gitkeep' | wc -l | tr -d ' ')
fi

# ── 6. Next session recommendation ───────────────────────────────────────────
NEXT_REC=$(jq -r '._session_state.next_session_recommendation // "None"' "$STATE_FILE" 2>/dev/null)
SESSION_COUNT=$(jq -r '._session_state.session_count // 0' "$STATE_FILE" 2>/dev/null)

# ── 7. Git status ─────────────────────────────────────────────────────────────
GIT_DIRTY=$(git -C "$PROJECT_DIR" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
GIT_STATUS="clean"
[[ "$GIT_DIRTY" -gt 0 ]] && GIT_STATUS="$GIT_DIRTY file(s) modified"

# ── Output ────────────────────────────────────────────────────────────────────
cat << BRIEF
<wai-session-init>
Session ${SESSION_COUNT} initialized. Track: WAI-Spoke/sessions/${SESSION_NAME}/track.jsonl

ACTIVE WORK
  Epics: ${EPICS_OPEN} open, ${EPICS_IP} in-progress
  Tasks: ${TASKS_OPEN} open | Bugs/Features in-progress: $((BUGS_IP + FEATURES_IP))
  Other open: ${OTHER_OPEN} | Signals undelivered: ${SIGNALS}

EPICS
${EPIC_LIST}
IN-PROGRESS (non-epic)
${IP_LIST}
TEACHINGS
  Hub: ${HUB_STATUS} | Teachings repo: ${TEACH_STATUS}
  Total: ${TEACH_TOTAL} | Adopted: ${TEACH_ADOPTED} | New: ${TEACH_NEW}
$(if [[ $TEACH_NEW -gt 0 ]]; then printf "  New teachings:\n%b" "$NEW_TEACHINGS"; fi)

HUB SIGNALS INBOX: ${HUB_SIGNALS} items

CONTEXT HEALTH
  Git: ${GIT_STATUS}
  Hub path: ${HUB_STATUS}

NEXT ACTIONS (from session $((SESSION_COUNT - 1)))
  ${NEXT_REC}
</wai-session-init>
BRIEF

exit 0

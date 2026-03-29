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
TEACH_DIR="$HUB_PATH/teachings_repo/spoke/current"
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
if [[ -d "$HUB_PATH/WAI-Hub/signals/incoming" ]]; then
  HUB_SIGNALS=$(ls "$HUB_PATH/WAI-Hub/signals/incoming/"*.json 2>/dev/null | grep -v '.gitkeep' | wc -l | tr -d ' ')
fi

# ── 6. Next session recommendation ───────────────────────────────────────────
NEXT_REC=$(jq -r '._session_state.next_session_recommendation // "None"' "$STATE_FILE" 2>/dev/null)
SESSION_COUNT=$(jq -r '._session_state.session_count // 0' "$STATE_FILE" 2>/dev/null)

# ── 7. Git status ─────────────────────────────────────────────────────────────
GIT_DIRTY=$(git -C "$PROJECT_DIR" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
GIT_STATUS="clean"
[[ "$GIT_DIRTY" -gt 0 ]] && GIT_STATUS="$GIT_DIRTY file(s) modified"

# ── 8. CC health check (claude-maximizer trigger) ────────────────────────────
CC_GAPS=""
SETTINGS_FILE="$PROJECT_DIR/.claude/settings.json"
CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"

# Check deny rules
DENY_COUNT=$(jq '.permissions.deny // [] | length' "$SETTINGS_FILE" 2>/dev/null || echo 0)
[[ "$DENY_COUNT" -eq 0 ]] && CC_GAPS="${CC_GAPS}  - No deny rules in .claude/settings.json\n"

# Check CLAUDE.md weight
if [[ -f "$CLAUDE_MD" ]]; then
  CMD_LINES=$(wc -l < "$CLAUDE_MD" | tr -d ' ')
  [[ "$CMD_LINES" -lt 50 ]] && CC_GAPS="${CC_GAPS}  - CLAUDE.md underweight (${CMD_LINES} lines, ideal 50+)\n"
else
  CC_GAPS="${CC_GAPS}  - CLAUDE.md missing\n"
fi

# Check PreToolUse hook
HAS_PRETOOL=$(jq '.hooks.PreToolUse // empty' "$SETTINGS_FILE" 2>/dev/null)
[[ -z "$HAS_PRETOOL" ]] && CC_GAPS="${CC_GAPS}  - No PreToolUse guard hook configured\n"

# Check subagent definitions
AGENTS_DIR="$PROJECT_DIR/.claude/agents"
if [[ ! -d "$AGENTS_DIR" ]] || [[ -z "$(ls -A "$AGENTS_DIR" 2>/dev/null)" ]]; then
  CC_GAPS="${CC_GAPS}  - No subagent definitions in .claude/agents/\n"
fi

# ── 9. Historian advice (latest review) ──────────────────────────────────────
HISTORIAN_ADVICE=""
HISTORIAN_DIR="$PROJECT_DIR/WAI-Spoke/advisors/historian/reviews"
if [[ -d "$HISTORIAN_DIR" ]]; then
  LATEST_REVIEW=$(ls -1 "$HISTORIAN_DIR"/review-*.md 2>/dev/null | sort | tail -1)
  if [[ -n "$LATEST_REVIEW" ]]; then
    # Extract "Advice for Next Session" section
    ADVICE=$(sed -n '/^## Advice for Next Session/,/^## /{ /^## Advice/d; /^## /d; p; }' "$LATEST_REVIEW" 2>/dev/null | head -10)
    if [[ -n "$ADVICE" ]]; then
      REVIEW_DATE=$(basename "$LATEST_REVIEW" .md | sed 's/review-//')
      HISTORIAN_ADVICE="  Historian ($REVIEW_DATE):\n$(echo "$ADVICE" | sed 's/^/    /')"
    fi
  fi
fi

# ── 10. Ozi nightly report (if hub connected) ───────────────────────────────
OZI_NIGHTLY=""
if [[ -n "$HUB_PATH" && -d "$HUB_PATH/WAI-Hub/runtime/ozi-nightly-reports" ]]; then
  # Find most recent report (today or yesterday)
  TODAY=$(date +%Y-%m-%d)
  YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null || echo "")
  REPORT_FILE=""
  [[ -f "$HUB_PATH/WAI-Hub/runtime/ozi-nightly-reports/$TODAY.json" ]] && REPORT_FILE="$HUB_PATH/WAI-Hub/runtime/ozi-nightly-reports/$TODAY.json"
  [[ -z "$REPORT_FILE" && -n "$YESTERDAY" && -f "$HUB_PATH/WAI-Hub/runtime/ozi-nightly-reports/$YESTERDAY.json" ]] && REPORT_FILE="$HUB_PATH/WAI-Hub/runtime/ozi-nightly-reports/$YESTERDAY.json"

  if [[ -n "$REPORT_FILE" ]]; then
    REPORT_DATE=$(jq -r '.date // "unknown"' "$REPORT_FILE" 2>/dev/null)
    FLEET_SCANNED=$(jq -r '.spokes_scanned // 0' "$REPORT_FILE" 2>/dev/null)
    FLEET_GREEN=$(jq -r '.spokes_green // 0' "$REPORT_FILE" 2>/dev/null)
    FLEET_RED=$(jq -r '.spokes_red // 0' "$REPORT_FILE" 2>/dev/null)
    ITEMS_DONE=$(jq -r '.total_items_completed // 0' "$REPORT_FILE" 2>/dev/null)
    ITEMS_FAIL=$(jq -r '.total_items_failed // 0' "$REPORT_FILE" 2>/dev/null)
    TEACHINGS_ADOPTED=$(jq -r '.teachings_adopted // 0' "$REPORT_FILE" 2>/dev/null)

    # This spoke's results
    SPOKE_NAME=$(jq -r '.wheel.name // ""' "$STATE_FILE" 2>/dev/null)
    SPOKE_ITEMS=$(jq -r --arg name "$SPOKE_NAME" '.per_spoke[]? | select(.name == $name) | "\(.items_completed // 0) completed, \(.items_failed // 0) failed"' "$REPORT_FILE" 2>/dev/null)
    [[ -z "$SPOKE_ITEMS" ]] && SPOKE_ITEMS="not included in run"

    OZI_NIGHTLY="  Ozi nightly ($REPORT_DATE): fleet ${FLEET_GREEN}/${FLEET_SCANNED} green"
    [[ "$FLEET_RED" -gt 0 ]] && OZI_NIGHTLY="$OZI_NIGHTLY, ${FLEET_RED} red"
    OZI_NIGHTLY="$OZI_NIGHTLY | ${ITEMS_DONE} items done"
    [[ "$ITEMS_FAIL" -gt 0 ]] && OZI_NIGHTLY="$OZI_NIGHTLY, ${ITEMS_FAIL} failed"
    OZI_NIGHTLY="$OZI_NIGHTLY | teachings: ${TEACHINGS_ADOPTED}"
    OZI_NIGHTLY="$OZI_NIGHTLY\n  This spoke: ${SPOKE_ITEMS}"
  fi
fi

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

$(if [[ -n "$OZI_NIGHTLY" ]]; then printf "OZI NIGHTLY\n%b\n" "$OZI_NIGHTLY"; fi)
$(if [[ -n "$HISTORIAN_ADVICE" ]]; then printf "HISTORIAN ADVICE\n%b\n" "$HISTORIAN_ADVICE"; fi)
CONTEXT HEALTH
  Git: ${GIT_STATUS}
  Hub path: ${HUB_STATUS}
$(if [[ -n "$CC_GAPS" ]]; then printf "\nCC OPTIMIZATION (run /wai-claude-maximizer for details)\n%b" "$CC_GAPS"; fi)
NEXT ACTIONS (from session $((SESSION_COUNT - 1)))
  ${NEXT_REC}
</wai-session-init>
BRIEF

exit 0

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

# Auto-init: if no WAI-State.json but template exists, bootstrap WAI-Spoke/
TEMPLATE_FILE="$PROJECT_DIR/templates/spoke/WAI-State.json.template"
if [[ ! -f "$STATE_FILE" && -f "$TEMPLATE_FILE" ]]; then
  mkdir -p "$PROJECT_DIR/WAI-Spoke"
  cp "$TEMPLATE_FILE" "$STATE_FILE"
  # Create essential directories
  mkdir -p "$PROJECT_DIR/WAI-Spoke/sessions"
  mkdir -p "$PROJECT_DIR/WAI-Spoke/lugs/bytype/epic/open"
  mkdir -p "$PROJECT_DIR/WAI-Spoke/lugs/bytype/task/open"
  mkdir -p "$PROJECT_DIR/WAI-Spoke/lugs/bytype/bug/open"
  mkdir -p "$PROJECT_DIR/WAI-Spoke/lugs/bytype/feature/open"
  mkdir -p "$PROJECT_DIR/WAI-Spoke/lugs/bytype/signal/undelivered"
  mkdir -p "$PROJECT_DIR/WAI-Spoke/lugs/bytype/other/open"
  mkdir -p "$PROJECT_DIR/WAI-Spoke/seed/ingest"
  mkdir -p "$PROJECT_DIR/WAI-Spoke/runtime"
fi

# Exit silently if still no state file (not a WAI project)
[[ ! -f "$STATE_FILE" ]] && exit 0

# ── 1. Create session directory ──────────────────────────────────────────────
SESSION_NAME="session-$(date +%Y%m%d-%H%M)"
SESSION_DIR="$PROJECT_DIR/WAI-Spoke/sessions/$SESSION_NAME"
mkdir -p "$SESSION_DIR"
touch "$SESSION_DIR/track.jsonl"

# ── 1b. Check previous session track integrity ──────────────────────────────
PREV_SESSION_STATUS="FIRST_SESSION"
PREV_SESSION_ID=""
PREV_SESSION=$(ls -1t "$PROJECT_DIR/WAI-Spoke/sessions/" 2>/dev/null | grep -v "^${SESSION_NAME}$" | head -1)
if [[ -n "$PREV_SESSION" ]]; then
  PREV_TRACK="$PROJECT_DIR/WAI-Spoke/sessions/$PREV_SESSION/track.jsonl"
  PREV_SESSION_ID="$PREV_SESSION"
  if [[ -f "$PREV_TRACK" && -s "$PREV_TRACK" ]]; then
    LAST_LINE=$(tail -1 "$PREV_TRACK")
    # CLEAN = completed turn OR explicit closeout event
    if echo "$LAST_LINE" | jq -e '.completed == true or .event == "closeout"' >/dev/null 2>&1; then
      PREV_SESSION_STATUS="CLEAN"
    elif echo "$LAST_LINE" | jq . >/dev/null 2>&1; then
      PREV_SESSION_STATUS="INTERRUPTED"
    else
      PREV_SESSION_STATUS="INTERRUPTED"
    fi
  else
    PREV_SESSION_STATUS="EMPTY"
  fi
fi

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

# ── 7a. Spoke integrity score + parity check ────────────────────────────────
INTEGRITY_SCORE=""
PARITY_STATUS=""
if [[ -f "$PROJECT_DIR/tools/spoke_integrity_score.py" ]]; then
  _SCORE=$(python3 "$PROJECT_DIR/tools/spoke_integrity_score.py" --quiet 2>/dev/null)
  if [[ -n "$_SCORE" ]]; then
    if [[ "$_SCORE" -ge 80 ]]; then
      INTEGRITY_SCORE="  Integrity: ${_SCORE}/100 [HEALTHY]"
    elif [[ "$_SCORE" -ge 50 ]]; then
      INTEGRITY_SCORE="  Integrity: ${_SCORE}/100 [DEGRADED]"
    else
      INTEGRITY_SCORE="  Integrity: ${_SCORE}/100 [CRITICAL]"
    fi
  fi
fi
if [[ -f "$PROJECT_DIR/tools/spoke_parity_check.py" ]]; then
  if python3 "$PROJECT_DIR/tools/spoke_parity_check.py" --quiet 2>/dev/null; then
    PARITY_STATUS="  Parity: at head"
  else
    PARITY_STATUS="  Parity: BEHIND HEAD — run spoke_parity_check.py"
  fi
fi

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

# ── 8b. Skill sync check ─────────────────────────────────────────────────────
SYNC_STATUS="OK"
TEMPLATES_CMDS="$PROJECT_DIR/templates/commands"
CLAUDE_CMDS="$PROJECT_DIR/.claude/commands"
if [[ -d "$TEMPLATES_CMDS" && -d "$CLAUDE_CMDS" ]]; then
  SYNC_OUT_OF_SYNC=""
  for src in "$TEMPLATES_CMDS"/wai*.md; do
    [[ -f "$src" ]] || continue
    fname=$(basename "$src")
    dst="$CLAUDE_CMDS/$fname"
    if [[ ! -f "$dst" ]] || [[ "$src" -nt "$dst" ]]; then
      SYNC_OUT_OF_SYNC="$SYNC_OUT_OF_SYNC $fname"
    fi
  done
  [[ -n "$SYNC_OUT_OF_SYNC" ]] && SYNC_STATUS="⚠ out of sync:$SYNC_OUT_OF_SYNC — run /shipit"
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

# ── 9b. Expediter summary ────────────────────────────────────────────────────
EXPEDITER_SUMMARY=""
EXPEDITER_STATE="$PROJECT_DIR/WAI-Spoke/advisors/expediter/scan_state.json"
if [[ -f "$PROJECT_DIR/tools/spoke_expediter.py" ]]; then
  python3 "$PROJECT_DIR/tools/spoke_expediter.py" --spoke-path "$PROJECT_DIR" >/dev/null 2>&1 || true
fi
if [[ -f "$EXPEDITER_STATE" ]]; then
  EXP_AVG=$(jq -r '.stats.last_quality_avg // "?"' "$EXPEDITER_STATE" 2>/dev/null)
  EXP_QUEUE=$(jq -r '.refinement_queue_size // 0' "$EXPEDITER_STATE" 2>/dev/null)
  EXP_RUN=$(jq -r '.last_run_at // ""' "$EXPEDITER_STATE" 2>/dev/null | cut -c1-10)
  EXPEDITER_SUMMARY="  Expediter: avg ${EXP_AVG}/10 | ${EXP_QUEUE} need refinement | last ${EXP_RUN}"
fi

# ── 9c. Advisor context feed staleness check ─────────────────────────────────
CONTEXT_FEED_STATUS=""
ADVISORS_DIR="$PROJECT_DIR/WAI-Spoke/advisors"
if [[ -d "$ADVISORS_DIR" && -f "$PROJECT_DIR/tools/advisor_context_refresh.py" ]]; then
  STALE_ADVISORS=""
  UNINIT_ADVISORS=""
  NOW_TS=$(date +%s)

  for advisor_dir in "$ADVISORS_DIR"/*/; do
    [[ -f "${advisor_dir}feeds.yaml" ]] || continue
    advisor=$(basename "$advisor_dir")
    context_dir="${advisor_dir}context"

    # Get refresh interval (default 7 days)
    interval=$(python3 -c "
import sys, yaml
try:
    d = yaml.safe_load(open('${advisor_dir}feeds.yaml'))
    print(d.get('refresh_interval_days', 7))
except: print(7)
" 2>/dev/null || echo 7)

    # Find most recent snapshot
    if [[ -d "$context_dir" ]]; then
      latest_snap=$(ls -1t "$context_dir"/snapshot-*.md 2>/dev/null | head -1)
    else
      latest_snap=""
    fi

    if [[ -z "$latest_snap" ]]; then
      UNINIT_ADVISORS="$UNINIT_ADVISORS $advisor"
    else
      snap_ts=$(date -r "$latest_snap" +%s 2>/dev/null || echo 0)
      age_days=$(( (NOW_TS - snap_ts) / 86400 ))
      if [[ "$age_days" -gt "$interval" ]]; then
        STALE_ADVISORS="$STALE_ADVISORS ${advisor}[${age_days}d]"
      fi
    fi
  done

  # Auto-init uninit advisors in background
  if [[ -n "$UNINIT_ADVISORS" ]]; then
    mkdir -p "$HOME/.claude/logs"
    python3 "$PROJECT_DIR/tools/advisor_context_refresh.py" \
      --init --quiet --spoke-path "$PROJECT_DIR" \
      >> "$HOME/.claude/logs/context-refresh-$(date +%Y%m%d).log" 2>&1 &
    UNINIT_COUNT=$(echo $UNINIT_ADVISORS | wc -w | tr -d ' ')
    CONTEXT_FEED_STATUS="  Context feeds: ${UNINIT_COUNT} initializing in background (${UNINIT_ADVISORS# })"
  elif [[ -n "$STALE_ADVISORS" ]]; then
    STALE_COUNT=$(echo $STALE_ADVISORS | wc -w | tr -d ' ')
    CONTEXT_FEED_STATUS="  Context feeds: ${STALE_COUNT} stale — run: python3 tools/advisor_context_refresh.py"
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

# ── CC Advisor: session counter + session_start event ────────────────────────
CC_ADVISOR_STATE="$PROJECT_DIR/WAI-Spoke/advisors/cc-advisor/scan_state.json"
CC_ADVISOR_LOGS="$PROJECT_DIR/WAI-Spoke/advisors/cc-advisor/logs"

if [[ -f "$CC_ADVISOR_STATE" ]]; then
  # Increment sessions_since_last_audit
  TMP_CC=$(mktemp)
  jq '.sessions_since_last_audit = (.sessions_since_last_audit // 0) + 1 |
      if .sessions_since_last_audit >= 10 then .audit_pending = true else . end' \
    "$CC_ADVISOR_STATE" > "$TMP_CC" && mv "$TMP_CC" "$CC_ADVISOR_STATE"

  # Log session_start event
  mkdir -p "$CC_ADVISOR_LOGS"
  SPOKE_NAME=$(jq -r '.wheel.name // "unknown"' "$STATE_FILE" 2>/dev/null)
  printf '{"ts":"%s","session":"%s","spoke":"%s","event":"session_start","data":{}}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "${SESSION_NAME}" \
    "${SPOKE_NAME}" \
    >> "$CC_ADVISOR_LOGS/session-events.jsonl"

  # Log hook_fire for session-start itself
  printf '{"ts":"%s","session":"%s","spoke":"%s","event":"hook_fire","data":{"hook_name":"session-start","result":"ok","duration_ms":0,"error":null}}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "${SESSION_NAME}" \
    "${SPOKE_NAME}" \
    >> "$CC_ADVISOR_LOGS/hook-events.jsonl"
fi

# ── CC Advisor: surface pending proposals/regressions ────────────────────────
CC_ADVISOR_PENDING=""
if [[ -f "$CC_ADVISOR_STATE" ]]; then
  AUDIT_PENDING=$(jq -r '.audit_pending // false' "$CC_ADVISOR_STATE" 2>/dev/null)
  PENDING_PROPOSALS=$(jq -r '.pending_proposals | length' "$CC_ADVISOR_STATE" 2>/dev/null || echo 0)
  REGRESSION_COUNT=$(grep -c '"status":"watching"' "$PROJECT_DIR/WAI-Spoke/advisors/cc-advisor/vectors.jsonl" 2>/dev/null || echo 0)

  [[ "$AUDIT_PENDING" == "true" ]] && CC_ADVISOR_PENDING="  ⚠ CC Audit due (10 sessions reached) — run /cc-advisor"
  [[ "$PENDING_PROPOSALS" -gt 0 ]] && CC_ADVISOR_PENDING="${CC_ADVISOR_PENDING}\n  ⚠ CC: ${PENDING_PROPOSALS} proposal(s) pending approval — see advisors/cc-advisor/reports/"
  [[ "$REGRESSION_COUNT" -gt 0 ]] && CC_ADVISOR_PENDING="${CC_ADVISOR_PENDING}\n  ⚠ CC: ${REGRESSION_COUNT} regression vector(s) watching — run /cc-advisor for details"
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
  Prev session: ${PREV_SESSION_STATUS}$(if [[ -n "$PREV_SESSION_ID" ]]; then echo " (${PREV_SESSION_ID})"; fi)$(if [[ "$PREV_SESSION_STATUS" == "INTERRUPTED" ]]; then echo " ⚠ recovery options at wakeup"; fi)
$(if [[ -n "$INTEGRITY_SCORE" ]]; then echo "$INTEGRITY_SCORE"; fi)
$(if [[ -n "$PARITY_STATUS" ]]; then echo "$PARITY_STATUS"; fi)
  Sync: ${SYNC_STATUS}
$(if [[ -n "$EXPEDITER_SUMMARY" ]]; then echo "$EXPEDITER_SUMMARY"; fi)
$(if [[ -n "$CONTEXT_FEED_STATUS" ]]; then echo "$CONTEXT_FEED_STATUS"; fi)
$(if [[ -n "$CC_GAPS" ]]; then printf "\nCC OPTIMIZATION (run /wai-claude-maximizer for details)\n%b" "$CC_GAPS"; fi)
NEXT ACTIONS (from session $((SESSION_COUNT - 1)))
  ${NEXT_REC}
$(if [[ -n "$CC_ADVISOR_PENDING" ]]; then printf "\nCC ADVISOR\n%b\n" "$CC_ADVISOR_PENDING"; fi)
</wai-session-init>
BRIEF

exit 0

#!/bin/bash
#
# CC Advisor — Full Audit Pass
# Scores 8 CC configuration areas, appends to passes.jsonl, detects regressions.
#
# Usage: bash run-audit.sh [project_dir]
#

PROJECT_DIR="${1:-${CLAUDE_PROJECT_DIR:-.}}"
ADVISOR_DIR="$PROJECT_DIR/WAI-Spoke/advisors/cc-advisor"
STATE_FILE="$PROJECT_DIR/WAI-Spoke/WAI-State.json"
SETTINGS_FILE="$PROJECT_DIR/.claude/settings.json"
CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"
AGENTS_DIR="$PROJECT_DIR/.claude/agents"
COMMANDS_DIR="$PROJECT_DIR/.claude/commands"
GLOBAL_SETTINGS="$HOME/.claude/settings.json"

[[ ! -d "$ADVISOR_DIR" ]] && echo "ERROR: advisor dir not found: $ADVISOR_DIR" >&2 && exit 1
[[ ! -f "$SETTINGS_FILE" ]] && echo "ERROR: settings.json not found: $SETTINGS_FILE" >&2 && exit 1

PASS_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
PASS_DATE=$(date -u +%Y%m%d)
SESSION_ID=$(jq -r '._session_state.last_session_id // "unknown"' "$STATE_FILE" 2>/dev/null)
SPOKE_NAME=$(jq -r '.wheel.name // "unknown"' "$STATE_FILE" 2>/dev/null)
SESSION_COUNT=$(jq -r '._session_state.session_count // 0' "$STATE_FILE" 2>/dev/null)

# ── 1. CLAUDE.md ──────────────────────────────────────────────────────────────
score_claudemd="fail"
if [[ -f "$CLAUDE_MD" ]]; then
  LINES=$(wc -l < "$CLAUDE_MD" | tr -d ' ')
  HAS_STACK=$(grep -c "Stack:" "$CLAUDE_MD" 2>/dev/null || echo 0)
  HAS_ANTIPATTERNS=$(grep -c "Anti-Patterns\|Anti-patterns" "$CLAUDE_MD" 2>/dev/null || echo 0)
  HAS_WORKFLOW=$(grep -c "Workflow\|workflow" "$CLAUDE_MD" 2>/dev/null || echo 0)
  if [[ "$LINES" -ge 50 && "$HAS_STACK" -ge 1 && "$HAS_ANTIPATTERNS" -ge 1 ]]; then
    score_claudemd="pass"
  fi
fi

# ── 2. Hooks ──────────────────────────────────────────────────────────────────
score_hooks="fail"
HAS_SESSION_START=$(jq '.hooks.SessionStart // empty' "$SETTINGS_FILE" 2>/dev/null)
HAS_USER_PROMPT=$(jq '.hooks.UserPromptSubmit // empty' "$SETTINGS_FILE" 2>/dev/null)
HAS_PRE_TOOL=$(jq '.hooks.PreToolUse // empty' "$SETTINGS_FILE" 2>/dev/null)
if [[ -n "$HAS_SESSION_START" && -n "$HAS_USER_PROMPT" && -n "$HAS_PRE_TOOL" ]]; then
  score_hooks="pass"
fi

# ── 3. Permissions ────────────────────────────────────────────────────────────
score_permissions="fail"
DENY_COUNT=$(jq '.permissions.deny // [] | length' "$SETTINGS_FILE" 2>/dev/null || echo 0)
ALLOW_COUNT=$(jq '.permissions.allow // [] | length' "$SETTINGS_FILE" 2>/dev/null || echo 0)
if [[ "$DENY_COUNT" -gt 0 && "$ALLOW_COUNT" -gt 0 ]]; then
  score_permissions="pass"
fi

# ── 4. Statusline ─────────────────────────────────────────────────────────────
score_statusline="fail"
if [[ -f "$GLOBAL_SETTINGS" ]]; then
  HAS_STATUS=$(jq '.statusLine // empty' "$GLOBAL_SETTINGS" 2>/dev/null)
  [[ -n "$HAS_STATUS" ]] && score_statusline="pass"
fi

# ── 5. Slash Commands ─────────────────────────────────────────────────────────
score_slash="fail"
if [[ -d "$COMMANDS_DIR" ]]; then
  CMD_COUNT=$(ls "$COMMANDS_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
  HAS_WAI=$(ls "$COMMANDS_DIR"/wai*.md 2>/dev/null | wc -l | tr -d ' ')
  [[ "$CMD_COUNT" -ge 3 && "$HAS_WAI" -ge 1 ]] && score_slash="pass"
fi

# ── 6. Subagents ──────────────────────────────────────────────────────────────
score_subagents="fail"
if [[ -d "$AGENTS_DIR" ]]; then
  AGENT_COUNT=$(ls "$AGENTS_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
  [[ "$AGENT_COUNT" -ge 1 ]] && score_subagents="pass"
fi

# ── 7. MCP Servers ────────────────────────────────────────────────────────────
score_mcp="fail"
MCP_FILE="$PROJECT_DIR/.mcp.json"
[[ -f "$MCP_FILE" ]] && score_mcp="pass"

# ── 8. Git Worktrees ──────────────────────────────────────────────────────────
score_worktrees="fail"
WORKTREE_COUNT=$(git -C "$PROJECT_DIR" worktree list 2>/dev/null | wc -l | tr -d ' ')
[[ "$WORKTREE_COUNT" -gt 1 ]] && score_worktrees="pass"

# ── Score ─────────────────────────────────────────────────────────────────────
SCORE=0
declare -a FINDINGS=()

count_pass() { [[ "$1" == "pass" ]] && echo 1 || echo 0; }
SCORE=$(( $(count_pass "$score_claudemd") + $(count_pass "$score_hooks") + \
          $(count_pass "$score_permissions") + $(count_pass "$score_statusline") + \
          $(count_pass "$score_slash") + $(count_pass "$score_subagents") + \
          $(count_pass "$score_mcp") + $(count_pass "$score_worktrees") ))

[[ "$score_claudemd" == "fail" ]]    && FINDINGS+=("CLAUDE.md incomplete or underweight")
[[ "$score_hooks" == "fail" ]]       && FINDINGS+=("Missing required hooks (SessionStart/UserPromptSubmit/PreToolUse)")
[[ "$score_permissions" == "fail" ]] && FINDINGS+=("Missing allow or deny rules in settings.json")
[[ "$score_statusline" == "fail" ]]  && FINDINGS+=("Statusline not configured in ~/.claude/settings.json")
[[ "$score_slash" == "fail" ]]       && FINDINGS+=("Insufficient slash commands (<3 or no WAI commands)")
[[ "$score_subagents" == "fail" ]]   && FINDINGS+=("No subagent definitions in .claude/agents/")
[[ "$score_mcp" == "fail" ]]         && FINDINGS+=("No .mcp.json found")
[[ "$score_worktrees" == "fail" ]]   && FINDINGS+=("No git worktrees configured")

# ── Previous score for delta ──────────────────────────────────────────────────
PREV_SCORE=$(jq -r '.current_score // null' "$ADVISOR_DIR/scan_state.json" 2>/dev/null)
DELTA=0
if [[ "$PREV_SCORE" != "null" && -n "$PREV_SCORE" ]]; then
  DELTA=$(( SCORE - PREV_SCORE ))
fi

# ── Build findings JSON array ─────────────────────────────────────────────────
FINDINGS_JSON=$(printf '%s\n' "${FINDINGS[@]}" | jq -R . | jq -cs .)

# ── Append to passes.jsonl ────────────────────────────────────────────────────
printf '{"id":"pass-%s","ts":"%s","session":"%s","spoke":"%s","score":%d,"score_by_area":{"CLAUDE.md":"%s","Hooks":"%s","Permissions":"%s","Statusline":"%s","Slash_Commands":"%s","Subagents":"%s","MCP_Servers":"%s","Git_Worktrees":"%s"},"score_delta":%d,"findings":%s,"proposals_generated":0,"auto_applied":0,"session_count_at_audit":%s}\n' \
  "$PASS_DATE" "$PASS_TS" "$SESSION_ID" "$SPOKE_NAME" \
  "$SCORE" \
  "$score_claudemd" "$score_hooks" "$score_permissions" "$score_statusline" \
  "$score_slash" "$score_subagents" "$score_mcp" "$score_worktrees" \
  "$DELTA" "$FINDINGS_JSON" "$SESSION_COUNT" \
  >> "$ADVISOR_DIR/passes.jsonl"

# ── Regression detection → vectors.jsonl ─────────────────────────────────────
if [[ "$DELTA" -lt 0 ]]; then
  VECTOR_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  VECTOR_ID="vector-${PASS_DATE}-regression"
  # Check if same-day vector already exists
  if ! grep -q "\"id\":\"${VECTOR_ID}\"" "$ADVISOR_DIR/vectors.jsonl" 2>/dev/null; then
    printf '{"id":"%s","pattern_type":"regression","description":"Score dropped %d (from %s to %d) in session %s","first_seen":"%s","last_seen":"%s","occurrences":1,"status":"watching","resolution":null}\n' \
      "$VECTOR_ID" "$DELTA" "$PREV_SCORE" "$SCORE" "$SESSION_ID" \
      "$VECTOR_TS" "$VECTOR_TS" \
      >> "$ADVISOR_DIR/vectors.jsonl"
  fi
fi

# ── Update scan_state.json ────────────────────────────────────────────────────
TMP_STATE=$(mktemp)
jq --arg ts "$PASS_TS" \
   --arg sid "$SESSION_ID" \
   --argjson score "$SCORE" \
   --argjson delta "$DELTA" \
   --arg cm "$score_claudemd" \
   --arg hk "$score_hooks" \
   --arg pm "$score_permissions" \
   --arg sl "$score_statusline" \
   --arg sc "$score_slash" \
   --arg sa "$score_subagents" \
   --arg mc "$score_mcp" \
   --arg wt "$score_worktrees" \
   '.last_audit_at = $ts |
    .last_audit_session = $sid |
    .current_score = $score |
    .score_by_area = {"CLAUDE.md": $cm, "Hooks": $hk, "Permissions": $pm, "Statusline": $sl, "Slash_Commands": $sc, "Subagents": $sa, "MCP_Servers": $mc, "Git_Worktrees": $wt} |
    .sessions_since_last_audit = 0 |
    .audit_pending = false |
    .total_audits = (.total_audits // 0) + 1' \
  "$ADVISOR_DIR/scan_state.json" > "$TMP_STATE" && mv "$TMP_STATE" "$ADVISOR_DIR/scan_state.json"

# ── Phase 4: Permission friction analysis + safe auto-apply ──────────────────
PERM_LOGS="$ADVISOR_DIR/logs/permission-prompts.jsonl"
AUTO_APPLY_LOG="$ADVISOR_DIR/logs/auto-apply.jsonl"
AUTO_APPLIED_THIS_RUN=0

if [[ -f "$PERM_LOGS" && -s "$PERM_LOGS" ]]; then
  # Count unique commands prompted, grouped by command text
  # A command is auto-apply candidate if: prompted in 3+ distinct sessions, read-only
  READONLY_VERBS="cat|ls|find|head|tail|wc|grep|diff|git log|git status|git diff|git show|echo|pwd|date|which|test"

  # Build per-command session counts from JSONL
  CANDIDATES=$(python3 -c "
import json, sys, re, collections
logs = []
try:
    for line in open('$PERM_LOGS'):
        line = line.strip()
        if line:
            logs.append(json.loads(line))
except: pass

# Group by command, count unique sessions
cmd_sessions = collections.defaultdict(set)
cmd_verbs = {}
for e in logs:
    cmd = e.get('data', {}).get('command', '')
    verb = e.get('data', {}).get('verb', '') or cmd.split()[0] if cmd else ''
    session = e.get('session', '')
    cmd_sessions[cmd].add(session)
    cmd_verbs[cmd] = verb

readonly_pattern = re.compile(r'^(cat|ls|find|head|tail|wc|grep|diff|git log|git status|git diff|git show|echo|pwd|date|which|test)\b', re.IGNORECASE)
for cmd, sessions in cmd_sessions.items():
    if len(sessions) >= 3:
        verb = cmd_verbs.get(cmd, '')
        if readonly_pattern.match(cmd.strip()):
            print(cmd)
" 2>/dev/null || true)

  if [[ -n "$CANDIDATES" ]]; then
    SETTINGS_TMP=$(mktemp)
    while IFS= read -r cmd; do
      [[ -z "$cmd" ]] && continue
      # Check not already in allow list
      ALREADY=$(jq --arg c "$cmd" '.permissions.allow // [] | map(select(. == ("Bash(" + $c + ")"))) | length' "$SETTINGS_FILE" 2>/dev/null || echo 0)
      if [[ "$ALREADY" -eq 0 ]]; then
        jq --arg c "Bash($cmd)" '.permissions.allow += [$c]' "$SETTINGS_FILE" > "$SETTINGS_TMP" && mv "$SETTINGS_TMP" "$SETTINGS_FILE"
        printf '{"ts":"%s","session":"%s","command":"%s","reason":"read-only command prompted 3+ sessions"}\n' \
          "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$SESSION_ID" "$cmd" \
          >> "$AUTO_APPLY_LOG"
        AUTO_APPLIED_THIS_RUN=$(( AUTO_APPLIED_THIS_RUN + 1 ))
        echo "  AUTO-APPLIED: Added 'Bash($cmd)' to permissions.allow (prompted 3+ sessions, read-only)"
      fi
    done <<< "$CANDIDATES"

    if [[ "$AUTO_APPLIED_THIS_RUN" -gt 0 ]]; then
      TMP_STATE2=$(mktemp)
      jq --argjson n "$AUTO_APPLIED_THIS_RUN" '.auto_applied_count = (.auto_applied_count // 0) + $n' \
        "$ADVISOR_DIR/scan_state.json" > "$TMP_STATE2" && mv "$TMP_STATE2" "$ADVISOR_DIR/scan_state.json"
    fi
  fi
fi

# ── Phase 4: CLAUDE.md proposal generation ───────────────────────────────────
REPORTS_DIR="$ADVISOR_DIR/reports"
mkdir -p "$REPORTS_DIR"
PROPOSALS_GENERATED=0

if [[ "$score_claudemd" == "fail" && -f "$CLAUDE_MD" ]]; then
  PROPOSAL_FILE="$REPORTS_DIR/proposal-${PASS_DATE}-claude-md.md"
  if [[ ! -f "$PROPOSAL_FILE" ]]; then
    LINES=$(wc -l < "$CLAUDE_MD" | tr -d ' ')
    cat > "$PROPOSAL_FILE" << PROPOSAL
# CC Advisor Proposal: CLAUDE.md Gap

**Generated:** ${PASS_TS}
**Session:** ${SESSION_ID}
**Area:** CLAUDE.md
**Gap:** CLAUDE.md incomplete — ${LINES} lines (ideal 50+), missing required blocks

## Proposed Changes

The following blocks should be added or completed in \`CLAUDE.md\`:

$([ "$LINES" -lt 50 ] && echo "- **Expand content** — file has only ${LINES} lines, needs 50+ for full effectiveness")
$(grep -qc "Stack:" "$CLAUDE_MD" 2>/dev/null || echo "- **Add Stack block** — declare technology stack for consistent tool choices")
$(grep -qc "Anti-Patterns\|Anti-patterns" "$CLAUDE_MD" 2>/dev/null || echo "- **Add Anti-Patterns block** — document what Claude has done wrong in this project")
$(grep -qc "Workflow\|workflow" "$CLAUDE_MD" 2>/dev/null || echo "- **Add Development Workflow block** — ordered build/test/lint commands")

## Why

Without these blocks, Claude defaults to generic behavior. CLAUDE.md is the primary
mechanism for persistent project knowledge across sessions.

## Apply

Review this proposal, edit CLAUDE.md manually, then delete this file.

**Requires user approval before applying.**
PROPOSAL
    PROPOSALS_GENERATED=$(( PROPOSALS_GENERATED + 1 ))

    # Update pending_proposals in scan_state.json
    TMP_STATE3=$(mktemp)
    jq --arg pid "proposal-${PASS_DATE}-claude-md" \
      '.pending_proposals = (.pending_proposals // []) + [$pid]' \
      "$ADVISOR_DIR/scan_state.json" > "$TMP_STATE3" && mv "$TMP_STATE3" "$ADVISOR_DIR/scan_state.json"
  fi
fi

# Update passes.jsonl proposals_generated count (patch last line)
if [[ "$PROPOSALS_GENERATED" -gt 0 || "$AUTO_APPLIED_THIS_RUN" -gt 0 ]]; then
  LAST_LINE=$(tail -1 "$ADVISOR_DIR/passes.jsonl")
  UPDATED_LINE=$(echo "$LAST_LINE" | jq --argjson p "$PROPOSALS_GENERATED" --argjson a "$AUTO_APPLIED_THIS_RUN" \
    '.proposals_generated = $p | .auto_applied = $a')
  # Replace last line
  TMP_PASSES=$(mktemp)
  head -n -1 "$ADVISOR_DIR/passes.jsonl" > "$TMP_PASSES"
  echo "$UPDATED_LINE" >> "$TMP_PASSES"
  mv "$TMP_PASSES" "$ADVISOR_DIR/passes.jsonl"
fi

# ── Phase 4: Signal emission for hub-worthy findings ─────────────────────────
LUGS_DIR="$PROJECT_DIR/WAI-Spoke/lugs/bytype/signal/undelivered"
if [[ "$DELTA" -le -2 ]]; then
  # Significant regression — emit signal
  SIG_ID="signal-cc-regression-${PASS_DATE}"
  SIG_FILE="$LUGS_DIR/${SIG_ID}.json"
  if [[ ! -f "$SIG_FILE" ]] && mkdir -p "$LUGS_DIR"; then
    cat > "$SIG_FILE" << SIGNAL
{"i":"${SIG_ID}","ty":"signal","t":"CC Advisor: Score regression detected — dropped ${DELTA} to ${SCORE}/8","s":"o","ca":"${PASS_TS}","gb":"cc-advisor","impact":8,"description":"CC configuration score dropped ${DELTA} points (to ${SCORE}/8) in session ${SESSION_ID}. Findings: $(echo "${FINDINGS[@]}" | tr '\n' '; ')","tags":["cc-advisor","regression"],"session":"${SESSION_ID}","spoke":"${SPOKE_NAME}"}
SIGNAL
    echo "  SIGNAL: Emitted cc-regression signal (impact=8) for hub delivery"
  fi
fi

# ── Output ────────────────────────────────────────────────────────────────────
echo "CC Advisor Audit — Score: ${SCORE}/8 (delta: ${DELTA})"
for f in "${FINDINGS[@]}"; do echo "  FAIL: $f"; done
[[ "${#FINDINGS[@]}" -eq 0 ]] && echo "  All 8 areas passing."

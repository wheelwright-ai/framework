#!/bin/bash
#
# wai-enter.sh — WAI pre-tool launch wrapper (hub-aware)
#
# Auto-detects hub vs spoke and runs appropriate prep steps.
# Hub detection: WAI-Hub/ directory present
# Spoke detection: WAI-Spoke/WAI-State.json present
#
# Usage:
#   ./wai-enter.sh           # launches claude (default)
#   ./wai-enter.sh gemini    # launches gemini
#   ./wai-enter.sh codex     # launches codex
#

PROJECT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"

# ── Detect project type ──────────────────────────────────────────────────────
IS_HUB=false
IS_SPOKE=false
[[ -d "$PROJECT_DIR/WAI-Hub" ]] && IS_HUB=true
[[ -f "$PROJECT_DIR/WAI-Spoke/WAI-State.json" ]] && IS_SPOKE=true

# Not a WAI project? Launch tool directly
if [[ "$IS_HUB" == "false" && "$IS_SPOKE" == "false" ]]; then
    exec "${1:-claude}"
fi

echo "[wai-enter] Preparing session..."
[[ "$IS_HUB" == "true" ]] && echo "[wai-enter] Mode: hub"

# ── 1. Generate fresh wakeup brief ──────────────────────────────────────────
if [[ "$IS_HUB" == "true" && -f "$PROJECT_DIR/tools/octo_brief.py" ]]; then
    if python3 "$PROJECT_DIR/tools/octo_brief.py" 2>/dev/null; then
        echo "[wai-enter] Brief: ready (octo)"
    else
        echo "[wai-enter] Brief: octo generation failed — wakeup will use live scan"
    fi
elif [[ -f "$PROJECT_DIR/tools/generate_wakeup_brief.py" ]]; then
    if python3 "$PROJECT_DIR/tools/generate_wakeup_brief.py"; then
        echo "[wai-enter] Brief: ready"
    else
        echo "[wai-enter] Brief: generation failed — wakeup will use live scan"
    fi
else
    echo "[wai-enter] Brief: generator not found — wakeup will use live scan"
fi

# ── 2. Refresh stale context feeds in background ────────────────────────────
if [[ "$IS_HUB" == "true" && -f "$PROJECT_DIR/tools/hub_context_refresh.py" ]]; then
    mkdir -p "$HOME/.claude/logs"
    python3 "$PROJECT_DIR/tools/hub_context_refresh.py" \
        --quiet \
        >> "$HOME/.claude/logs/hub-context-refresh-$(date +%Y%m%d).log" 2>&1 &
    echo "[wai-enter] Feeds: hub refresh running in background"
else
    EXPEDITER_STATE="$PROJECT_DIR/WAI-Spoke/advisors/expediter/scan_state.json"
    if [[ -f "$EXPEDITER_STATE" && -f "$PROJECT_DIR/tools/advisor_context_refresh.py" ]]; then
        LAST_RUN=$(python3 -c "
import json
try:
    s = json.load(open('$EXPEDITER_STATE'))
    print(s.get('last_run_at','')[:10])
except:
    print('')
" 2>/dev/null || echo "")
        TODAY=$(date +%Y-%m-%d)
        if [[ -n "$LAST_RUN" && "$LAST_RUN" != "$TODAY" ]]; then
            mkdir -p "$HOME/.claude/logs"
            python3 "$PROJECT_DIR/tools/advisor_context_refresh.py" \
                --quiet --spoke-path "$PROJECT_DIR" \
                >> "$HOME/.claude/logs/context-refresh-$(date +%Y%m%d).log" 2>&1 &
            echo "[wai-enter] Feeds: refreshing in background (last: $LAST_RUN)"
        fi
    fi
fi

# ── 3. Hub: check outbox for pending deliveries ──────────────────────────────
if [[ "$IS_HUB" == "true" ]]; then
    OUTBOX="$PROJECT_DIR/WAI-Hub/outbox"
    if [[ -d "$OUTBOX" ]]; then
        PENDING=$(find "$OUTBOX" -mindepth 2 -maxdepth 2 -name "*.json" 2>/dev/null | wc -l)
        [[ "$PENDING" -gt 0 ]] && echo "[wai-enter] Outbox: $PENDING pending deliveries"
    fi
fi

# ── 3. Spoke: run basher doctor audit if available ───────────────────────────
if [[ "$IS_HUB" == "false" ]] && command -v basher >/dev/null 2>&1; then
    BASHER_OUT=$(basher doctor audit 2>&1) || true
    BASHER_EXIT=$?
    if [[ $BASHER_EXIT -ne 0 ]] || echo "$BASHER_OUT" | grep -qiE 'fixed|changed|updated|repaired'; then
        mkdir -p "$PROJECT_DIR/WAI-Spoke/runtime"
        python3 -c "
import json, datetime
result = {
    'run_at': datetime.datetime.now().isoformat(),
    'output': '''$BASHER_OUT'''[:500],
    'exit_code': $BASHER_EXIT,
    'changes_detected': True
}
with open('$PROJECT_DIR/WAI-Spoke/runtime/basher-audit-result.json', 'w') as f:
    json.dump(result, f, indent=2)
" 2>/dev/null || true
        echo "[wai-enter] Basher: config changes detected — see wakeup blurb"
    else
        echo "[wai-enter] Basher: OK"
    fi
fi

# ── 4. Spoke: detect anomalies outside WAI-Spoke/ (read-only) ───────────────
if [[ "$IS_HUB" == "false" ]]; then
    ANOMALIES=0

    for d in "$PROJECT_DIR"/session-*/; do
        [[ -d "$d" ]] || continue
        NAME=$(basename "$d")
        TS=$(date +%s)
        python3 -c "
import json, datetime
lug = {
    'id': 'signal-pre-wrapper-anomaly-${TS}-v1',
    'type': 'signal',
    'status': 'undelivered',
    'title': 'Anomaly: session dir at project root: $NAME',
    'source': 'pre-wrapper-scan',
    'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'description': 'Found $d outside WAI-Spoke/sessions/. Likely misplaced. Verify and move or delete.'
}
import os; os.makedirs('$PROJECT_DIR/WAI-Spoke/lugs/bytype/signal/undelivered', exist_ok=True)
with open('$PROJECT_DIR/WAI-Spoke/lugs/bytype/signal/undelivered/signal-pre-wrapper-anomaly-${TS}-v1.json', 'w') as f:
    json.dump(lug, f, indent=2)
" 2>/dev/null && ANOMALIES=$((ANOMALIES + 1))
    done

    if [[ -f "$PROJECT_DIR/track.jsonl" ]]; then
        TS=$(date +%s)
        python3 -c "
import json, datetime
lug = {
    'id': 'signal-pre-wrapper-anomaly-${TS}-v1',
    'type': 'signal',
    'status': 'undelivered',
    'title': 'Anomaly: track.jsonl found at project root',
    'source': 'pre-wrapper-scan',
    'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'description': 'Found track.jsonl at $PROJECT_DIR root — should be under WAI-Spoke/sessions/.'
}
import os; os.makedirs('$PROJECT_DIR/WAI-Spoke/lugs/bytype/signal/undelivered', exist_ok=True)
with open('$PROJECT_DIR/WAI-Spoke/lugs/bytype/signal/undelivered/signal-pre-wrapper-anomaly-${TS}-v1.json', 'w') as f:
    json.dump(lug, f, indent=2)
" 2>/dev/null && ANOMALIES=$((ANOMALIES + 1))
    fi

    [[ $ANOMALIES -gt 0 ]] && echo "[wai-enter] Anomalies: $ANOMALIES signal lug(s) created — handle at wakeup"
fi

# ── 5. Auto-fix inside WAI-Spoke/ only ──────────────────────────────────────
mkdir -p "$PROJECT_DIR/WAI-Spoke/runtime"

for d in "$PROJECT_DIR/WAI-Spoke/session-"*/; do
    [[ -d "$d" ]] || continue
    NAME=$(basename "$d")
    mkdir -p "$PROJECT_DIR/WAI-Spoke/sessions"
    mv "$d" "$PROJECT_DIR/WAI-Spoke/sessions/$NAME" 2>/dev/null \
        && echo "[wai-enter] Fixed: moved $NAME → WAI-Spoke/sessions/"
done

if [[ -d "$PROJECT_DIR/.claude/hooks" ]]; then
    chmod +x "$PROJECT_DIR/.claude/hooks/"*.sh 2>/dev/null || true
fi

# ── 6. Launch tool ──────────────────────────────────────────────────────────
TOOL="${1:-}"
if [[ -z "$TOOL" ]]; then
    read -r -p "[wai-enter] Tool to launch (claude/gemini/codex): " TOOL
fi

if ! command -v "$TOOL" >/dev/null 2>&1; then
    echo "[wai-enter] ERROR: tool '$TOOL' not found in PATH"
    exit 1
fi

echo "[wai-enter] Launching $TOOL..."
"$TOOL"

# ── 7. Post-exit: regenerate brief for next session ─────────────────────────
if [[ -f "$PROJECT_DIR/wai-exit.sh" ]]; then
    "$PROJECT_DIR/wai-exit.sh"
fi

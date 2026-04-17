#!/bin/bash
#
# wai-exit.sh — WAI post-tool wrapper (hub-aware)
#
# Runs after the AI tool exits. Regenerates the wakeup brief so the next
# wai-enter.sh always finds a fresh brief regardless of how the session ended.
#
# Hub detection: WAI-Hub/ directory present
# Spoke detection: WAI-Spoke/WAI-State.json present
#
# Called automatically by wai-enter.sh. Can also be run manually.
#
# Usage:
#   ./wai-exit.sh
#

PROJECT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"

# ── Detect project type ──────────────────────────────────────────────────────
IS_HUB=false
[[ -d "$PROJECT_DIR/WAI-Hub" ]] && IS_HUB=true

# Silent no-op if not a WAI project
if [[ "$IS_HUB" == "false" && ! -f "$PROJECT_DIR/WAI-Spoke/WAI-State.json" ]]; then
    exit 0
fi

echo "[wai-exit] Closing session..."

# ── 1. Regenerate brief for next session ────────────────────────────────────
if [[ "$IS_HUB" == "true" && -f "$PROJECT_DIR/tools/octo_brief.py" ]]; then
    if python3 "$PROJECT_DIR/tools/octo_brief.py" 2>/dev/null; then
        echo "[wai-exit] Brief: ready for next session (octo)"
    else
        echo "[wai-exit] Brief: octo generation failed"
    fi
elif [[ -f "$PROJECT_DIR/tools/generate_wakeup_brief.py" ]]; then
    if python3 "$PROJECT_DIR/tools/generate_wakeup_brief.py"; then
        echo "[wai-exit] Brief: ready for next session"
    else
        echo "[wai-exit] Brief: generation failed"
    fi
else
    echo "[wai-exit] Brief: generator not found — skipping"
fi

# ── 2. Refresh context feeds in background ──────────────────────────────────
if [[ "$IS_HUB" == "true" && -f "$PROJECT_DIR/tools/hub_context_refresh.py" ]]; then
    mkdir -p "$HOME/.claude/logs"
    python3 "$PROJECT_DIR/tools/hub_context_refresh.py" \
        --quiet \
        >> "$HOME/.claude/logs/hub-context-refresh-$(date +%Y%m%d).log" 2>&1 &
    echo "[wai-exit] Feeds: hub refresh running in background"
elif [[ -f "$PROJECT_DIR/tools/advisor_context_refresh.py" ]]; then
    mkdir -p "$HOME/.claude/logs"
    python3 "$PROJECT_DIR/tools/advisor_context_refresh.py" \
        --quiet --spoke-path "$PROJECT_DIR" \
        >> "$HOME/.claude/logs/context-refresh-$(date +%Y%m%d).log" 2>&1 &
    echo "[wai-exit] Feeds: refresh running in background"
fi

echo "[wai-exit] Done. Next wakeup will use fast path."

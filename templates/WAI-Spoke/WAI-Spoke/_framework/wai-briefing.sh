#!/bin/bash
#
# WAI Briefing Generator
# Unified "where are we" briefing used by hooks, commands, and natural language
#

set -e

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-${WAI_PROJECT_DIR:-${CODEX_PROJECT_DIR:-.}}}"
STATE_FILE="$PROJECT_DIR/WAI-Spoke/WAI-State.json"
LUGS_FILE="$PROJECT_DIR/WAI-Spoke/WAI-Lugs.jsonl"

# Exit if WAI-Spoke doesn't exist
[[ ! -f "$STATE_FILE" ]] && echo "WAI not initialized in this project" && exit 1

generate_wai_briefing() {
  # Project Identity
  local project_name=$(jq -r '.wheel.name // "Unknown Project"' "$STATE_FILE")
  local current_phase=$(jq -r '.context.current_phase // "Unknown Phase"' "$STATE_FILE")
  local last_modified_by=$(jq -r '._session_state.last_modified_by // "Unknown"' "$STATE_FILE")
  local last_modified_at=$(jq -r '._session_state.last_modified_at // "Unknown"' "$STATE_FILE")

  # Environment Detection
  local current_tool="claude-code"  # Default, can be enhanced
  local current_machine=$(hostname -s 2>/dev/null || echo "unknown")
  local current_os=$(uname -s 2>/dev/null || echo "unknown")

  # Context Health
  local token_pct=$(jq -r '._session_state.context_usage_at_closeout // 0 | . * 100 | floor' "$STATE_FILE" 2>/dev/null || echo "0")
  local last_teach=$(jq -r '(.wheelwright.sync_history[-1].date // .wheel.sync_history[-1].date) // "never"' "$STATE_FILE" 2>/dev/null || echo "never")
  local hub_connected=$(jq -r '(.wheel.hub_path // .wheelwright.hub_path) // ""' "$STATE_FILE")
  [[ -n "$hub_connected" ]] && hub_status="✓ Connected" || hub_status="⚠ Not connected"

  # Git Status
  cd "$PROJECT_DIR"
  local uncommitted_count=$(git status --short 2>/dev/null | wc -l || echo "0")
  [[ "$uncommitted_count" -gt 0 ]] && git_status="⚠ $uncommitted_count uncommitted" || git_status="✓ Clean"

  # Output unified briefing
  echo "## 🎡 WAI Point - $project_name"
  echo ""
  echo "**Phase:** $current_phase"
  echo "**Last session:** $last_modified_at by $last_modified_by"
  echo "**Environment:** $current_tool on $current_machine ($current_os)"
  echo ""

  # Active Work (if lugs exist)
  if [[ -f "$LUGS_FILE" ]]; then
    echo "### Active Work (Prioritized)"
    echo ""

    # Priority counts
    local flagged=$(jq -r 'select(.priority == "before_next_epic" and .s == "open") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)
    local bugs=$(jq -r 'select(.ty == "bug" and .s == "open") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)
    local verify=$(jq -r 'select(.verify_on_closeout == true and .s == "open") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)
    local in_progress=$(jq -r 'select(.s == "p") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)
    local open_tasks=$(jq -r 'select(.s == "o" and .ty != "epic") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)
    local epics=$(jq -r 'select(.ty == "epic" and .s == "open") | .i' "$LUGS_FILE" 2>/dev/null | wc -l)

    echo "- 🚨 **Flagged Priority:** $flagged items"
    echo "- 🐛 **Bugs:** $bugs open"
    echo "- ✓ **Verification Needed:** $verify items"
    echo "- ⏳ **In Progress:** $in_progress items"
    echo "- 📋 **Open Tasks:** $open_tasks items"
    echo "- 🎪 **Epics (Blocked Until Above Clear):** $epics epics"
    echo ""

    # Show top priority item
    local top_priority=$(jq -r '
      select(.priority == "before_next_epic" and .s == "open") |
      "\(.i): \(.t)"
    ' "$LUGS_FILE" 2>/dev/null | head -1)

    if [[ -n "$top_priority" ]]; then
      echo "**Top Priority:** $top_priority"
      echo ""
    fi

    # Autosave checkpoint detection (unreconciled = previous session work)
    if command -v python3 &>/dev/null; then
      unreconciled=$(python3 -c "
import json
count = 0
last = {}
with open('$LUGS_FILE') as f:
    for line in f:
        try:
            l = json.loads(line.strip())
            if l.get('autosave') and not l.get('reconciled'):
                count += 1
                last = l
        except: pass
if count:
    print(f'{count}|{last.get(\"task_context\",\"unknown\")}|{last.get(\"completion_estimate\",\"?\")}')
" 2>/dev/null)
      if [[ -n "$unreconciled" ]]; then
        IFS='|' read -r cnt task est <<< "$unreconciled"
        echo "### ⚠️ Incomplete Work ($cnt autosave checkpoints)"
        echo "- Task: $task"
        echo "- Progress: $est"
        echo "- **Resume:** \`Green Light\` | **Inspect:** \`Red Light\` | **Discard:** reconciled on next Closeout"
        echo ""
      fi
    fi
  fi

  # Context Health
  echo "### Context Health"

  # Only show token usage if we have real data (not default/unknown)
  if [[ $token_pct -gt 0 ]]; then
    echo "- Token usage: ${token_pct}% of 200K budget"
  fi

  # File loading stats with byte/token metrics
  # Core files that get loaded into context
  local CORE_FILES=(
    "$PROJECT_DIR/WAI-Spoke/WAI-Guide.md"
    "$PROJECT_DIR/WAI-Spoke/WAI-State.json"
    "$PROJECT_DIR/WAI-Spoke/WAI-State.md"
    "$PROJECT_DIR/WAI-Spoke/WAI-Lugs.jsonl"
  )

  # Calculate sizes of loaded files
  local loaded_bytes=0
  local loaded_count=0
  for f in "${CORE_FILES[@]}"; do
    if [[ -f "$f" ]]; then
      local fsize=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null || echo 0)
      loaded_bytes=$((loaded_bytes + fsize))
      loaded_count=$((loaded_count + 1))
    fi
  done

  # Calculate total size of all WAI-Spoke files
  local total_bytes=0
  while IFS= read -r f; do
    local fsize=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null || echo 0)
    total_bytes=$((total_bytes + fsize))
  done < <(find "$PROJECT_DIR/WAI-Spoke" -type f 2>/dev/null)

  local total_files=$(find "$PROJECT_DIR/WAI-Spoke" -type f 2>/dev/null | wc -l)

  # Prevent division by zero
  if [[ $total_bytes -eq 0 ]]; then
    echo "- Files: No WAI-Spoke files found"
  else
    local saved_bytes=$((total_bytes - loaded_bytes))
    local saved_files=$((total_files - loaded_count))

    # Convert bytes to human-readable and estimate tokens (1 token ≈ 4 bytes)
    local loaded_kb=$((loaded_bytes / 1024))
    local total_kb=$((total_bytes / 1024))
    local saved_kb=$((saved_bytes / 1024))

    local loaded_tokens_raw=$((loaded_bytes / 4))
    local saved_tokens_raw=$((saved_bytes / 4))

    # Format tokens with K suffix
    local loaded_tokens="${loaded_tokens_raw}"
    local saved_tokens="${saved_tokens_raw}"
    if [[ $loaded_tokens_raw -ge 1000 ]]; then
      loaded_tokens="$((loaded_tokens_raw / 1000))K"
    fi
    if [[ $saved_tokens_raw -ge 1000 ]]; then
      saved_tokens="$((saved_tokens_raw / 1000))K"
    fi

    # Calculate percentages
    local pct_files=$((loaded_count * 100 / total_files))
    local pct_bytes=$((loaded_bytes * 100 / total_bytes))

    echo "- File loading: $loaded_count loaded / $total_files total (${pct_files}%) → ${loaded_kb}KB / ${total_kb}KB (${pct_bytes}%) ≈ ${loaded_tokens} tokens [Saved: ${saved_kb}KB ≈ ${saved_tokens} tokens]"
  fi

  echo "- Hub: $hub_status"
  echo "- Last teach: $last_teach"
  echo "- Git: $git_status"
  echo ""

  # Hub Just-In-Time Context (quota warnings, notifications)
  if [[ -n "$hub_connected" ]] && [[ -d "$hub_connected" ]]; then
    # Try to get hub context via Python
    local hub_context=$(python3 -c "
import sys
sys.path.insert(0, '$PROJECT_DIR')
try:
    from wai.hub_state import format_hub_context_for_agent
    from pathlib import Path
    result = format_hub_context_for_agent(Path('$hub_connected'))
    if result:
        print(result)
except Exception as e:
    pass
" 2>/dev/null)

    if [[ -n "$hub_context" ]]; then
      echo "### 🌐 Hub Context"
      echo ""
      echo "$hub_context"
      echo ""
    fi
  fi

  # Teaching Files Detection
  local MANIFEST_FILE="$PROJECT_DIR/WAI-Spoke/seed/ingest/manifest.json"

  if [[ -f "$MANIFEST_FILE" ]]; then
    echo "### 🎓 Pending Teachings"

    local TEACHING_COUNT=$(jq -r '.files_taught | length' "$MANIFEST_FILE" 2>/dev/null || echo "0")
    local TAUGHT_AT=$(jq -r '.taught_at' "$MANIFEST_FILE" 2>/dev/null || echo "unknown")

    echo "- **$TEACHING_COUNT file(s) awaiting review**"
    echo "- Taught: $TAUGHT_AT"
    echo ""
    echo "**Files to review:**"
    jq -r '.files_taught[] | "  • \(.name)"' "$MANIFEST_FILE" 2>/dev/null | head -5
    echo ""
    echo "**Action Required:** Review and adopt teaching files"
    echo ""
  fi

  # Recent High-Impact Decisions
  local recent_decisions=$(jq -r '
    .decisions
    | map(select(.impact >= 8))
    | sort_by(.date)
    | reverse
    | .[0:3]
    | map("- " + .decision + " (impact: " + (.impact|tostring) + ")")
    | join("\n")
  ' "$STATE_FILE")

  if [[ -n "$recent_decisions" ]]; then
    echo "### Recent Changes"
    echo "$recent_decisions"
    echo ""
  fi

  # Next Actions
  local next_actions=$(jq -r '
    .context.next_actions
    | .[0:5]
    | map("- " + .)
    | join("\n")
  ' "$STATE_FILE")

  if [[ -n "$next_actions" ]]; then
    echo "### Next Actions"
    echo "$next_actions"
    echo ""
  fi

  # Quick Commands
  echo "### Quick Commands"
  echo "- **/wai-status** - Integration health check"
  echo "- **/wai-time** - Token usage estimate"
  echo "- **/wai-rules** - Project boundaries and guidelines"
  echo "- **/wai-closeout** - End session and extract signals"
  echo "- **/wai-shipit** - Closeout + commit WAI files"
  echo ""
  echo "---"
  echo "*Ask \"what should I work on?\" for recommendations*"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  generate_wai_briefing
fi

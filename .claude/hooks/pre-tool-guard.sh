#!/bin/bash
#
# PreToolUse Guard — blocks destructive commands at hook level
# Returns JSON with decision: allow/deny/ask
# Stderr output blocks the action; stdout is informational
#

input=$(cat)
tool=$(echo "$input" | jq -r '.tool_name // ""')

# Only guard Bash commands
[[ "$tool" != "Bash" ]] && echo '{"decision":"allow"}' && exit 0

cmd=$(echo "$input" | jq -r '.tool_input.command // ""')

# Extract only executable lines (strip heredoc bodies and quoted strings)
# Take the first line and any lines not inside a heredoc
first_line=$(echo "$cmd" | head -1)

# Block: rm -rf / (root deletion) — only on first line to avoid heredoc false positives
if echo "$first_line" | grep -qE '^\s*\\?rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?/\s*$|^\s*\\?rm\s+-rf\s+/'; then
  echo "BLOCKED: rm -rf / — destructive root deletion" >&2
  exit 2
fi

# Block: force push — check full command but only as a standalone git command
if echo "$first_line" | grep -qE '^\s*git\s+push\s+(-f|--force)'; then
  echo "BLOCKED: git push --force — use regular push" >&2
  exit 2
fi

# Block: git reset --hard without specific ref (too broad)
if echo "$first_line" | grep -qE '^\s*git\s+reset\s+--hard\s*$'; then
  echo "BLOCKED: git reset --hard (no ref) — specify a commit or use git stash" >&2
  exit 2
fi

# Block: drop database — only on first line
if echo "$first_line" | grep -qiE '^\s*.*drop\s+(database|table)'; then
  echo "BLOCKED: DROP DATABASE/TABLE — destructive DB operation" >&2
  exit 2
fi

# Allow everything else
echo '{"decision":"allow"}'
exit 0

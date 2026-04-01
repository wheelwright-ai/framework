#!/bin/bash
#
# WAI PostToolUse Hook — Python Syntax Checker
# Fires after Write and Edit on .py files.
# Runs python3 -m py_compile to catch syntax errors immediately.
# Never exits non-zero — PostToolUse is advisory only.
#

input=$(cat)
tool=$(echo "$input" | jq -r '.tool_name // ""')

# Only check Write and Edit
[[ "$tool" != "Write" && "$tool" != "Edit" ]] && exit 0

# Get file path
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')
[[ -z "$file_path" ]] && exit 0

# Only check Python files
[[ "$file_path" != *.py ]] && exit 0

# File must exist
[[ ! -f "$file_path" ]] && exit 0

# Run syntax check
RESULT=$(python3 -m py_compile "$file_path" 2>&1)
if [[ $? -ne 0 ]]; then
  echo "<post-tool-warning>"
  echo "Python syntax error in $file_path:"
  echo "$RESULT"
  echo "</post-tool-warning>"
fi

exit 0

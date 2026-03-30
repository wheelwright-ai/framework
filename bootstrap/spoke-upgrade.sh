#!/bin/bash
#
# WAI Spoke Upgrade Script
# Upgrades a spoke to the latest framework version.
# Run from the spoke's project root directory.
#
# Usage: bash /path/to/spoke-upgrade.sh [spoke_path]
#
set -euo pipefail

SPOKE_PATH="${1:-.}"
HUB_PATH="${PROJECTS_ROOT:-~/projects}/wheelwright/hub"
FRAMEWORK_PATH="$HUB_PATH/framework"
TEMPLATE_PATH="$FRAMEWORK_PATH/templates/spoke"

cd "$SPOKE_PATH"
SPOKE_NAME=$(basename "$(pwd)")

echo "=== WAI Spoke Upgrade: $SPOKE_NAME ==="
echo "Spoke: $(pwd)"
echo "Hub: $HUB_PATH"
echo "Framework: $FRAMEWORK_PATH"
echo ""

# --- Preflight ---
if [ ! -d "$HUB_PATH" ]; then
  echo "ERROR: Hub not found at $HUB_PATH"
  exit 1
fi
if [ ! -d "$FRAMEWORK_PATH/templates/spoke" ]; then
  echo "ERROR: Framework templates not found at $FRAMEWORK_PATH/templates/spoke"
  exit 1
fi

# Get framework version
FW_VERSION=$(python3 -c "import json; print(json.load(open('$FRAMEWORK_PATH/WAI-Spoke/WAI-State.json'))['wheel']['version'])")
echo "Framework version: $FW_VERSION"

# --- Step 1: Git safety snapshot ---
echo ""
echo "--- Step 1: Git safety snapshot ---"
if [ -d .git ]; then
  if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    git add -A
    git commit -m "WAI: Pre-upgrade snapshot (framework $FW_VERSION)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>" 2>/dev/null || echo "  (nothing to commit)"
  else
    echo "  Working tree clean — no snapshot needed"
  fi
else
  echo "  Not a git repo — skipping snapshot"
fi

# --- Step 2: Ensure WAI-Spoke structure ---
echo ""
echo "--- Step 2: Ensure WAI-Spoke structure ---"
mkdir -p WAI-Spoke/commands
mkdir -p WAI-Spoke/lugs/inbox
mkdir -p WAI-Spoke/lugs/outbox
mkdir -p WAI-Spoke/seed/ingest/processed
mkdir -p WAI-Spoke/sessions
mkdir -p .claude/hooks
echo "  Directories: OK"

# --- Step 3: Initialize WAI-State.json if missing ---
echo ""
echo "--- Step 3: WAI-State.json ---"
if [ ! -f WAI-Spoke/WAI-State.json ]; then
  cp "$TEMPLATE_PATH/WAI-State.json" WAI-Spoke/WAI-State.json
  echo "  Created from template"
fi

# Update hub_path and framework_version (preserve everything else)
python3 << PYEOF
import json, sys

state_path = "WAI-Spoke/WAI-State.json"
with open(state_path) as f:
    state = json.load(f)

changed = []

if "wheel" not in state:
    state["wheel"] = {}

if state["wheel"].get("hub_path") != "${PROJECTS_ROOT:-~/projects}/wheelwright/hub/":
    state["wheel"]["hub_path"] = "${PROJECTS_ROOT:-~/projects}/wheelwright/hub/"
    changed.append("wheel.hub_path")

fw_ver = "$FW_VERSION"
if state["wheel"].get("framework_version") != fw_ver:
    state["wheel"]["framework_version"] = fw_ver
    changed.append(f"wheel.framework_version = {fw_ver}")

if state["wheel"].get("node_type") != "spoke":
    state["wheel"]["node_type"] = "spoke"
    changed.append("wheel.node_type = spoke")

if "wheelwright" in state:
    if state["wheelwright"].get("hub_path") != "${PROJECTS_ROOT:-~/projects}/wheelwright/hub/":
        state["wheelwright"]["hub_path"] = "${PROJECTS_ROOT:-~/projects}/wheelwright/hub/"
        changed.append("wheelwright.hub_path")
    if state["wheelwright"].get("framework_path") != "${PROJECTS_ROOT:-~/projects}/wheelwright/framework":
        state["wheelwright"]["framework_path"] = "${PROJECTS_ROOT:-~/projects}/wheelwright/framework"
        changed.append("wheelwright.framework_path")

if changed:
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
    for c in changed:
        print(f"  Updated: {c}")
else:
    print("  Already current")
PYEOF

# --- Step 4: Copy AI bootstrap files ---
echo ""
echo "--- Step 4: AI bootstrap files ---"
cp "$TEMPLATE_PATH/AGENTS.md" ./AGENTS.md
echo "  AGENTS.md: copied"

cp "$TEMPLATE_PATH/CLAUDE.md" ./CLAUDE.md
echo "  CLAUDE.md: copied"

cp "$TEMPLATE_PATH/GEMINI.md" ./GEMINI.md
echo "  GEMINI.md: copied"

# --- Step 5: Copy skills ---
echo ""
echo "--- Step 5: Skills (WAI-Spoke/commands/) ---"
SKILL_COUNT=0
for f in "$TEMPLATE_PATH"/commands/*.md; do
  fname=$(basename "$f")
  cp "$f" WAI-Spoke/commands/"$fname"
  SKILL_COUNT=$((SKILL_COUNT + 1))
done
echo "  Copied $SKILL_COUNT skill files"

# --- Step 6: Copy hook ---
echo ""
echo "--- Step 6: Hook ---"
cp "$TEMPLATE_PATH/.claude/hooks/user-prompt-submit.sh" .claude/hooks/user-prompt-submit.sh
chmod +x .claude/hooks/user-prompt-submit.sh
echo "  user-prompt-submit.sh: copied"

# Merge hook config into .claude/settings.json
python3 << 'HOOKEOF'
import json, os

settings_path = ".claude/settings.json"
hook_entry_prompt = {
    "matcher": ".*",
    "hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit.sh"}]
}

if os.path.exists(settings_path):
    with open(settings_path) as f:
        settings = json.load(f)
else:
    settings = {}

if "hooks" not in settings:
    settings["hooks"] = {}

# Ensure UserPromptSubmit hook exists
existing = settings["hooks"].get("UserPromptSubmit", [])
hook_cmd = "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit.sh"
already_has = any(
    h.get("hooks", [{}])[0].get("command") == hook_cmd
    for h in existing if h.get("hooks")
)

if not already_has:
    existing.append(hook_entry_prompt)
    settings["hooks"]["UserPromptSubmit"] = existing
    print("  settings.json: hook added")
else:
    print("  settings.json: hook already configured")

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")
HOOKEOF

# --- Step 7: WAI-Spoke README ---
echo ""
echo "--- Step 7: WAI-Spoke README ---"
cat > WAI-Spoke/README.md << 'READMEEOF'
# WAI-Spoke

This project is a **Wheelwright spoke** — it maintains session continuity across AI tools and sessions.

## For AI Assistants

Start here: Read `WAI-State.json`, then follow `commands/wai.md` for the wakeup protocol.

## For Humans

| File | Purpose |
|------|---------|
| `WAI-State.json` | Project state, identity, hub connection |
| `WAI-Lugs.jsonl` | Work tracker (tasks, bugs, decisions) — append-only |
| `commands/` | Skills — behavioral rules as .md files |
| `lugs/inbox/` | Incoming items from hub/other projects |
| `lugs/outbox/` | Outbound items for hub/other projects |
| `seed/ingest/` | Pending framework teachings |
| `session-*/` | Session tracks (turn-by-turn capture) |

## Hub Connection

Hub path is in `WAI-State.json` → `wheel.hub_path`.
Framework (protocol source of truth) is at `{hub_path}/framework/`.
READMEEOF
echo "  WAI-Spoke/README.md: written"

# --- Step 8: Reconciliation ---
echo ""
echo "--- Step 8: Reconciliation ---"

# WAI-Lugs.jsonl: canonical location is WAI-Spoke/
if [ -f WAI-Spoke/WAI-Lugs.jsonl ]; then
  echo "  WAI-Spoke/WAI-Lugs.jsonl: exists (preserved)"
elif [ -f WAI-Lugs.jsonl ]; then
  # Found at root — move to canonical location
  mv WAI-Lugs.jsonl WAI-Spoke/WAI-Lugs.jsonl
  echo "  Moved WAI-Lugs.jsonl → WAI-Spoke/WAI-Lugs.jsonl"
else
  touch WAI-Spoke/WAI-Lugs.jsonl
  echo "  Created WAI-Spoke/WAI-Lugs.jsonl (empty)"
fi

# Clean up orphaned skill files in WAI-Spoke/ root (v1 had them loose, v2 uses commands/)
ORPHAN_COUNT=0
for f in WAI-Spoke/wai-*.md; do
  [ -f "$f" ] || continue
  fname=$(basename "$f")
  if [ -f "WAI-Spoke/commands/$fname" ]; then
    rm "$f"
    ORPHAN_COUNT=$((ORPHAN_COUNT + 1))
  fi
done
if [ "$ORPHAN_COUNT" -gt 0 ]; then
  echo "  Cleaned $ORPHAN_COUNT orphaned skill files from WAI-Spoke/ root (now in commands/)"
fi

# Migrate seed/processed → seed/ingest/processed if old path exists
if [ -d WAI-Spoke/seed/processed ] && [ ! -d WAI-Spoke/seed/ingest/processed ]; then
  mv WAI-Spoke/seed/processed WAI-Spoke/seed/ingest/processed
  echo "  Migrated seed/processed → seed/ingest/processed"
elif [ -d WAI-Spoke/seed/processed ]; then
  echo "  seed/processed: old path still exists (seed/ingest/processed also exists — manual check needed)"
fi

# --- Step 9: Git commit upgrade ---
echo ""
echo "--- Step 9: Commit upgrade ---"
if [ -d .git ]; then
  git add AGENTS.md 2>/dev/null; git add CLAUDE.md 2>/dev/null; git add GEMINI.md 2>/dev/null
  git add WAI-Spoke/ 2>/dev/null; git add .claude/ 2>/dev/null
  git commit -m "WAI: Upgraded to framework $FW_VERSION — skills, hooks, bootstrap files

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>" 2>/dev/null || echo "  (nothing new to commit)"
else
  echo "  Not a git repo — skipping commit"
fi

# --- Summary ---
echo ""
echo "=== Upgrade Complete: $SPOKE_NAME ==="
echo "Framework version: $FW_VERSION"
echo "Skills: $SKILL_COUNT files in WAI-Spoke/commands/"
echo "Hub: ${PROJECTS_ROOT:-~/projects}/wheelwright/hub/"
echo "Bootstrap files: AGENTS.md, CLAUDE.md, GEMINI.md"
echo "Hook: .claude/hooks/user-prompt-submit.sh (wired in settings.json)"
echo ""

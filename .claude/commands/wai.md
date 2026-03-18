# WAI Wakeup - v2 Protocol (10 Steps)

## Overview

Execute the 10-step wakeup protocol to initialize the spoke, discover new teachings, and get ready for work.

---

## Step 1: Load WAI-State.json

Load the spoke's technical spec, foundation, and session state:

```bash
cat WAI-Spoke/WAI-State.json
```

Key sections to check:
- `_foundation` - Project identity, context, vision
- `_session_state` - Last session info, session count
- `_auto_implementation` - Auto-execution settings (if exists)

---

## Step 2: Load WAI-State.md

Load the strategic context and vision:

```bash
cat WAI-Spoke/WAI-State.md
```

This complements the technical spec in WAI-State.json.

---

## Step 3a: Auto-Discovery of New Hub Teachings ⭐ NEW!

Poll the hub's teachings folder and reconcile with local implementation state:

```bash
# Scan hub/framework/*.teaching and reconcile
HUB_PATH=$(jq -r '.hub.path // "/home/mario/projects/wheelwright/hub"' WAI-Spoke/WAI-State.json 2>/dev/null)
TEACHINGS=("$HUB_PATH"/framework/*.teaching)
TOTAL=${#TEACHINGS[@]}
RECONCILED=0
NEW_COUNT=0

mkdir -p WAI-Spoke/seed/processed

for teaching in "${TEACHINGS[@]}"; do
    [ ! -f "$teaching" ] && continue
    BASENAME=$(basename "$teaching")
    
    # Already processed? Skip
    if [ -f "WAI-Spoke/seed/processed/$BASENAME" ]; then
        continue
    fi
    
    # Check if already implemented (light verification)
    TEACHING_NAME=$(head -1 "$teaching" | sed 's/# Teaching: //;s/^# //')
    IS_IMPLEMENTED=false
    
    # Check 1: Filename mentioned in signals (most reliable)
    if grep -q "$BASENAME" WAI-Spoke/WAI-Signals.jsonl 2>/dev/null; then
        IS_IMPLEMENTED=true
    fi
    
    # Check 2: Teaching name in signals (case-insensitive, partial match)
    if [ "$IS_IMPLEMENTED" = false ]; then
        if grep -qi "$(echo "$TEACHING_NAME" | cut -d' ' -f1-3)" WAI-Spoke/WAI-Signals.jsonl 2>/dev/null; then
            IS_IMPLEMENTED=true
        fi
    fi
    
    # Check 3: Verification files exist
    if [ "$IS_IMPLEMENTED" = false ]; then
        VERIF_FILES=$(grep -A 20 "## Verification" "$teaching" 2>/dev/null | grep -oP '`[^`]+\.(yaml|json|jsonl|md|py|sh)`' | tr -d '`' || true)
        for vfile in $VERIF_FILES; do
            if [ -f "$vfile" ] || [ -d "$vfile" ]; then
                IS_IMPLEMENTED=true
                break
            fi
        done
    fi
    
    # Auto-reconcile if implemented
    if $IS_IMPLEMENTED; then
        cp "$teaching" "WAI-Spoke/seed/processed/"
        RECONCILED=$((RECONCILED + 1))
    else
        NEW_COUNT=$((NEW_COUNT + 1))
    fi
done
```

**Display discovery result:**
```
### 📚 Teaching Discovery from Hub
🎯 {TOTAL} teachings scanned
✅ {RECONCILED} already implemented (reconciled)
🆕 {NEW_COUNT} new teachings found

{if NEW_COUNT > 0}
New Queue:
- ⚠️  teaching-X - {title} (safe: false)
- ✅ teaching-Y - {title} (safe: true)
{endif}
```

**Reconciliation behavior:**
- Already in processed/ → skip (no action)
- Implemented but not in processed/ → auto-copy to processed/ (reconcile gap)
- Not implemented → add to new teachings queue

If `auto_adopt_teachings: true` and new teachings found with confirmation:
- Auto-adopt all safe teachings
- Apply transformations
- Copy to WAI-Spoke/seed/processed/
- Log adoption

---

## Step 3: Load Skills

Load active skills from WAI-Skills.jsonl:

```bash
cat WAI-Spoke/WAI-Skills.jsonl
```

Report any active advisory watches and skills that recommend themselves at session start.

---

## Step 4: Load Lugs and Signals

Load active work and learnings:

```bash
cat WAI-Spoke/WAI-Lugs.jsonl
cat WAI-Spoke/WAI-Signals.jsonl
```

---

## Step 4.1: Detect External Tracks (Ported from template)

Check `WAI-Spoke/seed/ingest/` for `WAI_Track-*.jsonl` files — external session tracks captured via the Chat-to-Track prompt. If present:
- Output: "📡 N external track file(s) awaiting ingest"
- For each file:
  1. Read the first line. Validate it is valid JSON containing `"event":"session_start"` with `provider` and `model` fields.
  2. If valid: copy file to `WAI-Spoke/sessions/` preserving the original filename. Move the original to `seed/ingest/processed/`.
     Output:
     ```
     📡 Absorbed: {filename}
        Source: {provider} / {model}
        Events: {total line count}
        Decisions: {count of lines containing "decision_made"}
        Concepts: {count of lines containing "concept_update"}
     ```
  3. If invalid (missing session_start, missing provider/model, or malformed JSON on first line): output:
     ```
     ⚠️ Could not absorb: {filename}
        Issue: {specific problem}
        File left in seed/ingest/ — fix and retry.
     ```
     Do not move the file.

---

## Step 5: Display Briefing

Show unified WAI Point briefing:
- Project identity and phase
- Current environment
- Active work (prioritized backlog)
- Context health (tokens, hub, git)
- Recent high-impact changes
- Next actions

---

## Step 6: Auto-Implementation Queue ⭐ NEW!

Check for auto-implementation work:

If `_auto_implementation.enabled == true`:
- Build queue from WAI-Lugs.jsonl
- Sort by natural priority (bugs > flagged > tasks)
- Display queue in awareness mode

```
### Auto-Implementation Queue (Awareness Mode)
🎯 {count} items in queue
🔒 Auto-Implement: {enabled|disabled}

Queue (confidence = N/10):
- 🔴 bug-001 - Fix authentication (conf: 9)
- 🟡 feature-002 - Add payment processing (conf: 6) [review]
- 🟢 task-001 - Update API docs (conf: 8)
```

If `review_low_confidence == true`:
- Highlight low-confidence items (< 8)
- Run Step 6.1: Interactive review

---

## Step 6.1: Interactive Review (Low-Confidence Work) ⭐ NEW!

For low-confidence items (confidence < 8), provide interactive review:

1. Show analysis:
   - What the lug does
   - Why confidence is low
   - Risks if wrong
   - Suggested improvements

2. Offer 6 options:
   - [1] 🚀 Approve with current confidence
   - [2] ⬆️ Improve + Approve (add improvements, increase confidence)
   - [3] 🔍 Request review (create review finding, skip)
   - [4] ⏸️ Defer (keep in queue, skip now)
   - [5] ❌ Reject (close lug, skip)
   - [6] ⚙️  Override (force execute despite low confidence)

---

## Step 7: Session Check

Check session state:
- `last_modified_by` / `last_modified_at`
- `requires_review` - surface reason if true
- `session_count` - increment on significant update

---

## Step 8: Environment Detection

Auto-detect environment:
- Tool (claude-code, cursor, etc.)
- Machine (hostname or WAI_MACHINE env var)
- OS
- Parent session (WAI_PARENT_SESSION)

Scan WAI-Spoke/sessions/ to surface recent activity from other tools/machines.

---

## Step 9: Initialize Session Track ⭐ NEW!

Create session tracking:

```bash
# Create session directory
SESSION_DIR="WAI-Spoke/session-$(date +%Y%m%d-%H%M)"
mkdir -p "$SESSION_DIR"

# Initialize track.jsonl
touch "$SESSION_DIR/track.jsonl"
```

**MANDATORY: High-Fidelity Turn Capture**
Every turn MUST conclude with an append to `track.jsonl`. 
- **Detail:** Do not compress or summarize the technical story.
- **Thinking:** Capture the *complete* architectural rationale (5-8 sentences).
- **Activity:** List every file read, every command run, and the specific result.
- **Goal:** Enable any agent to pick up your exact mental state cold.

Per-turn point capture schema:
```json
{
  "turn": 1,
  "ts": "ISO-8601",
  "focus": "Descriptive topic thread",
  "action": "Detailed summary of outcomes",
  "thinking": "Full technical narrative (reasoning/rationale)",
  "activity": ["Concrete actions taken"],
  "decisions": ["Architectural choices"],
  "insights": ["New understandings"],
  "open": ["Unresolved threads"],
  "phase": "Current phase",
  "evolution": "How understanding evolved"
}
```

---

## Step 10: Ready Prompt

After completing all steps, ask:

"Wake complete. Ready to work. What would you like to do next?"

---

## Context

### Core Files Reference

| File | Purpose | Access |
|------|---------|--------|
| `WAI-State.json` | Technical spec, foundation, session state | UPDATE |
| `WAI-State.md` | Strategic context, vision | UPDATE |
| `WAI-Skills.jsonl` | Skill registry with metadata | READ |
| `WAI-Lugs.jsonl` | Active task/dependency graph | UPDATE |
| `WAI-Signals.jsonl` | High-impact learnings | APPEND |
| `WAI-Session-Log.jsonl` | Conversation turns (cleared on closeout) | APPEND |

---

## Multi-Environment Sessions

Each environment (tool + machine) gets its own session log:
```
WAI-Spoke/sessions/
  claude-code-laptop.jsonl
  cursor-desktop.jsonl
```

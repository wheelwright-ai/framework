# WAI Wakeup Protocol — Reference

**Companion to `wai.md`.** Contains scripts, schemas, and verbose specs. Load on-demand.

---

## Step 3b: Track Integrity — Full Script

```bash
# Skip current session dir (just created by hook); check previous
LAST_TRACK="WAI-Spoke/sessions/$(ls -1t WAI-Spoke/sessions/ | sed -n '2p')/track.jsonl"
if [ -f "$LAST_TRACK" ]; then
    LAST_LINE=$(tail -1 "$LAST_TRACK")
    # CLEAN = completed turn OR explicit closeout event
    if echo "$LAST_LINE" | jq -e '.completed == true or .event == "closeout"' >/dev/null 2>&1; then
        STATUS="CLEAN"
    elif echo "$LAST_LINE" | jq . >/dev/null 2>&1; then
        STATUS="INTERRUPTED"  # valid JSON but no completion marker
    else
        STATUS="INTERRUPTED"  # malformed JSON = crash
    fi
else
    STATUS="FIRST_SESSION"
fi
```

**Recovery options (INTERRUPTED):**
- **Green Light** — Resume from last autosave checkpoint
- **Red Light** — Inspect track + autosave before resuming
- **Skip** — Ignore, start fresh
- **New Project** — Abandon spoke, start over

Autosave: `ls WAI-Spoke/.autosave/turn-*.json | sort -t- -k2 -rn | head -1`

---

## Step 4: Lug Folder Structure

```
WAI-Spoke/lugs/
  incoming/                        — inbound deliveries
  outgoing/                        — outbound deliveries
  reference/                       — reference docs
  bytype/
    epic/{open,in_progress,completed}/
    task/{open,in_progress,completed}/
    feature/{open,in_progress,completed}/
    bug/{open,in_progress,completed}/
    implementation/{in_progress,completed}/
    signal/{undelivered,delivered}/
    session-summary/               — no status subfolder
    other/{open,completed}/
```

## Step 4: Stale In-Progress Detection Script

```bash
FOUR_HOURS_AGO=$(date -d '4 hours ago' +%s 2>/dev/null || date -v-4H +%s)
for lug in WAI-Spoke/lugs/bytype/*/in_progress/*.json; do
    UPDATED=$(jq -r '.updated_at // .created_at' "$lug")
    UPDATED_EPOCH=$(date -d "$UPDATED" +%s 2>/dev/null || echo 0)
    if [ "$UPDATED_EPOCH" -lt "$FOUR_HOURS_AGO" ]; then
        echo "STALE: $(basename $lug) unchanged since $UPDATED"
    fi
done
```

Options: **Abandon** (→ completed with "abandoned" note) | **Resume** (→ open) | **Extend** (update timestamp).

---

## Step 4b: Historian Watermark Script

```bash
LAST_SCAN_RAW=$(jq -r '.last_scan_session // ""' WAI-Spoke/advisors/historian/scan_state.json 2>/dev/null)
LAST_SCAN_TS=$(echo "$LAST_SCAN_RAW" | sed 's/^[^0-9]*//')

UNREVIEWED_SESSIONS=0
UNREVIEWED_POINTS=0
for session_dir in WAI-Spoke/sessions/session-*/; do
    session_ts="${$(basename "$session_dir")#session-}"
    if [[ -z "$LAST_SCAN_TS" || "$session_ts" > "$LAST_SCAN_TS" ]]; then
        count=$(wc -l < "$session_dir/track.jsonl" 2>/dev/null || echo 0)
        UNREVIEWED_POINTS=$((UNREVIEWED_POINTS + count))
        UNREVIEWED_SESSIONS=$((UNREVIEWED_SESSIONS + 1))
    fi
done
```

---

## Step 4c: Taste Bootstrap Content

```yaml
# taste.spoke.yaml — project-level preferences
# Auto-generated at wakeup. Edit freely.
preferences:
  communication:
    verbosity: balanced
    style: direct
  workflow:
    plan_threshold: 2
    auto_commit: false
nudges: []
```

---

## Step 5: Teaching Scan Script

```bash
HUB_PATH=$(jq -r '.wheel.hub_path' WAI-Spoke/WAI-State.json)
test -d "${HUB_PATH}" && echo "HUB_OK" || echo "HUB_MISSING"
test -d "${HUB_PATH}/teachings_repo/framework/current" && echo "TEACHINGS_OK" || echo "TEACHINGS_MISSING"

# Before-state count
BEFORE_COUNT=$(ls -1 WAI-Spoke/seed/ingest/processed/*.teaching 2>/dev/null | wc -l)
ls -1 "${HUB_PATH}/teachings_repo/framework/current/"*.teaching 2>/dev/null

# Detect auto-adopt flag
grep -im1 "safe.to.auto.adopt" {teaching_file}
```

**Hub path error format (briefing):**
```
HUB PATH ERROR: wheel.hub_path is {value} — directory not found. Teaching discovery skipped.
Fix: Set wheel.hub_path in WAI-State.json to the correct hub directory.
```

**Teaching Path A (safe_to_auto_adopt: true):**
1. Extract: what it affects, behavioral implication, challenge solved
2. Check `## Batch Sequence` block — respect apply order
3. Compact table: File | Summary | Impact
4. Duplicate check: skip if same `timestamp` OR `id` exists — log "Signal already known; skipping"
5. "Apply all / Skip all / Apply [specific]?" — wait
6. Prerequisites check — if any fail: skip, add to unprocessed list
7. Adopt approved, move to `seed/ingest/processed/`

**Teaching Path B (safe_to_auto_adopt: false):**
1. List files + summary table (File | Type | Summary | Apply Order)
2. State interpretation + planned action for each
3. Wait for approval
4. Record `adoption_status` + `adoption_action` + `adoption_reviewed_at` on the associated lug; move to `seed/ingest/processed/`

---

## Step 8: Track Schemas

### Autosave Checkpoint

```json
{
  "turn": 1,
  "ts": "2026-03-31T16:32:00Z",
  "focus": "Current work thread",
  "completed": false,
  "state": { "open_lugs": [], "decisions": [], "open_threads": [] }
}
```

Keep rolling window of 3: `ls -1 WAI-Spoke/.autosave/turn-*.json | sort -V | head -n -3 | xargs -r rm -f`

### Track Entry (JSONL)

```json
{
  "turn": 1, "ts": "2026-03-31T16:32:00Z",
  "focus": "Topic thread", "action": "Outcome summary",
  "thinking": "Full rationale (5-8 sentences)",
  "activity": ["Actions taken"], "decisions": ["Choices made"],
  "insights": ["New understandings"], "open": ["Unresolved threads"],
  "phase": "orientation|exploration|planning|execution|review|recovery",
  "evolution": "How understanding evolved",
  "completed": true
}
```

`completed: true` = clean turn. If absent at next wakeup → implies interruption.

---

## Step 9: Vibe Affinity Reference

| Vibe | Energy | Best for | Suppresses |
|------|--------|----------|------------|
| `build` | Creative | Features, epics | Bugs, routing |
| `fix` | Corrective | Bugs, reliability | Epics, features |
| `think` | Strategic | Architecture, signals | Mechanical tasks |
| `grind` | Mechanical | Batch tasks, thrift | Creative design |
| `ship` | Finishing | In-progress, close lugs | Starting new work |

### Step 9: Recent Completions Script

```bash
if [ -f "WAI-Spoke/runtime/spoke-changelog.jsonl" ]; then
    tail -5 WAI-Spoke/runtime/spoke-changelog.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    e = json.loads(line.strip())
    print(f\"  {e.get('ts','')[:10]} {e.get('type',''):<8} {e.get('title','')[:50]} [{e.get('result','')}]\")
"
fi
```

---

## Core Files Reference

| File | Purpose | Access |
|------|---------|--------|
| `WAI-State.json` | Identity, foundation, session state | UPDATE |
| `WAI-State-extended.json` | Migration, closeout, bootstrap | READ (on-demand) |
| `WAI-Spoke/skills/WAI-Skills.jsonl` | Skill registry | READ |
| `lugs/bytype/*/open/*.json` | Active work — open | UPDATE |
| `lugs/bytype/*/in_progress/*.json` | Active work — in progress | UPDATE |
| `WAI-LugIndex.jsonl` | Lug lookup index | READ (on-demand) |

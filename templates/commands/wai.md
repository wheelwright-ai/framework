# WAI Wakeup

Unified session start protocol — where are we, what's the status, what to work on.

## Execution Context

- **Nodes:** spoke, hub
- **Exposure:** spoke.chat:local, spoke.chat:external
- **Trigger:** Session start, user asks "wai point", or /wai command

## When to Use

- **Every session start** — Always run first
- **Orientation** — Lost context? Run /wai
- **After long break** — Get reoriented before work
- **Health check** — Periodic during long sessions (absorbs /wai-status)

---

## Wakeup Protocol

Follow these steps in order. Produce the complete briefing at the end.

### Step 1: Load Project Identity

Read `WAI-Spoke/WAI-State.json`:
- `wheel.name` — Project name
- `context.current_phase` — Current work phase
- `_session_state.last_modified_by` — Last AI to work here
- `_session_state.last_modified_at` — When last session ended
- `_session_state.session_count` — Total sessions completed
- `_project_foundation.identity.one_liner` — Project description
- `context.next_actions` — Recommended next steps

Read `WAI-Spoke/WAI-State.md` (if it exists and is relevant):
- Strategic vision and evolution log
- Key decisions and their rationale

Check `_session_state.last_compact` (if present):
- Read `compact_tokens_before` and `compact_tokens_after`
- Display token meter in header if available

Output header:
```
## WAI Point — {wheel.name}

**Phase:** {current_phase}
**Last session:** {last_modified_at} by {last_modified_by}
**Environment:** {tool} on {hostname} ({OS})
**Last compact:** Session {N} — ~{before}K → ~{after}K tokens
```

Note: If no `last_compact` in `_session_state`, omit the last line.

### Step 2: Check Git Status

Run `git status --short` and count lines:
- 0 lines → `✓ Clean`
- N lines → `⚠ N uncommitted`

Do NOT auto-commit or auto-resolve uncommitted changes. If uncommitted work exists, note it and ask the user if they want to resume or start fresh.

### Step 3: Check Hub Connection

From `WAI-State.json`, read `wheel.hub_path`:
- Path exists and is a directory → `✓ Connected`
- Missing or not a directory → `⚠ Not connected`

Read last teach date from sync history or `_session_state.last_closeout`.

### Step 4: Query Active Work

Read `WAI-Spoke/WAI-Lugs.jsonl` (one JSON object per line). Note: some entries use shorthand keys (`i`=id, `t`=title, `ty`=type, `s`=status).

**IMPORTANT: De-duplicate by ID first.** Build a map of ID → latest entry (WAI-Lugs.jsonl is append-only; reconciliation records override earlier entries with the same ID). All counts below use only the latest entry per ID.

**Status codes:** `s: "o"` or `"open"` = open; `s: "p"` or `"in-progress"` = in progress; `s: "c"`, `"closed"`, `"resolved"` = done (skip).

Count active lugs:
- **Flagged priority** — `priority == "before_next_epic"` AND `s == "o"`
- **Bugs** — `ty == "bug"` AND `s == "o"`
- **Verification needed** — `verify_on_closeout == true` AND `s == "o"`
- **In progress** — `s == "p"`
- **Open tasks** — `s == "o"` AND `ty != "epic"`
- **Epics** — `ty == "epic"` AND (`s == "o"` OR `s == "open"`)

Show top flagged priority item (i and t fields) if any exist.

Output:
```
### Active Work (Prioritized)

- 🚨 **Flagged Priority:** N items
- 🐛 **Bugs:** N open
- ✓ **Verification Needed:** N items
- ⏳ **In Progress:** N items
- 📋 **Open Tasks:** N items
- 🎪 **Epics (Blocked Until Above Clear):** N epics
```

### Step 5: Detect Autosave Checkpoints

**De-duplicate by ID first** — WAI-Lugs.jsonl is append-only. Reconciliation records are appended as overrides (same ID, but with `reconciled: true`). Build a map of ID → latest entry, then check only the latest.

```python
# Pseudocode for deduplication
latest_by_id = {}
for line in WAI-Lugs.jsonl:
    lug = json.loads(line)
    lid = lug.get('id') or lug.get('i')
    latest_by_id[lid] = lug  # Overwrite with latest

unreconciled = []
for lug in latest_by_id.values():
    if (lug.get('ty') == 'autosave' or lug.get('autosave') == True):
        if not lug.get('reconciled', False):
            unreconciled.append(lug)
```

If unreconciled autosaves found:
```
### ⚠️ Incomplete Work (N autosave checkpoints)
- Task: {task_context}
- Progress: {completion_estimate}
- **Resume:** `Green Light` | **Inspect:** `Red Light` | **Discard:** reconciled on next Closeout
```

### Step 6: Detect Pending Teachings

Check if `WAI-Spoke/seed/ingest/manifest.json` exists:
- If yes: read `files_taught` count and `taught_at` timestamp
- Output: "🎓 N file(s) awaiting review — taught {date}"
- **Action required:** Prioritize review before other work

Also check `WAI-Spoke/lugs/inbox/` for `.jsonl` files — these are lugs received from hub waiting to be processed. If present, note count and suggest `/wai-learn`.

### Step 7: Context Health

Estimate token footprint of loaded files:
- WAI-Spoke/WAI-State.json, WAI-State.md, WAI-Lugs.jsonl are typically loaded
- 1 token ≈ 4 bytes; report approximate token count
- Compare to 200K token budget

**Threshold recommendations:**
- Context > 70% → "Consider /wai-closeout before context fills"
- Hub sync > 7 days → "Consider /wai-teach to sync with hub"
- Turn count > 20 → "Run /wai-time for context health check"

### Step 8: Show Next Actions

From `WAI-State.json` → `context.next_actions` (first 5 items).

### Step 9: Show Available Skills

```
### Available Skills
- **/wai** — Unified briefing (this skill)
- **/wai-foundation** — Project identity, goals, boundaries
- **/wai-status** — Quick health check (hub, sync, session)
- **/wai-closeout** — Save session state, extract signals, commit
- **/wai-shipit** — Quality gates + closeout (for releases)
- **/wai-teach** — Push outbox to hub or spokes (auto-detects and initializes new spokes)
- **/wai-learn** — Process inbox teachings on wakeup
- **/wai-time** — Token usage estimate
- **/wai-rules** — Project boundaries and guidelines
- **/wai-principles** — WAI principles P1-P9
```

---

## Complete Briefing Format

```
## WAI Point — {project_name}

**Phase:** {current_phase}
**Last session:** {timestamp} by {agent}
**Environment:** {tool} on {hostname} ({OS})

### Active Work (Prioritized)
- 🚨 **Flagged Priority:** N items
- 🐛 **Bugs:** N open
- ✓ **Verification Needed:** N items
- ⏳ **In Progress:** N items
- 📋 **Open Tasks:** N items
- 🎪 **Epics (Blocked Until Above Clear):** N epics

### Context Health
- Hub: ✓ Connected / ⚠ Not connected
- Last teach: {date} / never
- Git: ✓ Clean / ⚠ N uncommitted

### Next Actions
- {action 1}
- {action 2}

### Available Skills
- **/wai** — Unified briefing
- **/wai-closeout** — Save session state
- **/wai-shipit** — Quality gates + closeout
- **/wai-teach** — Push to hub/spokes
- **/wai-learn** — Process inbox
- **/wai-time** — Token usage
- **/wai-rules** — Project boundaries

---
*Ask "what should I work on?" for recommendations*
```

---

## Health Check (absorbs /wai-status)

This logic runs inline during wakeup. `/wai-status` as a standalone command shows this section only.

| Metric | How to Check | Threshold |
|--------|-------------|-----------|
| Hub connection | `wheel.hub_path` is a real directory | > 0 days disconnected → warn |
| Hub sync age | Days since last teach | > 7 days → recommend teach |
| Context usage | Estimated tokens / 200K | > 70% → recommend closeout |
| Git status | `git status --short` line count | Any uncommitted → note |
| Turn count | Current session turns | > 20 → suggest /wai-time |

Output format for standalone `/wai-status`:
```
### WAI Status

**Hub:** ✓ Connected / ⚠ Not connected
**Last teach:** {date}
**Git:** ✓ Clean / ⚠ N uncommitted
**Context:** ~{K} tokens / 200K budget

**Recommendations:**
- {action if threshold crossed}
```

---

## Lug Type Reference

When reading WAI-Lugs.jsonl:
- `ty: "bug"` — Bugs requiring fixes
- `ty: "epic"` — Large multi-session efforts (blocked until tasks clear)
- `ty: "task"`, `ty: "feature"`, `ty: "review"` — Standard work items
- `ty: "autosave"` — Session checkpoint (check `reconciled` field)
- `ty: "session-summary"` — Completed session record (skip, already done)
- `ty: "signal"` — High-impact decision captured for cross-session learning
- `ty: "core-protocol"` — Framework protocol documentation lug

---

## Related Skills

- **/wai-closeout** — End session, reconcile autosaves, commit
- **/wai-shipit** — Quality gates + closeout for releases
- **/wai-rules** — Project boundaries and scope
- **/wai-principles** — WAI principles P1-P9

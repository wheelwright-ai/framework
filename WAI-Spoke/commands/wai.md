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

From `WAI-State.json`, read the hub path — check `wheel.hub_path` first, fall back to `wheelwright.hub_path` for older spokes:
- Path exists and is a directory → `✓ Connected`
- Both fields are null or missing → `⚠ Not connected`

**Warning:** If `hub_path` is configured but the directory is missing or inaccessible, surface a prominent warning: `⚠ CRITICAL: Configured hub_path is inaccessible. Check path or ask user.`

Read last teach date from sync history or `_session_state.last_closeout`.

### Step 3a: Check Hub for New Teachings (Spoke only)

If `hub_path` is connected, check for new teachings available from the hub:

1. **Check teachings:** List `.teaching` files in `{hub_path}/framework/`
   - This path is a symlink the hub maintains pointing to the framework's `teachings/` folder
   - If the path does not exist or is empty, skip silently
   - Compare filenames against `WAI-Spoke/seed/ingest/processed/` (create this directory if it does not exist)
   - Any `.teaching` file present in hub but absent from `processed/` is new
   - If new teachings found: note in briefing "📥 {N} new teaching(s) available — run `/wai-learn` to ingest"

2. **Check lug inbox:** Check `WAI-Spoke/lugs/inbox/` for `.jsonl` files not yet processed
   - If present, note count and suggest `/wai-learn`

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

De-duplicate by ID first — WAI-Lugs.jsonl is append-only. Build a map of ID → latest entry, then check only the latest for unreconciled autosaves (`ty == "autosave"` AND `reconciled` is false/absent).

If unreconciled autosaves found, show task context, completion estimate, and offer: Resume (Green Light) / Inspect (Red Light) / Discard on next Closeout.

### Step 5a: Read Session Track (Resume / Recovery)

Check for previous session tracks in `WAI-Spoke/session-*/track.jsonl`:

1. List `WAI-Spoke/session-*/` directories sorted by name (newest last)
2. If no session directories exist → skip silently (legacy spoke, no tracks yet)
3. Read the most recent `track.jsonl`
4. Check if previous session had a clean closeout:
   - Compare `_session_state.last_closeout` against last point's `ts` field
   - If closeout timestamp > last point timestamp → **resume** (clean end)
   - If closeout timestamp < last point timestamp or missing → **recovery** (session interrupted)
5. Read last 5 points and produce a catch-up brief:
   - Arc: how focus shifted across turns (from `evolution` fields)
   - Decisions: accumulated from all points
   - Open threads: `open` fields from final points
   - Recommend: what to do next based on track state

If recovery mode, highlight incomplete work and ask user whether to resume or start fresh.

### Step 5b: Read Taste Files

Load user and project preferences:

1. Check for `WAI-Spoke/taste.spoke.yaml` — if exists, read all entries with `status: accepted`
2. Check hub connection. If connected, check for `{hub_path}/taste.user.yaml` — if exists, read accepted entries
3. Apply accepted preferences to session behavior (communication style, workflow, approach)
4. If either taste file has entries with `status: proposed`:
   - Present proposed entries: "Historian suggests: {preference}. Accept / Reject?"
   - Wait for user response before proceeding
5. If no taste files exist → skip silently

Note: `taste.spoke` overrides `taste.user` for project-specific matters. User's direct instructions override both.

### Step 5c: Check Historian Threshold

1. If `WAI-Spoke/advisors/historian/` does not exist → skip silently
2. Read `WAI-Spoke/advisors/historian/passes.jsonl` (if exists) to find last reviewed session and point count
3. Count total unreviewed points across all session tracks since last pass
4. If >= 30 unreviewed points: "Historian: {N} unreviewed points across {M} sessions. Run `/wai-review` when ready."
5. If < 30 → silent

### Step 6: Detect Pending Teachings (Local Inbox)

Hub teaching detection was handled in Step 3a. This step checks the local inbox only.

Check if `WAI-Spoke/seed/ingest/manifest.json` exists:
- If yes: read `files_taught` count and `taught_at` timestamp
- Output: "🎓 N file(s) awaiting review — taught {date}"
- **Action required:** Prioritize review before other work

Check `WAI-Spoke/seed/ingest/` for `.track.jsonl` files. If present:
- Create `WAI-Spoke/session-{ts}/` (ts from first JSON line's `ts` field) and move file in as `track.jsonl`

### Step 7: Context Health

Estimate token footprint (WAI-State.json + WAI-State.md + WAI-Lugs.jsonl). 1 token ≈ 4 bytes. Compare to 200K budget.

Thresholds: Context > 70% → recommend closeout. Hub sync > 7 days → recommend teach. Turn count > 20 → suggest /wai-time.

### Step 8: Show Next Actions

From the de-duplicated lug map: show up to 3 wakeup_visibility lugs, then flagged priority, then in-progress, then bugs, then open tasks (fill to 5 total). Format as a prioritized list.

### Step 9: Initialize Session Track

1. Generate session ID from current UTC time: `session-YYYYMMDD-HHMM`
2. Create directory: `WAI-Spoke/session-{id}/`
3. Update `_session_state.track_path` in WAI-State.json to point to the new track
4. The first point will be written after this wakeup briefing completes (phase: `orientation`)

Note: After each subsequent turn in this session, append a point to `WAI-Spoke/session-{id}/track.jsonl`. Each point is a JSON object with fields: `turn` (integer), `ts` (ISO-8601 UTC), `focus` (short phrase), `action` (what happened), `thinking` (agent reasoning, 2-3 sentences), `activity` (list of actions taken), `decisions` (array), `insights` (array), `open` (unresolved questions), `phase` (one of: orientation/exploration/planning/execution/review/recovery), `evolution` (null on first point, else `"previous -> current: reason"`).

### Step 10: Show Available Skills

Available skills vary by spoke. Standard set:
- **/wai** — Unified briefing (this skill)
- **/wai-foundation** — Project identity, goals, boundaries
- **/wai-status** — Quick health check
- **/wai-closeout** — Save session state, extract signals, commit
- **/wai-shipit** — Quality gates + closeout
- **/wai-teach** — Push outbox to hub or spokes
- **/wai-learn** — Process inbox teachings
- **/wai-review** — Historian review of session tracks
- **/wai-time** — Token usage estimate
- **/wai-rules** — Project boundaries
- **/wai-principles** — WAI principles P1-P9

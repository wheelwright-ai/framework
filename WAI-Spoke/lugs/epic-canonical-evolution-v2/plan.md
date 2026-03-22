# Canonical Evolution v2 — Implementation Plan

**Parent:** epic-canonical-evolution-v2
**Execution order:** Tier 1 → Tier 2 → Tier 3 (Tier 3 items get child lugs before execution)

---

## Tier 1 — State Correctness

### E2-01: Adoption Marker Sync

**Perceive:**
`WAI-State.json._migration_state.adoption_markers.canonical_state_migration.adopted` is `false`.
The implementation lug `implementation-canonical-state-migration-v1` in `WAI-Lugs.jsonl` has `status: "implemented"`.
These contradict. Every future wakeup tells agents the migration is pending when it is done.

**Execute:**
In `WAI-Spoke/WAI-State.json`:
1. Set `canonical_state_migration.adopted = true`
2. Set `canonical_state_migration.adopted_at` = current UTC timestamp
3. Set `canonical_state_migration.adopted_by` = executing agent name
4. Set `canonical_state_migration.receipt_id` = `"receipt-state-migration-20260322"`
5. Append to `_migration_state.framework_migrations_applied[]`:
   ```json
   {
     "migration_id": "canonical-state-migration-v1",
     "applied_at": "<UTC>",
     "applied_by": "<agent>",
     "receipt_id": "receipt-state-migration-20260322",
     "rollback_checkpoint": "WAI-Lugs.jsonl.backup",
     "capabilities_adopted": ["canonical_state_schema", "canonical_workflow_types"]
   }
   ```
6. Append to `_migration_state.capability_adoptions[]`:
   ```json
   {"capability": "canonical_state_schema", "status": "active", "adopted_at": "<UTC>", "migration_batch": "canonical-state-migration-v1"}
   ```

**Verify:**
- `cat WAI-Spoke/WAI-State.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['_migration_state']['adoption_markers']['canonical_state_migration']['adopted'])"` → `True`
- `_migration_state.framework_migrations_applied` has 2 entries (baseline + this one)

---

### E2-02: Migration Receipts

**Perceive:**
`_migration_state.migration_receipts[]` is empty. Two migrations are recorded as applied
(`canonical-runtime-baseline-v1` in `framework_migrations_applied`), but no receipts exist.
This breaks rollback safety — there is no evidence trail for either migration.

**Execute:**
In `WAI-Spoke/WAI-State.json`, populate `_migration_state.migration_receipts[]` with:
```json
[
  {
    "receipt_id": "receipt-runtime-baseline-20260319-0935",
    "migration_id": "canonical-runtime-baseline-v1",
    "issued_at": "2026-03-19T09:35:00Z",
    "issued_by": "OpenCode GPT-5.4",
    "rollback_checkpoint": "state-backup-20260319-0930.json",
    "status": "active",
    "notes": "Retroactively created — migration was applied but receipt was not written at time of adoption"
  },
  {
    "receipt_id": "receipt-state-migration-20260322",
    "migration_id": "canonical-state-migration-v1",
    "issued_at": "<current UTC>",
    "issued_by": "<agent>",
    "rollback_checkpoint": "WAI-Lugs.jsonl.backup",
    "status": "active",
    "notes": "Adoption marker corrected — implementation was done in session 50 but marker was not flipped"
  }
]
```

**Verify:**
- `migration_receipts` array has 2 entries
- Both have `status: "active"`
- Both reference an accessible rollback checkpoint

---

### E2-03: track_path Stale Format

**Perceive:**
`WAI-State.json._session_state.track_path` = `"WAI-Spoke/sessions/track_20260318-wakeup.jsonl"` — flat file format.
Canonical format is `WAI-Spoke/sessions/session-YYYYMMDD-HHMM/track.jsonl`.
This tells agents the wrong track location at wakeup.

**Execute:**
1. Check which session directories exist: `ls WAI-Spoke/sessions/`
2. Identify the most recent session directory (expect `session-20260319-1616/` or `session-20260322-0000/`)
3. In `WAI-State.json._session_state`:
   - Update `track_path` to `"WAI-Spoke/sessions/session-20260319-1616/track.jsonl"` (last real session)
   - Update `last_session_id` to `"session-20260319-1616"` if not already accurate

**Verify:**
- Referenced file path exists on disk
- Format matches `WAI-Spoke/sessions/session-YYYYMMDD-HHMM/track.jsonl` pattern

---

### E2-04: WAI-Signals.jsonl Retirement

**Perceive:**
`WAI-Spoke/WAI-Signals.jsonl` exists (56KB). Signals are now canonically high-impact lugs in
`WAI-Lugs.jsonl`. The file header says "RETIRED" per the audit, but the file still sits in the
WAI-Spoke root alongside the canonical files — creating a stale competing source of truth.

**Execute:**
1. Read `WAI-Spoke/WAI-Signals.jsonl` — verify header says RETIRED and no new signals exist
2. Check if any signals in the file are NOT already present in `WAI-Lugs.jsonl` (compare by id or timestamp)
3. If any are missing from `WAI-Lugs.jsonl`: migrate them as high-impact lugs before retiring
4. Move file to `WAI-Spoke/seed/ingest/processed/WAI-Signals-retired-20260322.jsonl`
   (preserves content, removes from live root, documents retirement)
5. Append a signal lug to `WAI-Lugs.jsonl` noting the retirement

**Verify:**
- `WAI-Spoke/WAI-Signals.jsonl` no longer exists in root
- Archived copy exists in `seed/ingest/processed/`
- Any non-migrated signals are now in `WAI-Lugs.jsonl`

---

### E2-05: Lug Backup Cleanup

**Perceive:**
Two backup files in `WAI-Spoke/`:
- `WAI-Lugs.jsonl.backup` (389KB, 2026-03-19)
- `WAI-Lugs.jsonl.backup-20260318-035344` (343KB)
Also: open lug `task-lug-storage-cleanup-v1` already tracks this risk.
These may contain trapped data (lugs written before a migration that are now invisible).

**Execute:**
1. Diff `WAI-Lugs.jsonl.backup` against `WAI-Lugs.jsonl` — identify any lugs in backup NOT in current file
2. For any rescued lugs: append to `WAI-Lugs.jsonl` with `rescued_from_backup: true` and original timestamp
3. Move both backup files to `WAI-Spoke/seed/ingest/processed/` for archival
4. Update `task-lug-storage-cleanup-v1` status to `implemented`

**Verify:**
- No `.backup` files in `WAI-Spoke/` root
- No lugs were silently lost (diff confirms)
- `task-lug-storage-cleanup-v1` status updated

---

## Tier 2 — Protocol Consistency

### E2-06: wai-lug-advisor.md Signal Routing Fix

**Perceive:**
`templates/commands/wai-lug-advisor.md` line 65 says:
`| signal | High-impact decision or insight (impact >= 8) | No — record in WAI-Signals.jsonl |`
Every other protocol file (`wai.md`, `wai-closeout.md`, `wai-principles.md`) says signals are
high-impact lugs in `WAI-Lugs.jsonl`. This file is the dedicated lug authoring guide — it is the
worst possible place to have a wrong signal routing instruction.

**Execute:**
In `templates/commands/wai-lug-advisor.md`, find and update the signal row in the lug type table:
- Old: `No — record in WAI-Signals.jsonl`
- New: `No — signal IS a lug (impact >= 8); append to WAI-Lugs.jsonl and copy qualifying lugs to hub bulletin`

Also propagate the fix to `WAI-Spoke/commands/wai-lug-advisor.md` if it exists (check first).

**Verify:**
- Grep for `WAI-Signals.jsonl` in `templates/commands/` — should return zero results after fix
- The signal row in the type table correctly describes the lug-based model

---

### E2-07: WAI-Guide.md Stale Patterns

**Perceive:**
`WAI-Spoke/WAI-Guide.md` is listed as the first file agents should read (`ai_rules.context_loading`).
It contains `select(.status == "published")` as the sample filter — a v1-era status value that
returns zero results against all current lugs (which use `open`, `in_progress`, `accepted`, etc.).
An agent following this guide literally will query lugs and get nothing, not knowing why.

**Execute:**
1. Read `WAI-Spoke/WAI-Guide.md` in full to find all stale patterns
2. Update sample filter: `select(.status == "published")` → `select(.status == "open" or .status == "in_progress")`
3. Check for any other references to `WAI-Signals.jsonl`, `BRIEF.md`, `WAI-Manifest.yaml`, or legacy paths
4. Update or remove stale references found

**Verify:**
- Sample filter query against `WAI-Lugs.jsonl` returns results (not empty)
- No references to retired artifacts remain in the quick-reference sections

---

### E2-08: Adoption Marker Enforcement at Closeout

**Perceive:**
`canonical_state_migration` stayed `false` after implementation because nothing in the closeout
protocol enforces the link between "implementation lug reached `implemented`" and "flip the
adoption marker." This is structural — it will silently recur for every future capability.

**Execute:**
In `templates/commands/wai-closeout.md` (and WAI-Spoke copy), add a step to the closeout
protocol — after the existing implementation lug reconciliation step:

```
### Adoption Marker Sync (after each session)
For each lug in WAI-Lugs.jsonl where type = "implementation" and status = "implemented":
  1. Check if a corresponding adoption_markers entry exists in WAI-State.json
  2. If adoption_markers[<migration_id>].adopted = false, update to true + record adopted_at/by
  3. Log: "Synced adoption marker: <migration_id>"
If no mismatches: "Adoption markers current — no sync needed"
```

**Verify:**
- Step appears in closeout protocol with clear trigger condition
- The mechanism would have caught the `canonical_state_migration` marker gap if it had been running

---

### E2-09: Single Source of Truth for Lug Storage

**Perceive:**
"Where do lugs go?" is answered in 5+ places with contradictions:
- `wai-lug-advisor.md` → `WAI-Signals.jsonl` (wrong, being fixed in E2-06)
- `wai.md` Step 4 → `WAI-Lugs.jsonl` (correct)
- `wai-closeout.md` → `WAI-Lugs.jsonl` (correct)
- `WAI-Guide.md` → `WAI-Lugs.jsonl` (correct but stale filter)
- `goal-state-wheelwright.md` section 5.1 → `WAI-Lugs.jsonl` (correct)
No file says "this is the single canonical declaration." Contradiction recurs every time one file
is updated without the others.

**Execute:**
1. Add a canonical declaration block to `templates/commands/wai-lug-advisor.md` (the authoritative
   lug authoring guide) near the top:

   ```
   ## Canonical Storage
   Lugs are stored in: WAI-Spoke/WAI-Lugs.jsonl (append-only JSONL, one object per line)
   Signals: are lugs with impact >= 8 — no separate file
   Inbox/outbox: WAI-Spoke/lugs/inbox/ and outbox/ are the delivery channel — not durable storage
   This is the single canonical answer. All other protocol files defer to this declaration.
   ```

2. Add a cross-reference to this declaration in `wai.md` Step 4 comment and `wai-closeout.md` signal step.

**Verify:**
- `wai-lug-advisor.md` has a clearly labelled "Canonical Storage" section near the top
- Grep for `WAI-Signals.jsonl` across `templates/commands/` returns zero results
- `wai.md` and `wai-closeout.md` both reference `wai-lug-advisor.md` as the authority

---

## Tier 3 — Architectural Completion (Track and Plan)

Each of these needs a child lug with its own BRIEF.md before execution.

### E2-10: Hub Signals Bulletin

**Perceive:**
Goal-state section 5.3 defines `WAI-Hub/Signals/incoming/` and `WAI-Hub/Signals/processed/` as
the hub bulletin board. Qualifying lugs (impact > 7) are copied there at closeout. Other spokes
inspect `incoming/` on wakeup. This directory does not exist.

**Planned approach:**
- Create `hub/WAI-Hub/Signals/incoming/` and `processed/` directories
- Add closeout step: copy lugs with impact > 7 to hub bulletin at closeout
- Add wakeup step: inspect hub bulletin during hub teachings discovery (Step 3a)
- Child lug: `lug-hub-signals-bulletin-v1`

---

### E2-11: PEV as Linked Lugs

**Perceive:**
Goal-state section 4.8 defines PEV as a chain of linked lugs (Perceive lug → Execute lug →
Verify lug). Current implementation stuffs perceive/execute/verify as optional fields on a single
lug. This means the relation between problem framing, intended action, and proof is invisible
to any agent doing cross-lug analysis.

**Planned approach:**
- Define the PEV link schema (each lug gets `pev_role: perceive|execute|verify` and `pev_chain_id`)
- Update `wai-lug-advisor.md` with PEV authoring guidance
- Add historian pattern detector for unverified execute lugs (execute exists, verify missing)
- Child lug: `lug-pev-linked-chain-v1`

---

### E2-12: Lug Type Schema Cleanup

**Perceive:**
Goal-state section 6.5 defines canonical top-level types: `epic`, `work`, `decision`, `finding`,
`test`, `session-summary`. `task`, `bug`, and `feature` become `work.kind` — not top-level types.
`WAI-Lugs.jsonl` has hundreds of lugs with `type: "task"`, `type: "bug"`, `type: "feature"`.

**Planned approach:**
- This is a migration, not a deletion — dual-read required
- Add `work.kind` field support to `wai-lug-advisor.md`
- New lugs use canonical types; existing lugs are read with dual-read compatibility
- No bulk rewrite of existing lugs — compatibility bridge only
- Child lug: `lug-lug-type-schema-v1`

---

## Execution Order

```
E2-01 (adoption marker)
E2-02 (receipts)          ← do together, both touch WAI-State.json
E2-03 (track_path)

E2-04 (signals retirement)
E2-05 (backup cleanup)    ← do together, both touch WAI-Spoke root

E2-06 (lug-advisor fix)
E2-07 (guide stale patterns)
E2-09 (single source of truth)  ← do together, all touch templates/commands/

E2-08 (closeout enforcement)    ← after E2-06/07/09 so the protocol is clean first

E2-10, E2-11, E2-12 ← each needs child lug authored first, then execution session
```

## Definition of Done

This epic is complete when:
1. All Tier 1 and Tier 2 items are verified
2. Tier 3 items each have a child lug authored (execution is a separate session per item)
3. `WAI-State.json._migration_state` is truthful end-to-end
4. Zero contradictions exist across `templates/commands/` on lug storage location
5. The wakeup protocol surfaces this epic as resolved on next session

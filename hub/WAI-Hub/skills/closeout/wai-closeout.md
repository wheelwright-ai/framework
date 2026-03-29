# WAI Closeout — Hub Protocol

**Hub override of the spoke closeout. Includes all spoke steps plus hub superpowers: spoke distribution, fleet signal propagation, teaching delivery to all registered spokes, and hub state persistence.**

> This file is the complete closeout protocol for hub nodes. It replaces `WAI-Spoke/skills/closeout/wai-closeout.md` via the hub override resolution rule. All spoke steps are preserved; hub-only sections are marked `[HUB ONLY]`.

---

## Execution Context

- **Nodes:** hub
- **Exposure:** hub.chat:local
- **Resolution:** `WAI-Hub/skills/closeout/wai-closeout.md` takes precedence over `WAI-Spoke/skills/closeout/wai-closeout.md` on hub nodes

---

## Before Beginning

Read `_session_state.last_closeout` from `WAI-State.json` — store as `old_last_closeout`. This value is used in Step 9b to identify new signals from this session. It must be captured before Step 5 overwrites it.

**[HUB ONLY]** Also read:
- `hub/registry.yaml` — spoke list for distribution steps
- Note `hub/WAI-Lugs.jsonl` — will receive a hub session summary in Step 1b

---

## Step 0: Idempotency and Concurrency Setup

Generate deterministic session ID: `session-$(date -u +%Y%m%d-%H%M%S)`

Ownership-based concurrency: update active implementation lug to `in_progress` before starting. Other agents seeing `in_progress` with recent activity must not take over.

Check `_closeout_state.duplicate_detection_keys.session_summaries` for existing session ID.

---

## Step 1: Lug Reconciliation

Consolidate autosave checkpoints into permanent record.

1. Read `WAI-Spoke/WAI-Lugs.jsonl`
2. Find `ty="autosave"` AND `reconciled=false`
3. Consolidate into ONE `session-summary` lug
4. Mark autosave lugs `reconciled: true`, `s: "c"`
5. Append session-summary lug to `WAI-Spoke/WAI-Lugs.jsonl`

Session-summary lug format:
```json
{
  "i": "ss-{session_id}",
  "ty": "session-summary",
  "t": "Session N summary",
  "s": "c",
  "ca": "ISO-8601",
  "gb": "agent-name",
  "session_number": N,
  "accomplished": [],
  "files_touched": [],
  "decisions": [],
  "incomplete_work": {"tasks": [], "blockers": [], "next_steps": []},
  "autosaves_reconciled": []
}
```

---

## Step 1b: Hub Session Summary [HUB ONLY]

In addition to the spoke session-summary, append a `hub-session-summary` lug to `hub/WAI-Lugs.jsonl`:

```json
{
  "id": "hub-ss-{session_id}",
  "type": "hub-session-summary",
  "session_id": "{session_id}",
  "timestamp": "ISO-8601",
  "agent": "{model}",
  "spoke_count": N,
  "fleet_status": "healthy | degraded | critical",
  "teachings_distributed": ["teaching-id-1", "..."],
  "signals_published": ["signal-id-1", "..."],
  "lug_reviews_processed": N,
  "spoke_health_reports": [{"spoke_id": "...", "status": "...", "score": "..."}],
  "accomplished": [],
  "incomplete_work": {}
}
```

This is the hub's institutional memory — a cross-session record of fleet activity.

---

## Step 2: Signal Extraction

Review session for decisions or learnings with `impact >= 8`.

For each qualifying signal, create a high-impact lug in `WAI-Spoke/WAI-Lugs.jsonl`:

```json
{
  "id": "signal-YYYYMMDD-HHMM-brief-description",
  "type": "signal",
  "title": "...",
  "impact": 8-10,
  "created_by": "agent",
  "created_at": "ISO-8601",
  "fw_ver": "{current_fw_ver}"
}
```

**[HUB ONLY]** Hub-origin signals (cross-fleet patterns, architectural insights) should also be appended to `hub/WAI-Lugs.jsonl` with `"hub_signal": true` flag — these become candidates for the knowledge base curator.

---

## Step 3: Incomplete Work Capture

Document unfinished work with continuation guidance.

Store in session-summary `incomplete_work` field AND in `_session_state.next_session_recommendation`.

**[HUB ONLY]** Also capture any pending fleet operations:
- Unreachable spokes from wakeup Step 4.4
- Teaching delivery debt (spokes that haven't received current teachings)
- Unprocessed lug-review returns

Include in `next_session_recommendation`: "Fleet follow-ups: {list}"

---

## Step 4: Version Increment

Parse `wheel.version` from `WAI-State.json`. Increment patch. Write back.

---

## Step 5: State Update

Update session metadata in `WAI-State.json`:
- `_session_state.session_count` += 1
- `_session_state.last_closeout` = current UTC timestamp
- `_session_state.last_modified_by` = current AI model
- `_session_state.last_modified_at` = current UTC timestamp
- `_session_state.next_session_recommendation` = what to do next
- `_session_state.track_path` = current session track path
- `_migration_state.last_migration_check` = current UTC timestamp

---

## Step 5b: Adoption Marker Sync

Check `WAI-Lugs.jsonl` for `type="implementation"` + `status="implemented"` lugs. For each, verify `_migration_state.adoption_markers[<key>].adopted = true`. Fix any false markers.

---

## Step 6: Finalize Session Track

Write final point to session `track.jsonl` (phase: `review`). Do NOT delete track file.

---

## Step 7: Documentation Updates

Update CHANGELOG.md. Update any files affected by session work.

---

## Step 8: Lug Dogfooding

Validate lugs created/modified this session (excluding session-summary and autosave types):
- PEV fields present and actionable?
- Self-contained? (no conversation-dependent references)
- Could a naive agent understand cold?

Present scope to user, await approval, fix gaps found.

---

## Step 9: Outgoing Delivery

Deliver hub spoke's own outgoing lugs:

1. Check `WAI-Spoke/lugs/outgoing/` for `.jsonl` files
2. If empty: skip, log "Outgoing empty"
3. For each file: copy to `{hub_path}/WAI-Spoke/lugs/incoming/` (self-delivery loop)
4. Hub routes to appropriate destination based on `destination_wheel_id`

---

## Step 9b: Teaching Generation + Hub Publish

Generate current teaching files from session changes. Publish to `{hub_path}/teachings_repo/{spoke_id}/current/`.

Conditions:
- At least one migration-relevant framework object changed, OR new high-impact lug with `created_at > old_last_closeout`
- `hub_path` set and `teachings_repo/` accessible

Generate teaching files into `teachings/`. Each must include `## Prerequisites` and `## Batch Sequence` blocks.

Publish: move old current to `archive/{family_key}/`, copy new current into `current/`. Update `index.json`.

---

## Step 9c: Hub Signal Bulletin

Publish high-impact lugs to hub bulletin for cross-spoke visibility.

For each lug where `type == "signal"` AND `impact > 7` AND `status != "archived"`:
1. Check if `{hub_path}/WAI-Hub/signals/incoming/{lug-id}.json` already exists
2. If not: write full lug JSON to that path

---

## Step 9d: Spoke Health Report

Send self-health snapshot to hub registry:

1. Load `templates/health-check.jsonl`
2. Run each check, score PASS/FAIL
3. Write health lug to `{hub_path}/WAI-Spoke/seed/ingest/spoke-health-{spoke_id}-{session_id}.json`

---

## Step 9e: Spoke Distribution [HUB ONLY]

**Distribute teachings and signals from the hub to all registered spokes.**

This is the hub's primary distribution responsibility. Every spoke checks its own `seed/ingest/` at wakeup — this step ensures the hub's current knowledge reaches them.

### 9e.1: Teaching Distribution

```bash
# For each registered spoke in hub/registry.yaml
for spoke in registry.spokes:
    spoke_ingest="${spoke.path}/WAI-Spoke/seed/ingest/"

    # Check if spoke ingest dir is accessible
    if not accessible(spoke_ingest):
        log(f"Skipping {spoke.name}: seed/ingest not accessible")
        continue

    # For each teaching in hub current/
    for teaching in hub/teachings_repo/spoke/current/*.teaching:
        teaching_name = basename(teaching)
        dest = f"{spoke_ingest}{teaching_name}"
        processed = f"{spoke.path}/WAI-Spoke/seed/ingest/processed/{teaching_name}"

        # Skip if already delivered or already processed by spoke
        if exists(dest) or exists(processed):
            continue

        # Deliver
        copy(teaching, dest)
        log(f"Delivered to {spoke.name}: {teaching_name}")
```

Report: "Teaching distribution: N teachings delivered to M spokes | K already current | L spokes unreachable"

### 9e.2: Signal Bulletin Distribution

Signals are available to spokes via `WAI-Hub/signals/incoming/` (which Step 9c populates). No additional copying needed — spokes read the hub bulletin directly at wakeup.

If `WAI-Hub/signals/incoming/` has grown significantly (> 50 files), move acknowledged signals to `processed/` to keep the inbox manageable.

### 9e.3: Distribution Lug

Append a distribution record to `hub/WAI-Lugs.jsonl`:

```json
{
  "id": "distribution-{session_id}",
  "type": "distribution-run",
  "timestamp": "ISO-8601",
  "teachings_delivered": N,
  "spokes_reached": M,
  "spokes_unreachable": ["spoke-name", "..."],
  "teaching_names": ["..."],
  "fw_ver": "{current_fw_ver}",
  "created_by": "hub-closeout"
}
```

---

## Step 9f: Hub State Persistence [HUB ONLY]

Finalize `hub/WAI-Lugs.jsonl` with the hub session summary from Step 1b (update if distribution results are now available).

Ensure `hub/registry.yaml` is current — update `last_seen` for this hub session.

---

## Step 10: Summary Generation

Present to user:
- What was accomplished
- Signals extracted
- Files modified
- Track stats (turns, phase distribution, open threads)
- **[HUB ONLY]** Fleet summary: teachings distributed to N spokes, signals published, lug reviews processed
- Incomplete work with continuation guidance
- New version number

---

## Step 11: Git Commit + Push

Stage and commit:

```bash
git add WAI-Spoke/
git add hub/WAI-Lugs.jsonl hub/registry.yaml   # [HUB ONLY] — hub state files
git add [other session files]
git status
```

**Commit message format:**
```
Hub Session [N]: {accomplishments} | Fleet: {N} spokes | v{version}
```

Push immediately after commit.

---

## Step 12: Idempotency Summary and Cleanup

Display final summary of completed vs skipped operations. Clear `_closeout_state.current_session_id`. Record `last_closeout_check`.

---

## Success Criteria

**All spoke criteria, plus:**
- [ ] Hub session summary written to `hub/WAI-Lugs.jsonl`
- [ ] Hub-origin signals flagged and appended to `hub/WAI-Lugs.jsonl`
- [ ] Spoke distribution completed (teachings delivered to all accessible spokes)
- [ ] Distribution run lug appended to `hub/WAI-Lugs.jsonl`
- [ ] `hub/registry.yaml` `last_seen` updated
- [ ] Hub signal bulletin current (Step 9c)
- [ ] Commit includes `hub/` files

---

## Language Rules

**Never say:** "Probably saved", "Should be committed", "I think it persisted"
**Always say:** "Verified with git status", "Confirmed commit with git log", "Distribution completed: N spokes reached"

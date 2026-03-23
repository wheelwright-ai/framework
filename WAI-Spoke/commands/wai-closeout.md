# WAI Closeout

**Session State Preservation Protocol**

Save where we are so we can pick up seamlessly in a new session.

---

## Execution Context

- **Nodes:** spoke, hub
- **Exposure:** spoke.chat:local, spoke.chat:external
- **Paths Required:** spoke_path (current directory with WAI-Spoke/)

---

## When to Use

- End of any work session
- Before context fills up (>70% capacity)
- Before breaks or stopping work
- When switching to different task/project
- After completing a milestone

## Prerequisites

- WAI-Spoke/ directory exists
- WAI-State.json is valid
- Git repository initialized
- Work worth preserving exists

## Follow-ons

- New session — Will auto-learn from inbox on wakeup

## Use Cases

**Use Case 1: End of Day**
- Situation: Finished working, need to preserve progress
- Action: Run closeout to save state
- Result: Next session loads exactly where you left off

**Use Case 2: Context Near Capacity**
- Situation: `/wai-time` shows >70% context used
- Action: Run closeout before context overflow
- Result: State saved, can continue in fresh session

**Use Case 3: Incomplete Work**
- Situation: Task partially done, need to stop
- Action: Run closeout with detailed incomplete work capture
- Result: New agent can identify and continue the work

**Use Case 4: Milestone Complete**
- Situation: Feature or fix finished
- Action: Run closeout to checkpoint progress
- Result: Clean save point, version incremented

---

## Purpose

Persist session state with enough detail that a new agent/session can:
- Understand what was accomplished
- Identify incomplete work remaining
- Continue where we left off

---

## Closeout Procedure

**Before beginning:** Read `_session_state.last_closeout` from `WAI-State.json` and store it as `old_last_closeout`. This value is used in Step 9b to identify new signals written this session. It must be captured now — Step 5 will overwrite it.

### 0. Idempotency and Concurrency Setup

**Purpose:** Ensure replay safety and handle concurrent closeout attempts.

> **NOT IMPLEMENTED — DEFERRED:** File locking (`.closeout.lock`, `.state.lock`, `.lugs.lock`) and migration checkpoints (`.migration-checkpoint.json`) are NOT implemented. These are deferred to a future batch. Concurrency is handled by the ownership-based model below.

**Session ID Generation:**
1. Generate deterministic session ID: `session-$(date -u +%Y%m%d-%H%M%S)`
2. Check `_closeout_state.duplicate_detection_keys.session_summaries` for existing session ID
3. If duplicate session ID exists: append `-2`, `-3`, etc. until unique

**Concurrency Protection (Ownership-Based):**
> File locking is deferred. Concurrency is handled by ownership:
> 1. Before starting closeout, agent updates the active implementation lug to `in_progress` with `updated_at` timestamp
> 2. Other agents seeing a lug in `in_progress` with activity within 4 hours MUST NOT take over
> 3. If `in_progress` with no `updated_at` activity >4 hours: consider stale, ask user before proceeding
> 4. This model is explicitly limited to human-in-loop AI collaboration — not designed for fully autonomous concurrent agents

**Serialized Operations (Graceful Failure):**
- Teaching distribution: Check for `.teaching-distribution.lock`
- Git operations: Check for `.git/index.lock`
- If conflict detected: Show warning, provide retry suggestion

**Duplicate Detection Preparation:**
1. Load existing operations from `_closeout_state.completed_operations`
2. Check for partial closeout state (interrupted previous attempt)
3. If interrupted closeout detected: Warn and offer recovery options

### 1. Lug Reconciliation

**Purpose:** Consolidate autosave checkpoints into permanent record.

**Idempotency Check:**
1. Check if session-summary for current session ID already exists in WAI-Lugs.jsonl
2. If exists: ⚠️ **DUPLICATE DETECTED:** Session summary `{session_id}` already exists
   - Display warning: "Skipping session summary creation, continuing with signal extraction..."
   - Record in `_closeout_state.completed_operations`: "session_summary_skipped"
   - Continue to Step 2

**Actions:**
1. Read `WAI-Spoke/WAI-Lugs.jsonl`
2. Find entries where `ty="autosave"` AND `reconciled=false` (or `reconciled` not set)
3. Consolidate into ONE permanent `session-summary` lug capturing:
   - Task context (what was the session about?)
   - Actions taken
   - Files touched
   - Key decisions made
   - **Incomplete work** (critical for session continuity)
   - Final state
4. Mark all autosave lugs: set `reconciled: true`, `s: "c"`
5. Append session-summary lug to `WAI-Spoke/WAI-Lugs.jsonl`
6. Record session ID in `_closeout_state.duplicate_detection_keys.session_summaries[]`
7. Record completion in `_closeout_state.completed_operations`: "lug_reconciliation_complete"

**Session-summary lug format:**
```json
{
  "i": "ss-{session_id}",
  "ty": "session-summary",
  "t": "Session N summary",
  "s": "c",
  "ca": "ISO-8601",
  "gb": "agent-name",
  "session_number": N,
  "accomplished": ["list of accomplishments"],
  "files_touched": ["list of files"],
  "decisions": ["key decisions made"],
  "incomplete_work": {
    "tasks": ["what remains"],
    "blockers": ["what's blocking"],
    "next_steps": ["how to continue"]
  },
  "autosaves_reconciled": ["list of autosave lug ids"]
}
```

### 2. Signal Extraction

# Signal storage: see wai-lug-advisor.md — Canonical Storage

**Purpose:** Capture high-impact decisions for cross-session learning.

**Idempotency Check:**
1. For each potential signal, generate deduplication key: `{created_at}+{title}+{impact}`
2. Check `_closeout_state.duplicate_detection_keys.signal_teachings` for existing keys
3. If duplicate exists: ⚠️ **DUPLICATE DETECTED:** Signal `{title}` already extracted
   - Display warning: "Skipping duplicate signal extraction, continuing..."
   - Continue with remaining signals

**Actions:**
1. Review session for decisions or learnings with **impact >= 8**
2. For each qualifying signal, create a high-impact lug entry in `WAI-Spoke/WAI-Lugs.jsonl`:

```json
{
  "id": "signal-YYYYMMDD-HHMM-brief-description",
  "type": "signal",
  "title": "Brief descriptive title of signal",
  "description": "what was decided/learned",
  "impact": 8-10,
  "created_by": "agent-name",
  "created_at": "ISO-8601",
  "session_id": "session-YYYYMMDD-HHMMSS",
  "rationale": "why it matters"
}
```

**Impact scale:**
- 10: Fundamental direction change
- 9: Major architectural decision
- 8: Significant protocol or pattern established
- < 8: Normal decisions, no signal needed

3. Flag signals that warrant hub consideration:
   - Cross-project patterns
   - Architectural insights
   - Reusable solutions

**Note:** This step absorbs the `wai-signal-advisor.md` behavior — closeout is where signals get permanently captured.

**Completion:**
3. Record signal deduplication keys in `_closeout_state.duplicate_detection_keys.signal_teachings[]`
4. Record completion in `_closeout_state.completed_operations`: "signal_extraction_complete"

### 3. Incomplete Work Capture

**Critical for session continuity.**

Document any unfinished work with enough detail to resume:

```markdown
## Incomplete Work

### [Task Name]
- **Status:** In Progress / Blocked / Pending Decision
- **What's Done:** [completed steps]
- **What Remains:** [specific next steps]
- **Blockers:** [if any]
- **Files Involved:** [paths]
- **To Continue:** [exact instructions for next session]
```

Store in session-summary lug `incomplete_work` field AND in `_session_state.next_session_recommendation`.

**Enhanced with Track:** If a session track exists (`_session_state.track_path`), also read the track's open threads and phase state. The track captures unresolved questions that may not surface in the lug reconciliation. Include any `open` items from the last 3 track points in the incomplete work section.

### 4. Version Increment

**Bump project state version:**

1. Read `WAI-Spoke/WAI-State.json`
2. Parse `wheel.version` (semver format, e.g., "2.0.7")
3. Increment patch: `2.0.7` → `2.0.8`
4. Write back to `WAI-State.json`

This versions the *session state*, not a release.

### 5. State Update

**Idempotency Check:**
1. Check current `_session_state.last_modified_at` timestamp
2. If modified within last 30 seconds: ⚠️ **DUPLICATE DETECTED:** Recent state update detected
   - Display warning: "Skipping state update, appears already completed..."
   - Continue to Step 6

**Actions:**
1. Read current WAI-State.json for compare-and-swap validation
2. Update session metadata in `WAI-State.json`:

- `_session_state.session_count` += 1
- `_session_state.last_closeout` = current UTC timestamp (ISO-8601)
- `_session_state.last_modified_by` = current AI model name
- `_session_state.last_modified_at` = current UTC timestamp
- `_session_state.next_session_recommendation` = summary of what to do next
- `_session_state.track_path` = path to current session's track file (e.g., `WAI-Spoke/sessions/session-20260312-2100/track.jsonl`)
- `_migration_state.last_migration_check` = current UTC timestamp (ISO-8601)
- `_closeout_state.current_session_id` = current session ID
- `_closeout_state.last_closeout_check` = current UTC timestamp

**Update migration receipts (if any capability adoptions occurred this session):**

- If implementation lugs completed: add migration receipt to `_migration_state.migration_receipts[]`
- If capability adoptions occurred: update `_migration_state.adoption_markers` with receipt IDs and rollback checkpoints
- If framework version changed: record in `_migration_state.framework_migrations_applied[]`

**Completion:**
3. Write updated WAI-State.json
4. Record completion in `_closeout_state.completed_operations`: "state_update_complete"

### 5b. Adoption Marker Sync

Check that WAI-State.json adoption markers reflect the actual implementation state of capability lugs.

For each lug in `WAI-Lugs.jsonl` where `type = "implementation"` and `status = "implemented"`:
1. Derive the expected adoption marker key (strip `-v1`/`-v2` suffix from migration_id or lug id to get the marker name)
2. Check `_migration_state.adoption_markers[<key>].adopted` in `WAI-State.json`
3. If `adopted = false`: update to `true`, set `adopted_at` = current UTC, set `adopted_by` = current agent
4. Log: "Synced adoption marker: <key>"

If no mismatches found: output "Adoption markers current — no sync needed"

**Why:** Prevents adoption markers from staying false after implementation completes, which misleads future agents into believing migrations are pending when they are done.

### 6. Finalize Session Track

**Close the session track (if active):**

- Write a final point to `track.jsonl` recording the closeout activity (phase: `review`)
- The track file is the permanent session record — do NOT delete or truncate it
- The session track file is committed to git with other WAI-Spoke files

**Legacy cleanup:**

- Truncate `WAI-Spoke/WAI-Session-Log.jsonl` (if exists) — replaced by session tracks
- Insights already extracted to lugs/signals

### 7. Documentation Updates

**Document what's known and can be captured:**

- Update `CHANGELOG.md` with session accomplishments
- Update any documentation files affected by session work
- Generate clear, descriptive commit message

### 8. Lug Dogfooding (Before Commit)

**Validate all lugs created or modified this session before they ship.**

Any lug intended for another agent (including future-you in a new session) must pass validation. This step catches gaps that are invisible in the current conversation but fatal for a cold reader.

1. **Identify lugs to validate** — all lugs created or modified this session (excluding session-summary and autosave types)
2. **State what you'll test and how deep** — present to user:
   ```
   Dogfood check — N lugs created/modified this session:
   - {lug i}: {lug title} — [schema + PEV + self-containment]
   ...
   Proceed? (yes / adjust scope)
   ```
3. **Wait for user approval** before running validation
4. **Run validation** on each lug:
   - Are PEV fields present and actionable? (required for task, bug, feature, review, epic)
   - Does `perceive` point to real, findable files?
   - Does `execute` describe concrete steps (not vague intentions)?
   - Does `verify` define a concrete "done" state?
   - Is the lug self-contained? (no "see above" or conversation-dependent references)
   - Could a naive agent understand this without your current context?
5. **Fix gaps found** — update lugs in WAI-Lugs.jsonl before proceeding
6. **Report results** — "N lugs validated, M gaps filled" or "All lugs clean"

**Skip conditions:** If no actionable lugs were created/modified this session, skip this step entirely.

### 9. Outbox Delivery

**Deliver queued lugs to hub before committing.**

1. Check `WAI-Spoke/lugs/outbox/` for `.jsonl` files
2. If outbox is empty → skip, note "Outbox empty" in summary
3. If items found and `hub_path` is connected:
   - For each file where `destination_wheel_id` matches hub or target: copy to `{hub_path}/WAI-Spoke/lugs/inbox/`
   - Report: "N lugs delivered to hub"
4. If hub unreachable: note in `_session_state.next_session_recommendation`, continue — do not block commit

### 9b. Teaching Generation + Hub Publish (Conditional)

**Automatically generate current teaching files during closeout, clean up superseded versions, and publish them to the hub using copy-based distribution. No separate manual teaching step is required for canonical framework changes.**

**Purpose:**
- Convert migration-relevant framework changes into teaching files automatically
- Keep exactly one current teaching per teaching family in the active publish location
- Archive superseded versions deterministically
- Publish current teachings to the hub without symlinks

**Framework objects covered:**
- High-impact signal lugs (`impact >= 8`)
- Skills and advisors in `templates/commands/`
- Spoke template changes in `templates/spoke/`
- State schema or canonical behavior changes affecting spoke migration
- Lug/schema or protocol changes that alter spoke behavior

**Conditions:**
- `teachings/` exists or can be created
- At least one migration-relevant framework object changed this session, OR at least one new high-impact lug exists with `created_at > old_last_closeout`

**Hub publishing conditions:**
- `wheel.hub_path` is set and the directory exists
- `{hub_path}/teachings_repo/` exists or can be created

**If no teaching-worthy changes are found:** Skip silently. Note "No new teachings to generate" in summary.

**Serialized Operation (Graceful Failure):**
1. Check for `.teaching-distribution.lock` file
2. If lock exists:
   - Display warning: "Another agent is distributing teachings. Retry in 30 seconds."
   - Record in `_session_state.next_session_recommendation`: "Retry teaching generation and hub publish"
   - Continue to next step (do not block commit)

**If no lock conflict:**
1. Create `.teaching-distribution.lock`
2. Detect migration-relevant changes from this session. Minimum detection sources:
   - High-impact lugs in `WAI-Lugs.jsonl` where `created_at > old_last_closeout` AND `impact >= 8`
   - Modified files under `templates/commands/`
   - Modified files under `templates/spoke/`
   - State/schema or protocol changes that alter spoke behavior
3. Normalize candidate changes before version decisions:
   - Ignore whitespace-only diffs, timestamp-only churn, and non-semantic formatting changes
   - Group changes into stable teaching families using `family_key = {object_type}-{object_name}` (examples: `skill-wai-closeout`, `advisor-wai-complexity`, `template-spoke-CLAUDE`, `state-schema`, `protocol-track-chain`)
4. For each teaching family:
   - Determine whether a new version is required based on migration-relevant content changes only
   - Bump version according to policy:
     - `major`: breaking or incompatible migration behavior
     - `minor`: backward-compatible capability addition
     - `patch`: clarification, fix, or non-breaking correction
   - Enforce the single-current rule: only one current teaching per family may remain in active publish state
5. Generate teaching files into `teachings/` using the filename pattern `{family_key}-v{version}.md.teaching`
6. Each generated teaching must include:
   - What changed
   - Why it matters to spokes
   - Exact migration/apply instructions
   - `safe_to_auto_adopt` with reasoning
   - Source files and originating lug(s), when available
   - Superseded family/version information, when applicable
7. Signal teachings remain first-class teachings. For each qualifying high-impact lug, embed the actual lug JSON verbatim inside the generated teaching. Receiving spokes must remain idempotent: if a lug with the same `id` or same semantic identity already exists locally, skip append.
8. Cleanup active teaching state before publish:
   - Scan for existing teachings in the same family
   - Keep only the newest current version in active publish state
   - Move superseded versions to `teachings/archive/{family_key}/`
   - Delete only duplicate-byte-identical files or failed partial files
   - If generation fails for a family after partial write, remove the partial artifact and preserve the prior current version
9. Idempotency requirements:
   - Re-running closeout without relevant source changes must not create a new version
   - Re-running closeout without relevant source changes must not duplicate archive entries
   - Identical current teaching content must not be rewritten unnecessarily

**Hub Publish (copy-based, no symlinks):**
1. If hub conditions are met, publish current teachings to `{hub_path}/teachings_repo/{spoke_id}/`
2. Use the canonical hub layout:
   - `current/` for current teachings only
   - `archive/{family_key}/` for superseded versions
   - `index.json` at the hub root and per-spoke directory
3. For each teaching family during publish:
   - If the current hub file has the same content hash, skip copy
   - If the hub current version differs, move the old current file to `archive/{family_key}/` and copy the new current file into `current/`
4. Rewrite `{hub_path}/teachings_repo/{spoke_id}/index.json` atomically
5. Rewrite `{hub_path}/teachings_repo/index.json` atomically
6. Never rely on or create symlinks inside `teachings_repo/`
7. If hub publish fails or hub is unavailable:
   - Keep local current teachings intact
   - Record retry guidance in `_session_state.next_session_recommendation`
   - Do not block commit

**Completion:**
1. Record generated teaching filenames in `_closeout_state.duplicate_detection_keys.signal_teachings[]` or a broader teaching receipt structure if available
2. Remove `.teaching-distribution.lock`
3. Record completion in `_closeout_state.completed_operations`: `teaching_generation_complete`
4. Report counts in summary:
   - `N` teachings generated
   - `M` superseded teachings archived
   - `P` teachings published to hub

### 9c. Hub Signal Bulletin

**Publish high-impact lugs to the hub bulletin board for cross-spoke visibility.**

Read `hub_path` from `WAI-State.json` at `wheel.hub_path`.

**If hub_path is null or hub not accessible:** Skip silently. Log: "Hub bulletin skipped — hub not connected"

**If hub is accessible:**

For each lug in `WAI-Lugs.jsonl` where `impact > 7` and `status != "archived"`:
1. Check if `{hub_path}/WAI-Hub/Signals/incoming/{lug-id}.json` already exists
2. If not: write the full lug JSON as `{hub_path}/WAI-Hub/Signals/incoming/{lug-id}.json`
3. Log: "Published to hub bulletin: {lug-id} (impact={impact})"

If no qualifying lugs found: log "Hub bulletin: no lugs with impact > 7 to publish"

### 9d. Spoke Health Report (Auto)

**Send a self-health snapshot to the hub registry at every closeout.**

Read `hub_path` from `WAI-State.json` at `wheel.hub_path`.

**If hub_path is null or hub not accessible:** Skip silently.

**If hub is accessible:**

1. Load `templates/health-check.jsonl` from the framework path. If not found, skip and log.
2. Run each check from the questionnaire (shell command, capture stdout).
3. Score: count PASS vs total checks. Compute percent.
4. Build the health lug:
```json
{
  "id": "spoke-health-{spoke_id}-{session_id}",
  "type": "spoke-health",
  "spoke_id": "{wheel.name}",
  "session_id": "{session_id}",
  "timestamp": "{ISO-8601}",
  "score": "{passed}/{total}",
  "percent": 95,
  "failures": [
    {"check_id": "hc-q-...", "title": "...", "fail_means": "..."}
  ],
  "status": "healthy | degraded | critical"
}
```
   Status thresholds: healthy = 100%, degraded = 80-99%, critical = <80%

5. Write the lug to `{hub_path}/WAI-Spoke/seed/ingest/spoke-health-{spoke_id}-{session_id}.json`
6. Log: "Spoke health: {score} ({status}) — sent to hub inbox"

**Purpose:** Hub aggregates these at wakeup to build a fleet health snapshot. Spoke does not need to wait for hub response.

### 10. Summary Generation

**Create and present session summary:**

- What was accomplished
- What decisions were made
- What's incomplete (with continuation guidance)
- New version number
- Signals extracted
- Files modified
- **Track stats** (if session track exists): total turns, phase distribution, open threads carried forward

Present to user before commit.

### 11. Git Commit + Push

**Persist to repository and push — always.**

**Serialized Operation (Graceful Failure):**
1. Check for `.git/index.lock` file
2. If lock exists: ⚠️ **GIT CONFLICT:** Another git operation in progress
   - Display warning: "Git operation in progress. Wait 10 seconds and retry, or resolve manually."
   - Record in `_session_state.next_session_recommendation`: "Complete git commit for session {session_id}"
   - Exit gracefully (do not attempt commit)

**Git Operations (Queue-based Retry):**
```bash
git add WAI-Spoke/
git add [other session files]
git status  # Review what's staged
```

**Idempotency Check:**
1. Check git log for commit with current session ID
2. If commit exists: ⚠️ **DUPLICATE DETECTED:** Session `{session_id}` already committed
   - Display warning: "Session already committed to git, skipping..."
   - Continue to push step

**Commit with descriptive message:**
```bash
git commit -m "WAI Session [N]: [accomplishments] | Incomplete: [if any]"
```

**Push immediately after commit (no confirmation needed):**
```bash
git push origin main
```

### 12. Idempotency Summary and Cleanup

**Generate Idempotency Report:**
1. Review all completed operations from `_closeout_state.completed_operations`
2. Display final summary of what was completed vs skipped:

```
✅ Closeout Summary for {session_id}:
├─ Lug Reconciliation: ✅ Completed / ⚠️ Skipped (already exists)
├─ Signal Extraction: ✅ Completed / ⚠️ Skipped (duplicates detected)  
├─ State Update: ✅ Completed / ⚠️ Skipped (recent modification)
├─ Signal Teaching: ✅ Completed / ⚠️ Skipped (concurrent operation)
└─ Git Operations: ✅ Committed / ⚠️ Skipped (already committed)

⚠️ Warnings encountered: N
📋 All operations completed successfully with replay safety verified
```

**Cleanup:**
1. Clear `_closeout_state.current_session_id`
2. Record final `_closeout_state.last_closeout_check` timestamp

> **NOT IMPLEMENTED — DEFERRED:** File lock cleanup (.state.lock, .lugs.lock, .teaching-distribution.lock) is deferred. Ownership-based concurrency (Step 0) is used instead.

---

## Success Criteria

**Core Closeout Operations:**
- [ ] Autosave lugs reconciled into permanent session-summary
- [ ] High-impact signals extracted (impact >= 8)
- [ ] **Incomplete work documented with continuation guidance**
- [ ] Version incremented in WAI-State.json
- [ ] Session state updated (session_count, timestamps, track_path)
- [ ] Session track finalized (final point written, track NOT deleted)
- [ ] Legacy session log cleared (if exists)
- [ ] Documentation updated where applicable
- [ ] Lugs dogfooded (PEV fields validated, gaps filled)
- [ ] Outbox delivered (or deferred with note if hub unreachable)
- [ ] Signal teachings written to teachings/ (or skipped — hub disconnected or no new signals)
- [ ] Changes committed with descriptive message (sessions/track file included)
- [ ] Changes pushed to origin/main

**Idempotency and Concurrency:**
- [ ] Session ID generated deterministically using `ss-{session_id}` format
- [ ] Duplicate operations detected via `_closeout_state.duplicate_detection_keys` and skipped gracefully (warn-continue)
- [ ] Concurrent operations handled gracefully (teaching distribution, git operations)
- [ ] Idempotency summary displayed with operation status
- [ ] Replay safety verified - running closeout twice produces consistent results

> **NOT IMPLEMENTED — DEFERRED:** File locking (.closeout.lock, .state.lock, .lugs.lock) and migration checkpoints (.migration-checkpoint.json) are not part of this implementation. Concurrency is handled by the ownership-based model in Step 0.

---

## Language Rules

**Never say:**
- "Probably saved"
- "Should be committed"
- "I think it persisted"

**Always say:**
- "Verified with git status"
- "Confirmed commit with git log"
- "Incomplete work documented in [location]"

---

## Related Commands

- `/wai-shipit` - Quality gates + closeout (for releases)
- `/wai-time` - Check context before closeout

---

*Closeout = Save game. Capture enough detail to continue the adventure.*

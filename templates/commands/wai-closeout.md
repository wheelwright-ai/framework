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

**Session ID Generation:**
1. Generate deterministic session ID: `session-$(date -u +%Y%m%d-%H%M%S)`
2. Check `_closeout_state.duplicate_detection_keys.session_summaries` for existing session ID
3. If duplicate session ID exists: append `-2`, `-3`, etc. until unique

**Concurrency Protection:**
1. **Critical Operations (File Locking):**
   - WAI-State.json updates: Create `.state.lock` (30s timeout)
   - WAI-Lugs.jsonl appends: Create `.lugs.lock` (30s timeout)
   - If lock acquisition fails: Display clear message and exit gracefully

2. **Serialized Operations (Graceful Failure):**
   - Teaching distribution: Check for `.teaching-distribution.lock`
   - Git operations: Check for `.git/index.lock`
   - If conflict detected: Show warning, provide retry suggestion

**Duplicate Detection Preparation:**
1. Load existing operations from `_closeout_state.completed_operations`
2. Check for partial closeout state (interrupted previous attempt)
3. If interrupted closeout detected: Warn and offer recovery options

**Lock Cleanup:**
- Set trap to remove locks on script exit (normal or error)
- Locks older than 5 minutes automatically ignored (stale protection)

### 1. Lug Reconciliation

**Purpose:** Consolidate autosave checkpoints into permanent record.

**Idempotency Check:**
1. Check if session-summary for current session ID already exists in WAI-Lugs.jsonl
2. If exists: ⚠️ **DUPLICATE DETECTED:** Session summary `{session_id}` already exists
   - Display warning: "Skipping session summary creation, continuing with signal extraction..."
   - Record in `_closeout_state.completed_operations`: "session_summary_skipped"
   - Continue to Step 2

**Concurrent-Safe Actions (with .lugs.lock):**
1. Acquire `.lugs.lock` file (30s timeout)
2. Read `WAI-Spoke/WAI-Lugs.jsonl`
3. Find entries where `ty="autosave"` AND `reconciled=false` (or `reconciled` not set)
4. Consolidate into ONE permanent `session-summary` lug capturing:
   - Task context (what was the session about?)
   - Actions taken
   - Files touched
   - Key decisions made
   - **Incomplete work** (critical for session continuity)
   - Final state
5. Mark all autosave lugs: set `reconciled: true`, `s: "c"`
6. Append session-summary lug to `WAI-Spoke/WAI-Lugs.jsonl`
7. Record session ID in `_closeout_state.duplicate_detection_keys.session_summaries[]`
8. Release `.lugs.lock`
9. Record completion in `_closeout_state.completed_operations`: "lug_reconciliation_complete"

**Session-summary lug format:**
```json
{
  "i": "session-YYYYMMDD-HHMMSS",
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

**Purpose:** Capture high-impact decisions for cross-session learning.

**Idempotency Check:**
1. For each potential signal, generate deduplication key: `{created_at}+{title}+{impact}`
2. Check `_closeout_state.duplicate_detection_keys.signal_teachings` for existing keys
3. If duplicate exists: ⚠️ **DUPLICATE DETECTED:** Signal `{title}` already extracted
   - Display warning: "Skipping duplicate signal extraction, continuing..."
   - Continue with remaining signals

**Concurrent-Safe Actions (with .lugs.lock):**
1. Acquire `.lugs.lock` file (30s timeout)
2. Review session for decisions or learnings with **impact >= 8**
3. For each qualifying signal, create a high-impact lug entry in `WAI-Spoke/WAI-Lugs.jsonl`:

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
4. Record signal deduplication keys in `_closeout_state.duplicate_detection_keys.signal_teachings[]`
5. Release `.lugs.lock`
6. Record completion in `_closeout_state.completed_operations`: "signal_extraction_complete"

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

**Concurrent-Safe Actions (with .state.lock):**
1. Acquire `.state.lock` file (30s timeout)
2. Read current WAI-State.json for compare-and-swap validation
3. Update session metadata in `WAI-State.json`:

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
4. Write updated WAI-State.json atomically
5. Release `.state.lock`
6. Record completion in `_closeout_state.completed_operations`: "state_update_complete"

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

### 9b. Signal Teach (Conditional)

**Automatically distribute new signals to the hub — no separate /wai (Step 9b: auto-teach on closeout) needed.**

**Conditions (both must be true):**
- `wheel.hub_path` is set and the directory exists
- `WAI-Lugs.jsonl` contains high-impact lugs (impact >= 8) with `created_at > old_last_closeout` (captured before Step 5)

**If either condition is false:** Skip silently. Note "No new signals to teach" in summary.

**Serialized Operation (Graceful Failure):**
1. Check for `.teaching-distribution.lock` file
2. If lock exists: ⚠️ **CONCURRENT OPERATION:** Teaching distribution in progress
   - Display warning: "Another agent is distributing teachings. Retry in 30 seconds or use --force-teaching flag to override."
   - Record in `_session_state.next_session_recommendation`: "Retry signal teaching distribution"
   - Continue to next step (do not block commit)

**If both conditions are true and no lock conflict:**
1. Create `.teaching-distribution.lock` file
2. Collect all high-impact lugs from `WAI-Lugs.jsonl` where `created_at > old_last_closeout` AND `impact >= 8` (canonical signal criteria)
3. For each qualifying lug, derive a filename: sanitize `created_at` to `YYYYMMDD-HHMM`, then append the sender spoke ID (from `wheel.name`, lowercased, spaces → hyphens) → `teachings/signal-YYYYMMDD-HHMM-from-{spoke_id}.md.teaching`. Example: `signal-20260316-0045-from-wheelwright.md.teaching`. If that filename already exists, append `-2`, `-3`, etc. until unique.
3. Write the teaching file — substitute the actual signal JSON verbatim (one file per signal, not a placeholder):

```markdown
# Teaching: Signal — {signal content summary}

**Type:** signal
**safe_to_auto_adopt:** true

---

## What This Teaching Does

Appends a high-impact lug (signal) to `WAI-Lugs.jsonl` on this spoke. Signals are canonically high-impact lugs (impact >= 8) that get distributed via the hub bulletin.

## Embedded Signal

```json
{actual high-impact lug JSON object here}
```

## Post-Completion

Move this file to `WAI-Spoke/seed/ingest/processed/`.
```

4. **Idempotency:** Receiving spokes may see the same signal teaching more than once (re-teach, restore). Before appending, check if a lug with the same `id` or (`created_at` + `title`) already exists in `WAI-Lugs.jsonl`. If it does, skip — do not duplicate.
5. Report: "N signal teaching(s) written to teachings/"

**Note:** The hub symlink (`hub/framework → ../framework/teachings/`) means these files are immediately visible to all connected spokes on their next wakeup. No further distribution step required.

**Completion:**
4. Record teaching filenames in `_closeout_state.duplicate_detection_keys.signal_teachings[]`
5. Remove `.teaching-distribution.lock`
6. Record completion in `_closeout_state.completed_operations`: "signal_teaching_complete"

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

**Cleanup Lock Files:**
1. Remove any remaining lock files (.state.lock, .lugs.lock, .teaching-distribution.lock)
2. Clear `_closeout_state.current_session_id`
3. Record final `_closeout_state.last_closeout_check` timestamp

**Trap Cleanup (Automatic):**
- All lock files are automatically removed on script exit (normal or error)
- Stale lock files (>5 minutes) are automatically ignored

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
- [ ] Session ID generated deterministically and uniquely
- [ ] Duplicate operations detected and handled gracefully (warn-continue)
- [ ] File locks acquired successfully for critical operations (WAI-State.json, WAI-Lugs.jsonl)
- [ ] Concurrent operations handled gracefully (teaching distribution, git operations)
- [ ] All lock files cleaned up properly
- [ ] Idempotency summary displayed with operation status
- [ ] Replay safety verified - running closeout twice produces consistent results

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

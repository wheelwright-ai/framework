# WAI Closeout

Save session state so the next agent can pick up where we left off.

---

## Execution Context

- **Nodes:** spoke, hub
- **Paths Required:** spoke_path (current directory with WAI-Spoke/)

---

## Closeout Procedure

**Before beginning:** Ask **Is this a production release? (y/n)**
- **Yes:** Run full closeout + quality gates + git tag `v{version}`
- **No:** Run standard closeout, skip gates and tagging

Read `_session_state.last_closeout` from `WAI-State.json` and store as `old_last_closeout`. Step 5 will overwrite it; Step 9b needs the old value.

### 0. Quality Gates (Production Releases Only)

Skip if not a production release.

**0a. File Hygiene:** Scan for AI sprawl (`temp_*`, `*.bak`, `*.tmp`, `debug_*`, `scratch_*`, `old_*`, `*.orig`). Delete temp files, ask about unknowns. Report findings.

**0b. Breaking Changes:** Check for API signature changes, removed functions, config format changes. Document in CHANGELOG.md. Confirm user acknowledges.

**0c. Tests:** Auto-detect and run (`pytest`, `npm test`, `make test`). Non-zero exit = abort.

**0d. Linting:** Auto-detect and run (`ruff`, `eslint`). Non-zero exit = abort.

**0e. Benchmarks:** Run if available. On regression: offer abort / acknowledge / update baseline.

Report gate results. Proceed only after user confirms all gates pass or are acknowledged.

### 1. Lug Reconciliation

Scan `WAI-Spoke/lugs/bytype/other/open/` for autosave lugs (`ty="autosave"`, `reconciled=false`). Consolidate into ONE session-summary lug covering: what the session was about, actions taken, files touched, decisions, incomplete work, final state. Mark autosaves `reconciled: true`, `s: "c"`. Write summary to `lugs/bytype/session-summary/{id}.json`.

Session-summary lug fields: `id`, `type: "session-summary"`, `title`, `status: "completed"`, `created_at`, `created_by`, `session_number`, `accomplished[]`, `files_touched[]`, `decisions[]`, `incomplete_work{tasks[], blockers[], next_steps[]}`, `autosaves_reconciled[]`.

### 2. Signal Extraction

Review session for decisions/learnings with **impact >= 8**. Write each as a signal lug to `lugs/bytype/signal/undelivered/{id}.json`. Signal schema: see `wai-lug-schema.md`. Impact scale: 10=direction change, 9=architectural, 8=significant pattern, <8=skip.

### 3. Incomplete Work Capture

Document unfinished work with enough detail to resume: status, what's done, what remains, blockers, files, continuation instructions. Store in session-summary `incomplete_work` AND `_session_state.next_session_recommendation`.

If a session track exists, also read `open` items from the last 3 track points — tracks capture unresolved questions that lug reconciliation may miss.

### 4. Version Increment

Bump `wheel.version` patch: `2.0.7` → `2.0.8`. This versions session state, not a release.

### 5. State Update

Update `WAI-State.json`:
- `_session_state.session_count` += 1
- `_session_state.last_closeout` = now (UTC ISO-8601)
- `_session_state.last_modified_by` = current model
- `_session_state.last_modified_at` = now
- `_session_state.next_session_recommendation` = what to do next
- `_session_state.track_path` = current session track path

If capability adoptions or migrations occurred: update extended state (`WAI-State-extended.json`) migration receipts and adoption markers accordingly.

### 5b. Adoption Marker Sync

For each implementation lug with `status = "implemented"`: check `_migration_state.adoption_markers` in extended state. If `adopted = false`, update to `true` with timestamp. Log result.

### 5c. Lug Status Sync and Routing-Aware Archival

1. Scan `bytype/*/open/` and `bytype/*/in_progress/` for lugs whose status changed this session
2. For each completed lug, check `routed_to` field:
   - **LOCAL:** Move to `bytype/{type}/completed/` (stays in this spoke)
   - **FRAMEWORK:** Move to `bytype/{type}/completed/` AND copy to hub teachings (Step 9b)
   - **SIGNAL:** Move to `bytype/signal/delivered/` AND copy to hub signal bulletin (Step 9c)
3. Move delivered signals from `undelivered/` to `delivered/` (archive metadata only; actual delivery in Step 9c)
4. Regenerate `WAI-LugIndex.jsonl` — one line per lug: `{id, type, status, title, folder, created_at, routed_to}`
5. Report: "Moved N lugs. Routing: M LOCAL, K FRAMEWORK, J SIGNAL. Index: T entries."

### 6. Finalize Session Track

Write a final track point (phase: `review`). Do NOT delete the track file — it's the permanent session record.

### 7. Documentation Updates

Update `CHANGELOG.md` if applicable. Generate descriptive commit message.

### 7b. Docs Sync (When Protocol Changes)

**Trigger:** After any session that modifies skills, protocol files, architecture, or lug schema.

1. **Update README.md:**
   - Check `wheel.version` in WAI-State.json — update version string if changed
   - If skills were added/removed: update skill list in README
   - If architecture changed: update architecture diagram

2. **Regenerate docs/llm-full.txt:**
   - Concatenate source files: WAI-State.json, wai.md, wai-closeout.md, wai-lug-schema.md, key utilities, CHANGELOG top entries
   - Format: header + `=== FILE: {path} ===` delimiters for each file
   - Target size: under 200KB
   - Purpose: Single-file LLM context loader for external agents

3. **If no protocol changes this session:** Note "Skip 7b: no protocol changes" in session summary.

This step is skippable but must be explicitly noted if skipped.

### 8. Lug Dogfooding

Validate lugs created/modified this session (excluding session-summary and autosave). Check: PEV fields present? `perceive` points to real files? `execute` has concrete steps? `verify` defines done state? Self-contained (no "see above")? Present validation plan to user, wait for approval, fix gaps found. Skip if no actionable lugs were created.

### 9. Outgoing Delivery

Check `WAI-Spoke/lugs/outgoing/` for queued deliveries. If found and hub connected: copy to `{hub_path}/WAI-Spoke/lugs/incoming/`. If hub unreachable: note in next_session_recommendation, don't block.

### 9b. Teaching Generation + Hub Publish

**Conditions:** Teaching-worthy changes exist this session (skill files modified, high-impact signals created since `old_last_closeout`, template/schema changes).

**If no changes:** Skip. Note "No new teachings" in summary.

**If changes exist:**
1. Group changes into teaching families: `{object_type}-{object_name}` (e.g., `skill-wai-closeout`)
2. Determine version bump: major (breaking), minor (new capability), patch (fix/clarification)
3. Generate teaching files to `teachings/{family_key}-v{version}.md.teaching`
4. Each teaching MUST include (hard gate — do not publish without these):
   - What changed and why it matters
   - Migration instructions
   - `safe_to_auto_adopt` flag
   - `## Prerequisites` block (runnable verify commands, or "None")
   - `## Batch Sequence` block (apply order, depends-on, required-before, parallel-safe)
   Missing either block = teaching is incomplete. Fix before publishing.
5. Enforce single-current rule: archive superseded versions to `teachings/archive/{family_key}/`
6. Signal teachings embed the actual lug JSON verbatim
7. If hub connected: publish to `{hub_path}/teachings_repo/framework/current/`, archive old versions, rewrite index.json
8. If hub unavailable: keep local, note retry in next_session_recommendation

Teaching format details: see `wai-closeout-reference.md` in this skill's folder.

### 9c. Hub Signal Bulletin (Routing-Aware)

For each lug with `routed_to = "SIGNAL"`: if not already at `{hub_path}/WAI-Hub/Signals/incoming/{id}.json`, write it there. Skip if hub not connected.

**Also include** any signal lug with `impact > 7` and `routed_to = "SIGNAL"` that wasn't already caught by routing.

Report: "Delivered N lugs to hub bulletin."

### 10. Autosave Cleanup (Interruption Recovery Hygiene)

Remove autosave checkpoints older than 3 sessions:

```bash
# Get current session count from WAI-State.json
CURRENT_SESSION=$(jq -r '._session_state.session_count' WAI-State.json)
CUTOFF=$((CURRENT_SESSION - 3))

# Remove old autosave files
find WAI-Spoke/.autosave -name "*.json" -exec basename {} \; | while read file; do
    # Extract session metadata from autosave if available
    # If autosave is from session < CUTOFF, delete it
    rm -f "WAI-Spoke/.autosave/$file"
done

echo "✅ Cleaned autosave checkpoints > 3 sessions old"
```

**Why:** Autosaves are crash recovery helpers, not permanent archives. After 3+ sessions, if we haven't resumed from them, they're stale and should be removed. Keeps .autosave/ folder clean.

### 11. Summary Generation

Present to user: accomplishments, decisions, incomplete work with continuation guidance, new version, signals extracted, files modified, track stats.

### 12. Git Commit + Push

```bash
git add WAI-Spoke/ [other session files]
git commit -m "WAI Session [N]: [accomplishments] | [version]"
git push origin main
```

Push is mandatory. Do not ask for confirmation.

### 13. Release Tag (Production Releases Only)

Skip if not a production release (confirmed in Step 0).

```bash
VERSION=$(jq -r '.wheel.version' WAI-Spoke/WAI-State.json)
git tag "v$VERSION"
git push origin "v$VERSION"
```

If tag already exists: stop and report conflict. Do not force-overwrite.

### 14. Verification

```bash
git status          # Must be clean
git log --oneline -1  # Verify commit
git tag -l | tail -1  # Verify tag (if production release)
```

---

## Success Criteria

- [ ] Quality gates pass (if production release)
- [ ] Autosave lugs reconciled into session-summary
- [ ] Signals extracted (impact >= 8)
- [ ] Incomplete work documented with continuation guidance
- [ ] Version incremented, state updated
- [ ] Lug status synced, index regenerated
- [ ] Session track finalized
- [ ] Lugs dogfooded (if applicable)
- [ ] Teachings generated and published (if applicable)
- [ ] Committed and pushed to origin/main
- [ ] Release tag applied and pushed (if production release)

---

*Closeout = Save game. Next agent continues the adventure.*

---

## Visual Completion Marker

When closeout succeeds, display this to signal completion distinctly:

```
┌─ CLOSEOUT Session-{N} [{track_name}] {timestamp}
│
│  Track stats: {turns} turns, {phase_distribution}
│  Context: {context_percent}% ({context_used}K/{context_limit}K tokens)
│  Version: v{old_version} → v{new_version}
│  Session count: {old_count} → {new_count}
│  Commits: {N} files pushed to origin/main
│
└─ Session saved. Next wakeup loads exactly where we left off.
```

**Values to fill:**
- `{N}` = `_session_state.session_count` from WAI-State.json (before increment)
- `{track_name}` = session directory name (e.g., `session-20260325-1326`)
- `{timestamp}` = current UTC time (ISO-8601)
- `{turns}` = total track points written (count lines in track.jsonl)
- `{phase_distribution}` = breakdown of phases in track (e.g., "execution (70%) + review (30%)")
- `{context_percent}`, `{context_used}`, `{context_limit}` = final context measurement from closeout (run `/context` before Step 11 if available)
- `{old_version}` → `{new_version}` = version before and after closeout
- `{old_count}` → `{new_count}` = session_count before and after increment
- `{N}` = number of files committed and pushed

**Distinction:** **WAKEUP** = shows project + active work. **CLOSEOUT** = shows track stats + context usage + version changes. Unmistakable when tab-switching.

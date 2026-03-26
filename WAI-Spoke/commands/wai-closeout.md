# WAI Closeout

Save session state so the next agent can pick up where we left off.

---

## Execution Context

- **Nodes:** spoke, hub
- **Paths Required:** spoke_path (current directory with WAI-Spoke/)

---

## Closeout Procedure

**Before beginning:** Read `_session_state.last_closeout` from `WAI-State.json` and store as `old_last_closeout`. Step 5 will overwrite it; Step 9b needs the old value.

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

### 5c. Lug Status Sync and Index Regeneration

1. Scan `bytype/*/open/` and `bytype/*/in_progress/` for lugs whose status changed this session
2. Move completed lugs to `bytype/{type}/completed/`
3. Move delivered signals from `undelivered/` to `delivered/`
4. Regenerate `WAI-LugIndex.jsonl` — one line per lug: `{id, type, status, title, folder, created_at}`
5. Report: "Moved N lugs. Index: T entries."

### 6. Finalize Session Track

Write a final track point (phase: `review`). Do NOT delete the track file — it's the permanent session record.

### 7. Documentation Updates

Update `CHANGELOG.md` if applicable. Generate descriptive commit message.

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

### 9c. Hub Signal Bulletin

For each signal lug with `impact > 7` and `status != "archived"`: if not already at `{hub_path}/WAI-Hub/Signals/incoming/{id}.json`, write it there. Skip if hub not connected.

### 10. Summary Generation

Output this block exactly after git push confirms — fill in real values, no placeholders:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WAI CLOSEOUT ✓  Session {N} · v{old} → v{new}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Done:
  ✓ {each accomplishment, one per line}

Signals:  {N extracted (impact N) | none}
Commit:   {short hash} — pushed to main
Next:     {next_session_recommendation, one line}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then stop. Do not add prose after the block.

### 11. Git Commit + Push

```bash
git add WAI-Spoke/ [other session files]
git commit -m "WAI Session [N]: [accomplishments] | [version]"
git push origin main
```

Push is mandatory. Do not ask for confirmation.

### 12. Verification

```bash
git status          # Must be clean
git log --oneline -1  # Verify commit
```

---

## Success Criteria

- [ ] Autosave lugs reconciled into session-summary
- [ ] Signals extracted (impact >= 8)
- [ ] Incomplete work documented with continuation guidance
- [ ] Version incremented, state updated
- [ ] Lug status synced, index regenerated
- [ ] Session track finalized
- [ ] Lugs dogfooded (if applicable)
- [ ] Teachings generated and published (if applicable)
- [ ] Committed and pushed to origin/main

---

*Closeout = Save game. Next agent continues the adventure.*

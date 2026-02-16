# WAI Closeout

**Session Completion Protocol - Mandatory for All Sessions**

End session with state preservation, signal extraction, and git commit/push.

## WAI Principles Reinforced

- **P1: Persistence** - Without closeout, nothing survives the session
- **P2: Verification** - Never assume success; verify with commands
- **P3: Stewardship** - Responsible completion, not silent exit
- **P7: Evolution Logging** - Capture learnings for future sessions

## Quick Reference

```
/wai-closeout              Standard closeout
/wai-closeout --dry-run    Preview without changes
/wai-shipit                Closeout + commit + push
```

---

## Execution Phases

### Phase 1: Reconciliation

1. **Scan for autosave lugs** in `WAI-Spoke/WAI-Lugs.jsonl`:
   - Find entries where `ty="autosave"` AND `reconciled=false`
   - Create ONE permanent `session-summary` lug capturing the session work
   - Mark autosave lugs: `reconciled=true`, `s="c"`
   - Report: `[N] autosave checkpoints reconciled`

2. **Extract high-impact signals** (impact >= 8):
   - Review session for significant decisions
   - Append to `WAI-Spoke/WAI-Lugs.jsonl` as `ty="signal"`
   - Report: `[N] signals extracted`

### Phase 2: State Updates

3. **Update WAI-State.json**:
   - Increment `_session_state.session_count`
   - Set `last_modified_by` to current AI model
   - Set `last_modified_at` to current ISO timestamp
   - Set `last_closeout` to current ISO timestamp
   - Append any new decisions to `decisions` array

4. **Clear session log**:
   - Truncate `WAI-Spoke/WAI-Session-Log.jsonl`
   - Ready for next session

### Phase 3: Git Operations

5. **Stage files**:
   ```bash
   git add WAI-Spoke/
   git add -A  # Include other session changes
   ```

6. **Generate commit message** summarizing session:
   - What was accomplished
   - Key decisions made
   - Session number

7. **Commit**:
   ```bash
   git commit -m "WAI Session [N]: [summary]"
   ```

8. **Push** (with user confirmation):
   ```bash
   git push origin main
   ```

### Phase 4: Verification (CRITICAL)

9. **Verify with actual commands** - do NOT assume success:

```bash
# 1. Local state clean?
git status
# MUST show: "nothing to commit, working tree clean"

# 2. Remote updated?
git log origin/main --oneline -1
# MUST show the new commit

# 3. Hashes match?
git log --oneline -1
# Local hash MUST equal remote hash
```

---

## Verification Checklist

**Closeout succeeds ONLY when ALL verify TRUE:**

- [ ] `git status` shows "nothing to commit, working tree clean"
- [ ] `git status` shows "up to date with 'origin/main'"
- [ ] `git log --oneline -1` shows new commit
- [ ] `git log origin/main --oneline -1` shows SAME commit hash
- [ ] WAI-State.json updated with current timestamp
- [ ] Session count incremented

**If ANY fails: Do NOT claim success. Diagnose and retry.**

---

## Fail Signals

### Critical (Stop Immediately)

```
GIT COMMIT FAILED
- Unstaged changes? Run: git add -A
- Merge conflicts? Run: git status
- No changes? Skip commit phase

GIT PUSH FAILED
- Network error? Check connectivity
- Auth failed? Check SSH: ssh -T git@github.com
- Branch protected? Check permissions
```

### Warning (Continue with Caution)

```
UNTRACKED FILES EXIST
- Review: git status
- Add or ignore as appropriate

MODIFIED FILES NOT STAGED
- Manual review required before commit
```

---

## Language Rules

**Never say:**
- "Probably succeeded"
- "Seems to have worked"
- "Should be pushed"
- "I believe it worked"

**Always say:**
- "Verified with `git status`"
- "Confirmed with `git log`"
- "Checked `origin/main`"
- "Working directory clean"

---

## Output Format

```
## Closeout Result

### Phase 1: Reconciliation
- [N] autosave lugs reconciled
- [N] high-impact signals extracted

### Phase 2: State Updates
- WAI-State.json updated (session #N)
- Session log cleared

### Phase 3: Git Operations
- Files staged: [count]
- Commit: [hash] "[message]"
- Push: [success/failed]

### Phase 4: Verification
- Local clean: [yes/no]
- Remote updated: [yes/no]
- Hashes match: [yes/no]

## Status: [SUCCESS / FAILED]

[If failed: diagnosis and remediation steps]
```

---

## Dry Run Mode

With `--dry-run`:
1. Execute all phases normally
2. Show what WOULD be committed
3. Do NOT actually commit or push
4. Ask: "Proceed with these changes?"

---

## Related Commands

- `/wai-shipit` - Closeout + commit + push in one command
- `/wai-time` - Check context usage before closeout
- `/wai-status` - Verify framework health

---

*Closeout is the session boundary. Without successful closeout, work is lost.*

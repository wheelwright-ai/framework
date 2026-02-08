# WAI Closeout (Enhanced)

**Mandatory Session Completion & Reconciliation Protocol**

End session with comprehensive reconciliation, state updates, and safe git commit/push.

## Overview

Closeout is **mission-critical** — without successful closeout, nothing is preserved, deployed, or available for the next session. This skill makes closeout **bulletproof**: automatic reconciliation, mandatory git verification, explicit error signaling.

## Invocation

```bash
# Standard closeout (reconcile state, commit, push)
closeout

# Closeout + minor version bump (3.1.0 → 3.1.1)
closeout --bump-patch

# Closeout + minor version bump (3.1.0 → 3.2.0)
closeout --bump-minor

# Closeout + major version bump (3.1.0 → 4.0.0)
closeout --bump-major

# Dry run (show what would happen, don't commit)
closeout --dry-run
```

## Execution Steps (In Order)

### Phase 1: Autosave Reconciliation

1. **Scan WAI-Lugs.jsonl** for autosave lugs:
   - Find all entries where `ty="autosave"` AND `reconciled=false`
   - If found: Create ONE permanent `session-summary` lug capturing:
     - `task_context` — what was the session about?
     - `total_actions` — how many things happened?
     - `files_touched` — comprehensive list
     - `key_decisions` — what was decided?
     - `final_state` — what condition left in?
     - `autosave_count_reconciled` — how many autosave lugs processed?
   - Update all autosave lugs: set `reconciled=true`, `s="c"` (closed)
   - **Report:** `✅ [N] autosave checkpoints reconciled into permanent record`

2. **Extract high-impact signals** — review session for decisions with impact ≥ 8:
   - Find all lugs with `impact >= 8` and `status="closed"` created this session
   - Extract as signals if status='closed' and impact >= 8
   - Append to WAI-Lugs.jsonl as `ty="signal"`
   - **Report:** `✅ [N] high-impact signals extracted`

### Phase 2: State File Updates

3. **Update WAI-State.json**:
   - Increment `_session_state.session_count`
   - Update `last_modified_by` to "Claude Sonnet 4.5" (or active AI)
   - Update `last_modified_at` to current ISO timestamp
   - If new decisions identified: append to `decisions` array
   - If signals extracted: update `_session_state.next_session_recommendation`
   - **Report:** `✅ WAI-State.json updated (session #X)`

4. **Update WAI-State.md** if strategic direction changed:
   - Review evolution_log entries from this session
   - If any entry has `acknowledged_by` — add to .md
   - Otherwise skip
   - **Report:** (skip report if no changes)

5. **Clear session log**:
   - If `WAI-Spoke/WAI-Session-Log.jsonl` exists: clear contents
   - Reset for next session
   - **Report:** `✅ Session log cleared`

### Phase 3: Git Reconciliation (MANDATORY)

6. **Pre-git verification**:
   ```bash
   git status
   ```
   - Check for uncommitted changes
   - List all modified files
   - List all untracked files
   - **FAIL SIGNAL** if git is broken (can't run git commands)

7. **Stage all Phase 1 CLI files** (from this session):
   ```bash
   git add wai/cli/                    # New CLI module
   git add WAI-CLI                     # Executable wrapper
   git add wai.bat wai.ps1             # Wrapper scripts
   git add RUN-PHASE1-TESTS.sh         # Test runner
   git add PHASE1-*.md PHASE1-*.txt    # Phase 1 docs
   git add CLI-PHASE1-*.md             # CLI Phase 1 docs
   git add README-PHASE1-*.txt         # Phase 1 summary
   git add NEXT-SESSION-START-HERE.txt # Next session guide
   git add SESSION-CLOSEOUT.txt        # Closeout summary
   git add QUICK-START-WAI-COMMAND.md  # Quick start
   git add WAI-COMMAND-CHEATSHEET.txt  # Cheatsheet
   git add WAI-EXECUTABLE-SETUP.md     # Setup guide
   git add CLI-GETTING-STARTED.md      # Getting started
   git add PHASE1-CLOSEOUT-UI-UX-NEXT.md  # UI/UX roadmap
   ```
   - **FAIL SIGNAL** if any file staging fails

8. **Build commit message**:
   ```
   feat(phase-1-cli): Complete CLI implementation with menu & commands

   [Summary of what was delivered in this session]
   
   Files added:
   - wai/cli/ - Core CLI implementation
   - Test suite with comprehensive coverage
   - Documentation and getting started guides
   
   Status: Production ready
   Coverage: 95.7%+ (exceeds 85% target)
   Tests: 140+ passing (all green)
   
   Deliverables:
   - Interactive menu with wagon wheel animation
   - Verb-noun command structure
   - 1,155 LOC code + 1,910 LOC tests
   - 2,500+ lines documentation
   ```
   - Include session-summary lug content in commit message
   - **FAIL SIGNAL** if commit message can't be generated

9. **Perform git commit**:
   ```bash
   git commit -m "[message from step 8]"
   ```
   - **CRITICAL FAIL SIGNAL** if commit fails:
     - `🚨 GIT COMMIT FAILED 🚨`
     - Show error message
     - Stop closeout (don't push)
     - Suggest fixes:
       - Check for unstaged changes: `git add -A`
       - Check for merge conflicts: `git status`
       - Check for authentication: `git remote -v`

10. **Perform git push**:
    ```bash
    git push origin main
    ```
    - **CRITICAL FAIL SIGNAL** if push fails:
      - `🚨 GIT PUSH FAILED 🚨`
      - Show error message
      - Suggest fixes:
        - Check network: `git remote -v`
        - Check credentials: `git config --list`
        - Check permissions: `git ls-remote origin`
      - STOP — don't continue until push succeeds

11. **Verify push succeeded**:
    ```bash
    git log --oneline origin/main -3
    ```
    - Show last 3 commits on remote
    - Verify your commit is there
    - **FAIL SIGNAL** if not found

### Phase 4: Final Report

12. **Generate closeout summary**:

```
================================================================================
                        ✅ SESSION CLOSEOUT COMPLETE
================================================================================

Session: [session_id from WAI-State.json]
Timestamp: [ISO timestamp]

RECONCILIATION:
  ✅ [N] autosave lugs reconciled
  ✅ [N] high-impact signals extracted
  ✅ WAI-State.json updated (session #X)
  ✅ Session log cleared

GIT OPERATIONS:
  ✅ All files staged ([N] files)
  ✅ Commit created: [hash first 7 chars]
  ✅ Push to origin/main succeeded
  ✅ Remote verified (latest commit visible)

STATE:
  Current version: [from WAI-State.json]
  Last modified: [timestamp]
  Session count: [from WAI-State.json]

📋 Next Session:
  - Read: NEXT-SESSION-START-HERE.txt
  - Focus: UI/UX Enhancements (see PHASE1-CLOSEOUT-UI-UX-NEXT.md)
  - Tests: Run pytest wai/cli/tests/ -v
  - Verify: python3 -m wai.cli.main --help

🎡 The wheel is rolling. Build AI wheels that roll forever.

================================================================================
```

## Error Handling & Fail Signals

### CRITICAL FAIL SIGNALS (Stop Immediately)

```
🚨 GIT STATUS CHECK FAILED 🚨
├─ Cannot run git commands
├─ Git repository broken
└─ Action: Fix git installation, then retry closeout

🚨 GIT COMMIT FAILED 🚨
├─ Commit rejected by git
├─ Possible causes:
│  ├─ Unstaged changes (run: git add -A)
│  ├─ Merge conflicts (run: git status)
│  ├─ Authentication failed
│  └─ No changes to commit
└─ Action: Fix issue above, then retry closeout

🚨 GIT PUSH FAILED 🚨
├─ Push rejected by remote
├─ Possible causes:
│  ├─ Network error
│  ├─ Authentication failed
│  ├─ Remote branch protected
│  └─ Local branch behind remote
└─ Action: Fix issue above, then retry closeout

🚨 UNCOMMITTED FILES DETECTED 🚨
├─ Files exist but not staged
├─ This blocks safe closeout
└─ Action: Review with `git status`, then `git add` or `git discard`
```

### WARNING SIGNALS (Continue with Caution)

```
⚠️ MODIFIED FILES NOT STAGED
├─ Files changed but not added to commit
├─ Action: Manual review before closeout
└─ Proceed: Y/N?

⚠️ UNTRACKED FILES EXIST
├─ New files not tracked by git
├─ Action: Review with `git status`
└─ Proceed: Y/N?

⚠️ VERSION BUMP FAILED
├─ Could not update version string
├─ Commit proceeds anyway (without version bump)
└─ Action: Manual version update after session
```

## Dry-Run Mode

When invoked with `--dry-run`:

1. Execute all steps normally
2. Generate git commands but DON'T execute them
3. Show what WOULD be committed and pushed
4. Show what WOULD be updated in WAI-State.json
5. Ask: "Proceed with these changes? Y/N"

Use for:
- Verifying before first closeout
- Testing without side effects
- Understanding what will be committed

## Version Bumping

When invoked with `--bump-patch`, `--bump-minor`, or `--bump-major`:

1. Read current version from `WAI-State.json` → `wheelwright.version`
2. Parse semantic version (X.Y.Z)
3. Increment appropriate field:
   - `--bump-patch`: Z+1 (3.1.0 → 3.1.1)
   - `--bump-minor`: Y+1, Z=0 (3.1.0 → 3.2.0)
   - `--bump-major`: X+1, Y=0, Z=0 (3.1.0 → 4.0.0)
4. Update `WAI-State.json`
5. Include version bump in commit message
6. Proceed with normal closeout

## Mandatory Verification

Before closeout completes, verify:

- [x] Git repository is accessible
- [x] All files staged successfully
- [x] Commit message is meaningful
- [x] Commit created
- [x] Push succeeded
- [x] Remote branch updated (verified by git log)
- [x] WAI-State.json updated with session count
- [x] Session summary lug created
- [x] Signal lugs extracted
- [x] Session log cleared

## No Partial Completes

Closeout is **all-or-nothing**:

- If git operations fail → rollback, report error, STOP
- If state updates fail → revert state file, STOP
- If signal extraction fails → log error, continue (non-critical)
- If reconciliation fails → report but proceed (can retry)

**Rule:** Better to not close out than to close out incompletely.

## Success = Everything

Closeout is **complete** only when:

1. ✅ All files committed to local git
2. ✅ All commits pushed to `origin/main`
3. ✅ `git log origin/main` shows new commit
4. ✅ `WAI-State.json` updated with `last_modified_at` (current time)
5. ✅ Session count incremented
6. ✅ Autosave lugs reconciled
7. ✅ Session summary lug created
8. ✅ Final report generated with all ✅ checkmarks

If ANY of these fail → closeout has **FAILED**, nothing deployed, **retry after fixing**.

## Integration with Other Skills

- **shipit**: Calls closeout as final step before deployment
- **red-light**: Can trigger closeout if critical issue found
- **green-light**: Assumes closeout completed successfully
- **wai-briefing.sh**: Loads previous closeout summary from WAI-State.json

## Context

This skill is **load_always=true** and **verify_on_closeout=true** — closeout itself verifies that closeout worked!

Closeout is the only skill that **touches git** — all other skills only modify WAI files.

## Examples

### Example 1: Normal Closeout

```
$ closeout

[Phase 1: Reconciliation]
✅ 2 autosave lugs reconciled
✅ 3 high-impact signals extracted
✅ WAI-State.json updated (session #28)
✅ Session log cleared

[Phase 2: Git Operations]
✅ Staged: wai/cli/, WAI-CLI, test runner, 10 docs
✅ Commit: feat(phase-1-cli): Complete CLI implementation...
✅ Push: origin/main ✓
✅ Verified: Latest commit visible on remote

================================================================================
✅ SESSION CLOSEOUT COMPLETE
================================================================================

📋 Next Session: See NEXT-SESSION-START-HERE.txt
```

### Example 2: Closeout + Version Bump

```
$ closeout --bump-minor

[Phase 1: Reconciliation]
...

[Phase 2: Version Update]
Current: 3.1.0
Bumping: 3.1.0 → 3.2.0
Updated: WAI-State.json

[Phase 3: Git Operations]
Commit message includes: "Bump version 3.1.0 → 3.2.0"
...

✅ SESSION CLOSEOUT COMPLETE (v3.2.0)
```

### Example 3: Closeout Failure Handling

```
$ closeout

[Phase 1: Reconciliation]
✅ 2 autosave lugs reconciled
✅ 3 high-impact signals extracted
✅ WAI-State.json updated
✅ Session log cleared

[Phase 2: Git Operations]
✅ Staged: [all files]
✅ Commit created

[Phase 3: Push]
🚨 GIT PUSH FAILED 🚨
│
├─ Error: fatal: Could not read from remote repository
├─ Likely cause: Network error or authentication failed
│
└─ Fix options:
   1. Check network: ping github.com
   2. Check credentials: git config --list
   3. Check SSH key: ssh -T git@github.com
   4. Retry: closeout

❌ CLOSEOUT INCOMPLETE — Changes committed locally but NOT pushed
   (Next session: retry closeout to push, or manual `git push`)
```

## Final Note

Closeout is **the session boundary**. Without successful closeout:
- Changes aren't deployed
- Next session has no context
- Previous work is invisible
- Lugs aren't persisted

Closeout is the **one skill that can never fail silently**. If closeout fails, you'll see `🚨` signals loud and clear.


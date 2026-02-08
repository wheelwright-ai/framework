# WAI Closeout

**Mandatory Session Completion & Reconciliation Protocol**

End session with comprehensive reconciliation, state updates, and safe git commit/push.

**WITH OBSERVATION LOGGING** - Every action logged for session playback and audit trail.

Implements the enhanced CloseoutWorkflow from `wai/closeout.py` with 4-phase execution and observation logging.

## Quick Reference

```bash
# Standard closeout (reconcile, commit, push)
closeout

# + minor version bump
closeout --bump-minor

# + dry run (preview only)
closeout --dry-run
```

## Execution Phases

1. **Autosave Reconciliation** - Reconcile autosave lugs into session-summary
2. **State Updates** - Update WAI-State.json with session count, timestamp, signals
3. **Git Operations** - Stage, commit, push to origin/main (MANDATORY)
4. **Verification** - Verify push succeeded and commit visible on remote

## Critical Points

- **Git is mandatory** — without git, there is no persistence
- **Fail signals** — CRITICAL failures stop closeout immediately (🚨 signals)
- **Version bumping** — Optional flags for semantic versioning
- **Dry-run mode** — Preview changes without committing

## Feedback Requirements

**CRITICAL:** Do NOT assume success. Verify explicitly.

### Use This Template for Closeout Results
👉 **`.claude/commands/wai-closeout-feedback-v2.md`**

This template ensures:
- ✅ Clear success outcomes (verified with actual commands)
- ❌ Clear failure outcomes (with solutioning steps)
- No assumptions, no vague language
- Remediation provided if any phase fails

### Verification Commands (Do NOT Skip)

```bash
# After closeout, VERIFY with these commands:

# 1. Check local state
git status
# MUST show: "nothing to commit, working tree clean"
# AND: "Your branch is up to date with 'origin/main'"

# 2. Check remote state
git log origin/main --oneline -1
# MUST show the new commit hash

# 3. Compare
git log --oneline -1
# Local commit hash MUST match remote

# 4. If any mismatch → Push failed → Use feedback template solutioning
```

## Mandatory Verification Checklist

**Closeout succeeds ONLY when ALL items below verify as TRUE:**

- [ ] `git status` shows "nothing to commit, working tree clean"
- [ ] `git status` shows "Your branch is up to date with 'origin/main'"
- [ ] `git log --oneline -1` shows new commit hash
- [ ] `git log origin/main --oneline -1` shows SAME hash
- [ ] WAI-State.json exists and updated with current timestamp
- [ ] Session count incremented (verify in file)
- [ ] Observations logged to observations.jsonl
- [ ] Session summary recorded

**If ANY verification fails:**
1. Do NOT claim success
2. Identify which verification failed
3. Use feedback template solutioning
4. Fix the issue
5. Retry closeout

---

## Do NOT Use These Phrases

❌ "Probably succeeded"  
❌ "Seems to have worked"  
❌ "Should be pushed"  
❌ "Likely committed"  
❌ "I believe it worked"  

**Use ONLY:**  
✅ "Verified with git status"  
✅ "Confirmed with git log"  
✅ "Checked origin/main"  
✅ "Working directory clean"  

---

For full specification, see: `.claude/commands/wai-closeout-enhanced.md`

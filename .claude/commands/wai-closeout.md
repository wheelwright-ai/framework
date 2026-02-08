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

## Mandatory Verification Checklist

- [x] Git repository accessible
- [x] All files staged
- [x] Commit message meaningful and generated from session-summary
- [x] Commit created locally
- [x] Push succeeded to origin/main
- [x] Remote branch verified (git log shows new commit)
- [x] WAI-State.json updated with current timestamp
- [x] Session count incremented
- [x] Autosave lugs reconciled
- [x] Session summary lug created
- [x] Final report generated with all ✅ checkmarks

**Closeout succeeds only when ALL items above are complete.**

For full specification, see: `.claude/commands/wai-closeout-enhanced.md`

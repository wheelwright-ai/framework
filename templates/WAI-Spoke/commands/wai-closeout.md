# WAI Closeout

End session with smart processing.

## Instructions

Execute the closeout protocol:

1. **Scan for unknown files** in WAI-Spoke/ - flag any untracked files
2. **Reconcile autosave lugs** — find all lugs where autosave=true AND reconciled=false:
   - If entries exist: create ONE permanent summary lug (ty="session-summary") in WAI-Lugs.jsonl
     capturing: task_context, total actions, files touched, key decisions, final state
   - Mark all autosave lugs: set reconciled=true, s="c"
   - Report: "[N] autosave checkpoints reconciled into permanent record"
3. **Extract signals** - review session for high-impact decisions (impact >= 8)
4. **Update WAI-State.json**:
   - Increment `_session_state.session_count`
   - Update `last_modified_by` and `last_modified_at`
   - Add any new decisions to decisions array
5. **Append to wheel-signals.jsonl** if high-impact learnings found
6. **Update WAI-State.md** if strategic direction changed
7. **Clear session log** after extracting insights
8. **Report** what was processed

Output format:
```
**Session Closeout Complete**

- Session #X ended
- [X] signals extracted
- [X] decisions logged
- Session log cleared
- State files updated

Ready for: `git commit` or `Shipit` to commit now
```

If the WAI CLI is available, suggest running `WAI closeout` for full processing.

## Context

### Conversation Logging

Every user and assistant turn is logged to `WAI-Spoke/WAI-Session-Log.jsonl`.

**Hub learning cannot proceed** until Closeout processes and clears the log.

During closeout, the session log is reviewed for high-impact decisions, then cleared. The extracted insights are preserved in WAI-State.json decisions and WAI-Signals.jsonl.

### Autosave Reconciliation

All autosave lugs (ty=autosave, reconciled=false) are summarized into ONE permanent session-summary lug, then marked reconciled=true, s="c".

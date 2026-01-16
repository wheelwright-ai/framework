# WAI Closeout

End session with smart processing.

## Instructions

Execute the closeout protocol:

1. **Scan for unknown files** in WAI-Spoke/ - flag any untracked files
2. **Extract signals** - review session for high-impact decisions (impact >= 8)
3. **Update WAI-State.json**:
   - Increment `_session_state.session_count`
   - Update `last_modified_by` and `last_modified_at`
   - Add any new decisions to decisions array
4. **Append to wheel-signals.jsonl** if high-impact learnings found
5. **Update WAI-State.md** if strategic direction changed
6. **Clear session log** after extracting insights
7. **Report** what was processed

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

# WAI Status

Health check with recommendations.

## Instructions

1. Read `WAI-Spoke/WAI-State.json` for current state
2. Check the session log size: `WAI-Spoke/WAI-Session-Log.jsonl` (count lines)
3. Check git status for uncommitted changes
4. Check hub sync status from `wheelwright.development_health`
5. Scan `WAI-Spoke/sessions/` for environment session files

6. Output a status table:
   ```
   **Wheelwright Status**

   | Check | State |
   |-------|-------|
   | Hub connected | Yes/No |
   | Last sync | X days ago |
   | Session log | X turns |
   | Uncommitted | X files |
   | Foundation | Complete/Incomplete |
   | Environments | X active |
   ```

7. If multiple environments exist, show environment table:
   ```
   **Active Environments**

   | Environment | Last Active | Entries | Hub |
   |-------------|-------------|---------|-----|
   | claude-code on laptop | today | 15 | Yes |
   | cursor on desktop | 2 days ago | 8 | No |
   ```

8. Provide recommendations based on findings:
   - Session log > 10 turns: "Consider `Closeout` soon"
   - Days since sync > 7: "Hub may have new learnings - run `Teach`"
   - Uncommitted changes: "Uncommitted work detected"
   - High-impact decisions logged: "Signals ready to share - run `Learn`"
   - Unreconciled entries > 20: "Run `Closeout` to reconcile environment sessions"

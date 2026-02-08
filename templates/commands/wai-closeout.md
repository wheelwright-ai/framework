# WAI Closeout

End session ceremony: extract signals, update state, clear log.

## What It Does

Marks formal end of work session. Transforms session work into persistent state:

1. **Extract signals** — Find high-impact decisions (impact >= 8)
2. **Update WAI-State** — Log session info, analytics, evolution
3. **Clear session log** — Flush WAI-Session-Log.jsonl for next session
4. **Prepare hub sync** — Create WAI-Signals.jsonl for /wai-learn

## When to Use

- **Session ending:** Run before stopping work
- **Context full:** Auto-recommended when context > 70%
- **Before sleep/break:** Preserve work, avoid loss

## How It Works

1. Scan session for high-impact decisions (impact >= 8)
   - Log to WAI-Signals.jsonl
2. Update WAI-State.json._session_state:
   - session_count += 1
   - last_modified_at = now
   - key_topics (extracted from work)
   - files_modified (git-based)
3. Flush WAI-Session-Log.jsonl (clear for next session)
4. Output summary of session work

## Example Session

User: I want to closeout now

AI: Initiating closeout...

Extracting signals (impact >= 8):
- Decision: Moved rules to skills-based architecture. Impact: 10
- Decision: Added teach cycle skill sync. Impact: 9

Updating WAI-State.json:
- Session count: 27 -> 28
- Key topics: [skill-system, teach-cycle-integration]
- Files modified: [WAI-Guide.md, CLAUDE.md, wai-teach.md, templates/commands/]

Clearing session log...

**Closeout Complete**

Summary:
- Session 28 recorded
- 2 high-impact signals logged
- Ready for hub sync (/wai-learn)
- Next session will load fresh context

## Related Skills

- /wai-shipit — Closeout + commit to git
- /wai-learn — Push signals to hub
- /wai-time — Check context usage before closeout

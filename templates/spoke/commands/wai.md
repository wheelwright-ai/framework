# WAI Wakeup

Show unified "WAI Point" briefing - where are we, what's the status, what should I work on?

## Instructions

**IMPORTANT:** Use the unified briefing script instead of custom formatting.

1. Run the briefing script:
   ```bash
   bash WAI-Spoke/_framework/wai-briefing.sh
   ```

2. Display the output to the user exactly as generated.

3. This unified briefing shows:
   - Project identity and phase
   - Current environment
   - Active work (prioritized backlog)
   - Context health (tokens, hub, git)
   - Recent high-impact changes
   - Next actions
   - Quick command reference

4. The briefing is identical to what hooks show and what "wai point" questions trigger.

5. After showing the briefing, ask if the user wants recommendations on what to work on next.

## Context

### Core Files Reference

| File | Purpose | Access |
|------|---------|--------|
| `WAI-State.json` | Technical spec, foundation, session state | UPDATE |
| `WAI-State.md` | Strategic context, vision | UPDATE |
| `WAI-Skills.jsonl` | Skill registry with metadata | READ |
| `WAI-Lugs.jsonl` | Active task/dependency graph | UPDATE |
| `WAI-Signals.jsonl` | High-impact learnings | APPEND |
| `WAI-Session-Log.jsonl` | Conversation turns (cleared on closeout) | APPEND |
| `WAI-Guide.md` | Legacy AI instructions (deprecated, see skills) | READ |

### Session State Protocol

On session start, check `_session_state` in WAI-State.json:
- `last_modified_by` / `last_modified_at` — who last touched the project
- `requires_review` — if true, surface the review reason before proceeding
- `session_count` — increment on each significant update

When making changes, update `_session_state`:
```json
{
  "last_session_id": "descriptive-session-id",
  "last_modified_by": "AI name",
  "last_modified_at": "ISO-8601",
  "session_count": "<increment by 1>"
}
```

### Multi-Environment Sessions

Each environment (tool + machine) gets its own session log:
```
WAI-Spoke/sessions/
  claude-code-laptop.jsonl
  cursor-desktop.jsonl
```

On wakeup, scan `WAI-Spoke/sessions/` to surface recent activity from other tools/machines.

**Environment auto-detection**: tool, machine (hostname or `WAI_MACHINE` env var), OS, parent session (`WAI_PARENT_SESSION`).

### Active Skills

On wakeup, load `WAI-Spoke/WAI-Skills.jsonl` and report any active advisory watches:
- Advisory skills with active watcher conditions
- Skills that recommend themselves at session start

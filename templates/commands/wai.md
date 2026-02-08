# WAI Wakeup

Unified briefing: where are we, what''s the status, what to work on.

## What It Does

When you first join this project (or resume a session), /wai:
1. Loads perfect context from WAI-State.json and WAI-State.md
2. Shows you what changed since last session
3. Checks for uncommitted git work
4. Briefs you on project scope and collaboration style

This is the entry point to Wheelwright continuity.

## When to Use

- **Session start:** Always run /wai first
- **Orientation needed:** Lost context? Run /wai
- **After long break:** Get reoriented before work

## How It Works

1. Read WAI-Spoke/WAI-State.json
   - Last session info
   - Project foundation (identity, scope, boundaries)
   - Analytics (sessions completed, token efficiency)

2. Read WAI-Spoke/WAI-State.md
   - Strategic vision and evolution log
   - Key decisions and their rationale
   - Active work and next steps

3. Check git status
   - List uncommitted changes
   - Ask if resuming or starting fresh

4. Brief the user
   - Project name and purpose
   - Last session date/time and summary
   - Current environment (tool + machine)
   - Any scope drift or foundation gaps

## Example

User: /wai

AI Output:


## Usage Pattern



## Related Skills

- /wai-status — Quick health check
- /wai-closeout — End session ceremony
- /wai-rules — Show boundaries

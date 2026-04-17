# Gemini Instructions for Wheelwright Framework

This project uses Wheelwright (WAI) for session continuity.

## Session Start

On your first turn in this repo:

1. Read `AGENTS.md`.
2. Read `WAI-Spoke/WAI-State.json`.
3. Follow `templates/commands/wai.md` to produce the WAI Point briefing.
4. Treat this `GEMINI.md` read as already satisfying `templates/commands/wai.md` Step 1 (`Load Integration File`).
5. Do not re-read `GEMINI.md` or rescan parent `GEMINI.md` files while executing wakeup unless the user explicitly asks.
6. Show the briefing, then respond to the user's message.

## Notes

- This framework repo uses `templates/commands/wai.md` as the canonical wakeup source.
- Keep this file thin. Behavioral rules live in `templates/commands/`.
## Wakeup Convergence

- Finish the WAI Point briefing before asking for approval on teachings or side actions.
- During wakeup, summarize teachings from filenames/frontmatter only.
- Do not read full teaching bodies during wakeup unless the user explicitly asks to review them now.

# Gemini Instructions for Wheelwright Framework

**This project uses Wheelwright for AI session continuity.**

## Session Start

On your first turn, run the WAI wakeup protocol:

1. Read `templates/commands/wai.md` — follow its steps to produce the WAI Point briefing
2. Show the briefing to the user (project state, active work, context health)
3. Then respond to the user's message

Gemini does not support hooks — invoke `/wai` manually at session start, or read `templates/commands/wai.md` and follow its protocol.

## Behavioral Protocols

**All behavioral rules live in skills.** Read the relevant skill file when you need guidance.

Skills are in `templates/commands/`:

| Skill | What It Does |
|-------|-------------|
| `wai.md` | Wakeup protocol — produces WAI Point briefing |
| `wai-closeout.md` | Session preservation — reconcile, signal, commit |
| `wai-shipit.md` | Quality gates + closeout for releases |
| `wai-teach.md` | Push templates and lugs to target nodes |
| `wai-learn.md` | Inbox processing protocol |
| `wai-foundation.md` | Project identity, goals, boundaries |
| `wai-lug-schema.md` | Lug system — schema, lifecycle, authoring |
| `wai-complexity-gate.md` | Planning gate (2+ files OR 6+ steps) |
| `wai-rules.md` | Project boundaries |
| `wai-principles.md` | WAI principles P1-P9 |

## Session Commands

- `/wai` — Unified briefing
- `/wai-closeout` — End session ceremony
- `/wai-shipit` — Closeout + commit
- `/wai-teach` — Push to hub/spokes
- `/wai-learn` — Process inbox
- `/wai-time` — Token usage
- `/wai-rules` — Show boundaries

## Key Files

- `WAI-Spoke/WAI-State.json` — Project state, session metadata
- `WAI-Spoke/WAI-Lugs.jsonl` — Work items, signals, decisions (append-only)
- `WAI-Spoke/WAI-State.md` — Strategic vision

---

**Skills are the source of truth. This file is a pointer.**

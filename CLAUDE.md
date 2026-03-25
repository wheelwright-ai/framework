# Claude Code Instructions for Wheelwright Framework

**This project uses Wheelwright for AI session continuity.**

## Session Start

On your first turn, run the WAI wakeup protocol:

1. Read `templates/commands/wai.md` — follow its steps to produce the WAI Point briefing
2. Show the briefing to the user (project state, active work, context health)
3. Then respond to the user's message

The hook in `.claude/hooks/user-prompt-submit.sh` injects this directive automatically.

## Behavioral Protocols

**All behavioral rules live in skills.** Read the relevant skill file when you need guidance.

Skills are in `templates/commands/`:

| Skill | What It Does |
|-------|-------------|
| `wai.md` | Wakeup protocol — produces WAI Point briefing |
| `wai-closeout.md` | Session preservation — reconcile, signal, commit (production release gate included) |
| `wai-foundation.md` | Project identity, goals, boundaries |
| `wai-lug-schema.md` | Lug system — schema, lifecycle, authoring (auto-trigger) |
| `wai-complexity-gate.md` | Planning gate — 2+ files OR 6+ steps (auto-trigger) |
| `wai-stewardship-guard.md` | Scope drift detection (auto-trigger) |
| `wai-ide-setup.md` | Hook configuration for Claude Code and other tools |
| `wai-rules.md` | Project boundaries |
| `wai-principles.md` | WAI principles P1-P9 |

When in doubt: read the relevant skill file. Don't memorize rules.

## Session Commands

- `/wai` — Unified briefing
- `/wai-closeout` — End session ceremony (integrated production release gate)
- `/wai-time` — Token usage
- `/wai-rules` — Show boundaries
- `/wai-status` — Quick health check

## Hook Setup

See `templates/commands/wai-ide-setup.md` for hook configuration.
Current hook: `.claude/hooks/user-prompt-submit.sh`

---

**Skills are the source of truth. This file is a pointer.**

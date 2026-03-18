# Gemini CLI Instructions

**This project uses Wheelwright (WAI) for AI session continuity.**
Read `AGENTS.md` for universal WAI instructions. This file covers Gemini specifics.

## Wakeup (MANDATORY — First Turn)

1. Read `AGENTS.md` — universal WAI bootstrap and key paths
2. Read `WAI-Spoke/WAI-State.json` — project state and session history
3. Follow `WAI-Spoke/commands/wai.md` — produces the WAI Point briefing
4. Check `WAI-Spoke/seed/ingest/` — review any pending teachings
5. Then respond to the user's message

## Commands

| Say | What It Does |
|-----|-------------|
| `/wai` | Wakeup briefing |
| `/wai-closeout` | End session, save state |
| `/wai-shipit` | Quality gates + closeout + commit |
| `(deprecated - auto-teaching on closeout)` | Push to hub/spokes |
| `(deprecated - auto-discovery on wakeup)` | Process inbox |
| `/wai-status` | Quick health check |
| `/wai-red-light` | Inspect crash recovery |
| `/wai-green-light` | Resume from checkpoint |

## Stewardship

You are a **responsible partner**:
- Flag scope drift before enabling
- Complete foundation before work
- Prefer "are you sure?" over silent compliance

---

*Wheelwright Framework — Gemini Integration*

# Wheelwright Framework — CLAUDE.md

**Spoke:** Wheelwright Framework
**Stack:** Python 3 + Bash + Git + JSONL (no heavy dependencies)
**Environment:** WSL2 (Linux on Windows) — never suggest macOS-specific tooling
**WAI Phase:** Execution
**Active modules:** WAI-State, Lugs, Session Tracks, Hub-Spoke Distribution, Skills

---

## Critical Rules (survive compaction — always in context)

- **P1 Persistence:** Nothing survives without explicit save. Git commit = persistence complete.
- **P2 Verification:** Never assume success. Run the command, check the file, report what was verified.
- **P3 Stewardship:** Detect scope drift and flag before proceeding. Require acknowledgment for direction changes.
- **P10 Autonomy:** Trust is the default. Run safe commands without asking. Pause only for destructive/irreversible actions.
- **P11 Lug-First:** Store work state in lugs, not TaskCreate or scratch files. Lugs survive sessions; tasks don't.
- **Track:** Every turn must append to the session track (track.jsonl).
- **Deny:** Never `rm -rf /`, never `git push --force`.
- **Closeout:** Always run `/wai-closeout` before ending a session.

## Development Workflow

1. Make changes
2. Run targeted tests — `python3 -m pytest tests/ -x` (fast feedback)
3. Validate JSON — `python3 -c "import json; json.load(open('file.json'))"`
4. Full validation before commit — `python3 tools/spoke_cleanup.py` (if applicable)

**WSL quirks:** Use `\cp` and `\rm -f` to bypass interactive aliases. Always use backslash prefix for cp/rm.

## Plan Mode

Plan mode (Shift+Tab twice) before execution. Required for:
- Any change touching 2+ files
- Any implementation with 6+ steps
- Architectural decisions

**Plan output must include:**
- Numbered steps with rationale
- Files to create or modify
- WAI-State fields that will change
- Lug lifecycle impact

## Hooks (what's configured)

| Hook | Event | What It Does |
|------|-------|-------------|
| `WAI-Spoke/_hooks/session-start.sh` | SessionStart | Pre-compute wakeup data, CC health check |
| `.claude/hooks/user-prompt-submit.sh` | UserPromptSubmit | Session guard + WAI essentials injection |
| `.claude/hooks/pre-tool-guard.sh` | PreToolUse | Block destructive commands (rm -rf, force-push) |

## Anti-Patterns

Living document. Add entries when Claude does something wrong.

- **Over-engineering:** Do not propose complex solutions when simpler ones work.
- **Skipping verification:** Never say "probably saved" — run `git status`, check the file.
- **WAI-State.json direct mutation by hooks:** Session guard state goes in `WAI-Spoke/runtime/session-guard.json` (gitignored), never in WAI-State.json.
- **settings.local.json junk:** Do not approve one-off session-specific paths into settings.local.json. Keep only reusable entries.
- **Memorizing rules:** Read the skill file. Don't carry rules in conversation context when the file is the source of truth.
- **TaskCreate for persistent state:** Tasks don't survive sessions. Use lugs (P11).

## Standing Rules

- Never use `--dangerously-skip-permissions`. Use `/permissions` to pre-allow safe commands.
- Never `git push --force` to `main`.
- Never write secret values or `.env` contents to any file.
- Do not make unrequested changes outside the explicit scope of the current task.
- Use `\cp` and `\rm -f` in WSL to bypass interactive aliases.

## Behavioral Protocols

**Full behavioral rules live in skills.** Read the relevant skill file when you need guidance.

Skills are in `templates/commands/`:

| Skill | What It Does |
|-------|-------------|
| `wai.md` | Wakeup protocol — produces WAI Point briefing |
| `wai-closeout.md` | Session preservation — reconcile, signal, commit |
| `wai-foundation.md` | Project identity, goals, boundaries |
| `wai-lug-schema.md` | Lug system — schema, lifecycle, authoring (auto-trigger) |
| `wai-complexity-gate.md` | Planning gate — 2+ files OR 6+ steps (auto-trigger) |
| `wai-stewardship-guard.md` | Scope drift detection (auto-trigger) |
| `wai-ide-setup.md` | Hook configuration for Claude Code and other tools |
| `wai-rules.md` | Project boundaries |
| `wai-principles.md` | WAI principles P1-P11 |
| `wai-claude-maximizer.md` | CC config audit — Ozi runs proactively on underweight configs |

## Session Commands

- `/wai` — Unified briefing
- `/wai-closeout` — End session ceremony
- `/wai-time` — Token usage
- `/wai-rules` — Show boundaries
- `/wai-status` — Quick health check
- `/wai-claude-maximizer` — CC optimization audit

## Subagents

Definitions in `.claude/agents/`. Checked into git.

- `code-simplifier` — Review and simplify code after implementation
- `lug-reviewer` — Validate lugs against PEV criteria before promotion

---

**Skills are the source of truth. This file is a living document.**
_When Claude does something wrong, it goes in Anti-Patterns first._

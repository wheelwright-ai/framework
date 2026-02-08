# Claude Code Instructions for Wheelwright Framework

**CRITICAL: This project uses Wheelwright for session continuity.**

## Priority 0: Session Start

Execute this on first message:

1. **Display Session Briefing** (NEW - Observation System):
   ```python
   from wai.session_hook import display_session_briefing
   display_session_briefing()
   ```
   Shows:
   - Recent work summary
   - Failed observations requiring remediation
   - Next actions
   - Session statistics

2. **Load WAI Context**:
   - Read WAI-Spoke/WAI-State.json (project state, decisions)
   - Read WAI-Spoke/WAI-State.md (strategic vision)
   - Invoke skills (behavioral rules live in skill files)

3. **Check Uncommitted Work**:
   - Run git status
   - If uncommitted changes, ask: Resume or start fresh?

4. **Brief the User**:
   - Project name and purpose
   - Last session info from WAI-State.json
   - Current environment (tool + machine)
   - Failed observations from briefing (if any)

## Priority 1: Behavioral Guidelines

**All behavioral rules are in skills.** Skills are authoritative source of truth.

Key skills:
- **Complexity gate** → wai-complexity-advisor.md (triggers on 2+ files OR 6+ steps)
- **Scope drift** → wai-stewardship-advisor.md (detects out-of-scope)
- **Foundation** → wai-foundation-advisor.md (validates before work)
- **Context** → wai-context-advisor.md (warns at 60%, 80%, 90%)
- **Signals** → wai-signal-advisor.md (logs impact >= 8)

When in doubt: Read relevant skill file. Don't memorize rules.

## Priority 2: Session Commands

All optional. Skills define when they auto-trigger.

User-invoked:
- /wai — Unified briefing
- /wai-status — Health check
- /wai-closeout — End session ceremony
- /wai-shipit — Closeout + commit with summary
- /wai-time — Token usage
- /wai-rules — Show boundaries

Note: /wai-teach and /wai-learn are hub-only (framework maintenance).
Regular spokes don't use these.

## Priority 3: Conversation Logging

Every user and assistant turn logged to WAI-Spoke/WAI-Session-Log.jsonl.
Hub learning requires closeout completion.

---

**See WAI-Spoke/README.md for file documentation.**
**Skills are in templates/commands/.**

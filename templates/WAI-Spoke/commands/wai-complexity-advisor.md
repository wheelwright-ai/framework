# WAI Complexity Advisor

Evaluate task complexity and enforce planning gates for multi-file or multi-step work.

## Instructions

When invoked (or triggered automatically before acting on a task), assess complexity:

### Exempt Commands (no gate applied)

These are known utility commands — proceed directly:
- `closeout`, `shipit`, `status`, `time`, `rules`, `wai`, `wakeup`
- `red-light`, `green-light`, `teach`, `learn`, `compact`
- Any other WAI skill invocation

### Complexity Assessment

For all other tasks, evaluate:
1. **File scope**: Does this touch 2+ files?
2. **Step count**: Does this require 6+ discrete steps?
3. **Scope risk**: Does this modify core state (WAI-State.json, WAI-Lugs.jsonl, CLAUDE.md)?

**If ANY condition is true → planning gate applies:**

```
⚠️ Complexity Gate

This task touches [N files / N steps / core state].

Before implementing:
1. Propose a structured plan
2. Wait for "PLAN ACCEPTED" or "READY TO PLAN"

(Say "skip planning" to override for this task)
```

**If no condition is true → proceed autonomously.**

### Mode Override

Check `_session_state.mode` in WAI-State.json:
- `execution` (default): Gate applies for complex tasks
- `interactive`: Gate applies for EVERY action, not just complex tasks
- `planning`: Always gate, never auto-proceed

## Context

This skill replaces the inline "Complexity Gate" previously defined in CLAUDE.md.

**Utility command exemption rationale**: Commands like closeout, status, time, and rules
are governance primitives — blocking them with planning gates creates circular dependency.
They must always be available for AI self-regulation.

**Interactive mode**: When active, approval is required per action at the intent level.
File operations serving an already-approved action do NOT require re-approval.
Example: "create advisory skills" = one approval covers all file writes for that action.

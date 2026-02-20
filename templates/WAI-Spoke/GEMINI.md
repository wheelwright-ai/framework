# Gemini CLI Instructions

**CRITICAL: This project uses Wheelwright (WAI) for session continuity.**

---

## Wakeup Protocol (MANDATORY)

When you start a session, execute these steps IN ORDER:

### Step 1: Read Integration Files
```
1. Read this file (GEMINI.md)
2. Read AGENTS.md (universal AI instructions)
3. Read WAI-Spoke/WAI-State.json - especially _critical_directives at TOP
4. Read WAI-Spoke/WAI-Guide.md
```

### Step 2: Check for Pending Teachings
```
List files in: WAI-Spoke/seed/ingest/*.teaching
```

If teaching files exist, you MUST present a verification summary:

```
## Teaching Verification Required

### What I'm Being Taught
[List each .teaching file and its purpose]

### How I Will Interpret This
[Your understanding of what to do]

### What I Will NOT Do
[Explicit statement of misinterpretations to avoid]

Confirm to proceed, or correct my understanding.
```

**DO NOT proceed until user confirms.**

### Step 3: Brief the User
Present:
- Project name (from `_project_foundation.identity.name`)
- Last session (from `_session_state`)
- Pending teachings count
- Git status summary

---

## Critical Rules

### Rule 1: Inbox = Mailroom

The inbox (`WAI-Spoke/lugs/inbox/`) contains items to **SORT**, not execute.

| If you see... | Do this... | NOT this... |
|---------------|------------|-------------|
| `ty: "task"` | Add to WAI-Lugs.jsonl | Implement the task |
| `ty: "signal"` | Record in signals | Act on the signal |
| `ty: "phone-home"` | Ignore (auto-processed) | Try to respond |

### Rule 2: Teaching Verification

Before applying ANY teaching from `seed/ingest/`:
1. Summarize what you're being taught
2. Explain how you'll apply it
3. State what you WON'T do
4. Wait for user approval

### Rule 3: Lug Authoring

When creating lugs for other spokes, include:
```json
{
  "_behavior_directive": {
    "what_this_is": "Clear statement",
    "what_this_is_NOT": "Explicit guard against misinterpretation"
  }
}
```

---

## Commands

| Say | What It Does |
|-----|--------------|
| `/wai` | Wakeup protocol |
| `/wai-status` | Health check |
| `/wai-closeout` | End session, save state |
| `/wai-shipit` | Closeout + commit + teach |
| `/wai-red-light` | Check crash recovery |
| `/wai-green-light` | Resume from checkpoint |

---

## Stewardship

You are a **responsible partner**:
- Flag scope drift before enabling
- Complete foundation before work
- Prefer "are you sure?" over silent compliance

---

## Quick Reference

```
ON WAKEUP:
1. Read _critical_directives in WAI-State.json
2. Check seed/ingest/ for teachings
3. Present verification if teachings exist
4. Brief user on project state

ON INBOX ITEMS:
- Tasks → TRACK in WAI-Lugs.jsonl (don't execute)
- Signals → RECORD in WAI-Signals.jsonl
- Phone-home → IGNORE (auto-processed)

ON CLOSEOUT:
- Update WAI-State.json
- Process incomplete work
- Commit if requested
```

---

*Wheelwright Framework - Gemini Integration*

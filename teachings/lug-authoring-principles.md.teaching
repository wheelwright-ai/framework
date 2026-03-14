# WAI Lug Authoring Principles

**MANDATORY: Follow these principles when creating any lug, task, or cross-spoke message.**

---

## Core Principle

> **Lugs travel across sessions, models, and contexts. They must be unambiguous enough that ANY agent can interpret them correctly WITHOUT access to your current context.**

You cannot assume the receiving agent:
- Knows your project's conventions
- Has the same capabilities as you
- Interprets ambiguous terms the same way
- Has access to conversation history

---

## The Misinterpretation Test

Before sending any lug, ask:

1. **Could a different model read this and do something harmful?**
2. **Could this be interpreted as "execute immediately" vs "track for later"?**
3. **Are there implicit assumptions that aren't stated?**
4. **Would I understand this with zero context?**

If any answer is "yes" or "maybe", add more clarity.

---

## Required Lug Structure

Every lug MUST include:

### 1. `_behavior_directive` (for actionable lugs)

```json
"_behavior_directive": {
  "what_this_is": "Clear statement of what this lug represents",
  "what_this_is_NOT": "Explicit statement of what NOT to do",
  "processing_agent": "Who/what handles this (code/AI/user)",
  "expected_outcome": "What should happen when processed correctly"
}
```

### 2. Explicit Type Classification

```json
"ty": "task",           // or signal, phone-home, idea, etc.
"category": "task",     // Redundant but ensures clarity
"is_executable": false  // Explicit flag if relevant
```

### 3. Self-Contained Content

Don't write:
```json
"content": {"action": "implement"}  // Ambiguous - implement what? how?
```

Write:
```json
"content": {
  "request_type": "work_item_tracking",
  "description": "Add this to WAI-Lugs.jsonl as a tracked task. Do NOT execute.",
  "details": "Full description of the work to be tracked...",
  "when_to_implement": "When user selects this task from the task list"
}
```

---

## Anti-Patterns to Avoid

### BAD: Ambiguous Action Fields

```json
// WRONG - "action" implies execution
{"action": "implement_feature"}
{"action": "fix_bug"}
{"action": "execute_scaffold"}
```

```json
// RIGHT - Clear intent
{"request_type": "track_work_item", "work_description": "..."}
{"request_type": "status_report", "no_action_required": true}
```

### BAD: Implicit Context

```json
// WRONG - Assumes knowledge
{"task": "Update the config"}
```

```json
// RIGHT - Self-contained
{
  "task_type": "configuration_change",
  "target_file": "WAI-Spoke/WAI-State.json",
  "change_description": "Add hub_analysis section with last_analysis_at field",
  "tracking_only": true,
  "do_not_execute_automatically": true
}
```

### BAD: Missing Negative Constraints

```json
// WRONG - No guardrails
{"description": "Generate status report"}
```

```json
// RIGHT - Explicit boundaries
{
  "description": "Generate status report by READING existing state files",
  "constraints": {
    "read_only": true,
    "no_code_modification": true,
    "no_file_creation_except": ["outbox/*.jsonl"]
  }
}
```

---

## Lug Detail Levels

### Level 1: Minimal (NEVER use for cross-spoke)
```json
{"task": "fix auth"}  // Useless - no context
```

### Level 2: Basic (internal notes only)
```json
{
  "task": "Fix authentication",
  "file": "auth.py"
}
```

### Level 3: Standard (cross-session, same project)
```json
{
  "ty": "task",
  "title": "Fix authentication timeout in auth.py",
  "description": "Session timeout not being refreshed on activity",
  "files_involved": ["src/auth.py", "src/session.py"],
  "tracking_only": true
}
```

### Level 4: Cross-Spoke (REQUIRED for inter-project lugs)
```json
{
  "_behavior_directive": {
    "what_this_is": "A work item to be ADDED to the task tracker",
    "what_this_is_NOT": "An instruction to execute immediately",
    "processing_agent": "inbox_processor.py routes to WAI-Lugs.jsonl",
    "ai_agent_action": "None until user selects task"
  },
  "ty": "task",
  "category": "task",
  "title": "Fix authentication timeout in auth.py",
  "source_wheel_id": "framework",
  "destination_wheel_id": "basher",
  "created_at": "2026-02-17T12:00:00Z",
  "content": {
    "request_type": "work_item_tracking",
    "description": "Session timeout not being refreshed on user activity. Token expires even when user is active.",
    "files_likely_involved": ["src/auth.py", "src/session.py"],
    "suggested_approach": "Check session refresh logic in middleware",
    "do_not_execute_automatically": true,
    "implementation_trigger": "User explicitly selects this task"
  }
}
```

---

## Cross-Spoke Communication Checklist

Before sending a lug to another spoke:

- [ ] `_behavior_directive` is present and complete
- [ ] `what_this_is_NOT` explicitly prevents misinterpretation
- [ ] No implicit project-specific knowledge required
- [ ] `source_wheel_id` and `destination_wheel_id` are set
- [ ] Content is self-contained (no "see above" references)
- [ ] Action words are qualified ("TRACK this task" not just "implement")
- [ ] Receiving agent knows whether to execute or just record

---

## Signal vs Task vs Phone-Home

| Type | Purpose | AI Execution? | Example |
|------|---------|---------------|---------|
| `task` | Track work item | NO - add to tracker | "Implement caching" → added to task list |
| `signal` | Share insight | NO - record pattern | "Found useful pattern" → logged |
| `phone-home` | Request status | AUTO by code | inbox_processor.py handles it |
| `idea` | Suggest consideration | NO - record for review | "Consider using Redis" |

---

## Summary

```
CLARITY > BREVITY

When in doubt:
- Add more context, not less
- State what NOT to do
- Include _behavior_directive
- Assume the receiver knows NOTHING about your context
```

**The cost of over-specification: A few extra bytes.**
**The cost of under-specification: Dangerous misinterpretation.**

Always choose over-specification for cross-spoke communication.

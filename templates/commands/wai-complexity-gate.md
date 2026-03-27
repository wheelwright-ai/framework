# Complexity Gate

Planning gate for multi-file or multi-step tasks; exempts utility commands.

## What It Does

Auto-triggers when:
- Task affects 2+ files, OR
- Implementation requires 6+ steps

Prevents scope creep by requiring structured planning before complex work.

**Exempted:** All WAI utility commands (wakeup, closeout, status, etc.)

## When It Triggers

Example 1: Refactoring
User: Refactor auth module (will touch service, middleware, tests, config)
AI: Complex task detected. Planning required. Propose a plan?

Example 2: Multi-step feature
User: Implement new teach command workflow (6+ steps)
AI: Complex task detected. Planning required. Propose a plan?

Example 3: Simple fix (NOT triggered)
User: Fix typo in CLAUDE.md
AI: (Proceeds autonomously, no planning gate)

## Expected Workflow

**User requests complex task →**
**AI detects (2+ files OR 6+ steps) →**
**AI blocks and asks for plan →**
**User says PLAN ACCEPTED →**
**AI proceeds with implementation →**
**Result: Intentional work, no surprises**

## Example Session

User: I want to refactor the skill system to add versioning (touches: WAI-Skills.jsonl, 8 skill files, auto-teaching (closeout Step 9b).md, manifest.json, tests). Should take 10+ steps.

AI: Complex task detected (9 files, 10+ steps).

**Proposed Plan:**

Step 1: Add version field to skill schema
Step 2: Update WAI-Skills.jsonl schema docs
Step 3-10: Add version to each skill file
Step 11: Update auto-teaching (closeout Step 9b).md to compare versions
Step 12: Write tests
Step 13: Update manifest.json

Ready? (yes/no)

User: PLAN ACCEPTED

AI: (Proceeds with implementation)

## Model-Task Awareness

In addition to complexity, this gate watches for **architectural signals** — indicators that the current task needs stronger model judgment than the active model may provide.

### Architectural Signals

- User is correcting fundamental assumptions about system design
- Task involves defining new protocols or boundaries
- Decisions affect multiple spokes or the entire wheel
- Task requires "should we?" judgment, not "how do we?" execution
- Agent is making assumptions about projects it hasn't verified
- Agent is creating multiple new artifacts without user validation

### When Detected

Prompt the user **once per session** (not repeatedly):

> "This work involves architectural decisions. I'm running as {model_name}. For design-level work where judgment matters, consider `/model` to switch to Sonnet or Opus."

### Model Tier Guidance

| Tier | Good For | Watch Out |
|------|----------|-----------|
| Haiku | Execution, file ops, following plans, tests | Misses assumption errors, treats design as execution |
| Sonnet | Balanced work, moderate design + execution | May miss novel architectural issues |
| Opus | Architecture, protocol design, reviewing prior work | Higher token cost; use when judgment matters |

### Session Logging

Model switches are recorded in `WAI-State.json` under `model_log`. On closeout, note which models were active and what task types they handled. This enables retrospective analysis.

See lug: `decision-model-task-awareness-protocol` for full protocol and incident record.

## Plan Validation (Before Showing to User)

When creating an implementation plan (epic + child lugs), self-validate before presenting:

**Required on each implementation lug:**
- `behavior_specification` — input schema, process steps, output schema, state changes
- `test_requirements` — at least unit tests + integration tests, with one concrete example test case
- `acceptance_criteria` — specific, testable, objective (not "looks good")
- `dependencies` — `requires` (blocks), `blocks` (blocked-by), valid DAG

**Required on epic:**
- Child tasks ordered by sequence
- Parallelization declared (which tasks can run in parallel)
- Dependency graph with no circular deps

**Validation gates:**
- No vague language ("make it better", "refactor", "improve" without specifics)
- Each acceptance criterion maps to a named test
- Behavior spec has all three: input + process + output

**Only present plan to user after self-validation passes.** Append to plan:
```
✅ Plan validated — behavior, tests, acceptance criteria, and dependencies complete.
```

**Scope thresholds for when validation is required:**
- Always: epics, implementation lugs, 3+ files affected, anything with test requirements
- Optional: small bug fixes (<20 lines, 1 file), documentation updates, config changes

## Related Skills

- /wai-rules — Show scope boundaries
- /wai-stewardship-guard — Detect scope drift

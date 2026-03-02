# Complexity Advisor

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

User: I want to refactor the skill system to add versioning (touches: WAI-Skills.jsonl, 8 skill files, wai-teach.md, manifest.json, tests). Should take 10+ steps.

AI: Complex task detected (9 files, 10+ steps).

**Proposed Plan:**

Step 1: Add version field to skill schema
Step 2: Update WAI-Skills.jsonl schema docs
Step 3-10: Add version to each skill file
Step 11: Update wai-teach.md to compare versions
Step 12: Write tests
Step 13: Update manifest.json

Ready? (yes/no)

User: PLAN ACCEPTED

AI: (Proceeds with implementation)

## Related Skills

- /wai-rules — Show scope boundaries
- /wai-stewardship-advisor — Detect scope drift

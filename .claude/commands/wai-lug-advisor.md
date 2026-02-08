# WAI Lug Advisor

Guidance on the lug system: task graph management, schemas, and minification.

## Instructions

When invoked, provide guidance on lug operations:

1. **List**: Show open lugs by priority (`WAI lug list` or read WAI-Lugs.jsonl directly)
2. **Create**: Help construct a well-formed lug entry
3. **Close**: Mark lug as closed (s="c") after verifying completion
4. **Explain**: Clarify lug schema fields on request

### AI Workflow with Lugs

1. **Wakeup**: Browse open lugs to understand current priorities
2. **Execution**: Create lugs for sub-tasks or newly discovered bugs
3. **Commit**: During closeout, suggest closing lugs associated with the session

### Lug Creation Template

```json
{
  "i": "<12-char hex>",
  "t": "<type code>",
  "ty": "<type>",
  "title": "<brief imperative title>",
  "s": "o",
  "status": "open",
  "description": "<full description>",
  "created_at": "<ISO-8601>",
  "priority": "<low|medium|high>",
  "tags": [],
  "blocks": [],
  "blocked_by": []
}
```

Generate `i` from first 12 chars of SHA256 of the title.

## Context

### Lug Minification Legend

**Lug ID Format (i):**
- 12-character hex strings (e.g., `4f1e687a652f`)
- First 12 characters of SHA256 hash
- 16 trillion combinations (2^48) — collision-resistant
- Human-readable, copy-paste friendly, token-efficient

**Lug Type Codes (t):**
- `t` = task
- `d` = decision
- `l` = learning
- `p` = policy
- `b` = bug
- `e` = epic

**Status Codes (s):**
- `o` = open
- `p` = in_progress
- `c` = closed
- `b` = blocked

**Priority Flags:**
- `session_focus` — Current session epic
- `before_next_epic` — Must complete before starting new epics

**Scope:**
- `only_this_spoke` — Learning/policy applies to this project only
- `all_spokes` — Applies to all projects of this type
- `wheel` — Applies globally (hub + all spokes)

**Conditional Loading Fields:**
- `load_always` (boolean) — Auto-load on session start
- `verify_on_closeout` (boolean) — Test/verify before closeout
- `verification_count` (int) — How many times verified
- `verification_target` (int) — Target verifications (default 5)

**Minimal required fields:** `i`, `t`, `title`

All lugs support extensible fields — add any data you need.

# WAI Lug Advisor

**Lug System Protocol — task graph management, schemas, authoring, and lifecycle.**

---

## Execution Context

- **Nodes:** spoke, hub
- **Exposure:** spoke.chat:local, spoke.chat:external

---

## What Is A Lug

A lug is a JSON object stored in `WAI-Spoke/WAI-Lugs.jsonl` (one per line). Lugs are the persistent memory of the session system — they carry work items, decisions, signals, and protocols across sessions, models, and projects.

**Lugs travel across contexts.** They must be unambiguous enough that ANY agent can interpret them correctly WITHOUT your current conversation history.

---

## Key Mapping (Minified ↔ Full)

| Short | Full | Purpose |
|-------|------|---------|
| `i` | `id` | Unique identifier |
| `t` | `title` | Brief imperative title |
| `ty` | `type` | Lug type (see catalog below) |
| `s` | `status` | Current status |
| `ca` | `created_at` | ISO-8601 creation timestamp |
| `gb` | `gathered_by` | Agent or session that created it |
| `v` | `version` | Version number (foundation, core-protocol lugs) |

Both short and full key forms are valid. Prefer short keys for storage efficiency.

---

## Status Values

| Code | Meaning |
|------|---------|
| `o` or `open` | Open / pending — not started |
| `p` or `in-progress` | In progress — actively being worked |
| `c` or `closed` or `resolved` | Complete / closed |
| `b` or `blocked` | Blocked by another lug or external dependency |

---

## Complete Lug Type Catalog

| Type | Purpose | Auto-process? |
|------|---------|--------------|
| `task` | Work item to track and implement | No — add to tracker |
| `bug` | Defect requiring a fix | No — add to tracker |
| `feature` | New capability or enhancement | No — add to tracker |
| `review` | Something needing review or verification | No — add to tracker |
| `epic` | Large multi-session effort (blocked until tasks clear) | No — add to tracker |
| `signal` | High-impact decision or insight (impact >= 8) | No — record in WAI-Signals.jsonl |
| `foundation` | Project identity, boundaries, approach | No — defines the project |
| `session-summary` | Completed session record (autosaves reconciled) | No — archive only |
| `autosave` | Crash-recovery checkpoint from mid-session | Reconcile at closeout |
| `policy` | Project rules or constraints | No — reference document |
| `observation` | Factual observation logged for pattern detection | No — record |
| `learning` | Cross-session insight worth preserving | No — record |
| `maintenance` | Infrastructure or tooling work | No — add to tracker |
| `core-protocol` | Framework protocol documentation (replaces reference docs) | No — reference document |
| `delivery_confirmation` | Confirms lug was delivered to target spoke | Auto-acknowledged |
| `phone-home` | Hub requests status report from spoke | Auto-handled by learn |
| `config` | Configuration update for node | Applied during learn |
| `session` | Historical session record (legacy) | No — archive only |
| `challenge` | Problem-centric anchor for idea lugs — stable problem statement with linked hypotheses | No — append-only record in WAI-Challenges.jsonl |

---

## Lug ID Generation

Generate `i` from first 12 characters of SHA256 of the title:
```
i = sha256(title)[:12]
```

Example: `sha256("Fix authentication timeout") → 4f1e687a652f`

For named lugs (foundation, epic): use human-readable IDs:
```
"lug-fnd-abc12345"    (foundation)
"epic-slimdown-20260227"  (epic with date)
"ss-e48218a6"         (session-summary)
```

---

## Lug Creation Template

Minimal required fields: `i`, `ty`, `t` (or `title`):

```json
{
  "i": "4f1e687a652f",
  "ty": "task",
  "t": "Fix authentication timeout in session middleware",
  "s": "o",
  "ca": "2026-02-28T10:00:00Z",
  "gb": "claude-sonnet-4-6",
  "description": "Session timeout not being refreshed on user activity. Token expires even when user is active.",
  "priority": "medium",
  "impact": 5,
  "tags": ["auth", "session"],
  "blocks": [],
  "blocked_by": []
}
```

Append to `WAI-Spoke/WAI-Lugs.jsonl` (one JSON object per line).

---

## PEV Fields (Required for Actionable Lugs)

**Every `task`, `epic`, `bug`, `feature`, and `review` lug MUST include PEV fields.** These transform a lug from a decision record into a workable ticket that any agent can pick up cold.

| Field | Purpose | Example |
|-------|---------|---------|
| `perceive` | What to read/examine before starting. File paths, current state, context. | `"Read templates/spoke/WAI-State.json for current schema. Check hub-registry.json for spoke list."` |
| `execute` | Concrete steps to take. What to build, modify, or design. | `"1. Add wheel.framework_version to template. 2. Update spoke-upgrade.sh to set it."` |
| `verify` | How to confirm the work is done correctly. | `"Run spoke-upgrade.sh on a test spoke. Confirm wheel.framework_version appears in WAI-State.json."` |

```json
{
  "i": "4f1e687a652f",
  "ty": "task",
  "t": "Add framework_version to spoke template",
  "s": "o",
  "perceive": "Read templates/spoke/WAI-State.json — current wheel section has no framework_version field. Read bootstrap/spoke-upgrade.sh — it already sets this field on upgrade.",
  "execute": "Add wheel.framework_version: null to the template WAI-State.json wheel section. This field gets populated by spoke-upgrade.sh or on first closeout.",
  "verify": "Confirm field exists in template. Run spoke-upgrade.sh --dry-run on a test path. Verify new spokes created from template include the field."
}
```

**Why this matters:** A lug without PEV forces the next agent to explore the codebase guessing where to start. PEV gives them a runway — `perceive` orients, `execute` directs, `verify` closes the loop.

---

## Dogfooding Lugs (Required Before Closeout)

**Before finalizing any lug intended for another agent (including future-you), validate it:**

1. **State what you'll test** — which lug(s), what aspects
2. **State how deep** — schema check, self-containment review, sub-agent simulation
3. **Wait for user approval** on scope
4. **Run the validation** — at minimum, check:
   - Can a naive agent understand this without conversation context?
   - Are PEV fields present and actionable?
   - Does `perceive` point to real, findable files?
   - Does `verify` define a concrete "done" state?
5. **Fix gaps found** before the lug ships

**When to dogfood:**
- Before closeout (batch-validate all lugs created this session)
- Before sending cross-spoke lugs (higher stakes — misinterpretation risk)
- When creating epics with children (validate the parent→child navigation works)

**The naive agent test:** Send the lug to a sub-agent with only AGENTS.md and lug schema knowledge. Ask it to draft a plan. Where it gets stuck = where the lug needs more detail.

---

## Lug Lifecycle

```
CREATE → TRACK → WORK → COMPLETE → RECONCILE → ARCHIVE
```

1. **CREATE** — Append new lug to WAI-Lugs.jsonl with `s: "o"`
2. **TRACK** — Visible in wakeup briefing; user selects for work
3. **WORK** — Update `s: "p"` when starting; update description with progress
4. **COMPLETE** — Set `s: "c"` when done; add `resolution` field
5. **RECONCILE** — Autosave lugs consolidated into session-summary at closeout
6. **ARCHIVE** — Closed lugs remain in WAI-Lugs.jsonl for history

WAI-Lugs.jsonl is **append-only**. Do not delete or modify past entries — append new versions.

---

## WAI-Challenges.jsonl

First-class append-only file alongside `WAI-Lugs.jsonl`. Stores stable problem statements independently of the hypotheses (idea lugs) that address them.

**Schema:**
```json
{
  "i": "chal-{3-5-word-slug}",
  "ty": "challenge",
  "statement": "The stable problem text — refined after wai-improve Step 3",
  "first_seen": "ISO-8601 — when this challenge was first articulated",
  "first_seen_in": "idea lug ID of the first idea that identified this challenge",
  "status": "open | resolved | deferred",
  "related_lugs": ["idea and epic IDs addressing this challenge"],
  "resolution_notes": "How it was resolved (if status=resolved)"
}
```

**Append-only:** Override entries follow the same convention as `WAI-Lugs.jsonl` — append a new line with the same `i` and updated fields. Latest entry per `i` wins.

**Lifecycle:** Created by `/wai-improve` Step 3b on first intake of a challenge. Updated (override entry) each time a new idea links to it. Resolved when the challenge is addressed.

**Relationship to ideas:** Challenge = stable problem. Idea = one hypothesis. One challenge can have many ideas across sessions and models. The `challenge_id` field on an idea lug is the link back.

**Slug generation:** Take 3–5 most meaningful words (nouns, verbs — skip stopwords). Join with hyphens, lowercase.
Example: `"Recurring friction across sessions is invisible"` → `chal-recurring-friction-invisible`

---

## AI Workflow with Lugs

1. **Wakeup** — Browse open lugs (s=o, s=p) to understand priorities
2. **Session** — Create lugs for sub-tasks or newly discovered bugs
3. **Autosave** — Checkpoint lugs with `ty: "autosave"` and `reconciled: false`
4. **Closeout** — Reconcile autosaves, signal high-impact items, update status

---

## Cross-Spoke Authoring (Critical Safety)

When creating lugs that travel to other nodes, ALWAYS include `_behavior_directive`:

```json
{
  "_behavior_directive": {
    "what_this_is": "A work item to be ADDED to the task tracker",
    "what_this_is_NOT": "An instruction to execute immediately",
    "processing_agent": "inbox router appends to WAI-Lugs.jsonl",
    "expected_outcome": "Item appears in task list for user to prioritize"
  },
  "ty": "task",
  "source_wheel_id": "framework",
  "destination_wheel_id": "basher",
  "t": "Fix authentication timeout",
  "ca": "2026-02-28T10:00:00Z"
}
```

**The misinterpretation test** — before sending any lug, ask:
1. Could a different model read this and execute it immediately?
2. Could this be interpreted as "do now" vs "track for later"?
3. Are there implicit assumptions not stated?
4. Would I understand this with zero context?

If any answer is "yes or maybe" → add more clarity.

**Cross-spoke checklist:**
- [ ] `_behavior_directive` present and complete
- [ ] `what_this_is_NOT` explicitly prevents misinterpretation
- [ ] `source_wheel_id` and `destination_wheel_id` set
- [ ] Content is self-contained (no "see above" references)
- [ ] Action words are qualified ("TRACK this" not just "implement")

---

## Priority Flags

- `priority: "before_next_epic"` — Must complete before starting any new epic
- `priority: "session_focus"` — Current session's primary epic
- `priority: "high"` / `"medium"` / `"low"` — Standard priority

---

## Scope Flags

- `"only_this_spoke"` — Applies to this project only
- `"all_spokes"` — Applies to all projects of this type
- `"wheel"` — Applies globally (hub + all spokes)

---

## Conditional Loading Fields

- `load_always: true` — Auto-load on session start
- `verify_on_closeout: true` — Test/verify before closeout
- `verification_count: N` — Times verified so far
- `verification_target: 5` — Target verifications (default 5)

---

## Signal vs Task vs Phone-Home

| Type | Purpose | AI Execution? | Example |
|------|---------|--------------|---------|
| `task` | Track work item | NO — add to tracker | "Implement caching" → task list |
| `signal` | Share insight (impact >= 8) | NO — record in Signals | "Found useful pattern" → logged |
| `phone-home` | Request status | AUTO by learn | inbox processor handles |
| `foundation` | Project identity | NO — defines project | Identity and boundaries |

---

## Anti-Patterns

**BAD — ambiguous action:**
```json
{"action": "implement_feature"}
```

**GOOD — explicit intent:**
```json
{"request_type": "work_item_tracking", "work_description": "...", "do_not_execute_automatically": true}
```

**BAD — implicit context:**
```json
{"task": "Update the config"}
```

**GOOD — self-contained:**
```json
{"task_type": "configuration_change", "target_file": "WAI-Spoke/WAI-State.json", "change_description": "Add hub_analysis section", "tracking_only": true}
```

---

## Related Skills

- `/wai-closeout` — Reconciles autosaves, creates session-summary
- `/wai-learn` — Processes incoming lugs from inbox
- `/wai-teach` — Delivers outbox lugs to target nodes

---

*Lugs = Persistent memory. CLARITY > BREVITY for cross-spoke communication.*

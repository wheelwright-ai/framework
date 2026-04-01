# WAI Lug Schema

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
| `implementation` | Execution-control lug for non-trivial planned work | No — add to tracker |
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

## `implementation` Lugs

`implementation` is a first-class lug type for non-trivial execution batches, especially when work sits under an epic and needs ordered implementation.

Use an `implementation` lug when:
- work spans multiple files or child lugs
- sequence matters
- the implementer should review the plan before editing
- multiple agents may contribute and need one durable control record

Expected behavior:
- link the work lugs it composes
- specify sequence, safe parallelism, and non-goals
- record implementer review before implementation begins
- bounce back to the user if concerns remain
- track contributors and sub-agent use
- capture implementation feedback and observations on completion
- include a ready-to-build gate and review rubric so the implementer knows how the work will be graded
- require a remediation plan on the lug before retrying work that was kicked back on quality
- update the workflow action tracker at major handoffs so continuation agents know who has the ball

Persistence gate:
- review is not complete until written back to the implementation lug
- before editing target files, update review status, review history, current owner, and intended next step
- if approval only exists in chat, the review is incomplete
- implementation is not complete until the lug is updated with what changed, verification actually performed, observations, and follow-up work, plus a session-summary lug is appended

**Canonical Lifecycle:**
```text
planned → review_pending → approved_to_implement → in_progress → in_remediation → ready_for_recheck → implemented → accepted
```

**Review/Reconciliation Workflow:**

All `implementation` lugs must include canonical review fields:
- `review_notes[]`: Persistent review findings with id, timestamp, model attribution, type (concern/gap/suggestion/acceptance-note/blocked), scope, message, file references, status (open/acknowledged/resolved/rejected), resolution notes
- `review_cycles[]`: Review history with cycle number, timestamp, model attribution, result (approved/needs_remediation/accepted), summary, blocking/non-blocking note IDs  
- `acceptance`: Final acceptance status with timestamp and model attribution

**Workflow Rules:**
1. **All review notes persistent**: Review findings recorded in lug, not just chat
2. **Remediation tracking**: Open review notes prevent final acceptance
3. **Status transitions**: If review finds gaps → `in_remediation` → fix → `ready_for_recheck` → re-review → `accepted`
4. **Model attribution**: Every review cycle and note tracks which model performed the review
5. **Blocking vs non-blocking**: Review notes classified to determine if remediation required
6. **Lug-centered interaction**: For non-trivial implementation work, use the implementation lug as the durable interaction surface; chat should mostly direct the implementer to load the lug and address persisted notes
7. **Ready-to-build gate**: Before implementation starts, the implementer must record that the lug is ready to build using explicit readiness checks
8. **Self-grading**: Before requesting recheck, the implementer must run the lug's review rubric against its own work and persist the outcome
9. **Remediation plan**: If a quality review moves the lug to `in_remediation`, the builder must persist a remediation plan on the same lug before retrying. The plan should explain what failed, what will change, how it will be verified, and whether user review is needed.
10. **Workflow action tracker**: Update workflow.current_phase/current_owner/current_state at handoffs so agents can instantly see who owns the ball

Recommended additional fields:
- `ready_to_build_gate`: required readiness checks before implementation begins
- `review_rubric`: ready-to-build questions plus acceptance checks used by implementer and reviewer
- `remediation_plan`: required when a kicked-back implementation is about to be retried
- `workflow`: action tracker with phases (plan/work/verify/accept), owners (planner/builder/validator/user), and states (open/in_progress/complete)

If work is non-trivial, especially epic-backed and plan-driven, prefer creating an `implementation` lug rather than relying on conversational handoff.

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

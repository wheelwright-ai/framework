# WAI Lug Advisor

**Lug System Protocol — task graph management, schemas, authoring, and lifecycle.**

---

## Execution Context

- **Nodes:** spoke, hub
- **Exposure:** spoke.chat:local, spoke.chat:external

---

## Canonical Storage

**Single source of truth:** This file is the canonical declaration for lug storage. All other protocol files defer here.

| What | Where | Notes |
|------|-------|-------|
| All lugs | `WAI-Spoke/WAI-Lugs.jsonl` | Append-only JSONL, one object per line |
| Signals | `WAI-Spoke/WAI-Lugs.jsonl` | Signals ARE lugs with `impact >= 8` — no separate file |
| Inbox/outbox | `WAI-Spoke/lugs/inbox/` and `lugs/outbox/` | Delivery channel only — not durable storage |
| Hub bulletin | `WAI-Hub/Signals/incoming/` | High-impact lugs copied here at closeout for cross-spoke visibility |

`WAI-Spoke/WAI-Signals.jsonl` is **retired**. Do not create it or write to it.

---

## What Is A Lug

A lug is a JSON object stored in `WAI-Spoke/WAI-Lugs.jsonl` (one per line). Lugs are the persistent memory of the session system — they carry work items, decisions, signals, and protocols across sessions, models, and projects.

**Lugs travel across contexts.** They must be unambiguous enough that ANY agent can interpret them correctly WITHOUT your current conversation history.

---

## Key Mapping (Minified ↔ Full)

| Short | Full | Purpose |
|-------|------|---------|
| `i` | `id` | Unique identifier |
| `t` | `title` | **Indicative, descriptive title (5+ words)**. Explain the *intent* or *impact* (e.g., "Implement dual-watermark fix for historian ASCII sort bug" NOT "Fix bug"). |
| `ty` | `type` | Lug type (see catalog below) |
| `s` | `status` | Current status |
| `ca` | `created_at` | ISO-8601 creation timestamp |
| `gb` | `gathered_by` | Agent or session that created it |
| `v` | `version` | Version number (foundation, core-protocol lugs) |

**Title Policy:**
- **No generic session summaries:** "Session 35 summary" is BANNED.
- **Good:** "Session 35: Successfully implemented chat-to-track epic and historian dual-watermark"
- **Good:** "Task: Update WAI-State.json schema to include hub_fingerprint"
- **Bad:** "Task: Update state"

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
| `signal` | High-impact decision or insight (impact >= 8) | No — signals ARE lugs; store in WAI-Lugs.jsonl (no separate file) |
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

## PEV Chain Pattern

For work requiring structured perceive→execute→verify reasoning, use linked lugs instead of PEV fields on a single record.

### Link Schema

Each lug in a PEV chain carries:
- `pev_role`: one of `perceive` | `execute` | `verify`
- `pev_chain_id`: shared identifier for the chain (e.g. `pev-feature-auth-20260322`)

### Chain Structure

| Role | Purpose | Key Fields |
|------|---------|-----------|
| `perceive` | Frames the problem: evidence, conditions, unknowns | `pev_role`, `pev_chain_id`, `evidence[]`, `conditions[]` |
| `execute` | Records intended action or implementation plan | `pev_role`, `pev_chain_id`, `plan`, `target_files[]` |
| `verify` | Defines proof the work is correct | `pev_role`, `pev_chain_id`, `criteria[]`, `verified_at` |

### Example

```json
{"id": "pev-auth-perceive", "type": "work", "pev_role": "perceive", "pev_chain_id": "pev-auth-20260322", "title": "Auth system: problem framing", "evidence": ["Users can bypass 2FA via API"], "conditions": ["Only affects API endpoints, not web UI"]}
{"id": "pev-auth-execute", "type": "work", "pev_role": "execute", "pev_chain_id": "pev-auth-20260322", "title": "Auth system: implementation plan", "plan": "Add 2FA enforcement middleware to API router"}
{"id": "pev-auth-verify", "type": "work", "pev_role": "verify", "pev_chain_id": "pev-auth-20260322", "title": "Auth system: verification criteria", "criteria": ["API requests without valid 2FA token receive 403", "Existing web UI 2FA flow unchanged"]}
```

### When to Use

Use PEV chains for: architectural decisions, bug investigations, features with clear acceptance criteria.
Skip for: simple tasks, signal lugs, session summaries.

### Compatibility

Existing lugs with `perceive`/`execute`/`verify` as plain fields remain valid. Dual-read: both patterns are acceptable. New structured work should prefer the chain pattern.

---

## Canonical Type System

### Top-Level Types (use these for new lugs)

| Type | Purpose |
|------|---------|
| `epic` | Large work body spanning multiple sessions |
| `work` | Executable work item (replaces task/bug/feature) |
| `decision` | Architectural or directional choice |
| `finding` | Investigation result or discovered fact |
| `test` | Test specification or result |
| `session-summary` | End-of-session record |
| `signal` | High-impact learning (impact >= 8) |

### work.kind Field

When creating a `work` lug, set `work.kind` to classify the work:

| work.kind | Replaces | Use when |
|-----------|---------|---------|
| `task` | type: "task" | Defined unit of work |
| `bug` | type: "bug" | Defect or broken behavior |
| `feature` | type: "feature" | New capability |
| `implementation` | type: "implementation" | Capability rollout |

**Example:**
```json
{"id": "work-fix-auth-20260322", "type": "work", "work": {"kind": "bug"}, "title": "Fix auth bypass"}
```

### Dual-Read Compatibility

Existing lugs with `type: "task"`, `type: "bug"`, or `type: "feature"` remain valid and are read correctly. Do not bulk-rewrite existing lugs. New lugs should use canonical types.

**Reading old lugs:** treat `type: "task"` as equivalent to `type: "work", work.kind: "task"`.

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

## Required Field Defaults

When authoring a lug and a field is not explicitly specified, use these defaults:

| Field | Default | Notes |
|-------|---------|-------|
| `s` | `"o"` | Open — not started |
| `ca` | current UTC timestamp | ISO-8601, e.g. `"2026-03-17T04:44:00Z"` |
| `impact` | `5` | Medium. Adjust up/down based on scope. |
| `priority` | `"medium"` | Use `"before_next_epic"` only when truly blocking |
| `blocks` | `[]` | Empty array |
| `blocked_by` | `[]` | Empty array |
| `tags` | `[]` | Empty array |

### `gb` (gathered_by) — Model ID Required

`gb` MUST be the **actual model identifier** of the AI that authored the lug.

```
CORRECT:  "gb": "claude-sonnet-4-6"
CORRECT:  "gb": "claude-opus-4-6"
CORRECT:  "gb": "gemini-1.5-pro"
WRONG:    "gb": "Sparky"
WRONG:    "gb": "Assistant"
WRONG:    "gb": "AI"
```

**Why this matters:** Self-chosen names (Sparky, Max, etc.) create ambiguity. `gb` is an audit field — it must answer "which model wrote this?" unambiguously across sessions, tools, and time. If you are working in a v1 spoke that has `current_ai: "Sparky"` in WAI-State.json, ignore that field for `gb` — use your model ID.

Optionally append session ID for traceability: `"gb": "claude-sonnet-4-6 (session-20260317-0444)"`

---

## PEV Fields (Required for Actionable Lugs)

**Every `task`, `epic`, `bug`, `feature`, `review`, and `implementation` lug MUST include PEV fields.** These transform a lug from a decision record into a workable ticket that any agent can pick up cold.

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

## `implementation` Lugs

`implementation` is a first-class lug type for **non-trivial execution batches**.

Use an `implementation` lug when:
- work spans multiple files or multiple child lugs
- work sits under an `epic` and needs ordered execution
- the implementer needs a review gate before editing
- multiple agents or sub-agents may participate and need one control record
- you want durable implementation feedback, not just a one-shot task description

**Default expectation:** If work is non-trivial, especially if it is epic-backed and requires a plan, create an `implementation` lug.

An `implementation` lug should:
- link the child work lugs it composes
- state sequence: what is sequential, what may parallelize safely, what is deferred
- require implementer review before editing begins
- record whether the implementer is satisfied to proceed
- bounce back to the user if concerns or ambiguities remain
- record who worked on it and any contributing sub-agents
- capture completion feedback, implementation observations, and follow-up risks

Recommended fields in addition to the normal lug fields:
- `parent_epic`
- `composes`
- `target_files`
- `non_goals`
- `sequence`
- `implementer_review`
- `subagent_policy`
- `verification_requirements`
- `implementation_feedback`
- `ownership`

**Canonical Lifecycle:**
```text
planned → review_pending → approved_to_implement → in_progress → in_remediation → ready_for_recheck → implemented → accepted
```

**Status Definitions:**
- `planned`: Initial creation, ready for review
- `review_pending`: Under review by implementer
- `approved_to_implement`: Review passed, ready for implementation
- `in_progress`: Implementation in progress  
- `in_remediation`: Review found gaps, being fixed
- `ready_for_recheck`: Remediation complete, needs re-review
- `implemented`: Implementation complete but pending final acceptance
- `accepted`: Fully complete with all review notes resolved

**Review/Reconciliation Workflow:**

All `implementation` lugs must include these canonical fields:

```json
{
  "ready_to_build_gate": {
    "required": true,
    "checks": [
      "Scope is bounded and non-goals are explicit",
      "Dependencies, blockers, and target files or target objects are named",
      "Sequence is clear enough to execute without chat context",
      "Verification requirements are concrete and relevant",
      "Review sources and review questions are present"
    ]
  },
  "review_rubric": {
    "self_review_required": true,
    "ready_to_build": [
      "Is this lug mature enough to build without filling architectural gaps from chat?",
      "Are sequence, non-goals, and dependencies explicit?",
      "Are target files or target objects named?",
      "Is verification concrete rather than aspirational?"
    ],
    "acceptance_checks": [
      {
        "id": "scope",
        "question": "Did the implementation stay within the lug's scope and non-goals?",
        "pass_condition": "No unauthorized file or architecture expansion occurred",
        "failure_action": "Move to in_remediation and add review note"
      },
      {
        "id": "canonical_alignment",
        "question": "Do the changes align with the goal-state design and parent epic?",
        "pass_condition": "No contradiction with the canonical object model or behavior remains in touched files",
        "failure_action": "Move to in_remediation and add review note"
      },
      {
        "id": "persistence",
        "question": "Was review, progress, and completion written back to the lug?",
        "pass_condition": "The implementation lug and session-summary reflect the real work performed",
        "failure_action": "Treat work as incomplete until persisted"
      },
      {
        "id": "verification",
        "question": "Was actual verification performed and recorded?",
        "pass_condition": "Claims are backed by concrete checks, not just assertions",
        "failure_action": "Require remediation or downgrade completion claim"
      },
      {
        "id": "handoff_quality",
        "question": "Could a new agent continue from the lug alone?",
        "pass_condition": "Next steps, blockers, observations, and remaining work are durable",
        "failure_action": "Require lug update before acceptance"
      }
    ]
  },
  "remediation_plan": {
    "required_when_in_remediation": true,
    "version": 1,
    "authored_at": "ISO-8601",
    "authored_by": "agent-name",
    "model": "model-id",
    "addresses_note_ids": ["rn-001-example"],
    "problem_summary": "Why the prior attempt failed or was kicked back.",
    "planned_changes": [
      "What will be changed to address the review note",
      "What will remain out of scope during remediation"
    ],
    "verification_plan": [
      "How the remediation will be checked",
      "What evidence will be gathered before recheck"
    ],
    "risks": [
      "Known uncertainty, dependency, or likely follow-up"
    ],
    "needs_user_review": false
  },
  "workflow": {
    "current_phase": "plan|work|verify|accept",
    "current_owner": "planner|builder|validator|user",
    "current_state": "open|in_progress|complete",
    "handoff_reason": "Why the ball moved to this owner",
    "next_expected_transition": "What should happen next",
    "steps": {
      "plan": {
        "type": "plan",
        "owner": "planner",
        "state": "open|in_progress|complete"
      },
      "work": {
        "type": "work",
        "owner": "builder",
        "state": "open|in_progress|complete"
      },
      "verify": {
        "type": "verify",
        "owner": "validator",
        "state": "open|in_progress|complete"
      },
      "accept": {
        "type": "accept",
        "owner": "user",
        "state": "open|in_progress|complete"
      }
    }
  },
  "review_notes": [
    {
      "id": "rn-001-example",
      "at": "2026-03-19T09:05:00Z", 
      "by": "agent-name",
      "model": "claude-sonnet-4-20250514",
      "type": "concern|gap|suggestion|acceptance-note|blocked",
      "scope": "signals|tracks|state|verification|etc",
      "message": "Detailed description of issue",
      "file_refs": ["path/to/file.md:123", "other/file.md:456"],
      "status": "open|acknowledged|resolved|rejected",
      "resolution_note": "How this was addressed"
    }
  ],
  "review_cycles": [
    {
      "cycle": 1,
      "reviewed_at": "2026-03-19T09:05:00Z",
      "reviewed_by": "agent-name", 
      "model": "claude-sonnet-4-20250514",
      "result": "approved|needs_remediation|accepted",
      "summary": "Brief review outcome description",
      "blocking_note_ids": ["rn-001-example"],
      "non_blocking_note_ids": []
    }
  ],
  "acceptance": {
    "status": "pending|ready_for_acceptance|accepted",
    "accepted_at": null,
    "accepted_by": null,
    "model": null,
    "notes": "Final acceptance notes"
  }
}
```

**Review Gate Rules:**
1. **Pre-Implementation Review**: Before any implementation, create review cycle documenting approval/concerns
2. **Persistent Review Notes**: All review findings must be recorded as `review_notes[]`, not just in chat
3. **Remediation Tracking**: If review finds gaps, status moves to `in_remediation` with blocking note IDs
4. **Recheck Required**: After fixes, implementer moves to `ready_for_recheck`, reviewer confirms resolution
5. **Final Acceptance**: Only after all review notes are resolved can status move to `accepted`
6. **Lug-Centered Interaction**: For non-trivial implementation work, reviewer/implementer back-and-forth should be written to the lug itself whenever possible; chat should mainly tell an agent which lug to load and what state to inspect
7. **Ready-To-Build Gate**: Before implementation starts, the implementer must explicitly check and record that the lug is ready to build using the `ready_to_build_gate` and `review_rubric.ready_to_build` criteria
8. **Self-Grading Requirement**: Before requesting recheck, the implementer must run the `review_rubric.acceptance_checks` against its own work and persist the result on the lug
9. **Remediation Plan Requirement**: If a quality review kicks the lug back to `in_remediation`, the builder must write a `remediation_plan` to the same lug before retrying. The plan should state what failed, what will change, how it will be verified, and whether any user review is needed before reimplementation.
10. **Workflow Action Tracker**: Update `workflow.current_phase`, `workflow.current_owner`, and `workflow.current_state` at major handoffs so future agents can instantly see who has the ball and what phase is active without parsing the full audit trail.

**Persistence Gate Rule:** Review is not complete until it is written back to the `implementation` lug. Before editing any target file, the implementer must update the lug with review cycle entry, any review notes, and the intended next step. If review only exists in chat, it is incomplete.

**Completion gate rule:** Implementation is not complete until the same lug is updated with what changed, verification actually performed, contributors/sub-agents used, completion notes, observations, and follow-up candidates, and a session-summary lug is appended.

**Remediation planning rule:** When a lug is in `in_remediation`, do not silently retry. First persist a `remediation_plan` that addresses the open review note IDs. If the remediation materially changes scope or architecture, set `needs_user_review: true` and return to the user before implementing.

**Workflow handoff rule:** At major transitions (plan complete, implementation complete, verification complete, acceptance recorded), update the `workflow` action tracker so the lug shows exactly who has the ball. This helps continuation agents identify their role without reading the full history.

**Sub-agent rule:** Sub-agents may help with bounded analysis, comparison, or verification, but they do not replace the primary implementer's judgment on architecture, scope, or final reconciliation unless the lug explicitly allows it.

**Storage note:** `implementation` lugs improve traceability for complex work, but they do not solve scaling limits of a single large JSONL file. If JSONL maintenance friction rises, treat that as a separate architecture problem to address rather than skipping durable planning records.

---

## Dogfooding Lugs (Required Before Closeout)

**Before finalizing any lug intended for another agent (including future-you), validate it:**

1. **State what you'll test** — which lug(s), what aspects
2. **State how deep** — schema check, self-containment review, sub-agent simulation
## Lug Lifecycle

```
CREATE → DOGFOOD → DISCUSS → IMPLEMENT → VERIFY → CELEBRATE → ARCHIVE
```

1. **CREATE** — Append new lug to `WAI-Lugs.jsonl` with `s: "o"`. Ensure PEV fields are present.
2. **DOGFOOD** — Run the naive agent test. Fix gaps before work begins.
3. **DISCUSS** — (Optional) For high-impact lugs (impact >= 8), present the implementation strategy to the user. Refine based on feedback.
4. **IMPLEMENT** — Set `s: "p"`. Follow the `execute` steps in the lug. If reality diverges from the lug's plan, update the lug first.
5. **VERIFY** — Execute every step in the `verify` field. Run regression tests. Ensure no `TODO` or `FIXME` comments remain in the code.
6. **CELEBRATE** — Present the **Victory Briefing** (see below). Set `s: "c"`.
7. **ARCHIVE** — Closed lugs remain in `WAI-Lugs.jsonl` for history. Reconcile in session-summary at closeout.

---

## Dogfooding Lugs (Naive Agent Test)

**Before finalizing any lug intended for another agent (including future-you), validate it:**

1. **State what you'll test** — which lug(s), what aspects.
2. **Invoke the Naive Agent Test** — Send the lug's `perceive`, `execute`, and `verify` fields to a sub-agent (e.g., `planning-agent` or `generalist`) with **zero project context**. 
3. **Analyze the Plan** — Ask the sub-agent to draft an implementation plan based *only* on the lug.
4. **Identify "STUCK" Points** — Anywhere the sub-agent needs clarification or makes an assumption is a gap in the lug.
5. **Fix Gaps** — Update the lug with missing file paths, specific line numbers, or clearer logic until a naive agent can draft a perfect plan.

**The Golden Rule:** A lug is only `dogfood_pass: true` when a "cold" agent can implement it correctly without asking a single question.

---

## Implementation & Verification Protocol

When implementing a lug:
- **Set Focus:** Declare the lug ID you are working on.
- **Follow PEV:** Do not improvise. If the `execute` steps are wrong, backtrack to the "Discuss" phase and update the lug.
- **Surgical Edits:** Keep changes focused on the lug's goals. Avoid unrelated refactoring.
- **Mandatory Verification:** You MUST run the commands specified in the `verify` field. If no commands are specified, you must invent and run a test case that proves behavioral correctness.

---

## The Victory Briefing (Announcing Completion)

After a lug or epic is implemented and verified, present a celebratory briefing to the user. This "shares the win" and provides a human-readable record of the accomplishment.

### **Briefing Format:**

1. **Header:** `### 🎉 EPIC WIN: {Title}` or `### 🎉 LUG CLOSED: {Title}`
2. **The Human Why:** 1-2 concise paragraphs explaining what was built and *why it matters* for the project or the user. Focus on value, not just code.
3. **The Stats:**
   - **Complexity:** [Low | Medium | High] (How much cognitive load/risk?)
   - **Impact:** [1-10] (How much did this move the needle?)
   - **Files Touched:** [Count]
   - **Verification:** [Brief summary of tests passed]
4. **The "Check it Out":** A specific command or file the user can look at to see the result.

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
| `signal` | Share insight (impact >= 8) | NO — record in WAI-Lugs.jsonl | "Found useful pattern" → logged as lug |
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
- `/wai (Step 3a: auto-discovery)` — Processes incoming lugs from inbox
- `/wai (Step 9b: auto-teach on closeout)` — Delivers outbox lugs to target nodes

---

*Lugs = Persistent memory. CLARITY > BREVITY for cross-spoke communication.*

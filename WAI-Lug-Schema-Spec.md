# WAI Lug Schema Specification

**Version:** 1.1.0
**Date:** 2026-02-11
**Status:** Foundation Spec — Architectural North Star
**Revision:** Added PEV fields, outbound monitoring, migration YAML pattern, upgrade tracking

---

## Philosophy

Lugs are WAI's universal communication primitive. They are **actionable records** — not summaries, not notes, not chat logs. Every Lug represents decomposed, meaningful work with full traceability.

Lugs serve as shared memory across agent colonies. They are how agents show their work, communicate across nodes, and build institutional history. If an agent didn't write a Lug, it didn't happen.

**Core Principles:**

- **Actionable:** Every Lug has a clear "what needs to happen" or "what happened"
- **Traceable:** Every Lug links to its origin — parent Lugs, source Lugs from other nodes, git commits
- **Idempotent:** Running the same analysis twice produces the same Lug (or finds and updates the existing one)
- **Decomposed:** Lugs are broken down to meaningful units — one concern per Lug
- **Self-contained:** A Lug carries enough context to be understood without reading the full history

---

## Lug Types

| Type | Purpose | Example |
|------|---------|---------|
| `task` | Work to be done | "Migrate auth from JWT to sessions" |
| `diagnosis` | Problem identified by a sub-agent | "SQL injection in auth handler" |
| `prescription` | Recommended fix attached to a diagnosis | "Parameterize query at line 47" |
| `decision` | A judgment call made by the conductor | "Accepted risk on X because Y" |
| `observation` | Event or pattern worth recording | "Test coverage dropped from 82% to 73%" |
| `signal` | High-impact Lug (impact ≥ 8) relevant to other nodes | "Architecture change affects API contract" |
| `update` | Framework or template version change notification | "Template v3 available, running v2" |
| `session` | Session synthesis — human-readable summary of a work session | "Security review ran, 2 issues found, 1 resolved" |

**Note:** Signals are not a separate system. A signal is any Lug with `impact >= 8`. The type field describes what kind of information it carries. Impact determines who sees it.

---

## Schema

### Required Fields

```yaml
id: "lug-2026-02-11-001"          # Unique identifier: lug-{date}-{sequence}
type: "diagnosis"                  # One of: task, diagnosis, prescription, decision, 
                                   #   observation, signal, update, session
title: "SQL injection in auth handler"
status: "published"                # Lifecycle state (see Lifecycle section)
impact: 9                          # 1-10 scale. ≥8 = signal (visible to other nodes)
created_at: "2026-02-11T14:30:00Z"
created_by: "security-reviewer"    # Agent/skill that created this Lug
node: "ownersshare/cto"            # Node path where this Lug lives
```

### Traceability Fields

```yaml
# Git linkage — which commit(s) resulted from this Lug
repo_version: "a3f7b2c"           # Commit hash where this work landed
branch: "main"                     # Branch name
changelog_note: "Fixed SQL injection in auth handler per Lug SEC-047"

# Lug lineage — where did this Lug come from
parent_id: "lug-2026-02-10-015"   # Parent Lug if decomposed from a larger item
source_id: "hub:lug-2026-02-09-003"  # External Lug ID if inherited from another node
source_node: "hub"                 # Which node the source Lug lives in
source_acknowledged: true          # Has the source node been notified this was processed

# Decision tracing (for type: decision)
alternatives_considered:
  - option: "Migrate to sessions"
    chosen: true
    reasoning: "Simpler state management, no token expiry issues"
  - option: "Keep JWT with refresh tokens"
    chosen: false
    reasoning: "Added complexity, still has edge cases"
```

### Diagnosis & Prescription Fields

```yaml
# For type: diagnosis
severity: "critical"               # critical | high | medium | low
category: "security"               # Domain: security, quality, performance, compliance, etc.
evidence: "Line 47 of auth.js uses string concatenation in SQL query"
affected_files:
  - "src/auth/handler.js"

# For type: prescription (always linked to a diagnosis)
diagnosis_id: "lug-2026-02-11-001"
prescription: "Replace string concatenation with parameterized query using pg.query($1)"
estimated_effort: "15 minutes"
auto_applicable: false             # Can a main agent apply this without human review?
```

### Calibration Fields

```yaml
# Applied when a Lug is resolved — feeds learning loops
resolution: "accepted"             # accepted | deferred | dismissed | modified
resolution_reason: "Applied as prescribed"  # One-line explanation
resolved_at: "2026-02-11T15:00:00Z"
resolved_by: "main-agent"
```

### PEV Fields (Perceive / Execute / Verify)

Optional structured execution context. When present, the agent follows these instructions instead of interpreting the title. Simple Lugs don't need PEV. Complex Lugs where precision matters should carry it.

```yaml
# Perceive — what to look at and what "wrong" looks like
perceive:
  look_at:
    - "src/auth/handler.js"
    - "tests/auth/handler.test.js"
  current_state: "Email field accepts any string, no validation"
  success_state: "Email field validates against RFC 5322"
  context: "Phone validator in src/validators/phone.ts uses same pattern"

# Execute — what actions to take and constraints
execute:
  approach: "Add email validation using the pattern in phone.ts validator"
  constraints:
    - "Do not modify the existing phone validator"
    - "Follow project convention for error messages"
  avoid:
    - "Do not use regex-only validation — use the validator library"
  reference_patterns:
    - "src/validators/phone.ts"

# Verify — how to confirm success
verify:
  commands:
    - "npm test -- --grep 'email validation'"
    - "npm run lint"
  expected_output: "All tests pass, no lint errors"
  manual_check: "Try submitting form with invalid email — should show error"
```

**PEV is optional and backward compatible.** Existing Lugs without PEV fields continue to work — agents fall back to title + description interpretation. PEV is an upgrade path, not a migration requirement. Over time, agents learn which Lugs benefit from PEV and can suggest adding it.

### Outbound Monitoring Fields

```yaml
# For tracking cross-node signal delivery (spoke → Hub)
outbound_submitted_to: "hub/intake"
outbound_submitted_at: "2026-02-11T15:00:00Z"
outbound_acknowledged: false        # Flips to true when Hub processes it
outbound_acknowledged_at: null
```

When a spoke creates a high-impact Lug and submits it to Hub intake, these fields track whether the Hub has processed it. On next spoke wakeup, the hub-watcher Skill checks: is this still pending? If so, surface to the user that Hub needs attention.

```yaml
# For session log synthesis
skill_name: "security-review"
model_tier: "lightweight"          # lightweight | standard | advanced
execution_duration_ms: 4200
execution_status: "success"        # success | failure | partial
execution_summary: "Scanned 23 files, found 2 vulnerabilities (1 critical, 1 low)"
```

### Session Synthesis Fields

```yaml
# For type: session — human-readable session summary
session_id: "session-2026-02-11-001"
session_start: "2026-02-11T14:00:00Z"
session_end: "2026-02-11T16:30:00Z"
skills_executed:
  - skill: "security-review"
    status: "success"
    findings: 2
  - skill: "qc-check"
    status: "success"
    findings: 0
lugs_created: 3
lugs_resolved: 2
commits:
  - hash: "a3f7b2c"
    message: "Fix SQL injection in auth handler"
  - hash: "b4e8f1a"
    message: "Add parameterized query tests"
summary: >
  Security reviewer ran, found 2 issues (1 critical, 1 low).
  QC ran, all tests passing. Main agent resolved the critical issue.
  Framework update Lug created for next session.
```

---

## Lifecycle

```
draft → published → acknowledged → in_progress → resolved
                                                     ↓
                                                  (calibration applied)
```

| State | Meaning |
|-------|---------|
| `draft` | Created but not yet ready for action |
| `published` | Active and visible to relevant agents |
| `acknowledged` | Another node has seen this (for signals/cross-node Lugs) |
| `in_progress` | Work has started on this Lug |
| `resolved` | Completed — resolution and calibration fields populated |

**Special cases:**

- A Lug can move from `resolved` back to `published` if a regression is detected (new Lug referencing the original)
- Sub-agent Lugs (diagnosis, prescription) are created as `published` — they don't need drafts
- Session Lugs are created as `resolved` — they're retrospective records

---

## Impact Scoring

Impact determines visibility radius:

| Score | Visibility | Example |
|-------|-----------|---------|
| 1-3 | Local only — visible within the creating node | "Refactored helper function" |
| 4-7 | Project-wide — visible to other extensions in the same project | "API contract changed" |
| 8-10 | Wheel-wide signal — copied to Hub intake | "Architecture pattern applicable across projects" |

**Impact assessment heuristics for agents:**

- Does this affect other extensions in this project? → 4+
- Does this affect other projects? → 8+
- Does this change a shared interface or contract? → 7+
- Is this a framework-level learning? → 9+
- Is this a policy or security concern? → 8+

---

## Idempotency Rules

1. Before creating a Lug, check if an equivalent Lug already exists (same type, same title pattern, same affected scope)
2. If found and still open: update the existing Lug (bump priority if recurring)
3. If found and resolved: create a new Lug referencing the original as a regression
4. Lug ID is the idempotency key for cross-node references
5. Sub-agents running the same check twice should produce the same findings unless the codebase changed

---

## Cross-Node Communication Protocol

### Outbound (Spoke → Hub)

When a spoke creates a Lug with `impact >= 8`:

1. Write the Lug to local `WAI-Lugs.jsonl`
2. Copy the Lug to `hub/intake/{node-path}/{lug-id}.yaml`
3. Record in local manifest: `outbound_pending: [{id, submitted_at}]`
4. On next spoke load: check if Hub has processed the intake item
5. If still pending after threshold: surface to user "Hub has unprocessed signals"

### Inbound (Hub → Spoke)

When a spoke wakes up:

1. Read `hub/WAI-Lugs.jsonl` — filter for Lugs newer than spoke's `hub_lug_cursor`
2. For each relevant Lug (matching spoke's subscription scope):
   - Create a local Lug with `source_id` pointing to Hub Lug
   - Decompose into actionable local work
   - Update spoke manifest `hub_lug_cursor`
3. Mark Hub Lug as acknowledged by this spoke

### Hub Processing

When Hub wakes up:

1. Read all items in `hub/intake/`
2. Evaluate each: wheel-wide pattern? policy-relevant? framework feedback?
3. Create Hub-level Lugs as appropriate
4. Move processed intake items to `hub/intake/processed/`
5. Aggregate patterns across spokes into observation Lugs

---

## Decision Records

Decision Lugs are the apprenticeship engine. They capture not just what was decided but the reasoning and alternatives, allowing the system to learn the conductor's judgment.

**When to create a decision Lug:**

- Conductor overrides a sub-agent recommendation
- Conductor chooses between competing prescriptions
- Conductor defers or dismisses a diagnosis with reasoning
- Conductor makes a strategic choice that affects project direction

**Learning from decisions:**

Sub-agents should reference past decision Lugs when making future recommendations:

> "Flagging potential SQL injection in payment handler. Note: similar finding in auth handler (Lug SEC-047) was accepted and fixed. Same reasoning likely applies here."

Over time, the decision history teaches sub-agents the conductor's risk tolerance, quality standards, and priorities — not by being programmed but by observing patterns.

---

## Storage Format

Lugs are stored in `WAI-Lugs.jsonl` — one JSON object per line. This format supports:

- Append-only writes (no file corruption from concurrent access)
- Line-by-line streaming reads
- Simple grep/filter operations
- Git-friendly diffs

```jsonl
{"id":"lug-2026-02-11-001","type":"diagnosis","title":"SQL injection in auth handler","status":"published","impact":9,"created_at":"2026-02-11T14:30:00Z","created_by":"security-reviewer","node":"ownersshare/cto","severity":"critical","category":"security"}
{"id":"lug-2026-02-11-002","type":"prescription","title":"Parameterize auth query","status":"published","impact":9,"created_at":"2026-02-11T14:30:05Z","created_by":"security-reviewer","node":"ownersshare/cto","diagnosis_id":"lug-2026-02-11-001","prescription":"Replace string concatenation with pg.query($1)"}
```

---

## BRIEF Integrity Checking

A Hub-level or spoke-level Skill that compares Lug patterns against BRIEF policies:

- BRIEF states "maintain 80% test coverage" but 3 QC Lugs about declining coverage were dismissed → surface contradiction
- BRIEF states "security findings resolved within 48 hours" but critical diagnosis Lug is 72 hours old → surface alert
- BRIEF states "no direct database queries in API handlers" but diagnosis Lug found one → confirm policy still holds

This is not enforcement — it's awareness. The conductor decides whether to update the policy or address the violation.

---

## Migration & Upgrade Tracking

Lugs serve as the permanent record for migrations and upgrades. The pattern:

1. A `WAI-MIGRATION.yaml` or `WAI-UPGRADE.yaml` file tracks migration/upgrade state during execution
2. Each phase closeout updates the YAML with commit hash and timestamp
3. On completion, the YAML is converted into a decision Lug capturing the full migration record
4. The YAML file is deleted — the Lug IS the permanent record

This pattern applies at every scale: framework-wide migrations (v1→v2), node-level template upgrades (template v2→v3), and Skill version updates.

---

## Session Ledger (WAI-Ledger.jsonl)

The session ledger is an append-only log of what was requested, what was agreed to, and what was delivered. It lives per-node alongside WAI-Lugs.jsonl. Each entry records a commitment and its resolution.

**Origin:** During WAI v2 migration, token exhaustion and a crash caused context loss. The executing agent reconstructed intent from partial memory, renamed core concepts (PEV → perspective/evidence/verdict), skipped two phases, and declared migration complete. There was no mechanism to detect drift because commitments lived only in conversation context, not in files.

The session ledger ensures commitments survive any context loss. On session resume, the agent reads the ledger and verifies: "Was this commitment fulfilled?"

### Ledger Entry Types

| Type | Who Creates | Meaning |
|------|-------------|---------|
| `request` | conductor | "I want this done" |
| `agreement` | agent | "I will do this, here's how" |
| `clarification` | either | "Do you mean X or Y?" / "I mean X" |
| `amendment` | either | "Actually, let's change the approach" |
| `delivery` | agent | "This is done" — links to commit hash |
| `verification` | conductor | "Confirmed" or "Doesn't match agreement" |
| `rejection` | conductor | "Doesn't fulfill the agreement, because..." |

### Ledger Entry Schema

```jsonl
{"id":"led-2026-02-12-001","timestamp":"2026-02-12T14:00:00Z","session_id":"session-001","type":"request","content":"Migrate Lug schema to v2 with PEV fields","source":"conductor","status":"open"}
{"id":"led-2026-02-12-002","timestamp":"2026-02-12T14:05:00Z","session_id":"session-001","type":"agreement","content":"Will add perceive/execute/verify as optional fields","source":"agent","references":"led-2026-02-12-001","status":"open"}
{"id":"led-2026-02-12-003","timestamp":"2026-02-12T15:00:00Z","session_id":"session-001","type":"delivery","content":"350 Lugs upgraded, PEV fields added","source":"agent","references":"led-2026-02-12-001","commit":"73112e9","status":"fulfilled"}
```

### Ledger Entry Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Unique: led-{date}-{seq} |
| timestamp | datetime | yes | ISO 8601 |
| session_id | string | yes | Which session |
| type | enum | yes | request, agreement, clarification, amendment, delivery, verification, rejection |
| content | string | yes | Plain language description |
| source | enum | yes | "conductor" or "agent" |
| references | string | no | ID of entry this responds to |
| commit | string | no | Git commit hash (for deliveries) |
| status | enum | yes | open, fulfilled, amended, rejected |
| lug_ids | array | no | Lugs created to fulfill this |

### Lifecycle

```
request (conductor) → agreement (agent) → delivery (agent) → verification (conductor)
                   ↗                    ↗
          clarification              amendment
```

- Requests start as `open`
- When agent delivers with matching commit, status flips to `fulfilled`
- Conductor can verify (confirmed) or reject (back to open with rejection entry)
- Amendments create new agreement entries, superseding previous

### Integration

- **Wakeup:** Read ledger, surface open commitments in composite briefing
- **Closeout:** session-observer reconciles — flags unfulfilled commitments
- **Resume:** New agent reads ledger, compares commitments against codebase state
- **Integrity:** WAI-Ledger.jsonl is append-only (declared in WAI-Integrity.md)

### Storage

Same as WAI-Lugs.jsonl: JSONL format, one entry per line, append-only, git-tracked.

**Example migration Lug:**

```yaml
id: "lug-v2-migration-001"
type: "decision"
title: "WAI v2 migration completed"
status: "resolved"
impact: 10
created_by: "conductor"
node: "hub"
resolution: "accepted"
repo_version: "v2.0.0 tag hash"
alternatives_considered:
  - option: "CLI-based management"
    chosen: false
    reasoning: "CLI destroyed Hub folder; no data protection"
  - option: "File-based protocol with Skills and Lugs"
    chosen: true
    reasoning: "Agents communicate through files, show work via Lugs"
summary: "Migrated v1→v2. Signals absorbed into Lugs. Backpressure became Skills."
```

---

## Appendix: Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Unique identifier |
| type | enum | yes | task, diagnosis, prescription, decision, observation, signal, update, session |
| title | string | yes | Human-readable one-line description |
| status | enum | yes | draft, published, acknowledged, in_progress, resolved |
| impact | integer | yes | 1-10 visibility score |
| created_at | datetime | yes | ISO 8601 timestamp |
| created_by | string | yes | Agent or skill identifier |
| node | string | yes | Node path (project/extension) |
| repo_version | string | no | Git commit hash |
| branch | string | no | Git branch |
| changelog_note | string | no | Human-readable change description for git log |
| parent_id | string | no | Parent Lug if decomposed |
| source_id | string | no | External Lug ID from another node |
| source_node | string | no | Origin node for external Lugs |
| source_acknowledged | boolean | no | Whether source node knows this was processed |
| severity | enum | no | critical, high, medium, low (for diagnoses) |
| category | string | no | Domain category |
| evidence | string | no | Supporting evidence |
| affected_files | array | no | Files involved |
| diagnosis_id | string | no | Linked diagnosis (for prescriptions) |
| prescription | string | no | Recommended action text |
| estimated_effort | string | no | Time estimate |
| auto_applicable | boolean | no | Can be applied without human review |
| resolution | enum | no | accepted, deferred, dismissed, modified |
| resolution_reason | string | no | One-line explanation |
| resolved_at | datetime | no | When resolved |
| resolved_by | string | no | Who resolved |
| alternatives_considered | array | no | Decision alternatives (for decisions) |
| skill_name | string | no | Skill that generated this Lug |
| model_tier | enum | no | lightweight, standard, advanced |
| execution_duration_ms | integer | no | How long the skill ran |
| execution_status | enum | no | success, failure, partial |
| execution_summary | string | no | Brief skill execution summary |
| session_id | string | no | Session identifier |
| session_start | datetime | no | Session start time |
| session_end | datetime | no | Session end time |
| skills_executed | array | no | Skills that ran during session |
| lugs_created | integer | no | Count of Lugs created in session |
| lugs_resolved | integer | no | Count of Lugs resolved in session |
| commits | array | no | Git commits made during session |
| summary | string | no | Human-readable session narrative |
| perceive | object | no | PEV: what to look at, current/success state, context |
| execute | object | no | PEV: approach, constraints, avoid, reference patterns |
| verify | object | no | PEV: commands to run, expected output, manual checks |
| outbound_submitted_to | string | no | Where this Lug was submitted (e.g., hub/intake) |
| outbound_submitted_at | datetime | no | When submitted to intake |
| outbound_acknowledged | boolean | no | Whether the receiving node processed it |
| outbound_acknowledged_at | datetime | no | When acknowledged |

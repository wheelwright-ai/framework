# Wheelwright AI Framework - Complete Documentation
# Generated: 2026-04-17T08:11:40Z
# Version: 2.0.180

This file contains the complete Wheelwright documentation including:
- Framework guides and setup instructions
- Lug Schema Specification (complete field reference)
- Skill Contract Specification (how to build skills)
- Hub policies and communication protocols
- Built-in skills documentation
- E2E benchmark validation details
- Use cases and real-world examples

---

# Lug Schema Specification (Complete)
Source: WAI-Lug-Schema-Spec.md

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
| `preference` | Communication style or workflow preference | "User prefers terse confirmations over verbose status reports" |
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
                                   #   observation, preference, signal, update, session
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

### Preference Fields

```yaml
# For type: preference — communication style and workflow preferences
category: "communication"          # communication | workflow | tooling
observation: "User prefers terse confirmations over verbose status reports"
context: "After seeing three different verification formats, requested homogenization"
guidance: "Keep verification responses to numbered list format, <10 lines total"
applies_to: "all"                  # all | hub | spoke | specific node path
```

**Purpose:** Preference Lugs capture the conductor's communication style, workflow preferences, and interaction patterns. They feed the apprenticeship loop by teaching agents how the user wants to work, not just what work they want done.

**When to create preference Lugs:**
- User gives feedback on response format or tone ("too verbose", "I just need bullets")
- User corrects interaction patterns ("don't ask permission, just do it")
- User establishes workflow preferences ("always run tests before committing")
- User defines style boundaries ("never use emojis in technical docs")

**Integration with hub/BRIEF.md:**
- Preference Lugs are created in the moment when feedback is given
- Periodically (via /wai-teach), preference Lugs are reviewed and consolidated
- Common patterns get promoted into hub/BRIEF.md Communication Style section
- Once codified in BRIEF, the original Lugs can be marked resolved

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
| type | enum | yes | task, diagnosis, prescription, decision, observation, preference, signal, update, session |
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
| adoption_status | enum | no | Teaching adoption decision: pending_review, adopted, deferred, rejected |
| adoption_action | string | no | What was done when the teaching was processed |
| adoption_reviewed_at | string | no | ISO 8601 timestamp of adoption review |
| alternatives_considered | array | no | Decision alternatives (for decisions) |
| observation | string | no | What preference pattern was observed (for preferences) |
| context | string | no | Situation where preference was expressed (for preferences) |
| guidance | string | no | How to apply this preference (for preferences) |
| applies_to | string | no | Scope: all, hub, spoke, or node path (for preferences) |
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


---

# Skill Contract Specification (Complete)
Source: WAI-Skill-Contract-Spec.md

# WAI Skill Contract Specification

**Version:** 1.1.0
**Date:** 2026-02-11
**Status:** Foundation Spec — Architectural North Star
**Revision:** Added use_cases requirement, integration-check Skill, migration YAML pattern for upgrades

---

## Philosophy

Skills are WAI's universal behavior primitive. They are **executable capabilities** — not documentation, not suggestions, not prompts. A Skill declares what it does, when it fires, what model it needs, what it's allowed to touch, and what it produces.

Skills are the agents in the agent colony. Each Skill is a sub-agent with a defined scope, a cost profile, and an output contract. The main coding agent is itself just a Skill — the most expensive one, with the broadest write access.

**Core Principles:**

- **Declarative:** A Skill describes its contract; the runtime decides when and how to execute it
- **Scoped:** Every Skill declares exactly what it reads and what it writes — nothing else
- **Testable:** Every Skill can include its own test suite to verify correct behavior
- **Composable:** Skills can depend on other Skills and chain outputs
- **Inheritable:** Framework defines base Skills → Hub refines → Spoke overrides

---

## Skill Types

| Type | Purpose | Model Tier | Write Access |
|------|---------|------------|--------------|
| `reviewer` | Analyzes code/content, produces diagnosis Lugs | lightweight | Lugs only |
| `watcher` | Monitors state changes, produces observation Lugs | lightweight | Lugs only |
| `guardian` | Enforces policies, blocks unsafe actions | standard | Lugs + can block operations |
| `worker` | Executes implementation tasks | advanced | Code + Lugs |
| `advisor` | Evaluates BRIEF alignment, suggests amendments | standard | Lugs only |
| `orchestrator` | Reconciles sub-agent output, builds plans | advanced | Lugs + plans |

**Key distinction:** Reviewers, watchers, and advisors are cheap read-mostly agents. Workers and orchestrators are expensive write-capable agents. Guardians sit in between — they read broadly and can veto.

---

## Skill Contract Schema

### Identity

```yaml
skill: security-review
version: 1.2.0
type: reviewer
description: >
  Scans codebase for OWASP Top 10 vulnerabilities, 
  dependency version risks, and hardcoded credentials.
  Produces diagnosis and prescription Lugs.
```

### Model Requirements

```yaml
model:
  tier: lightweight                # lightweight | standard | advanced
  min_context: 32000               # Minimum context window needed (tokens)
  capabilities:                    # Required model capabilities
    - code_analysis
  notes: >
    Lightweight model sufficient for pattern matching against known 
    vulnerability signatures. Does not need advanced reasoning.
```

**Model tier guidance:**

| Tier | Use For | Example Models |
|------|---------|---------------|
| `lightweight` | Pattern matching, checklist verification, simple analysis | Haiku-class |
| `standard` | Nuanced evaluation, multi-factor analysis, policy interpretation | Sonnet-class |
| `advanced` | Complex reasoning, plan reconciliation, implementation, judgment calls | Opus-class |

**Multi-model diversification benefit:** Running different Skills at different model tiers provides implicit ensemble validation. Different architectures catch different blind spots. The orchestrator (advanced tier) reconciles potentially contradictory findings, producing higher-confidence outcomes than any single model.

### Trigger Configuration

```yaml
trigger:
  event: on_load                   # When this Skill fires
  frequency: per_session           # How often within a session
  priority: 2                      # Execution order (1 = first)
  conditions:                      # Optional conditions to evaluate before firing
    - "files_changed: src/**"
    - "last_run_age: > 24h"
  can_be_skipped: false            # Whether the user/BRIEF can disable this
```

**Trigger events:**

| Event | When It Fires |
|-------|--------------|
| `on_load` | Spoke/Hub wakeup sequence |
| `on_commit` | After a git commit |
| `on_content_change` | After source files are modified |
| `on_lug_created` | When a new Lug appears (filtered by type/impact) |
| `on_schedule` | Time-based (daily, weekly) — checked on load |
| `on_demand` | Only when explicitly requested by conductor or another Skill |
| `pre_refactor` | Before any structural file changes |

**Frequency options:**

| Frequency | Meaning |
|-----------|---------|
| `per_session` | Once per session load |
| `per_change` | Every qualifying trigger event |
| `periodic` | Based on time elapsed since last run (uses `last_run_age` condition) |
| `once` | Run once, then mark complete |

### Scope & Permissions

```yaml
scope:
  reads:
    - "src/**"                     # Can read source code
    - "tests/**"                   # Can read test files
    - "WAI-Lugs.jsonl"             # Can read current Lugs
    - "hub/WAI-Lugs.jsonl"         # Can read Hub Lugs (read-only)
    - "BRIEF.md"                   # Can read current BRIEF
  writes:
    - "WAI-Lugs.jsonl"             # Can write Lugs
  never:
    - "src/**"                     # CANNOT modify source code
    - ".env*"                      # CANNOT access environment files
    - "hub/**"                     # CANNOT write to Hub (except via intake)
  intake_access: true              # Can write to hub/intake/
```

**Scope rules:**

1. A Skill MUST declare everything it reads and writes
2. `never` overrides `writes` — explicit denial takes precedence
3. Reviewer and watcher types can only write to `WAI-Lugs.jsonl` and `hub/intake/`
4. Only `worker` type Skills can write to source code
5. `guardian` type Skills can write to Lugs AND set blocking flags
6. If a Skill attempts to write outside its declared scope, the action is logged as a violation Lug

### Prerequisites

```yaml
prerequisites:
  tools:
    - name: "git"
      check: "git --version"
      required: true
    - name: "npm"
      check: "npm --version"
      required: false
  skills:
    - "safe-refactor"              # This Skill depends on safe-refactor being available
  files:
    - "package.json"               # Project must have this file
  state:
    - "git_clean: true"            # Working directory must be clean
```

**Prerequisite checking:**

On load, each Skill's prerequisites are verified. Status is reported:

> "4 Skills loaded. 3 ready. `deploy` blocked: missing AWS credentials."

If a prerequisite is `required: true` and missing, the Skill is marked `blocked` and a Lug is created explaining what's needed. If `required: false`, the Skill runs with reduced capability.

### Output Contract

```yaml
outputs:
  lugs:
    types:
      - "diagnosis"
      - "prescription"
    impact_range: [5, 10]          # Expected impact range for Lugs this Skill creates
  session_log:
    required: true                 # Must write execution summary to session log
    fields:
      - execution_status
      - execution_duration_ms
      - execution_summary
      - findings_count
```

**Output contract enforcement:**

Every Skill execution must produce:
1. At minimum: a session log entry recording that it ran, how long, success/failure, brief summary
2. If findings exist: properly formed Lugs with all required fields
3. If no findings: a session log entry confirming clean check

This ensures the audit trail is complete. No Skill runs silently.

### Inheritance & Override

```yaml
inheritance:
  base: "framework://skills/security-review@1.0.0"    # Framework template
  hub_overlay: "hub://skills/security-review-policy"    # Hub-level additions
  local_overrides:
    - "Also check for PII exposure in API responses"    # Spoke-specific additions
    - "Ignore false positives in test fixtures"
  locked_by: "enterprise"          # Who can modify: enterprise | hub | spoke | none
```

**Inheritance cascade:**

```
Framework template (base behavior, default rules)
  ↓ Hub overlay adds (wheel-wide policies, additional checks)
    ↓ Spoke override refines (project-specific context, local exceptions)
```

**Rules:**

- Each level can ADD checks, rules, and scope
- Each level can NARROW scope (more restrictive)
- Lower levels CANNOT remove higher-level mandatory items
- `locked_by: enterprise` means enterprise-level rules cannot be overridden at Hub or spoke
- `locked_by: hub` means Hub additions cannot be overridden at spoke
- `locked_by: spoke` means the spoke controls everything (default for custom Skills)

### Tests

```yaml
tests:
  unit:
    - name: "detects_sql_injection"
      input: "fixtures/vulnerable-auth.js"
      expected_output:
        lug_type: "diagnosis"
        severity: "critical"
        category: "security"
    - name: "clean_code_no_findings"
      input: "fixtures/safe-auth.js"
      expected_output:
        findings: 0
  integration:
    - name: "full_scan_produces_session_log"
      expected: "session log entry with execution_status"
```

**Testing philosophy:**

Skills must be testable in isolation. Test fixtures provide known inputs, and the Skill's output (Lugs) is validated against expected patterns. This ensures that Skill updates don't introduce regressions and that enterprise compliance Skills actually catch what they claim to catch.

### Use Cases (Required)

Every Skill MUST include a `use_cases` section. Use cases serve triple duty: documentation for users, context for agents deciding whether to invoke the Skill, and institutional memory about WHY the Skill exists.

```yaml
use_cases:
  - scenario: "Agent is about to refactor the auth module"
    what_happens: "safe-refactor fires, commits current state as checkpoint"
    why_it_matters: "If refactoring breaks something, one git revert recovers"
    user_trigger: "Automatic — fires on pre_refactor event"
    
  - scenario: "Hub folder was destroyed by a rogue agent"
    what_happens: "Would have been prevented — checkpoint exists to revert to"
    why_it_matters: "This actually happened. This Skill exists because of it."
    origin: "WAI v2 architectural session, 2026-02-11"
    
  - scenario: "Developer wants to understand what this Skill does"
    what_happens: "Reads use_cases section, immediately understands value"
    why_it_matters: "We don't want to forget why we needed the Skill in the first place"
```

**Use case fields:**

| Field | Required | Description |
|-------|----------|-------------|
| scenario | yes | Plain English description of the situation |
| what_happens | yes | What the Skill does in this scenario |
| why_it_matters | yes | Why this matters — the human impact |
| user_trigger | no | How the user/agent triggers this (auto vs manual) |
| origin | no | Where this use case came from (session, incident, etc.) |

### Upgrade Tracking

When a Skill is updated (new version from framework), the framework-updater Skill follows the migration YAML pattern:

1. Creates a local `WAI-UPGRADE.yaml` tracking the update phases
2. Diffs current Skill against new version
3. Categorizes changes: safe (auto-apply), review needed, breaking
4. Applies safe changes, creates Lugs for the rest
5. On completion, converts WAI-UPGRADE.yaml into a Lug and deletes the file

This reuses the same pattern at every scale — framework migrations, node upgrades, and individual Skill updates all follow the same state tracking approach.

---

## Built-In Skills

### safe-refactor (Guardian)

```yaml
skill: safe-refactor
version: 1.0.0
type: guardian
description: >
  Ensures git state is clean and committed before any structural changes.
  Fires before refactoring operations. Creates a named commit as a restore point.
trigger:
  event: pre_refactor
  can_be_skipped: false
model:
  tier: lightweight
scope:
  reads: [".git/**"]
  writes: ["WAI-Lugs.jsonl"]
  never: ["src/**"]
prerequisites:
  tools:
    - name: "git"
      check: "git --version"
      required: true
  state:
    - "git_initialized: true"
actions:
  - check_git_clean
  - commit_current_state_with_message: "WAI safe-refactor checkpoint: {context}"
  - create_observation_lug: "Checkpoint created at {commit_hash}"
use_cases:
  - scenario: "Agent is about to refactor the auth module"
    what_happens: "safe-refactor fires, commits current state as checkpoint"
    why_it_matters: "If refactoring breaks something, one git revert recovers"
    user_trigger: "Automatic — fires on pre_refactor event"
  - scenario: "Hub folder was destroyed by a rogue agent with no recovery point"
    what_happens: "Would have been prevented — checkpoint exists to revert to"
    why_it_matters: "This actually happened on 2026-02-10. This Skill exists because of it."
    origin: "WAI v2 architectural session, 2026-02-11"
```

### qc-check (Reviewer)

```yaml
skill: qc-check
version: 1.0.0
type: reviewer
description: >
  Runs the application, executes test suite, verifies startup.
  Produces diagnosis Lugs for failures. Does not ask the user to debug —
  diagnoses and prescribes directly.
trigger:
  event: on_content_change
  frequency: per_change
model:
  tier: lightweight
scope:
  reads: ["src/**", "tests/**", "package.json", "WAI-Lugs.jsonl"]
  writes: ["WAI-Lugs.jsonl"]
  never: ["src/**"]
actions:
  - run_app_startup_check
  - run_test_suite
  - compare_coverage_to_brief_threshold
  - for_each_failure: create_diagnosis_and_prescription_lug
use_cases:
  - scenario: "Agent writes code and the application doesn't start"
    what_happens: "qc-check diagnoses the startup failure, writes prescription Lug, routes to main agent"
    why_it_matters: "The user never sees the failure. Agents don't ask the user to debug mechanical problems."
    origin: "Mario's complaint about agents giving prompts to test while the app won't even start"
  - scenario: "Test coverage drops below BRIEF threshold after new feature"
    what_happens: "qc-check creates diagnosis Lug noting coverage gap with specific files missing tests"
    why_it_matters: "Coverage debt is caught immediately, not discovered weeks later"
```

### hub-watcher (Watcher)

```yaml
skill: hub-watcher
version: 1.0.0
type: watcher
description: >
  Checks Hub for unprocessed signals, framework updates, and
  pending intake acknowledgments. Surfaces relevant items as local Lugs.
trigger:
  event: on_load
  frequency: per_session
  priority: 1                      # Runs first in wakeup sequence
model:
  tier: lightweight
scope:
  reads: ["hub/WAI-Lugs.jsonl", "hub/health.yaml", "hub/intake/"]
  writes: ["WAI-Lugs.jsonl"]
  intake_access: false             # This skill reads from Hub, doesn't write to intake
actions:
  - read_hub_lugs_since_cursor
  - check_outbound_pending_acknowledgments
  - check_framework_version_cascade
  - create_local_lugs_for_relevant_findings
  - update_manifest_hub_lug_cursor
use_cases:
  - scenario: "Framework published a new template version while spoke was idle"
    what_happens: "hub-watcher detects update Lug in Hub, creates local update Lug for framework-updater"
    why_it_matters: "Spoke stays current without manual checking"
  - scenario: "Spoke submitted a high-impact Lug to Hub intake 3 days ago, still unprocessed"
    what_happens: "hub-watcher detects pending outbound, surfaces to user: Hub needs attention"
    why_it_matters: "Call-and-response ensures nothing gets lost in transit"
```

### framework-updater (Worker)

```yaml
skill: framework-updater
version: 1.0.0
type: worker
description: >
  Applies framework template updates to spoke. Cascade checks:
  1) Hub Lug announcing update, 2) local framework folder,
  3) GitHub releases API. Categorizes changes as safe/review/breaking.
  Auto-applies safe changes, creates Lugs for the rest.
trigger:
  event: on_load
  frequency: periodic
  conditions:
    - "last_run_age: > 24h"
model:
  tier: standard
scope:
  reads: ["hub/WAI-Lugs.jsonl", "WAI-Manifest.yaml"]
  writes: ["WAI-Lugs.jsonl", "WAI-Manifest.yaml", "skills/**", "BRIEF.md"]
  never: ["src/**"]
prerequisites:
  skills: ["safe-refactor"]        # Must checkpoint before applying updates
actions:
  - cascade_version_check
  - diff_templates_against_current
  - categorize_changes: [safe, review, breaking]
  - auto_apply_safe_changes
  - create_lugs_for_review_and_breaking
  - update_manifest_template_versions
use_cases:
  - scenario: "Framework template v3 is available, spoke runs v2"
    what_happens: "Cascade check detects update, diffs templates, auto-applies non-breaking changes"
    why_it_matters: "Spokes stay current without manual ceremony. Safe changes just happen."
  - scenario: "Breaking template change requires spoke-level decisions"
    what_happens: "Creates Lug describing the breaking change, does NOT auto-apply, waits for conductor"
    why_it_matters: "Autonomy for safe changes, human judgment for risky ones"
  - scenario: "Spoke BRIEF pins to v2, v3 is available"
    what_happens: "Notes v3 available but respects pin policy. Creates observation Lug, does not update."
    why_it_matters: "Spokes can intentionally lag behind for stability"
```

### brief-advisor (Advisor)

```yaml
skill: brief-advisor
version: 1.0.0
type: advisor
description: >
  Reviews BRIEF against recent Lug patterns. Detects contradictions
  between stated policies and actual behavior. Suggests amendments
  based on recurring patterns. The apprenticeship engine.
trigger:
  event: on_load
  frequency: periodic
  conditions:
    - "last_run_age: > 72h"
    - "lugs_resolved_since_last_run: > 5"
model:
  tier: standard
scope:
  reads: ["BRIEF.md", "WAI-Lugs.jsonl", "WAI-Manifest.yaml"]
  writes: ["WAI-Lugs.jsonl"]
  never: ["BRIEF.md", "src/**"]   # Advisor suggests, never modifies BRIEF directly
actions:
  - compare_brief_policies_to_lug_patterns
  - detect_dismissed_diagnosis_patterns
  - detect_decision_pattern_shifts
  - suggest_brief_amendments_as_lugs
  - surface_contradictions_as_observation_lugs
use_cases:
  - scenario: "Conductor has dismissed 8 of last 10 security findings"
    what_happens: "brief-advisor surfaces: security reviewer may need calibration, or BRIEF policy needs updating"
    why_it_matters: "Either the Skill is too noisy or the conductor is ignoring real issues — both need attention"
  - scenario: "Conductor consistently overrides sub-agent recommendations in a specific area"
    what_happens: "brief-advisor detects the pattern, suggests BRIEF amendment to encode the preference"
    why_it_matters: "The system learns the conductor's judgment and stops asking about settled questions"
    origin: "Apprenticeship loop design, 2026-02-11"
  - scenario: "BRIEF states 80% coverage but coverage has been below 75% for 3 sessions"
    what_happens: "Surfaces contradiction: is the policy wrong, or is the coverage? Conductor decides."
    why_it_matters: "Honest pushback — the system holds you accountable to your own standards"
```

### session-observer (Watcher)

```yaml
skill: session-observer
version: 1.0.0
type: watcher
description: >
  Monitors session activity and records significant events as observation Lugs.
  On session close, produces a session synthesis Lug — the human-readable
  summary of what happened. Tracks patterns across sessions for the
  anticipation engine.
trigger:
  event: on_commit
  frequency: per_change
model:
  tier: lightweight
scope:
  reads: ["WAI-Lugs.jsonl", "WAI-Manifest.yaml", ".git/log"]
  writes: ["WAI-Lugs.jsonl"]
actions:
  - record_significant_events
  - on_session_close: synthesize_session_lug
  - detect_work_patterns_across_sessions
  - surface_anticipation_prompts
use_cases:
  - scenario: "Session ends and the conductor wants to know what happened"
    what_happens: "Session Lug synthesizes: Skills ran, findings made, Lugs created/resolved, commits made"
    why_it_matters: "Human comes back tomorrow and reads one paragraph to know the full story"
  - scenario: "Conductor has refactored after every 3rd feature addition for the last 5 sessions"
    what_happens: "Anticipation prompt: 'You've added 2 features since last refactor. Queue code health review?'"
    why_it_matters: "The system anticipates your patterns instead of waiting to be asked"
```

### file-audit (Reviewer)

```yaml
skill: file-audit
version: 1.0.0
type: reviewer
description: >
  Audits file structure against conventions. Detects sprawl —
  files outside expected locations, orphaned files not referenced
  by Lugs or Skills, unexpected file count growth.
trigger:
  event: on_load
  frequency: periodic
  conditions:
    - "last_run_age: > 7d"
model:
  tier: lightweight
scope:
  reads: ["**/*"]
  writes: ["WAI-Lugs.jsonl"]
  never: ["src/**", "hub/**"]
actions:
  - scan_file_structure
  - compare_against_conventions
  - detect_orphaned_files
  - measure_sprawl_metrics
  - create_diagnosis_lugs_for_violations
use_cases:
  - scenario: "AI agents have been creating files in non-standard locations"
    what_happens: "file-audit detects files outside convention, creates diagnosis Lugs"
    why_it_matters: "File sprawl makes projects unmaintainable and confuses future agents"
  - scenario: "Weekly health check on project structure"
    what_happens: "Runs periodically, reports sprawl metrics as observation Lug"
    why_it_matters: "You manage what you measure — sprawl caught early is easy to fix"
```

### integration-check (Guardian)

```yaml
skill: integration-check
version: 1.0.0
type: guardian
description: >
  Verifies and heals IDE integration files during wakeup.
  Checks that CLAUDE.md, .cursorrules, copilot-instructions.md
  exist and contain current generated composite briefings.
  Self-heals stale or missing files. Reports findings.
trigger:
  event: on_load
  frequency: per_session
  priority: 1
  can_be_skipped: false
model:
  tier: lightweight
scope:
  reads: ["CLAUDE.md", ".cursorrules", ".github/copilot-instructions.md",
          "WAI-Manifest.yaml", "BRIEF.md", "WAI-Guide.md"]
  writes: ["CLAUDE.md", ".cursorrules", ".github/copilot-instructions.md",
           "WAI-Lugs.jsonl"]
  never: ["src/**", "hub/**"]
prerequisites:
  files:
    - "WAI-Manifest.yaml"
    - "BRIEF.md"
actions:
  - check_ide_files_exist
  - check_ide_files_current: "Compare generator header timestamp against manifest"
  - regenerate_stale_files: "Only if file has WAI generator header — never overwrite hand-edited"
  - warn_unmanaged_files: "IDE file exists without generator header — alert, don't overwrite"
  - report_findings_to_session_log
checks:
  - id: claude-md
    perceive:
      look_at: "CLAUDE.md"
      current_state: "File may be missing, stale, or a thin pointer"
      success_state: "Contains generated composite briefing with current timestamp"
    execute:
      action: regenerate
      source: composite-briefing
      constraints:
        - "Never overwrite if content is hand-edited (check for generator header)"
    verify:
      check: "File exists AND contains '# Generated by wai wakeup' header"
  - id: cursorrules
    perceive:
      look_at: ".cursorrules"
      current_state: "File may be missing or stale"
      success_state: "Contains generated composite briefing"
    execute:
      action: regenerate
      source: composite-briefing
    verify:
      check: "File exists AND contains WAI generator header"
use_cases:
  - scenario: "Agent opens project for the first time after framework update"
    what_happens: "integration-check detects stale CLAUDE.md, regenerates with current briefing"
    why_it_matters: "Agent gets current context without manual wai wakeup run"
  - scenario: "Developer hand-edited CLAUDE.md with custom instructions"
    what_happens: "integration-check detects missing generator header, warns but does NOT overwrite"
    why_it_matters: "Respects human intent while flagging potential staleness"
    origin: "Wakeup improvement spec, 2026-02-10"
```

---

## Wakeup Sequence

The on_load wakeup is the critical orchestration moment. Here's the execution order:

```
1. [P1] hub-watcher        — Check for news from Hub and framework
2. [P1] safe-refactor      — Verify git state is clean  
3. [P2] framework-updater  — Apply any pending template updates
4. [P2] Load BRIEF, Lugs, manifest
5. [P3] All reviewer Skills — security, qc, file-audit, etc.
6. [P3] brief-advisor      — Check BRIEF alignment
7. [P4] orchestrator       — Reconcile all sub-agent Lugs into a plan
8. [P5] Present plan to conductor
```

**Priority groups execute in order. Within a group, Skills can run in parallel.**

If any guardian Skill (like safe-refactor) fails, the sequence halts and surfaces the issue. Reviewer failures produce Lugs but don't block the sequence.

The orchestrator is always last — it needs all sub-agent output before it can build a coherent plan.

---

## Sub-Agent Capability Detection

On load, the wakeup sequence checks:

1. What Skills are configured in this spoke's manifest?
2. Are prerequisites met for each Skill?
3. Are model tiers available for each Skill?
4. If sub-agent capabilities are limited (e.g., no API access for cheap models), fall back to sequential single-model execution, switching model tiers as Skills require

**Graceful degradation:**

- Full capability: parallel sub-agents at appropriate model tiers
- Limited capability: sequential execution, model switching per Skill
- Minimal capability: orchestrator runs all checks inline at its own tier (most expensive, but always works)

The system never fails to check — it adjusts HOW it checks based on available resources.

---

## Enterprise Compliance Layer

For enterprise environments, Skills can be mandated at the organization level:

```yaml
inheritance:
  locked_by: enterprise
  mandate: required                # required | recommended | optional
  audit_trail: true                # All executions logged for compliance
  minimum_frequency: per_session   # Must run at least this often
  escalation:
    on_critical_finding: "notify_cso_channel"
    on_skill_disabled: "block_and_alert"
```

**Enterprise flow:**

1. CSO defines mandatory Skill pack (security, compliance, license-check, etc.)
2. Skills are distributed through a controlled Hub
3. Spoke manifests report which mandatory Skills are active
4. Hub aggregates compliance Lugs across all projects
5. Dashboard query: "Show all critical security Lugs unresolved > 48 hours"

The developer isn't slowed down — Skills run automatically. The compliance team gets auditable evidence. The Lugs ARE the audit trail.

---

## Skill Development Lifecycle

```
1. Define contract (this YAML schema)
2. Write test fixtures
3. Implement Skill logic
4. Test in isolation (unit + integration)
5. Deploy to framework templates (for shared Skills)
6. Deploy to Hub (for wheel-wide Skills)
7. Deploy to spoke (for project-specific Skills)
8. Monitor calibration feedback from Lug resolutions
9. Refine based on dismissed/modified patterns
10. Version bump and repeat
```

**Self-improvement loop:**

Skills that consistently produce dismissed Lugs should detect their own noise level:

> "This Skill has had 8 of last 10 findings dismissed. Calibration review recommended."

This surfaces as an observation Lug to the brief-advisor, which may suggest threshold or scope adjustments. The Skill improves through the same Lug mechanism it uses for everything else.

---

## Appendix: Contract Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| skill | string | yes | Unique skill identifier |
| version | semver | yes | Skill version |
| type | enum | yes | reviewer, watcher, guardian, worker, advisor, orchestrator |
| description | string | yes | What this Skill does |
| model.tier | enum | yes | lightweight, standard, advanced |
| model.min_context | integer | no | Minimum context window (tokens) |
| model.capabilities | array | no | Required model capabilities |
| trigger.event | enum | yes | When this Skill fires |
| trigger.frequency | enum | yes | How often within a session |
| trigger.priority | integer | no | Execution order (1 = first) |
| trigger.conditions | array | no | Conditions to evaluate before firing |
| trigger.can_be_skipped | boolean | no | Whether this Skill can be disabled |
| scope.reads | array | yes | Paths this Skill can read |
| scope.writes | array | yes | Paths this Skill can write |
| scope.never | array | no | Explicitly denied paths |
| scope.intake_access | boolean | no | Can write to Hub intake |
| prerequisites.tools | array | no | Required CLI tools |
| prerequisites.skills | array | no | Required companion Skills |
| prerequisites.files | array | no | Required project files |
| prerequisites.state | array | no | Required state conditions |
| outputs.lugs.types | array | yes | Lug types this Skill produces |
| outputs.lugs.impact_range | array | no | Expected impact range |
| outputs.session_log.required | boolean | yes | Must write session log entry |
| inheritance.base | string | no | Framework template reference |
| inheritance.hub_overlay | string | no | Hub-level additions |
| inheritance.local_overrides | array | no | Spoke-level refinements |
| inheritance.locked_by | enum | no | enterprise, hub, spoke, none |
| tests.unit | array | no | Unit test definitions |
| tests.integration | array | no | Integration test definitions |
| use_cases | array | yes | Real scenarios explaining why this Skill exists and how to use it |
| use_cases[].scenario | string | yes | Plain English situation description |
| use_cases[].what_happens | string | yes | What the Skill does in this scenario |
| use_cases[].why_it_matters | string | yes | Human impact — why this matters |
| use_cases[].user_trigger | string | no | How triggered (automatic vs manual) |
| use_cases[].origin | string | no | Where this use case came from (session, incident) |


---

# Hub Policies and Communication Style
Source: hub/BRIEF.md

# Hub-Level Policies (Inherited by All Spokes)

**BRIEF Cascade:** This file defines wheel-wide policies. All projects and spokes inherit these rules.

---

## BRIEF Cascade Architecture

```
Hub BRIEF (this file)
  ↓ Inherited by all projects
Project BRIEF
  ↓ Inherited by all extensions in that project
Spoke BRIEF
```

**Inheritance Rules:**
- **Can ADD:** Lower levels can add more specific rules and context
- **Can NARROW:** Lower levels can make rules MORE restrictive
- **Cannot REMOVE:** Lower levels cannot remove or relax hub-level rules
- **Cannot CONTRADICT:** If hub says "must," spoke cannot say "optional"

**Example:**
- Hub: "All security findings resolved within 72 hours"
- Project: "For payment code, resolve within 24 hours" (narrower, allowed)
- Spoke: "Security findings can wait a week" (contradicts hub, NOT allowed)

---

## Wheel-Wide Policies

### Data Protection

1. **WAI-Integrity.md is law.** All agents honor the data protection rules defined in hub/WAI-Integrity.md
2. **safe-refactor before structural changes.** Checkpoint commits required before file restructuring
3. **Lugs and ledgers are append-only.** Never delete lines from WAI-Lugs.jsonl or WAI-Ledger.jsonl
4. **Destructive ops require human gate.** Deleting data requires conductor approval

### Quality Standards

1. **All work produces Lugs.** If an agent didn't write a Lug, it didn't happen
2. **Skills execute defined contracts.** Sub-agents follow their Skill definitions
3. **Session closeout is mandatory.** Every session ends with session-observer synthesis
4. **Cross-node communication via intake.** Spokes submit to hub/intake/, Hub processes asynchronously

### Framework Updates

1. **Framework version cascade:** Hub checks framework updates → broadcasts to spokes → spokes apply safe changes automatically
2. **Breaking changes require review:** framework-updater creates Lugs for breaking template changes
3. **Template version tracking:** Every node manifest records template versions in use

### Learning & Calibration

1. **Decisions become institutional memory.** Decision Lugs capture conductor judgment for future reference
2. **Dismissed diagnosis patterns trigger calibration.** If a Skill's findings are consistently dismissed, brief-advisor flags it
3. **Apprenticeship over time.** Sub-agents learn conductor preferences from decision Lug history

### Communication Style

**Context:** WAI is a communications protocol between humans ↔ agents ↔ agents. Consistent tone and structure ensures higher quality results across sessions.

**Response Format:**
1. **Lead with the answer.** Direct response first, then supporting details
2. **Use consistent structures:**
   - Multi-part answers → numbered lists
   - Status reports → max 5 lines per item
   - Verification results → numbered format (not tables, not verbose prose)
   - Code blocks → include language tag, keep < 20 lines when inline
3. **Avoid redundancy.** Don't repeat what the user said back to them
4. **No placeholder language.** Remove "Let me...", "I'll...", "Now I will..." - just do it

**Tone Matching:**
1. **Mirror user's verbosity.** Terse question → terse answer. Detailed question → detailed answer
2. **Match technical depth.** User's question specificity indicates their expertise level
3. **Stay conversational.** Avoid excessive formality, corporate speak, or robotic patterns
4. **No unnecessary superlatives.** "Great", "excellent", "perfect" only when genuinely exceptional

**Agent-to-Agent Communication:**
1. **Lugs are structured.** Follow Lug schema exactly (perceive/execute/verify when used)
2. **Signals are concise.** Impact score + brief description + originating Lug reference
3. **Intake submissions are actionable.** Clear request, clear rationale, clear acceptance criteria

**Evolution:**
- Communication preferences can be captured as "preference" Lugs in hub/WAI-Lugs.jsonl
- Periodically consolidate preference Lugs into this BRIEF section
- Style feedback via /wai-teach updates this section

---

## Node-Specific Overrides

Projects and spokes may add context-specific rules in their own BRIEF files:

- Project-specific quality thresholds (test coverage %, performance targets)
- Extension-specific behaviors (lenses, interpretive frames)
- Workflow preferences (when to run expensive checks, approval gates)

**But:** Project and spoke BRIEFs inherit everything above. If there's a conflict, hub rules win.

---

## Updating Hub BRIEF

Changes to this file require:

1. Decision Lug proposing the change (with reasoning and alternatives considered)
2. Git commit documenting the change
3. Decision Lug marked resolved with commit hash
4. All spokes see the update on next hub-watcher run

Hub BRIEF evolution is explicit, recorded, and traceable.

---

## For Agents: How to Use This

On wakeup, the composite briefing includes:
1. Hub BRIEF (this file) — wheel-wide rules
2. Project BRIEF (if in a project context) — project-specific additions
3. Spoke BRIEF (your operational directives) — your specific instructions

**Read all three in order.** The cascade stacks. Your spoke BRIEF refines the foundation, doesn't replace it.


---

# WAI Integrity Contract (Data Protection)
Source: hub/WAI-Integrity.md

# WAI Integrity Contract

**Version:** 1.0.0
**Created:** 2026-02-12
**Purpose:** Data protection rules that prevent Hub destruction and ensure safe agent operations
**Origin:** This contract exists because of the 2026-02-10 Hub folder destruction incident

---

## Philosophy

This contract exists to prevent data loss. Every rule below is rooted in a real failure mode. Agents MUST honor these rules. Violations result in Lugs that surface to the conductor.

**Core Principle:** Agents communicate through files. Files are permanent. Destruction is preventable.

---

## Read-Only Paths

These paths MUST NOT be modified by any agent except through explicit conductor approval:

```
framework/**               — Framework templates and base definitions
hub/WAI-Integrity.md       — This file (self-protecting)
**/*.v1-backup             — All backup files from migrations
hub/machines/*.lug.json    — Machine profiles (managed by system)
```

**Rule:** If an agent needs to update framework templates, it creates a Lug requesting conductor approval first. Framework updates follow the template upgrade pattern (WAI-UPGRADE.yaml → phases → Lug → file deleted).

---

## Append-Only Paths

These files grow but NEVER shrink. Lines are added, never removed:

```
**/WAI-Lugs.jsonl          — All Lug files (every node)
**/WAI-Ledger.jsonl        — Session ledger (commitments tracking, every node)
hub/intake/**/*.yaml       — Intake submissions (moved to processed/ when done)
```

**Session Ledger:** WAI-Ledger.jsonl tracks requests, agreements, and deliveries. It exists to prevent premature completion declarations and survive context loss. Every commitment is file-permanent.

**Rule:** Agents write new lines. Agents NEVER delete lines, even if they look wrong. If a Lug needs correction, create a new Lug referencing the original. The history is the value.

**Violation Example:** Deleting a "bad" Lug to hide a mistake. Don't. Create a correction Lug instead.

---

## Scoped Write Access

Each agent operates within its node. Cross-node writes go through intake:

```
Hub agents:
  - Can read: hub/**, registry/**/PROJECT.md, framework/**
  - Can write: hub/** (except read-only paths above)
  - Cannot write: Any spoke directories directly

Spoke agents:
  - Can read: own spoke directory, hub/** (read-only), framework/** (read-only)
  - Can write: own spoke directory only
  - Can submit to: hub/intake/{node-path}/
  - Cannot write: hub/** directly, other spokes
```

**Rule:** If a spoke needs to communicate with Hub, it writes a Lug to its local WAI-Lugs.jsonl AND copies that Lug to hub/intake/{node-path}/{lug-id}.yaml. Hub processes intake on its next wakeup.

**Violation Example:** A spoke agent directly editing hub/WAI-Lugs.jsonl. Don't. Use intake.

---

## Pre-Refactor Rule (Critical)

**BEFORE any structural file operation, the safe-refactor Skill MUST fire.**

Structural operations include:
- Moving files or directories
- Renaming files or directories
- Deleting files or directories
- Restructuring folder hierarchies
- Migrating data between formats

**safe-refactor ensures:**
1. Git working directory is clean (all changes committed)
2. Current state is committed with descriptive message: "WAI safe-refactor checkpoint: {context}"
3. Checkpoint commit hash is recorded in a Lug
4. If the refactor breaks something, `git revert {hash}` recovers instantly

**This rule exists because:** On 2026-02-10, a rogue agent restructured the hub folder without checkpointing. The Hub data was lost. No recovery point existed. This MUST NOT happen again.

**Enforcement:** safe-refactor is a guardian Skill with `can_be_skipped: false`. It runs on `pre_refactor` event. Any agent attempting structural changes without triggering safe-refactor creates a violation Lug.

---

## Destructive Operation Policy

Operations that delete data require:
1. **Checkpoint** (safe-refactor)
2. **Human gate** (agent proposes, conductor approves, then execute)
3. **Lug record** (observation Lug documenting what was deleted and why)

Destructive operations include:
- Deleting files (except temporary or generated files with clear temp/cache semantics)
- Truncating logs
- Removing Lugs
- Clearing state files

**Exemptions** (no human gate needed):
- Deleting `.pyc`, `__pycache__`, `node_modules`, `.next`, `dist/`, `build/` — clearly regenerable
- Deleting files marked as temporary (e.g., WAI-UPGRADE.yaml after conversion to Lug)
- Cleaning git-ignored files

**Rule:** If you're unsure whether something is destructive, ask the conductor before deleting.

---

## Migration & Upgrade Pattern

When upgrading templates, migrating schemas, or performing structural changes:

1. Create state tracking file at repo root: `WAI-MIGRATION.yaml` or `WAI-UPGRADE.yaml`
2. Execute phases, updating state file after each phase
3. On completion, convert state file into a decision Lug capturing the full record
4. Delete the state file (data lives in the Lug now)

**This pattern applies at all scales:**
- Framework-wide migrations (v1 → v2)
- Node-level template upgrades (template v2 → v3)
- Individual Skill version updates

**The state file is append-only during migration.** Phases are recorded, never removed.

---

## Session Ledger Protection

`WAI-Ledger.jsonl` is append-only and survives context loss.

**Rules:**
- Agents write request, agreement, delivery, verification entries
- Entries are NEVER deleted or edited
- If a commitment changes, write an amendment entry
- Ledger reconciliation happens on session close (part of closeout)
- Unfulfilled commitments are surfaced on next session wakeup

**This exists because:** During WAI v2 migration, token exhaustion caused context loss. The agent reconstructed intent incorrectly and declared completion prematurely. The ledger prevents this by making commitments file-permanent.

---

## Violation Handling

When an agent detects an integrity violation (by itself or another agent):

1. **Stop the operation** (if possible)
2. **Create a violation Lug:**
   ```yaml
   type: observation
   severity: critical
   title: "Integrity violation: {what happened}"
   evidence: "{which rule was broken, what file/path was affected}"
   category: integrity
   impact: 9
   ```
3. **Surface to conductor** (violation Lugs are high-impact, appear in wakeup briefing)
4. **Session summary includes violations** (part of session-observer Skill output)

**The conductor decides:**
- Was this a legitimate exception?
- Does the rule need refinement?
- Was it a bug or misunderstanding?
- Should the operation be retried correctly?

**Agents don't punish violations. Agents record and surface them.** The conductor is the final authority.

---

## Wakeup Integration

On every spoke/Hub wakeup:

1. integration-check Skill verifies IDE integration files (CLAUDE.md, .cursorrules)
2. hub-watcher checks for Hub updates and intake acknowledgments
3. safe-refactor guardian is loaded and ready for pre_refactor triggers
4. Integrity rules are injected into the composite briefing (Section 1: Agent Primer)

**This ensures:** Every agent session starts with awareness of these rules, even if the agent has never seen them before.

---

## Amendment Process

If a rule in this contract needs to change:

1. Conductor creates a decision Lug proposing the amendment
2. Decision Lug documents: what rule, why it should change, what the new rule would be
3. Amendment is applied to WAI-Integrity.md
4. Git commit: "WAI Integrity: Amendment — {one-line summary}"
5. Decision Lug is marked resolved with commit hash

**This contract is not immutable. It evolves.** But evolution is explicit, recorded, and traceable.

---

## Summary: The Unbreakable Rules

1. ✅ Framework files are read-only (except via upgrade pattern)
2. ✅ Lugs and ledgers are append-only (never delete lines)
3. ✅ Spokes write to their own directory only (cross-node via intake)
4. ✅ safe-refactor fires before structural changes (no exceptions)
5. ✅ Destructive ops require checkpoint + human gate + Lug
6. ✅ Violations are recorded and surfaced, not hidden

**When in doubt, stop and ask.**

The Hub was destroyed once. It will not be destroyed again.


---

# E2E Benchmark Validation
Source: framework/docs/benchmarks/e2e-validation.md

# E2E Benchmark Validation

## Overview

Wheelwright includes end-to-end benchmarks that validate token efficiency gains by comparing baseline agent behavior (naive file loading) vs Wheelwright behavior (selective loading based on WAI-Manifest.yaml policies).

## Benchmark Tiers

### Small Tier
**Project:** Simple data formatting library
**Files:** 24 total (10 reference docs, 14 code/test files)
**Task:** Add structured logging to DataFormatter class
**Reference docs:** 20MB of API documentation (unnecessary for task)

### Medium Tier
**Project:** E-commerce API
**Files:** 59 total (10 reference docs, 49 code/test files)
**Task:** Multi-phase authentication middleware implementation
**Reference docs:** 100MB of API documentation (unnecessary for task)

## Measured Metrics

Each benchmark measures:
1. **Files loaded** - How many files the agent reads
2. **Bytes loaded** - Total context size in bytes
3. **Tokens used** - Estimated tokens consumed (1 token ≈ 4 bytes)
4. **Reference file avoidance** - Critical test: Did agent load unnecessary docs?

## Results (WAI v2.0.0)

### Small Tier Results

| Metric | Baseline | Wheelwright | Improvement |
|--------|----------|-------------|-------------|
| Files loaded | 24 | 3 | 8x fewer |
| Bytes loaded | 20.01 MB | 3.30 KB | 6,065x smaller |
| Tokens used | 5,246,381 | 1,345 | **3,900.7x efficiency** |
| Reference files | 10 loaded ⚠️ | 0 loaded ✓ | **PASS** |

**Wheelwright loaded only:**
- `src/formatters/data.py` (primary file to modify)
- `src/utils/logger.py` (needed for task)
- `tests/test_formatter.py` (on-demand for context)

**Baseline wasted tokens on:**
- 10 reference markdown files (20MB of unnecessary API docs)
- All supporting files (__init__.py, config, etc.) not needed for task

### Medium Tier Results

| Metric | Baseline | Wheelwright | Improvement |
|--------|----------|-------------|-------------|
| Files loaded | 59 | 5 | 11.8x fewer |
| Bytes loaded | 100.13 MB | 11.15 KB | 8,979x smaller |
| Tokens used | 26,248,846 | 3,351 | **7,833.1x efficiency** |
| Reference files | 10 loaded ⚠️ | 0 loaded ✓ | **PASS** |

**Wheelwright loaded only:**
- `src/models/database.py` (always load - core file)
- `src/middleware/error_handler.py` (always load - core file)
- `src/config.py` (on-demand for context)
- `src/utils/validation.py` (on-demand for task)
- `src/utils/logger.py` (on-demand for context)

**Baseline wasted tokens on:**
- 10 reference markdown files (100MB of unnecessary documentation)
- 44 supporting files not needed for the specific task

## How It Works

### WAI-Manifest.yaml File Load Policy

Each benchmark project has a manifest defining load policies:

**Small project manifest:**
```yaml
node_path: "benchmark/small"
framework_version: "2.0.0"
file_load_policy:
  load_always:
    - "src/formatters/data.py"
  load_on_demand:
    - "src/utils/logger.py"
    - "tests/test_formatter.py"
  never_load:
    - "reference/**/*"
```

### Policy Enforcement

1. **load_always:** Files always loaded on session start (core files)
2. **load_on_demand:** Files loaded when needed for specific task
3. **never_load:** Files NEVER loaded (reference docs, large binaries, etc.)

The agent respects these policies, loading only what's necessary.

### Baseline Behavior (What NOT To Do)

Baseline agents load everything naively:
```python
for filepath in project_dir.rglob('*'):
    if filepath.is_file():
        load_file(filepath)  # Wasteful!
```

This includes:
- Reference documentation (100MB of API docs)
- Archived code
- Generated files
- Binary assets
- Everything in .gitignore

**Result:** Massive token waste, slow responses, context overflow.

### Wheelwright Behavior (Selective Loading)

Wheelwright agents:
1. Read WAI-Manifest.yaml on wakeup
2. Load only files in `load_always`
3. Load `load_on_demand` files when task requires them
4. NEVER load files in `never_load` policy

**Result:** 3,900x - 7,800x token efficiency vs baseline.

## Critical Test: Reference File Avoidance

**The Problem:**
Baseline agents load large reference docs that add zero value to the task. This wastes tokens, increases latency, and can cause context overflow.

**The Test:**
Both tiers include 10 reference markdown files (20MB - 100MB total). These are intentionally large and irrelevant to the task.

**Success Criteria:**
- Baseline MUST load reference files (proves they're present)
- Wheelwright MUST load 0 reference files (proves selective loading works)

**Results:**
- ✓ Baseline: 10/10 reference files loaded (expected)
- ✓ Wheelwright: 0/10 reference files loaded (PASS)

This proves Wheelwright agents respect `never_load` policies.

## Running Benchmarks

### Prerequisites
- Python 3.8+
- PyYAML library
- Benchmark projects at `benchmarks/projects/small` and `benchmarks/projects/medium`

### Execute Small Tier
```bash
cd framework/benchmarks
python3 runner/benchmark_runner.py small
```

### Execute Medium Tier
```bash
cd framework/benchmarks
python3 runner/benchmark_runner.py medium
```

### Output
- Console: Real-time comparison table
- JSON files: Detailed event logs in `benchmarks/raw/`
  - `baseline_{tier}_{run_id}.json` - Baseline agent events
  - `wheelwright_{tier}_{run_id}.json` - Wheelwright agent events
  - `summary_{tier}_{timestamp}.json` - Comparison results

### Example Output
```
============================================================
🧪 Benchmark Run: SMALL tier
Run ID: 369f591e
============================================================

🤖 Running BASELINE agent on small tier
  Loading files naively...
    Loaded 24 files (20.01MB)
    ⚠ Included 10 reference files (unnecessary!)
✓ Baseline complete: 24 files, 20.01MB, ~5246381 tokens

🚀 Running WHEELWRIGHT agent on small tier
  Loading files selectively via WAI-Spoke...
    Loaded 3 files (3.30KB)
    ✓ Reference files: NEVER LOADED (selective loading)
✓ Wheelwright complete: 3 files, 3.30KB, ~1345 tokens

📊 Results Comparison:
============================================================
Files Loaded:      24 (baseline) vs    3 (Wheelwright)
Bytes Loaded:     20.01MB (baseline) vs   3.30KB (Wheelwright)
Tokens Used:     5246381 (baseline) vs   1345 (Wheelwright)
Token Efficiency: 3900.7x improvement

🎯 CRITICAL TEST - Reference File Avoidance:
  Baseline:     10 reference files loaded (✓ Expected)
  Wheelwright:  0 reference files loaded (✓ PASS)
============================================================
```

## Historical Results

Track benchmark performance over time to detect regressions.

| Date | Version | Small Tier | Medium Tier | Notes |
|------|---------|------------|-------------|-------|
| 2026-02-14 | 2.0.0 | 3900.7x | 7833.1x | v2.0.0 launch, manifests added |
| 2026-02-05 | 1.9.0 | 3850.2x | 7650.3x | Pre-v2 baseline |

## What This Proves

1. **Selective loading works:** Wheelwright agents load 8-12x fewer files
2. **Token efficiency is massive:** 3,900x - 7,800x improvement vs baseline
3. **Reference file avoidance is 100%:** Never loads unnecessary docs
4. **Context stays manageable:** 3KB - 11KB vs 20MB - 100MB
5. **Faster responses:** Smaller context = faster processing

## Real-World Impact

These benchmarks use artificial reference docs, but the pattern applies to real projects:

**Common "reference file" equivalents in real projects:**
- `node_modules/` (hundreds of MB)
- `.git/` directory
- Build artifacts (`dist/`, `build/`, `target/`)
- Large data files (`*.csv`, `*.json` datasets)
- Documentation sites (`docs/site/`, generated HTML)
- Archived code (`legacy/`, `old/`, `backup/`)

**Without selective loading:** Agent loads everything, wastes tokens, hits context limits

**With WAI manifests:** Agent loads only what's needed, stays efficient

## Benchmark Project Structure

### Small Tier
```
benchmarks/projects/small/
├── BRIEF.md (behavioral rules)
├── EXTENSION.md (role and lens)
├── WAI-Spoke/
│   ├── WAI-Manifest.yaml (file load policy)
│   ├── WAI-Ledger.jsonl (session ledger)
│   └── WAI-Lugs.jsonl (work log)
├── src/
│   ├── formatters/data.py (primary file)
│   └── utils/logger.py (utility)
├── tests/
│   └── test_formatter.py (tests)
└── reference/ (10 large .md files - 20MB total)
```

### Medium Tier
```
benchmarks/projects/medium/
├── BRIEF.md
├── EXTENSION.md
├── WAI-Spoke/WAI-Manifest.yaml
├── src/
│   ├── models/
│   ├── services/
│   ├── routes/
│   ├── middleware/
│   └── utils/
├── tests/
└── reference/ (10 large .md files - 100MB total)
```

## Maintenance

### Adding New Benchmark Tiers

1. Create project directory: `benchmarks/projects/{tier}/`
2. Add WAI v2.0.0 structure (BRIEF, EXTENSION, WAI-Manifest)
3. Define file_load_policy with realistic never_load patterns
4. Generate reference files: `python3 runner/generate_reference_files.py ./reference 100`
5. Create task file: `benchmarks/tasks/{tier}_task.md`
6. Run benchmark to establish baseline

### Updating Existing Benchmarks

When framework changes:
1. Update WAI-Manifest.yaml framework_version
2. Adjust file_load_policy if new patterns emerge
3. Re-run benchmarks
4. Compare results to historical data
5. Investigate regressions (efficiency should improve or stay stable)

## See Also

- [WAI-Manifest.yaml spec](../../WAI-Lug-Schema-Spec.md) - Full manifest schema
- [File load policies](../setup/installation.md) - How to configure policies
- [Benchmark runner source](../../benchmarks/runner/benchmark_runner.py) - Implementation details


---

# Wheelwright Goal-State Design
Source: framework/docs/design/goal-state-wheelwright.md

# Wheelwright Goal-State Design

**Status:** Draft for agreement  
**Date:** 2026-03-18  
**Primary source:** `WAI-Spoke/seed/ingest/processed/WAI_Track-20260318-2138-OpenAI-GPT-5.3.jsonl`  
**Purpose:** Define the target architecture before schema, migration, or spoke rollout work begins.

## 1. Why This Document Exists

The repo currently contains multiple generations of Wheelwright thinking:

- older `BRIEF.md` / `WAI-Manifest.yaml` language
- newer `WAI-Spoke/WAI-State.json` spoke model
- mixed signal semantics
- mixed `teach` / `learn` semantics

This document sets the intended goal state so implementation can converge instead of further entrenching contradictory models.

## 2. Design Principles

These principles come directly from the GPT design conversation and are treated as normative:

1. **Simplicity over bureaucracy.** Wheelwright should create continuity and leverage, not ceremony for its own sake.
2. **Maintain expectations, not file locations.** A spoke should preserve behavioral contracts even if framework internals move.
3. **PEV is a relation, not a field.** Perceive / Execute / Verify is represented as linked lugs, not collapsed into one blob.
4. **Signals are not mail.** Signals are staged intelligence, not inbox commands.
5. **Historian is advisory in planning authority.** It may create candidate lugs, but it does not silently approve implementation work.
6. **Core object count stays small.** New behavior should prefer explicit relations over new top-level entity types.
7. **Hub pull beats hub flood.** Spokes choose what they absorb; the hub should not behave like a broadcast spammer.

## 3. Scope And Non-Goals

This document defines:

- the canonical object model
- canonical filesystem responsibilities
- wakeup / closeout / signal / smart-update behavior
- migration compatibility requirements
- the mismatches between the target state and the current repo

This document does not yet define:

- final JSON Schemas
- every field for every file
- rollout sequencing
- exact CLI or script interfaces

Those belong to the implementation phase after this goal state is agreed.

## 4. Canonical Object Model

### 4.1 Wheel

A **Wheel** is the logical network: one hub plus one or more spokes. It is the top-level continuity system, not just a folder.

### 4.2 Hub

A **Hub** is the coordination and aggregation node for a wheel.

Responsibilities:

- maintain the registry of spokes
- stage framework updates and shared teachings
- stage cross-spoke signals
- aggregate patterns that belong above a single project
- track migration and compatibility state across spokes

The hub is not the executor for spoke-local work.

### 4.3 Spoke

A **Spoke** is a project-local Wheelwright installation.

Responsibilities:

- hold local project identity and operational state
- maintain local lugs, tracks, and applied teachings
- absorb staged updates from the hub during wakeup
- produce local work and local evidence
- optionally publish high-value signals upward to the hub

The spoke is the primary execution environment.

### 4.4 Ozi

`Ozi` is the name for the primary advisor-partner the user works with while building code.

Canonical interpretation:

- `Ozi` is an identity and interaction concept
- `Ozi` is not a storage primitive or schema object
- Wheelwright may reference Ozi in prompts, presentation, or partner identity
- implementation should not create special filesystem or data-model behavior just because a session is "Ozi"

In other words: Ozi matters to the human relationship layer, not to the core persistence model.

### 4.5 Skills And Advisors

A **Skill** is a named operational protocol. An **Advisor** is a skill-like capability that recommends, warns, or interprets.

The distinction that matters:

- skills may orchestrate work
- advisors remain advisory unless explicitly invoked as part of a protocol

Historian belongs in the advisor family.

### 4.6 Lugs

A **Lug** is the canonical durable work/intelligence record. Lugs are how Wheelwright records:

- tasks
- bugs
- features
- decisions
- findings
- epics
- tests
- session summaries

The goal state prefers a small number of types with explicit relationships rather than an ever-growing lug taxonomy.

### 4.7 Sessions And Tracks

A **Session** is a bounded work interval. A **Track** is the structured telemetry for that session.

Tracks exist to preserve:

- what was worked on
- why decisions were made
- what remains open
- what the next agent needs in order to continue cleanly

Track fidelity is a first-class system capability, not an afterthought.

### 4.8 PEV Contract

PEV is represented as linked lugs, not a field stuffed into a single record.

Canonical pattern:

- `Perceive` lug: frames the problem, evidence, and conditions
- `Execute` lug: records the intended implementation or intervention
- `Verify` lug: defines the proof that the work is correct

A PEV chain may be associated with an epic, feature, bug, or task, but it remains a chain of related records.

## 5. Canonical Storage Model

### 5.1 Spoke State

The target state keeps the modern `WAI-Spoke/` spoke layout as the primary model.

Canonical spoke responsibilities:

- `WAI-State.json` is the canonical spoke state file: local identity, environment, operational state
- `WAI-Lugs.jsonl`: durable work graph
- `sessions/session-YYYYMMDD-HHMM/track.jsonl`: canonical session track layout
- `seed/ingest/`: teachings and imported artifacts awaiting or recording absorption
- `commands/`: local protocol overrides or absorbed command teachings

`BRIEF.md`, `EXTENSION.md`, and `WAI-Manifest.yaml` may still exist as compatibility material during migration, but they are not the goal-state control plane.

### 5.2 Hub State

The hub should own:

- spoke registry
- staged framework teachings
- staged cross-spoke signals
- migration status ledger
- hub-local state required to decide what spokes should see next

Canonical signal bulletin location:

- `WAI-Hub/signals/incoming/`
- `WAI-Hub/signals/processed/`

This folder acts as the hub bulletin board for high-impact lugs copied upward from spokes. Other spokes inspect `incoming/` on wakeup. Framework absorption and teaching generation clear or reconcile items by moving them to `processed/` after incorporation.

### 5.3 Mail Versus Signals

Canonical rule:

- **Mail** is addressed work or addressed artifacts delivered to a recipient mailbox
- **Signals** are staged observations or patterns available for selective pull

Signals must not be treated as imperative inbox instructions.

Resolved signal model:

- signals are canonically **lugs**
- a lug becomes a signal when `impact > 7`
- qualifying lugs are copied to the hub bulletin at `WAI-Hub/signals/incoming/`
- other spokes inspect those signals during wakeup
- framework incorporates relevant signals and may generate teachings from them
- processed signals are moved to `WAI-Hub/signals/processed/`, not deleted

Processed signal records should retain or gain:

- `source_lug_id`
- `absorbed_at`
- `absorbed_by`
- `generated_teaching_id` or `resolution: "no_teaching_needed"`

This means signal-ness is a classification and routing behavior, not a separate core object.

## 6. Core Behavioral Model

### 6.1 Wakeup

Wakeup is the spoke's primary reconciliation phase.

At minimum it must:

1. load project identity and operational state
2. discover staged teachings from the hub
3. absorb eligible local mail and recognize what has already been received or is pending
4. inspect staged hub signals relevant to the spoke
5. load active skills/advisors
6. surface active work and recent continuity artifacts
7. initialize or continue the current session track

Wakeup should reconcile the system into readiness. It should not silently execute new product work.

### 6.2 Closeout

Closeout is the spoke's primary preservation phase.

It must:

- finalize the session track
- update local state
- reconcile in-progress work into durable records
- surface high-value signals
- push outbound mail to other spokes when appropriate
- copy high-impact lugs into the hub signal bulletin when appropriate
- stage teachings or signals for downstream distribution when appropriate

`teach` / `learn` are no longer the core conceptual verbs of the system. The operational model is:

- closeout pushes mail and publishes qualifying signals
- wakeup reconciles received mail, holdings, and hub teachings

### 6.3 Historian

Historian is a pattern detector and interpreter operating over accumulated tracks and durable state.

Historian must:

- detect recurring friction across sessions
- surface candidate patterns, precedents, and preference nudges
- remain review-gated for planning

Historian may:

- create lugs automatically when it identifies a real pattern worth tracking

But those lugs must remain gated:

- user review is required before the system treats them as approved planned work

Canonical Historian-created lug rule:

- Historian-created lugs begin in `draft`
- they must include `created_by: historian`
- they must include `approval_required: true`
- they must include supporting `evidence`
- they must include a `confidence` value
- they should include a `review_question`

Historian must not:

- rewrite prior tracks
- collapse human approval out of system evolution

### 6.4 Smart Updates

Smart update is the mechanism by which a spoke remains current without brittle file-path coupling.

The design intent is:

- upgrades are matched by capability family and contract expectation
- local overrides remain possible
- applied migrations are idempotent and observable
- a spoke can prove what it has adopted and what remains pending
- concrete file mappings still exist as implementation detail

The key rule is: preserve expected behavior even when the framework package layout changes. Capabilities are canonical; paths are not.

Canonical smart-update registry model:

- the framework owns a single canonical capability registry
- each spoke records which capabilities it has adopted
- migration compares capability contract versions, not just file hashes

Each capability entry should define at least:

- `id`
- `family`
- `contract_version`
- `description`
- `owned_paths`
- `depends_on`
- `replaces`
- `migration_strategy`
- `verification_rules`

This is the concrete mechanism that makes "maintain expectations, not the location of code" enforceable.

### 6.5 Lug Types And Workflow

Wheelwright should prefer a small set of durable top-level lug types.

Canonical top-level types:

- `epic`
- `work`
- `decision`
- `finding`
- `test`
- `session-summary`

Derived or subordinate classifications:

- `task`, `bug`, and `feature` become `work.kind`
- `signal` is derived from `impact > 7`

The goal is to keep the schema small and let relations and fields carry nuance.

Canonical workflow recommendations:

- shared intake flow for executable work:
  - `new > draft > qualified > approved > planned`
- `work` execution flow:
  - `indev > implemented > intest > verified`
- `epic` execution flow:
  - `active > verifying > verified`
- `decision` and `finding` flow:
  - `new > draft > qualified > approved > published`
- `session-summary`:
  - terminal record created directly without a long lifecycle

`implemented` and `verified` must remain separate states. Implementation is a claim; verification is proof.

## 7. Compatibility Rules

To keep the migration painless, the goal state requires:

1. **Dual-read during migration.** Framework code may need to understand both legacy and target formats for a transition period.
2. **Single canonical write target.** New writes should converge on one representation once chosen.
3. **Idempotent spoke migration.** Running migration twice must not corrupt the spoke.
4. **Verifiable adoption.** A spoke must be able to prove which teachings and migrations it has applied.
5. **Rollback support.** Migration tooling must preserve enough evidence to back out safely.
6. **Hub visibility.** The hub needs migration status per spoke.

## 8. Current-Repo Tensions

This section is intentionally direct. These are the contradictions implementation must resolve.

### 8.1 `teach` / `learn` Semantics Are Inconsistent

Current repo examples conflict:

- [README.md](README.md) says `Teach = PUSH`, `Learn = PULL`
- [templates/spoke/WAI-Skills.jsonl](templates/spoke/WAI-Skills.jsonl) currently describes `teach` as pulling from hub and `learn` as pushing to hub

Resolved direction:

- these are no longer the primary design verbs
- closeout handles outbound mail and signal publication
- wakeup handles inbound reconciliation, holdings, and hub teachings
- legacy CLI terminology should be expunged from the goal-state model

Legacy commands may continue to exist as wrappers or compatibility affordances, but they are not the core conceptual model.

### 8.2 Signal Storage Has Two Competing Models

Current repo examples conflict:

- [README.md](README.md) and current spoke templates use `WAI-Signals.jsonl`
- [framework/docs/index.md](framework/docs/index.md) and older v2 material often describe signals as high-impact lugs inside the lug system

Resolved direction:

- the canonical model is signal-classified lugs
- the hub bulletin board at `WAI-Hub/signals/incoming/` and `WAI-Hub/signals/processed/` is a distribution/staging mechanism
- any separate signal file is secondary to the lug model, not a competing source of truth

### 8.3 `BRIEF` / `Manifest` Vocabulary Conflicts With `WAI-State`

Current repo examples conflict:

- [framework/docs/guides/migration-v1-to-v2.md](framework/docs/guides/migration-v1-to-v2.md) centers `BRIEF.md`, `EXTENSION.md`, and `WAI-Manifest.yaml`
- [templates/spoke/WAI-State.json](templates/spoke/WAI-State.json) centers `WAI-State.json` and `WAI-Spoke/`

Resolved direction:

- `WAI-Spoke/WAI-State.json` is the canonical state model
- older `BRIEF` / `Manifest` / `Extension` material is migration-era compatibility content unless explicitly reintroduced later

### 8.4 Track Storage Needs One Canonical Path Model

Current repo examples conflict:

- [tracks/spec/track-format.md](tracks/spec/track-format.md) implies standalone `track_YYYYMMDD-HHMM.jsonl`
- [WAI-Spoke/commands/wai.md](WAI-Spoke/commands/wai.md) still includes `session-YYYYMMDD-HHMM/track.jsonl`
- current repo data contains both `sessions/track_*.jsonl` and older `session-*/track.jsonl`

Resolved direction:

- canonical path is `WAI-Spoke/sessions/session-YYYYMMDD-HHMM/track.jsonl`
- flat `sessions/track_*.jsonl` remains legacy-read compatibility only

### 8.5 Public Docs Over-Promise Some Unsettled Concepts

Examples:

- [framework/docs/index.md](framework/docs/index.md) describes a richer multi-agent / BRIEF / ledger system than the current repo actually enforces
- GPT conversation introduced `Ozi`, which is now clarified here as a partner identity layer rather than a persistence object

The design should separate:

- what exists today
- what is canonical goal state
- what is still exploratory

## 9. Proposed Resolution Direction

If we follow the GPT conversation faithfully while staying grounded in this repo, the cleanest direction is:

1. Treat `WAI-Spoke/` as the canonical installation root.
2. Keep `hub` / `spoke` as the primary topology.
3. Keep `WAI-State.json` as the canonical state file.
4. Keep session directories with `track.jsonl` as the canonical track layout.
5. Model PEV as linked lugs.
6. Treat signals as high-impact lugs routed through the hub bulletin board.
7. Allow Historian to create candidate lugs automatically, but require user review before planned execution.
8. Treat `Ozi` as partner identity, not as a persistence object.
9. Collapse legacy vocabulary behind compatibility shims rather than preserving multiple first-class models forever.

## 10. Implementation Questions

No major architectural questions remain open from this design pass.

Implementation planning still needs to specify:

1. the exact file path and schema for the framework capability registry
2. the exact spoke file that records adopted capabilities
3. the exact field names for `work.kind`, Historian evidence payloads, and processed hub signal receipts
4. the precise compatibility behavior for any temporary wrappers retained during migration

## 11. Acceptance Criteria For Design Sign-Off

This design is ready for implementation planning when:

1. The remaining implementation questions above are either answered or explicitly deferred.
2. We agree on the canonical models for signals, state, and tracks defined here.
3. We agree on the minimal core object set and the Ozi non-object interpretation.
4. We agree that migration must be compatibility-first rather than big-bang replacement.

Once that is true, the next document should be the implementation design:

- schemas
- file mappings
- migration tooling
- spoke teaching bundle
- rollout and verification plan


---

# Canonical Wheelwright Migration Guide
Source: framework/docs/guides/migration-v1-to-v2.md

# Canonical Wheelwright Migration Guide

This guide covers migration to the canonical Wheelwright object model and behavior.

## Canonical Architecture

The canonical Wheelwright model uses these core objects:

| Component | Purpose | Canonical File |
|-----------|---------|----------------|
| **Wheel** | Top-level network identity | `WAI-State.json` (wheel section) |
| **Hub** | Coordination node | Hub directory with registry |
| **Spoke** | Project-local installation | `WAI-Spoke/` directory |
| **Skills** | Operational protocols | `WAI-Spoke/commands/*.md` |
| **Lugs** | Work/intelligence records | `WAI-Spoke/WAI-Lugs.jsonl` |
| **Sessions** | Bounded work intervals | `WAI-Spoke/sessions/` |
| **Tracks** | Session telemetry | `session-*/track.jsonl` |

## Migration Principles

The canonical migration follows dual-read/single-write compatibility:

1. **Dual-read capability** - Framework can understand both legacy and canonical formats
2. **Single canonical write** - New writes use canonical format only  
3. **Idempotent adoption** - Migration can be safely repeated
4. **Rollback support** - Migration receipts enable safe rollback
5. **Hub visibility** - Hub tracks migration status per spoke

## Migration Process

### Phase 1: Pre-Migration Backup

Create rollback checkpoint before any changes:

```bash
# Create migration checkpoint
cp WAI-Spoke/WAI-State.json WAI-State-pre-canonical-$(date +%Y%m%d-%H%M).json
cp -r WAI-Spoke WAI-Spoke-backup-$(date +%Y%m%d-%H%M)
git add . && git commit -m "Migration checkpoint: pre-canonical state"
```

### Phase 2: Framework Version Verification  

Check framework version compatibility in `WAI-State.json`:

```json
{
  "wheel": {
    "framework_version": "3.0.0",
    "version": "your-project-version"
  }
}
```

**Note:** `framework_version` tracks Wheelwright capability level, `version` tracks your project.

### Phase 3: Migration State Initialization

Add `_migration_state` section to `WAI-State.json` for adoption tracking:

```json
{
  "_migration_state": {
    "_purpose": "Tracks capability adoption and migration receipts for dual-read/single-write compatibility",
    "framework_migrations_applied": [],
    "capability_adoptions": [], 
    "migration_receipts": [],
    "rollback_checkpoints": [],
    "dual_read_capabilities": {
      "state_format": "v3_canonical_with_v1_v2_compat",
      "signal_storage": "canonical_lugs_with_signals_compat",
      "track_storage": "canonical_sessions_with_flat_compat"
    },
    "adoption_markers": {
      "canonical_runtime_baseline": {
        "adopted": false,
        "adopted_at": null,
        "adopted_by": null,
        "receipt_id": null,
        "rollback_checkpoint": null
      },
      "canonical_state_migration": {
        "adopted": false,
        "adopted_at": null,
        "adopted_by": null,
        "receipt_id": null,
        "rollback_checkpoint": null
      }
    },
    "compatibility_notes": "This section enables dual-read during migration while maintaining single canonical write target",
    "last_migration_check": null
  }
}
```

### Phase 4: Signal Migration

**Legacy Pattern:** Separate `WAI-Signals.jsonl` file
**Canonical Pattern:** High-impact lugs (impact >= 8) in `WAI-Lugs.jsonl`

If you have existing signals in `WAI-Signals.jsonl`:

```bash
# Review existing signals
cat WAI-Spoke/WAI-Signals.jsonl

# Each signal becomes a high-impact lug in WAI-Lugs.jsonl
# Manual conversion required - automated tooling pending
```

### Phase 5: Track Storage Migration  

**Legacy Pattern:** Flat `track_*.jsonl` files in `WAI-Spoke/`
**Canonical Pattern:** Session directories `WAI-Spoke/sessions/session-YYYYMMDD-HHMM/track.jsonl`

```bash
# Create canonical session directory structure
mkdir -p WAI-Spoke/sessions/

# Move existing tracks (if any) to session directories
# Update WAI-State.json _session_state.track_path accordingly
```

### Phase 6: State Template Migration

**Legacy Pattern:** Mixed schema generations with BRIEF.md/WAI-Manifest.yaml references
**Canonical Pattern:** WAI-State.json with canonical `wheel` section and `_compatibility` section

1. Ensure `wheel` section is primary with proper `framework_version` separation
2. Move legacy fields to `_compatibility` section  
3. Remove references to BRIEF.md, WAI-Manifest.yaml, EXTENSION.md patterns

## Migration Validation

After migration, verify canonical compliance:

1. **State Structure:** `wheel` section is primary, legacy in `_compatibility`
2. **Signal Storage:** High-impact decisions stored as lugs in `WAI-Lugs.jsonl` 
3. **Track Storage:** Session tracks in canonical directory structure
4. **Framework Version:** Properly separated from project version
5. **Migration Receipts:** All adoptions tracked in `_migration_state`

## Rollback Process

If migration issues occur:

```bash
# Restore from checkpoint
cp WAI-State-pre-canonical-YYYYMMDD-HHMM.json WAI-Spoke/WAI-State.json
rm -rf WAI-Spoke/sessions/  # if canonical sessions were created
git reset --hard HEAD~1  # back to migration checkpoint commit
```

## Post-Migration

- Update `_migration_state.adoption_markers` as capabilities are adopted
- Use dual-read capability during transition period
- Monitor `_migration_state.last_migration_check` for compatibility status

## Deprecated Patterns

These patterns are **incompatible** with canonical Wheelwright:

❌ **BRIEF.md as control plane** - Use WAI-State.json `wheel` section
❌ **WAI-Manifest.yaml** - Use WAI-State.json migration tracking  
❌ **EXTENSION.md** - Use skill system (`WAI-Spoke/commands/`)
❌ **Separate WAI-Signals.jsonl** - Use high-impact lugs in WAI-Lugs.jsonl
❌ **Flat track storage** - Use canonical session directories
❌ **CLI teach/learn commands** - Use wakeup/closeout protocol


---

# Hub Architecture
Source: framework/docs/hub/architecture.md

# Hub Architecture

The Hub is the central node in WAI's hub-and-spoke model. It stores wheel-wide policies, aggregates cross-project learnings, and distributes patterns to all spokes.

## Purpose

The Hub serves three functions:

1. **Policy Authority** - Defines wheel-wide rules via `hub/BRIEF.md`
2. **Learning Aggregator** - Collects high-impact Lugs from all spokes
3. **Pattern Distributor** - Broadcasts learnings back to spokes

## Directory Structure

```
hub/
├── BRIEF.md              # Wheel-wide policies (inherited by all spokes)
├── WAI-Integrity.md      # Data protection contract
├── WAI-Lugs.jsonl        # Hub-level Lugs (patterns, decisions, learnings)
├── WAI-Ledger.jsonl      # Hub commitments ledger
├── registry.yaml         # All registered nodes (spokes + hub)
├── health.yaml           # Hub health status
└── intake/               # Pending signals from spokes
    ├── {node-path}/      # Signals organized by source spoke
    └── processed/        # Processed signals (moved after processing)
```

## BRIEF Cascade

Policies cascade from Hub to spokes:

```
hub/BRIEF.md (wheel-wide policies)
  ↓ Inherited by all projects
Project BRIEF.md (project-specific policies)
  ↓ Inherited by all extensions
Spoke BRIEF.md (spoke-specific policies)
```

**Inheritance Rules:**
- Lower levels can ADD more specific rules
- Lower levels can NARROW rules (make more restrictive)
- Lower levels CANNOT REMOVE or CONTRADICT hub rules

## Intake Processing

Spokes submit high-impact Lugs (impact >= 8) to `hub/intake/`:

1. Spoke creates Lug with impact >= 8
2. Spoke copies Lug to `hub/intake/{spoke-path}/{lug-id}.yaml`
3. Hub wakeup triggers `hub-processor` skill
4. hub-processor reads intake, creates hub Lugs
5. Moves processed signals to `hub/intake/processed/`

## Cross-Spoke Pattern Detection

hub-processor detects patterns across spokes:

- **Recurring diagnosis** - Same issue in 2+ projects → observation Lug
- **Common preference** - Same style preference across spokes → flag for BRIEF update
- **Architecture convergence** - Similar patterns adopted independently → learning Lug
- **Template gap** - Multiple spokes created similar files → suggest framework template

## Hub Health

`hub/health.yaml` tracks:

```yaml
intake_pending: 5          # Unprocessed signals in intake/
oldest_pending: "2026-02-14T00:00:00Z"
spokes_outdated: 2         # Spokes on old framework version
patterns_detected: 3       # Cross-spoke patterns this session
last_processed: "2026-02-14T05:00:00Z"
```

## Hub Wakeup Flow

On hub session start:

1. `hub-processor` skill fires (node_type == "hub")
2. Processes all files in `hub/intake/`
3. Detects cross-spoke patterns
4. Checks spoke health from `hub/registry.yaml`
5. Updates `hub/health.yaml`
6. Reports: "{N} signals processed, {P} patterns detected"
7. Suggests: "Use /wai (Step 9b: auto-teach on closeout) to consolidate learnings"

## Registry

`hub/registry.yaml` tracks all nodes:

```yaml
nodes:
  - path: "wheelwright/hub"
    type: hub
    status: active
    framework_version: "2.0.0"

  - path: "your-org/project-1"
    type: spoke
    status: active
    framework_version: "2.0.0"

  - path: "archive/old-project"
    type: spoke
    status: archived
    framework_version: "2.0.0"
```

## Hub vs Spoke Responsibilities

| Responsibility | Hub | Spoke |
|----------------|-----|-------|
| Define wheel-wide policies | ✓ | ✗ (inherits) |
| Process intake signals | ✓ | ✗ |
| Detect cross-spoke patterns | ✓ | ✗ |
| Track spoke health | ✓ | ✗ |
| Create local Lugs | ✓ | ✓ |
| Submit high-impact signals | ✗ (receives) | ✓ |
| Auto-upgrade framework | ✗ (source) | ✓ (patches) |

## Data Protection

Hub data is protected by `hub/WAI-Integrity.md`:

- `hub/BRIEF.md` - Modifiable via decision Lug + commit
- `hub/WAI-Integrity.md` - Read-only (conductor approval for changes)
- `hub/WAI-Lugs.jsonl` - Append-only
- `hub/intake/` - Append-only (processed moves to processed/)

See [WAI-Integrity.md](../../hub/WAI-Integrity.md) for full protection rules.


---

# Meet Wheelwright
Source: framework/docs/index.md

# Meet Wheelwright

**Wheelwright** is an agent communication protocol for multi-AI collaboration. It's how AI agents talk to each other, show their work, and build institutional memory — without destroying your data.

---

## What Problem Does This Solve?

AI coding agents are powerful, but they have problems:

1. **They don't show their work.** You ask for a feature, code appears, but you don't know what was considered or why.
2. **They don't remember across sessions.** Every conversation starts from zero. No learning, no institutional memory.
3. **They can destroy data.** Agents have restructured folders, deleted files, and broken systems — with no undo button.
4. **They don't collaborate.** One agent can't hand off work to another. No specialization, no division of labor.

Wheelwright fixes this.

---

## How It Works

Wheelwright has two primitives: **Skills** and **Lugs**.

### Skills = Agents with Contracts

A **Skill** is a sub-agent with a defined job. Each Skill declares:
- What it does
- When it fires (on load, on commit, on demand)
- What it reads and writes
- What model it needs (lightweight, standard, advanced)
- What it produces (Lugs)

**Examples:**
- `safe-refactor` (guardian) — checkpoints git before structural changes
- `qc-check` (reviewer) — runs tests, diagnoses failures
- `security-review` (reviewer) — scans for vulnerabilities
- `brief-advisor` (advisor) — detects contradictions between stated policies and actual behavior

Skills are **cheap, specialized agents**. The expensive main coding agent doesn't do everything — it orchestrates sub-agents.

### Lugs = Structured Work Items

A **Lug** is an actionable record. Every diagnosis, prescription, decision, and observation is a Lug.

**Lug types:**
- `diagnosis` — Problem identified ("SQL injection in auth handler")
- `prescription` — Recommended fix ("Parameterize query at line 47")
- `decision` — Judgment call made ("Chose JWT over sessions because...")
- `observation` — Event worth recording ("Test coverage dropped to 73%")
- `task` — Work to be done ("Migrate auth from JWT to sessions")
- `signal` — High-impact Lug (impact ≥ 8) relevant to other projects

**If an agent didn't write a Lug, it didn't happen.**

Lugs are the audit trail. They're how agents show their work, communicate across sessions, and build institutional memory.

---

## Architecture: Hub and Spokes

Wheelwright uses a **hub-and-spoke** model:

```
Hub (shared memory across all projects)
  ├── Spoke: Project A / Extension 1
  ├── Spoke: Project A / Extension 2
  ├── Spoke: Project B / Extension 1
  └── Spoke: Project C / Extension 1
```

- **Hub:** Shared learning, policies, patterns
- **Spoke:** Per-project extension with local state
- **Extension:** A role/lens (CTO, PM, QA, Security, etc.)

**Cross-node communication:** Spokes submit high-impact Lugs to `hub/intake/`. Hub processes them asynchronously and broadcasts learnings back to all spokes.

---

## Data Protection: WAI-Integrity.md

Agents follow **WAI-Integrity.md** rules:

1. **Read-only paths:** Framework files can't be modified directly
2. **Append-only paths:** Lugs and ledgers grow, never shrink
3. **Scoped write access:** Spokes write to their own directory only
4. **Pre-refactor checkpoints:** `safe-refactor` fires before structural changes
5. **Destructive ops require human gate:** Deleting data requires conductor approval

**This exists because a rogue agent destroyed the Hub folder on 2026-02-10.** WAI-Integrity prevents it from happening again.

---

## Session Ledger: Preventing Context Loss

**WAI-Ledger.jsonl** tracks commitments across sessions:

```jsonl
{"type":"request","content":"Add PEV fields to Lug schema","status":"open"}
{"type":"agreement","content":"Will add perceive/execute/verify as optional fields","status":"open"}
{"type":"delivery","content":"350 Lugs upgraded with PEV fields","commit":"73112e9","status":"fulfilled"}
```

**Why it exists:** During WAI v2 migration, token exhaustion caused context loss. The agent reconstructed intent incorrectly, renamed core concepts, skipped 2 phases, and declared completion prematurely. The ledger prevents this by making commitments file-permanent.

On session close: Reconcile open entries, flag unfulfilled commitments.
On resume: Compare agreements against actual codebase state.

---

## Quick Start

1. **Read the framework primer** in your IDE (CLAUDE.md, .cursorrules, etc.)
2. **Explore start-here/** for core concepts
3. **Check your spoke's BRIEF.md** for behavioral rules
4. **Create Lugs as you work** — diagnosis, prescription, decision
5. **Let Skills run automatically** — they're your safety net

---

## For Agents

Wheelwright is a **file-based protocol**. Everything happens through files:

- **Skills** define behavior (YAML files in `framework/skills/`, `hub/skills/`, `{spoke}/skills/`)
- **Lugs** record work (appended to `WAI-Lugs.jsonl`)
- **Ledger** tracks commitments (appended to `WAI-Ledger.jsonl`)
- **BRIEF** defines rules (cascade: hub → project → spoke)
- **WAI-Integrity.md** protects data (read-only, append-only, scoped writes)

**No CLI. No API. Just files.**

Read the specs:
- [Lug Schema Specification](../../WAI-Lug-Schema-Spec.md)
- [Skill Contract Specification](../../WAI-Skill-Contract-Spec.md)
- [Implementation Plan](../../WAI-v2-Implementation-Plan-Revised.md)

---

## Documentation Structure

- **design/** - Goal-state architecture and decisions to align on before implementation
- **start-here/** — Core concepts, quickstart, architecture
- **skills/** — Skill contract, built-in Skills, creating custom Skills
- **lugs/** — Lug schema, types, PEV pattern, impact scoring
- **hub/** — Hub architecture, integrity contract, intake flow
- **spokes/** — Spoke structure, extensions, BRIEF cascade
- **multi-agent/** — Agent colony patterns, model diversification
- **guides/** — Migration guides, cookbooks, enterprise setup
- **reference/** — Field tables, glossary, changelog

---

**WAI v2.0.0** — February 2026

Agents communicate through files. Institutions remember through Lugs.

## Current Canonical Draft

- [Goal-State Design](./design/goal-state-wheelwright.md)


---

# Session Ledger
Source: framework/docs/lugs/session-ledger.md

# Session Ledger

**WAI-Ledger.jsonl** is an append-only log of commitments that survives context loss.

## Origin Story

During WAI v2 migration (2026-02-12), token exhaustion caused context loss mid-migration. The executing agent:

- Reconstructed intent from partial memory
- Renamed PEV fields (perceive/execute/verify → perspective/evidence/verdict)
- Skipped 2 phases (8-9 of 9)
- Declared migration complete

**There was no mechanism to detect the drift** because commitments lived only in conversation context, not in files.

The session ledger fixes this.

## How It Works

### Lifecycle

```
request (conductor) → agreement (agent) → delivery (agent) → verification (conductor)
```

### Entry Types

| Type | Who | Meaning |
|------|-----|---------|
| `request` | conductor | "I want this done" |
| `agreement` | agent | "I will do this, here's how" |
| `clarification` | either | "Do you mean X or Y?" / "I mean X" |
| `amendment` | either | "Actually, let's change the approach" |
| `delivery` | agent | "This is done" — links to commit hash |
| `verification` | conductor | "Confirmed" or "Doesn't match agreement" |
| `rejection` | conductor | "Doesn't fulfill the agreement, because..." |

### Schema

```jsonl
{"id":"led-2026-02-12-001","timestamp":"2026-02-12T14:00:00Z","session_id":"session-001","type":"request","content":"Migrate Lug schema to v2 with PEV fields","source":"conductor","status":"open"}
{"id":"led-2026-02-12-002","timestamp":"2026-02-12T14:05:00Z","session_id":"session-001","type":"agreement","content":"Will add perceive/execute/verify as optional fields","source":"agent","references":"led-2026-02-12-001","status":"open"}
{"id":"led-2026-02-12-003","timestamp":"2026-02-12T15:00:00Z","session_id":"session-001","type":"delivery","content":"350 Lugs upgraded, PEV fields added","source":"agent","references":"led-2026-02-12-001","commit":"73112e9","status":"fulfilled"}
```

## Integration Points

### On Session Start (Wakeup)

1. Read WAI-Ledger.jsonl
2. Filter for status: "open"
3. Surface in composite briefing: "Open commitments from prior sessions"

### On Session Close (Closeout)

1. session-observer reconciles open ledger entries
2. For each: was it delivered? Create delivery entry with commit hash
3. Surface unfulfilled commitments: "These requests are still open"

### On Context Loss / Resume

1. New agent reads ledger
2. Compares open agreements against actual state of codebase
3. Identifies drift: "Agreement says X, but codebase has Y"
4. Creates diagnosis Lug for each discrepancy

## Use Cases

### Prevents Premature Completion

**Scenario:** Conductor asks for 9 phases, agent delivers 7 and says "complete"

**Ledger:** Has 9 request entries. Only 7 have delivery entries.

**Closeout:** Flags 2 open commitments remain. Catches premature completion.

### Detects Spec Drift

**Scenario:** Agreement says "perceive/execute/verify", code has "perspective/evidence/verdict"

**On Resume:** Ledger shows the agreement. New agent reads code, detects mismatch, creates diagnosis Lug.

### Survives Context Loss

**Scenario:** Token exhaustion mid-session

**Recovery:** Commitments are file-permanent. New agent reads ledger, sees what was agreed to, verifies against codebase.

## Integrity Rules

Per WAI-Integrity.md:

- **Append-only:** Never delete ledger entries
- **Status progression:** open → fulfilled / amended / rejected
- **Amendments create new entries:** Don't modify old entries
- **Reconciliation is mandatory:** Part of closeout ceremony

## For Agents

- Write ledger entries as you make commitments
- Use the ledger to track multi-session work
- On resume, read the ledger FIRST to understand prior commitments
- Flag unfulfilled commitments at session close

The ledger is the parity check. Use it.


---

# Multi-Agent Colony Patterns
Source: framework/docs/multi-agent/colony-patterns.md

# Multi-Agent Colony Patterns

WAI enables agent colonies: groups of specialized agents working together under a conductor's direction.

## The Colony Model

```
Conductor (Human)
    ↓
Main Agent (Expensive - Sonnet/Opus)
    ↓ orchestrates
┌────────────────────────────────────┐
│ Skill Agents (Cheap - Haiku/Flash) │
├────────────────────────────────────┤
│ safe-refactor │ qc-check │ review │
│ hub-watcher   │ session-observer  │
└────────────────────────────────────┘
```

## Why Colonies?

**Problem:** Expensive models are good at everything but costly.
**Solution:** Use expensive models for hard problems, cheap models for routine checks.

**Cost comparison:**
- Opus 4.5: $15/M input, $75/M output
- Sonnet 4.5: $3/M input, $15/M output
- Haiku 3.5: $0.25/M input, $1.25/M output

Running safe-refactor with Haiku costs 60x less than Opus. For routine git checkpoints, Haiku is sufficient.

## Skill Roles

### Guardian (Pre-emptive Protection)
**Model:** Lightweight (Haiku)
**Trigger:** Before risky operations
**Examples:**
- `safe-refactor` - Git checkpoint before structural changes
- `backup-check` - Verify backups before deletions

### Reviewer (Quality Assurance)
**Model:** Standard (Sonnet) or Lightweight (Haiku)
**Trigger:** After changes
**Examples:**
- `qc-check` - Run tests, report failures
- `security-review` - Scan for vulnerabilities
- `lint-check` - Code style validation

### Advisor (Guidance)
**Model:** Standard (Sonnet)
**Trigger:** When thresholds crossed
**Examples:**
- `complexity-advisor` - Warn when task is complex
- `context-advisor` - Warn when context is filling up
- `signal-advisor` - Auto-submit high-impact Lugs

### Watcher (Observation)
**Model:** Lightweight (Haiku)
**Trigger:** Session events
**Examples:**
- `session-observer` - Track events, create closeout summary
- `hub-watcher` - Check hub for updates on wakeup
- `hub-processor` - Process intake on hub wakeup

## Orchestration Flow

```
User: "Refactor auth module to use sessions"

1. Main Agent receives task
2. safe-refactor fires (guardian, lightweight)
   → Creates checkpoint commit
3. Main Agent plans and implements changes
4. qc-check fires (reviewer, standard)
   → Runs tests, finds failure
   → Creates diagnosis Lug
5. Main Agent fixes based on diagnosis
6. security-review fires (reviewer, advanced)
   → Scans auth code
   → Creates 2 diagnosis Lugs
7. Main Agent addresses security issues
8. signal-advisor fires (advisor, lightweight)
   → Detects high-impact Lugs
   → Submits to hub/intake/
9. User triggers closeout
10. session-observer fires (watcher, lightweight)
    → Reconciles ledger
    → Creates session summary Lug
```

## Model Selection Guidelines

| Task Type | Model Tier | Examples |
|-----------|------------|----------|
| File existence, git status | Lightweight | safe-refactor, hub-watcher |
| Code analysis, test interpretation | Standard | qc-check, security-review |
| Architecture decisions, complex reasoning | Advanced | brief-advisor, complexity-advisor |

## Communication via Lugs

Skills communicate through Lugs, not direct messages:

```
security-review creates:
  Lug: {type: "diagnosis", title: "SQL injection in auth handler", impact: 9}

Main Agent reads Lug, addresses issue

Main Agent creates:
  Lug: {type: "prescription", title: "Parameterized queries", diagnosis_id: "..."}

On resolution:
  Lug updated: {status: "resolved", resolution: "accepted", commit: "abc123"}
```

## Cross-Session Learning

Skills learn from past decisions:

```
security-review checks:
  "Has this pattern been seen before?"
  → Reads past diagnosis Lugs
  → "Similar issue in auth handler was fixed with parameterized queries"
  → Includes context in new diagnosis
```

**Decision Lugs feed the apprenticeship loop:**
- Sub-agents reference past decision Lugs
- Learn conductor's risk tolerance, quality standards, priorities
- Adjust recommendations based on patterns

## Model Diversification

Mix providers for resilience and capability:

```yaml
skills:
  safe-refactor:
    model: haiku  # Fast, cheap
  qc-check:
    model: sonnet  # Good code analysis
  security-review:
    model: opus  # Deep reasoning
  hub-watcher:
    model: gemini-flash  # Alternative provider
```

Benefits:
- No single provider dependency
- Match model to task requirements
- Cost optimization

## Anti-Patterns

### ❌ Expensive Model for Routine Checks
```yaml
safe-refactor:
  model: opus  # Overkill for git status + commit
```

### ❌ Cheap Model for Complex Reasoning
```yaml
architecture-advisor:
  model: haiku  # Can't handle nuanced decisions
```

### ❌ Direct Communication Instead of Lugs
```python
# Bad: Skills talking directly
main_agent.message(security_review, "Found a bug")

# Good: Skills communicate via Lugs
create_lug(type="diagnosis", title="Found SQL injection")
```

### ❌ No Conductor Gate for Destructive Actions
```yaml
file-deleter:
  trigger: auto
  # Missing: requires_approval: true
```

## Best Practices

1. **Use the cheapest model that works** - Don't pay Opus prices for Haiku tasks
2. **Create Lugs for everything** - Communication happens through files
3. **Let skills run automatically** - Trust the trigger conditions
4. **Review high-impact findings** - Conductor makes final decisions
5. **Learn from decisions** - Reference past decision Lugs in recommendations


---

# Glossary
Source: framework/docs/reference/glossary.md

# Glossary

## Core Concepts

### Lug
An actionable record representing decomposed, meaningful work. Every diagnosis, prescription, decision, and observation is a Lug. If an agent didn't write a Lug, it didn't happen.

### Skill
A sub-agent with a defined contract. Each skill declares what it does, when it fires, what model it needs, and what it produces.

### Hub
The central node in WAI's hub-and-spoke model. Stores wheel-wide policies, aggregates cross-project learnings, distributes patterns to spokes.

### Spoke
A WAI extension for a specific project. Inherits policies from Hub, maintains local state, Lugs, and configuration.

### Conductor
The human directing the agent colony. Makes final decisions, approves destructive operations, provides strategic direction.

### Wheel
A complete WAI installation: one hub + multiple spokes. Named after the framework (Wheelwright).

### Node
Any component in the WAI network. Can be a hub or a spoke.

### BRIEF
Behavioral rules document. Defines Always/Never/When Uncertain rules. Cascades from hub to project to spoke.

### EXTENSION
Identity document for a spoke. Defines Role, Lens, Primary Focus, Skills Loaded, Offers, and Subscriptions.

### Manifest
Node configuration file (WAI-Manifest.yaml). Contains node_type, node_path, framework_version, skills_loaded, etc.

### Ledger
Session commitment tracking (WAI-Ledger.jsonl). Append-only log of requests, agreements, and deliveries.

### Intake
Hub directory (hub/intake/) where spokes submit high-impact Lugs for processing.

---

## Lug Types

### Task
Work to be done. "Migrate auth from JWT to sessions"

### Diagnosis
Problem identified by a sub-agent. "SQL injection in auth handler"

### Prescription
Recommended fix attached to a diagnosis. "Parameterize query at line 47"

### Decision
A judgment call made by the conductor. "Accepted risk on X because Y"

### Observation
Event or pattern worth recording. "Test coverage dropped to 73%"

### Preference
Communication style or workflow preference. "User prefers terse confirmations"

### Signal
High-impact Lug (impact >= 8) relevant to other nodes. Submitted to hub/intake/.

### Update
Framework or template version change notification.

### Session
Session synthesis — human-readable summary of a work session.

---

## Skill Roles

### Guardian
Pre-emptive protection. Fires before risky operations to create safety checkpoints.
Example: `safe-refactor`

### Reviewer
Quality assurance. Fires after changes to validate correctness.
Example: `qc-check`, `security-review`

### Advisor
Guidance and warnings. Fires when thresholds crossed or patterns detected.
Example: `complexity-advisor`, `context-advisor`

### Watcher
Observation and synthesis. Fires on session events to track and summarize.
Example: `session-observer`, `hub-watcher`

---

## PEV Pattern

**P**erceive / **E**xecute / **V**erify

Optional structured execution context for complex Lugs:

### Perceive
What to look at and what "wrong" looks like.
- `look_at`: Files/patterns to examine
- `current_state`: What's wrong now
- `success_state`: What "fixed" looks like

### Execute
What actions to take and constraints.
- `approach`: How to fix
- `constraints`: What not to change
- `avoid`: Patterns to avoid

### Verify
How to confirm success.
- `commands`: Tests to run
- `expected_output`: What success looks like
- `manual_check`: Human verification steps

---

## Impact Scoring

### 1-3: Local
Visible only within the creating node.
"Refactored helper function"

### 4-7: Project-wide
Visible to other extensions in the same project.
"API contract changed"

### 8-10: Wheel-wide (Signal)
Copied to Hub intake, visible to all spokes.
"Architecture pattern applicable across projects"

---

## Lifecycle States

### Lug Lifecycle
```
draft → published → acknowledged → in_progress → resolved
```

### Ledger Entry Lifecycle
```
request → agreement → delivery → verification
            ↗               ↗
     clarification    amendment
```

---

## File Types

### .jsonl
JSON Lines format. One JSON object per line. Used for WAI-Lugs.jsonl, WAI-Ledger.jsonl.

### .yaml
YAML format. Used for skills (*.yaml), manifests (WAI-Manifest.yaml), registry (registry.yaml).

### .md
Markdown format. Used for documentation, BRIEF.md, EXTENSION.md, specs.

---

## Cascade

The inheritance pattern where policies flow from hub to spoke:

```
hub/BRIEF.md (wheel-wide)
  ↓ inherited by
Project BRIEF.md (project-specific)
  ↓ inherited by
Spoke BRIEF.md (spoke-specific)
```

Lower levels can ADD and NARROW, but cannot REMOVE or CONTRADICT.

---

## Integrity Rules

### Read-Only
Files that cannot be modified. Framework core files.

### Append-Only
Files where content can only be added, never deleted. WAI-Lugs.jsonl, WAI-Ledger.jsonl.

### Scoped Write
Files that can be modified but only within defined scope. Spoke writes only to its own directory.

### Human Gate
Operations requiring explicit conductor approval. Destructive operations (delete, reset).

---

## Model Tiers

### Lightweight
Fast, cheap models for simple operations.
Examples: Haiku, Gemini Flash

### Standard
Balanced models for code analysis.
Examples: Sonnet, Gemini Pro

### Advanced
Expensive models for complex reasoning.
Examples: Opus, o1-pro


---

# Installation & Setup
Source: framework/docs/setup/installation.md

# Installation & Setup

## Prerequisites

- Git repository (local or remote)
- AI coding agent (Claude Code, Cursor, etc.)
- Basic familiarity with YAML and JSONL formats

## Quick Setup (New Project)

### 1. Install WAI Framework

Clone the Wheelwright framework:

```bash
git clone https://github.com/wheelwright-ai/framework.git
cd framework
```

### 2. Create Your Spoke

```bash
mkdir -p /path/to/your-project/WAI-Spoke
cd /path/to/your-project
```

Copy spoke templates:

```bash
cp framework/templates/WAI-Spoke/* ./WAI-Spoke/
cp framework/templates/BRIEF.md ./BRIEF.md
cp framework/templates/EXTENSION.md ./EXTENSION.md
```

### 3. Configure Your Spoke

Edit `WAI-Spoke/WAI-Manifest.yaml`:

```yaml
node_type: spoke
node_path: "your-org/your-project"
framework_version: "2.0.0"
hub_lug_cursor: null
skills_loaded:
  - safe-refactor
  - session-observer
last_session: null
outbound_pending: []
```

Edit `EXTENSION.md`:

```markdown
## Identity

**Role:** [Your role - CTO, PM, QA, etc.]
**Lens:** [Your perspective - what you focus on]

**Primary Focus:**
- [Key responsibility 1]
- [Key responsibility 2]
```

Edit `BRIEF.md`:

```markdown
# BRIEF — your-project

**BRIEF Cascade:** This file inherits rules from hub/BRIEF.md

## Always
- [Non-negotiable rule 1]
- [Non-negotiable rule 2]

## Never
- [Prohibited action 1]
- [Prohibited action 2]

## When Uncertain
- [Clarification source 1]
- [Clarification source 2]
```

### 4. Connect to Hub (Optional)

If you have a central hub for cross-project learning:

Edit `WAI-Spoke/WAI-State.json` (if exists) or create it:

```json
{
  "hub_path": "/path/to/wheelwright-hub",
  "subscriptions": ["hub:framework:*", "hub:pattern:*"]
}
```

### 5. Load Framework in Your IDE

Add to `.cursorrules`, `CLAUDE.md`, or equivalent:

```markdown
# Wheelwright Framework

Load WAI context on session start:
1. Read BRIEF.md (behavioral rules)
2. Read EXTENSION.md (role and lens)
3. Read WAI-Spoke/WAI-Manifest.yaml (framework config)
4. Check WAI-Spoke/WAI-Ledger.jsonl for open commitments

Skills auto-fire based on triggers. Let them run.

Create Lugs as you work (diagnosis, prescription, decision).
```

## Hub Setup (Optional - For Cross-Project Learning)

### 1. Create Hub Directory

```bash
mkdir -p /path/to/wheelwright-hub
cd /path/to/wheelwright-hub
```

### 2. Initialize Hub Structure

```bash
cp -r framework/hub/* ./
```

This creates:
- `hub/BRIEF.md` (wheel-wide policies)
- `hub/WAI-Integrity.md` (data protection contract)
- `hub/registry.yaml` (all registered nodes)
- `hub/health.yaml` (hub health status)
- `hub/intake/` (pending signals from spokes)
- `hub/WAI-Lugs.jsonl` (hub learning log)

### 3. Register Your Spokes

Edit `hub/registry.yaml`:

```yaml
nodes:
  - path: "wheelwright/hub"
    type: hub
    status: active
    framework_version: "2.0.0"
    description: "Central Hub"

  - path: "your-org/project-1"
    type: spoke
    status: active
    framework_version: "2.0.0"
    description: "Project 1 description"

  - path: "your-org/project-2"
    type: spoke
    status: active
    framework_version: "2.0.0"
    description: "Project 2 description"
```

## Verification

After setup, verify WAI is working:

### Spoke Verification

Run this prompt in your spoke project:

```
Verify WAI v2 working:
1. Does BRIEF.md mention cascade or hub inheritance?
2. What's my role AND lens from EXTENSION.md?
3. What's my node_path from WAI-Manifest.yaml?
4. Does WAI-Ledger.jsonl exist and is it append-only?
5. Does skills/ directory exist?
6. Create a test ledger entry and show it
```

Expected output: All checks pass, test entry created.

### Hub Verification (if using hub)

Run this in hub project:

```
Hub health check:
1. Does hub/registry.yaml exist with all spokes listed?
2. Does hub/BRIEF.md exist with wheel-wide policies?
3. Does hub/WAI-Integrity.md exist with data protection rules?
4. Does hub/intake/ directory exist?
5. How many spokes are registered?
```

Expected output: All files exist, registry shows your spokes.

## Troubleshooting

### "Framework files not found"

**Symptom:** Agent can't find templates or skills
**Solution:** Verify `framework_version` in WAI-Manifest.yaml matches installed version

### "Hub not accessible"

**Symptom:** hub-watcher reports connection failure
**Solution:** Check `hub_path` in WAI-State.json points to correct absolute path

### "Skills not firing"

**Symptom:** safe-refactor doesn't run before changes
**Solution:** Verify skills are listed in WAI-Manifest.yaml `skills_loaded` array

### "Documentation drift flagged"

**Symptom:** Closeout warns about doc updates needed
**Solution:** This is expected - update docs before closing session

## Next Steps

- Read [core-concepts.md](../start-here/core-concepts.md) to understand Skills and Lugs
- Explore [skills documentation](../skills/built-in/) to see available skills
- Check [use-cases.md](./use-cases.md) for common scenarios
- Review [hub-architecture.md](../hub/architecture.md) if using cross-project learning


---

# Common Use Cases
Source: framework/docs/setup/use-cases.md

# Common Use Cases

## Solo Developer with Multiple Projects

**Scenario:** You maintain 5 different projects and want patterns from one to benefit others.

**Setup:**
- Hub at `~/wheelwright-hub`
- 5 spokes (one per project)
- Each spoke submits high-impact learnings to hub/intake/
- Hub processes patterns, broadcasts back to all spokes

**Example:**
1. Project A discovers SQL injection pattern, creates diagnosis Lug (impact: 9)
2. Spoke auto-submits to hub/intake/
3. On next hub wakeup, hub-processor detects pattern
4. Creates hub observation Lug: "SQL injection pattern seen in Project A"
5. Project B wakes up, hub-watcher pulls this signal
6. Project B agent sees warning about SQL injection, checks its own code

**Value:** Learn once, apply everywhere.

---

## Team with Shared Coding Standards

**Scenario:** Team of 5 developers, want consistent code quality across all repos.

**Setup:**
- Centralized hub with team-wide policies in hub/BRIEF.md
- Each developer's projects are spokes inheriting hub policies
- QA skill runs on all commits, creates diagnosis Lugs

**Hub BRIEF.md:**
```markdown
## Always
- Maintain 80% test coverage
- Run safe-refactor before structural changes
- Create decision Lugs for architectural choices

## Never
- Deploy without tests passing
- Commit secrets or credentials
- Skip security review on auth changes
```

**Value:** Policies cascade to all projects. No copy-paste, no drift.

---

## Long-Running Migration

**Scenario:** Migrating auth from JWT to sessions across 20 routes over 3 weeks.

**Setup:**
- Use WAI-Ledger.jsonl to track commitments across sessions
- Break work into 20 task Lugs (one per route)
- Each session: agent reads ledger, sees what's still open

**Ledger entries:**
```jsonl
{"type":"request","content":"Migrate all 20 routes from JWT to sessions","status":"open"}
{"type":"agreement","content":"Will migrate 5 routes per week, starting with public routes","status":"open"}
{"type":"delivery","content":"Routes 1-5 migrated","commit":"abc123","status":"fulfilled"}
{"type":"delivery","content":"Routes 6-10 migrated","commit":"def456","status":"fulfilled"}
...
```

**Closeout each session:** Reconciles ledger, shows "10 routes done, 10 remaining"

**Value:** No context loss. Work survives across weeks, token limits, crashes.

---

## Multi-Agent Collaboration

**Scenario:** Main agent orchestrates, specialist skills handle specific domains.

**Agents:**
- **Main agent** (expensive, Sonnet 4.5): Writes code, makes decisions
- **safe-refactor** (cheap, Haiku): Checkpoints git before structural changes
- **qc-check** (medium, Sonnet 3.5): Runs tests, diagnoses failures
- **security-review** (expensive, Opus 4.5): Scans for vulnerabilities on auth changes

**Workflow:**
1. Main agent plans change: "Refactor auth module"
2. safe-refactor fires automatically (pre-refactor trigger)
3. Main agent makes changes
4. qc-check fires on commit, finds test failure
5. Main agent fixes based on diagnosis Lug
6. security-review fires (auth code changed)
7. security-review creates 2 diagnosis Lugs (SQL injection, session fixation)
8. Main agent addresses both issues

**Value:** Specialization. Cheap agents do repetitive checks, expensive agents solve hard problems.

---

## Institutional Memory (Decision Tracking)

**Scenario:** 6 months from now, you need to know "why did we choose X over Y?"

**Setup:**
- Create decision Lugs whenever making architectural choices
- Include alternatives_considered with reasoning

**Example decision Lug:**
```json
{
  "type": "decision",
  "title": "Use JWT tokens instead of sessions",
  "alternatives_considered": [
    {
      "option": "Server-side sessions",
      "chosen": false,
      "reasoning": "Requires sticky sessions with load balancer, adds state complexity"
    },
    {
      "option": "JWT tokens",
      "chosen": true,
      "reasoning": "Stateless, works with horizontal scaling, simpler deployment"
    }
  ],
  "summary": "Chose JWT for stateless auth. Trade-off: token revocation is harder but worth it for scaling simplicity."
}
```

**6 months later:**
- Agent reads past decision Lugs
- Sees JWT was chosen specifically for horizontal scaling
- When refactoring auth, preserves this requirement

**Value:** Institutional memory. Decisions persist beyond any single developer or session.

---

## Preventing Data Loss

**Scenario:** Agent previously destroyed Hub folder by restructuring files.

**Setup:**
- WAI-Integrity.md defines data protection rules
- safe-refactor fires before structural changes
- Destructive ops require human gate

**Protection layers:**
1. **Read-only paths:** Framework files can't be modified
2. **Append-only paths:** WAI-Lugs.jsonl and WAI-Ledger.jsonl only grow
3. **Scoped writes:** Spokes write to their own directory only
4. **Pre-refactor checkpoint:** Git commit before structural changes
5. **Human gate:** Deleting data requires explicit approval

**What prevented:**
- Hub folder deletion (read-only)
- Lug file truncation (append-only)
- Cross-project file modification (scoped writes)

**Value:** Safety net. Agents can't accidentally destroy critical data.

---

## E2E Benchmarking (Performance Validation)

**Scenario:** Want to prove WAI reduces token usage vs baseline agents.

**Setup:**
- Benchmark projects at benchmarks/projects/small and benchmarks/projects/medium
- Each has reference documentation (large, unnecessary files)
- Compare baseline (loads everything) vs Wheelwright (selective loading)

**Results:**
- **Small tier:** 3900.7x token efficiency (24 files → 3 files, 20MB → 3.3KB)
- **Medium tier:** 7833.1x token efficiency (59 files → 5 files, 100MB → 11KB)
- **Critical test:** Wheelwright NEVER loads reference files (0/10 loaded)

**How it works:**
- WAI-Manifest.yaml defines file_load_policy:
  ```yaml
  file_load_policy:
    load_always: ["src/formatters/data.py"]
    load_on_demand: ["src/utils/logger.py"]
    never_load: ["reference/**/*"]
  ```
- Agent respects policy, loads only necessary files
- Massive token savings, faster responses

**Value:** Quantifiable proof of efficiency gains.

---

## Cross-Project Pattern Detection

**Scenario:** Want to know if same bug appears in multiple projects.

**Setup:**
- Hub aggregates signals from all spokes
- hub-processor detects recurring patterns

**Flow:**
1. Project A: security-review finds SQL injection, creates Lug (impact: 9)
2. Project A submits to hub/intake/
3. Project B: security-review finds same pattern, submits to hub
4. Hub wakeup: hub-processor sees 2 spokes with same diagnosis
5. Creates hub observation Lug: "SQL injection pattern detected in 2 projects"
6. Suggests: "Promote parameterized query helper to framework template"

**Value:** Learn from mistakes across ALL projects, not just one.

---

## Communication Style Consistency

**Scenario:** Want all agents to respond in consistent format (terse, numbered lists).

**Setup:**
- hub/BRIEF.md Communication Style section defines format rules
- All spokes inherit via cascade
- preference Lugs capture style feedback

**hub/BRIEF.md:**
```markdown
### Communication Style

**Response Format:**
- Lead with the answer, then supporting details
- Use numbered lists for multi-part answers
- Verification responses: max 10 lines total
- No verbose explanations unless errors found

**Tone Matching:**
- Mirror user's verbosity (terse question → terse answer)
- Match technical depth to question specificity
```

**User feedback:** "Too verbose, just give me bullets"
**Agent creates:** preference Lug documenting this
**Later:** Preference consolidated into hub/BRIEF.md via /wai (Step 9b: auto-teach on closeout)

**Value:** Agents learn your communication preferences, apply consistently.


---

# Built-In Skills
Source: framework/docs/skills/built-in-skills.md

# Built-In Skills

WAI includes built-in skills for common agent operations. All skills follow the [Skill Contract Specification](../../WAI-Skill-Contract-Spec.md).

## Core Skills

### safe-refactor (Guardian)

**Purpose:** Create git checkpoint before structural changes

**Trigger:** Before file restructuring, deletions, or large refactors

**Model:** Lightweight (Haiku)

**Behavior:**
1. Detect structural change intent (move files, delete directories, rename modules)
2. Run `git status` to see current state
3. Create checkpoint commit: `git commit -m "checkpoint: before [operation]"`
4. Allow operation to proceed
5. If operation fails, user can easily revert to checkpoint

**Why it exists:** An agent once deleted the entire Hub folder by restructuring files without a checkpoint. This skill prevents data loss.

**Output:** Checkpoint commit hash

**Use cases:**
- Moving `src/` to `app/`
- Deleting deprecated modules
- Renaming package structure
- Large multi-file refactors

---

### session-observer (Watcher)

**Purpose:** Track session events and create synthesis at closeout

**Trigger:**
- session_start (passive observation)
- session_end (active synthesis)
- pre_closeout (ledger reconciliation)

**Model:** Lightweight (Haiku)

**Behavior:**

**On session_end:**
1. **Ledger Reconciliation:**
   - Read WAI-Ledger.jsonl
   - Filter entries with status: "open"
   - For each: check if delivered this session (matching commit exists)
   - Create delivery entries for fulfilled commitments
   - Flag unfulfilled commitments

2. **Documentation Check:**
   - If commits modified framework files (hub/BRIEF.md, *-Spec.md, templates/*, skills/*)
   - AND docs/ directory exists
   - Flag: "Documentation may need updates"
   - List files changed that affect docs
   - Suggest: "Update README, regenerate llms-full.txt, update guides"

3. **Session Synthesis:**
   - Read all observations from current session
   - Read Lugs created this session
   - Read commits made (git log since session start)
   - Create session summary Lug with:
     - High-impact events (impact >= 8)
     - New Lugs created (count by type)
     - Commits made (count, summary)
     - Incomplete work (Lugs still in-progress)
     - Unfulfilled commitments (from ledger)
     - Documentation updates needed (if applicable)

**Output:** Session summary Lug (type: observation)

**Use cases:**
- End-of-session closeout
- Context loss prevention (ledger reconciliation)
- Documentation drift detection
- Progress tracking across sessions

---

### hub-watcher (Watcher - Spoke-Only)

**Purpose:** Monitor Hub for framework updates and cross-node signals

**Trigger:** session_start (automatic on spoke wakeup)

**Conditions:** ONLY runs if node_type == "spoke" (skips if node_type == "hub")

**Model:** Lightweight (Haiku)

**Behavior:**
1. **Check node_type:** If "hub", skip (hub doesn't watch itself)
2. **Framework version check:**
   - Read hub/registry.yaml - get hub framework_version
   - Compare with spoke framework_version in WAI-Manifest.yaml
   - If patch update (2.0.0 → 2.0.1) AND no breaking changes:
     * Auto-apply: Update spoke WAI-Manifest.yaml
     * Pull new templates from framework/templates/
     * Create update Lug documenting changes
     * Report: "Auto-upgraded to v{X} (patch update)"
   - If minor/major update (2.0.0 → 2.1.0 or 3.0.0):
     * Notify agent: "Hub has v{X}, you're on v{Y}"
     * Read hub update Lugs to show what changed
     * Suggest: "Review changes and run /framework-update when ready"
     * Flag: Breaking changes require review

3. **Pending signals check:**
   - Check hub/intake/ for unprocessed signals addressed to this spoke
   - Count: how many high-impact signals pending
   - Auto-pull signals relevant to this spoke (matching subscription patterns)
   - Create local Lugs with source_id pointing to hub signals
   - Suggest: "Review and acknowledge signals"

4. **Hub health check:**
   - Check hub/health.yaml for:
     - intake_pending > 0
     - oldest_pending timestamp
   - If stale intake (oldest_pending > 7 days):
     - Report: "Hub has stale intake"
     - Suggest: "Run hub maintenance"

**Output:**
- Framework update status
- Pending signals count and titles
- Hub health issues (if any)
- Recommendations for conductor

**Use cases:**
- Automatic patch upgrades (zero user action)
- Framework update notifications (minor/major versions)
- Cross-spoke learning (pull patterns from hub)
- Hub health monitoring

---

### hub-processor (Watcher - Hub-Only)

**Purpose:** Process hub/intake/, detect cross-spoke patterns, check spoke health

**Trigger:** session_start (automatic on hub wakeup)

**Conditions:** ONLY runs if node_type == "hub" (skips if node_type == "spoke")

**Model:** Lightweight (Haiku)

**Behavior:**
1. **Check node_type:** If "spoke", skip (spokes don't process intake)

2. **Process Intake:**
   - Read all files in hub/intake/**/*.yaml
   - For each signal:
     * Parse Lug content (id, type, impact, node, summary)
     * Check if already processed (exists in hub/WAI-Lugs.jsonl with same source_id)
     * If new: Create hub Lug with source_id pointing to spoke Lug
     * Move to hub/intake/processed/{node-path}/{lug-id}.yaml
   - Count: signals processed, duplicates skipped

3. **Aggregate Patterns:**
   - Group signals by category (security, performance, architecture, preference, etc.)
   - Look for recurring patterns across spokes:
     * Same diagnosis appearing in 2+ projects → create observation Lug
     * Similar decisions made independently → learning Lug
     * Common preferences emerging → flag for hub/BRIEF.md consolidation
   - Create observation Lugs for patterns with 2+ instances

4. **Check Spoke Health:**
   - Read hub/registry.yaml for all registered spokes
   - For each spoke:
     * Check if framework_version matches hub version
     * Check last_session timestamp (stale if >30 days)
     * Check outbound_pending count (stuck signals?)
   - Create observation Lugs for health issues

5. **Update Hub Health:**
   - Write hub/health.yaml:
     * intake_pending: count of unprocessed signals
     * oldest_pending: timestamp of oldest signal
     * spokes_outdated: count of spokes on old framework version
     * patterns_detected: count of cross-spoke patterns this session

**Output:**
- "{N} signals processed from {M} spokes"
- "{P} patterns detected across spokes"
- "{S} spokes need framework updates"
- "Use /wai (Step 9b: auto-teach on closeout) to consolidate learnings into framework"

**Pattern detection examples:**
- **Recurring diagnosis:** 3 spokes found same SQL injection → recommend framework guidance
- **Common preference:** Multiple spokes have same communication style → consolidate into hub/BRIEF.md
- **Architecture convergence:** 2+ spokes adopted similar pattern → document as learning
- **Template gap:** Multiple spokes created similar custom files → promote to framework template

**Use cases:**
- Cross-spoke learning aggregation
- Pattern detection across projects
- Hub health monitoring
- Framework evolution feedback loop

---

## Advisor Skills (Coming Soon)

### complexity-advisor

**Purpose:** Warn when task complexity exceeds threshold

**Trigger:** Task analysis (2+ files OR 6+ steps)

**Output:** Diagnosis Lug if complexity is high

---

### stewardship-advisor

**Purpose:** Detect scope drift (out-of-scope work)

**Trigger:** Work item analysis

**Output:** Warning if work doesn't match stated scope

---

### context-advisor

**Purpose:** Warn when token usage approaches limits

**Trigger:** Context analysis at 60%, 80%, 90% thresholds

**Output:** Warning with recommendations to reduce context

---

### signal-advisor

**Purpose:** Auto-submit high-impact Lugs to hub/intake/

**Trigger:** Lug creation with impact >= 8

**Output:** Signal submission to hub

---

## Creating Custom Skills

See [WAI-Skill-Contract-Spec.md](../../WAI-Skill-Contract-Spec.md) for full specification.

**Minimal skill template:**
```yaml
name: my-skill
role: reviewer  # guardian | reviewer | advisor | watcher
model: lightweight  # lightweight | standard | advanced
description: "What this skill does"

trigger:
  events:
    - on_commit
  conditions:
    - "files match pattern"

scope:
  reads:
    - "src/**/*.py"
  writes:
    - "WAI-Lugs.jsonl"

behavior:
  on_trigger: |
    1. Read files matching trigger
    2. Analyze for issues
    3. Create diagnosis Lugs if problems found

output:
  success:
    type: "check_complete"
    data:
      issues_found: 0
  findings:
    type: "issues_detected"
    data:
      lugs: ["lug-001", "lug-002"]
```

**Best practices:**
- Use lightweight models for simple checks (git status, file exists)
- Use standard models for code analysis
- Use advanced models only for complex reasoning (architecture decisions, security analysis)
- Always produce Lugs (diagnosis, prescription, observation)
- Include use_cases in skill definition for clarity
- Test skills with realistic scenarios before deploying

## Skill Orchestration

Main agent orchestrates skills:
1. Reads skill definitions from `framework/skills/`, `hub/skills/`, `{spoke}/skills/`
2. Matches triggers to current operation
3. Fires applicable skills in order: guardians → reviewers → advisors → watchers
4. Collects Lugs from each skill
5. Presents findings to conductor
6. Executes based on conductor decisions

**Example flow:**
```
User: "Refactor auth module to use sessions instead of JWT"

1. safe-refactor fires (guardian, pre-refactor trigger)
   → Creates checkpoint commit

2. Main agent refactors code

3. qc-check fires (reviewer, on_commit trigger)
   → Runs tests
   → Creates diagnosis Lug: "Test failure in /tests/auth/test_login.py"

4. Main agent fixes test failure

5. security-review fires (reviewer, auth code changed)
   → Scans for vulnerabilities
   → Creates diagnosis Lug: "Session fixation vulnerability in session creation"

6. Main agent addresses security issue

7. signal-advisor fires (advisor, high-impact Lug created)
   → Submits security finding to hub/intake/ (impact: 9)

8. session-observer fires (watcher, pre_closeout)
   → Reconciles ledger
   → Creates session summary Lug
```

This is agent collaboration in action.


---

# Spoke Structure
Source: framework/docs/spokes/structure.md

# Spoke Structure

A spoke is a WAI extension for a specific project. It inherits policies from the Hub and maintains local state, Lugs, and configuration.

## Purpose

Each spoke:
1. **Defines project-specific behavior** via BRIEF.md and EXTENSION.md
2. **Tracks local work** via WAI-Lugs.jsonl
3. **Maintains session continuity** via WAI-Ledger.jsonl
4. **Submits learnings** to Hub for cross-project sharing

## Directory Structure

```
your-project/
├── BRIEF.md              # Project behavioral rules (inherits hub/BRIEF.md)
├── EXTENSION.md          # Role and lens definition
├── skills/               # Project-specific skills (optional)
└── WAI-Spoke/
    ├── WAI-Manifest.yaml # Node configuration
    ├── WAI-Lugs.jsonl    # Local work log
    ├── WAI-Ledger.jsonl  # Session commitments
    └── WAI-State.json    # Runtime state (optional)
```

## Core Files

### BRIEF.md

Project-specific behavioral rules that inherit from hub/BRIEF.md:

```markdown
# BRIEF — your-project

**BRIEF Cascade:** This file inherits rules from hub/BRIEF.md

## Always
- [Project-specific rule 1]
- [Project-specific rule 2]

## Never
- [Project-specific prohibition]

## When Uncertain
- [Project-specific clarification source]
```

### EXTENSION.md

Defines the spoke's identity and perspective:

```markdown
# your-project Extension

## Identity

**Role:** [Your role - CTO, PM, QA, etc.]
**Lens:** [Your perspective - what you focus on]

**Primary Focus:**
- [Key responsibility 1]
- [Key responsibility 2]

## Behaviors

### Always
- [Role-specific behavior]

### Never
- [Role-specific prohibition]

## Skills Loaded

- safe-refactor (guardian)
- session-observer (watcher)
- [custom-skill] (reviewer)

## Offers

What this extension produces:
- [Output type 1]
- [Output type 2]

## Subscribes To

What this extension watches for:
- hub:framework:* (framework updates)
- hub:pattern:* (cross-spoke patterns)
```

### WAI-Manifest.yaml

Node configuration and framework state:

```yaml
node_type: spoke
node_path: "your-org/your-project"
framework_version: "2.0.0"
template_versions:
  lugs: 2
  brief: 1
  guide: 1
hub_lug_cursor: null        # Last processed hub Lug
skills_loaded:
  - safe-refactor
  - session-observer
last_session: null
outbound_pending: []        # Signals waiting for hub processing
file_load_policy:           # Optional: selective file loading
  load_always:
    - "src/core/*.py"
  load_on_demand:
    - "tests/*.py"
  never_load:
    - "reference/**/*"
```

### WAI-Lugs.jsonl

Append-only log of all work items:

```jsonl
{"id":"lug-2026-02-14-001","type":"diagnosis","title":"Bug in auth handler","status":"published","impact":7,...}
{"id":"lug-2026-02-14-002","type":"prescription","title":"Fix auth handler","diagnosis_id":"lug-2026-02-14-001",...}
{"id":"lug-2026-02-14-003","type":"decision","title":"Chose JWT over sessions","alternatives_considered":[...],...}
```

### WAI-Ledger.jsonl

Session commitment tracking:

```jsonl
{"id":"led-001","type":"request","content":"Add user authentication","status":"open",...}
{"id":"led-002","type":"agreement","content":"Will implement JWT auth","references":"led-001",...}
{"id":"led-003","type":"delivery","content":"JWT auth implemented","commit":"abc123","status":"fulfilled",...}
```

## Spoke Wakeup Flow

When opening a spoke project:

1. Agent reads BRIEF.md (behavioral rules)
2. Agent reads EXTENSION.md (role and lens)
3. Agent reads WAI-Manifest.yaml (framework config)
4. `hub-watcher` skill fires (if node_type == "spoke"):
   - Checks hub for framework updates
   - Auto-applies patch updates (2.0.0 → 2.0.1)
   - Notifies about minor/major updates (2.0.0 → 2.1.0)
   - Pulls pending signals from hub
5. Agent reads WAI-Ledger.jsonl for open commitments
6. Agent is briefed and ready to work

## Spoke Closeout Flow

When ending a session:

1. `session-observer` skill fires
2. Reconciles WAI-Ledger.jsonl (flags unfulfilled commitments)
3. Checks if framework files changed (flags doc updates needed)
4. Creates session summary Lug
5. Agent reports closeout status

## Cross-Node Communication

### Submitting to Hub

When a spoke creates a high-impact Lug (impact >= 8):

1. Lug written to local WAI-Lugs.jsonl
2. Lug copied to `hub/intake/{node-path}/{lug-id}.yaml`
3. Added to WAI-Manifest.yaml `outbound_pending`
4. On next spoke wakeup, hub-watcher checks if hub processed it

### Receiving from Hub

When hub has new signals for this spoke:

1. hub-watcher reads hub/health.yaml for pending signals
2. Pulls signals matching spoke's subscription patterns
3. Creates local Lugs with `source_id` pointing to hub Lug
4. Updates WAI-Manifest.yaml `hub_lug_cursor`

## Spoke Types

### Active Spoke
```yaml
node_type: spoke
status: active
```
Full functionality, receives updates, submits signals.

### Archived Spoke
```yaml
node_type: spoke
status: archived
```
Read-only reference, minimal skills, no signal submission.

## Best Practices

1. **Keep BRIEF.md focused** - Only add rules specific to this project
2. **Define clear lens** - EXTENSION.md should explain your unique perspective
3. **Create Lugs as you work** - If you didn't write a Lug, it didn't happen
4. **Use the ledger** - Track commitments to survive context loss
5. **Submit high-impact learnings** - Share patterns that benefit other projects


---

# What is WAI?
Source: framework/docs/start-here/what-is-wai.md

# What is WAI?

**WAI** (Wheelwright AI) is an agent communication protocol. It's how AI agents talk to each other, show their work, and build institutional memory.

## Core Principles

1. **Agents communicate through files** — not APIs, not databases, files
2. **Show your work** — every agent action produces a Lug (audit trail)
3. **Institutional memory** — decision Lugs capture conductor judgment, sub-agents learn over time
4. **Data protection** — WAI-Integrity.md prevents Hub destruction
5. **Multi-agent colonies** — cheap specialists + expensive orchestrator

## The Two Primitives

### Skills

A Skill is a sub-agent with a contract. It declares what it does, when it fires, what model it needs, and what it produces.

See: [skills/overview.md](../skills/overview.md)

### Lugs

A Lug is an actionable record. Diagnosis, prescription, decision, observation, task, signal.

See: [lugs/overview.md](../lugs/overview.md)

## Architecture

Hub-and-spoke model. Hub is shared memory across projects. Spokes are per-project extensions.

See: [architecture.md](./architecture.md)

## For Newcomers

Start here:
1. Read this file (you're here)
2. Read [core-concepts.md](./core-concepts.md)
3. Read [quickstart.md](./quickstart.md)
4. Explore [skills/](../skills/) and [lugs/](../lugs/)

## For Agents

Read the specs at repo root:
- WAI-Lug-Schema-Spec.md
- WAI-Skill-Contract-Spec.md
- WAI-v2-Implementation-Plan-Revised.md

Then read WAI-Integrity.md for data protection rules.


---


---

**End of Documentation**

Wheelwright AI Framework v2.0.180
Agents communicate through files. Institutions remember through Lugs.


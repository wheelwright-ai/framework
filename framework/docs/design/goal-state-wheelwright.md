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

- `WAI-Hub/Signals/incoming/`
- `WAI-Hub/Signals/processed/`

This folder acts as the hub bulletin board for high-impact lugs copied upward from spokes. Other spokes inspect `incoming/` on wakeup. Framework absorption and teaching generation clear or reconcile items by moving them to `processed/` after incorporation.

### 5.3 Mail Versus Signals

Canonical rule:

- **Mail** is addressed work or addressed artifacts delivered to a recipient mailbox
- **Signals** are staged observations or patterns available for selective pull

Signals must not be treated as imperative inbox instructions.

Resolved signal model:

- signals are canonically **lugs**
- a lug becomes a signal when `impact > 7`
- qualifying lugs are copied to the hub bulletin at `WAI-Hub/Signals/incoming/`
- other spokes inspect those signals during wakeup
- framework incorporates relevant signals and may generate teachings from them
- processed signals are moved to `WAI-Hub/Signals/processed/`, not deleted

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

- [README.md](/home/mario/projects/wheelwright/framework/README.md) says `Teach = PUSH`, `Learn = PULL`
- [templates/spoke/WAI-Skills.jsonl](/home/mario/projects/wheelwright/framework/templates/spoke/WAI-Skills.jsonl) currently describes `teach` as pulling from hub and `learn` as pushing to hub

Resolved direction:

- these are no longer the primary design verbs
- closeout handles outbound mail and signal publication
- wakeup handles inbound reconciliation, holdings, and hub teachings
- legacy CLI terminology should be expunged from the goal-state model

Legacy commands may continue to exist as wrappers or compatibility affordances, but they are not the core conceptual model.

### 8.2 Signal Storage Has Two Competing Models

Current repo examples conflict:

- [README.md](/home/mario/projects/wheelwright/framework/README.md) and current spoke templates use `WAI-Signals.jsonl`
- [framework/docs/index.md](/home/mario/projects/wheelwright/framework/framework/docs/index.md) and older v2 material often describe signals as high-impact lugs inside the lug system

Resolved direction:

- the canonical model is signal-classified lugs
- the hub bulletin board at `WAI-Hub/Signals/incoming/` and `WAI-Hub/Signals/processed/` is a distribution/staging mechanism
- any separate signal file is secondary to the lug model, not a competing source of truth

### 8.3 `BRIEF` / `Manifest` Vocabulary Conflicts With `WAI-State`

Current repo examples conflict:

- [framework/docs/guides/migration-v1-to-v2.md](/home/mario/projects/wheelwright/framework/framework/docs/guides/migration-v1-to-v2.md) centers `BRIEF.md`, `EXTENSION.md`, and `WAI-Manifest.yaml`
- [templates/spoke/WAI-State.json](/home/mario/projects/wheelwright/framework/templates/spoke/WAI-State.json) centers `WAI-State.json` and `WAI-Spoke/`

Resolved direction:

- `WAI-Spoke/WAI-State.json` is the canonical state model
- older `BRIEF` / `Manifest` / `Extension` material is migration-era compatibility content unless explicitly reintroduced later

### 8.4 Track Storage Needs One Canonical Path Model

Current repo examples conflict:

- [tracks/spec/track-format.md](/home/mario/projects/wheelwright/framework/tracks/spec/track-format.md) implies standalone `track_YYYYMMDD-HHMM.jsonl`
- [WAI-Spoke/commands/wai.md](/home/mario/projects/wheelwright/framework/WAI-Spoke/commands/wai.md) still includes `session-YYYYMMDD-HHMM/track.jsonl`
- current repo data contains both `sessions/track_*.jsonl` and older `session-*/track.jsonl`

Resolved direction:

- canonical path is `WAI-Spoke/sessions/session-YYYYMMDD-HHMM/track.jsonl`
- flat `sessions/track_*.jsonl` remains legacy-read compatibility only

### 8.5 Public Docs Over-Promise Some Unsettled Concepts

Examples:

- [framework/docs/index.md](/home/mario/projects/wheelwright/framework/framework/docs/index.md) describes a richer multi-agent / BRIEF / ledger system than the current repo actually enforces
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

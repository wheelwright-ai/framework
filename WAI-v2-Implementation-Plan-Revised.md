# WAI v2 Implementation Plan (Revised)

**Version:** 1.1.0
**Date:** 2026-02-11
**Agent Level:** Advanced (Opus-class) — orchestrator with human gates
**Status:** Ready for execution
**Revision Notes:** Incorporates extensibility spec, wakeup improvement spec, PEV pattern, documentation structure, closeout discipline, and migration YAML as reusable pattern.

---

## Guiding Principles

1. **Additive then subtractive.** Build new alongside old. Copy, never move. Verify, only then remove.
2. **Git is your undo button.** Tag before starting. Commit after every phase.
3. **Human gates at every structural milestone.** Agent proposes, conductor approves, then execute.
4. **Existing data is sacred.** All content is preserved and migrated, never recreated.
5. **One concern per phase.** If it fails, only that thing reverts.
6. **Closeout every phase.** Formal git commit, migration state update, commit hash recorded. This is the receipt.
7. **Learnings become Lugs.** Every session ends with observation Lugs capturing what was learned during the work.
8. **Skills carry use cases.** Every Skill includes sample scenarios explaining why it exists and how to use it.

---

## The Migration YAML Pattern

`WAI-MIGRATION.yaml` is created at repo root in Phase 0. It serves as the single source of truth for migration state. This is also a **reusable pattern** — any future upgrade (v3, template updates, node-level upgrades) uses the same approach:

```yaml
migration: v2
status: in_progress            # in_progress | complete
current_phase: 0
completed_phases: []           # [{phase: 1, commit: "abc123", closed_at: "..."}]
authoritative_format: v1       # Flips to v2 after Phase 6
retired_files:                 # Agents: do not read or write these
  - WAI-Signals.jsonl
  - WAI-Backpressure.yaml
notes: "If you see this file, migration is active. Read it FIRST."
```

**Phase closeout updates this file:**
```yaml
completed_phases:
  - phase: 1
    commit: "a3f7b2c"
    closed_at: "2026-02-12T14:30:00Z"
    summary: "Lug schema migrated, signals absorbed, PEV fields added"
```

**On final merge (Phase 8):** The migration YAML is converted into a Hub-level decision Lug recording the full migration, then the YAML file is deleted. The Lug IS the permanent record.

**Reuse for node-level updates:** When a spoke checks for framework template updates, the framework-updater Skill can create a local `WAI-UPGRADE.yaml` following this same pattern — tracking what's being updated, what phase it's in, what's authoritative. Completes, becomes a Lug, file removed. Same pattern at every scale.

---

## Current State Inventory

### Files That Exist Today (per spoke)

```
WAI-Spoke/
├── WAI-Guide.md          → KEEP (project identity, migrates byte-for-byte)
├── BRIEF.md              → KEEP (operational directives, migrates as-is)
├── WAI-State.json        → KEEP (session state, migrates as-is)
├── WAI-Lugs.jsonl        → KEEP (CRITICAL DATA — schema additions, no deletions)
├── WAI-Signals.jsonl     → RETIRE (absorbed into Lugs as impact ≥ 8)
├── WAI-Backpressure.yaml → EVOLVE (becomes qc-check Skill definition)
├── WAI-Features/         → KEEP (feature specs, migrates as-is)
```

### New Files Created

```
# Per node (hub + each spoke)
WAI-Manifest.yaml         → Node identity, versions, cursor tracking
skills/                   → Skill definitions directory
EXTENSION.md              → Extension identity (spokes only)

# Hub-only
hub/intake/               → Cross-node signal intake
hub/intake/processed/     → Processed intake audit trail
hub/health.yaml           → Hub health status
hub/WAI-Integrity.md      → Data protection contract

# Framework-level (lives in framework, NOT pushed to wheel)
framework/skills/         → Base Skill templates with use cases
framework/templates/      → Versioned file templates
framework/docs/           → Documentation source (see Phase 9)

# Repo root (temporary)
WAI-MIGRATION.yaml        → Migration state (becomes Lug on completion)
```

---

## Phase 0: Safety Checkpoint

**Purpose:** Unbreakable restore point + migration state file.
**Human Gate:** BEFORE — Confirm ready to start.
**Agent Level:** Any.

### Actions

```
0.1  Verify clean git state. If dirty, commit with message:
     "WAI: Pre-v2 migration — uncommitted work checkpoint"

0.2  Tag current state:
     git tag -a v1.0-pre-migration -m "WAI v1 state before v2 migration"
     git push origin v1.0-pre-migration

0.3  Create migration branch:
     git checkout -b wai-v2-migration

0.4  Create WAI-MIGRATION.yaml at repo root (see pattern above)

0.5  CLOSEOUT:
     git add -A
     git commit -m "WAI v2 Phase 0: Safety checkpoint and migration state initialized"
     Update WAI-MIGRATION.yaml: current_phase: 0, add to completed_phases with commit hash
     git add WAI-MIGRATION.yaml && git commit --amend --no-edit
```

### Verification

- [ ] Tag v1.0-pre-migration exists and is pushed
- [ ] On wai-v2-migration branch
- [ ] WAI-MIGRATION.yaml exists at repo root
- [ ] All existing data is committed

### Rollback

```
git checkout main && git branch -D wai-v2-migration
```

**GATE: Show conductor tag and migration file. Get approval.**

---

## Phase 1: Lug Schema Migration

**Purpose:** Upgrade WAI-Lugs.jsonl to v2 schema. Add PEV optional fields. Absorb signals.
**Human Gate:** AFTER — Review migrated Lugs.
**Agent Level:** Advanced.

### Actions

```
1.1  BACKUP every WAI-Lugs.jsonl:
     cp WAI-Lugs.jsonl WAI-Lugs.jsonl.v1-backup

1.2  MIGRATE each Lug — ADD fields, never remove:
     
     New required fields:
       impact: 3 (default for local tasks)
       created_by: "conductor" (default for human-created)
       node: derived from folder path (e.g., "wheelwright/cto")
       created_at: "2026-02-11T00:00:00Z" (or best estimate)
     
     Status mapping:
       "ready"       → "published"
       "in-progress" → "in_progress"
       "closed"      → "resolved"
       "blocked"     → "published" (preserve blocker info)
     
     Preserve originals:
       _v1_status: original status value
     
     New optional PEV fields (empty/null — available for future Lugs):
       perceive: null
       execute: null
       verify: null
     
     New calibration fields (empty — populated on future resolutions):
       resolution: null
       resolution_reason: null

1.3  ABSORB SIGNALS from each WAI-Signals.jsonl:
     - Convert each signal to a Lug with impact: 8+
     - type: "signal"
     - Append to corresponding WAI-Lugs.jsonl
     - Add tombstone header to WAI-Signals.jsonl:
       "# RETIRED: Absorbed into WAI-Lugs.jsonl as of WAI v2. Do not use."
     
1.4  TOMBSTONE WAI-Signals.jsonl (do NOT delete yet)

1.5  CLOSEOUT:
     git add -A
     git commit -m "WAI v2 Phase 1: Lug schema migrated, signals absorbed, PEV fields added"
     Update WAI-MIGRATION.yaml with phase completion + commit hash

1.6  LEARNINGS LUG:
     Create observation Lug in Hub:
     "Phase 1 learnings: [what was encountered, any edge cases, data quality notes]"
```

### Verification

- [ ] Every Lug has: id, type, title, status, impact, created_by, node, created_at
- [ ] PEV fields present (null is fine — schema is ready)
- [ ] No data lost (new line count ≥ old + absorbed signals)
- [ ] _v1_status preserves original values
- [ ] v1-backup files exist for all migrated files
- [ ] WAI-Signals.jsonl files have tombstone headers
- [ ] git diff shows only additions to existing Lug content

### Rollback

```
find . -name "*.v1-backup" -exec sh -c 'cp "$1" "${1%.v1-backup}"' _ {} \;
git checkout -- .
```

**GATE: Show before/after sample. Get approval.**

---

## Phase 2: Registry Structure + Manifests

**Purpose:** Establish registry folder hierarchy. Create manifests for all nodes. Migrate existing spokes into registry paths.
**Human Gate:** AFTER — Review structure and manifests.
**Agent Level:** Advanced — must map existing spokes to correct registry locations.

### Actions

```
2.1  Create registry directory structure:
     
     registry/
       {project}/              # One per existing project
         PROJECT.md            # Created from existing WAI-Guide.md project context
         {extension}/          # One per existing spoke
           (existing spoke files migrated here)

2.2  MIGRATE existing spoke folders into registry paths:
     - Map each WAI-Spoke to registry/{project}/{extension}/
     - COPY files (do not move yet — additive first)
     - Verify all files present in new location
     
2.3  Create WAI-Manifest.yaml for EACH node:

     # Hub manifest
     node_type: hub
     node_path: hub
     framework_version: "2.0.0"
     template_versions:
       lugs: 2
       brief: 1
       guide: 1
     hub_lug_cursor: null
     skills_loaded: []
     last_session: null
     outbound_pending: []

     # Spoke manifests (one per extension in registry)
     node_type: spoke
     node_path: "{project}/{extension}"
     framework_version: "2.0.0"
     template_versions:
       lugs: 2
       brief: 1
       guide: 1
     hub_lug_cursor: null
     skills_loaded: []
     last_session: null
     outbound_pending: []

2.4  Create hub/registry.yaml — the index of all nodes:
     
     nodes:
       - path: "wheelwright/cto"
         type: spoke
         status: active
         framework_version: "2.0.0"
       - path: "ownersshare/cto"
         type: spoke
         status: active
         framework_version: "2.0.0"
       # ... etc

2.5  CLOSEOUT:
     git add -A
     git commit -m "WAI v2 Phase 2: Registry structure created, manifests initialized"
     Update WAI-MIGRATION.yaml

2.6  LEARNINGS LUG
```

### Verification

- [ ] Every project has registry/{project}/PROJECT.md
- [ ] Every spoke has registry/{project}/{extension}/ with all files
- [ ] Every node has WAI-Manifest.yaml with correct node_path
- [ ] hub/registry.yaml lists all nodes
- [ ] Original spoke locations still exist (not yet removed)

### Rollback

```
rm -rf registry/ hub/registry.yaml
find . -name "WAI-Manifest.yaml" -delete
git checkout -- .
```

**GATE: Show registry tree and sample manifest. Get approval.**

---

## Phase 3: Skills Directory + Extension Identity

**Purpose:** Create framework Skills (with use cases), spoke Skills directories, and EXTENSION.md per extension. Also create the integration-check Skill from the wakeup spec.
**Human Gate:** AFTER — Review Skill definitions and use cases.
**Agent Level:** Advanced.

### Skill Use Case Requirement

Every Skill YAML MUST include a `use_cases` section:

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
```

This serves triple duty: documentation for users, context for agents deciding whether to invoke the Skill, and institutional memory about WHY the Skill exists.

### Actions

```
3.1  Create framework/skills/ with all built-in Skill YAMLs:
     - safe-refactor.yaml (guardian)
     - qc-check.yaml (reviewer)
     - hub-watcher.yaml (watcher)
     - framework-updater.yaml (worker)
     - brief-advisor.yaml (advisor)
     - session-observer.yaml (watcher)
     - file-audit.yaml (reviewer)
     - integration-check.yaml (guardian) — from wakeup improvement spec
     
     Each file follows the Skill Contract Specification with:
     - Full identity, model, trigger, scope, prerequisites, output sections
     - use_cases section with real scenarios
     - tests section with unit test definitions

3.2  Create framework/templates/:
     - WAI-Manifest.yaml.template
     - WAI-Lugs.jsonl.template (v2 schema example)
     - BRIEF.md.template
     - EXTENSION.md.template
     - PROJECT.md.template

3.3  Create EXTENSION.md for each existing spoke:
     
     # {Extension Name}
     
     ## Identity
     Role: {e.g., CTO — Technical Architecture & Development}
     Lens: {How this extension interprets information}
     
     ## Behaviors
     Always: {What this extension always does}
     Never: {What this extension never does}
     
     ## Skills Loaded
     - safe-refactor (guardian)
     - qc-check (reviewer)
     - {any project-specific skills}
     
     ## Offers (what I produce that others may need)
     - Architecture decisions
     - Technical feasibility assessments
     
     ## Subscribes To (what I watch for from other nodes)
     - hub:framework:* (framework updates)
     - hub:pattern:* (cross-project patterns)

3.4  Migrate WAI-Backpressure.yaml into spoke-level qc-check override:
     - Read existing backpressure commands
     - Create {spoke}/skills/qc-check.yaml with those commands
     - Add tombstone to WAI-Backpressure.yaml
     
3.5  Create hub/skills/ — link/copy relevant framework Skills
     Plus hub-specific Skills if any.

3.6  Create spoke/skills/ directories (empty or with overrides only)

3.7  Update all WAI-Manifest.yaml: skills_loaded field

3.8  CLOSEOUT:
     git add -A
     git commit -m "WAI v2 Phase 3: Skills, extension identity, and integration-check created"
     Update WAI-MIGRATION.yaml

3.9  LEARNINGS LUG
```

### Verification

- [ ] framework/skills/ has all 8 built-in Skill YAMLs
- [ ] Every Skill has use_cases section with real scenarios
- [ ] Every Skill has tests section
- [ ] framework/templates/ has all template files
- [ ] Every spoke has EXTENSION.md
- [ ] Backpressure configs captured in spoke qc-check overrides
- [ ] WAI-Backpressure.yaml files have tombstones
- [ ] Manifests updated with skills_loaded

### Rollback

```
rm -rf framework/
find . -name "EXTENSION.md" -delete
find . -path "*/skills/" -type d -exec rm -rf {} +
git checkout -- .
```

**GATE: Show Skill YAMLs with use cases. Verify against spec. Get approval.**

---

## Phase 4: Hub Infrastructure

**Purpose:** Hub intake, health file, BRIEF cascade.
**Human Gate:** AFTER — Review structure.
**Agent Level:** Standard.

### Actions

```
4.1  Create Hub intake:
     hub/intake/.gitkeep
     hub/intake/processed/.gitkeep

4.2  Initialize hub/health.yaml:
     intake_pending: 0
     oldest_pending: null
     last_hub_session: null
     framework_update_available: false
     spokes_with_stale_cursors: []

4.3  Formalize BRIEF cascade:
     - Hub BRIEF.md gets a header: "# Hub-Level Policies (inherited by all spokes)"
     - Document the cascade: hub BRIEF → project BRIEF → spoke BRIEF
     - Spokes can add, can narrow, cannot remove hub-level rules
     - Add cascade documentation to framework/templates/BRIEF.md.template

4.4  CLOSEOUT + LEARNINGS LUG
```

### Verification

- [ ] hub/intake/ and hub/intake/processed/ exist
- [ ] hub/health.yaml initialized
- [ ] BRIEF cascade documented and templated

**GATE: Quick review. Get approval.**

---

## Phase 5: WAI-Integrity.md

**Purpose:** Data protection contract that prevents another Hub destruction.
**Human Gate:** AFTER — Conductor reads this thoroughly.
**Agent Level:** Advanced.

### Actions

```
5.1  Create hub/WAI-Integrity.md with:
     - Read-only paths (framework/**, hub/WAI-Integrity.md, backups)
     - Append-only paths (WAI-Lugs.jsonl, hub/intake/)
     - Scoped write access (each spoke owns only its directory)
     - Pre-refactor rule (safe-refactor MUST fire before structural changes)
     - Destructive operation policy (checkpoint + human gate + Lug)
     - Violation handling (violation Lug, session summary report)

5.2  Add use case to safe-refactor Skill:
     scenario: "Agent attempted to restructure hub folder without checkpoint"
     what_happens: "safe-refactor blocks the operation until git is clean and committed"
     why_it_matters: "Hub folder was destroyed on 2026-02-10 with no recovery point"

5.3  CLOSEOUT + LEARNINGS LUG
```

### Verification

- [ ] WAI-Integrity.md is clear, unambiguous, agent-actionable
- [ ] References safe-refactor Skill by name
- [ ] Destructive ops require human gate

**GATE: Conductor reads WAI-Integrity.md thoroughly. This IS the safety policy. Get approval.**

---

## Phase 6: Wakeup Sequence Update

**Purpose:** v2 wakeup generates composite briefings with Skills, Integrity, PEV-aware Lugs, manifest data.
**Human Gate:** AFTER — Review generated briefing.
**Agent Level:** Advanced.

### Actions

```
6.1  Create framework/templates/agent-primer.md:
     Section 1 template — WAI Framework Primer
     - WAI as agent communication protocol
     - Skills and Lugs as two primitives (with PEV explanation)
     - Hub-and-spoke architecture
     - WAI-Integrity rules (injected placeholder)
     - Wakeup sequence description
     - Manifest awareness

6.2  Update wakeup generation to produce composite briefing:
     Section 1: Agent Primer (from template + Integrity injection)
     Section 2: This Project (from WAI-Guide.md — unchanged)
     Section 3: Current Directives (BRIEF cascade + state + ready Lugs + Skills status)

6.3  Wire integration-check Skill into wakeup sequence:
     - Verify IDE files exist and are current
     - Self-heal what it can (regenerate stale files)
     - Report what it found in session log

6.4  Wire full wakeup sequence:
     P1: hub-watcher + safe-refactor
     P2: framework-updater + load BRIEF/Lugs/manifest
     P3: all reviewers + brief-advisor
     P4: orchestrator reconciliation
     P5: present plan to conductor

6.5  Update WAI-MIGRATION.yaml: authoritative_format: v2

6.6  CLOSEOUT + LEARNINGS LUG
```

### Verification

- [ ] Generated CLAUDE.md includes Integrity rules
- [ ] Generated CLAUDE.md includes Skills status
- [ ] v2 Lug format (with PEV fields) displays correctly
- [ ] Hub-watcher findings included
- [ ] Manifest data visible
- [ ] WAI-Guide.md and BRIEF.md content preserved byte-for-byte

**GATE: Show generated CLAUDE.md. Review. Get approval.**

---

## Phase 7: Cleanup

**Purpose:** Remove retired files. Remove old spoke locations (data now in registry).
**Human Gate:** BEFORE — Confirm all verifications pass.
**Agent Level:** Standard.

### Pre-Cleanup Verification (ALL must pass)

- [ ] Phases 1-6 committed on migration branch
- [ ] All Lugs have v2 schema
- [ ] All signals absorbed
- [ ] All backpressure configs in Skills
- [ ] Wakeup generates correct v2 briefings
- [ ] Registry structure has all data
- [ ] v1-backup files exist

**GATE: Conductor confirms all verifications. Approve before any deletion.**

### Actions

```
7.1  safe-refactor checkpoint

7.2  Delete tombstoned files:
     - WAI-Signals.jsonl (all instances)
     - WAI-Backpressure.yaml (all instances)

7.3  Remove old spoke locations (data lives in registry now):
     - Only after verifying registry copies are complete and identical

7.4  v1-backup files: ASK conductor whether to keep or remove

7.5  CLOSEOUT + LEARNINGS LUG
```

**GATE: Quick review of deletions. Get approval.**

---

## Phase 8: Integration Test & Merge

**Purpose:** End-to-end verification, then merge to main.
**Human Gate:** BEFORE merge.
**Agent Level:** Advanced.

### Actions

```
8.1  Full wakeup test on every spoke
8.2  Full wakeup test on Hub
8.3  Cross-node communication test (high-impact Lug → intake → Hub process → spoke detect)
8.4  Data preservation count (total Lugs ≥ pre-migration + absorbed signals)

8.5  Convert WAI-MIGRATION.yaml into Hub decision Lug:
     {
       type: "decision",
       title: "WAI v2 migration completed",
       impact: 10,
       status: "resolved",
       resolution: "accepted",
       repo_version: "{v2.0.0 tag hash}",
       alternatives_considered: [
         {option: "CLI-based management", chosen: false, 
          reasoning: "CLI destroyed Hub folder; no data protection"},
         {option: "File-based protocol with Skills and Lugs", chosen: true,
          reasoning: "Agents communicate through files, show work via Lugs, 
                      execute via Skills, boundaries enforced by convention"}
       ],
       summary: "Full migration from v1 to v2. Signals → Lugs. 
                 Backpressure → Skills. Integrity contract. Registry structure.
                 PEV fields. Extension identity. All data preserved."
     }

8.6  Delete WAI-MIGRATION.yaml (data now lives in the Lug)

8.7  Merge:
     git checkout main
     git merge wai-v2-migration
     git tag -a v2.0.0 -m "WAI v2: Agent Communication Protocol — Skills and Lugs"
     git push origin main --tags

8.8  FINAL LEARNINGS LUGS:
     - Overall migration learnings (what went well, what was harder than expected)
     - Pattern observations (what should be automated next time)
     - Any BRIEF amendments suggested by the experience
```

### Verification

- [ ] All wakeup tests pass
- [ ] Cross-node communication works
- [ ] Zero data loss
- [ ] Migration Lug exists in Hub
- [ ] WAI-MIGRATION.yaml deleted
- [ ] v2.0.0 tag pushed

---

## Phase 9: Documentation Structure

**Purpose:** Create the documentation source for Wheelwright. Lives in framework, not pushed to the wheel. Includes llms-full.txt export for agent consumption.
**Human Gate:** AFTER — Review doc structure and sample content.
**Agent Level:** Advanced.

### Documentation Architecture

Following the Lindy docs pattern: clean hierarchy, progressive disclosure, and an `llms-full.txt` flat export that agents can consume in a single fetch.

```
framework/docs/
├── index.md                          # "Meet Wheelwright" — landing page
├── llms-full.txt                     # AUTO-GENERATED flat export of all docs
├── generate-llms-txt.sh              # Script to build llms-full.txt from sources
│
├── start-here/
│   ├── what-is-wai.md                # WAI as agent communication protocol
│   ├── quickstart.md                 # Get running in 10 minutes
│   ├── core-concepts.md              # Skills, Lugs, Hub, Spokes, Conductor
│   └── architecture.md               # Hub-and-spoke, file-based protocol, no CLI
│
├── skills/
│   ├── overview.md                   # What Skills are, how they work
│   ├── skill-contract.md             # The Skill Contract Specification
│   ├── model-tiers.md                # lightweight/standard/advanced + cost optimization
│   ├── built-in/
│   │   ├── safe-refactor.md          # Guardian — git checkpoint before changes
│   │   ├── qc-check.md              # Reviewer — test/startup/coverage verification
│   │   ├── hub-watcher.md           # Watcher — Hub/framework update detection
│   │   ├── framework-updater.md     # Worker — template cascade updates
│   │   ├── brief-advisor.md         # Advisor — BRIEF alignment + apprenticeship
│   │   ├── session-observer.md      # Watcher — event recording + session synthesis
│   │   ├── file-audit.md            # Reviewer — sprawl detection
│   │   └── integration-check.md     # Guardian — IDE environment verification
│   ├── creating-skills.md            # How to create custom Skills
│   ├── skill-inheritance.md          # Framework → Hub → Spoke cascade
│   └── enterprise-skills.md          # Mandatory Skills, compliance, CSO integration
│
├── lugs/
│   ├── overview.md                   # What Lugs are, why they're the universal primitive
│   ├── lug-schema.md                 # The Lug Schema Specification
│   ├── lug-types.md                  # task, diagnosis, prescription, decision, etc.
│   ├── pev-pattern.md                # Perceive/Execute/Verify on Lugs
│   ├── impact-scoring.md             # 1-10 scale, signal threshold at 8
│   ├── lifecycle.md                  # draft → published → acknowledged → resolved
│   ├── calibration.md                # accepted/deferred/dismissed/modified + learning
│   ├── cross-node.md                 # Outbound, inbound, Hub processing
│   ├── decision-records.md           # The apprenticeship engine
│   └── idempotency.md               # Rules for preventing duplicates
│
├── hub/
│   ├── overview.md                   # Hub as Spoke+ node
│   ├── integrity.md                  # WAI-Integrity.md — data protection
│   ├── intake.md                     # How cross-node signals flow through intake
│   ├── health.md                     # hub/health.yaml — herald pattern
│   ├── registry.md                   # Project and idea registry
│   └── conductor-view.md             # Cross-project orchestration
│
├── spokes/
│   ├── overview.md                   # Spoke structure and conventions
│   ├── extensions.md                 # EXTENSION.md — identity, lens, behaviors
│   ├── brief-cascade.md              # Hub → project → spoke BRIEF inheritance
│   ├── manifests.md                  # WAI-Manifest.yaml — node state tracking
│   └── wakeup-sequence.md            # What happens when a spoke loads
│
├── multi-agent/
│   ├── overview.md                   # Agent colony architecture
│   ├── sub-agents.md                 # Reviewer/watcher/guardian/worker/advisor/orchestrator
│   ├── model-diversification.md      # Multi-model as ensemble validation
│   ├── colony-patterns.md            # Main agent + cheap specialist sub-agents
│   └── audit-trail.md               # WAI as agent communication protocol — showing work
│
├── guides/
│   ├── migrating-to-v2.md            # Migration guide (from this plan)
│   ├── creating-extensions.md        # Bootstrap conversation → conformant extension
│   ├── cookbooks.md                  # Pre-built extension collections
│   ├── idea-registry.md              # Capturing and nurturing ideas
│   └── enterprise-setup.md           # Mandatory Skills, compliance layer
│
└── reference/
    ├── file-reference.md             # Every WAI file type, purpose, who edits it
    ├── lug-field-reference.md        # Complete field table
    ├── skill-field-reference.md      # Complete field table
    ├── glossary.md                   # Terms: Lug, Skill, Hub, Spoke, PEV, etc.
    └── changelog.md                  # Version history
```

### llms-full.txt Generation

A script (`generate-llms-txt.sh`) concatenates all doc files into a single flat text file, prepending each section with its source path:

```
# What is WAI
Source: framework/docs/start-here/what-is-wai.md

[content]

# Core Concepts
Source: framework/docs/start-here/core-concepts.md

[content]
...
```

This file is what agents fetch when they need to understand Wheelwright. One URL, complete knowledge. Same pattern as Lindy's llms-full.txt.

### Skill Directory (within docs)

Each built-in Skill gets its own doc page containing:
- What it does (plain English)
- Why it exists (origin story / use cases from the Skill YAML)
- When it fires
- What model it needs
- What it reads and writes
- Sample output (example Lug it would produce)
- How to customize it (spoke-level overrides)
- Related Skills

### Documentation Principles

1. **Docs live in framework/, not in the wheel.** Spokes don't get doc files. Agents fetch llms-full.txt or read framework/docs/ directly.
2. **Every doc page stands alone.** A reader landing on any page can understand it without reading the entire site.
3. **Progressive disclosure.** Start Here → deep dives → reference. Never front-load complexity.
4. **Use cases are first-class.** Every concept page starts with "when would you use this" before explaining how.
5. **Agent-readable.** llms-full.txt is the agent interface. It contains everything a new agent needs to understand WAI in one read.

### Actions

```
9.1  Create framework/docs/ directory structure
9.2  Write start-here/ pages (what-is-wai, quickstart, core-concepts, architecture)
9.3  Write skills/ pages (overview + each built-in Skill page from YAML use cases)
9.4  Write lugs/ pages (overview + schema + each aspect)
9.5  Write hub/ and spokes/ pages
9.6  Write multi-agent/ pages
9.7  Write guides/ (migration guide from this plan)
9.8  Write reference/ pages (field tables, glossary, changelog)
9.9  Create generate-llms-txt.sh and generate initial llms-full.txt
9.10 CLOSEOUT + LEARNINGS LUG
```

### Verification

- [ ] Every doc directory has its files
- [ ] llms-full.txt generates cleanly from source
- [ ] Skill docs match Skill YAMLs (use cases, fields)
- [ ] No docs reference features that don't exist yet (tabled items)
- [ ] Progressive disclosure works (start-here is accessible to newcomers)

**GATE: Review doc structure and sample pages. Get approval.**

---

## Phase Summary

| Phase | Purpose | Agent | Gate | Est. Effort |
|-------|---------|-------|------|-------------|
| 0 | Safety checkpoint + migration YAML | Any | Before | 10 min |
| 1 | Lug schema + PEV fields + signal absorption | Advanced | After | 1-2 hrs |
| 2 | Registry structure + manifests | Advanced | After | 1-2 hrs |
| 3 | Skills + extension identity + use cases | Advanced | After | 3-4 hrs |
| 4 | Hub infrastructure + BRIEF cascade | Standard | After | 30 min |
| 5 | WAI-Integrity contract | Advanced | After | 30 min |
| 6 | Wakeup sequence v2 | Advanced | After | 2-3 hrs |
| 7 | Cleanup retired files | Standard | Before | 30 min |
| 8 | Integration test + merge | Advanced | Before | 1-2 hrs |
| 9 | Documentation structure + llms-full.txt | Advanced | After | 4-6 hrs |

**Total: ~15-22 hours across 3-5 sessions.**

**Recommended session breaks:** After Phase 2, after Phase 5, after Phase 8, Phase 9 as standalone.

---

## Tabled Items (Become Lugs After v2 Merge)

These are valuable features built ON TOP of v2 infrastructure. Each becomes a Lug with clear scope:

| Item | Impact | Type | Notes |
|------|--------|------|-------|
| Cookbook system | 6 | task | Pre-built extension collections |
| Idea registry + ingest | 7 | task | IDEA.md, _ingest/, simmering section |
| Bootstrap conversation flow | 6 | task | "What would you like to do?" → extension |
| Project groups with budgets | 7 | task | Shared constraints, time allocations |
| Conductor view | 8 | task | Cross-project unified planning |
| Self-improvement loops | 8 | task | Skill calibration from Lug resolution patterns |
| METRICS.md separation | 4 | task | Quantitative vs qualitative split |
| Anticipation engine | 7 | task | Session pattern detection for proactive prompts |
| Decision pattern learning | 8 | task | Sub-agents referencing past decisions |

---

## Critical Reminders for the Executing Agent

1. NEVER delete without verifying migration is complete.
2. ALWAYS safe-refactor before structural changes.
3. ALWAYS show conductor at gate points before executing.
4. If you encounter data you don't understand, ASK.
5. Existing Lug content is sacred. Add fields, never remove.
6. WAI-Guide.md and BRIEF.md migrate byte-for-byte.
7. Every Skill MUST have use_cases with real scenarios.
8. Every phase MUST closeout with commit + migration YAML update.
9. Every session MUST end with learnings captured as Lugs.
10. When in doubt, commit and stop. Partial safe > complete broken.
11. You are modifying the framework that protects everything else.

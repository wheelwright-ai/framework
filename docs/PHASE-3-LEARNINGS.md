# Phase 3 Learnings: Skills Directory + Extension Identity

**Completed:** 2026-02-12
**Impact:** 9/10

---

## What Was Accomplished

### 1. Framework Skills Created (8 Total)

All Skills include comprehensive documentation:
- **Role classification** (guardian/reviewer/advisor/watcher/worker)
- **Trigger conditions** (events and when they fire)
- **Scope** (what they read/write)
- **Prerequisites** (what must exist)
- **Behavior** (what they do on trigger)
- **Output formats** (success/failure structures)
- **Use cases** (4-6 real scenarios per Skill)
- **Tests** (validation scenarios)
- **Notes** (context and rationale)

**Guardian Skills:**
- `safe-refactor.yaml` - Git checkpoint before structural changes
  - Origin story: Hub destroyed 2026-02-10, this prevents recurrence
  - Blocks refactoring if checkpoint fails

- `integration-check.yaml` - IDE environment verification
  - Runs before session briefing in wakeup sequence
  - Verifies Wheelwright detectable, framework importable, git available
  - Creates missing machine profile automatically

**Reviewer Skills:**
- `qc-check.yaml` - Quality gates (tests, startup, coverage)
  - Replaces WAI-Backpressure.yaml from v1
  - Spoke-level overrides in `spoke/skills/qc-check.yaml`
  - Gates: unit tests, integration tests, startup validation, coverage

- `file-audit.yaml` - Sprawl detection and organization health
  - Detects: flat root, config sprawl, test separation, orphan files
  - Health score 0-10 based on organization quality
  - Prevention pattern: flag at 15 files, not 50 files

**Advisor Skills:**
- `brief-advisor.yaml` - BRIEF alignment + apprenticeship
  - Pre-decision: checks alignment with BRIEF + past decisions
  - Post-decision: learns user preferences from resolution patterns
  - Surfaces relevant past decisions for institutional memory

**Watcher Skills:**
- `hub-watcher.yaml` - Hub updates and signal detection
  - Runs on session_start, checks framework version mismatch
  - Detects pending signals in hub/intake/
  - Reports hub health status

- `session-observer.yaml` - Event recording and synthesis
  - Logs high-impact events (impact >= 6) to observations.jsonl
  - Synthesizes session summary on closeout
  - Flags incomplete work for next session

**Worker Skills:**
- `framework-updater.yaml` - Template cascade
  - Updates spoke files when framework version changes
  - Auto-updates if no local modifications
  - Human gate if spoke modified template (shows diff)

### 2. Templates Created (5 Total)

**WAI-Manifest.yaml.template:**
- Extension registry entry structure
- Includes: extension_id, type, paths, skills_loaded, signals config
- Hub connection fields (hub_path, hub_lug_cursor)
- Machine optimization fields (machine_class, optimized)

**WAI-Lugs.jsonl.template:**
- Example Lugs showing structure
- Observation Lug (type: observation)
- Decision Lug (alternatives_considered, resolution_reason)
- Signal Lug (destination: hub, cross_node: true)

**BRIEF.md.template:**
- Always/Never/Preferences sections
- Cascade structure (Hub → Project → Spoke)
- Project-specific and spoke-specific rule sections
- Integration with brief-advisor Skill

**EXTENSION.md.template:**
- Extension identity and purpose
- Structure documentation
- Scope (what it does/doesn't do)
- Hub connection, Skills loaded, machine optimization
- Lifecycle (session start/during/end)

**PROJECT.md.template:**
- Project-level coordination document
- Spoke list and shared rules
- Cross-spoke communication patterns
- Machine profiles, framework updates, maintenance

### 3. Framework EXTENSION.md Created

Documents the framework extension itself:
- **Purpose:** Meta-extension defining how Wheelwright works
- **Structure:** wai/, skills/, templates/, docs/
- **Scope:** Infrastructure, not project-specific work
- **Skills:** Lists all 8 built-in Skills with descriptions
- **Machine optimization:** Classification and profile tracking
- **Template cascade:** Update flow from hub → spoke
- **Cross-node communication:** Signal propagation pattern
- **Skill overrides:** How spokes customize framework Skills
- **Version history:** v2.0.0 features vs v1.x legacy

### 4. Skills Directory Structure Created

```
framework/skills/          (8 built-in Skills)
hub/skills/                (hub-specific overrides)
spoke/skills/              (spoke-specific overrides)
```

Pattern: Framework provides defaults, spokes override as needed.

### 5. Manifests Updated

Added `skills_loaded` field to:
- `framework/registry/wheelwright/framework/WAI-Manifest.yaml`
- `hub/WAI-Manifest.yaml`

Structure:
```yaml
skills_loaded:
  framework:
    - safe-refactor
    - qc-check
    - [... 6 more Skills ...]
  spoke: []  # or hub: []
```

---

## Key Patterns Established

### 1. Skill Contract Structure
Every Skill YAML includes:
```yaml
name: skill-name
role: guardian|reviewer|advisor|watcher|worker
model: lightweight|standard
description: "One-line purpose"
trigger: {events, conditions}
scope: {reads, writes}
prerequisites: [list]
behavior: {on_trigger, on_failure}
output: {success, failure}
use_cases: [4-6 scenarios]
tests: [validation scenarios]
notes: "Context and rationale"
```

### 2. Use Case Format
Each use case includes:
- **scenario:** What happens
- **what_happens:** Skill's response
- **why_it_matters:** Impact/value
- **user_trigger:** How it fires (automatic vs manual)
- **origin:** (optional) Where pattern came from
- **reference:** (optional) Related docs

Example:
```yaml
- scenario: "Hub folder destroyed by rogue agent on 2026-02-10"
  what_happens: "Would have been prevented - checkpoint exists to revert to"
  why_it_matters: "This actually happened. This Skill exists because of it."
  origin: "WAI v2 architectural session, 2026-02-11"
```

### 3. Template Cascade Pattern
1. Hub updates framework version in `hub/WAI-Manifest.yaml`
2. Spoke's hub-watcher detects mismatch on session_start
3. User runs `/framework-update`
4. framework-updater compares templates, updates or asks for merge
5. Spoke manifest updated to new framework version

### 4. Skill Override Pattern
Framework provides defaults, spokes customize:
- `framework/skills/qc-check.yaml` - default gates
- `spoke/skills/qc-check.yaml` - custom commands, thresholds

qc-check loads spoke override if present.

### 5. Machine-Aware Recommendations
Skills adjust behavior based on machine class:
- HIGH-PERFORMANCE: Aggressive features, parallel execution
- STANDARD: Balanced features, moderate parallelism
- LOW-POWER: Conservative features, sequential execution

Example: Don't recommend workspace-wide type checking on LOW-POWER machine.

---

## Critical Decisions

### Decision: Comprehensive Use Cases Required
**Alternatives considered:**
- Minimal documentation (name, trigger, behavior only)
- Full documentation with 4-6 use cases per Skill

**Chosen:** Full documentation

**Resolution reason:**
Skills are behavioral contracts. Users and AI agents need to understand:
- When they fire (trigger conditions)
- What they do (behavior)
- **Why they exist** (use cases with real scenarios)
- How to validate (tests)

Use cases ground abstract Skill contracts in concrete scenarios.

### Decision: Lightweight vs Standard Model Per Skill
**Pattern established:**
- **Lightweight model:** Deterministic checks (file reads, command execution, version comparison)
  - safe-refactor, qc-check, hub-watcher, session-observer, file-audit, integration-check

- **Standard model:** Reasoning required (semantic analysis, pattern recognition, conflict resolution)
  - framework-updater (diff analysis, merge conflicts)
  - brief-advisor (decision alignment, preference learning)

**Rationale:**
- Lightweight model: Faster, cheaper, sufficient for most Skills
- Standard model: Only when semantic understanding needed

### Decision: Skills Directory Hierarchy
**Structure:**
```
framework/skills/    # 8 built-in Skills (defaults)
hub/skills/          # Hub-specific overrides
spoke/skills/        # Spoke-specific overrides
```

**Rationale:**
- Framework provides sensible defaults
- Hub can override for all spokes in project
- Spoke can override for local requirements
- Cascade pattern: framework → hub → spoke (most specific wins)

### Decision: Template Variables Pattern
Templates use `${VARIABLE}` syntax:
- `${EXTENSION_ID}` - Extension identifier
- `${EXTENSION_TYPE}` - spoke | project | hub
- `${MACHINE_CLASS}` - HIGH-PERFORMANCE | STANDARD | LOW-POWER
- `${TIMESTAMP}` - ISO 8601 timestamp

**Rationale:**
Shell-style variables familiar, easy to replace programmatically.

---

## Integration Points

### With Phase 2 (Registry)
- Skills referenced in registry manifests (`skills_loaded` field)
- hub-watcher reads registry for version checks
- framework-updater uses registry paths for cascades

### With Phase 1 (Lug Schema)
- session-observer creates session Lugs (type: observation)
- brief-advisor reads decision Lugs for apprenticeship
- wai-signal-advisor writes signal Lugs to hub/intake/

### With Machine Protocol
- integration-check verifies machine profile exists
- Skills adjust recommendations based on machine_class
- Session briefing shows machine optimization status

### With Wakeup Spec
- integration-check runs before briefing (step 1)
- hub-watcher runs after briefing (step 3)
- Wakeup sequence now fully specified

---

## What's Next (Phase 4)

**Phase 4: BRIEF Cascade + Command Orchestration**

1. Create hub/BRIEF.md (universal rules)
2. Create project/BRIEF.md (shared rules)
3. Create spoke/BRIEF.md (local rules)
4. Document cascade hierarchy (Hub → Project → Spoke)
5. Update brief-advisor to read cascade
6. Map /wai commands to Skills (commands → Skill invocations)
7. Closeout + Learnings

---

## Metrics

**Files Created:** 14
- 8 Skill YAMLs
- 5 template files
- 1 EXTENSION.md

**Directories Created:** 3
- framework/skills/
- hub/skills/
- spoke/skills/

**Lines of Documentation:** ~1,500 lines
- Skill definitions: ~1,200 lines
- Templates: ~200 lines
- EXTENSION.md: ~200 lines

**Use Cases Documented:** 40+ scenarios
- Average 5 use cases per Skill
- Each with scenario, behavior, impact, trigger

**Time Investment:** Advanced complexity (multi-session work)
- Use case creation: Creative work, not mechanical
- Pattern documentation: Distilling architectural decisions
- Integration specification: Cross-system coordination

---

## Origin Stories Captured

### safe-refactor Skill
**Origin:** Hub folder destroyed 2026-02-10 by rogue agent, no recovery point.
**Response:** Created guardian Skill to checkpoint before any structural change.
**Lesson:** "git is your undo button" - always checkpoint before risk.

### qc-check Skill
**Origin:** CLI rebuild phase - menu system broke despite passing tests.
**Response:** Added startup validation gate (tests passing ≠ app working).
**Lesson:** Quality gates must verify the whole system, not just unit tests.

### integration-check Skill
**Origin:** Wakeup spec requirement - verify environment before session.
**Response:** Created guardian to check Wheelwright detectable, framework importable.
**Lesson:** Session start should validate environment, not assume correctness.

---

## Reflection

**What went well:**
- Use cases ground abstract Skill contracts in reality
- Comprehensive documentation enables future reference
- Pattern capture (lightweight vs standard, cascade, overrides)

**What was challenging:**
- Use case creation requires creative scenario design
- Balancing detail (comprehensive) vs brevity (readable)
- Distilling architectural decisions into patterns

**What was learned:**
- Skills are **behavioral contracts** - not just code, but philosophy
- Use cases are **examples as specification** - show, don't just tell
- Origin stories provide **context for future maintainers** - why this exists

---

**Phase 3 Status:** COMPLETE ✅
**Next Phase:** Phase 4 - BRIEF Cascade + Command Orchestration

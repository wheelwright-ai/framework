# Phase 4 Learnings: BRIEF Cascade + Command Orchestration

**Completed:** 2026-02-12
**Impact:** 9/10

---

## What Was Accomplished

### 1. BRIEF Cascade Formalized (3 Levels)

**Hub BRIEF (`hub/BRIEF.md`):**
- Universal rules for ALL extensions
- 7 "Always" requirements (checkpoints, quality gates, observability, machine-awareness, etc.)
- 6 "Never" prohibitions (skip safety, destructive changes, commit secrets, etc.)
- Universal preferences (simplicity, observability, prevention)
- Origin stories documented (Hub destroyed 2026-02-10, quality gates from CLI rebuild)

**Project BRIEF (`project/BRIEF.md`):**
- Shared rules for all spokes in Wheelwright Framework project
- 5 project-specific "Always" requirements (document decisions, maintain use cases, version cascade, signal hygiene, phase docs)
- 4 project-specific "Never" prohibitions (breaking changes, skills without use cases, untested templates, signal spam)
- Project preferences (lightweight models, YAML configs, co-author attribution, hub-centric registry)
- Quality standards (dependency policy, testing 80%+, documentation standards, code style)

**Spoke BRIEF (`framework/BRIEF.md`):**
- Framework spoke-specific rules
- 4 spoke "Always" requirements (test Skills, template compatibility, version hooks, document framework changes)
- 3 spoke "Never" prohibitions (breaking changes without version bump, untested Skill changes, template variables without defaults)
- Spoke preferences (Python style, Skill definition style, template organization)
- Custom QC commands, file organization, code style, testing strategy

### 2. Cascade Algorithm Documented (`docs/BRIEF-CASCADE.md`)

**Key Principles:**
- Lower levels inherit higher levels (automatic)
- Lower levels can ADD rules, but cannot OVERRIDE higher-level "always/never"
- Preferences: Spoke > Project > Hub (lowest level wins)
- Hub rules are absolute (non-negotiable)

**Reading Algorithm:**
```python
def read_brief_cascade(spoke_path):
    hub_brief = read("hub/BRIEF.md")       # Required, universal
    project_brief = read("project/BRIEF.md") # Optional, shared
    spoke_brief = read("spoke/BRIEF.md")   # Optional, local

    # Merge: Hub always/never absolute
    # Project adds specificity
    # Spoke preferences override
    return merged_rules
```

**Conflict Resolution:**
1. Hub "always/never" - Absolute (highest priority)
2. Project "always/never" - Cannot be overridden by spoke
3. Spoke "always/never" - Local only
4. Preferences - Spoke > Project > Hub

**5 Use Cases Documented:**
- Universal safety (Hub blocks refactor without checkpoint)
- Project policy (justification required for dependencies)
- Spoke customization (custom quality gates)
- Cascade alignment check (decision checked against all 3 levels)
- Framework update cascade (Hub rule changes propagate to all spokes)

### 3. brief-advisor Skill Updated

Added `cascade_reading` behavior section:
- Documents 5-step algorithm for reading Hub → Project → Spoke
- Explains merge rules (Hub highest priority)
- References `docs/BRIEF-CASCADE.md` for complete algorithm
- Updated `on_pre_decision` to use cascade_reading

### 4. Command Mapping Documented (`docs/COMMAND-MAPPING.md`)

**9 Commands Mapped:**

**Session Management:**
- `/wai` → integration-check + session-observer (briefing)
- `/wai-status` → integration-check + file-audit (health check)
- `/wai-closeout` → session-observer + integration-check (session synthesis)
- `/wai-shipit` → session-observer + qc-check + safe-refactor (closeout + commit + push) [Planned]

**Quality & Validation:**
- `/check-brief` → brief-advisor (BRIEF alignment)
- `/audit-files` → file-audit (organization health)

**Framework Updates:**
- `/framework-update` → framework-updater + safe-refactor (template cascade)

**Learning & Documentation:**
- `/wai-time` → wai-context-advisor (token usage)
- `/wai-rules` → display BRIEF cascade (no Skill)

**Automatic Triggers:**
- Documented 10 Skills that fire without user command
- Event-based triggers (pre_refactor, pre_commit, session_start, etc.)

**Implementation Notes:**
- Command parsing by Claude Code skill system
- Skill execution flow diagram
- Error handling guidance
- Related documents cross-referenced

---

## Key Patterns Established

### 1. Three-Level Behavioral Hierarchy

**Pattern:** Hub (universal) → Project (shared) → Spoke (local)

**Inheritance Rules:**
- Hub defines foundation (all extensions must follow)
- Project adds shared policies (all spokes in project)
- Spoke adds local customizations (single extension)
- Lower levels inherit higher levels automatically
- Cannot override higher-level "always/never" rules

**Example:**
```yaml
# Hub BRIEF (universal)
always:
  - "Always run quality gates before commit"

# Project BRIEF (adds specificity)
always:
  - "Always run lint + tests + coverage before commit"

# Spoke BRIEF (adds detail)
always:
  - "Always run npm run lint && npm test && npm run coverage"

# Result: All three apply (spoke most specific)
```

### 2. Rule Type Priority

**Hierarchy (highest to lowest):**
1. Hub "Always" - Absolute requirement
2. Hub "Never" - Absolute prohibition
3. Project "Always" - Shared requirement
4. Project "Never" - Shared prohibition
5. Spoke "Always" - Local requirement
6. Spoke "Never" - Local prohibition
7. Preferences - Spoke > Project > Hub (inverted)

**Rationale:**
- Safety rules must be universal (Hub)
- Shared policies maintain consistency (Project)
- Local customization allows flexibility (Spoke)
- Preferences adapt to local needs (Spoke wins)

### 3. Origin Story Documentation

**Pattern:** Document WHY rules exist, not just WHAT they are

**Examples from Hub BRIEF:**
- Git checkpoint rule: "Hub destroyed 2026-02-10, no recovery"
- Quality gates rule: "CLI rebuild - menu broke despite passing tests"
- Machine classification: "LOW-POWER machine unresponsive with aggressive settings"

**Value:**
- Future maintainers understand context
- Rules feel justified, not arbitrary
- Origin stories prevent rule removal ("that'll never happen again")

### 4. Command-to-Skill Orchestration

**Pattern:** User commands invoke Skills, not direct implementation

**Flow:**
```
User: /check-brief
  ↓
Claude Code: Skill invocation
  ↓
brief-advisor Skill: Read cascade, check alignment
  ↓
Agent: Display result
```

**Benefits:**
- Skills testable independently of commands
- Commands can invoke multiple Skills (orchestration)
- Skills reusable across contexts (automatic triggers + commands)

### 5. Cascade Update Propagation

**Pattern:** Framework updates flow Hub → Project → Spoke

**Trigger:**
1. Hub updates BRIEF.md (new universal rule)
2. Framework version bumped (2.0.0 → 2.1.0)
3. hub-watcher detects version mismatch on spoke session_start
4. User runs /framework-update
5. framework-updater cascades template changes
6. Spoke inherits new Hub rule automatically

**Value:**
- Universal rules propagate to all extensions
- Breaking changes have clear migration path
- Spokes stay current with framework

---

## Critical Decisions

### Decision: Three Levels (Not Two or Four)

**Alternatives considered:**
- Two levels: Hub + Spoke (no Project)
- Three levels: Hub + Project + Spoke
- Four levels: Hub + Org + Project + Spoke

**Chosen:** Three levels (Hub + Project + Spoke)

**Resolution reason:**
- Two levels: No shared rules across spokes in same project
- Three levels: Right granularity (universal, shared, local)
- Four levels: Over-engineered for current use case

**Evidence:**
- Hub provides universal safety (all extensions)
- Project provides shared policy (Wheelwright Framework spokes)
- Spoke provides local customization (framework spoke specifics)
- Four levels would add org layer (not needed - single org)

### Decision: Hub Rules Non-Negotiable

**Alternatives considered:**
- All rules overridable (maximum flexibility)
- Hub rules can be overridden by explicit spoke opt-out
- Hub rules absolute (current design)

**Chosen:** Hub rules absolute

**Resolution reason:**
Safety rules exist because failures happened. Allowing override defeats purpose.

**Examples:**
- Git checkpoint rule: Prevents data loss (Hub destroyed 2026-02-10)
- Quality gate rule: Prevents broken code shipping
- If spoke could disable: "Just this once" becomes "always disabled"

**Implementation:**
- brief-advisor BLOCKS decisions that violate Hub "always/never"
- safe-refactor BLOCKS refactor if checkpoint fails
- qc-check BLOCKS commit if quality gates fail

### Decision: Preferences Inverted (Spoke > Hub)

**Alternatives considered:**
- Preferences follow same hierarchy as rules (Hub > Spoke)
- Preferences inverted (Spoke > Hub)

**Chosen:** Preferences inverted (Spoke > Hub)

**Resolution reason:**
- Preferences are guidelines, not requirements
- Local context knows best ("prefer simplicity" may not apply to all spokes)
- Allows spoke to say "this spoke prefers complexity for good reason"

**Implementation:**
```python
# Preferences: Spoke wins
rules["preferences"] = spoke.preferences + project.preferences + hub.preferences
# First preference in list takes precedence
```

### Decision: Command Mapping Documented (Not Implemented)

**Alternatives considered:**
- Implement all commands immediately (Phase 4)
- Document mapping, implement later (Phase 5+)

**Chosen:** Document mapping, implement later

**Resolution reason:**
- Documentation clarifies design before implementation
- Command orchestration complex (/wai-shipit needs multiple Skills)
- Phase 4 establishes contracts, Phase 5 implements

**What's documented:**
- 9 commands with expected behavior
- Skills each command invokes
- Example outputs
- Automatic trigger Skills (no command needed)

**What's deferred:**
- /wai-shipit implementation (planned Phase 5)
- /wai-teach, /wai-learn (planned Phase 6)
- Command-level error handling

---

## Integration Points

### With Phase 3 (Skills)

- brief-advisor Skill updated with cascade_reading logic
- Skills mapped to commands (/check-brief → brief-advisor)
- Automatic trigger Skills documented (no command needed)

### With Phase 2 (Registry)

- BRIEF cascade reads from hub/, project/, spoke/ paths
- framework-updater uses BRIEF cascade to detect conflicts
- hub-watcher notifies spokes when BRIEF.md template changes

### With Phase 1 (Lug Schema)

- brief-advisor reads decision Lugs for apprenticeship
- Decision Lugs include alternatives_considered, resolution_reason
- Pattern learning from decision clusters

### With Machine Protocol

- Hub BRIEF mandates "Always respect machine classification"
- Commands adjust recommendations based on machine class
- integration-check verifies machine profile exists

---

## What's Next (Phase 5)

**Phase 5: Shipit Skill + Compact Action Integration**

1. Implement /wai-shipit Skill (orchestration)
2. Add compact_action field to session summary Lug schema
3. Update session_hook to display compact action in briefing
4. Enhance qc-check with pre-commit warnings (secrets, large files, console.log)
5. Add phase tracking to WAI-State.json (current_phase, completed_phases)
6. Closeout + Learnings

---

## Metrics

**Files Created:** 6
- hub/BRIEF.md (2,000 lines)
- project/BRIEF.md (1,500 lines)
- framework/BRIEF.md (1,200 lines)
- docs/BRIEF-CASCADE.md (1,800 lines)
- docs/COMMAND-MAPPING.md (1,600 lines)
- docs/PHASE-4-LEARNINGS.md (this file)

**Directories Created:** 1
- project/ (project-level coordination)

**Lines of Documentation:** ~8,100 lines
- BRIEF files: ~4,700 lines
- Cascade algorithm: ~1,800 lines
- Command mapping: ~1,600 lines

**Rules Documented:**
- Hub: 7 Always, 6 Never, 5 Preferences
- Project: 5 Always, 4 Never, 4 Preferences
- Spoke: 4 Always, 3 Never, 4 Preferences
- **Total: 16 Always, 13 Never, 13 Preferences**

**Commands Mapped:** 9 user commands, 10 automatic Skills

**Time Investment:** Moderate complexity (single session)
- BRIEF writing: Creative policy work
- Cascade algorithm: Technical documentation
- Command mapping: Integration specification

---

## Reflection

**What went well:**
- Three-level cascade feels right (not too few, not too many)
- Origin stories add weight to rules (explain WHY)
- Hub rules as absolute prevents "just this once" erosion
- Preferences inverted makes sense (local context wins)
- Command mapping clarifies implementation before building

**What was challenging:**
- Balancing detail (comprehensive) vs brevity (readable)
- Deciding where rules belong (Hub vs Project vs Spoke)
- Avoiding duplication across three BRIEF files
- Command mapping without actual implementation (documentation-first)

**What was learned:**
- Behavioral rules need hierarchy (universal vs shared vs local)
- Origin stories prevent rule removal (context matters)
- Documentation-first design clarifies before implementation
- Preferences are guidelines (not requirements) - should be overridable

**What surprised:**
- Three levels emerged naturally (not over-designed)
- Hub BRIEF is longest (universal rules foundational)
- Spoke BRIEF is shortest (inherits most, adds least)
- Command mapping reveals orchestration complexity (/wai-shipit = 6 steps)

---

**Phase 4 Status:** COMPLETE ✅
**Next Phase:** Phase 5 - Shipit Skill + Compact Action Integration

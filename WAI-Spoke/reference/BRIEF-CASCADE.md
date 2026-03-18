# BRIEF Cascade: Hub → Project → Spoke

**Purpose:** Hierarchical behavioral rules system
**Version:** 1.0.0
**Framework:** Wheelwright v2.0.0

---

## Overview

The BRIEF cascade is a three-level hierarchical system for defining behavioral rules in Wheelwright:

```
Hub BRIEF (Universal)
  ↓ inherits + adds
Project BRIEF (Shared)
  ↓ inherits + adds
Spoke BRIEF (Local)
  = Merged Rules
```

**Key Principle:** **Lower levels inherit higher levels and can ADD rules, but cannot OVERRIDE higher-level rules.**

---

## Cascade Levels

### Level 1: Hub BRIEF (`hub/BRIEF.md`)

**Scope:** ALL extensions in the ecosystem
**Authority:** Highest (non-negotiable)
**Can be overridden:** NO

**Contains:**
- Universal safety rules (git checkpoints, quality gates)
- Machine-aware development requirements
- Session continuity mandates
- Prohibited actions (skip tests, commit secrets, etc.)
- Universal preferences (simplicity, observability, prevention)

**Example rules:**
- ✅ Always create git checkpoint before structural changes
- ❌ Never skip quality gates without approval
- Prefer simplicity over complexity

**Who updates:** Framework architects (rare, high-ceremony)

---

### Level 2: Project BRIEF (`project/BRIEF.md`)

**Scope:** All spokes in a single project
**Authority:** Medium (overrides defaults, adds shared rules)
**Can be overridden:** By Hub (NO), By Spoke (NO)

**Contains:**
- Project-wide dependency policy
- Shared testing requirements
- Documentation standards
- Code style guidelines
- Cross-spoke communication rules

**Example rules:**
- ✅ Always document architectural decisions (impact >= 8)
- ❌ Never change templates without cascade testing
- Prefer lightweight models for deterministic Skills

**Who updates:** Project coordinators (moderate ceremony)

**Inheritance:**
- Inherits ALL Hub rules (automatic)
- Adds project-specific rules
- Result: Hub + Project rules

---

### Level 3: Spoke BRIEF (`spoke/BRIEF.md`)

**Scope:** Single extension (spoke)
**Authority:** Lowest (local preferences only)
**Can be overridden:** By Hub (YES), By Project (YES)

**Contains:**
- Spoke-specific code style
- Custom quality gate commands
- Local feature flags
- Spoke-specific testing strategies
- Development workflow preferences

**Example rules:**
- ✅ Always test Skill YAML syntax before commit (framework spoke)
- Prefer co-located tests in src/ (custom spoke preference)
- Custom QC: Run `npm run lint && npm test` (override qc-check)

**Who updates:** Spoke maintainers (low ceremony)

**Inheritance:**
- Inherits ALL Hub rules (automatic)
- Inherits ALL Project rules (automatic)
- Adds spoke-specific rules
- Result: Hub + Project + Spoke rules

---

## Cascade Reading Algorithm

When `brief-advisor` checks decision alignment:

```python
def read_brief_cascade(spoke_path):
    """Read BRIEF cascade and merge rules."""

    # 1. Find Hub BRIEF (required)
    hub_brief = read_file(hub_path / "BRIEF.md")
    if not hub_brief:
        error("Hub BRIEF missing - cannot proceed")

    # 2. Find Project BRIEF (optional)
    project_brief = read_file(project_path / "BRIEF.md")

    # 3. Find Spoke BRIEF (optional)
    spoke_brief = read_file(spoke_path / "BRIEF.md")

    # 4. Merge rules (Hub highest priority)
    rules = {
        "always": [],
        "never": [],
        "preferences": []
    }

    # Hub rules (cannot be overridden)
    rules["always"].extend(hub_brief.always)
    rules["never"].extend(hub_brief.never)
    rules["preferences"].extend(hub_brief.preferences)

    # Project rules (add to Hub)
    if project_brief:
        rules["always"].extend(project_brief.always)
        rules["never"].extend(project_brief.never)
        rules["preferences"].extend(project_brief.preferences)
        # Project preferences can override Hub preferences
        # But NOT Hub always/never rules

    # Spoke rules (add to Hub + Project)
    if spoke_brief:
        rules["always"].extend(spoke_brief.always)
        rules["never"].extend(spoke_brief.never)
        # Spoke preferences override Project preferences
        # But NOT Hub/Project always/never rules
        rules["preferences"] = spoke_brief.preferences + \
                               rules["preferences"]

    return rules
```

---

## Conflict Resolution

### Rule Type Hierarchy

1. **Hub "Always" rules** - Absolute (cannot be overridden)
2. **Hub "Never" rules** - Absolute (cannot be overridden)
3. **Project "Always" rules** - Cannot be overridden by Spoke
4. **Project "Never" rules** - Cannot be overridden by Spoke
5. **Spoke "Always" rules** - Local only
6. **Spoke "Never" rules** - Local only
7. **Preferences** - Lower levels override higher levels

### Conflict Examples

**Example 1: Hub rule violated**
```yaml
# Hub BRIEF
never:
  - "Never commit secrets (.env files)"

# Spoke BRIEF (INVALID - cannot override)
always:
  - "Always commit .env for deployment"
```
**Result:** brief-advisor BLOCKS, Hub rule wins

**Example 2: Preference override (valid)**
```yaml
# Hub BRIEF
preferences:
  - "Prefer simplicity over complexity"

# Spoke BRIEF (VALID - preferences can override)
preferences:
  - "Prefer feature-rich solutions for this spoke"
```
**Result:** Spoke preference wins (preferences are guidelines)

**Example 3: Adding specificity (valid)**
```yaml
# Project BRIEF
always:
  - "Always run tests before commit"

# Spoke BRIEF (VALID - adds specificity)
always:
  - "Always run lint + tests + type-check before commit"
```
**Result:** Both rules apply (spoke adds detail)

---

## Use Cases

### Use Case 1: Universal Safety (Hub)
**Scenario:** Agent wants to refactor without git checkpoint
**What happens:**
1. brief-advisor reads Hub BRIEF
2. Finds "Always create checkpoint before refactor"
3. Checks if checkpoint exists
4. BLOCKS refactor if no checkpoint

**Why it matters:** Hub rule protects all spokes from data loss

---

### Use Case 2: Project Policy (Project)
**Scenario:** Spoke wants to add dependency without justification
**What happens:**
1. brief-advisor reads Hub + Project BRIEFs
2. Finds Project rule: "Always justify new dependencies (decision Lug)"
3. Checks if decision Lug created
4. WARNS if no justification (soft enforcement)

**Why it matters:** Project rule maintains shared dependency policy

---

### Use Case 3: Spoke Customization (Spoke)
**Scenario:** Spoke has custom quality gates (linting)
**What happens:**
1. qc-check reads framework default: "Run pytest"
2. Checks for spoke/skills/qc-check.yaml override
3. Finds custom_commands: ["npm run lint", "npm test"]
4. Runs spoke commands instead of default

**Why it matters:** Spoke can customize without breaking Hub/Project rules

---

### Use Case 4: Cascade Alignment Check
**Scenario:** Agent makes architectural decision (impact: 9)
**What happens:**
1. brief-advisor reads Hub + Project + Spoke BRIEFs
2. Merges rules (Hub highest priority)
3. Checks decision against merged rules:
   - Hub: "Always use PEV for high-impact decisions" ✓
   - Project: "Always document alternatives_considered" ✓
   - Spoke: "Always test architectural changes" ✓
4. All rules satisfied, decision approved

**Why it matters:** Cascade ensures compliance at all levels

---

### Use Case 5: Framework Update Cascade
**Scenario:** Hub BRIEF updated with new universal rule
**What happens:**
1. Hub updates hub/BRIEF.md, increments version
2. framework-updater detects BRIEF.md template change
3. Spokes' hub-watcher notifies on session_start
4. User runs /framework-update
5. New Hub rule now applies to all spokes (automatic)

**Why it matters:** Universal rules cascade to all extensions

---

## Integration with Skills

### Skills That Read BRIEF Cascade

**brief-advisor (primary):**
- Reads Hub + Project + Spoke BRIEFs
- Merges rules (Hub highest priority)
- Checks decision alignment
- Warns on violations
- Learns preferences from decision Lugs

**framework-updater:**
- Reads Project BRIEF when cascading templates
- Checks if template updates conflict with project rules
- Human gate if BRIEF.md template changed

**qc-check:**
- Reads spoke/skills/qc-check.yaml (override)
- Falls back to framework default if no override
- Respects Hub rule: "Always run quality gates"

### Skills That Enforce BRIEF Rules

**Guardian Skills:**
- **safe-refactor:** Enforces Hub "Always checkpoint before refactor"
- **integration-check:** Enforces Hub "Always validate environment"

**Reviewer Skills:**
- **qc-check:** Enforces Hub "Always run quality gates"
- **file-audit:** Enforces Hub preference "Preventive over reactive"

**Advisor Skills:**
- **brief-advisor:** Enforces all BRIEF rules (cascade)
- **wai-foundation-advisor:** Enforces Hub "Never proceed on uncertain foundation"

---

## Viewing the Cascade

### Command Line
```bash
# View full cascade
cat hub/BRIEF.md          # Level 1: Universal
cat project/BRIEF.md      # Level 2: Shared
cat spoke/BRIEF.md        # Level 3: Local

# Check alignment
/check-brief              # brief-advisor reads cascade
```

### Session Briefing
```
Machine: workstation (HIGH-PERFORMANCE, 64GB RAM)
Project: Wheelwright Framework
BRIEF Cascade: Hub v1.0 + Project v1.0 + Spoke v1.0
Last session: Phase 3 completed - Skills directory created
```

---

## Maintenance

### Updating Hub BRIEF
**Ceremony:** High (affects all extensions)
**Process:**
1. Create architectural decision Lug (impact: 10)
2. Update hub/BRIEF.md
3. Increment Hub BRIEF version
4. Update framework_version (triggers cascade)
5. Commit with detailed explanation
6. hub-watcher notifies all spokes

### Updating Project BRIEF
**Ceremony:** Moderate (affects all spokes in project)
**Process:**
1. Create decision Lug (impact: 8+)
2. Update project/BRIEF.md
3. Increment Project BRIEF version
4. Commit with explanation
5. Notify spokes if behavior changes

### Updating Spoke BRIEF
**Ceremony:** Low (local changes only)
**Process:**
1. Edit spoke/BRIEF.md
2. Focus on spoke-specific rules (don't repeat Hub/Project)
3. Commit with brief explanation
4. No notification needed

---

## Testing Cascade

### Validation Checklist
- [ ] Hub BRIEF exists and is readable
- [ ] Project BRIEF inherits Hub (no conflicting "always/never")
- [ ] Spoke BRIEF inherits Hub + Project (no conflicts)
- [ ] brief-advisor can read all three levels
- [ ] Merged rules have no contradictions
- [ ] Preferences override correctly (Spoke > Project > Hub)
- [ ] Always/never rules enforce correctly (Hub highest)

### Test Scenario
```python
# Test cascade reading
def test_brief_cascade():
    rules = read_brief_cascade("framework/")

    # Hub rule present
    assert "Always create checkpoint" in rules["always"]

    # Project rule present
    assert "Always document decisions" in rules["always"]

    # Spoke rule present
    assert "Always test Skills" in rules["always"]

    # Preference override (Spoke wins)
    assert rules["preferences"][0].startswith("Spoke:")
```

---

## Related Documents

- **hub/BRIEF.md** - Universal rules (Level 1)
- **project/BRIEF.md** - Project rules (Level 2)
- **spoke/BRIEF.md** - Spoke rules (Level 3)
- **framework/skills/brief-advisor.yaml** - BRIEF enforcement Skill
- **COMMAND-MAPPING.md** - /check-brief command

---

**Document Version:** 1.0.0
**Framework Version:** 2.0.0
**Last Updated:** 2026-02-12 (Phase 4 - BRIEF cascade formalized)

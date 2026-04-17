# BRIEF - Framework Spoke Rules

**Scope:** Framework spoke only (wheelwright/framework)
**Level:** Spoke (inherits Hub + Project, adds local rules)
**Last Updated:** 2026-02-12

---

## Purpose

This BRIEF defines **spoke-specific behavioral rules** for the Wheelwright Framework spoke. This spoke contains the core framework implementation (Skills, templates, session hooks).

**Inheritance:**
- ✅ **Inherits ALL Hub rules** (universal, non-negotiable)
- ✅ **Inherits ALL Project rules** (shared across spokes)
- ➕ **Adds framework-specific rules** (below)

**Cascade:**
- Hub BRIEF → Project BRIEF → **Spoke BRIEF (this file)**

---

## Always (Framework Spoke Requirements)

In addition to Hub + Project rules:

### 1. Test Skills Before Committing
- ✅ **Always** validate Skill YAML syntax before commit
- ✅ **Always** verify trigger conditions are testable
- ✅ **Always** ensure use cases reference real scenarios (not hypothetical)
- ✅ **Always** test Skill behavior changes with framework spoke

**Rationale:** Skills define framework behavior. Broken Skills break all spokes.

### 2. Maintain Template Compatibility
- ✅ **Always** test template variable substitution before commit
- ✅ **Always** provide default values for new template variables
- ✅ **Always** document template changes in CHANGELOG.md (if exists)
- ✅ **Always** verify templates render correctly with spoke data

**Rationale:** Templates cascade to all spokes. Errors propagate widely.

### 3. Version Session Hooks
- ✅ **Always** maintain backward compatibility in session_hook.py
- ✅ **Always** test briefing display format changes
- ✅ **Always** verify closeout_validator with spoke data
- ✅ **Always** document breaking changes with migration path

**Rationale:** Session hooks are framework API. Breaking changes disrupt all spokes.

### 4. Document Framework Changes
- ✅ **Always** update framework_version when making breaking changes
- ✅ **Always** create migration guide for schema changes
- ✅ **Always** test cascade flow (framework → hub → spoke)
- ✅ **Always** notify via hub-watcher when framework updates

**Rationale:** Spokes depend on framework. Changes need clear communication.

---

## Never (Framework Spoke Prohibitions)

In addition to Hub + Project prohibitions:

### 1. Breaking Changes Without Version Bump
- ❌ **Never** change Skill contract without framework version bump
- ❌ **Never** modify template structure without cascade testing
- ❌ **Never** alter Lug schema without migration documentation
- ❌ **Never** remove session hook functions without deprecation

**Rationale:** Framework is dependency. Semantic versioning required.

### 2. Untested Skill Changes
- ❌ **Never** modify Skill behavior without use case validation
- ❌ **Never** add triggers without testing fire conditions
- ❌ **Never** change output format without spoke compatibility check
- ❌ **Never** deploy Skills that fail their own test scenarios

**Rationale:** Skills guard behavior. Broken guards break safety.

### 3. Template Variables Without Defaults
- ❌ **Never** add required template variables without default values
- ❌ **Never** use undefined variables in templates
- ❌ **Never** break template rendering with invalid syntax
- ❌ **Never** commit templates without substitution testing

**Rationale:** Templates must render safely. Missing defaults = broken cascade.

---

## Preferences (Framework Spoke Guidelines)

In addition to Hub + Project preferences:

### 1. Python Implementation Style
- Prefer **standard library** over external dependencies
- Prefer **explicit imports** over wildcard imports
- Prefer **type hints** for public APIs (session_hook, validators)
- Prefer **docstrings** for modules and public functions

### 2. Skill Definition Style
- Prefer **YAML format** for Skill definitions (not JSON)
- Prefer **use_cases first** (most important section for understanding)
- Prefer **origin stories** for guardian Skills (explain why they exist)
- Prefer **real scenarios** in use cases (not "when user does X")

### 3. Template Organization
- Prefer **${VARIABLE}** syntax for substitution (shell-style)
- Prefer **alphabetical variable order** in templates (where order doesn't matter)
- Prefer **comments** explaining non-obvious template sections
- Prefer **consistent indentation** (2 spaces for YAML, 4 for Python)

### 4. Documentation Location
- Prefer **inline use cases** in Skill YAMLs (not separate docs)
- Prefer **LEARNINGS.md** for phase retrospectives
- Prefer **EXTENSION.md** for framework identity
- Prefer **comments in code** only for non-obvious logic

---

## Framework Spoke Quality Gates

### Custom QC Commands

This spoke uses custom quality gates (spoke/skills/qc-check.yaml if created):

```yaml
# Example: Framework spoke custom QC (not yet created)
custom_commands:
  - "python -m pytest wai/tests/"           # Unit tests
  - "python -m wai.schema --validate"        # Schema validation
  - "python -m wai.closeout_validator --check"  # Closeout readiness
startup_command: "python -m wai --version"   # Verify importable
coverage_threshold: 80
```

### File Organization
- **wai/**: Python implementation
- **skills/**: Built-in Skill YAMLs (8 Skills)
- **templates/**: Cascade templates (5 files)
- **docs/**: Phase learnings, specifications
- **EXTENSION.md**: Framework identity

### Sprawl Prevention
- **Root files:** Limit to 10 files (EXTENSION.md, BRIEF.md, setup.py, etc.)
- **Config files:** Single format preferred (YAML)
- **Tests:** Co-located with source (wai/tests/)
- **Documentation:** Centralized in docs/

---

## Spoke-Specific Rules

### Code Style
- **Python:** PEP 8 (use black if available, but not required)
- **Line length:** 100 characters (not strict, but preferred)
- **Imports:** Standard lib, third-party, local (grouped, alphabetical)
- **Naming:** snake_case for functions/variables, PascalCase for classes

### Commit Style
- **Phase commits:** "WAI v2 Phase {N}: {Description}"
- **Feature commits:** "feat: {Description}"
- **Fix commits:** "fix: {Description}"
- **Doc commits:** "docs: {Description}"
- **Always include:** Compact action for next phase (on phase commits)

### Testing Strategy
- **Unit tests:** For schema validation, hook functions
- **Integration tests:** For cascade flow (template updates)
- **Scenario tests:** Match Skill use_cases (test what Skills claim)
- **Startup tests:** Verify framework importable (qc-check gate)

### Feature Flags
None currently. If experimental features added:
- Use `features.yaml` in framework root
- Document in EXTENSION.md
- Gate with environment variables or config

---

## Integration Points

### Skills Defined in This Spoke

Framework spoke **defines** the 8 built-in Skills:
- safe-refactor, qc-check, hub-watcher, framework-updater
- brief-advisor, session-observer, file-audit, integration-check

**Responsibility:** Maintain use cases, test scenarios, origin stories.

### Templates Provided

Framework spoke **provides** 5 templates:
- WAI-Manifest.yaml.template
- WAI-Lugs.jsonl.template
- BRIEF.md.template
- EXTENSION.md.template
- PROJECT.md.template

**Responsibility:** Test substitution, maintain backward compatibility.

### Session Hooks

Framework spoke **implements** session hooks:
- `wai.session_hook.get_session_start_briefing()` (wakeup)
- `wai.closeout_validator` (session end validation)
- `wai.hooks.get_machine_status()` (machine optimization)

**Responsibility:** Maintain API stability, document changes.

---

## Maintenance

### Updating Framework Spoke BRIEF

**When to update:**
- New Skill added (update quality gates)
- Template structure changed (update testing requirements)
- Code style decision made (document in preferences)

**Process:**
1. Edit this file (spoke/BRIEF.md)
2. Do NOT repeat Hub or Project rules (inheritance automatic)
3. Commit with explanation
4. No spoke notification needed (local changes only)

### Checking Cascade

```bash
# View full cascade
cat hub/BRIEF.md          # Universal rules
cat project/BRIEF.md      # Project rules
cat spoke/BRIEF.md        # This file

# Check alignment
/check-brief              # brief-advisor reads cascade
```

---

## Related Documents

- **hub/BRIEF.md** - Universal rules (inherited)
- **project/BRIEF.md** - Project rules (inherited)
- **EXTENSION.md** - Framework spoke identity
- **SKILL-CONTRACT-SPECIFICATION.md** - Skill structure
- **AI-AGENT-MACHINE-PROTOCOL.md** - Machine optimization

---

**Spoke BRIEF Version:** 1.0.0
**Framework Version:** 2.0.0
**Inherits:** Hub BRIEF v1.0.0 + Project BRIEF v1.0.0
**Last Updated:** 2026-02-12 (Phase 4 - BRIEF cascade formalized)

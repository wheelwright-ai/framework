# Command Mapping: /wai Commands → Skills

**Purpose:** Document how user commands map to Skill invocations
**Version:** 1.0.0
**Framework:** Wheelwright v2.0.0

---

## Overview

Wheelwright provides user-facing commands (prefixed with `/wai`) that invoke Skills or framework functions. This document maps commands to their implementations.

**Command Structure:**
```
/wai-{action}  →  Skill invocation OR framework function
```

---

## Command Reference

### Session Management Commands

#### `/wai` - Unified Briefing
**Implementation:** `wai.session_hook.get_session_start_briefing()`
**When to use:** Session start (automatic) or on-demand refresh

**What it does:**
1. integration-check verifies environment
2. Display machine status (classification, RAM, optimization)
3. Show recent work summary (last session Lug)
4. List failed observations (requiring remediation)
5. Show incomplete Lugs (in-progress work)
6. Display session statistics

**Output example:**
```
✓ IDE optimized for workstation (HIGH-PERFORMANCE, 64GB RAM)

Project: Wheelwright Framework
Last session: Phase 3 completed - Skills directory created

Action items:
- Resume: Phase 4 - BRIEF cascade + command orchestration

Environment: Claude Code CLI, framework v2.0.0
```

**Skills invoked:**
- integration-check (environment verification)
- session-observer (reads last session summary Lug)

---

#### `/wai-status` - Health Check
**Implementation:** `wai.closeout_validator.check_status()`
**When to use:** Check extension health anytime

**What it does:**
1. Check git status (clean or uncommitted changes)
2. Check observations logged (count)
3. Check framework detectable (import test)
4. Check machine profile exists
5. Report overall health score

**Output example:**
```
Extension Health Check:
  ✓ Git: Clean working tree
  ✓ Observations: 5 logged this session
  ✓ Framework: v2.0.0 (importable)
  ✓ Machine: workstation profile exists

Health Score: 100/100
```

**Skills invoked:**
- integration-check (environment verification)
- file-audit (organization health)

---

#### `/wai-closeout` - End Session Ceremony
**Implementation:** `wai.closeout_validator.run_closeout()`
**When to use:** End of session (before commit)

**What it does:**
1. session-observer synthesizes session summary
2. closeout_validator checks git, observations, framework
3. Create session summary Lug
4. Generate compact action for next session (3-6 steps)
5. Report closeout status

**Output example:**
```
Session Closeout:
  ✓ Git status: 12 files staged, ready to commit
  ✓ Observations: 3 high-impact events logged
  ✓ Session summary: Created (Lug: session-2026-02-12-001)

Compact Action for Next Session:
1. Create hub/BRIEF.md
2. Document BRIEF cascade
3. Map /wai commands
4. Update brief-advisor
5. Closeout with learnings

Ready for commit.
```

**Skills invoked:**
- session-observer (session synthesis)
- integration-check (final validation)

---

#### `/wai-shipit` - Closeout + Commit + Push
**Implementation:** Orchestrated workflow (future Skill)
**When to use:** End session with commit and push

**What it does:**
1. Run /wai-closeout (session synthesis)
2. Run qc-check (quality gates)
3. Stage all files (git add -A)
4. Create structured commit message:
   - Title: "{Phase}: {Description}"
   - Body: Completed, Impact, Next, Compact Action
   - Footer: Co-Authored-By attribution
5. Commit with message
6. Push to remote (if configured)
7. Report commit SHA and push status

**Output example:**
```
Running /wai-shipit...

Closeout: ✓ Session synthesized
Quality Gates: ✓ Tests passed (48/48)
Commit: ✓ 4e0d0d1 "WAI v2 Phase 4: BRIEF cascade"
Push: ✓ Pushed to origin/wai-v2-migration

Session complete! 🎉
Next: Resume Phase 5 (see compact action in commit)
```

**Skills invoked:**
- session-observer (closeout)
- qc-check (quality gates)
- safe-refactor (checkpoint if needed)

**Status:** Planned (Phase 5 implementation)

---

### Quality & Validation Commands

#### `/check-brief` - BRIEF Alignment Check
**Implementation:** Skill invocation (`brief-advisor`)
**When to use:** Before making significant decisions

**What it does:**
1. Read BRIEF cascade (Hub → Project → Spoke)
2. Extract current decision context
3. Check alignment with BRIEF rules
4. Search past decisions for similar scenarios
5. Advise: aligned, warning (violates BRIEF), or note (differs from past)

**Output example:**
```
BRIEF Alignment Check:

Decision: Add new dependency (lodash)

BRIEF Rules:
  ✓ Hub: "Always justify new dependencies"
  ⚠ Project: "Prefer minimize dependencies"

Past Decisions:
  • Decision abc123: Rejected lodash, used native methods

Recommendation:
  NOTE: Different from past decision abc123
  Past rationale: "Native methods sufficient for our use case"

Consider: Why is native approach insufficient now?
```

**Skills invoked:**
- brief-advisor (alignment check)

---

#### `/audit-files` - File Organization Health
**Implementation:** Skill invocation (`file-audit`)
**When to use:** Check for sprawl or disorganization

**What it does:**
1. Scan project structure (file counts, depth, naming)
2. Detect sprawl patterns (flat root, config sprawl, orphans)
3. Check against declared structure (EXTENSION.md)
4. Calculate health score (0-10)
5. Report issues and recommendations

**Output example:**
```
File Organization Audit:

Health Score: 7/10

Issues:
  ⚠ Minor: 12 files in project root (recommend: < 10)
  ⚠ Minor: 3 config formats (.yaml, .yml, .json)

Recommendations:
  - Move scripts to scripts/ directory
  - Standardize config format (prefer .yaml)

Overall: Minor organization issues, address when convenient.
```

**Skills invoked:**
- file-audit (organization check)

---

### Framework Update Commands

#### `/framework-update` - Cascade Template Updates
**Implementation:** Skill invocation (`framework-updater`)
**When to use:** After hub-watcher notifies of framework update

**What it does:**
1. Compare hub framework_version with spoke framework_version
2. Read changed templates from framework/templates/
3. For each template:
   - Check if spoke has local modifications
   - Auto-update if no mods, or show diff and ask
4. Update spoke WAI-Manifest.yaml framework_version
5. Record update in observations.jsonl

**Output example:**
```
Framework Update: v2.0.0 → v2.1.0

Templates Changed:
  ✓ WAI-Manifest.yaml - Updated (no local mods)
  ⚠ BRIEF.md - Conflict detected (local mods exist)

BRIEF.md Conflict:
  Hub added: "Always use PEV for high-impact decisions"
  Spoke modified: Section 3 (custom rule added)

Action required:
  [1] Accept hub template (lose spoke changes)
  [2] Keep spoke version (skip this update)
  [3] Merge manually (show 3-way diff)

Choice: 3

[Shows diff...]
Merge complete. Review changes before commit.
```

**Skills invoked:**
- framework-updater (template cascade)
- safe-refactor (checkpoint before updates)

---

### Learning & Documentation Commands

#### `/wai-time` - Token Usage Summary
**Implementation:** Framework function (token tracking)
**When to use:** Check context usage during session

**What it does:**
1. Read session token usage (from Claude Code)
2. Calculate: used, remaining, percentage
3. Show context warnings if approaching limits
4. Suggest: context management if > 80%

**Output example:**
```
Token Usage:
  Used: 65,432 / 200,000 (32.7%)
  Remaining: 134,568

Context Status: ✓ Healthy
```

**Skills invoked:**
- wai-context-advisor (if > 60% used)

---

#### `/wai-rules` - Show BRIEF Cascade
**Implementation:** Framework function (file display)
**When to use:** Review behavioral rules

**What it does:**
1. Display hub/BRIEF.md (universal rules)
2. Display project/BRIEF.md (if exists)
3. Display spoke/BRIEF.md (if exists)
4. Show cascade summary (inheritance chain)

**Output example:**
```
BRIEF Cascade:

Hub Rules (universal):
  Always: Git checkpoints, quality gates, observe work
  Never: Skip tests, commit secrets, break continuity

Project Rules (shared):
  Always: Document decisions, maintain Skill use cases
  Never: Breaking changes without migration

Spoke Rules (local):
  Always: Test Skills before commit
  Prefer: Co-located tests

Cascade: Hub v1.0 + Project v1.0 + Spoke v1.0
```

**Skills invoked:** None (display only)

---

### Future Commands (Planned)

#### `/wai-teach` - Hub Learning (Hub Only)
**Implementation:** Hub-specific Skill
**When to use:** Submit learnings from spoke to hub
**Status:** Planned (Phase 6)

#### `/wai-learn` - Acknowledge Hub Signals (Hub Only)
**Implementation:** Hub-specific Skill
**When to use:** Review and adopt hub/intake/ signals
**Status:** Planned (Phase 6)

#### `/wai-green-light` - Approve Work to Proceed
**Implementation:** Foundation validation override
**When to use:** Explicit approval when foundation uncertain
**Status:** Exists (from v1)

#### `/wai-red-light` - Block Work from Proceeding
**Implementation:** Foundation validation block
**When to use:** Explicit block when scope unclear
**Status:** Exists (from v1)

---

## Command-to-Skill Mapping Table

| Command | Skill(s) Invoked | Model | Purpose |
|---------|------------------|-------|---------|
| `/wai` | integration-check, session-observer | lightweight | Session briefing |
| `/wai-status` | integration-check, file-audit | lightweight | Health check |
| `/wai-closeout` | session-observer, integration-check | lightweight | Session synthesis |
| `/wai-shipit` | session-observer, qc-check, safe-refactor | standard | Complete closeout + commit + push |
| `/check-brief` | brief-advisor | standard | BRIEF alignment check |
| `/audit-files` | file-audit | lightweight | Organization health |
| `/framework-update` | framework-updater, safe-refactor | standard | Template cascade |
| `/wai-time` | wai-context-advisor (optional) | lightweight | Token usage |
| `/wai-rules` | None | n/a | Display BRIEF cascade |

---

## Automatic Skill Triggers (No Command Needed)

Some Skills fire automatically on events, no user command required:

| Skill | Trigger Event | When It Fires |
|-------|---------------|---------------|
| safe-refactor | pre_refactor | Before any structural change |
| qc-check | pre_commit, pre_shipit | Before git commit |
| hub-watcher | session_start | On every session start |
| brief-advisor | pre_decision (impact >= 7) | Before high-impact decisions |
| session-observer | significant_event (impact >= 6) | On high-impact events |
| file-audit | session_start | On every session start |
| integration-check | session_start | First thing on session start |
| wai-complexity-advisor | 2+ files OR 6+ steps | When complexity threshold hit |
| wai-context-advisor | 60%, 80%, 90% context | When context thresholds crossed |
| wai-signal-advisor | impact >= 8 | On high-impact decisions/observations |

---

## Implementation Notes

### Command Parsing
Commands are parsed by Claude Code skill system:
1. User types `/wai-{action}` in chat
2. Claude Code recognizes as skill invocation
3. Skill tool executes corresponding skill file
4. Skill returns output to Claude
5. Claude displays result to user

### Skill Execution Flow
```
User: /check-brief
  ↓
Claude Code: Recognize skill invocation
  ↓
Skill Tool: Load templates/commands/wai-brief-advisor.md
  ↓
Agent: Execute brief-advisor logic
  ↓
brief-advisor Skill: Read BRIEF cascade, check alignment
  ↓
Agent: Return alignment result
  ↓
User: See alignment check output
```

### Error Handling
If skill invocation fails:
1. Check skill file exists (templates/commands/wai-{action}.md)
2. Check prerequisites met (BRIEF.md exists, etc.)
3. Show helpful error message
4. Suggest: Run /wai-status to check environment

---

## Related Documents

- **SKILL-CONTRACT-SPECIFICATION.md** - Skill structure and roles
- **BRIEF-CASCADE.md** - BRIEF hierarchy and reading algorithm
- **framework/skills/*.yaml** - Skill definitions (8 built-in Skills)
- **templates/commands/*.md** - User-facing skill files (for Claude Code)

---

**Document Version:** 1.0.0
**Framework Version:** 2.0.0
**Last Updated:** 2026-02-12 (Phase 4 - Command orchestration mapped)

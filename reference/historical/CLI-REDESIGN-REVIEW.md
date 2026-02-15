# CLI Redesign Proposal Review
**Date:** 2026-02-08  
**Reviewer:** Amp (Rush Mode)  
**Status:** ✅ GOOD DIRECTION | ⚠️ NEEDS CLARIFICATION

---

## Executive Summary

**Verdict:** The proposal has **strong fundamentals** (dynamic menus, node-centric design, visual feedback) but requires significant **clarification on scope, integration, and priorities** before implementation.

### Quick Score
- **Vision:** 9/10 (bold, clear, coherent)
- **Feasibility:** 6/10 (depends on scope decisions)
- **Implementability:** 5/10 (needs detailed plan for migration)
- **Risk:** Medium (large refactor with existing mature code)

---

## ✅ STRENGTHS

### 1. **Dynamic Menu Generation from Skills** (Excellent Idea)
- **Why it works:** Eliminates menu/skill sync problems exposed in audit
- **Impact:** Every new skill = automatic CLI presence
- **Implementation:** Replace hardcoded menu lists in `core.py` with skill-driven generation
- **Current gap:** Skills.jsonl has `wai_cli` triggers but menus are manually coded

### 2. **Node-Centric Design** (Correct Focus)
- **Hub & Spoke as first-class objects:** Aligns with Wheelwright mental model
- **Clear verb-noun structure:** `wai learn NodeA`, `wai teach NodeB` (vs current nested menus)
- **Scalability:** Easier to add new nodes/actions without restructuring menus

### 3. **Visual Feedback & Animations** (Good UX)
- **User engagement:** Wheels, spinners, progress bars → feels modern
- **Status clarity:** Animations show task progress naturally
- **Brand consistency:** Wheelwright = rolling forward = visual metaphor works

### 4. **Separation of Concerns** (Clean Architecture)
```
wai.py          → entry point
commands/       → verb logic (learn.py, teach.py, etc.)
lib/            → menu_generator.py reusable
visuals/        → rendering isolated
data/           → skills.json, lug.json config-driven
```

### 5. **Extensibility** (Future-Proof)
- Add skill → updates CLI automatically
- Add node type → verb-noun pattern still works
- New visual → visuals/ folder isolated

---

## ⚠️ CRITICAL ISSUES

### 1. **Ambiguous Scope: Complete Rewrite vs. Refactor?**

**The Problem:**
- Proposal shows `cli/` folder structure but doesn't state if it **replaces** `wai/core.py` or **coexists**
- Current `wai/core.py` has 5000+ lines with:
  - 40+ commands (init, hub, projects, groups, status, closeout, shipit, etc.)
  - Interactive menus (not just CLI flags)
  - Hub/spoke management already implemented
  - Project discovery, groups, baseline tracking
- New proposal mentions only 5 commands: `init`, `learn`, `teach`, `stats`, `review`

**Questions:**
1. Do `learn` and `teach` **replace** current hub-sync workflows?
2. Where do `closeout`, `shipit`, `sync`, `baseline`, `projects add`, `groups` go?
3. Is this a **complete rewrite** (breaking change) or **parallel UI**?

**Recommendation:**
```
✅ CLARIFY: Define which existing commands stay/go/migrate
   - Inventory current 40+ commands
   - Map each to new verb-noun structure (if applicable)
   - Identify which are "core" vs. "legacy"
```

---

### 2. **Skills.json vs. WAI-Skills.jsonl (Data Source Confusion)**

**The Problem:**
```
Proposal says:
  data/skills.json         # All Skills definitions
  lib/menu_generator.py    # Builds CLI menus from Skills

But the framework has:
  WAI-Spoke/WAI-Skills.jsonl    # 17 skills already documented
  wai/valid_options.json        # Command definitions exist
```

**Questions:**
1. **Create new `data/skills.json`** or **reuse WAI-Skills.jsonl**?
2. **What schema** for skills.json? (It differs from current `.jsonl`)
3. **Single source of truth**: Should Skills live in `wai/` or `cli/`?
4. **How does WAI-State.json integration work** with new skills structure?

**Recommendation:**
```
✅ CLARIFY: Define unified Skills data model
   Option A: Migrate WAI-Skills.jsonl → cli/data/skills.json
   Option B: Keep .jsonl, create adapter layer in menu_generator.py
   Option C: Hybrid - .jsonl is authority, CLI reads it directly
```

---

### 3. **LUG Integration Feels Tangential**

**The Problem:**
```
Proposal mentions:
  data/lug.json            # Build/design instructions
  lib/menu_generator.py uses LUG for:
    - Default hub/spoke layout and colors
    - Animation preferences
    - Workflow constraints (teach_requires_hub)

But LUG is fundamentally:
  - Task dependency graphs (not UI config)
  - Work-tracking system (not CLI styling)
```

**Questions:**
1. **Why is LUG responsible for animation colors and hub/spoke layout?**
2. **Isn't this a UI config** (should be in Skills or separate config)?
3. **Does mixing concerns** (task graph + UI prefs) create debt?

**Recommendation:**
```
✅ REFACTOR: Separate concerns
   data/skills.json       → command definitions & help text
   data/config.json       → UI prefs, animations, colors, layouts
   data/lug.json          → remains task/dependency graph (read-only ref)
   
   Or: Put visual config IN skills.json under "ui_hints" key
```

---

### 4. **Interactive Menus vs. CLI Flags (Silent Paradigm Shift)**

**The Problem:**
Current CLI has **both**:
```
wai                      # No args → interactive menu
wai status mynode        # Direct command
wai projects add         # Submenu navigation
```

Proposal seems to be **pure CLI flags**:
```
wai learn NodeA --from hub
wai teach NodeB --to hub
wai stats NodeA --format table
```

**Lost in transition:**
- Discovery menus (user browses projects, selects one)
- Guided workflows (step-by-step initialization)
- Contextual help (dynamic based on state)

**Questions:**
1. **Does new design still support interactive mode** (`wai` with no args)?
2. **How do users discover available nodes** without flags?
3. **How do first-time users initialize hub/spoke** with flags alone?

**Recommendation:**
```
✅ CLARIFY: Hybrid approach
   wai                          # Still interactive menu (default)
   wai learn NodeA [flags]      # CLI-direct option (power users)
   wai --interactive learn      # Force interactive even with args
```

---

### 5. **Animation as Requirement vs. Nice-to-Have (Scope Creep Risk)**

**The Problem:**
Proposal dedicates significant space to animations:
```
visuals/
  ├── welcome_animation.py
  └── wheel_render.py

Build plan includes:
  "Create Welcome Animation: ASCII + colors + dynamic effects"
```

**Is this blocking?**
- ✅ Nice for branding/UX
- ❌ Adds complexity (blessed/rich dependencies)
- ❌ May not be priority given audit found 10 missing skills
- ❌ Terminal support varies (especially in WSL/CI)

**Recommendation:**
```
✅ SEPARATE: Make animations optional/phased
   
   Phase 1 (MVP): Dynamic menus + verb-noun structure
   Phase 2 (UX enhancement): Rich tables, progress bars
   Phase 3 (Brand): Animations, wheel rendering
   
   Config: animations: false/true in config.json
```

---

## 🚨 INTEGRATION CHALLENGES

### Issue: How does new CLI read/write WAI-State.json, sessions, etc.?

**Current flow:**
```
core.py reads:
  - WAI-Spoke/WAI-State.json (project state)
  - WAI-Spoke/WAI-Session-Log.jsonl (conversation log)
  - WAI-Spoke/WAI-Lugs.jsonl (task graph)
```

**New design doesn't mention:**
- Where CLI reads/writes state
- How it integrates with session hooks
- How it coordinates with IDE integrations

**Recommendation:**
```
✅ CLARIFY: State management architecture
   - State layer: Keep current WAI-State.json reading/writing
   - Session layer: Integration with session-start hooks
   - Data layer: How menu_generator.py accesses state
```

---

## ⚠️ TECHNICAL DEBT CONCERNS

### 1. **Typer + Rich Dependency Chain**
- ✅ Typer: Good for dynamic CLI
- ✅ Rich: Industry standard for formatting
- ⚠️ Blessed: Adds complexity for animations (terminal-specific)
- ❓ Current code uses basic argparse - is big refactor worth it?

**Recommendation:**
```
✅ PHASE approach:
   MVP: argparse + standard output (minimal change)
   Phase 2: Upgrade to Typer + Rich (incremental)
   Phase 3: Add Blessed only if animations are must-have
```

---

### 2. **Test Coverage & Migration Risk**
- Current `wai/core.py` has no mention of unit tests in this proposal
- Big refactor = high risk of regressions
- Need integration tests for all 40+ commands

**Recommendation:**
```
✅ TESTING PLAN:
   1. Write integration tests for existing commands FIRST
   2. Implement new CLI in parallel (don't break old one)
   3. Gradually migrate commands from old → new
   4. Parallel operation for N releases before full cutover
```

---

## 📋 IMPLEMENTATION PATHWAY ISSUES

**Current Build Plan:**
```
1. Define Skills JSON & LUG JSON fully
2. Build Menu Generator
3. Create Welcome Animation
4. Implement Node Workflows
5. Add Visual Feedback
6. Testing
7. Iterate
```

**Problems:**
- ❌ Starts with design (Skills JSON) but doesn't map to existing code
- ❌ "Testing" is step 6, not step 0
- ❌ No migration strategy for existing commands
- ❌ No clear definition of "Phase 0: Audit & Inventory"

**Better sequence:**
```
Phase 0: Audit & Inventory (FIRST)
  □ List all 40+ current commands
  □ Map to new verb-noun structure
  □ Identify "rewrite vs. keep" decisions
  □ Define backward compatibility requirements

Phase 1: Foundation (non-breaking)
  □ Create menu_generator.py (reads from Skills.jsonl)
  □ Implement basic verb-noun commands (learn, teach, stats)
  □ Write unit tests + integration tests
  □ Test against current WAI-State.json workflows

Phase 2: Incremental Migration
  □ Gradually move commands from core.py → new commands/
  □ Parallel operation (both UIs available)
  □ Gather feedback on verb-noun UX

Phase 3: Visual Enhancements
  □ Add Rich formatting
  □ Add progress bars, tables
  □ Animations (if still desired)

Phase 4: Deprecation
  □ Mark old menu system as deprecated
  □ Provide migration guide
  □ Full cutover in next major version
```

---

## ✅ IMPROVEMENTS & SUGGESTIONS

### 1. **Clarify New Commands vs. Old Commands**

**Current code already has these command modules:**
```
commands/
  ├── closeout.py         ← Session ending
  ├── status.py           ← Node/spoke status
  ├── sync.py             ← Structure upgrade
  ├── teach.py            ← Template distribution
  ├── lug.py              ← Lug/task management
  ├── context.py          ← Context export
  └── ... 8 more
```

**Proposal adds these verbs:**
```
learn, teach, stats, review, init
```

**Map current commands to proposal:**
| Current | Proposal | Decision |
|---------|----------|----------|
| `status` | `stats` | Rename? Parallel? |
| `teach` | `teach` | Keep? |
| `sync` (upgrade) | ??? | Where? New verb? |
| `closeout` | ??? | Where? |
| `projects add` | ??? | Where? |
| `groups create` | ??? | Where? |

---

### 2. **Define "Node" More Clearly**

**Current nodes:**
- Hub (central knowledge)
- Spoke (project/workspace)
- Group (collection of spokes)

**Proposal treats all as "Node" in verb-noun:**
```
wai learn hub CoreHub      # Hub is a node
wai learn spoke NodeA      # Spoke is a node
wai learn group TeamA      # Is Group also a node?
```

**Questions:**
- Are all three "nodes" or is it hierarchy: Hub > Spoke > Group?
- Does `wai stats spoke NodeA` work the same as `wai stats hub CoreHub`?
- How do flags vary by node type?

**Recommendation:**
```
✅ Create explicit node hierarchy:
   data/node_types.json:
   {
     "hub": {"verbs": ["learn", "teach", "review", "stats"], ...},
     "spoke": {"verbs": ["learn", "teach", "absorbe", "review"], ...},
     "group": {"verbs": ["stats", "review"], ...}
   }
   
   Then menu_generator filters available commands by node type
```

---

### 3. **Split Animations into Config**

Instead of hardcoding animation choices:

```python
# config.json
{
  "ui": {
    "animations": {
      "welcome": true,           # Show wheel animation on startup
      "progress": true,          # Show spinners during tasks
      "node_visualization": "wheel_ascii",  # Options: wheel_ascii, table, simple
      "color_scheme": "default"  # Options: default, high_contrast, monochrome
    },
    "colors": {
      "hub": "cyan",
      "spoke": "green",
      "active": "yellow",
      "error": "red"
    }
  }
}
```

This allows:
- Users to disable animations in CI/WSL
- Terminal customization without code changes
- Testing without animation delays

---

### 4. **Create Skills Registry Index**

Since proposal's strength is "dynamic menus from skills," ensure this is bulletproof:

```json
{
  "skills_registry": {
    "wai.learn": {
      "name": "Learn",
      "description": "Push signals to hub",
      "cli_trigger": ["learn", "push"],
      "node_types": ["spoke"],
      "flags": ["--from", "--priority", "--force"],
      "aliases": ["sync-up", "push-to-hub"]
    },
    "wai.teach": {
      "name": "Teach",
      "description": "Pull templates from hub",
      "cli_trigger": ["teach", "pull"],
      "node_types": ["spoke"],
      "flags": ["--from", "--force"],
      "aliases": ["sync-down", "pull-from-hub"]
    }
  }
}
```

Then `menu_generator.py` iterates this to build:
- `wai learn` subcommands
- `--help` text
- Shell autocomplete
- Command discovery

---

### 5. **Backward Compatibility Strategy**

**Proposal doesn't address:** What happens to users relying on current menu system?

**Recommendation:**
```
1. Keep old interactive menus as fallback
2. New CLI flags as opt-in (power users)
3. Deprecation notice in help:
   "Note: Interactive menus will be deprecated in v3.2.
    Try: wai learn <node> instead of menu navigation"
4. Migration guide for moving to verb-noun commands
5. Version detection to warn old users
```

---

## 📊 RISK MATRIX

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **Breaking change to CLI** | High | Parallel operation, long deprecation |
| **Missing command mapping** | High | Audit → inventory phase first |
| **Integration with WAI-State** | Medium | Write data layer tests first |
| **Animation/terminal compat** | Medium | Make optional, test in CI/WSL |
| **Scope creep (animations first)** | Medium | Phased approach, MVP focus |
| **Dependency conflicts** | Low | Use vendoring or careful pinning |
| **User confusion (new paradigm)** | Medium | Clear migration docs + examples |

---

## 🎯 REVISED BUILD PLAN (PHASED)

### **Phase 0: Planning & Audit (1-2 days)**
- [ ] Inventory all 40+ current commands
- [ ] Map to new verb-noun structure
- [ ] Create node_types.json schema
- [ ] Create skills_registry.json template
- [ ] Define backward compatibility policy

### **Phase 1: Foundation (3-5 days)**
- [ ] Create `lib/menu_generator.py` (reads skills.jsonl, outputs command trees)
- [ ] Implement core verbs: `init`, `learn`, `teach`, `stats`, `review`
- [ ] Update `commands/__init__.py` to use menu_generator
- [ ] Write unit tests for menu generation
- [ ] Write integration tests for 5 core commands

### **Phase 2: Incremental Migration (5-10 days)**
- [ ] Migrate existing `commands/teach.py` → align with new structure
- [ ] Migrate `commands/status.py` → align with new structure
- [ ] Run both old menus + new CLI flags in parallel
- [ ] User testing: Can power users prefer verb-noun over menus?

### **Phase 3: Visual Enhancement (5-7 days)**
- [ ] Add Rich formatting to output (tables, colors)
- [ ] Add progress bars for long operations
- [ ] Add optional spinner animations (config-driven)
- [ ] Wheel ASCII visualization (optional, Phase 3.5)

### **Phase 4: Polish & Docs (3-5 days)**
- [ ] Migration guide for old → new commands
- [ ] Autocomplete setup
- [ ] Examples and tutorials
- [ ] Release notes with deprecation warnings

---

## 🏁 VERDICT & RECOMMENDATIONS

### **APPROVE WITH CONDITIONS:**

✅ **Approve the vision** - verb-noun, dynamic menus, visual feedback  
❌ **Do NOT start implementation** without clarity on:

1. **Scope clarity:** Is this complete rewrite or refactor?
2. **Command inventory:** Where do all 40+ commands map?
3. **Data model:** Unified Skills definition format
4. **Backward compatibility:** How long do old menus stay?
5. **Phased rollout:** Don't do everything at once

### **Key Decisions Before Implementation:**

1. **Interview stakeholders:** Who uses `wai` CLI?
   - Framework developers (want CLI flags, scripting)
   - Project teams (want guided menus, discovery)
   - CI/CD pipelines (want `--json` output, no animations)

2. **Prototype Phase 1 only** (menu_generator.py) before committing to full refactor

3. **Parallel operation during transition** - don't force old users to relearn immediately

4. **Config-driven visuals** - animations should be nice-to-have, not blocking

### **Next Step:**

Create **DETAILED SPECIFICATION DOCUMENT** that answers:
```
CLI-REDESIGN-SPEC.md
├── 1. Command Inventory (audit results)
├── 2. Node Type Definitions (hub, spoke, group)
├── 3. Verb Definitions (learn, teach, stats, etc.)
├── 4. Data Model (skills.json schema)
├── 5. Backward Compatibility Plan
├── 6. Phased Rollout Timeline
├── 7. Risk Mitigation Strategies
└── 8. User Migration Guide (draft)
```

---

## SUMMARY TABLE

| Aspect | Rating | Comment |
|--------|--------|---------|
| **Vision/Direction** | 9/10 | Bold, coherent, user-friendly |
| **Architecture** | 7/10 | Good separation, but LUG integration needs rework |
| **Feasibility** | 5/10 | Depends on scope & command mapping clarity |
| **Risk** | Medium | Large refactor, needs phasing |
| **Readiness** | 4/10 | Needs detailed spec before implementation |

**OVERALL: Promising direction. Invest in planning before coding.**

---

## Quick Checklist Before Implementation

- [ ] Create detailed command inventory (all 40+ commands)
- [ ] Define node_types.json schema
- [ ] Create unified skills_registry.json template
- [ ] Write backward compatibility policy
- [ ] Create phased timeline (Phase 0-4)
- [ ] Get stakeholder buy-in on verb-noun paradigm
- [ ] Prototype menu_generator.py alone (non-breaking)
- [ ] Plan parallel operation during transition
- [ ] Define animation/visual config system
- [ ] Set up tests BEFORE implementation

---

**Report Generated:** 2026-02-08  
**Confidence Level:** High (based on audit + current codebase understanding)  
**Recommendation:** 🟡 **APPROVED for detailed planning, not yet for implementation**

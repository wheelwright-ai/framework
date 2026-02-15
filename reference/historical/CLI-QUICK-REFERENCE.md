# CLI Redesign: Quick Reference Card
**Print this. Reference during implementation.**

---

## Vision in One Line
> **Verb-noun CLI with iconic wagon wheel animation, driven by Skills, node-centric design.**

---

## The 5 Core Verbs

| Verb | Usage | Animation | Flags | Phase |
|------|-------|-----------|-------|-------|
| **init** | `wai init hub/spoke --name X` | 🎡 Wheel | --name, --path, --desc | 1 |
| **learn** | `wai learn spoke X` | 🎡 Wheel | --priority, --force, --format | 1 |
| **teach** | `wai teach spoke X` | 🎡 Wheel | --force, --format | 1 |
| **stats** | `wai stats spoke X` | - | --format, --all | 2 |
| **review** | `wai review spoke X` | - | --deep, --format | 2 |
| **absorbe** | `wai absorbe spoke X` | - | --dry-run, --force | 2 |

---

## The 3 Node Types

| Node | Purpose | Commands | Phase |
|------|---------|----------|-------|
| **hub** | Central knowledge | init, learn, teach, review, stats | 1 |
| **spoke** | Project/workspace | init, learn, teach, review, stats, absorbe | 1 |
| **group** | Org collection | create, add-spoke, remove-spoke, stats | 2 |

---

## Architecture: 3 Layers

```
┌────────────────────────────────────────┐
│ Layer 1: CLI Entry Point               │
│ wai/cli/main.py                        │
│ ├─ Show welcome banner (with wheel)    │
│ ├─ Generate parser from skills         │
│ └─ Route to command                    │
└────────────────────────────────────────┘
            ↓
┌────────────────────────────────────────┐
│ Layer 2: Commands (Verbs)              │
│ wai/cli/commands/{init,learn,teach...} │
│ ├─ Parse arguments                     │
│ ├─ Load state via state_manager        │
│ ├─ Show wheel animation                │
│ └─ Return result                       │
└────────────────────────────────────────┘
            ↓
┌────────────────────────────────────────┐
│ Layer 3: Data & Visuals                │
│ state_manager.py (WAI-State.json)      │
│ wheel.py (🎡 animation)                │
│ formatter.py (Rich tables)             │
└────────────────────────────────────────┘
```

---

## Directory Structure (What to Create)

```
wai/cli/
├── __init__.py
├── main.py                    ← Entry point
├── commands/
│   ├── __init__.py
│   ├── init.py                ← Create hub/spoke
│   ├── learn.py               ← Push signals
│   ├── teach.py               ← Pull templates
│   ├── stats.py               ← Metrics
│   ├── review.py              ← State inspection
│   ├── absorbe.py             ← Seed processing
│   └── utils.py               ← Shared functions
├── lib/
│   ├── __init__.py
│   ├── menu_generator.py      ← Parse WAI-Skills.jsonl
│   ├── state_manager.py       ← Read/write WAI-State.json
│   └── node_types.py          ← Node definitions
├── visuals/
│   ├── __init__.py
│   ├── wheel.py               ← 🎡 Wagon wheel animation
│   ├── formatter.py           ← Rich tables & colors
│   └── animations.py          ← Animation utilities
└── tests/
    ├── test_commands.py
    ├── test_wheel.py
    └── test_integration.py
```

---

## Data Flow

```
┌─────────────────────────────────┐
│ WAI-Skills.jsonl                │
│ (Command definitions)           │
└────────────────┬────────────────┘
                 │
                 ↓
      ┌──────────────────────┐
      │ menu_generator.py    │
      │ Extracts:            │
      │ - Verb definitions   │
      │ - Node types         │
      │ - Flags              │
      └──────────────┬───────┘
                     │
                     ↓
         ┌───────────────────────┐
         │ cli/main.py           │
         │ Builds argument parser│
         │ Routes to command     │
         └───────────┬───────────┘
                     │
        ┌────────────┴─────────────┐
        │                          │
        ↓                          ↓
   ┌────────────┐          ┌──────────────┐
   │ Command    │          │ state_manager│
   │ (learn.py) │ ------→  │ (WAI-State)  │
   └──────┬─────┘          └──────────────┘
          │
          ↓
     ┌────────────┐
     │ wheel.py   │
     │ (animate)  │
     └────────────┘
```

---

## Phase 1 Deliverables (2 weeks)

### Week 1
- [ ] Directory structure created
- [ ] Dependencies installed (typer, rich, blessed)
- [ ] Wagon wheel animation working
- [ ] Welcome banner displaying
- [ ] menu_generator.py reading Skills.jsonl
- [ ] cli/main.py routing commands

### Week 2
- [ ] `init` command complete (hub + spoke)
- [ ] `learn` command complete (push signals)
- [ ] `teach` command complete (pull templates)
- [ ] state_manager.py complete
- [ ] 40+ unit tests passing
- [ ] Integration tests passing
- [ ] Documentation written

**Result:** Users see wagon wheel, basic CLI works.

---

## Phase Timeline

| Phase | Timeline | Goal |
|-------|----------|------|
| **1** | Week 1-2 | Wagon wheel + init/learn/teach |
| **2** | Week 2-3 | stats, review, absorbe complete |
| **3** | Week 3-4 | Parallel operation (old + new UI) |
| **4** | Week 4-5 | Config, themes, polish |
| **Launch** | Week 5-6 | Release, migration docs |

---

## Command Examples

### Hub Setup
```bash
wai init hub --name CoreHub --path /data/hub
```

### Spoke Creation
```bash
wai init spoke --name ProjectA --hub CoreHub --path /projects/A
```

### Learning (Power User)
```bash
wai learn spoke ProjectA --priority high --force
```

### Learning (Interactive)
```bash
wai
  → Hub
  → Spokes
  → ProjectA
  → Learn Signals
  → [confirmation]
```

### Teaching
```bash
wai teach spoke ProjectA
[shows diff preview]
[asks confirmation]
[animates wheel while pulling]
```

### Statistics
```bash
wai stats spoke ProjectA --format table
```

### Review
```bash
wai review spoke ProjectA --deep
```

---

## Key Files to Integrate With

| Existing File | Use | How |
|---------------|-----|-----|
| `wai/hub.py` | HubManager | Wrap in state_manager |
| `wai/init.py` | Init logic | Import and reuse |
| `wai/utils/input.py` | Prompts | `confirm()`, `safe_input()` |
| `WAI-Spoke/WAI-Skills.jsonl` | Menu source | Read in menu_generator |
| `WAI-Spoke/WAI-State.json` | Node state | Read/write via state_manager |
| `WAI-Spoke/WAI-Signals.jsonl` | Signals | Discover in learn command |

---

## Testing Checklist

- [ ] Wheel renders without errors
- [ ] Detects non-TTY (no animation)
- [ ] Works in WSL terminal
- [ ] init hub creates .hub marker
- [ ] init spoke creates WAI-Spoke/
- [ ] learn discovers signals correctly
- [ ] teach fetches from hub
- [ ] All commands support --json
- [ ] --help shows skill descriptions
- [ ] Error messages are helpful
- [ ] 85%+ code coverage
- [ ] No regressions in wai/ package

---

## Dependencies (Lock These)

```
typer==0.9.0            # CLI framework
rich==13.7.0            # Tables, colors, formatting
blessed==1.20.0         # Terminal animations
click==8.1.7            # CLI utils (fallback)
pydantic==2.5.0         # Config validation
```

---

## Success Metrics

### Phase 1 Complete When:
- ✅ Wagon wheel visible on every major operation
- ✅ All 3 verbs (init, learn, teach) working
- ✅ 85%+ test coverage
- ✅ Works in WSL without errors
- ✅ Animations disable gracefully in CI
- ✅ `--help` shows meaningful text

### No Breaking Changes When:
- ✅ Old `wai` (no args) still shows interactive menu
- ✅ Existing `wai/` commands still work
- ✅ WAI-State.json unchanged
- ✅ Session hooks still trigger

---

## Decision Quick-Ref

### What's LOCKED IN
- ✅ Wagon wheel Phase 1 (calling card)
- ✅ Verb-noun structure
- ✅ 5 core verbs (phase 1: 3, phase 2: 3 more)
- ✅ Hub, Spoke, Group nodes
- ✅ 4-phase rollout
- ✅ Backward compatibility

### What's FLEXIBLE
- ❓ Exact animation speed (configurable)
- ❓ Terminal rendering tweaks (during Phase 1)
- ❓ Color scheme (Phase 4, multiple options)
- ❓ Exact flag names (within reason)

### What's DEPRECATED
- 🔴 `wai sync` → use `wai teach` instead

### What's PRESERVED
- 🟢 `wai` (no args) interactive menu
- 🟢 `wai closeout` (IDE hooks)
- 🟢 `wai shipit` (IDE hooks)
- 🟢 All existing wai/ commands

---

## Questions? Reference These

| Question | Answer Location |
|----------|-----------------|
| How does menu_generator work? | CLI-REDESIGN-SPEC.md, Section 3 |
| What's the wagon wheel design? | CLI-REDESIGN-SPEC.md, Section 6 |
| What are Phase 1 tasks? | CLI-PHASE1-TASKS.md |
| Why this design? | CLI-REDESIGN-REVIEW.md |
| How long will this take? | CLI-PHASE1-TASKS.md, Timeline table |
| How do we test it? | CLI-PHASE1-TASKS.md, Task 6.1 |
| What about groups? | CLI-REDESIGN-SPEC.md, Section 3 |

---

## Mantra During Implementation

> **"The wagon wheel rolls forward."**

- When adding a feature: Does it advance the wheel?
- When debugging: Check the wheel first (visuals are public)
- When uncertain: Ask "Does this move us closer to Phase 2?"
- When done: Show the wheel animating.

---

**Print this card. Keep it on desk. Reference daily.**

**Version:** 1.0  
**Last Updated:** 2026-02-08  
**Status:** Ready for implementation

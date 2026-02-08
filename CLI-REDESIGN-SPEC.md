# CLI Redesign Specification
**Version:** 1.0  
**Date:** 2026-02-08  
**Status:** 🟢 READY FOR IMPLEMENTATION PLANNING

---

## 1. Executive Overview

### Vision
Create a **visually iconic CLI** for Wheelwright where the **rolling wagon wheel** is the signature brand element. The CLI is **verb-noun structured**, **skills-driven**, and provides **power-user scripting** while maintaining **interactive discovery** for guided workflows.

### Core Principle
> "The wagon wheel rolls forward. So does your work."

Every interaction reminds users they're in a unified knowledge system with hub + spokes moving together.

---

## 2. Scope Clarifications

### ✅ IN SCOPE
```
Core Verbs:
  - init      Create hub or spoke
  - learn     Push signals from spoke to hub
  - teach     Pull templates/learnings from hub to spoke
  - stats     View node statistics
  - review    Inspect project/node state

Node Types:
  - hub       Central knowledge repository
  - spoke     Individual project/workspace
  - group     Collection of spokes (organizational)

Animations & Visuals:
  - Wagon wheel rolling (signature animation) ← PHASE 1 PRIORITY
  - Rich table formatting
  - Progress spinners
  - Color coding by node type

Data Sources:
  - WAI-Skills.jsonl (source of truth for command definitions)
  - Lugs (CLI specifications & hidden design details)
  - WAI-State.json (node state, integration)
```

### ❌ OUT OF SCOPE
```
These are IDE-integrated or deprecated:
  - closeout  (IDE hook system)
  - shipit    (IDE hook system)
  - baseline  (deferred - CLI doesn't need to expose)
  - projects  (covered by spoke management + groups)
  - sync      (DEPRECATED → teach replaces it)

These are in flux:
  - groups    (will be added after Phase 1)
```

---

## 3. Node Type Architecture

### Hub
```
Represent: Central knowledge repository
Commands:
  - wai init hub --name CoreHub
  - wai learn hub CoreHub              (no-op, shows help)
  - wai teach hub CoreHub              (distribute to spokes)
  - wai review hub CoreHub
  - wai stats hub CoreHub

Stored In:
  - {hub_root}/.hub                    (marker file)
  - {hub_root}/hub-profile.json        (metadata)
```

### Spoke
```
Represent: Individual project/workspace
Commands:
  - wai init spoke --hub CoreHub --name ProjectA
  - wai learn spoke ProjectA           (push to hub)
  - wai teach spoke ProjectA           (pull from hub)
  - wai review spoke ProjectA
  - wai stats spoke ProjectA
  - wai absorbe spoke ProjectA         (process seed folders)

Stored In:
  - {spoke_root}/WAI-Spoke/            (session data)
  - {spoke_root}/WAI-Spoke/WAI-State.json
```

### Group
```
Represent: Organizational collection of spokes
Commands (Phase 2):
  - wai group create MyTeam
  - wai group add-spoke MyTeam ProjectA
  - wai group stats MyTeam
  - wai group remove-spoke MyTeam ProjectA

Stored In:
  - {hub_root}/groups/MyTeam.json      (group membership + metadata)
```

---

## 4. Verb Definitions

### INIT
```
Purpose: Set up a new node (hub or spoke)

wai init hub
  --name, -n              Hub name (required)
  --path, -p              Location (default: current dir)
  --description, -d       Hub description

wai init spoke
  --name, -n              Spoke name (required)
  --hub, -H               Hub location or ID (required)
  --path, -p              Location (default: current dir)
  --description, -d       Spoke description

Triggers:
  - Wagon wheel animation during setup
  - Confirmation message with visual feedback
```

### LEARN
```
Purpose: Push signals/changes from spoke to hub

wai learn spoke ProjectA
  --priority, -p          Signal priority (high/normal/low)
  --force, -f             Skip confirmation
  --from                  Specific signal file (optional)
  --json                  Output as JSON (scripting)

Behavior:
  1. Detect signals in WAI-Spoke/WAI-Signals.jsonl
  2. Prepare for hub ingestion
  3. Display preview with table
  4. Confirm with user
  5. Animate wheel while pushing
  6. Show success message with stats

Output:
  ✅ Learned: 5 signals
     • 3 high-impact decisions
     • 2 patterns identified
     Destination: CoreHub
```

### TEACH
```
Purpose: Pull templates/learnings from hub to spoke
(REPLACES deprecated 'sync' command)

wai teach spoke ProjectA
  --force, -f             Skip confirmation
  --from                  Specific template (optional)
  --json                  Output as JSON

wai teach hub CoreHub    (distribute to all spokes)
  --force, -f
  --json

Behavior:
  1. Fetch latest from hub
  2. Show what's new (diff summary)
  3. Confirm with user
  4. Animate wheel while pulling
  5. Apply templates/learnings
  6. Show success with sync details

Output:
  ✅ Taught: ProjectA
     Updated templates:
     • session-start.md
     • reference-guide.md
     Hub version: 2026-02-08
```

### STATS
```
Purpose: View metrics and information about nodes

wai stats spoke ProjectA
  --format, -f            table/json/text (default: table)
  --all, -a               Show detailed breakdown

wai stats hub CoreHub
  --spokes                Show all connected spokes
  --format

Output (table mode):
  ┌─────────────────────────────────────┐
  │ ProjectA Statistics                 │
  ├─────────────────────────────────────┤
  │ Status:     Active                  │
  │ Last Sync:  2 days ago              │
  │ Signals:    12 pending              │
  │ Templates:  Up to date              │
  │ Tech Stack: Python, FastAPI         │
  └─────────────────────────────────────┘
```

### REVIEW
```
Purpose: Inspect project/node state and configuration

wai review spoke ProjectA
  --deep                  Detailed analysis
  --format, -f            text/json

wai review hub CoreHub
  --health                Health check
  --spokes                List all spokes

Output:
  📋 ProjectA Review
  ─────────────────
  ✅ WAI-Spoke initialized
  ✅ Git repository found
  ⚠️  4 uncommitted changes
  ✅ 3 signals waiting for hub
  ⚠️  Templates not synced (2 days old)

  Recommendations:
  • Run: wai teach spoke ProjectA
  • Run: wai learn spoke ProjectA
```

### ABSORBE (Spoke-only)
```
Purpose: Process seed folders and archive sprawl

wai absorbe spoke ProjectA
  --dry-run, -d           Preview without changes
  --force, -f             Skip confirmation

Behavior:
  1. Find seed/ directories
  2. Process into WAI-Spoke structure
  3. Archive processed items
  4. Show what changed

(This exists in current code, keep as-is with new styling)
```

---

## 5. Data Architecture

### Skills Registry (WAI-Skills.jsonl source)
Current structure is good. Menu generator reads from this.

**Key fields for new CLI:**
```json
{
  "id": "wai.learn",
  "name": "Learn",
  "cli_trigger": ["learn"],
  "node_types": ["spoke"],           ← Which nodes support this verb
  "flags": {
    "priority": "high/normal/low",
    "force": "boolean",
    "json": "boolean"
  },
  "examples": [
    "wai learn spoke ProjectA",
    "wai learn spoke ProjectA --priority high"
  ]
}
```

### Lug Integration (CLI Hidden Specs)
Lugs hold **CLI specifications** (hidden from other objects).

**Example lug structure for CLI:**
```
WAI-Spoke/WAI-Lugs.jsonl:
{
  "id": "lug-cli-wheel-animation",
  "type": "cli_design",
  "scope": "cli_only",              ← Hidden from other objects
  "content": {
    "feature": "wagon_wheel_animation",
    "triggers": ["init", "learn", "teach"],
    "animation": {
      "type": "wagon_wheel",
      "speed": "medium",
      "direction": "left_to_right",
      "duration_ms": 3000
    }
  }
}
```

This keeps CLI design decisions **separate** from hub/spoke/group concerns.

### Configuration (config.json)
```json
{
  "cli": {
    "ui": {
      "animations_enabled": true,
      "animation_speed": "medium",      // fast, medium, slow
      "node_visualization": "wheel",    // wheel, table, simple
      "color_scheme": "default"         // default, high_contrast, monochrome
    },
    "output": {
      "default_format": "table",        // table, json, text
      "color_enabled": true
    },
    "wagon_wheel": {
      "frames": 12,
      "width": 60
    }
  }
}
```

---

## 6. Visual Design: Wagon Wheel Animation

### Welcome Banner
```
On startup (or wai --version):

        ╔═══════════════════════════════╗
        ║                               ║
        ║    WHEELWRIGHT AI             ║
        ║                               ║
        ║         v3.1.0                ║
        ║                               ║
        ║    Build AI wheels that       ║
        ║    roll forward forever       ║
        ║                               ║
        ║      [animation plays]        ║
        ║    Rolling wagon wheel...     ║
        ║      ◎ ◐ ◑ ◒ ◓ ◔ ◕ ◖        ║
        ║                               ║
        ╚═══════════════════════════════╝
```

### Wagon Wheel Rolling Animation
```
Frames (simplified, actual implementation more fluid):

Frame 1:
    ╔════════════════════════════════════╗
    ║         ◆                          ║
    ║       ◎   ◉                        ║
    ║    ◉     ◎  ◉                      ║
    ║       ◉   ◉                        ║
    ║         ◉                          ║
    ╚════════════════════════════════════╝

Frame 2:
    ╔════════════════════════════════════╗
    ║            ◆                       ║
    ║         ◎   ◉                      ║
    ║      ◉     ◎  ◉                    ║
    ║         ◉   ◉                      ║
    ║            ◉                       ║
    ╚════════════════════════════════════╝

(Continues rolling left to right...)
```

**Usage:**
- `wai init` → wheel rolls during setup
- `wai learn` → wheel animates while pushing
- `wai teach` → wheel animates while pulling
- `wai --help` → brief wheel animation in header

---

## 7. Folder Structure

```
wai/
├── cli/
│   ├── __init__.py
│   ├── main.py                    # Entry point (replaces part of core.py)
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── init.py
│   │   ├── learn.py
│   │   ├── teach.py
│   │   ├── stats.py
│   │   ├── review.py
│   │   ├── absorbe.py
│   │   └── utils.py               # Shared command utilities
│   ├── lib/
│   │   ├── __init__.py
│   │   ├── menu_generator.py      # Builds menus from WAI-Skills.jsonl
│   │   ├── state_manager.py       # Read/write WAI-State.json
│   │   └── node_types.py          # Node definitions
│   ├── visuals/
│   │   ├── __init__.py
│   │   ├── wheel.py               # Wagon wheel animation
│   │   ├── formatter.py           # Rich tables, colors
│   │   └── animations.py          # General animation library
│   └── tests/
│       ├── test_commands.py
│       ├── test_menu_generator.py
│       └── test_animations.py
│
├── core.py                        # Main entry point (refactored)
├── commands/                      # Existing commands (migrate gradually)
│   ├── closeout.py
│   ├── sync.py → DEPRECATED
│   ├── teach.py → MIGRATE TO cli/
│   └── ...
│
└── (rest of framework unchanged)
```

---

## 8. Implementation Phases

### Phase 1: Foundation & Wagon Wheel (Weeks 1-2)
**Goal:** MVP with signature animation

- [ ] Create `cli/lib/menu_generator.py` (reads WAI-Skills.jsonl)
- [ ] Create `cli/visuals/wheel.py` (rolling wagon wheel)
- [ ] Create `cli/main.py` entry point
- [ ] Implement `init` command (hub + spoke)
- [ ] Implement `learn` command (basic, with animation)
- [ ] Implement `teach` command (basic, with animation)
- [ ] Add wagon wheel to welcome banner + all animations
- [ ] Write unit tests for animation + command routing
- [ ] Integration tests against WAI-State.json

**Deliverable:** Users see wagon wheel rolling, basic verb-noun workflow works

### Phase 2: Complete Core Verbs (Weeks 2-3)
**Goal:** All 5 verbs fully functional

- [ ] Complete `stats` command with Rich tables
- [ ] Complete `review` command with detailed analysis
- [ ] Complete `absorbe` command (migrate from existing)
- [ ] Add `--json` output to all commands
- [ ] Add `--format table/json/text` to all commands
- [ ] Add shell autocomplete setup
- [ ] Write comprehensive tests

**Deliverable:** Full verb-noun CLI ready for power users

### Phase 3: Migration & Parallel Operation (Week 3-4)
**Goal:** Both old and new UIs work

- [ ] Preserve old interactive menus in `core.py`
- [ ] Route `wai` (no args) → interactive menus (old behavior)
- [ ] Route `wai verb node` → new CLI (new behavior)
- [ ] Add deprecation warnings to old commands
- [ ] Migration guide: old menu → new verbs
- [ ] Smoke tests for backward compatibility

**Deliverable:** Users can migrate at their own pace

### Phase 4: Polish & Documentation (Week 4)
**Goal:** Production ready

- [ ] Visual themes (high_contrast, monochrome options)
- [ ] Config system for animation preferences
- [ ] Comprehensive examples & tutorials
- [ ] Release notes with migration path
- [ ] Performance optimization (wheel.py rendering)

**Deliverable:** Ready for v3.2 release with calling card visuals

---

## 9. Key Implementation Details

### Menu Generator Algorithm
```python
# cli/lib/menu_generator.py

def generate_cli_from_skills(skills_jsonl_path):
    """
    Read WAI-Skills.jsonl
    Extract cli_trigger and flags
    Build argparse structure dynamically
    Return parser ready for sys.argv
    """
    
    commands = {}
    for skill in load_jsonl(skills_jsonl_path):
        if not skill.get('wai_cli'):
            continue
            
        verb = skill['wai_cli'][0]
        commands[verb] = {
            'name': skill['name'],
            'description': skill['description'],
            'node_types': skill.get('node_types', []),
            'flags': skill.get('flags', {})
        }
    
    return build_argparse(commands)
```

### Wagon Wheel Rendering
```python
# cli/visuals/wheel.py

class WagonWheel:
    def __init__(self, width=60, frames=12, speed='medium'):
        self.width = width
        self.frames = frames
        self.speed = speed
        
    def roll(self, duration_ms=3000):
        """Animate wagon wheel rolling left to right"""
        # Load frames from lug specification
        # Render with Rich console
        # Sleep between frames based on speed
        # Clean up after animation
        
    def pulse(self):
        """Brief pulse animation (for inline use)"""
        # Quick 1-frame animation for status messages
```

### Command Structure Example (learn.py)
```python
# cli/commands/learn.py

def cmd_learn(args):
    """Push signals from spoke to hub"""
    
    node_type = args.node_type  # 'spoke' or 'hub'
    node_id = args.node_id      # 'ProjectA'
    
    # Validate node exists
    state = load_state(node_id)
    
    # Find signals
    signals = discover_signals(state)
    
    # Show preview
    print_table(signals, format=args.format)
    
    # Confirm
    if not args.force:
        if not confirm(f"Push {len(signals)} signals?"):
            return
    
    # Animate
    with WagonWheel().roll(duration_ms=2000):
        push_to_hub(signals)
    
    # Report
    print_success(f"✅ Learned: {len(signals)} signals → {hub_id}")
```

---

## 10. Deprecations & Migration

### Sync → Teach Migration
```
OLD (deprecated):
  wai sync
  WAI sync (interactive)

NEW:
  wai teach spoke ProjectA    # Pull templates from hub

Migration:
  - Add deprecation warning to sync.py
  - Document mapping in README
  - Support both commands for 2 releases
  - Remove sync.py in v3.3
```

### Interactive Menus → Verb-Noun
```
OLD (preserved during transition):
  wai                         # Interactive main menu
  → Hub
  → Spokes
  (nested navigation)

NEW (opt-in):
  wai learn spoke ProjectA
  wai teach spoke ProjectA
  (direct command)

Coexistence:
  - Both work in v3.2
  - Interactive menus marked "deprecated" in help
  - v3.3: Remove interactive menus, verb-noun only
```

---

## 11. Success Criteria

### Phase 1 (Week 2)
- [ ] Wagon wheel animation works on startup
- [ ] `wai init hub CoreHub` succeeds
- [ ] `wai init spoke ProjectA --hub CoreHub` succeeds
- [ ] `wai learn spoke ProjectA` animates wheel
- [ ] `wai teach spoke ProjectA` animates wheel
- [ ] Animation works in WSL terminal
- [ ] Tests pass for command routing

### Phase 2 (Week 4)
- [ ] All 5 verbs fully implemented
- [ ] `--json` output works for scripting
- [ ] `--format` option works (table/json/text)
- [ ] Interactive menus still functional (parallel)
- [ ] Backward compatibility tests pass

### Phase 3 (Week 5)
- [ ] Old and new UIs coexist
- [ ] Users can opt-in to new CLI
- [ ] Migration guide is clear
- [ ] No regressions in current workflows

### Phase 4 (Week 6)
- [ ] Config system working
- [ ] All themes (default, high_contrast, monochrome) working
- [ ] Shell autocomplete ready
- [ ] Documentation complete

---

## 12. Open Questions & Decisions

### Q: Should `wai` (no args) still show interactive menu?
**A:** YES (during transition). Route to old menu system. In v3.3, route to help text.

### Q: Where do groups fit?
**A:** Phase 2. `wai group create TeamA`, `wai group add-spoke`, etc. Follow same pattern.

### Q: What about existing commands like `closeout`, `shipit`?
**A:** Stay in core.py, IDE-integrated only. Not exposed in CLI menu.

### Q: Should wheel animation be configurable?
**A:** YES. Config option: `animations_enabled: true/false`. Default: true.

### Q: How do we handle CI/headless environments?
**A:** Detect non-TTY, disable animations automatically. Or use `--no-animation` flag.

### Q: Does `--json` output include animation metadata?
**A:** NO. `--json` mode disables all animations. Pure data output for scripting.

---

## 13. Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| **Breaking change to CLI** | Parallel operation in Phase 3; long deprecation path |
| **Animation terminal issues** | Test in WSL, detect TTY, config option to disable |
| **Integration with WAI-State.json** | Write state manager layer first (Phase 1) |
| **Menu generator complexity** | Start simple, iterate; keep skills.jsonl as source of truth |
| **Performance (wheel animation)** | Cache frames, optimize rendering, config speed setting |

---

## 14. Reference: Example User Journeys

### Journey 1: First-Time User (Interactive)
```
$ wai
  ╔════════════════════════════════════╗
  ║     WHEELWRIGHT AI                 ║
  ║                                    ║
  ║    [wagon wheel animation]         ║
  ║                                    ║
  ║    1. Create Hub                   ║
  ║    2. Create Spoke                 ║
  ║    3. Learn Workflows              ║
  ║    ?. Help                         ║
  ╚════════════════════════════════════╝

$ (user selects "1. Create Hub")

Hub Setup
─────────
Hub name: [MyHub]
Location: [/current/dir] (or specify)

  [wagon wheel rolling...]

✅ Hub created: MyHub
```

### Journey 2: Power User (Direct Commands)
```
$ wai learn spoke ProjectA --priority high
  [wagon wheel animates while pushing]
✅ Learned: 12 signals
   • 3 high-impact decisions
   • 2 patterns identified
   Destination: CoreHub

$ wai stats spoke ProjectA --format json
{
  "name": "ProjectA",
  "status": "active",
  "signals_pending": 12,
  "last_sync": "2026-02-08T10:30:00Z"
}

$ wai teach spoke ProjectA --from hub
  [wagon wheel rolling...]
✅ Taught: ProjectA
   Updated templates: 3
   Hub version: 2026-02-08
```

### Journey 3: Hub Manager (Groups & Oversight)
```
$ wai group create TeamBackend
✅ Created group: TeamBackend

$ wai group add-spoke TeamBackend ProjectA
✅ Added ProjectA → TeamBackend

$ wai stats hub CoreHub --spokes
┌──────────────┬────────┬──────────┐
│ Spoke        │ Status │ Signals  │
├──────────────┼────────┼──────────┤
│ ProjectA     │ Active │ 12       │
│ ProjectB     │ Active │ 5        │
│ ProjectC     │ Idle   │ 0        │
└──────────────┴────────┴──────────┘
```

---

## 15. Next Steps

1. **Approve this spec** (or request changes)
2. **Create Phase 1 lug** defining wagon wheel animation specs
3. **Bootstrap Phase 1 tasks** (Week 1 start date)
4. **Set up parallel testing** (old menu + new CLI)
5. **Create migration guide template** (for Phase 3)

---

## Summary Table

| Aspect | Decision |
|--------|----------|
| **Core Verbs** | init, learn, teach, stats, review, absorbe |
| **Node Types** | hub, spoke, group (phased) |
| **Signature Element** | Wagon wheel rolling animation (Phase 1) |
| **Data Source** | WAI-Skills.jsonl (menus) + Lugs (CLI specs) |
| **Implementation** | 4 phases, 6 weeks, non-breaking |
| **Coexistence** | Old interactive menus + new CLI in v3.2 |
| **Deprecation** | sync → teach; interactive → verb-noun in v3.3 |
| **Config** | Animation speed, color scheme, format defaults |

---

**Document Status:** ✅ READY FOR IMPLEMENTATION  
**Confidence Level:** High  
**Next Action:** Approve or request specific changes before Phase 1 start

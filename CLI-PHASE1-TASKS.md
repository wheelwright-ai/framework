# CLI Phase 1: Foundation & Wagon Wheel
**Duration:** 2 weeks  
**Goal:** MVP with signature animation + core verb-noun workflow

---

## Overview

Phase 1 delivers the **calling card**—the rolling wagon wheel animation—plus the foundation for all future CLI verbs. Users will see:
- Bold animated banner on startup
- Working `init`, `learn`, `teach` commands
- Wagon wheel animation during operations
- Rich table formatting for output

---

## Task Breakdown

### BLOCK 1: Setup & Infrastructure (Days 1-2)

#### Task 1.1: Create CLI Module Structure
```
wai/
├── cli/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── init.py
│   │   ├── learn.py
│   │   ├── teach.py
│   │   ├── stats.py
│   │   ├── review.py
│   │   ├── absorbe.py
│   │   └── utils.py
│   ├── lib/
│   │   ├── __init__.py
│   │   ├── menu_generator.py
│   │   ├── state_manager.py
│   │   └── node_types.py
│   ├── visuals/
│   │   ├── __init__.py
│   │   ├── wheel.py
│   │   ├── formatter.py
│   │   └── animations.py
│   └── tests/
│       ├── __init__.py
│       ├── test_commands.py
│       ├── test_wheel.py
│       └── test_integration.py
```

**Deliverable:** Empty module structure with docstrings  
**Effort:** 30 min

---

#### Task 1.2: Setup Dependencies
Create `requirements-cli.txt`:
```
typer==0.9.0           # CLI framework
rich==13.7.0           # Tables, colors, formatting
blessed==1.20.0        # Terminal animations
click==8.1.7           # CLI utilities (fallback)
pydantic==2.5.0        # Configuration validation
```

**Deliverable:** Dependencies installed, verified in test import  
**Effort:** 30 min

---

### BLOCK 2: Wagon Wheel Animation (Days 2-4)

#### Task 2.1: Implement WagonWheel Class
**File:** `cli/visuals/wheel.py`

```python
class WagonWheel:
    """ASCII wagon wheel rolling animation."""
    
    def __init__(self, width=60, frames=12, speed='medium'):
        """Initialize wheel with config."""
        
    def roll(self, duration_ms=3000):
        """Animate wagon rolling left to right."""
        
    def pulse(self):
        """Brief pulse effect (inline use)."""
        
    def render_frame(self, frame_num):
        """Return string of current frame."""
```

**Design Notes:**
- 12 frames = smooth rotation
- Width = 60 chars (fits standard terminal)
- Use `blessed` for smooth terminal handling
- Speed: fast (100ms), medium (150ms), slow (250ms) between frames
- Support TTY detection (disable in non-interactive)

**Test Requirements:**
- [ ] Renders without errors
- [ ] Detects non-TTY (no animation)
- [ ] Works in WSL terminal
- [ ] Duration matches config

**Deliverable:** Working wagon wheel, unit tests pass  
**Effort:** 2 days

---

#### Task 2.2: Implement Welcome Banner
**File:** `cli/visuals/animations.py`

```python
def show_welcome_banner(include_wheel=True):
    """Display welcome banner with optional animation."""
    
def show_simple_banner():
    """Text-only banner (for CI/headless)."""
```

**Design:**
```
        ╔═══════════════════════════════╗
        ║                               ║
        ║    WHEELWRIGHT AI             ║
        ║                               ║
        ║         v3.1.0                ║
        ║                               ║
        ║    Build AI wheels that       ║
        ║    roll forward forever       ║
        ║                               ║
        ║      [wagon wheel rolling]    ║
        ║                               ║
        ╚═══════════════════════════════╝
```

**Test Requirements:**
- [ ] Banner displays without errors
- [ ] Animation runs for 3 seconds
- [ ] Non-TTY shows text-only version
- [ ] Colors work in terminal

**Deliverable:** Banner + animation, integration test  
**Effort:** 1 day

---

### BLOCK 3: Command Routing & Menu Generator (Days 3-5)

#### Task 3.1: Implement menu_generator.py
**File:** `cli/lib/menu_generator.py`

```python
def load_skills_from_jsonl(path):
    """Read WAI-Skills.jsonl, extract CLI definitions."""
    
def build_command_structure(skills):
    """Map skills → argparse command structure."""
    
def generate_argparse(skills):
    """Create dynamic ArgumentParser from skills."""
    
    # Returns parser with subcommands:
    # wai init [hub|spoke] [args]
    # wai learn [spoke|hub] [args]
    # wai teach [spoke|hub] [args]
    # etc.
```

**Key Requirements:**
- Read from `WAI-Spoke/WAI-Skills.jsonl`
- Extract `cli_trigger`, `node_types`, `flags` from each skill
- Build argparse dynamically
- Support `--help` from skill descriptions

**Test Requirements:**
- [ ] Parses skills.jsonl correctly
- [ ] Generates valid argument parser
- [ ] `--help` shows skill descriptions
- [ ] Unknown commands handled gracefully

**Deliverable:** Menu generator, unit tests  
**Effort:** 2 days

---

#### Task 3.2: Implement cli/main.py Entry Point
**File:** `cli/main.py`

```python
def main():
    """CLI entry point."""
    
    # Show welcome banner
    show_welcome_banner()
    
    # Generate parser from skills
    parser = generate_argparse(load_skills_from_jsonl(...))
    
    # Route command
    args = parser.parse_args()
    route_command(args)

if __name__ == '__main__':
    main()
```

**Test Requirements:**
- [ ] Entry point callable
- [ ] Routes commands correctly
- [ ] Error handling for invalid commands
- [ ] Works in test harness

**Deliverable:** CLI entry point, routing logic  
**Effort:** 1 day

---

### BLOCK 4: Core Commands (Days 4-8)

#### Task 4.1: Implement INIT Command
**File:** `cli/commands/init.py`

```python
def cmd_init(args):
    """
    wai init hub
    wai init spoke
    """
    
    if args.node_type == 'hub':
        create_hub(
            name=args.name,
            path=args.path or '.',
            description=args.description
        )
    elif args.node_type == 'spoke':
        create_spoke(
            name=args.name,
            hub=args.hub,
            path=args.path or '.',
            description=args.description
        )
```

**Behavior:**
1. Validate inputs
2. Show wagon wheel animation
3. Create hub/.hub or spoke/WAI-Spoke/
4. Show success message

**Flags:**
```
wai init hub
  --name, -n              Hub name (required)
  --path, -p              Location (default: current)
  --description, -d       Description

wai init spoke
  --name, -n              Spoke name (required)
  --hub, -H               Hub location (required)
  --path, -p              Location (default: current)
  --description, -d       Description
```

**Test Requirements:**
- [ ] Hub creation works
- [ ] Spoke creation works
- [ ] WAI-State.json created correctly
- [ ] Wheel animation runs
- [ ] Duplicate hub/spoke rejected

**Deliverable:** Init command, tests  
**Effort:** 2 days

---

#### Task 4.2: Implement LEARN Command
**File:** `cli/commands/learn.py`

```python
def cmd_learn(args):
    """
    wai learn spoke ProjectA
    wai learn spoke ProjectA --priority high --force
    """
    
    # Load signals from WAI-Spoke/WAI-Signals.jsonl
    signals = discover_signals(args.node_id)
    
    # Show preview
    print_table(signals, format=args.format or 'table')
    
    # Confirm
    if not args.force and not confirm(f"Push {len(signals)}?"):
        return
    
    # Animate
    with WagonWheel().roll(duration_ms=2000):
        result = push_to_hub(signals, priority=args.priority)
    
    # Report
    print_success(f"✅ Learned: {result.count} signals → {result.hub}")
```

**Flags:**
```
wai learn spoke NodeID
  --priority, -p          high/normal/low (default: normal)
  --force, -f             Skip confirmation
  --from                  Specific signal file
  --format, -F            table/json/text (default: table)
```

**Test Requirements:**
- [ ] Discovers signals correctly
- [ ] Table formatting works
- [ ] Confirmation prompts work
- [ ] Wagon wheel animates
- [ ] JSON output works
- [ ] Force flag skips confirmation

**Deliverable:** Learn command, tests  
**Effort:** 2 days

---

#### Task 4.3: Implement TEACH Command
**File:** `cli/commands/teach.py`

```python
def cmd_teach(args):
    """
    wai teach spoke ProjectA
    wai teach hub CoreHub (distribute to all spokes)
    """
    
    if args.node_type == 'spoke':
        # Pull templates for single spoke
        templates = fetch_from_hub(args.node_id)
        print_diff_preview(templates)
        if not args.force and not confirm("Apply changes?"):
            return
        with WagonWheel().roll(duration_ms=2000):
            result = apply_templates(args.node_id, templates)
    elif args.node_type == 'hub':
        # Distribute to all spokes
        with WagonWheel().roll(duration_ms=5000):
            result = distribute_to_all_spokes()
    
    print_success(f"✅ Taught: {result.count} templates applied")
```

**Flags:** Same as learn (priority, force, format, from)

**Test Requirements:**
- [ ] Fetches templates from hub
- [ ] Diff preview correct
- [ ] Applies templates
- [ ] Wagon wheel animates
- [ ] Hub distribution works
- [ ] JSON output works

**Deliverable:** Teach command, tests  
**Effort:** 2 days

---

### BLOCK 5: State & Integration (Days 6-8)

#### Task 5.1: Implement state_manager.py
**File:** `cli/lib/state_manager.py`

```python
class StateManager:
    """Read/write WAI-State.json for nodes."""
    
    def load_state(self, node_id):
        """Load WAI-State.json for node."""
        
    def save_state(self, node_id, state):
        """Write WAI-State.json."""
        
    def discover_signals(self, node_id):
        """Read WAI-Signals.jsonl."""
        
    def discover_nodes(self, hub_id):
        """List all spokes in hub."""
```

**Test Requirements:**
- [ ] Reads/writes WAI-State.json
- [ ] Discovers signals from .jsonl
- [ ] Handles missing files gracefully
- [ ] Creates backup before write

**Deliverable:** State manager, tests  
**Effort:** 1 day

---

#### Task 5.2: Integration Tests
**File:** `cli/tests/test_integration.py`

```python
def test_init_hub_to_learn_cycle():
    """Test: init hub → init spoke → learn."""
    
    with temp_workspace() as ws:
        # Create hub
        result = run_cli('init', 'hub', '--name', 'TestHub', '--path', ws)
        assert result.returncode == 0
        assert (ws / '.hub').exists()
        
        # Create spoke
        result = run_cli('init', 'spoke', '--name', 'TestSpoke', 
                        '--hub', ws, '--path', ws)
        assert result.returncode == 0
        
        # Learn
        result = run_cli('learn', 'spoke', 'TestSpoke', '--force')
        assert result.returncode == 0
        assert '✅ Learned' in result.stdout
```

**Test Scenarios:**
- [ ] Complete init → learn → teach cycle
- [ ] State persistence across commands
- [ ] Error handling for missing nodes
- [ ] Animation in real terminal

**Deliverable:** Integration test suite  
**Effort:** 1.5 days

---

### BLOCK 6: Testing & Documentation (Days 8-10)

#### Task 6.1: Unit Test Suite
- Wheel rendering: 5+ test cases
- Menu generator: 10+ test cases
- Command routing: 8+ test cases
- State manager: 10+ test cases

**Coverage Target:** 85%+ of Phase 1 code

**Deliverable:** pytest suite with 40+ tests  
**Effort:** 2 days

---

#### Task 6.2: Documentation
**File:** `cli/README.md`

```markdown
# Wheelwright CLI (Phase 1)

## Quick Start

```bash
wai init hub --name MyHub
wai init spoke --name MyProject --hub MyHub
wai learn spoke MyProject
```

## Commands

- `wai init` - Create hub or spoke
- `wai learn` - Push signals to hub
- `wai teach` - Pull templates from hub
- (stats, review in Phase 2)

## Configuration

See `config.json` for animation preferences.

## Troubleshooting

### Animation not showing
- Set `TERM=xterm-256color`
- Or disable: `config.json → animations_enabled: false`
```

**Deliverable:** CLI docs, usage examples  
**Effort:** 1 day

---

## Dependencies: WAI Modules to Integrate With

### From existing `wai/`:
- `wai/hub.py` - HubManager (keep, wrap in state_manager)
- `wai/utils/input.py` - Prompts (reuse confirm, safe_input)
- `wai/init.py` - Initialization logic (reuse)

### From WAI-Spoke/:
- `WAI-Spoke/WAI-Skills.jsonl` - Menu source
- `WAI-Spoke/WAI-State.json` - State persistence
- `WAI-Spoke/WAI-Signals.jsonl` - Signal discovery

---

## Timeline

| Phase | Dates | Deliverable |
|-------|-------|-------------|
| **Block 1** | Day 1-2 | Module structure + dependencies |
| **Block 2** | Day 2-4 | Wagon wheel animation |
| **Block 3** | Day 3-5 | Menu generator + entry point |
| **Block 4** | Day 4-8 | Init, learn, teach commands |
| **Block 5** | Day 6-8 | State management + integration |
| **Block 6** | Day 8-10 | Tests + documentation |
| **Buffer** | Day 10-14 | Bug fixes, polish, feedback loop |

**Total:** 2 weeks

---

## Success Criteria

- [ ] Wagon wheel animation displays on startup
- [ ] `wai init hub TestHub` creates hub successfully
- [ ] `wai init spoke TestSpoke --hub TestHub` creates spoke
- [ ] `wai learn spoke TestSpoke` animates wheel and pushes signals
- [ ] `wai teach spoke TestSpoke` animates wheel and pulls templates
- [ ] All commands support `--json` output for scripting
- [ ] 85%+ test coverage for Phase 1 code
- [ ] Works in WSL terminal without errors
- [ ] Animation disables gracefully in non-TTY environments
- [ ] `--help` shows meaningful descriptions from skills
- [ ] No regressions in existing `wai/` functionality

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| **Terminal compat** | Test on Windows + WSL, detect TTY early |
| **Animation performance** | Cache frames, benchmark rendering |
| **Integration with old code** | Keep existing `wai/` unchanged in Phase 1 |
| **Scope creep** | Lock Phase 1 to init/learn/teach only |

---

## Notes

- **No breaking changes in Phase 1** - old `wai` still works
- **Animation is non-blocking** - if render fails, CLI continues
- **Config system deferred to Phase 4** - use defaults for now
- **Stats & review deferred to Phase 2** - focus on core 3 verbs

---

**Ready to start?** Approve this breakdown or request changes.

Next: Create Phase 1 lug with animation specifications.

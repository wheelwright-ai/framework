# CLI Usability Audit & Improvement Plan

## Current State Problems

### 1. **Inconsistent Prompts & Inputs**
- `safe_menu_choice()` - unclear when to use
- `prompt_for_input()` - basic, no validation, no clear defaults shown
- Some commands accept args, some don't
- No consistent "yes/no" confirmation pattern

### 2. **Missing User Feedback**
- No confirmation of what action will happen
- No preview of what will be changed
- Success/failure messages inconsistent
- No "what just happened" summary

### 3. **No Clear Cancel/Skip Options**
- "Back" vs "Cancel" vs "Quit" inconsistent
- No universal [0] = cancel pattern
- No way to skip optional steps
- No "enter to accept default" message

### 4. **Command Options Unclear**
- `teach` - what spokes? which ones need teaching? why?
- `learn` - what priority means, what happens with each
- `init` - what is hub vs spoke?
- No help text on commands that need args

### 5. **Status Output Issues**
- Too much info at once
- No section headers/clear grouping
- Mixed success/warning indicators
- Hard to spot what needs action

### 6. **Non-Interactive Mode Usability**
- `wai teach` without spoke - confusing error
- `wai learn --priority high` - unclear what this does
- No examples shown
- No usage help integrated

## Usability Principles to Implement

```
1. CLARITY - Every action shows: "You are about to..."
2. CONSISTENCY - All prompts follow same pattern
3. SAFETY - Never destructive without confirmation
4. DEFAULTS - Always show default option & how to use it
5. FEEDBACK - Always confirm what happened
6. SKIPPABLE - Always offer cancel/skip at every step
7. EXAMPLES - Show examples of what commands do
8. HELP - Every command has --help that explains all options
```

## Implementation Roadmap

### PHASE 1: Standardize Input Patterns (Foundation)
- Create `PromptStyle` class with 4 patterns:
  - `menu()` - numbered options with default
  - `confirm()` - yes/no with default shown
  - `text()` - text input with validation & default
  - `choice()` - select from list with descriptions
- All use same visual style (colors, formatting)
- All show "[1] = select, [0] = cancel"
- All show default in brackets

### PHASE 2: Fix Teach Command UX
**Problem:** `wai teach` confusing
**Solution:**
```
$ wai teach
? Which spoke to teach? (required)
  1 - MyProject (3 days since update)
  2 - Hub (never updated)
  [0] - Cancel

? Confirm teach MyProject - distribute 5 template updates?
  [Y/n] - yes, continue / no, cancel

✓ Teaching MyProject...
  • Updating session.md (no changes)
  • Updating patterns.md (5 new patterns added)
  • Updating reference.md (2 sections updated)
✓ Complete - 2 files changed, 0 conflicts
```

### PHASE 3: Fix Learn Command UX
**Problem:** Priority unclear, no preview
**Solution:**
```
$ wai learn
? Which spoke to learn from? (required)
  1 - MyProject (5 new signals available)
  2 - Hub (2 new signals)
  [0] - Cancel

? Select signal priority level:
  1 - High (critical decisions, 1 signals)
  2 - Normal (patterns & learnings, 4 signals)
  3 - Low (experiments & notes, 2 signals)
  [2] - default (Normal)

? Preview: Import 4 signals into MyProject?
  • Pattern: Async/await pattern
  • Decision: Use UUID for IDs
  • Learning: Git workflow best practice
  • Note: ESLint config strategy

  [Y/n] - yes, continue / no, cancel

✓ Learning from MyProject...
  [1/4] Integrating Pattern: Async/await...
  [2/4] Integrating Decision: Use UUID...
  [3/4] Integrating Learning: Git workflow...
  [4/4] Integrating Note: ESLint config...
✓ Complete - 4 signals integrated, 0 conflicts
```

### PHASE 4: Fix Init Command UX
**Problem:** Hub vs Spoke unclear
**Solution:**
```
$ wai init
? What do you want to initialize?
  1 - Hub (central knowledge base - only one per wheel)
  2 - Spoke (project in wheel - one per project)
  [0] - Cancel

$ wai init hub
? Hub path [./wheelwright-hub]:
  (this is the central hub for your wheel)

? Confirm initialize hub at ./wheelwright-hub?
  [Y/n] - yes / no

✓ Hub created at ./wheelwright-hub
  • Configuration: wheelwright-hub/wheelwright.yml
  • Registry: wheelwright-hub/.registry
  • Learn from any spoke: wai learn <spoke>

$ wai init spoke
? Spoke name (e.g., my-project) [my-spoke]:

? Hub path (leave empty to auto-detect) [auto-detect]:
  (found existing hub at ../wheelwright-hub)

? Confirm initialize spoke at .?
  Name: my-spoke
  Hub: ../wheelwright-hub
  
  [Y/n] - yes / no

✓ Spoke created
  • Configuration: ./WAI-Spoke/wheelwright.yml
  • Observation log: ./WAI-Spoke/observations.jsonl
  • Teach from hub: wai teach --from-hub
```

### PHASE 5: Fix Status Output
**Problem:** Too much info, hard to scan
**Solution:**
```
$ wai status

WHEELWRIGHT STATUS
═════════════════════════════════════════════════

📍 CURRENT SPOKE: my-project
   • Hub: connected to ../wheelwright-hub
   • Status: Ready
   • Last modified: 2 hours ago by mario

📊 STATS
   • Observations: 47 logged
   • Signals: 3 new (2 high, 1 normal)
   • Last sync: today at 14:32

⚙️  ENVIRONMENT
   • OS: Windows + WSL2
   • Python: 3.10 (CPython)
   • Editors: VS Code

⚠️  NEEDS ATTENTION
   • 2 failed observations (see: wai history --failed)
   • Hub update available (run: wai teach --from-hub)

💡 QUICK ACTIONS
   [t] teach     [l] learn     [h] help     [q] quit
```

### PHASE 6: Add Help System
**Problem:** No integrated help
**Solution:**
```
$ wai --help
$ wai teach --help
$ wai learn --help
$ wai status --help

All show:
  • What it does
  • When to use it
  • Examples
  • Common options
  • See also: ...
```

### PHASE 7: Add Confirmation System
**Problem:** No "are you sure" for destructive ops
**Solution:**
```python
# Always confirm:
- teach (updates files)
- learn (imports signals)
- init (creates structure)
- closeout (git operations)

Except: skip with --force flag
Show: what will change before ask
```

## Code Structure

```
wai/
  cli/
    lib/
      ▲ prompts.py (NEW - standard prompt styles)
      ▲ confirmations.py (NEW - confirmation patterns)
      ▲ help.py (NEW - help system)
      menu_generator.py (refactored)
      state_manager.py
      discovery.py
    commands/
      teach.py (refactored)
      learn.py (refactored)
      init.py (refactored)
      status.py (refactored)
    main.py (small changes)
```

## Files to Create/Modify

### NEW FILES
1. `wai/cli/lib/prompts.py` - 4 prompt types with consistent style
2. `wai/cli/lib/confirmations.py` - confirmation patterns
3. `wai/cli/lib/help_system.py` - help text registry
4. `wai/cli/commands/teach_interactive.py` - interactive teach command
5. `wai/cli/commands/learn_interactive.py` - interactive learn command
6. `wai/cli/commands/init_interactive.py` - interactive init command

### MODIFY
1. `wai/cli/main.py` - hook new help system, call interactive commands
2. `wai/cli/lib/menu_generator.py` - use new prompt styles
3. `wai/commands/status.py` - refactor to use new output style
4. `wai/commands/teach.py` - use interactive version
5. `wai/commands/learn.py` - use interactive version

## Testing Strategy

**For each command:**
1. ✓ Happy path (all defaults, confirm yes)
2. ✓ Cancel at each step
3. ✓ Custom input (not default)
4. ✓ Invalid input (handled gracefully)
5. ✓ --force flag (skip confirmations)
6. ✓ --help flag (shows help)
7. ✓ No arguments (shows menu)

**For each prompt:**
1. ✓ Default highlighted
2. ✓ Cancel option [0] works
3. ✓ Keyboard shortcuts work (1/2/c for cancel)
4. ✓ Invalid input re-prompts
5. ✓ Help text shown for complex options

## Success Criteria

- [ ] All commands show clear before/after
- [ ] All prompts consistent (style, cancel, defaults)
- [ ] Every command has --help
- [ ] No command confusing about what it does
- [ ] Every destructive action needs confirmation
- [ ] Tests pass: all 7 scenarios × all commands
- [ ] User can complete teach/learn/init without help

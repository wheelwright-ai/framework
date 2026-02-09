# CLI Usability Testing Guide

## Overview
This guide walks through testing the improved CLI usability. Tests cover:
1. Prompt consistency and clarity
2. Help system
3. Interactive workflows
4. Error handling & edge cases

## Prerequisites
```bash
cd /path/to/wheelwright-ai/framework
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
```

## Test Suite

### PHASE 1: Help System (Foundation)

**Test 1.1 - Main Help**
```bash
$ wai help
# Expected:
# - Shows all commands
# - Shows "For command help: wai <command> --help"
# - No errors
```

**Test 1.2 - Command-Specific Help**
```bash
$ wai teach --help
# Expected:
# - Shows what teach does
# - Shows examples
# - Shows all options (--force, --json)

$ wai learn --help
# Expected:
# - Shows what learn does
# - Explains priority levels (high/normal/low)
# - Shows examples

$ wai init --help
# Expected:
# - Explains hub vs spoke
# - Shows examples for both

$ wai status --help
# Expected:
# - Shows what status displays
```

**Test 1.3 - Help for Topics**
```bash
$ wai help teach
# Same as `wai teach --help`

$ wai help learn
# Same as `wai learn --help`
```

---

### PHASE 2: Teach Command Usability

**Test 2.1 - Interactive Teaching (Happy Path)**
```bash
$ wai teach
# Expected flow:
# 1. "Which spoke to teach?" → Shows list with descriptions
#    - Default is [1] (first spoke)
#    - Cancel option [0]
# 2. Confirm "Teach my-project?" → [Y/n] with Y as default
# 3. Show preview of files changing
# 4. Progress bar during teaching
# 5. Summary "✓ Taught 1 spoke, X changes"

# Verify:
# - Can select [1] or [m] or [Enter]
# - Can cancel with [0] or [c] or Ctrl+C
# - Preview shows what will change
# - Can see progress
```

**Test 2.2 - Teach with Spoke Name (Non-Interactive)**
```bash
$ wai teach my-project
# Expected:
# - Should auto-select my-project
# - Still shows preview
# - Still asks for confirmation (unless --force)
# - Then teaches
```

**Test 2.3 - Teach with --force Flag**
```bash
$ wai teach my-project --force
# Expected:
# - Skips all confirmations
# - Still shows what's happening
# - Shows results
# - No "continue? [Y/n]" prompts
```

**Test 2.4 - Cancel at Different Steps**
```bash
$ wai teach
# At menu:
#   [0] → Should exit with "Cancelled"
# 
$ wai teach
# At confirm:
#   [n] → Should cancel, exit cleanly
```

**Test 2.5 - Invalid Input Handling**
```bash
$ wai teach
# At menu, enter [99]:
#   → Should show "Invalid choice '99'. Try again."
#   → Should re-prompt
#
# Enter [abc]:
#   → Same as above
#
# Just press Enter:
#   → Should use default [1]
```

**Test 2.6 - JSON Output**
```bash
$ wai teach my-project --force --json
# Expected:
# {
#   "success": true,
#   "spoke_count": 1,
#   "changes": 5,
#   "failed": []
# }
```

---

### PHASE 3: Learn Command Usability

**Test 3.1 - Interactive Learning (Happy Path)**
```bash
$ wai learn
# Expected flow:
# 1. "Which spoke to learn from?" → List with signal counts
#    - Default [1]
#    - Cancel [0]
# 2. (If no --force) "Signal priority level?"
#    - [1] High (critical, N signals)
#    - [2] Normal (patterns, N signals)
#    - [3] Low (experiments, N signals)
#    - Default [2]
# 3. Preview: "Signals from my-project (normal priority)"
#    - Lists each signal
# 4. Confirm "Import 4 signals?"
#    - [Y/n] with Y default
# 5. Progress: "[1/4] Integrating Pattern: ..."
# 6. Summary: "✓ Learned from 1 spoke, 4 signals integrated"
```

**Test 3.2 - Learn with Priority Flag**
```bash
$ wai learn my-project --priority high
# Expected:
# - Skips priority selection
# - Goes straight to preview
# - Shows "high priority" in preview
# - Filters to only high signals
```

**Test 3.3 - Learn with --force**
```bash
$ wai learn my-project --priority normal --force
# Expected:
# - Skips preview confirmation
# - Still shows preview (informational)
# - Still shows progress
# - No confirmations
```

**Test 3.4 - Cancel Workflows**
```bash
$ wai learn
# At spoke selection [0]:
#   → Exit with "Cancelled"
#
$ wai learn my-project
# At priority selection [0]:
#   → Cancel, don't learn
#
$ wai learn my-project --priority normal
# At confirmation [n]:
#   → Don't import, exit cleanly
```

**Test 3.5 - Invalid Inputs**
```bash
$ wai learn
# At spoke selection, enter [99]:
#   → "Invalid choice. Try again."
#
# At priority, enter [5]:
#   → "Invalid choice. Try again."
#
# Enter empty / just [Enter]:
#   → Use default
```

**Test 3.6 - JSON Output**
```bash
$ wai learn my-project --priority high --force --json
# {
#   "success": true,
#   "spoke_count": 1,
#   "signals": 2,
#   "priority": "high",
#   "failed": []
# }
```

---

### PHASE 4: Init Command Usability

**Test 4.1 - Interactive Init (Hub)**
```bash
$ wai init
# Expected:
# 1. "What do you want to initialize?"
#    - [1/h] Hub
#    - [2/s] Spoke
#    - [0/c] Cancel
#    - Default [1]
# 2. "Hub path [./wheelwright-hub]:"
#    - Shows default
#    - Can override
# 3. Confirm "Initialize hub at ./wheelwright-hub?"
#    - Shows what will happen
#    - [Y/n] default Y
# 4. Result: "✓ Hub created..."
```

**Test 4.2 - Interactive Init (Spoke)**
```bash
$ wai init
# Choose [2] Spoke
# 1. "Spoke name [my-spoke]:"
# 2. "Hub path [./wheelwright-hub]:" (auto-detected)
# 3. Confirm
# 4. Result
```

**Test 4.3 - Init Hub (Non-Interactive)**
```bash
$ wai init hub
# Should prompt for path with default
# Should confirm
# Should create
```

**Test 4.4 - Init Spoke (Non-Interactive)**
```bash
$ wai init spoke
# Should prompt for name
# Should auto-detect hub
# Should confirm
# Should create
```

**Test 4.5 - Cancel at Each Step**
```bash
$ wai init
# At type selection [0]:
#   → Exit
#
$ wai init hub
# At path prompt, [Ctrl+C]:
#   → "Cancelled"
```

---

### PHASE 5: Status Command

**Test 5.1 - Status Display Format**
```bash
$ wai status
# Expected:
# WHEELWRIGHT STATUS
# ═════════════════════════
# 
# 📍 CURRENT SPOKE: my-project
#    • Hub: connected
#    • Status: Ready
#    • Last modified: 2 hours ago
# 
# 📊 STATS
#    • Observations: 47
#    • Signals: 3 new
#    • Last sync: today
# 
# ⚙️  ENVIRONMENT
#    • OS: Windows + WSL2
#    • Python: 3.10
#    • Editors: VS Code
# 
# ⚠️  NEEDS ATTENTION
#    • 2 failed observations
# 
# 💡 QUICK ACTIONS
#    [t] teach   [l] learn   [h] help   [q] quit
```

**Test 5.2 - Status with No Spoke**
```bash
$ cd /tmp/empty-dir
$ wai status
# Expected:
# ⚠️  No spoke found at: /tmp/empty-dir
# Run: wai init spoke
```

---

### PHASE 6: Error Handling

**Test 6.1 - Missing Hub Connection**
```bash
$ wai init spoke
# Without existing hub:
#   → Should warn "No hub found"
#   → Should prompt for hub path
#   → Should validate path exists
```

**Test 6.2 - Corrupted State File**
```bash
# Manually corrupt WAI-Spoke/WAI-State.json
$ wai status
# Expected:
# ⚠️  Error loading state: JSON decode error
# Run: wai init spoke --force
```

**Test 6.3 - Permission Errors**
```bash
# Make WAI-Spoke read-only
$ wai teach my-project
# Expected:
# ✗ Failed to teach: Permission denied
# Run with elevated permissions
```

---

### PHASE 7: Accessibility & UX

**Test 7.1 - Color Contrast**
- Run on dark terminal background
- All text is readable
- Success (green), error (red), warning (yellow) are distinct

**Test 7.2 - Keyboard Navigation**
- All prompts work with keyboard only
- Tab, arrow keys, number keys work
- Ctrl+C always cancels

**Test 7.3 - Help is Always Accessible**
```bash
$ wai teach -h        # Works
$ wai teach --help    # Works
$ wai help teach      # Works
```

---

## Test Scenarios Checklist

### ✓ Happy Path
- [ ] teach (all defaults)
- [ ] teach <spoke> (with name)
- [ ] learn (all defaults)
- [ ] learn <spoke> --priority high
- [ ] init hub (defaults)
- [ ] init spoke (defaults)
- [ ] status (shows all sections)

### ✓ Cancel Paths
- [ ] teach: cancel at spoke selection
- [ ] teach: cancel at confirmation
- [ ] learn: cancel at spoke selection
- [ ] learn: cancel at priority selection
- [ ] init: cancel at type selection
- [ ] All: Ctrl+C exits gracefully

### ✓ Invalid Input Paths
- [ ] teach: invalid spoke number
- [ ] learn: invalid priority choice
- [ ] init: invalid type choice
- [ ] All: re-prompt on invalid input

### ✓ Non-Interactive Paths
- [ ] wai teach <spoke>
- [ ] wai learn <spoke>
- [ ] wai init hub
- [ ] wai init spoke

### ✓ Force/Skip Paths
- [ ] teach --force (no confirmations)
- [ ] learn --force (no confirmations)
- [ ] Both still show progress

### ✓ Flag Paths
- [ ] --help on all commands
- [ ] --json on teach/learn
- [ ] --priority on learn
- [ ] --force on teach/learn/init

### ✓ Error Paths
- [ ] No hub found
- [ ] No spoke found
- [ ] Invalid paths
- [ ] Permission errors
- [ ] Corrupted state
- [ ] All show helpful messages

---

## Success Criteria

- [ ] All happy paths work without confusion
- [ ] User always knows what will happen before confirming
- [ ] Cancel option always available
- [ ] Invalid input never crashes, always re-prompts
- [ ] Help is always accessible
- [ ] All output is readable on dark background
- [ ] No user has to guess what a command does
- [ ] Clear before/after feedback on all operations
- [ ] Keyboard shortcuts work (1/2/3, c for cancel, etc)
- [ ] Defaults are reasonable and obvious

---

## Known Issues to Fix

If you find issues, file them as:
```
[ISSUE] Test: <test number>
Description: <what went wrong>
Expected: <what should happen>
Actual: <what happened>
Terminal: <Windows/Mac/Linux/WSL>
```

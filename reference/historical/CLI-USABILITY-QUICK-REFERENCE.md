# CLI Usability Quick Reference

## For Users

### Get Help
```bash
wai help              # Show all commands
wai help teach        # Help for teach command
wai teach --help      # Same as above
```

### Teach (Distribute Templates)
```bash
# Interactive - select spoke
$ wai teach

# Named - specific spoke
$ wai teach my-project

# Skip confirmations
$ wai teach my-project --force

# For scripts
$ wai teach my-project --json
```

### Learn (Collect Insights)
```bash
# Interactive - select spoke and priority
$ wai learn

# Specific spoke
$ wai learn my-project

# Filter by priority
$ wai learn my-project --priority high

# Skip confirmations
$ wai learn my-project --force

# For scripts
$ wai learn my-project --json
```

### Initialize
```bash
# Interactive - choose hub or spoke
$ wai init

# Initialize hub
$ wai init hub

# Initialize spoke
$ wai init spoke
```

### Check Status
```bash
$ wai status
```

---

## For Developers

### Using PromptStyle in Your Code

**Menu with Cancel Option**
```python
from wai.cli.lib.prompts import PromptStyle

options = [
    ("1", "t", "Teach"),
    ("2", "l", "Learn"),
    ("3", "s", "Status"),
]
choice = PromptStyle.menu(
    "What would you like to do?",
    options,
    default="1"
)
# Returns: "1", "2", "3", or None (if cancelled)
```

**Yes/No Confirmation**
```python
result = PromptStyle.confirm(
    "Are you sure you want to teach?",
    default=True
)
# Returns: True, False, or None (if cancelled)
```

**Text Input with Validation**
```python
def validate_name(val):
    if len(val) < 3:
        return False, "Name must be 3+ characters"
    return True, ""

name = PromptStyle.text(
    "Project name",
    default="my-project",
    validator=validate_name
)
# Returns: user input (validated) or None if cancelled
```

**Select from List**
```python
items = [
    ("high", "h", "High (critical decisions)"),
    ("normal", "n", "Normal (patterns)"),
    ("low", "l", "Low (experiments)"),
]
descriptions = [
    "1 signal available",
    "4 signals available",
    "2 signals available",
]
priority = PromptStyle.select(
    "Priority level",
    items,
    descriptions=descriptions,
    default="2"  # Normal
)
# Returns: "high", "normal", "low", or None if cancelled
```

**Show Preview**
```python
PromptStyle.show_preview(
    "Files to update",
    ["patterns.md", "reference.md"],
    warn=False
)
# Output:
# Preview: Files to update
#   • patterns.md
#   • reference.md
```

**Show Results**
```python
PromptStyle.show_results(
    "Taught MyProject",
    success=True,
    items=[
        "✓ patterns.md (5 new patterns)",
        "✓ reference.md (2 sections updated)",
    ]
)
# Output:
# ✓ Taught MyProject
#   ✓ patterns.md (5 new patterns)
#   ✓ reference.md (2 sections updated)
```

### Adding Help to Your Command

**1. Add Help Text**
```python
from wai.cli.lib.help_system import HelpRegistry

# In help_system.py, add to HELP_TEXT dict:
"my_command": {
    "title": "My Command",
    "description": "What it does",
    "when_to_use": "When to use it",
    "what_happens": "Step 1...\nStep 2...",
    "examples": "$ wai my_command\n$ wai my_command --flag",
    "options": "--flag   Description\n--other  Description",
    "see_also": "other_command",
}
```

**2. Show Help in Your Code**
```python
from wai.cli.lib.help_system import HelpRegistry

if show_help:
    HelpRegistry.show_help("my_command")
```

### Creating an Interactive Command

**Pattern to Follow:**
```python
from wai.cli.lib.prompts import PromptStyle

class MyCommand:
    def run_interactive(self, arg=None, force=False):
        # Step 1: Get input
        if not arg:
            arg = PromptStyle.select(...)
            if not arg:
                return 0  # User cancelled
        
        # Step 2: Show preview
        preview = self._get_preview(arg)
        PromptStyle.show_preview("What will happen", preview)
        
        # Step 3: Confirm (unless --force)
        if not force:
            if not PromptStyle.confirm("Continue?", default=True):
                return 0
        
        # Step 4: Do the thing
        success = self._do_thing(arg)
        
        # Step 5: Show results
        PromptStyle.show_results("Done", success=success, items=[...])
        return 0 if success else 1
```

### Formatter/Visual Methods

```python
from wai.cli.visuals import get_formatter

fmt = get_formatter()

# Info messages
fmt.print_info("Normal text")

# Success
fmt.print_success("✓ Success message")

# Warning
fmt.print_warning("⚠ Warning message")

# Error
fmt.print_error("✗ Error message")

# Header
fmt.print_header("Section Title", width=50)

# Prompt
fmt.print_prompt("? What's your name?")

# Progress
fmt.print_progress("Working...")

# Comment (for code/examples)
fmt.print_comment("# This is a comment")
```

---

## Prompt Style Reference

### Rules (Always Follow These)

1. **Every prompt asks clearly what will happen**
   - ✅ "Which spoke to teach?"
   - ❌ "Select spoke"

2. **Always show default**
   - ✅ `Choose [1]:`
   - ✅ `[Y/n]`
   - ✅ `Project name [my-spoke]:`

3. **Always offer cancel**
   - ✅ `[0] - Cancel`
   - ✅ `Ctrl+C works`
   - ✅ Shows "Cancelled" on exit

4. **Always show keyboard shortcuts**
   - ✅ `1/t - Teach` (number or letter)
   - ✅ `2/l - Learn`
   - ✅ `0/c - Cancel` (0 or c both work)

5. **Never crash on bad input**
   - ✅ Show "Invalid choice. Try again."
   - ✅ Re-prompt

6. **Always confirm before destructive ops**
   - ✅ teach (updates files)
   - ✅ learn (imports signals)
   - ✅ init (creates structure)
   - ✅ closeout (git ops)

7. **Always show what happened**
   - ✅ `✓ Success`
   - ✅ `⚠ Partial: X failed`
   - ✅ `✗ Failed: reason`

---

## Common Patterns

### Pattern 1: Select → Preview → Confirm → Execute

```python
# User selects
spoke = PromptStyle.select("Which spoke?", items)
if not spoke: return  # Cancelled

# Show what will change
preview = get_preview(spoke)
PromptStyle.show_preview("Changes", preview)

# Ask to proceed
if not PromptStyle.confirm("Proceed?"):
    return  # User said no

# Do it
result = execute(spoke)

# Show result
PromptStyle.show_results("Done", success=result.ok, items=result.messages)
```

### Pattern 2: Menu Loop with Submenus

```python
while True:
    cmd = PromptStyle.menu("Main menu", options, default="1")
    if cmd is None or cmd == "0":
        break  # Quit
    
    if cmd == "1":
        # Handle option 1
    elif cmd == "2":
        # Handle option 2
```

### Pattern 3: Text Input with Validation

```python
def validate_email(val):
    if "@" not in val:
        return False, "Email must contain @"
    return True, ""

email = PromptStyle.text(
    "Email address",
    default="user@example.com",
    validator=validate_email
)
```

### Pattern 4: Forced Workflow (--force flag)

```python
def run(self, force=False):
    items = self.get_items()
    
    # Always show preview
    PromptStyle.show_preview("Items", items)
    
    # Only confirm if NOT --force
    if not force:
        if not PromptStyle.confirm("Continue?"):
            return  # Cancelled
    
    # Always show progress/results
    self.execute(items)
    PromptStyle.show_results("Done", success=True, items=items)
```

---

## Testing Your Changes

### Before Committing
```bash
# Verify imports compile
python -m py_compile wai/cli/lib/prompts.py

# Test help system
python -m wai.cli.main help teach

# Test interactive command
# (manually run: python -m wai.cli.main teach)

# Run existing tests
python -m pytest tests/
```

### Manual Testing Checklist
- [ ] Help works: `wai help teach`
- [ ] Happy path: `wai teach` → all defaults → confirm
- [ ] Cancel: `wai teach` → [0] → shows "Cancelled"
- [ ] Invalid input: `wai teach` → [99] → re-prompts
- [ ] Custom input: `wai teach` → [2] → selects 2nd option
- [ ] Keyboard shortcuts: `wai teach` → [l] → same as [2]
- [ ] --force flag: `wai teach --force` → no prompts
- [ ] Output readable on dark background

---

## File Locations

```
wai/cli/lib/
├── prompts.py                    ← All prompt styles
├── help_system.py               ← All help text
├── menu_generator.py            ← Uses prompts.py
└── state_manager.py

wai/cli/commands/
├── teach_interactive.py         ← Interactive teach
├── learn_interactive.py         ← Interactive learn
└── ...

wai/cli/visuals/
└── (formatter for colors)

Documentation:
├── CLI-USABILITY-AUDIT.md
├── CLI-USABILITY-IMPROVEMENTS-DELIVERED.md
├── CLI-USABILITY-TEST-GUIDE.md
└── CLI-USABILITY-QUICK-REFERENCE.md    ← You are here
```

---

## Key Takeaways

1. **Always be clear** - what will happen, what changed, what went wrong
2. **Always be consistent** - same prompts, same formatting, same patterns
3. **Always offer escape** - cancel at any step, Ctrl+C always works
4. **Always show defaults** - users should know they can just press Enter
5. **Always validate** - re-prompt on bad input, never crash
6. **Always confirm** - before anything destructive
7. **Always help** - integrated help, never make users guess

Follow these patterns and your CLI will be **usable, professional, and trustworthy**. 🎯

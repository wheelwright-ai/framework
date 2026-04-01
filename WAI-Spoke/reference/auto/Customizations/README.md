# Customizations Folder

**Purpose:** AI agent creates project enhancements and custom tools here

---

## What Goes Here

The AI agent should create enhancements in this location:
- Custom analysis scripts
- Project-specific automation
- Workflow optimizations
- Quality gates tailored to this project
- Helper utilities discovered during work

## Why This Exists

> "The wheel should know its customizations."

When the AI creates useful tools during sessions, they go here (not scattered randomly).
Lugs track what was created and why - the wheel maintains awareness.

## Agent Guidelines

**When creating custom enhancements:**
1. Create file in `Customizations/`
2. Add lug with `ty='enhancement'` describing what it does
3. Ask user: "Should this enhancement become permanent or be referenced externally?"

**When finding unreferenced files:**
- See global policy: "No unreferenced files"
- Ask user to: evaluate, absorb into project, or add to reference + relocate

## Examples

- `analyze-performance.py` - Custom benchmark script
- `quality-gate.sh` - Project-specific checks
- `workflow-helper.md` - Documentation for custom process

---

## Philosophy

The framework provides wheels. The AI creates customizations that make YOUR wheel roll perfectly for YOUR terrain.

Partnership = Framework foundation + AI customizations + User preferences

---

*Wheelwright Framework v3.0 - github.com/wheelwright-ai/framework*

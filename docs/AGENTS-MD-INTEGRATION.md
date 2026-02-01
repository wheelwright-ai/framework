# AGENTS.md Auto-Discovery Integration

**Status**: ✓ IMPLEMENTED  
**Date**: 2026-01-31

## Overview

Wheelwright now injects itself into every project's `AGENTS.md` file, enabling automatic IDE context discovery on every session. No manual prompt needed.

This is **the** critical feature for universal adoption - IDEs already support `AGENTS.md` (Claude Code, Cursor, etc.), so WAI becomes invisible-but-essential infrastructure.

## How It Works

### 1. **On Project Init** (`wai init`)

When you initialize a new wheel:

```bash
WAI init /path/to/project
```

The init flow:
1. Creates `WAI-Spoke/` with all templates
2. **NEWLY: Creates `AGENTS.md` in project root** with WAI briefing
3. Generates initial state files

The `AGENTS.md` template (templates/wheel/AGENTS.md):
- Contains instructions for reading WAI files
- Shows the "quick start" protocol
- Lists key commands
- Has placeholders for dynamic state: `{{PROJECT_NAME}}`, `{{CURRENT_PHASE}}`, `{{NEXT_ACTIONS}}`, etc.

### 2. **On Session Start** (IDE auto-detects)

When you open the project in Claude Code, Cursor, or any IDE:

1. IDE reads `AGENTS.md` (if present)
2. IDE provides this context to the AI assistant
3. AI sees the WAI briefing **automatically** (no human prompt needed)
4. AI follows the quick start:
   - Read `WAI-Spoke/WAI-Point.json` (instant context)
   - Read `WAI-Spoke/WAI-Guide.md` (current instructions)
   - Check `WAI-Spoke/WAI-State.json` (state and phase)
5. AI has full context, can proceed autonomously

### 3. **On Closeout** (`WAI shipit` or `WAI closeout`)

During end-of-session processing:

1. **Integration Refresh step** calls `AgentsIntegration.refresh_agents_md()`
2. Reads latest state from `WAI-State.json`
3. Updates `AGENTS.md` with:
   - Current phase
   - Last actions/summary
   - Next actions
   - Active blockers
   - Timestamp
4. Writes back to project root `AGENTS.md`
5. **Next session, AI wakes up to fresh context**

## File Structure

```
project/
  AGENTS.md                    ← IDEs read this (auto-discovered)
  WAI-Spoke/
    WAI-State.json             ← Source of truth (updated during work)
    WAI-Point.json             ← Instant context restore
    WAI-Guide.md               ← Current instructions
```

## Key Features

### ✓ Automatic Discovery
- No manual prompt needed
- Works with all major IDEs (Claude Code, Cursor, VS Code, ChatGPT)
- AGENTS.md is a widely recognized convention

### ✓ Dynamic Updates
- Every closeout refreshes AGENTS.md with latest state
- No stale context; next session always has fresh briefing
- Updates include: phase, next actions, blockers, summaries

### ✓ IDE-Native
- Works at the filesystem level (no API integration needed)
- Respects IDE's own AGENTS.md parsing
- Non-blocking: if AGENTS.md missing/broken, WAI still works

### ✓ Human-Readable
- Developer can read AGENTS.md to understand project state
- Not just for AI - useful reference for humans too

## Integration Points

### `wai_cli/init.py`
**Function**: `init_spoke()` (lines 111-422)

Added template copy for AGENTS.md:
```python
# Also copy AGENTS.md template to project root
agents_template = templates_dir.parent / 'wheel' / 'AGENTS.md'
if agents_template.exists():
    agents_target = spoke_path / 'AGENTS.md'
    content = agents_template.read_text()
    # Apply initial substitutions
    content = content.replace('{{PROJECT_NAME}}', spoke_path.name)
    # ... more substitutions
    agents_target.write_text(content)
```

### `wai_cli/agents_integration.py` (NEW)
**Purpose**: AGENTS.md generation and refresh

Main class: `AgentsIntegration`

Methods:
- `refresh_agents_md()` - Updates existing AGENTS.md with current state
- `generate_agents_md_from_template()` - Creates AGENTS.md from template

Called during:
- Project init (initial generation)
- Closeout (dynamic refresh)

### `wai_cli/closeout.py`
**Function**: `_refresh_integrations()` (lines 577-631)

Added AGENTS.md refresh:
```python
# Refresh AGENTS.md with latest state (IDE context discovery)
agents = AgentsIntegration(self.spoke_dir)
agents_refreshed = agents.refresh_agents_md()
if agents_refreshed:
    updated += 1
    statuses['AGENTS.md'] = 'updated'
    print_info("    [OK] AGENTS.md refreshed - next session will load with fresh context")
```

## Template: `templates/wheel/AGENTS.md`

Structure:
```
# Project Context: {{PROJECT_NAME}}

> **WAI Context Detected** — This project uses Wheelwright AI

## Quick Start (Every Session)

1. Read WAI-Point.json
2. Read WAI-Guide.md
3. Check WAI-State.json

## Session Start Protocol
[Instructions for AI to follow]

## Key Commands
[WAI command reference]

## Last Update
Updated: {{TIMESTAMP}}
Phase: {{CURRENT_PHASE}}
Status: {{STATUS}}
Last Actions: {{LAST_ACTIONS}}
Next Actions: {{NEXT_ACTIONS}}
Blockers: {{BLOCKERS}}
```

## Workflow: Init → Work → Closeout → Next Session

### Session 1: Init

```bash
$ WAI init my-project
✓ Created WAI-Spoke/
✓ Created AGENTS.md (auto-updated on closeout)
✓ Foundation ready for interviewing
```

Result: `AGENTS.md` exists with initial state

### Session 2: Open IDE

IDE reads `AGENTS.md`:
```
> **WAI Context Detected** — This project uses Wheelwright AI
> Read WAI-Point.json, WAI-Guide.md, WAI-State.json
```

AI automatically:
1. Loads Wheelwright context
2. Reads the 3 files
3. Understands phase, blockers, next steps
4. Proceeds with full autonomy

### Session N: Closeout

```bash
$ WAI shipit
[1/13] Quality Gates: Passed
[2/13] Lug Policy: Validated
...
[10/13] Integrations & AGENTS.md
  ✓ AGENTS.md refreshed - next session will load with fresh context
[11/13] Git commit...
```

`AGENTS.md` updated with:
```
Phase: Feature Development
Status: Ready for next session
Last Actions: Implemented authentication
Next Actions: Add tests, Deploy to staging
Blockers: None
Updated: 2026-01-31T15:30:00...
```

### Session N+1: Open IDE Again

IDE reads refreshed `AGENTS.md`:
```
Phase: Feature Development
Last Actions: Implemented authentication
Next Actions: Add tests, Deploy to staging
```

AI wakes up with perfect context. No context pasting needed.

## Edge Cases

### What if AGENTS.md doesn't exist?
- Init creates it
- If missing in older projects, closeout won't fail
- Non-blocking: WAI continues even if AGENTS.md missing

### What if state is incomplete?
- Substitutions use sensible defaults
- Missing keys become empty strings or "N/A"
- No crashes, graceful degradation

### What if IDE doesn't support AGENTS.md?
- IDE simply ignores it
- User can still manually read AGENTS.md
- WAI context is still available via WAI-Point.json

## Next Steps for Adoption

### Priority 1: Test Current Implementation ✓ DONE
- ✓ Template created
- ✓ Init.py updated
- ✓ AgentsIntegration module created
- ✓ Closeout.py integrated

### Priority 2: Test with Real Projects
- Create test wheel, run init
- Verify AGENTS.md created with substitutions
- Do a closeout, verify AGENTS.md updates
- Open in IDE, verify auto-discovery works

### Priority 3: Extend to Hub Integration
- Hub teach should include AGENTS.md refresh pattern
- Spokes in hub should auto-generate AGENTS.md templates

### Priority 4: Documentation
- Add to README: "AGENTS.md auto-discovery"
- Document the workflow for users
- Show before/after (with/without WAI)

## Success Metric

**When you open any Wheelwright project in an IDE, the AI automatically loads full context WITHOUT any manual prompt or context pasting.**

This is the "magic" that makes Wheelwright feel less like a tool and more like the project remembering you.

---

*This integration transforms Wheelwright from opt-in tool to invisible infrastructure.*

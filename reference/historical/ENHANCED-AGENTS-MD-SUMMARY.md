# AGENTS.md Enhancement: Living Document Summary

**Date**: 2026-01-31  
**Enhancement**: AGENTS.md now automatically surfaces incomplete multi-stage work  
**Tests**: 7 tests, all passing ✓

---

## What Changed

### Before (Basic Version)
AGENTS.md updated with static values on closeout:
```markdown
# Project Context: my-project

Phase: Implementation
Status: Ready
Next Actions:
- Implement auth - Stage 1 of 3
- Add tests
- Deploy
```

**Problem**: AI doesn't know you're only 1/3 done. Next session shows same actions with no context about continuation.

### After (Living Document)
AGENTS.md now generates intelligent briefing on closeout:
```markdown
# Project Context: my-project

## Session Focus (Must Continue)

[INCOMPLETE] **WORK FROM LAST SESSION**
Summary: Implemented partial auth (stage 1/3 complete)

[CONTINUE] **MULTI-STAGE ITEMS - IN SEQUENCE**
- Implement auth - Stage 1 of 3
- Add tests
- Deploy

[BLOCK] **BLOCKERS TO RESOLVE FIRST**
- Need OAuth token

Continuing from last session:
  - Auth module
  - JWT tokens

---

## Quick Start (Every Session)
...

Phase: Implementation
Status: Ready for next session
Last Actions: Implemented auth stage 1
Next Actions:
- Implement auth - Stage 1 of 3 (MULTI-STAGE - CONTINUE)
- Add tests
- Deploy
```

**Result**: AI wakes up knowing:
- "We're building a 3-stage auth system"
- "Stage 1 is done, we need to continue"
- "OAuth token blocks us"
- "Last session worked on auth module + JWT"

---

## Key Features

### 1. **Smart Pattern Detection**

| Pattern | Detected As | Example |
|---------|------------|---------|
| Contains "stage/phase/part/step" | Multi-stage item | "Implement auth - Stage 1 of 3" |
| Last session summary has "partial/incomplete/wip" | Incomplete work | "Implemented partial auth (1/3)" |
| blockers array exists | High priority | "Need OAuth token" |
| last_closeout.key_topics | Continuation context | ["Auth module", "JWT"] |

### 2. **Intelligent Append on Init**

- **Before**: Init would overwrite AGENTS.md
- **After**: Init appends new briefing, preserves existing
- If re-running init, existing context isn't blown away

### 3. **Topical Briefing Section**

Generated automatically on closeout:
```markdown
## Session Focus (Must Continue)
```

Contains:
- Incomplete work from last session
- Multi-stage items with emphasis on sequencing
- Blockers to resolve first
- Key topics from last session

---

## Code Changes

### New Methods in AgentsIntegration

#### `_build_topical_next_actions(next_actions, state)`
Emphasizes multi-stage items and continuations:
```python
if 'stage' in action.lower():
    return f"**{action}** (MULTI-STAGE - CONTINUE)"
```

#### `_generate_topical_briefing(state, next_actions)`
Intelligently surfaces incomplete work:
```python
if 'partial' in summary.lower():
    briefing.append("[INCOMPLETE] **WORK FROM LAST SESSION**")
    briefing.append(f"Summary: {summary}")
```

### Modified: init.py

Now appends instead of overwrites:
```python
if agents_target.exists():
    # APPEND: Preserve existing, add new briefing
    if spoke_path.name not in existing or '## Session Focus' not in existing:
        # Merge new content
        agents_target.write_text(content)
else:
    # CREATE: First time
    agents_target.write_text(content)
```

### Enhanced: closeout.py

Calls the new topical briefing:
```python
briefing_section = self._generate_topical_briefing(state, next_actions)
if briefing_section:
    # Insert new "Session Focus" section
    updated_content = updated_content.replace(
        '\n## Last Update',
        f'\n## Session Focus (Must Continue)\n\n{briefing_section}\n\n## Last Update'
    )
```

### Updated: Template

Added explanation note:
```markdown
## Important Notes

> **This file updates itself on every closeout.** AGENTS.md becomes a 
> living document that evolves with your project. Each session you open 
> this project, you'll see:
> - What was accomplished last session
> - What MUST continue this session (multi-stage items, incomplete work)
> - Any blockers to resolve first
> - Next actions in priority order
```

---

## Test Coverage (7 Tests)

### Original Tests (5)
1. ✅ Template exists with placeholders
2. ✅ Init.py includes AGENTS.md copy
3. ✅ Closeout.py calls refresh
4. ✅ State substitutions work
5. ✅ Error handling graceful

### New Tests (2) ← Added Today
6. ✅ **Topical briefing generated for incomplete work**
   - Multi-stage items detected and marked
   - Incomplete work surfaced with [INCOMPLETE] tag
   - Blockers highlighted with [BLOCK] tag
   - Last session topics included

7. ✅ **Init appends intelligently, doesn't overwrite**
   - Existing AGENTS.md preserved on re-init
   - New briefing merged intelligently
   - Project name and structure maintained

All tests pass: `python tests/test_agents_integration.py` ✓

---

## Real-World Flow

### Session 1: Init
```bash
$ WAI init my-project
✓ Created AGENTS.md with template
```

### Session 2: Work on Multi-Stage Item
```bash
# Work on "Implement auth - Stage 1 of 3"
# Closeout summary: "Implemented partial auth (stage 1/3)"

$ WAI shipit
✓ Closeout processing...
✓ AGENTS.md refreshed with Session Focus briefing
```

**AGENTS.md now contains**:
```markdown
## Session Focus (Must Continue)

[INCOMPLETE] **WORK FROM LAST SESSION**
Summary: Implemented partial auth (stage 1/3)

[CONTINUE] **MULTI-STAGE ITEMS - IN SEQUENCE**
- Implement auth - Stage 1 of 3
- Add tests
- Deploy
```

### Session 3: Open IDE
```bash
IDE reads AGENTS.md
├─→ Sees "Session Focus (Must Continue)"
├─→ Sees "[INCOMPLETE]" tag
├─→ Sees "[CONTINUE] MULTI-STAGE ITEMS"
└─→ Shows AI: "Stage 1 complete, need to continue with stages 2 & 3"

AI: "I see you implemented stage 1 of the auth system last time. 
     Shall we move on to stage 2: [next stage details]?"
```

**Zero manual prompts. Perfect context. AI knows exactly what to do.**

---

## Why This Matters

### For AI Autonomy
- AI no longer needs "what should we do?" prompt
- Context includes "what we must continue"
- Can proceed confidently with multi-stage work

### For Multi-Stage Features
- Long, complex features tracked naturally
- Progress is visible in AGENTS.md
- No context loss between sessions
- Blockers are surfaced automatically

### For Project Continuity
- AGENTS.md becomes the "project brief"
- Updates automatically on every closeout
- Living document that reflects current state
- Perfect for context windows and session starts

---

## Files Modified/Created

| File | Action | Lines |
|------|--------|-------|
| `wai_cli/agents_integration.py` | Enhanced with topical methods | +93 |
| `wai_cli/init.py` | Changed to intelligent append | +12 |
| `templates/wheel/AGENTS.md` | Added explanation note | +8 |
| `tests/test_agents_integration.py` | Added 2 new tests | +87 |
| `AGENTS-MD-LIVING-DOCUMENT.md` | Documentation | New |
| `WAI-Spoke/WAI-State.json` | Updated decision | Modified |
| `WAI-Spoke/WAI-State.md` | Updated current focus | Modified |

---

## Verification

All systems ready:
- ✅ Code syntax valid
- ✅ 7 tests pass (including 2 new)
- ✅ Error handling graceful
- ✅ Non-blocking on failures
- ✅ Documentation complete
- ✅ Decision logged in WAI-State.json

---

## Next Steps

1. **Manual Test** (ready now)
   ```bash
   WAI init test-project
   # Edit project
   WAI shipit
   # Verify AGENTS.md has Session Focus section
   ```

2. **Real Project Test**
   - Use this on actual multi-stage feature
   - Verify multi-stage items are highlighted
   - Confirm AI gets context on session start

3. **Hub Integration** (Phase 2)
   - Distribute AGENTS.md patterns across hub
   - Spokes inherit briefing generation logic

---

## The Vision

**AGENTS.md transforms from:**
- Static IDE discovery file
- Plain state value substitution

**Into:**
- Living project brief
- Intelligent work continuity tracker
- Self-updating context for AI autonomy

**When you open a Wheelwright project:**
- IDE auto-discovers AGENTS.md
- AI reads the latest briefing
- AI knows what was done, what's incomplete, what must continue
- AI proceeds with full autonomy, zero manual prompts

This is Wheelwright's superpower: **Perfect context continuity that enables true AI autonomy.**

---

*With AGENTS.md as a living document, multi-stage features become natural. The project remembers itself.*

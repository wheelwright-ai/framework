# AGENTS.md as a Living Document

**Enhancement**: AGENTS.md now evolves with your project, not just updating static state values.

## The Problem With Static Updates

**Before**: AGENTS.md just substituted placeholder values:
```markdown
Phase: Implementation
Status: Ready
Next Actions:
- Implement auth - Stage 1 of 3
- Add tests
- Deploy
```

On closeout, it would just update the timestamp and phase. But what if you only got to "Stage 1 of 3"? 
Next session, it would show the SAME actions, with no hint that you're in the middle of a multi-stage item.

**Result**: AI doesn't know what's incomplete. No context about what MUST continue vs what's truly done.

---

## The Solution: Topical Briefing

**After**: AGENTS.md now surfaces incomplete work and unfinished stages:

```markdown
# Project Context: my-project

## Session Focus (Must Continue)

[INCOMPLETE] **WORK FROM LAST SESSION**
Summary: Implemented partial authentication (stage 1/3 complete)

[CONTINUE] **MULTI-STAGE ITEMS - IN SEQUENCE**
- Implement authentication - Stage 1 of 3
- Set up database  
- Add tests

[BLOCK] **BLOCKERS TO RESOLVE FIRST**
- Need OAuth provider token

Continuing from last session:
  - Auth module
  - JWT tokens

---

## Quick Start (Every Session)
[... rest of briefing ...]

## Last Update
Updated: 2026-01-31T16:30:00Z
Phase: Implementation
Status: Ready for next session
```

**Result**: AI opens the project and immediately knows:
- "We're in the middle of a 3-stage auth implementation"
- "Only stage 1 is done, stages 2-3 must continue"
- "We need an OAuth token before we can proceed"
- "Last session worked on Auth module and JWT"

---

## How It Works

### On Init
```
User: WAI init my-project
│
├─→ Create AGENTS.md from template
├─→ If AGENTS.md already exists: APPEND new briefing (don't overwrite)
└─→ Project ready with IDE context
```

### On Closeout
```
User: WAI shipit
│
├─→ Process session
├─→ Read WAI-State.json looking for:
│   - Multi-stage items (words: "stage", "phase", "part", "step")
│   - Incomplete work (words: "started", "partial", "incomplete", "wip")
│   - Blockers that need resolution first
│   - Last session's key topics
│
├─→ Generate "Session Focus (Must Continue)" section
│   - Emphasize incomplete multi-stage work
│   - Surface unfinished items clearly
│   - Highlight blockers to resolve first
│
└─→ Update AGENTS.md with:
    - New phase
    - New status
    - Session Focus section (smart briefing)
    - Last actions & key topics
    - Timestamp
```

### On Next Session
```
IDE Opens project
│
├─→ Reads AGENTS.md
├─→ AI sees:
│   "Session Focus (Must Continue)"
│   "We're in middle of 3-stage auth, only 1/3 done"
│   "Blocker: need OAuth token"
│   "Last session: Auth module, JWT tokens"
│
└─→ AI proceeds knowing EXACTLY what to do
    NO manual prompts needed
    FULL context about continuation
```

---

## What Triggers the Briefing

### Pattern: Multi-Stage Items

If next_action contains: "stage", "phase", "part", "step"
```
"Implement authentication - Stage 1 of 3"
```
→ Marked as: `(MULTI-STAGE - CONTINUE)`

### Pattern: Incomplete Work

If last_closeout summary contains: "started", "partial", "incomplete", "wip", "in progress"
```
"Implemented partial authentication (stage 1/3 complete)"
```
→ Section: `[INCOMPLETE] WORK FROM LAST SESSION`

### Pattern: Blockers

If context.blockers exists:
```
"Need OAuth provider token"
```
→ Section: `[BLOCK] BLOCKERS TO RESOLVE FIRST`

### Pattern: Key Topics

If last_closeout.key_topics exists:
```
["Auth module", "JWT tokens"]
```
→ Section: `Continuing from last session:`

---

## Code: Enhanced AgentsIntegration

Two new methods enable topical briefing:

### 1. `_build_topical_next_actions()`

```python
def _build_topical_next_actions(self, next_actions: list, state: dict) -> str:
    """
    Build next actions emphasizing multi-stage items.
    
    - Detect "stage", "phase", "part", "step" keywords
    - Mark them as (MULTI-STAGE - CONTINUE)
    - Include last session's topics for continuity
    """
```

Transforms:
```
["Implement auth - Stage 1 of 3", "Add tests", "Deploy"]
```
Into:
```
- **Implement auth - Stage 1 of 3** (MULTI-STAGE - CONTINUE)
- Add tests
- Deploy

**Continuing from last session:**
  - Auth module
  - JWT tokens
```

### 2. `_generate_topical_briefing()`

```python
def _generate_topical_briefing(self, state: dict, next_actions: list) -> str:
    """
    Generate briefing that surfaces incomplete work.
    
    Detects:
    - Incomplete work from last session
    - Multi-stage items that need sequencing
    - Blockers that must be resolved first
    """
```

Returns a formatted section like:
```
[INCOMPLETE] **WORK FROM LAST SESSION**
Summary: Implemented partial auth (1/3)

[CONTINUE] **MULTI-STAGE ITEMS - IN SEQUENCE**
- Implement auth - Stage 1 of 3
- ... (stages 2, 3)

[BLOCK] **BLOCKERS TO RESOLVE FIRST**
- Need OAuth token
```

---

## Append Logic (Init.py)

On reinit, init.py now APPENDS rather than overwrites:

```python
if agents_target.exists():
    # APPEND: Preserve existing context, add new briefing
    existing = agents_target.read_text()
    # Only append if this is new content
    if spoke_path.name not in existing or '## Session Focus' not in existing:
        # Insert new briefing before Last Update section
        agents_target.write_text(new_content)
else:
    # CREATE: First time
    agents_target.write_text(content)
```

**Result**: If you reinit a project, AGENTS.md isn't blown away. New briefing is merged in intelligently.

---

## Real-World Example

### Session 1: Start Multi-Stage Feature

```bash
$ WAI init feature-5stage-auth
```

AGENTS.md created:
```
Phase: Initialization
Next Actions:
- Design authentication system
- Implement JWT support
- Add password recovery
- Write tests
- Deploy to staging
```

### Session 2: Complete Stage 1

Implemented JWT but didn't get to password recovery.

Closeout summary:
```
"Implemented JWT authentication system (Stage 1/5 complete)"
```

AGENTS.md refreshed:
```markdown
## Session Focus (Must Continue)

[INCOMPLETE] **WORK FROM LAST SESSION**
Summary: Implemented JWT auth (Stage 1/5 complete)

[CONTINUE] **MULTI-STAGE ITEMS - IN SEQUENCE**
- Implement JWT support (DONE)
- Add password recovery (NEXT!)
- Write tests
- Deploy to staging

Continuing from last session:
  - JWT tokens
  - Bearer auth
```

### Session 3: Open IDE

IDE reads AGENTS.md with Session Focus section.

AI immediately knows:
- "We're building a 5-stage auth system"
- "Stage 1 (JWT) is done"
- "Stage 2 (password recovery) is what we need to do next"
- "Last session worked on JWT tokens and bearer auth"

**AI: "I see we completed the JWT implementation last session. Shall we move on to password recovery, or finish any loose ends?"**

No manual prompt. Perfect context. AI understands the sequence.

---

## Test Coverage

7 tests verify the living document behavior:

1. ✅ Template exists with placeholders
2. ✅ Init includes AGENTS.md template
3. ✅ Closeout calls refresh
4. ✅ State substitutions work
5. ✅ Error handling graceful
6. ✅ **Topical briefing generated for incomplete work** ← NEW
7. ✅ **Init appends intelligently, doesn't overwrite** ← NEW

---

## Files Modified

| File | Change | Lines |
|------|--------|-------|
| `wai_cli/agents_integration.py` | Added `_build_topical_next_actions()`, `_generate_topical_briefing()` | +93 |
| `wai_cli/init.py` | Changed to append instead of overwrite | +12 modified |
| `templates/wheel/AGENTS.md` | Added "Important Notes" section | +9 |
| `tests/test_agents_integration.py` | Added topical briefing & append tests | +87 |

---

## Why This Matters

**Before AGENTS.md Living Document:**
- User must manually tell AI "we're in stage 2 of 3"
- AI doesn't know what's incomplete
- No persistence of multi-stage context

**After AGENTS.md Living Document:**
- AGENTS.md automatically surfaces incomplete work
- AI reads the briefing and understands the sequence
- Multi-stage items are tracked naturally
- No manual context needed

**Result**: AI autonomy becomes truly feasible. The project "remembers" its state, and communicates it clearly on every session start.

---

## Future Enhancements

1. **Infer multi-stage from git commits**
   - Look for patterns like "Stage 1/3" in commit messages
   - Auto-detect incomplete features

2. **Depend detection**
   - Surface dependencies between next actions
   - "Can't do X until Y is complete"

3. **Progress tracking**
   - Show % completion for multi-stage items
   - Track which stages are actually done

4. **Integration with Lugs**
   - AGENTS.md could show open Lugs related to next actions
   - Link incomplete work to specific Lugs

---

**Summary**: AGENTS.md is no longer just an IDE discovery file. It's the living, evolving brief that communicates project state, incomplete work, and continuations on every session. The project remembers itself.

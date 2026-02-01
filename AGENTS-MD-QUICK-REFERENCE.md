# AGENTS.md Auto-Discovery - Quick Reference

## The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│  IDE (Claude Code, Cursor, VS Code)                         │
│                                                              │
│  On session start:                                           │
│  1. Auto-reads AGENTS.md from project root                  │
│  2. Provides content to AI assistant                        │
│  3. AI sees WAI briefing automatically (NO PROMPT NEEDED!)  │
└─────────────────────────────────────────────────────────────┘
                            ↓
          Reads: WAI-Point.json, WAI-Guide.md, WAI-State.json
                            ↓
                  AI loads with FULL CONTEXT
                  Ready for autonomous operation
```

## How It Gets Updated

```
Session Work
    ↓
WAI shipit (or WAI closeout)
    ↓
Closeout reads WAI-State.json
    ↓
AgentsIntegration.refresh_agents_md()
    ↓
AGENTS.md updated with:
  - Current phase
  - Recent actions
  - Next actions
  - Blockers
  - Timestamp
    ↓
Next session → AI wakes up with FRESH context
```

## What Changes

### Before (Jan 2026 - Old Way)

```bash
$ Open IDE
AI: "Hi, I can help with your project"
User: "Check my WAI point please"
User: Manually runs `WAI context` and pastes output
AI: Finally has context after manual pasting
```

**Problem**: Manual, friction, not scalable

### After (Jan 31 2026 - New Way)

```bash
$ Open IDE
IDE auto-reads AGENTS.md
AI: "I see your project is in [Phase]. Last session you [Action]. 
     Next I'd suggest [Next Action]. Any blockers are [Blocker]."
User: "Great, let's start with..."
AI: Already has context, ready to go
```

**Result**: Frictionless, automatic, scalable

## File Checklist

### On Init
- ✅ `project/AGENTS.md` created with initial state
- ✅ Contains: project name, phase, quick start instructions
- ✅ Has placeholders for state values

### On Closeout
- ✅ `project/AGENTS.md` refreshed with latest state
- ✅ Updated fields: timestamp, phase, actions, blockers
- ✅ Ready for next IDE session

### Files Involved
```
Templates:
  templates/wheel/AGENTS.md          ← Template with placeholders

Code:
  wai_cli/agents_integration.py      ← Refresh logic
  wai_cli/init.py                    ← Create on init
  wai_cli/closeout.py                ← Refresh on closeout

Tests:
  tests/test_agents_integration.py   ← 5 passing tests

Docs:
  docs/AGENTS-MD-INTEGRATION.md      ← Full technical doc
  IMPLEMENTATION-SUMMARY.md          ← Complete walkthrough
  AGENTS-MD-QUICK-REFERENCE.md       ← This file
```

## Testing

**All tests pass** ✅

```
python tests/test_agents_integration.py

OK: AGENTS.md template exists with placeholders
OK: Init integration works
OK: Closeout integration works
OK: State substitutions correct
OK: Error handling graceful
```

## Real-World Example

### Project: feature-auth

**Init phase** (2026-01-31 10:00 AM):
```markdown
# Project Context: feature-auth

Phase: Initialization
Status: Initializing wheel...
Next Actions:
- Complete project foundation
- Define scope and boundaries
Blockers: None
```

**After 1st session** (2026-01-31 4:30 PM closeout):
```markdown
# Project Context: feature-auth

Phase: Implementation
Status: Ready for next session
Last Actions: Built authentication module, added JWT support
Next Actions:
- Write integration tests
- Set up password recovery
- Deploy to staging
Blockers: None
Updated: 2026-01-31T16:30:00Z
```

**Next session** (2026-02-01 9:00 AM):
IDE auto-reads this updated context. AI immediately knows:
- We're in Implementation phase
- Last session added auth module & JWT
- Next focus is tests & password recovery
- No blockers

No context pasting. No manual prompts. Just intuitive continuity.

## For Different Roles

### Developer
- Read: `AGENTS.md` shows you what happened, what's next
- Benefit: Understand project state at a glance

### AI Assistant
- Read: `AGENTS.md` loaded automatically on session start
- Benefit: Full context without manual prompts

### IDE
- Discovered: `AGENTS.md` in project root
- Benefit: Automatic context loading for any tool

### Hub
- Future: Distribute AGENTS.md patterns across projects
- Benefit: Consistent project context across organization

## The Power

**One simple file solves three problems:**

1. **Visibility** - IDEs can see Wheelwright projects
2. **Continuity** - AI gets context on session start
3. **Autonomy** - No manual prompts needed

This makes Wheelwright not a "tool you use" but "infrastructure that just works."

## Next: What Happens After This

### Coming Soon
1. **Hub Integration** - Hub teaches spokes AGENTS.md patterns
2. **Cross-Project** - Learnings flow via AGENTS.md templates
3. **IDE Extensions** - Native VS Code/Cursor support

### Far Future
1. **Cloud Sync** - AGENTS.md synced across machines
2. **Team Hub** - Organization-wide context sharing
3. **Marketplace** - AGENTS.md templates for different project types

---

**Bottom Line**: WAI is now woven into the IDE fabric. Every Wheelwright project speaks to AI automatically. Adoption is no longer a question - it's inevitable.

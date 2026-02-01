# WAI-Guide.md
**Version:** 3.0.0
**Project:** Wheelwright Framework
**Repository:** https://github.com/wheelwright-ai/framework
**Purpose:** AI instructions, protocols, and hub learnings
**Audience:** AI (primary)
**Managed by:** Framework (generated from hub teachings)
**Last Updated:** 2026-02-01T02:30:00Z

---

# Wheelwright Framework Guide

**For Humans:** This project uses Wheelwright for AI-assisted development with continuous context across sessions.

**For AI Assistants:** Read the sections below BEFORE making any changes to this project.

---

**Framework Version:** 1.0
**Repository:** https://github.com/wheelwright-ai/framework
**Created by:** Mario Vaccari

*"We aren't reinventing the wheel - we're evolving it faster than one person ever could."*

---

## What is Wheelwright?

Wheelwright builds AI wheels that remember everything. Instead of losing context when sessions end, your wheel rolls forward continuously - maintaining memory, learning patterns, and extending capabilities.

### The Wheel Metaphor
- **Hub** = Central memory and consolidated knowledge
- **Spokes** = Specialized capabilities (analysis, consultation, code review)
- **Rim** = The interface connecting to any LLM
- **Rolling** = Each turn moves forward, never losing ground

---

## AI INSTRUCTIONS - READ FIRST

### Context Refresh Check (Do This First!)

**Every session, check if the `WAI-Spoke/` folder has been updated since you last worked here:**

```python
import json
from pathlib import Path
from datetime import datetime

wai_path = Path("WAI-Spoke")
kb_sync = json.loads((wai_path / "kb-sync.json").read_text()) if (wai_path / "kb-sync.json").exists() else {}
state = json.loads((wai_path / "WAI-State.json").read_text())
wai_meta = state.get("wheelwright", {})

# Check for new hub teachings
hub_version = wai_meta.get("hub_reference", {}).get("current_hash_short", "unknown")
last_teach = wai_meta.get("sync_history", [{}])[-1].get("date", "never") if wai_meta.get("sync_history") else "never"

print(f"Hub version: {hub_version}")
print(f"Last teach sync: {last_teach}")
print(f"Days since sync: {wai_meta.get('development_health', {}).get('days_since_sync', 'unknown')}")
```

**If you see new learnings or policies were added:**
1. Read this entire file again for updated instructions
2. Check `kb-sync.json` for new hub knowledge version
3. Review any new sections in this README (especially "Learnings from Hub")
4. Apply new patterns to your current work

---

### Your Core Files

| `WAI-State.json` | Technical spec, foundation, session state | UPDATE |
| `WAI-State.md` | Strategic context, vision | UPDATE |
| `WAI-Dev-Profile.json` | Developer credentials, preferences, autonomy level | READ ONLY |
| `WAI-Point.json` | Minimal bootstrap for context restoration | READ ONLY (Update on shipit) |
| `wheel-signals.jsonl` | High-impact learnings | APPEND (never overwrite) |
| `lugs.jsonl` | Active task/dependency graph | UPDATE (via tools/CLI) |
| `kb-sync.json` | Hub sync status | READ ONLY |
| `WAI-Guide.md` (this file) | Your instructions | READ ONLY |

---

## CRITICAL: Foundation Check

**Before ANY work, check the project foundation:**

```python
import json
from pathlib import Path

state = json.loads(Path("WAI-Spoke/WAI-State.json").read_text())
foundation = state.get("_project_foundation", {})

if not foundation.get("completed"):
    print("STOP: Foundation incomplete!")
    print("Guide user through foundation setup before proceeding.")
```

### If Foundation is Incomplete

Do NOT proceed with any work. Instead, guide the user through establishing:

**1. Identity (ask conversationally):**
- "What's the one-sentence description of this project?"
- "Is this code, research, writing, design, or a mix?"
- "What does 'done' look like for you?"

**2. Boundaries:**
- "What's definitely IN scope for this project?"
- "What should we explicitly AVOID or consider out of scope?"
- "Any constraints I should know about? (time, tech, etc.)"

**3. Approach:**
- "What tools or technologies are we using?"
- "How do you want to work with AI - should I take initiative or check in frequently?"
- "How should decisions get reviewed?"

**After gathering answers:**
1. Update `_project_foundation` in WAI-State.json
2. Set `completed: true` with timestamp and your AI name
3. Add first entry to `evolution_log`
4. Update WAI-State.md with the vision

---

## Implementation Approval Gate

If the user asks for planning/ideation, pause after the plan and ask for explicit approval before making code changes.

---

## Stewardship Philosophy

You are a **responsible partner**, not just an enabler.

### Core Principle
> Enable but remain intentful. When vibe coding strays too far, you are best
> positioned to reign the project back in and ensure changes are deliberate.

### Required Behaviors

1. **Detect Scope Drift**
   - Before enabling work, check if it fits `boundaries.in_scope`
   - If request seems outside scope, FLAG it before proceeding

2. **Require Acknowledgment for Changes**
   - Direction changes need explicit user approval
   - Never silently expand scope

3. **Complete Foundation First**
   - No work until foundation is established
   - This is not optional

4. **Prefer Verification**
   - "Are you sure?" over silent compliance
   - When uncertain, ask

### Drift Detection Template

When you detect potential scope drift:

```markdown
## Scope Check

I want to verify this request aligns with our established foundation:

**Request:** [what user asked for]

**Current Boundaries:**
- In scope: [from foundation]
- Out of scope: [from foundation]

**Assessment:** [why this might be drift]

**Options:**
1. **Evolve** - Update foundation to include this
2. **Stay course** - Decline, keep original scope
3. **Explore** - Discuss before deciding

Which would you prefer?
```

---

## Session State Protocol

### On Session Start

```python
import json
from pathlib import Path

state = json.loads(Path("WAI-Spoke/WAI-State.json").read_text())
session = state.get("_session_state", {})

print(f"Last modified by: {session.get('last_modified_by')}")
print(f"At: {session.get('last_modified_at')}")
print(f"Requires review: {session.get('requires_review')}")

if session.get('requires_review'):
    print(f"Review reason: {session.get('review_reason')}")
    # Trigger change review process
```

### When Making Changes

Update `_session_state`:
```json
{
  "_session_state": {
    "last_session_id": "your-unique-session-id",
    "last_modified_by": "Claude/GPT/Copilot + timestamp",
    "last_modified_at": "ISO-8601-timestamp",
    "session_count": "increment by 1",
    "requires_review": false
  }
}
```

**CLI menu parity rule:** When adding or extending WAI-CLI commands, update the interactive menus and help text to match.

### Before Closing Session

If you made significant changes:
```json
{
  "requires_review": true,
  "review_reason": "Brief description of what changed"
}
```

---

## Signaling High-Impact Learnings

When you make a decision with **impact >= 8**, share it:

### 1. Add to decisions array in WAI-State.json
```json
{
  "date": "2025-12-28",
  "decision": "Description of the decision",
  "rationale": "Why this was the right choice",
  "impact": 8,
  "by": "Your AI name"
}
```

### 2. Append to wheel-signals.jsonl
```json
{"timestamp": "ISO-8601", "by": "AI-Name", "hub_kb_version": "...", "wheel_kb_version": "...", "offers": [{"type": "pattern_type", "topic": "Brief title", "impact": 8, "context": "Why this matters"}], "requests": [], "flags": {"has_high_impact_learnings": true}}
```

**IMPORTANT:** Append only, never overwrite wheel-signals.jsonl!

### What to Signal
- Architectural breakthroughs
- Patterns that saved significant time
- Critical bugs avoided
- Cross-project applicable solutions

### What NOT to Signal
- Project-specific implementation details
- Minor refactorings (impact < 8)
- Personal preferences without justification
- **Common knowledge** - Things any competent developer knows
- **Obvious patterns** - Standard practices documented everywhere
- **Routine fixes** - Normal debugging without novel insight

---

## Session Commands

Wheelwright commands work with or without the `WAI` prefix. If you're unsure whether a command like "Status" refers to WAI or something else, ask: *"Did you mean WAI Status?"*

### Command Reference

| Say This | Slash Command | What It Does |
|----------|---------------|--------------|
| **WAI** | `/wai` | Wakeup - load context, verify, brief |
| **Status** | `/wai-status` | Health check + recommendations |
| **Time** | `/wai-time` | Token capacity check |
| **Rules** | `/wai-rules` | Show boundaries and protocols |
| **Closeout** | `/wai-closeout` | End session ceremony |
| **Shipit** | `/wai-shipit` | Closeout + commit |
| **Lugs** | `/wai-lug` | Manage task/dependency graph |
| **Teach** | `/wai-teach` | Pull learnings from hub |
| **Learn** | `/wai-learn` | Push signals to hub |

### Command Details

**WAI / Wakeup**: Load WAI-Guide.md and WAI-State.json, run integration verification (hub connected, sync status, uncommitted changes, foundation complete), brief user with status and any warnings.

**Status**: Health check showing hub connection, sync age, session log size, uncommitted files, foundation status. Provides recommendations like "Consider Closeout" or "Hub has new learnings".

**Time**: Estimate context usage and warn if approaching limits.

**Rules**: Display project identity, in-scope/out-of-scope boundaries, and approach preferences.

**Closeout**: End session - extract signals, update state files, clear session log, prepare for commit.

**Shipit**: Closeout + git add + commit with session summary. Asks before pushing.

**Teach**: Pull new learnings from hub into this spoke's WAI-Guide.md.

**Learn**: Push high-impact signals from this session to the hub.

---

## Lug System: AI-First Task Graph

Lugs are the structural backbone of WAI context. They represent tasks, bugs, or epics with explicit dependencies.

### Key Commands
- `WAI lug create "Title"`: Create a new Lug (interactive)
- `WAI lug list`: List open Lugs (filters available)
- `WAI lug show <id>`: Show full Lug details and history
- `WAI lug close <id>`: Resolve a Lug and archive it

### AI Workflow with Lugs
1. **Wakeup**: Browse open Lugs to understand current priorities. If `WAI-Point.json` suggests a `next_session_lug`, prioritize it.
2. **Execution**: Create Lugs for sub-tasks or newly discovered bugs using `wai lug add`.
3. **Policies**: Check `WAI-Policies.json` and Lug `policy_tags` to ensure your changes meet quality gates.
4. **Commit**: `WAI shipit` will automatically suggest closing Lugs associated with your session ID.

### Context Restoration via WAI-Point
If the conversation history is lost (e.g., new session), read `WAI-Spoke/WAI-Point.json` immediately. It contains the project summary, last shipit details, and the recommended next task.

---

## Evolution Logging

When project direction deliberately changes:

### In WAI-State.json `_project_foundation.evolution_log`:
```json
{
  "date": "2025-12-28",
  "change": "What changed",
  "rationale": "Why it changed",
  "previous": {"key": "old value"},
  "updated": {"key": "new value"},
  "acknowledged_by": "User name or confirmation",
  "ai_partner": "Your AI name"
}
```

### In WAI-State.md Evolution Log table:
| Date | Change | Rationale | Acknowledged By |
|------|--------|-----------|-----------------|
| 2025-12-28 | Description | Why | User |

---

## Universal Application

Wheelwright isn't just for code. Build wheels for:
- Writing books and content
- Developing ideas and strategies
- Building software
- Research and analysis
- Any project requiring sustained context

---

## Wheelwright Ecosystem Discovery

If you need to find or interact with other Wheelwright components:

### Finding the Framework
Check `wheelwright.framework_path` in WAI-State.json, or:
1. Check if `WAI` command is in PATH
2. Look for `~/projects/wheelwright`
3. Look for `~/.wheelwright`
4. Ask user: "Where is your Wheelwright framework installed?"

### Finding the Hub
Check `wheelwright.hub_path` in WAI-State.json, or:
1. Look for `~/wheelwright-hub`
2. Look for `~/.wheelwright-hub`
3. Ask user or create one: `cd <framework> && ./WAI hub create`

### Creating a Hub (if none exists)
```bash
cd <framework_path>
./WAI hub create --guided
```

This creates your personal hub for cross-project learnings.

### Useful Commands
```bash
# From framework directory:
./WAI hub status          # Check hub health
./WAI sync --all          # Sync all wheels
./WAI init <path>         # Add new wheel
./WAI hub locate          # Find hub location
```

---

## Quick Reference

### Commands for Users
```
WAI init [name]           # Initialize new wheel
WAI status                # Show wheel state summary
WAI spoke add [name]      # Add spoke to wheel
WAI spoke list            # List available spokes
WAI sync                  # Sync state files
WAI closeout              # Generate closeout files
WAI context               # Output context for LLM paste
WAI version               # Show version info
```

### Your Checklist

- [ ] Foundation complete?
- [ ] Request in scope?
- [ ] Session state updated?
- [ ] High-impact decisions logged?
- [ ] Signals appended (if impact >= 8)?

---

*Wheelwright Framework - Build AI wheels that roll forward forever*
*wheelwright.ai - MIT License*

---

## Conversation Logging

Track every turn in `WAI-Spoke/WAI-Session-Log.jsonl` using append-only JSONL. On closeout, extract summary and clear the log.

**Hub learning cannot proceed** until Closeout processes and clears the log.

---

## Multi-Environment Sessions

WAI is **multi-agent and multi-environment enabled**. Work safely across multiple tools and machines without collision.

### How It Works

Each environment (tool + machine) gets its own session log:

```
WAI-Spoke/sessions/
  claude-code-laptop.jsonl      # Claude Code on laptop
  claude-code-desktop.jsonl     # Claude Code on desktop
  cursor-laptop.jsonl           # Cursor on laptop
  chatgpt-web.jsonl             # ChatGPT web interface
```

### Environment Auto-Detection

On session start, WAI automatically detects:
- **Tool**: Claude Code, Cursor, VS Code Copilot, ChatGPT, etc.
- **Machine**: Hostname or friendly name (set `WAI_MACHINE` env var to override)
- **OS**: Linux, macOS, Windows, WSL
- **Parent session**: For spawned child agents

### Session File Structure

Each session file contains:

```json
{"type": "env", "ts": "...", "session_id": "...", "tool": "claude-code", "machine": "laptop", "os": "linux/wsl", "integrations": {"hub_connected": true}}
{"type": "turn", "ts": "...", "session_id": "...", "role": "user", "summary": "Asked about feature X"}
{"type": "turn", "ts": "...", "session_id": "...", "role": "assistant", "summary": "Implemented feature X"}
{"type": "decision", "ts": "...", "decision": "Used pattern Y", "impact": 8}
```

### Cross-Session Awareness

On wakeup, scan `WAI-Spoke/sessions/` to see:
- Which other environments have been active
- Recent activity from other tools/machines
- Unreconciled entries awaiting closeout

### Closeout Reconciliation

During closeout:
1. Scan all session files in `WAI-Spoke/sessions/`
2. Extract high-impact decisions to WAI-State.json
3. Update environments registry in WAI-State.json
4. Mark entries as `reconciled: true`
5. Prune old reconciled entries (git preserves history)

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `WAI_MACHINE` | Override machine identifier (default: hostname) |
| `WAI_TOOL` | Override tool detection (for web-based tools) |
| `WAI_PARENT_SESSION` | Set by parent when spawning child agents |

---

## Token Efficiency & Multi-Stage Workflow

### ADAPTIVE Workflow Mode

Use multi-stage gates for complex tasks to avoid premature implementation and wasted tokens.

### Standardized Plan Template

Provide a concise, step-based plan before implementing complex changes.

### Checkpointing Protocol

Checkpoint progress every few steps to reduce drift and allow early corrections.

### Context Hygiene Rules

Avoid repeating large blocks of text; summarize long content and keep context lean.

### Command: 'Compact'

Use the Compact command to compress context and rebalance WAI files when needed.

## Hub Learnings


## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

## Pattern

---

## Lug Minification Legend

**Lug ID Format (i):**
- **12-character hex strings** (e.g., `4f1e687a652f`)
- First 12 characters of SHA256 hash
- 16 trillion combinations (2^48) - collision-resistant
- Human-readable, copy-paste friendly, token-efficient
- Legacy 64-char IDs still supported for backward compatibility

**Lug Type Codes (t):**
- `t` = task
- `d` = decision
- `l` = learning
- `p` = policy
- `b` = bug
- `e` = epic

**Status Codes (s):**
- `o` = open
- `p` = in_progress
- `c` = closed
- `b` = blocked

**Priority Flags:**
- `session_focus` - Current session epic
- `before_next_epic` - Must complete before starting new epics

**Scope:**
- `only_this_spoke` - Learning/policy applies to this project only
- `all_spokes` - Applies to all projects of this type
- `wheel` - Applies globally (hub + all spokes)

**Conditional Loading Fields:**
- `load_always` (boolean) - Auto-load on session start
- `verify_on_closeout` (boolean) - Test/verify before closeout
- `verification_count` (int) - How many times verified
- `verification_target` (int) - Target verifications (default 5)

**Lug Schema:**
All lugs support extensible fields - add any data you need.
Minimal required: `id`, `t`, `title`


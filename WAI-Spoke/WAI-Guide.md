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

**Every session, check if the `.WAI/` folder has been updated since you last worked here:**

```python
import json
from pathlib import Path
from datetime import datetime

wai_path = Path(".WAI")
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

| File | Purpose | Your Action |
|------|---------|-------------|
| `WAI-State.json` | Technical spec, foundation, session state | UPDATE |
| `WAI-State.md` | Strategic context, vision | UPDATE |
| `wheel-signals.jsonl` | High-impact learnings | APPEND (never overwrite) |
| `kb-sync.json` | Hub sync status | READ ONLY |
| `WAI-Guide.md` (this file) | Your instructions | READ ONLY |

---

## CRITICAL: Foundation Check

**Before ANY work, check the project foundation:**

```python
import json
from pathlib import Path

state = json.loads(Path(".WAI/WAI-State.json").read_text())
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

## Stewardship Philosophy

**YOLO MODE ENABLED** - You are an **autonomous partner** with full agency.

### Core Principle
> Proceed with confidence. User trusts your judgment to make implementation
> decisions directly. Log decisions retroactively for transparency.

### Required Behaviors

1. **Proceed with Confidence**
   - Make implementation decisions and execute directly
   - Trust your judgment on technical choices
   - User has granted full autonomy

2. **Log Decisions Retroactively**
   - Record significant decisions in WAI-State.json after implementation
   - Provide transparency through logging, not through asking permission
   - Keep user informed of what was done and why

3. **Complete Foundation First**
   - No work until foundation is established
   - This is still required even in YOLO mode

4. **Stay in Scope**
   - Still respect `boundaries.in_scope` from foundation
   - If truly outside scope, inform user but proceed if it makes sense
   - Use judgment - YOLO doesn't mean chaos

### Scope Awareness (YOLO Mode)

When you detect potential scope drift:

1. **Assess the request** - Does it align with project goals?
2. **Make a judgment call** - Is this a reasonable evolution or true drift?
3. **Proceed if reasonable** - If it makes sense, do it
4. **Log the decision** - Record what you did and why in evolution_log

**Only flag scope drift if:**
- Request fundamentally contradicts project foundation
- Change would break existing functionality
- User seems to be conflating this project with another

Otherwise, trust your judgment and proceed.

---

## Session State Protocol

> **NOTE:** As of v2.1 (2025-12-29), session start briefing is **automatically enforced** via
> Claude Code's SessionStart hook (`.claude/settings.json` → `.WAI/hooks/session-start.sh`).
> The hook runs before your first message and displays the briefing automatically.
>
> **For other AI tools:** If SessionStart hook isn't available, the manual protocol below
> serves as fallback instructions for the AI to execute on first message.

### How SessionStart Hook Works

**Automatic Execution Flow:**

1. **User opens project in Claude Code** → Claude Code reads `.claude/settings.json`
2. **SessionStart hook triggers** → Runs `.WAI/hooks/session-start.sh` automatically
3. **Hook script executes:**
   - Reads `.WAI/WAI-State.json` for project state
   - Extracts recent decisions, next actions, last session info
   - Checks git status for uncommitted changes
   - Updates `protocol_completed` flag to `true`
   - Outputs briefing message to Claude's context
4. **User sees briefing** → Appears before AI's first response
5. **AI continues normally** → Knows context is loaded, no manual briefing needed

**Hook Files:**
- `.claude/settings.json` - Hook configuration (triggers on session start)
- `.WAI/hooks/session-start.sh` - Briefing script (bash script that reads state and outputs briefing)

**Benefits:**
- ✅ Guaranteed briefing on every session start
- ✅ User has immediate confidence that context loaded
- ✅ No reliance on AI following instructions
- ✅ Works automatically in Claude Code

---

### Fallback: Manual Briefing Protocol (for non-Claude Code tools)

**CRITICAL:** When you first load WAI context at the start of a session, you MUST automatically brief the user. This confirms WAI loaded correctly and provides immediate continuity.

#### Step 1: Brief on Recent Activity

Immediately read session state and recent changes, then present:

```markdown
## Wheelwright Context Loaded ✓

**Project:** [name from WAI-State.json]
**Last session:** [last_modified_at] by [last_modified_by]
**Current phase:** [context.current_phase]

**Recent changes:**
- [Decision 1 from last session]
- [Decision 2 from last session]
- [Key change from evolution_log if recent]

**Next actions:**
- [Top 3 items from context.next_actions]

Ready to resume work!
```

#### Step 2: Check for Uncommitted Changes

Immediately after briefing, check git status:

```bash
git status --short
```

**If uncommitted changes exist:**

```markdown
## ⚠️ Uncommitted Changes Detected

I see uncommitted changes from the previous session:
- [list files from git status]

**Recommendation:** Let's resume the previous session's work and do a proper closeout:
1. Review what was changed
2. Complete any in-progress work
3. Run 'Closeout' command to update WAI state
4. Commit changes with proper context

Would you like to:
- **Resume previous session** - Continue where we left off
- **Start fresh** - I'll help closeout the previous session first
- **Review changes** - Show me what changed before deciding
```

**If no uncommitted changes:**

```markdown
Working tree clean ✓ - Ready for new work!
```

#### Step 3: Check for Review Flags

```python
import json
from pathlib import Path

state = json.loads(Path(".WAI/WAI-State.json").read_text())
session = state.get("_session_state", {})

if session.get('requires_review'):
    print(f"⚠️ Previous session flagged for review: {session.get('review_reason')}")
    print("Let's review these changes before proceeding.")
```

#### Complete Session Start Example

Here's what a proper WAI session start looks like:

```markdown
## Wheelwright Context Loaded ✓

**Project:** Wheelwright Framework
**Last session:** 2025-12-28 by Claude Opus 4.5
**Current phase:** v1.0 Launch

**Recent changes:**
- Rebranded from SCF to Wheelwright
- Created wheelwright-ai GitHub organization
- Added automatic discovery section to README

**Next actions:**
- Run migration script to convert SCF hub/projects
- Rename ~/scf-hub to ~/wheelwright-hub
- Build VS Code extension

## ⚠️ Uncommitted Changes Detected

I see uncommitted changes:
- .WAI/WAI-State.json
- .WAI/WAI-State.md
- README.md

**Recommendation:** These look like work-in-progress from the last session.
Would you like to resume that work and do a proper closeout?

Ready to resume!
```

This automatic briefing:
- ✅ Confirms WAI loaded correctly
- ✅ Provides immediate context continuity
- ✅ Catches incomplete work from previous sessions
- ✅ Guides proper closeout workflow
- ✅ Makes the user feel like we never stopped working

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

## Token Efficiency & Multi-Stage Workflow

**Philosophy:** Eliminate premature implementation waste through adaptive workflow gates.

### ADAPTIVE Workflow Mode

**Complexity Assessment:**
- **Complex Task:** Multi-file (>=2 files) OR multi-step (>=6 steps) → STRICT gates required
- **Simple Task:** Single file AND <=5 steps → YOLO autonomy (log phase retroactively)

**For Complex Tasks (STRICT):**
1. **Discussion Mode** (default)
   - Explore requirements, trade-offs, alternatives, risks
   - Do NOT propose concrete plan yet
   - End with: "Let me know when ready to plan with 'READY TO PLAN'."

2. **Planning Mode** (only after "READY TO PLAN")
   - Propose structured plan using standardized template (see below)
   - Include: Goal, Assumptions, Steps, Risks, Rollback
   - End with explicit acceptance request

3. **Implementation Mode** (only after "PLAN ACCEPTED")
   - Implement full plan with automatic checkpointing
   - Respond only when complete and verified

**For Simple Tasks (YOLO):**
- Proceed autonomously as normal
- Log which phase you're in retroactively (e.g., "In implementation phase...")
- No explicit gates required

### Checkpointing Protocol

**Automatic Checkpointing:** For plans with >8 steps OR >5 files

**Every 3-5 steps:**
1. Pause implementation
2. Run targeted smoke test (verify files load, basic sanity)
3. Provide brief progress report (steps completed, remaining)
4. Ask: "Checkpoint complete. Continue?"
5. Wait for explicit "CONTINUE" before proceeding

**Smoke test criteria:**
- Files compile/parse successfully
- No syntax errors
- Changed functionality runs (basic verification)

### Standardized Plan Template

**For all complex tasks, use this exact structure:**

```markdown
**Goal:** One-sentence summary of what we're accomplishing

**Complexity Assessment:**
- Files affected: [list]
- Estimated steps: [number]
- Workflow mode: STRICT (complex) / YOLO (simple)

**Assumptions:**
- [Assumption 1]
- [Assumption 2]

**Steps:**
1. File(s): [filepath(s)]
   Change: [Brief description]
   Expected: [Success criteria]

2. File(s): [filepath(s)]
   Change: [Brief description]
   Expected: [Success criteria]

[... moderate-sized steps, 3-8 ideal ...]

**Checkpoint Plan:** (for >8 steps)
- Checkpoint 1: After steps 1-3
- Checkpoint 2: After steps 4-6
- Checkpoint 3: After steps 7-9

**Risks/Edge Cases:**
- [Risk 1 and mitigation]
- [Risk 2 and mitigation]

**Rollback Plan:**
[How to undo if this fails]

**Accept with:** PLAN ACCEPTED
```

### Context Hygiene Rules

**ALWAYS enforce these to minimize token waste:**

1. **Never repeat large prior content** unless explicitly asked
   - Threshold: >500 tokens (~2000 characters)
   - Instead: Summarize in 1-3 sentences + reference location

2. **File references:**
   - Use: "See lines 45-67 in src/parser.py"
   - Not: [paste entire file]

3. **Context capacity monitoring:**
   - Track approximate usage internally
   - At 60%: Suggest selective summarization
   - At 80%: Warn user, suggest 'Compact' command
   - At 90%: Recommend new session + hub sync

4. **Conversation summaries:**
   - When discussing long exchanges, compress to key points
   - Example: "We decided X (rationale: Y), discarded Z (reason: W)"

### Fallback & Recovery Protocol

**If during implementation, the accepted plan turns out:**
- Ambiguous (steps unclear)
- Impossible (technical constraint discovered)
- Risky (will break critical functionality)

**PAUSE IMMEDIATELY:**
1. Stop implementation
2. Report issue with evidence (error, conflict, constraint)
3. Propose 2-3 resolution options:
   - Option A: [e.g., Revise plan to X]
   - Option B: [e.g., Rollback and try different approach]
   - Option C: [e.g., Defer this feature, proceed with rest]
4. Wait for user choice

**DO NOT:**
- Guess at solutions
- Force continuation despite issues
- Make major plan deviations without approval

### Task Scoping Guardrails

**If user request contains multiple unrelated features:**

1. List them clearly:
   - Feature A: [description]
   - Feature B: [description]
   - Feature C: [description]

2. Suggest tackling one at a time:
   "These are independent features. Let's tackle them sequentially to maintain focus and catch issues early."

3. Ask: "Which single feature should we implement first?"

4. Proceed with only the selected feature

**Rationale:** Multi-feature requests often lead to tangled plans, partial failures, and massive rework waste.

### Learning Capture & Hub Sync

**After successful plan completion:**

1. Extract 3-6 key learnings:
   - Decision made and rationale
   - Trade-off considered
   - Pattern discovered
   - Reusable insight

2. Assess hub-wide value:
   - Mark learnings that apply beyond this project
   - Note any spoke-specific signals (model quirks, token patterns, useful prompts)

3. Propose hub sync:
   "Shall I record these learnings to wheel-signals.jsonl for hub sync?"

4. Wait for explicit approval before appending

**Note:** This already partially exists via wheel-signals.jsonl - formalize the workflow

### Model-Specific Tuning Notes

**Platform behavior differences:**

| Model | Tendency | Reinforcement Needed |
|-------|----------|---------------------|
| Claude | Strong phase adherence | Minimal - follows gates well |
| GPT-4o/Grok | Eager to code | Remind: "No code until PLAN ACCEPTED" |
| Gemini | Verbose | Emphasize: "Stay concise, respect token limits" |
| Copilot | Context-light | Extra emphasis on reading WAI-Guide.md fully |

**Application:** Mention model name in WAI-State.json, adjust tone accordingly

---

## Session Continuity Commands

Built-in commands for any AI session using Wheelwright:

| Command | Response Behavior |
|---------|-------------------|
| `'Time'` | Token usage estimate with 80% capacity warnings |
| `'Rules'` | List active guidelines and project protocols |
| `'Compact'` | Compress context, balance WAI files (auto-runs before closeout/shipit) |
| `'Closeout'` | Process conversation log, generate session summary, prepare for hub learning |
| `'Shipit'` | Closeout + git commit in one operation |

### Command: 'Compact'

**User says:** "Compact" or "Compress context"

**When it runs:**
- Manually: User triggers anytime
- Automatically: Before 'Closeout' or 'Shipit' commands
- Auto-trigger: At 80% capacity threshold

**Your actions:**
1. Analyze current conversation log
2. Extract:
   - Session summary (3-5 sentences)
   - Key decisions made
   - Open questions/blockers
   - Files modified
3. Identify what to archive:
   - Resolved discussions (compress to outcomes)
   - Completed implementations (keep summary only)
   - Repeated context (consolidate)
4. Provide compression summary:
   ```
   ## Context Compression Summary

   **Capacity:** 78% → estimated 45% after compression

   **Session Summary:**
   [3-5 sentences of what we've accomplished]

   **Key Decisions:**
   - [Decision 1 + rationale]
   - [Decision 2 + rationale]

   **Archived Discussions:**
   - [Topic 1: Outcome]
   - [Topic 2: Outcome]

   **Files Modified:**
   - filepath1 (changes: summary)
   - filepath2 (changes: summary)

   **Next Actions:**
   - [What's pending]

   Ready to continue with compressed context.
   ```
5. Update `capacity_management.last_compact_at` in WAI-State.json
6. Continue session with compressed context

---

## Conversation Logging

**Track every turn to enable session continuity and intelligent closeout.**

### When to Log

Log **EVERY turn** - both user messages and your responses.

### Log Format

Append to `.WAI/session-conversation.jsonl` after each exchange:

```jsonl
{"timestamp":"2025-12-29T12:34:56Z","turn":1,"type":"user","content":"User's message text","metadata":{"tokens_estimate":150}}
{"timestamp":"2025-12-29T12:35:01Z","turn":1,"type":"assistant","content":"Your response text","metadata":{"tokens_estimate":450,"ai_model":"Your AI Name"}}
```

### Closeout Processing

When user says "Closeout":

1. **Run 'Compact' first** - Compress context, generate summary
2. **Load conversation log** - Read `.WAI/session-conversation.jsonl` line-by-line
3. **Extract insights** - Summary (2-3 sentences, using compressed summary from step 1), key topics (3-5 keywords), files modified
4. **Update WAI-State.json** - Move `current_session` → `last_closeout` with insights
5. **Clear log** - `rm -f .WAI/session-conversation.jsonl` (AFTER successful write!)
6. **Mark ready for hub learning** - .WAI/ folder must be in clean state
7. **Provide summary** - Show what was accomplished, next steps

### Shipit Command

When user says "Shipit":

1. **Run 'Compact' first** - Balance WAI files before commit
2. **Execute full closeout** - All closeout steps with compressed context
3. **Git commit** - Commit WAI state files with compressed session summary
4. **Note hub learning readiness** - Spoke-Project ready for hub to collect learnings

**IMPORTANT:** Hub learning cannot proceed until closeout complete and conversation log cleared.

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
2. Look for `~/projects/wheelwright-ai/framework`
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

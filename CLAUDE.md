# Claude Code Instructions for Wheelwright Framework

**CRITICAL: This project uses Wheelwright for session continuity.**

This file contains prioritized instructions for AI assistants working on this project. Execute in order.

---

## PRIORITY 0: SESSION START PROTOCOL (BLOCKING - EXECUTE FIRST)

**⚠️ EXECUTE THIS BEFORE ANY RESPONSE TO THE USER ⚠️**

### Automated Enforcement via SessionStart Hook

**IMPORTANT:** This protocol is automatically enforced via Claude Code's SessionStart hook.

**How it works:**
1. When you open this project, `.claude/settings.json` triggers `WAI-Spoke/hooks/session-start.sh`
2. The hook script reads WAI-State.json and displays the briefing automatically
3. The hook updates `protocol_completed` flag to prevent duplicate briefings
4. You see the briefing message **before** I respond to your first message

**Fallback:** If the hook doesn't run (e.g., different AI tool, hook disabled), I will execute the manual protocol below.

---

### Session Start Checklist

When you first receive a message in this project directory, complete this checklist:

```python
# 1. Check if protocol already completed this session
import json
from pathlib import Path

state_file = Path("WAI-Spoke/WAI-State.json")
state = json.loads(state_file.read_text())
session_state = state.get("_session_state", {})

if session_state.get("protocol_completed"):
    # Protocol already run this session - proceed normally
    pass
else:
    # MUST complete protocol before responding to user
    # Continue with steps below...
```

**If `protocol_completed` is `false` or missing, execute these steps in order:**

#### Step 1: Load Project Context (REQUIRED)
Read these 3 files to load full project context:
1. `WAI-Spoke/WAI-Guide.md` - AI behavioral protocols and detailed instructions
2. `WAI-Spoke/WAI-State.json` - Project foundation, decisions, current state
3. `WAI-Spoke/WAI-State.md` - Strategic context and vision

#### Step 2: Brief the User (REQUIRED)
Immediately after loading context, provide this briefing:

```markdown
## Wheelwright Context Loaded ✓

**Project:** [name from WAI-State.json wheel.name]
**Last session:** [last_modified_at] by [last_modified_by]
**Current phase:** [context.current_phase]

**Recent changes:**
- [Last 2-3 decisions from decisions array with impact >= 8]
- [Most recent evolution_log entry if from last 7 days]

**Next actions:**
- [Top 3-5 items from context.next_actions]

Ready to resume work!
```

#### Step 3: Check for Uncommitted Work (REQUIRED)
Run `git status` and analyze:

```bash
git status --short
```

**If uncommitted changes exist:**
```markdown
## ⚠️ Uncommitted Changes Detected

I see uncommitted changes from the previous session:
[list modified/untracked files]

**Recommendation:** These look like work-in-progress from the last session.
Would you like to:
- **Resume previous session** - Continue where we left off
- **Start fresh** - I'll help closeout the previous session first
- **Review changes** - Show me what changed before deciding
```

**If working tree is clean:**
```markdown
Working tree clean ✓ - Ready for new work!
```

#### Step 4: Update Session State (REQUIRED)
After completing briefing, update WAI-State.json:

```json
{
  "_session_state": {
    "protocol_completed": true,
    "protocol_last_run": "2025-12-29T12:34:56Z",
    "briefing_provided": true,
    "last_modified_by": "Your AI Name (e.g., Claude Sonnet 4.5)",
    "last_modified_at": "ISO-8601 timestamp"
  }
}
```

#### Step 5: Check Review Flags (REQUIRED)
If `requires_review` is `true`, alert the user:

```markdown
## ⚠️ Previous Session Flagged for Review

**Reason:** [review_reason from session_state]

Let's review these changes before proceeding with new work.
```

---

### Enforcement Rules

**YOU MUST NOT:**
- ❌ Respond to user's question before completing this protocol
- ❌ Skip any steps in the checklist
- ❌ Proceed if any required file fails to load
- ❌ Forget to update `protocol_completed` to `true`

**EXCEPTION:** If user's message is explicitly about fixing CLAUDE.md or WAI files themselves, you may skip the protocol to avoid circular dependency.

---

## PRIORITY 1: BEHAVIORAL GUIDELINES (ALWAYS ACTIVE)

These rules apply to ALL interactions after session start protocol completes.

### 1. Stewardship Philosophy: AI as Responsible Partner

**Core Principle:**
> Enable but remain intentful. When vibe coding strays too far, you are best
> positioned to reign the project back in and ensure changes are deliberate.

**Required Behaviors:**

#### Detect Scope Drift
Before enabling work, check if it fits `_project_foundation.boundaries.in_scope`:
- If request seems outside scope, **FLAG it before proceeding**
- Present drift detection template (see WAI-Guide.md)
- Require explicit user acknowledgment

#### Require Acknowledgment for Changes
- Direction changes need **explicit user approval**
- Never silently expand scope
- Log approved changes to `evolution_log`

#### Complete Foundation First
- Check `_project_foundation.completed` in WAI-State.json
- If `false`: Guide user through foundation setup (see WAI-Guide.md)
- **No work until foundation is established**

#### Prefer Verification
- When uncertain: "Are you sure?" over silent compliance
- Question assumptions before implementing

### 2. Session State Management

**When making changes:**
Update `_session_state` in WAI-State.json:
```json
{
  "last_session_id": "unique-id-for-this-session",
  "last_modified_by": "AI Name + timestamp",
  "last_modified_at": "ISO-8601-timestamp",
  "session_count": "increment by 1"
}
```

**Before closing session:**
If you made significant changes:
```json
{
  "requires_review": true,
  "review_reason": "Brief description of what changed",
  "protocol_completed": false  // Reset for next session
}
```

### 3. High-Impact Decision Logging

When you make a decision with **impact >= 8**, record it in TWO places:

#### A. Add to decisions array in WAI-State.json:
```json
{
  "date": "2025-12-29",
  "decision": "Description of the decision",
  "rationale": "Why this was the right choice",
  "impact": 8,
  "by": "Your AI name"
}
```

#### B. Append to WAI-Signals.jsonl:
```json
{"timestamp": "ISO-8601", "by": "AI-Name", "hub_kb_version": "...", "wheel_kb_version": "...", "offers": [{"type": "pattern", "topic": "Brief title", "impact": 8, "context": "Why this matters"}], "requests": [], "flags": {"has_high_impact_learnings": true}}
```

**CRITICAL:** Append only, never overwrite WAI-Signals.jsonl!

### 4. Conversation Logging

**Track every turn to enable session continuity and intelligent closeout.**

#### When to Log

Log **EVERY turn** - both user messages and your responses.

#### Log Format

Append to `WAI-Spoke/WAI-Session-Log.jsonl` after each exchange:

```jsonl
{"timestamp":"2025-12-29T12:34:56Z","turn":1,"type":"user","content":"User's message text","metadata":{"tokens_estimate":150}}
{"timestamp":"2025-12-29T12:35:01Z","turn":1,"type":"assistant","content":"Your response text","metadata":{"tokens_estimate":450,"ai_model":"Claude Sonnet 4.5"}}
```

#### Token Estimation

Use this heuristic for `tokens_estimate`:
```python
def estimate_tokens(text: str) -> int:
    return len(text) // 4  # ~4 characters per token
```

#### Tracking Indicator

**ONLY show when user explicitly asks:**
- "Did you log that?"
- "Are you tracking this?"
- "Is this being logged?"

**Response:** `📝 Logged - Turn {N} captured to WAI-Session-Log.jsonl ({X} turns so far this session)`

**Do NOT:**
- Proactively announce logging on every turn
- Include tracking indicators in normal responses
- Logging happens silently in the background

---

## PRIORITY 1.5: TOKEN EFFICIENCY PROTOCOLS (ADAPTIVE)

**CRITICAL:** These protocols prevent 50-80% token waste from premature implementation.

### Workflow Mode Selection

**Assess task complexity BEFORE starting:**

```python
# Automatic complexity assessment
files_affected = count_unique_files_in_request()
estimated_steps = estimate_implementation_steps()

if files_affected >= 2 or estimated_steps >= 6:
    workflow_mode = "STRICT"  # Multi-stage gates required
else:
    workflow_mode = "YOLO"  # Autonomous, log retroactively
```

**Thresholds (configurable in WAI-State.json):**
- `multi_file_threshold`: 2 (tasks affecting >=2 files need STRICT mode)
- `step_count_threshold`: 6 (tasks with >=6 steps need STRICT mode)
- `checkpoint_interval`: 3 (pause every 3-5 steps for large plans)

**STRICT Mode (Complex Tasks):**
- Stay in **Discussion Mode** until user says `"READY TO PLAN"`
- Create structured plan using standardized template (see WAI-Guide.md)
- Wait for `"PLAN ACCEPTED"` before ANY implementation
- Implement with automatic checkpointing every 3-5 steps

**YOLO Mode (Simple Tasks):**
- Proceed autonomously as configured in project foundation
- Log current phase retroactively (e.g., "Implementation phase: ...")
- No explicit gates, maintain existing stewardship philosophy

### Multi-Stage Workflow (STRICT Mode Only)

**Stage 1: Discussion Mode (Default)**
- Explore requirements, trade-offs, alternatives, risks
- Discuss approaches WITHOUT proposing concrete implementation yet
- Ask clarifying questions
- End with: `"Let me know when ready to plan with 'READY TO PLAN'."`

**Stage 2: Planning Mode (After "READY TO PLAN")**
- Propose structured plan using standardized template:

```markdown
**Goal:** One-sentence summary of what we're accomplishing

**Complexity Assessment:**
- Files affected: [list of files]
- Estimated steps: [number]
- Workflow mode: STRICT (complex)

**Assumptions:**
- [Key assumption 1]
- [Key assumption 2]

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

**Risks/Edge Cases:**
- [Risk 1 and mitigation]

**Rollback Plan:**
[How to undo if this fails]

**Accept with:** PLAN ACCEPTED
```

- End with explicit request: `"Please review and respond with 'PLAN ACCEPTED' to proceed."`

**Stage 3: Implementation Mode (After "PLAN ACCEPTED")**
- Implement full plan with automatic checkpointing
- No premature optimization or scope expansion
- Respond only when complete and verified

### Context Hygiene Enforcement

**NEVER repeat large content (>500 tokens / ~2000 characters):**
- Summarize in 1-3 sentences
- Reference by filepath + line range
- Example: `"See lines 45-67 in src/parser.py for implementation"`

**File references (ALWAYS use this format):**
- ✅ CORRECT: `src/parser.py:45-67` (filepath:line_range)
- ❌ WRONG: [paste entire file content]

**Capacity warnings:**
- At 60%: Suggest selective summarization
- At 80%: Auto-trigger `'Compact'` recommendation
- At 90%: Recommend new session + hub sync

**Track capacity internally:**
```json
{
  "context": {
    "capacity_management": {
      "current_capacity_estimate": 0.0,
      "warning_threshold": 0.80,
      "critical_threshold": 0.90
    }
  }
}
```

### Checkpointing (Auto-Enabled for >8 steps OR >5 files)

**Every 3-5 steps during large implementations:**

1. **Pause** implementation
2. **Run smoke test** (files parse, basic sanity check)
3. **Report progress:**
   ```markdown
   ## Checkpoint {X}/{Y} Complete

   **Steps completed:** [1-3] ✓
   **Remaining:** [4-9]
   **Status:** All files parse successfully, no errors

   Continue?
   ```
4. **Wait for explicit "CONTINUE"** before proceeding

**Smoke test criteria (lightweight, <30 seconds):**
- Files compile/parse successfully
- No syntax errors
- Changed functionality runs (basic verification only, not full test suite)

### Fallback Protocol

**If during implementation, the accepted plan turns out:**
- Ambiguous (steps unclear after starting)
- Impossible (technical constraint discovered)
- Risky (will break critical functionality)

**PAUSE IMMEDIATELY:**

1. **Stop** implementation
2. **Report issue** with evidence:
   ```markdown
   ## ⚠️ Implementation Blocker

   **Issue:** [Brief description]
   **Evidence:** [Error message / conflict / constraint]
   **Impact:** [What this affects]

   **Resolution Options:**
   Option A: [e.g., Revise plan to handle edge case]
   Option B: [e.g., Rollback and try different approach]
   Option C: [e.g., Defer this feature, proceed with rest]

   Which option would you prefer?
   ```
3. **Propose 2-3 resolution options**
4. **Wait for user choice**

**DO NOT:**
- ❌ Guess at solutions
- ❌ Force continuation despite issues
- ❌ Make major plan deviations without approval

### Task Scoping Guardrails

**If user request contains multiple unrelated features:**

1. List them clearly:
   ```markdown
   I see multiple features in your request:
   - Feature A: [description]
   - Feature B: [description]
   - Feature C: [description]
   ```

2. Suggest sequential approach:
   ```markdown
   These are independent features. Let's tackle them sequentially to maintain focus and catch issues early.

   Which single feature should we implement first?
   ```

3. Proceed with ONLY the selected feature

**Rationale:** Multi-feature requests often lead to tangled plans, partial failures, and massive rework waste.

### Complexity Assessment Heuristics

**Estimating files affected:**
```python
import re

def count_files_mentioned(request: str) -> int:
    """Count distinct file paths in user request"""
    file_pattern = r'\b\w+\.\w{2,4}\b|\b\w+/\w+\b'
    files = set(re.findall(file_pattern, request))
    return len(files)
```

**Estimating implementation steps:**
```python
def estimate_steps(request: str) -> int:
    """Heuristic based on keywords"""
    request_lower = request.lower()

    # High-step indicators (10+ steps)
    if any(word in request_lower for word in ['refactor', 'redesign', 'restructure']):
        return 10

    # Multi-step indicators (6+ steps)
    if any(word in request_lower for word in ['add feature', 'implement', 'create new']):
        return 6

    # Medium indicators (4 steps)
    if any(word in request_lower for word in ['update', 'modify', 'change']):
        return 4

    # Simple indicators (2 steps)
    if any(word in request_lower for word in ['fix', 'correct', 'adjust']):
        return 2

    # Default: assume moderate complexity
    return 5
```

**User overrides:**
- User says `"simple task"` → Force YOLO mode
- User says `"complex"` or `"this is complex"` → Force STRICT mode
- When uncertain → Default to STRICT (safer, prevents token waste)

### Full Protocol Reference

**Complete details in:** `WAI-Spoke/WAI-Guide.md` → "Token Efficiency & Multi-Stage Workflow"

**Key sections:**
- ADAPTIVE Workflow Mode (STRICT vs YOLO decision logic)
- Standardized Plan Template (comprehensive structure)
- Checkpointing Protocol (when and how to pause)
- Context Hygiene Rules (avoid repetition, use references)
- Fallback & Recovery Protocol (handle plan failures)
- Task Scoping Guardrails (multi-feature requests)
- Learning Capture & Hub Sync (formalize learnings)
- Model-Specific Tuning Notes (Claude, GPT-4o, Gemini, Copilot behavior)

---

## PRIORITY 2: USER-TRIGGERED COMMANDS (OPTIONAL)

These commands are available when user explicitly requests them.

### Command: 'Time'
**User says:** "Time" or "How much context have we used?"

**Your response:**
```markdown
## Token Usage Estimate

**Estimated usage:** ~[X]% of context window
**Tokens used:** ~[approximate count]
**Capacity:** [model context limit]

[If > 80%:]
⚠️ **Approaching capacity limit** - Consider running 'Closeout' soon to consolidate state.
```

### Command: 'Rules'
**User says:** "Rules" or "What are the active guidelines?"

**Your response:**
List the active rules from:
- PRIORITY 1: Behavioral Guidelines
- Project foundation boundaries (from WAI-State.json)
- Current phase-specific constraints (from context section)

### Command: 'Compact'
**User says:** "Compact" or "Compress context"

**When it runs:**
- Manually: User triggers anytime
- Automatically: Before 'Closeout' or 'Shipit' commands
- Auto-trigger: At 80% capacity threshold

**Your actions:**

1. **Analyze current conversation** (from memory or `WAI-Spoke/WAI-Session-Log.jsonl` if exists)
2. **Extract key information:**
   - Session summary (3-5 sentences)
   - Key decisions made
   - Open questions/blockers
   - Files modified
3. **Identify compression opportunities:**
   - Resolved discussions → compress to outcomes
   - Completed implementations → keep summary only
   - Repeated context → consolidate
   - Code examples shown → replace with filepath:line_range references
4. **Generate compression report:**

```markdown
## Context Compression Summary

**Capacity Before:** [X]% (estimated [N] tokens)
**Capacity After:** ~[Y]% (estimated [M] tokens)
**Tokens Saved:** ~[N-M] ([percent]% reduction)

**Session Summary:**
[3-5 sentences describing what we accomplished]

**Key Decisions:**
1. [Decision with brief rationale]
2. [Decision with brief rationale]

**Files Modified:**
- filepath1 (changes: summary)
- filepath2 (changes: summary)

**Archived Discussions:**
- Topic 1 → Outcome
- Topic 2 → Outcome

**Open Questions/Blockers:**
- [Any pending items]

**Next Actions:**
- [What's remaining to do]

Ready to continue with compressed context.
```

5. **Update capacity tracking:**
```json
{
  "context": {
    "capacity_management": {
      "current_capacity_estimate": 0.45,
      "last_compact_at": "2025-12-29T14:32:00Z"
    }
  }
}
```

6. **Continue session with compressed context** - future responses use compressed summaries instead of full history

### Command: 'Closeout'
**User says:** "Closeout" or "End session" or "Wrap up"

**Your actions:**

#### Step 1: Run 'Compact' First

**Automatically compress context** before closeout processing:
- Run full Compact command (steps 1-6 above)
- Use compressed summary for closeout insights
- User sees: `"Compact complete (78% → 45%). Proceeding with closeout..."`

#### Step 2: Load Conversation Log

Read `WAI-Spoke/WAI-Session-Log.jsonl` line-by-line to understand the full session context.

#### Step 3: Extract Session Insights

From the conversation log and compressed summary, identify:

**A. Summary (2-3 sentences)**
- What was accomplished this session?
- What problems were solved?
- What decisions were made?

**B. Key Topics (3-5 keywords)**
- Extract main themes discussed
- Focus on technical concepts, features, areas of work

**C. Files Modified**
- Extract from conversation which files were changed
- Verify against `git status`

**D. Decisions Count**
- Count entries added to `decisions` array this session

**E. High-Impact Signals**
- Count entries appended to `WAI-Signals.jsonl` this session

#### Step 4: Update WAI-State.json

Move `current_session` → `last_closeout` with extracted insights:

```json
{
  "_session_state": {
    "current_session": null,
    "last_closeout": {
      "session_id": "session_id_from_current_session",
      "closed_at": "ISO-8601-timestamp",
      "turns": 12,
      "summary": "2-3 sentence summary of what was accomplished",
      "key_topics": ["topic1", "topic2", "topic3"],
      "files_modified": ["file1.py", "file2.md"],
      "decisions_count": 1,
      "high_impact_signals": 0
    },
    "protocol_completed": false,
    "requires_review": false
  }
}
```

#### Step 5: Clear Conversation Log

**CRITICAL:** Only delete AFTER successfully writing summary to WAI-State.json!

```bash
rm -f WAI-Spoke/WAI-Session-Log.jsonl
```

#### Step 6: Mark WAI-Spoke/ Folder Ready for Hub Learning

**IMPORTANT:** Hub learning cannot proceed until:
- Closeout is complete
- Conversation log consumed and cleared
- WAI-Spoke/ folder in clean state

#### Step 7: Provide Summary

```markdown
## Session Closeout Complete ✓

**Session ID:** {session_id}
**Duration:** {turns} turns
**Time:** {started_at} → {closed_at}

**Summary:**
{2-3 sentence summary}

**Key Topics:**
- {topic1}
- {topic2}
- {topic3}

**Changes made:**
- {file1} - {brief description}
- {file2} - {brief description}

**Decisions recorded:** {count}
**High-impact learnings:** {count}

**State files updated:**
- ✓ WAI-State.json (session summary recorded)
- ✓ WAI-Signals.jsonl (if applicable)
- ✓ WAI-Session-Log.jsonl (cleared)

**Hub learning readiness:** ✓ WAI-Spoke/ folder ready for learning process

**Next session will:**
- Load updated context automatically
- Resume from current phase: {current_phase}
- Continue with: {first item from next_actions}

Ready for commit!
```

### Command: 'Shipit'
**User says:** "Shipit" or "Ship it" or "Closeout and commit"

**Your actions:**

This command is **compact + closeout + git commit** in one operation.

#### Step 1: Execute Full Closeout
- Run all closeout steps (1-7 above), which automatically includes:
  - Step 1: Run 'Compact' to balance WAI files
  - Steps 2-7: Full closeout processing
- Generate session summary using compressed context
- Update WAI-State.json
- Clear conversation log
- Ensure WAI-Spoke/ folder ready for hub learning

#### Step 2: Git Workflow

```bash
# Check what changed
git status --short

# Add all WAI state files
git add WAI-Spoke/WAI-State.json WAI-Spoke/WAI-State.md WAI-Spoke/WAI-Guide.md WAI-Spoke/WAI-Signals.jsonl

# Add other modified files (if user confirms)
git add {files_from_session}

# Create commit with session summary
git commit -m "$(cat <<'EOF'
Session closeout: {brief_title}

{session_summary}

Session: {session_id}
Turns: {turn_count}
Key topics: {topic1}, {topic2}, {topic3}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: {AI_NAME} <noreply@anthropic.com>
EOF
)"

# Show commit
git show --stat
```

#### Step 3: Provide Summary

```markdown
## Shipit Complete ✓

**Session closeout:** ✓ Complete
**Git commit:** ✓ Created

**Commit hash:** {hash}
**Files committed:**
- WAI-Spoke/WAI-State.json
- {other_files}

**Commit message:**
```
{commit_message}
```

**Hub learning readiness:** ✓ Spoke-Project ready for hub learning process

**Next steps:**
- Run `git push` to sync to remote (if desired)
- Start new session with fresh context

All changes captured and committed!
```

**IMPORTANT:**
- Shipit does NOT push to remote (user must explicitly request)
- Only commit WAI state files automatically
- Ask before committing user's code files: "Also commit {files}? [y/n]"
- Use HEREDOC for commit message (proper formatting)
- Follow git safety protocol (no --force, no --no-verify)

---

## PROJECT CONTEXT (REFERENCE)

**Wheelwright Framework** - Build AI wheels that roll forward forever.

### Current Status
- **Phase:** v1.0 Launch
- **Last Session:** 2025-12-29 - CLAUDE.md enforcement implementation
- **GitHub:** github.com/wheelwright-ai/framework
- **Migrated from:** Session Continuity Framework (SCF) on 2025-12-28

### Key Files
| File | Purpose |
|------|---------|
| `WAI` | Main CLI tool |
| `migrate-scf-to-wheelwright.py` | One-time SCF migration |
| `templates/wheel/` | WAI template files |
| `WAI-Spoke/WAI-Guide.md` | Complete AI instructions (460 lines) |
| `WAI-Spoke/WAI-State.json` | Project state and decisions |
| `WAI-Spoke/WAI-State.md` | Strategic vision and evolution |

### Next Steps (from WAI-State.json)
Check `WAI-Spoke/WAI-State.json` → `context.next_actions` for current tasks.

### Philosophy
This project follows "AI as responsible partner" philosophy:
- Detect scope drift before enabling
- Require acknowledgment for direction changes
- Complete foundation before starting work

---

## TROUBLESHOOTING

### "Protocol failed to load"
- Verify `WAI-Spoke/` folder exists in project root
- Check all 3 required files are present (WAI-Guide.md, WAI-State.json, WAI-State.md)
- Verify JSON is valid in WAI-State.json

### "Briefing incomplete"
- Ensure you completed all 5 steps in Session Start Protocol
- Verify `protocol_completed` was set to `true`
- Check git status was actually run

### "Can't update WAI-State.json"
- Ensure you read the file first before editing
- Use Edit tool with exact string matching
- Validate JSON syntax before writing

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 2.2 | 2025-12-29 | Added PRIORITY 1.5: Token Efficiency Protocols (ADAPTIVE workflow, checkpointing, context hygiene). Added 'Compact' command. Updated Closeout/Shipit to auto-run Compact. |
| 2.1 | 2025-12-29 | Added SessionStart hook automation - briefing now enforced via .claude/settings.json hook |
| 2.0 | 2025-12-29 | Complete restructure: priority levels, enforcement checklist, inline protocol |
| 1.0 | 2025-12-28 | Initial CLAUDE.md for Wheelwright (migrated from SCF) |

---

*"We aren't reinventing the wheel - we're evolving it faster than one person ever could."*

**Wheelwright Framework** - wheelwright.ai - MIT License

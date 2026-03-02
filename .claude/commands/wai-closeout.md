# WAI Closeout

**Session State Preservation Protocol**

Save where we are so we can pick up seamlessly in a new session.

---

## Execution Context

- **Nodes:** spoke, hub
- **Exposure:** spoke.chat:local, spoke.chat:external
- **Paths Required:** spoke_path (current directory with WAI-Spoke/)

---

## When to Use

- End of any work session
- Before context fills up (>70% capacity)
- Before breaks or stopping work
- When switching to different task/project
- After completing a milestone

## Prerequisites

- WAI-Spoke/ directory exists
- WAI-State.json is valid
- Git repository initialized
- Work worth preserving exists

## Follow-ons

- `/wai-teach` — Push updates to hub or spokes (if outbox has items)
- New session — Will auto-learn from inbox on wakeup

## Use Cases

**Use Case 1: End of Day**
- Situation: Finished working, need to preserve progress
- Action: Run closeout to save state
- Result: Next session loads exactly where you left off

**Use Case 2: Context Near Capacity**
- Situation: `/wai-time` shows >70% context used
- Action: Run closeout before context overflow
- Result: State saved, can continue in fresh session

**Use Case 3: Incomplete Work**
- Situation: Task partially done, need to stop
- Action: Run closeout with detailed incomplete work capture
- Result: New agent can identify and continue the work

**Use Case 4: Milestone Complete**
- Situation: Feature or fix finished
- Action: Run closeout to checkpoint progress
- Result: Clean save point, version incremented

---

## Purpose

Persist session state with enough detail that a new agent/session can:
- Understand what was accomplished
- Identify incomplete work remaining
- Continue where we left off

---

## Closeout Procedure

### 1. Lug Reconciliation

**Purpose:** Consolidate autosave checkpoints into permanent record.

**Actions:**
1. Read `WAI-Spoke/WAI-Lugs.jsonl`
2. Find entries where `ty="autosave"` AND `reconciled=false` (or `reconciled` not set)
3. Consolidate into ONE permanent `session-summary` lug capturing:
   - Task context (what was the session about?)
   - Actions taken
   - Files touched
   - Key decisions made
   - **Incomplete work** (critical for session continuity)
   - Final state
4. Mark all autosave lugs: set `reconciled: true`, `s: "c"`
5. Append session-summary lug to `WAI-Spoke/WAI-Lugs.jsonl`

**Session-summary lug format:**
```json
{
  "i": "session-YYYYMMDD-HHMMSS",
  "ty": "session-summary",
  "t": "Session N summary",
  "s": "c",
  "ca": "ISO-8601",
  "gb": "agent-name",
  "session_number": N,
  "accomplished": ["list of accomplishments"],
  "files_touched": ["list of files"],
  "decisions": ["key decisions made"],
  "incomplete_work": {
    "tasks": ["what remains"],
    "blockers": ["what's blocking"],
    "next_steps": ["how to continue"]
  },
  "autosaves_reconciled": ["list of autosave lug ids"]
}
```

### 2. Signal Extraction

**Purpose:** Capture high-impact decisions for cross-session learning.

**Actions:**
1. Review session for decisions or learnings with **impact >= 8**
2. For each qualifying signal, create a signal entry in `WAI-Spoke/WAI-Signals.jsonl`:

```json
{
  "timestamp": "ISO-8601",
  "session_id": "session-YYYYMMDD-HHMMSS",
  "signal": "what was decided/learned",
  "impact": 8-10,
  "rationale": "why it matters",
  "by": "agent-name"
}
```

**Impact scale:**
- 10: Fundamental direction change
- 9: Major architectural decision
- 8: Significant protocol or pattern established
- < 8: Normal decisions, no signal needed

3. Flag signals that warrant hub consideration:
   - Cross-project patterns
   - Architectural insights
   - Reusable solutions

**Note:** This step absorbs the `wai-signal-advisor.md` behavior — closeout is where signals get permanently captured.

### 3. Incomplete Work Capture

**Critical for session continuity.**

Document any unfinished work with enough detail to resume:

```markdown
## Incomplete Work

### [Task Name]
- **Status:** In Progress / Blocked / Pending Decision
- **What's Done:** [completed steps]
- **What Remains:** [specific next steps]
- **Blockers:** [if any]
- **Files Involved:** [paths]
- **To Continue:** [exact instructions for next session]
```

Store in session-summary lug `incomplete_work` field AND in `_session_state.next_session_recommendation`.

### 4. Version Increment

**Bump project state version:**

1. Read `WAI-Spoke/WAI-State.json`
2. Parse `wheel.version` (semver format, e.g., "2.0.7")
3. Increment patch: `2.0.7` → `2.0.8`
4. Write back to `WAI-State.json`

This versions the *session state*, not a release.

### 5. State Update

**Update session metadata in `WAI-State.json`:**

- `_session_state.session_count` += 1
- `_session_state.last_closeout` = current UTC timestamp (ISO-8601)
- `_session_state.last_modified_by` = current AI model name
- `_session_state.last_modified_at` = current UTC timestamp
- `_session_state.next_session_recommendation` = summary of what to do next

### 6. Session Log Clear

**Prepare for next session:**

- Truncate `WAI-Spoke/WAI-Session-Log.jsonl` (if exists)
- Insights already extracted to lugs/signals

### 7. Documentation Updates

**Document what's known and can be captured:**

- Update `CHANGELOG.md` with session accomplishments
- Update any documentation files affected by session work
- Generate clear, descriptive commit message

### 8. Summary Generation

**Create and present session summary:**

- What was accomplished
- What decisions were made
- What's incomplete (with continuation guidance)
- New version number
- Signals extracted
- Files modified

Present to user before commit.

### 9. Git Commit

**Persist to repository:**

```bash
git add WAI-Spoke/
git add [other session files]
git status  # Review what's staged
```

**Commit with descriptive message:**
```bash
git commit -m "WAI Session [N]: [accomplishments] | Incomplete: [if any]"
```

**Ask before push:**
```
Push to origin/main? (yes/no)
```

### 10. Verification

**Confirm persistence:**

```bash
git status                        # Must be clean
git log --oneline -1              # Verify commit exists
```

---

## Success Criteria

- [ ] Autosave lugs reconciled into permanent session-summary
- [ ] High-impact signals extracted (impact >= 8)
- [ ] **Incomplete work documented with continuation guidance**
- [ ] Version incremented in WAI-State.json
- [ ] Session state updated (session_count, timestamps)
- [ ] Session log cleared
- [ ] Documentation updated where applicable
- [ ] Changes committed with descriptive message
- [ ] User prompted before push

---

## Language Rules

**Never say:**
- "Probably saved"
- "Should be committed"
- "I think it persisted"

**Always say:**
- "Verified with git status"
- "Confirmed commit with git log"
- "Incomplete work documented in [location]"

---

## Related Commands

- `/wai-shipit` - Quality gates + closeout (for releases)
- `/wai-teach` - Push outbox to target (hub or spokes)
- `/wai-time` - Check context before closeout

---

*Closeout = Save game. Capture enough detail to continue the adventure.*

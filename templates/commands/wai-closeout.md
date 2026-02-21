# WAI Closeout

**Session State Preservation Protocol**

Save where we are so we can pick up seamlessly in a new session.

---

## Execution Context

- **Nodes:** spoke, hub
- **Exposure:** spoke.chat:local, spoke.chat:external
- **Paths Required:** spoke_path (current directory)
- **Paths Source:** Current working directory with WAI-Spoke/

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

- `/wai-teach` — Push signals/updates to hub or spokes (if outbox has items)
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

### 1. Distribute Outbox Lugs (P1, Auto-Teach)

**Purpose:** Automatically deliver lugs to their destinations

**Actions:**
1. Call `deliver_outbox_lugs(project_path, interactive=True)` from `wai.outbox_delivery`
2. For each lug in `WAI-Spoke/lugs/outbox/`:
   - Read destination_wheel_id
   - Resolve destination path (hub registry lookup)
   - Copy to destination inbox
   - Create delivery confirmation for hub
   - Move delivered lug to `outbox/distributed/`
3. If any destinations unresolved:
   - Present AskUserQuestion with valid spoke options from hub registry
   - Update lug destination_wheel_id with user choice
   - Retry delivery
4. Display delivery summary:
   - X lugs delivered to Y spokes
   - Z lugs skipped (with reasons)

**Failure Handling:**
- Delivery failures do NOT block closeout
- Undelivered lugs remain in outbox for next attempt
- Log all errors for user review

**Note:** This step runs for ALL nodes (spoke, hub, framework). Previously manual `/wai-teach` is now automated.

---

### 2. Lug Reconciliation (P6, P7)

**Review autosave lugs:**
```
WAI-Spoke/WAI-Lugs.jsonl
```

- Find entries where `ty="autosave"` AND `reconciled=false`
- Consolidate into ONE permanent `session-summary` lug capturing:
  - Task context (what was the session about?)
  - Actions taken
  - Files touched
  - Key decisions made
  - **Incomplete work** (critical for session continuity)
  - Final state
- Mark autosave lugs: `reconciled=true`, `s="c"`

### 3. Signal Extraction (P6, P7)

**Identify high-impact decisions (impact >= 8):**

- Review session for significant learnings
- Create signal lugs in `WAI-Spoke/WAI-Lugs.jsonl`
- **Flag which warrant hub consideration** for `/wai-learn`
  - Cross-project patterns
  - Architectural insights
  - Reusable solutions

### 4. Incomplete Work Capture (P1, P2)

**Critical for session continuity.**

Document any unfinished work with enough detail to resume:
- What remains to be done?
- What blockers exist?
- What decisions are pending?
- What files need attention?

Store in session-summary lug and/or `_session_state.next_session_recommendation`.

### 5. Version Increment (P7)

**Bump project state version:**

- Read `WAI-Spoke/WAI-State.json`
- Increment `wheel.version` patch (e.g., 2.0.1 → 2.0.2)
- This versions the *session state*, not a release

### 6. State Update (P1)

**Update session metadata:**

- `_session_state.session_count` += 1
- `_session_state.last_closeout` = current UTC timestamp
- `_session_state.last_modified_by` = current AI model
- `_session_state.last_modified_at` = current UTC timestamp
- Write to `WAI-State.json`

### 7. Session Log Clear (P1)

**Prepare for next session:**

- Truncate `WAI-Spoke/WAI-Session-Log.jsonl`
- Insights already extracted to lugs/signals

### 8. Documentation Updates (P7, P8)

**Document what's known and can be captured:**

- Update `README.md` if capabilities changed
- Update `CHANGELOG.md` with session accomplishments
- Update any documentation files affected by session work
- Generate clear, descriptive commit message

### 9. Summary Generation (P2)

**Create session summary:**

- What was accomplished
- What decisions were made
- What's incomplete (with continuation guidance)
- New version number
- Signals extracted
- Files modified

Present to user before commit.

### 10. Git Commit (P7)

**Persist to repository:**

```bash
git add WAI-Spoke/
git add [session files]
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

### 11. Verification

**Confirm persistence:**

```bash
git status                        # Must be clean
git log --oneline -1              # Verify commit exists
git log origin/main --oneline -1  # If pushed, verify remote
```


## Success Criteria

- [ ] Outbox lugs distributed to destinations (Step 1)
- [ ] Autosave lugs reconciled into permanent record
- [ ] High-impact signals extracted and flagged for hub
- [ ] **Incomplete work documented with continuation guidance**
- [ ] Version incremented
- [ ] WAI-State.json updated
- [ ] Session log cleared
- [ ] Documentation updated where applicable
- [ ] Changes committed with descriptive message
- [ ] User prompted before push
- [ ] Delivery summary displayed (X lugs to Y spokes)

---

## Incomplete Work Format

When documenting incomplete work, include:

```markdown
## Incomplete Work

### [Task Name]
- **Status:** [In Progress / Blocked / Pending Decision]
- **What's Done:** [completed steps]
- **What Remains:** [specific next steps]
- **Blockers:** [if any]
- **Files Involved:** [paths]
- **To Continue:** [exact instructions for next session]
```

This enables any new session to identify and resume the work.

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

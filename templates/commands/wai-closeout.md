# WAI Closeout

**Session State Preservation Protocol**

Save where we are so we can pick up seamlessly in a new session.

## Purpose

Persist session state with enough detail that a new agent/session can:
- Understand what was accomplished
- Identify incomplete work remaining
- Continue where we left off

---

## Closeout Procedure

### 1. Lug Reconciliation (P6, P7)

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

### 2. Signal Extraction (P6, P7)

**Identify high-impact decisions (impact >= 8):**

- Review session for significant learnings
- Create signal lugs in `WAI-Spoke/WAI-Lugs.jsonl`
- **Flag which warrant hub consideration** for `/wai-learn`
  - Cross-project patterns
  - Architectural insights
  - Reusable solutions

### 3. Incomplete Work Capture (P1, P2)

**Critical for session continuity.**

Document any unfinished work with enough detail to resume:
- What remains to be done?
- What blockers exist?
- What decisions are pending?
- What files need attention?

Store in session-summary lug and/or `_session_state.next_session_recommendation`.

### 4. Version Increment (P7)

**Bump project state version:**

- Read `WAI-Spoke/WAI-State.json`
- Increment `wheel.version` patch (e.g., 2.0.1 → 2.0.2)
- This versions the *session state*, not a release

### 5. State Update (P1)

**Update session metadata:**

- `_session_state.session_count` += 1
- `_session_state.last_closeout` = current UTC timestamp
- `_session_state.last_modified_by` = current AI model
- `_session_state.last_modified_at` = current UTC timestamp
- Write to `WAI-State.json`

### 6. Session Log Clear (P1)

**Prepare for next session:**

- Truncate `WAI-Spoke/WAI-Session-Log.jsonl`
- Insights already extracted to lugs/signals

### 7. Documentation Updates (P7, P8)

**Document what's known and can be captured:**

- Update `README.md` if capabilities changed
- Update `CHANGELOG.md` with session accomplishments
- Update any documentation files affected by session work
- Generate clear, descriptive commit message

### 8. Summary Generation (P2)

**Create session summary:**

- What was accomplished
- What decisions were made
- What's incomplete (with continuation guidance)
- New version number
- Signals extracted
- Files modified

Present to user before commit.

### 9. Git Commit (P7)

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

### 10. Verification

**Confirm persistence:**

```bash
git status                        # Must be clean
git log --oneline -1              # Verify commit exists
git log origin/main --oneline -1  # If pushed, verify remote
```

---

## Success Criteria

- [ ] Autosave lugs reconciled into permanent record
- [ ] High-impact signals extracted and flagged for hub
- [ ] **Incomplete work documented with continuation guidance**
- [ ] Version incremented
- [ ] WAI-State.json updated
- [ ] Session log cleared
- [ ] Documentation updated where applicable
- [ ] Changes committed with descriptive message
- [ ] User prompted before push

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
- `/wai-learn` - Push signals to hub
- `/wai-time` - Check context before closeout

---

*Closeout = Save game. Capture enough detail to continue the adventure.*

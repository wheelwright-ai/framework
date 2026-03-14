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

### Step 0: Ask What's Next (Before Everything Else)

**Purpose:** Shape how the session will be documented and whether gaps need filling.

This is the very first step, before any document writing or reconciliation:

```
Before I close out — what are you doing next?
  a) Continuing work (I'll optimize the handoff)
  b) Done for this session
```

Save the user's answer. Proceed to the next step with that context.

---

### Step 0b: Lug Gap Review (If Continuing)

**Purpose:** Ensure the next lug is complete enough to hand off to the next session.

If the user answered "Continuing work" in Step 0:

1. **Identify the next lug** using this priority order (same as wakeup Step 4):
   - `s: "p"` (in progress) → resume this
   - `priority: "before_next_epic"` AND `s: "o"` → start this
   - `ty: "bug"` AND `s: "o"` → fix this
   - First `s: "o"` non-epic → start this

2. **Review that lug against this gap checklist:**
   ```
   Gap check on next lug ({i} — {t}):
   □ perceive — describes current state and what to look at?
   □ execute — describes approach, constraints, what to avoid?
   □ verify — describes how to confirm success?
   □ description — detailed enough for a fresh agent to proceed?
   □ Discussed context — anything agreed outside the lug this session that should be added?
   ```

3. **Fill any gaps found** by updating the lug in `WAI-Spoke/WAI-Lugs.jsonl` before proceeding.

4. **Note completion:**
   - If gaps found and filled: "Lug updated with [specific field]."
   - If complete: "Lug is ready, no gaps found."

---

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

**Maintain project documentation so it reflects current reality.**

This step is NOT optional — documentation rot is a real problem. At minimum:

#### 7a. README.md (REQUIRED — every closeout)

Review `README.md` against current project state. Update if any of these changed this session:
- Project description or purpose
- Architecture or key components
- Setup/install instructions
- Available commands or APIs
- Dependencies or requirements

If `README.md` doesn't exist, create a minimal one with project name and one-liner from `_project_foundation.identity`.

#### 7b. Framework-only: llms-full.txt (if this is the framework repo)

If the current project IS the Wheelwright framework (check `wheel.name` or repo path):
- Regenerate `framework/docs/llms-full.txt` — a single-file concatenation of all framework documentation
- Include: README.md, skill files (templates/commands/*.md), lug schema spec, skill contract spec
- This file is consumed by LLMs for full-context framework understanding
- Header format: `# Wheelwright AI Framework - Complete Documentation\n# Generated: {ISO-8601}\n# Version: {wheel.version}`

#### 7c. Other documentation

- Update `CHANGELOG.md` with session accomplishments (if the project maintains one)
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

### Step 11: Intelligent Landing

**Purpose:** Provide clear context for the next session and optionally compress context.

#### Branch A — Continuing

If the user answered "Continuing work" in Step 0:

1. **Token meter BEFORE** — Estimate current context:
   - Formula: (turns × ~500 tokens/turn) + loaded files (1 token ≈ 4 bytes)
   - Record as `tokens_before`

2. **Build retention summary** (terse, 200–300 words):
   ```markdown
   ## Compact — Session {N} → {N+1}

   **Next:** {lug i} — {lug title}

   **Architecture decisions:**
   - {decision 1}
   - {decision 2}

   **Files touched:**
   - {path}: {one-line note}

   **Next lug (gap-filled):**
   - Perceive: {summary}
   - Execute: {summary}
   - Verify: {summary}
   - Discussed context: {anything agreed outside the lug this session}

   **WAI expectations:**
   - Signal threshold: {N} | Lug conventions: s=o/p/c | Closeout on >70% context

   **Dropped:** {N} turns exploration, resolved questions, file dumps
   ```

3. **Record compact event** — Append to `WAI-Spoke/WAI-Lugs.jsonl`:
   ```json
   {
     "i": "compact-{YYYYMMDD-HHMMSS}",
     "ty": "compact",
     "t": "Context compact: Session {N} → {N+1}",
     "s": "c",
     "ca": "{ISO-8601}",
     "gb": "{agent}",
     "from_session": "{session_id}",
     "tokens_before": {N},
     "tokens_after": null,
     "next_lug": "{next_lug_id}",
     "summary": "{retention_summary}"
   }
   ```
   Note: `tokens_after` is null here — it gets filled by wakeup after `/compact` fires.

4. **Auto-compress** — Invoke `/compact` with the retention summary as custom summary.

5. **Token meter AFTER** — Estimate tokens of the summary itself:
   ```
   Context compressed: ~{BEFORE}K → ~{AFTER}K ({PCT}% reduction)
   Next up: {lug title}
   ```

6. **Update WAI-State.json** — Record compact event reference in `_session_state`:
   ```json
   "_session_state": {
     "last_compact": "{compact-lug-id}",
     "compact_tokens_before": {N},
     "compact_tokens_after": {M}
   }
   ```

---

#### Branch B — Ending Session

If the user answered "Done for this session" in Step 0:

Display a summary and stop (no compression):

```
Session {N} complete. All work saved.

Accomplished:
- {item 1}
- {item 2}

When you return:
- Run /wai to orient
- Next up: {next lug title OR next_action}
- Version: {wheel.version}

See you next session.
```

Do not invoke `/compact`, do not write compact lug, do not read further files.

---

## Success Criteria

- [ ] Step 0: User answer recorded ("continuing" or "done")
- [ ] Step 0b (if continuing): Next lug gaps reviewed and filled if needed
- [ ] Autosave lugs reconciled into permanent record
- [ ] High-impact signals extracted and flagged for hub
- [ ] **Incomplete work documented with continuation guidance**
- [ ] Version incremented
- [ ] WAI-State.json updated
- [ ] Session log cleared
- [ ] Documentation updated where applicable
- [ ] Changes committed with descriptive message
- [ ] User prompted before push
- [ ] Step 11 completed: Branch A (compact + token meter) OR Branch B (clean exit)

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

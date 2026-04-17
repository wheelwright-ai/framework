# Built-In Skills

WAI includes built-in skills for common agent operations. All skills follow the [Skill Contract Specification](../../WAI-Skill-Contract-Spec.md).

## Core Skills

### safe-refactor (Guardian)

**Purpose:** Create git checkpoint before structural changes

**Trigger:** Before file restructuring, deletions, or large refactors

**Model:** Lightweight (Haiku)

**Behavior:**
1. Detect structural change intent (move files, delete directories, rename modules)
2. Run `git status` to see current state
3. Create checkpoint commit: `git commit -m "checkpoint: before [operation]"`
4. Allow operation to proceed
5. If operation fails, user can easily revert to checkpoint

**Why it exists:** An agent once deleted the entire Hub folder by restructuring files without a checkpoint. This skill prevents data loss.

**Output:** Checkpoint commit hash

**Use cases:**
- Moving `src/` to `app/`
- Deleting deprecated modules
- Renaming package structure
- Large multi-file refactors

---

### session-observer (Watcher)

**Purpose:** Track session events and create synthesis at closeout

**Trigger:**
- session_start (passive observation)
- session_end (active synthesis)
- pre_closeout (ledger reconciliation)

**Model:** Lightweight (Haiku)

**Behavior:**

**On session_end:**
1. **Ledger Reconciliation:**
   - Read WAI-Ledger.jsonl
   - Filter entries with status: "open"
   - For each: check if delivered this session (matching commit exists)
   - Create delivery entries for fulfilled commitments
   - Flag unfulfilled commitments

2. **Documentation Check:**
   - If commits modified framework files (hub/BRIEF.md, *-Spec.md, templates/*, skills/*)
   - AND docs/ directory exists
   - Flag: "Documentation may need updates"
   - List files changed that affect docs
   - Suggest: "Update README, regenerate llms-full.txt, update guides"

3. **Session Synthesis:**
   - Read all observations from current session
   - Read Lugs created this session
   - Read commits made (git log since session start)
   - Create session summary Lug with:
     - High-impact events (impact >= 8)
     - New Lugs created (count by type)
     - Commits made (count, summary)
     - Incomplete work (Lugs still in-progress)
     - Unfulfilled commitments (from ledger)
     - Documentation updates needed (if applicable)

**Output:** Session summary Lug (type: observation)

**Use cases:**
- End-of-session closeout
- Context loss prevention (ledger reconciliation)
- Documentation drift detection
- Progress tracking across sessions

---

### hub-watcher (Watcher - Spoke-Only)

**Purpose:** Monitor Hub for framework updates and cross-node signals

**Trigger:** session_start (automatic on spoke wakeup)

**Conditions:** ONLY runs if node_type == "spoke" (skips if node_type == "hub")

**Model:** Lightweight (Haiku)

**Behavior:**
1. **Check node_type:** If "hub", skip (hub doesn't watch itself)
2. **Framework version check:**
   - Read hub/registry.yaml - get hub framework_version
   - Compare with spoke framework_version in WAI-Manifest.yaml
   - If patch update (2.0.0 → 2.0.1) AND no breaking changes:
     * Auto-apply: Update spoke WAI-Manifest.yaml
     * Pull new templates from framework/templates/
     * Create update Lug documenting changes
     * Report: "Auto-upgraded to v{X} (patch update)"
   - If minor/major update (2.0.0 → 2.1.0 or 3.0.0):
     * Notify agent: "Hub has v{X}, you're on v{Y}"
     * Read hub update Lugs to show what changed
     * Suggest: "Review changes and run /framework-update when ready"
     * Flag: Breaking changes require review

3. **Pending signals check:**
   - Check hub/intake/ for unprocessed signals addressed to this spoke
   - Count: how many high-impact signals pending
   - Auto-pull signals relevant to this spoke (matching subscription patterns)
   - Create local Lugs with source_id pointing to hub signals
   - Suggest: "Review and acknowledge signals"

4. **Hub health check:**
   - Check hub/health.yaml for:
     - intake_pending > 0
     - oldest_pending timestamp
   - If stale intake (oldest_pending > 7 days):
     - Report: "Hub has stale intake"
     - Suggest: "Run hub maintenance"

**Output:**
- Framework update status
- Pending signals count and titles
- Hub health issues (if any)
- Recommendations for conductor

**Use cases:**
- Automatic patch upgrades (zero user action)
- Framework update notifications (minor/major versions)
- Cross-spoke learning (pull patterns from hub)
- Hub health monitoring

---

### hub-processor (Watcher - Hub-Only)

**Purpose:** Process hub/intake/, detect cross-spoke patterns, check spoke health

**Trigger:** session_start (automatic on hub wakeup)

**Conditions:** ONLY runs if node_type == "hub" (skips if node_type == "spoke")

**Model:** Lightweight (Haiku)

**Behavior:**
1. **Check node_type:** If "spoke", skip (spokes don't process intake)

2. **Process Intake:**
   - Read all files in hub/intake/**/*.yaml
   - For each signal:
     * Parse Lug content (id, type, impact, node, summary)
     * Check if already processed (exists in hub/WAI-Lugs.jsonl with same source_id)
     * If new: Create hub Lug with source_id pointing to spoke Lug
     * Move to hub/intake/processed/{node-path}/{lug-id}.yaml
   - Count: signals processed, duplicates skipped

3. **Aggregate Patterns:**
   - Group signals by category (security, performance, architecture, preference, etc.)
   - Look for recurring patterns across spokes:
     * Same diagnosis appearing in 2+ projects → create observation Lug
     * Similar decisions made independently → learning Lug
     * Common preferences emerging → flag for hub/BRIEF.md consolidation
   - Create observation Lugs for patterns with 2+ instances

4. **Check Spoke Health:**
   - Read hub/registry.yaml for all registered spokes
   - For each spoke:
     * Check if framework_version matches hub version
     * Check last_session timestamp (stale if >30 days)
     * Check outbound_pending count (stuck signals?)
   - Create observation Lugs for health issues

5. **Update Hub Health:**
   - Write hub/health.yaml:
     * intake_pending: count of unprocessed signals
     * oldest_pending: timestamp of oldest signal
     * spokes_outdated: count of spokes on old framework version
     * patterns_detected: count of cross-spoke patterns this session

**Output:**
- "{N} signals processed from {M} spokes"
- "{P} patterns detected across spokes"
- "{S} spokes need framework updates"
- "Use /wai (Step 9b: auto-teach on closeout) to consolidate learnings into framework"

**Pattern detection examples:**
- **Recurring diagnosis:** 3 spokes found same SQL injection → recommend framework guidance
- **Common preference:** Multiple spokes have same communication style → consolidate into hub/BRIEF.md
- **Architecture convergence:** 2+ spokes adopted similar pattern → document as learning
- **Template gap:** Multiple spokes created similar custom files → promote to framework template

**Use cases:**
- Cross-spoke learning aggregation
- Pattern detection across projects
- Hub health monitoring
- Framework evolution feedback loop

---

## Advisor Skills (Coming Soon)

### complexity-advisor

**Purpose:** Warn when task complexity exceeds threshold

**Trigger:** Task analysis (2+ files OR 6+ steps)

**Output:** Diagnosis Lug if complexity is high

---

### stewardship-advisor

**Purpose:** Detect scope drift (out-of-scope work)

**Trigger:** Work item analysis

**Output:** Warning if work doesn't match stated scope

---

### context-advisor

**Purpose:** Warn when token usage approaches limits

**Trigger:** Context analysis at 60%, 80%, 90% thresholds

**Output:** Warning with recommendations to reduce context

---

### signal-advisor

**Purpose:** Auto-submit high-impact Lugs to hub/intake/

**Trigger:** Lug creation with impact >= 8

**Output:** Signal submission to hub

---

## Creating Custom Skills

See [WAI-Skill-Contract-Spec.md](../../WAI-Skill-Contract-Spec.md) for full specification.

**Minimal skill template:**
```yaml
name: my-skill
role: reviewer  # guardian | reviewer | advisor | watcher
model: lightweight  # lightweight | standard | advanced
description: "What this skill does"

trigger:
  events:
    - on_commit
  conditions:
    - "files match pattern"

scope:
  reads:
    - "src/**/*.py"
  writes:
    - "WAI-Lugs.jsonl"

behavior:
  on_trigger: |
    1. Read files matching trigger
    2. Analyze for issues
    3. Create diagnosis Lugs if problems found

output:
  success:
    type: "check_complete"
    data:
      issues_found: 0
  findings:
    type: "issues_detected"
    data:
      lugs: ["lug-001", "lug-002"]
```

**Best practices:**
- Use lightweight models for simple checks (git status, file exists)
- Use standard models for code analysis
- Use advanced models only for complex reasoning (architecture decisions, security analysis)
- Always produce Lugs (diagnosis, prescription, observation)
- Include use_cases in skill definition for clarity
- Test skills with realistic scenarios before deploying

## Skill Orchestration

Main agent orchestrates skills:
1. Reads skill definitions from `framework/skills/`, `hub/skills/`, `{spoke}/skills/`
2. Matches triggers to current operation
3. Fires applicable skills in order: guardians → reviewers → advisors → watchers
4. Collects Lugs from each skill
5. Presents findings to conductor
6. Executes based on conductor decisions

**Example flow:**
```
User: "Refactor auth module to use sessions instead of JWT"

1. safe-refactor fires (guardian, pre-refactor trigger)
   → Creates checkpoint commit

2. Main agent refactors code

3. qc-check fires (reviewer, on_commit trigger)
   → Runs tests
   → Creates diagnosis Lug: "Test failure in /tests/auth/test_login.py"

4. Main agent fixes test failure

5. security-review fires (reviewer, auth code changed)
   → Scans for vulnerabilities
   → Creates diagnosis Lug: "Session fixation vulnerability in session creation"

6. Main agent addresses security issue

7. signal-advisor fires (advisor, high-impact Lug created)
   → Submits security finding to hub/intake/ (impact: 9)

8. session-observer fires (watcher, pre_closeout)
   → Reconciles ledger
   → Creates session summary Lug
```

This is agent collaboration in action.

# WAI Multi-Agent Evolution Plan
**Document Type:** Strategic Plan & Historical Record  
**Created:** January 19, 2026  
**Author:** Mario Vaccari + Claude Analysis  
**Status:** PROPOSAL → Ready for Lug Conversion

---

## Part 1: Backstory & Context

### The Wheelwright Journey

Wheelwright (WAI) evolved from the Session Continuity Framework (SCF), a system Mario developed over 18+ months to solve the fundamental problem of AI amnesia. The core insight: **AI assistants forget everything between sessions, forcing humans to re-explain context repeatedly.**

WAI introduced:
- **Hub-and-Spoke architecture** - Central Hub learns from all projects (Spokes)
- **WAI-Spoke/** directory - Project-level context persistence
- **Universal tool support** - Works with Claude, ChatGPT, Gemini, Copilot, etc.
- **Token efficiency** - ADAPTIVE workflow prevents premature implementation waste

The framework is open source at [github.com/wheelwright-ai/framework](https://github.com/wheelwright-ai/framework) and documented at [wheelwright.ai](https://wheelwright.ai).

### The Multi-Agent Moment (January 2026)

In early 2026, the AI coding landscape shifted dramatically toward multi-agent approaches. Several key developments converged:

1. **Steve Yegge's Gas Town launch** (January 1, 2026) - Orchestration layer for agent "colonies"
2. **Beads maturity** (v0.29, 4.4k GitHub stars) - Git-backed task graphs for agent memory
3. **Google Conductor** (December 2025) - Context-driven development methodology
4. **VS Code Copilot Instructions** - Auto-discovery of `.github/copilot-instructions.md`
5. **Backpressure philosophy** - Automated feedback loops as the key to agent autonomy

Mario recognized that WAI is perfectly positioned to be the **foundation layer** these tools build upon. WAI already solves context persistence; it needs to absorb the best ideas from this wave while maintaining its unique value proposition.

### Why This Matters for WAI

WAI's strategic position: **"The foundation other frameworks stand on top of."**

- Gas Town needs context persistence → WAI provides it
- Beads needs cross-project learning → WAI Hub provides it  
- All tools need IDE integration → WAI auto-configures it
- Multi-agent colonies need shared memory → WAI Hub is "the village brain"

**Marketing angle:** "It takes a village. WAI Hub is the brain your agent colony shares."

---

## Part 2: Reference Sources

### Primary Sources Analyzed

| Source | URL | Key Contribution |
|--------|-----|------------------|
| Wheelwright Framework | https://github.com/wheelwright-ai/framework | Current WAI implementation |
| Beads Issue Tracker | https://github.com/steveyegge/beads | Git-backed task graph, dependency chains, hash IDs |
| Steve Yegge - Future of Coding Agents | https://steve-yegge.medium.com/the-future-of-coding-agents-e9451a84207c | "Colonies > super-ants", Gas Town vision |
| Banay.me - Don't Waste Your Backpressure | https://banay.me/dont-waste-your-backpressure/ | Automated feedback loops scale agent autonomy |
| Focused Chaos - Vibe Coding Trap | https://www.focusedchaos.co/p/vibe-coding-without-system-design-is-a-trap | System sketch before prompts, 5 critical questions |
| VS Code Copilot Live | https://www.youtube.com/live/IdPtTBbYOtw?t=93s | Agent HQ, work trees, copilot-instructions.md |
| Optimized Vibecoding Stack | https://www.youtube.com/shorts/T2bd1kGEISo | Planning → Coding → Testing agent loop |
| Google Antigravity + Claude Code | https://www.youtube.com/watch?v=yMJcHcCbgi4 | IDE as agent hub |
| Testsprite Integration | https://www.youtube.com/watch?v=KcOQC_yJ5oM | Free test-runner agent for backpressure |

### Secondary Sources (Background)

| Source | URL | Relevance |
|--------|-----|-----------|
| Beads & Future of Programming | https://www.edgartools.io/beads-and-the-future-of-programming/ | Context on Yegge's 1M lines/year claim |
| Google Conductor / Gemini CLI | (December 2025 launch) | Context-driven development methodology |

---

## Part 3: Key Concepts Absorbed

### 3.1 Backpressure (from Banay.me)

**Definition:** Automated feedback that tells agents when they're wrong *without human intervention*.

**The Insight:**
> "If you're directly responsible for checking each line of code produced is syntactically valid, then that's time taken away from thinking about the larger goals."

**Types of backpressure:**
- Build systems (syntax validation)
- Type systems (contract enforcement)
- Test suites (correctness verification)
- Rendered previews (UI verification via Playwright/DevTools)
- LSP/linters (style/quality)

**WAI Application:** Add `WAI-Backpressure.yaml` config so AI knows how to self-verify.

### 3.2 Colony Architecture (from Steve Yegge)

**Definition:** Multiple coordinated agents rather than one "super-ant" running longer.

**The Insight:**
> "When work needs to be done, nature prefers colonies. Nature builds ant colonies, while Claude Code is 'the world's biggest fuckin' ant.'"

**Gas Town model:**
- Orchestration layer hurls swarms of Claude Code instances at epics
- Beads provides shared memory/task graph
- Agents coordinate via git-backed issue tracker

**WAI Application:** Hub becomes the "village brain" that agent colonies share.

### 3.3 Idempotent Tasks (Mario's Principle)

**Definition:** Tasks that can be re-processed without side effects unless explicitly cross-linked.

**The Insight:**
> "Lugs and epics should be idempotent unless cross-linked and explained. This makes the worklog actionable."

**Application:** 
- Default: `idempotent: true` - agent can pick up any Lug safely
- When blocked: `idempotent: false` + `dep_reason` required
- This enables safe parallel work by multiple agents

### 3.4 System Sketch (from Focused Chaos)

**Definition:** One-page forcing function to externalize architecture decisions before AI answers in code.

**5 Questions Before Any Feature:**
1. What is likely to change later? (don't hardcode)
2. Should this exist once or everywhere? (DRY)
3. What is the source of truth?
4. What breaks if I change this?
5. How would I test this?

**The Insight:**
> "You're always vibe coding *into* a system, whether you've designed it intentionally or not."

**WAI Application:** System Sketch section in WAI-Guide.md template.

### 3.5 Feature Specs (from Google Conductor)

**Definition:** Persistent context files that track feature-scoped work, surviving implementation.

**Conductor Model:**
1. Setup - persistent context files (Product.md, TechStack.md, Workflow.md)
2. New Track - specs + plan before code
3. Implement - task-by-task execution with plan.md updates
4. Smart Reverts - undo by "track" not just commits

**WAI Application:** `WAI-Features/` directory holding SPEC.md, PLAN.md, TEST-CASES.md per feature.

### 3.6 IDE Self-Optimization (Mario's Requirement)

**Definition:** WAI should audit itself at session start to ensure maximum effectiveness.

**The Insight:**
> "WAI should ask itself 'is this IDE fully optimized?' If not, ask to do so at time of startup so we are operating as effectively as possible."

**Application:** Session start checks for all integration files, prompts to create missing ones.

---

## Part 4: Consolidated Lug Format

### The Problem

Currently WAI has:
- `WAI-Backlog.md` - Human-readable list
- Separate Lug tracking - Machine-readable tasks

This creates redundancy and sync issues.

### The Solution: WAI-Lugs.jsonl

Single source of truth that IS the backlog:

```jsonl
{"id":"lug-a3f8","type":"epic","title":"Auth System","status":"open","priority":1,"deps":[],"idempotent":true,"created":"2026-01-19T10:00:00Z","updated":"2026-01-19T10:00:00Z"}
{"id":"lug-a3f8.1","type":"task","title":"Design login UI","parent":"lug-a3f8","status":"ready","priority":2,"deps":[],"idempotent":true,"created":"2026-01-19T10:05:00Z"}
{"id":"lug-a3f8.2","type":"task","title":"Backend validation","parent":"lug-a3f8","status":"blocked","priority":2,"deps":["lug-a3f8.1"],"idempotent":false,"dep_reason":"Needs UI contract to define API shape","created":"2026-01-19T10:06:00Z"}
{"id":"lug-b7c2","type":"bug","title":"Token refresh fails silently","status":"open","priority":0,"deps":[],"idempotent":true,"discovered_from":"lug-a3f8.1","created":"2026-01-19T11:00:00Z"}
```

### Schema Definition

```yaml
# WAI-Lugs.jsonl Schema v1.0

required_fields:
  id: string          # Format: "lug-{hash}" or "lug-{parent}.{seq}"
  type: enum          # epic | feature | task | bug | chore
  title: string       # Human-readable title
  status: enum        # open | ready | in_progress | blocked | closed
  priority: integer   # 0=critical, 1=high, 2=medium, 3=low, 4=backlog
  deps: array         # List of blocking Lug IDs
  idempotent: boolean # Can this be worked independently?
  created: datetime   # ISO 8601 timestamp

optional_fields:
  parent: string      # Parent Lug ID for hierarchical tasks
  description: string # Detailed description
  assignee: string    # Agent or human assigned
  labels: array       # Flexible tags
  dep_reason: string  # REQUIRED when idempotent=false
  discovered_from: string  # Parent Lug that surfaced this work
  closed_reason: string    # Why was this closed?
  updated: datetime   # Last modification timestamp

validation_rules:
  - if deps is non-empty, idempotent must be false
  - if idempotent is false, dep_reason is required
  - parent must reference existing Lug ID
  - discovered_from must reference existing Lug ID
```

### Lug ID Format

Following Beads' approach for collision resistance:

- **Hash-based:** `lug-a3f8` (4-6 hex chars based on DB size)
- **Hierarchical:** `lug-a3f8.1`, `lug-a3f8.2` (children of epic)
- **Deep nesting:** `lug-a3f8.3.1` (up to 3 levels)

Benefits:
- Merge-safe across branches
- Human-readable parent-child relationships
- No coordination needed for ID generation

---

## Part 5: Detailed Action Plans

### Epic 1: Lug System Consolidation

**Goal:** Replace WAI-Backlog.md + separate tracking with unified WAI-Lugs.jsonl

**Background:** WAI currently tracks work in multiple places, creating sync issues and making it harder for agents to understand what's actionable. Beads proved that a single JSONL file with dependency tracking is the right model.

**Reference:** https://github.com/steveyegge/beads (JSONL format, dependency types)

#### Lug 1.1 [Lug: 95bbdc7b]: Define WAI-Lugs.jsonl Schema
- **Type:** task
- **Priority:** 1 (high)
- **Idempotent:** true
- **Description:** Create formal schema definition for WAI-Lugs.jsonl including all field types, validation rules, and examples. Document in WAI-Spoke/schemas/ or docs/.
- **Acceptance Criteria:**
  - Schema supports: id, type, title, status, priority, deps, idempotent, dep_reason, parent, discovered_from
  - Validation rules documented
  - Example JSONL file created
- **Estimated Effort:** 2 hours

#### Lug 1.2 [Lug: 64fcb419]: Implement `wai lug` CLI Commands
- **Type:** feature
- **Priority:** 1 (high)
- **Idempotent:** true
- **Description:** Add CLI commands for Lug management: `wai lug create`, `wai lug list`, `wai lug update`, `wai lug close`, `wai lug show`
- **Acceptance Criteria:**
  - All CRUD operations work
  - `--json` flag for programmatic output
  - Validation enforces schema rules
- **Estimated Effort:** 8 hours

#### Lug 1.3 [Lug: 7a612105]: Implement `wai ready` Command
- **Type:** feature  
- **Priority:** 1 (high)
- **Idempotent:** true
- **Description:** Compute and return Lugs with no open blockers, sorted by priority. This is the "what should I work on next?" command.
- **Reference:** https://github.com/steveyegge/beads (`bd ready` implementation)
- **Acceptance Criteria:**
  - Returns only Lugs where all deps are closed
  - Respects priority ordering
  - `--json` flag for agents
  - `--limit N` flag for batch size
- **Estimated Effort:** 4 hours

#### Lug 1.4 [Lug: 6d9ffa7a]: Migrate Existing Backlogs
- **Type:** task
- **Priority:** 2 (medium)
- **Idempotent:** true
- **Description:** Create migration script to convert existing WAI-Backlog.md files to WAI-Lugs.jsonl format.
- **Acceptance Criteria:**
  - Script parses markdown backlog
  - Generates valid JSONL
  - Preserves all task information
- **Estimated Effort:** 4 hours

#### Lug 1.5 [Lug: d6ac7ba7]: Update WAI-Guide.md to Reference Lugs
- **Type:** task
- **Priority:** 2 (medium)
- **Deps:** [1.1]
- **Idempotent:** false
- **Dep Reason:** Schema must be finalized before documenting in guide
- **Description:** Update WAI-Guide.md template to explain Lug system and how AI agents should interact with it.
- **Estimated Effort:** 2 hours

---

### Epic 2: IDE Optimization System

**Goal:** WAI automatically checks and configures IDE integration on every session start

**Background:** Mario identified that agents often work in partially-configured environments, reducing effectiveness. WAI should self-audit and prompt to fix gaps.

**Reference:** 
- https://www.youtube.com/live/IdPtTBbYOtw?t=93s (VS Code Copilot instructions)
- https://github.com/wheelwright-ai/framework (existing integration files)

#### Lug 2.1 [Lug: c939c84e]: Define IDE Optimization Checklist
- **Type:** task
- **Priority:** 1 (high)
- **Idempotent:** true
- **Description:** Document all integration files WAI should check: .github/copilot-instructions.md, CLAUDE.md, .cursorrules, .vscode/settings.json, WAI-Backpressure.yaml, git hooks.
- **Acceptance Criteria:**
  - Checklist covers all major AI tools
  - Each item has: path, check condition, remediation action
- **Estimated Effort:** 2 hours

#### Lug 2.2 [Lug: f1163529]: Implement `wai align` Command
- **Type:** feature
- **Priority:** 1 (high)
- **Deps:** [2.1]
- **Idempotent:** false
- **Dep Reason:** Checklist must exist before implementing alignment
- **Description:** "Wheel alignment for your AI." Detect active tools/devices and optimize their configuration for WAI.
- **Acceptance Criteria:**
  - Detects tool (VS Code, Cursor, Terminal) and Device (Mac, WSL, Win)
  - Scores "Alignment" based on config quality (not just file existence)
  - Interactive wizard to tune configurations
  - Updates session log with alignment score
- **Estimated Effort:** 6 hours

#### Lug 2.3 [Lug: 36a0461d]: Implement Auto-Fix Prompts
- **Type:** feature
- **Priority:** 1 (high)
- **Deps:** [2.2]
- **Idempotent:** false
- **Dep Reason:** Audit function must work before adding prompts
- **Description:** When audit finds missing/invalid items, prompt user to fix: "⚠️ Missing .github/copilot-instructions.md - create? [Y/n]"
- **Acceptance Criteria:**
  - Interactive prompts for each issue
  - `--yes` flag for non-interactive (auto-fix all)
  - Templates used for file creation
- **Estimated Effort:** 4 hours

#### Lug 2.4 [Lug: e7a8e9ff]: Add Audit to Session Start
- **Type:** task
- **Priority:** 2 (medium)
- **Deps:** [2.3]
- **Idempotent:** false
- **Dep Reason:** Prompts must work before integrating into flow
- **Description:** Run IDE audit automatically when WAI session starts (via WAI-Guide.md instructions or CLI hook).
- **Acceptance Criteria:**
  - Audit runs on `wai status` or session start
  - Can be disabled with config flag
  - Results shown in session context
- **Estimated Effort:** 2 hours

#### Lug 2.5 [Lug: d4fd8c26]: Generate .github/copilot-instructions.md
- **Type:** task
- **Priority:** 1 (high)
- **Idempotent:** true
- **Description:** Add template for .github/copilot-instructions.md that points to WAI-Spoke/. Auto-generate on `wai init`.
- **Reference:** VS Code Copilot auto-discovery spec
- **Acceptance Criteria:**
  - Template references WAI-Spoke/WAI-Guide.md
  - Created automatically on `wai init`
  - Existing file not overwritten (merge or skip)
- **Estimated Effort:** 1 hour

#### Lug 2.6: Implement Hub Alignment Menu
- **Type:** feature
- **Priority:** 2 (medium)
- **Deps:** [2.2]
- **Idempotent:** true
- **Description:** specific Hub CLI menu to view the "Alignment Score" of all registered projects at a glance.
- **Acceptance Criteria:**
  - Scans registry/wheel-projects.json
  - Reads latest session log for each project
  - Displays table: Project | Tool | Score | Status
- **Estimated Effort:** 3 hours

---

### Epic 3: Backpressure Configuration

**Goal:** Let projects declare their build/test/lint commands so AI knows how to self-verify

**Background:** The Banay.me article established that backpressure (automated feedback) is the key to scaling agent autonomy. WAI should know what commands provide backpressure.

**Reference:** https://banay.me/dont-waste-your-backpressure/

#### Lug 3.1 [Lug: 4289c7c4]: Define WAI-Backpressure.yaml Schema
- **Type:** task
- **Priority:** 1 (high)
- **Idempotent:** true
- **Description:** Create schema for backpressure configuration file.
- **Acceptance Criteria:**
  - Supports: build, test, lint, typecheck commands
  - Each command has: command string, on_failure action (signal|warn|block)
  - Optional: timeout, working_directory
- **Estimated Effort:** 2 hours

#### Lug 3.2 [Lug: 5eb91d79]: Implement Backpressure Setup Wizard
- **Type:** feature
- **Priority:** 2 (medium)
- **Deps:** [3.1]
- **Idempotent:** false
- **Dep Reason:** Schema must exist before wizard can populate it
- **Description:** Interactive wizard that detects project type (package.json, pyproject.toml, etc.) and suggests backpressure commands.
- **Acceptance Criteria:**
  - Detects Node, Python, Go, Rust projects
  - Suggests appropriate test/build/lint commands
  - User can accept, modify, or skip each
  - Writes WAI-Backpressure.yaml
- **Estimated Effort:** 6 hours

#### Lug 3.3 [Lug: a683997d]: Implement `wai check` Command
- **Type:** feature
- **Priority:** 1 (high)
- **Deps:** [3.1]
- **Idempotent:** false
- **Dep Reason:** Config must exist before running checks
- **Description:** Run all configured backpressure commands and report results. This is what agents call to self-verify.
- **Acceptance Criteria:**
  - Runs commands in order: typecheck → lint → build → test
  - Stops on first failure if on_failure=block
  - Returns structured results with pass/fail + output
  - `--json` flag for agents
- **Estimated Effort:** 4 hours

#### Lug 3.4 [Lug: 49f3a260]: Add Backpressure Signal Type
- **Type:** task
- **Priority:** 2 (medium)
- **Idempotent:** true
- **Description:** Add `backpressure_failure` signal type to WAI-Signals.jsonl for logging when automated checks fail.
- **Acceptance Criteria:**
  - Signal includes: check type, command, error output, timestamp
  - Hub can aggregate backpressure failures across Spokes
- **Estimated Effort:** 2 hours

#### Lug 3.5 [Lug: 164164f6]: Integrate with Closeout Flow
- **Type:** task
- **Priority:** 2 (medium)
- **Deps:** [3.3]
- **Idempotent:** false
- **Dep Reason:** Check command must work before integrating
- **Description:** Run `wai check` automatically during `'Closeout'` command. Block closeout if critical checks fail.
- **Acceptance Criteria:**
  - Closeout runs backpressure checks
  - Failures logged as signals
  - Option to force closeout despite failures
- **Estimated Effort:** 2 hours

#### Lug 3.6: Implement Automatic Task Escalation logic
- **Type:** task
- **Priority:** 2 (medium)
- **Deps:** [3.3]
- **Idempotent:** true
- **Description:** Define policy for when backpressure blocks repeatedly (e.g. >5 failures or >timeout). Reassign to human or senior agent.
- **Acceptance Criteria:**
  - Policy defined in WAI-Policies.json
  - Escalation logic triggered by `wai check` or Hub
- **Estimated Effort:** 3 hours

---

### Epic 4: Feature Specs Directory

**Goal:** Track feature-scoped work with persistent specs that support future development and testing

**Background:** Google Conductor introduced the concept of persistent context files per feature. This helps future agents (and humans) understand *why* something was built, not just what.

**Reference:** Google Conductor / Gemini CLI (December 2025)

#### Lug 4.1 [Lug: 5ff777a3]: Define WAI-Features/ Structure
- **Type:** task
- **Priority:** 2 (medium)
- **Idempotent:** true
- **Description:** Document directory structure and file purposes for WAI-Features/.
- **Acceptance Criteria:**
  - Structure: WAI-Features/{feature-name}/SPEC.md, PLAN.md, TEST-CASES.md
  - Each file type has clear purpose
  - _template/ directory with starter files
- **Estimated Effort:** 2 hours

#### Lug 4.2 [Lug: ccbfd191]: Create SPEC.md Template
- **Type:** task
- **Priority:** 2 (medium)
- **Idempotent:** true
- **Description:** Create template for feature specification document.
- **Acceptance Criteria:**
  - Sections: Purpose, Expected Behavior, Boundaries (in/out scope), Dependencies, Test Scenarios
  - Status field: planning | implementing | complete | deprecated
  - Links to related Lugs
- **Estimated Effort:** 1 hour

#### Lug 4.3 [Lug: c70e1a99]: Create PLAN.md Template
- **Type:** task
- **Priority:** 2 (medium)
- **Idempotent:** true
- **Description:** Create template for implementation plan (Conductor-style).
- **Acceptance Criteria:**
  - Sections: Phases, Tasks per phase, Files to modify, Checkpoints
  - Progress tracking (checkbox style)
  - Links to Lugs for each task
- **Estimated Effort:** 1 hour

#### Lug 4.4 [Lug: be4493b4]: Create TEST-CASES.md Template
- **Type:** task
- **Priority:** 2 (medium)
- **Idempotent:** true
- **Description:** Create template for test scenarios document.
- **Acceptance Criteria:**
  - Format: Given/When/Then or equivalent
  - Categories: Happy path, Edge cases, Error handling
  - Links to backpressure config for automated tests
- **Estimated Effort:** 1 hour

#### Lug 4.5 [Lug: 43d42cd0]: Implement `wai feature` CLI Commands
- **Type:** feature
- **Priority:** 3 (low)
- **Deps:** [4.1, 4.2, 4.3, 4.4]
- **Idempotent:** false
- **Dep Reason:** Templates must exist before CLI can use them
- **Description:** Add CLI commands: `wai feature new`, `wai feature list`, `wai feature status`
- **Acceptance Criteria:**
  - `new` creates directory from templates
  - `list` shows all features with status
  - `status` updates SPEC.md status field
- **Estimated Effort:** 4 hours

---

### Epic 5: Multi-Agent Foundation

**Goal:** Prepare WAI Hub to serve as the shared brain for agent colonies

**Background:** Steve Yegge's Gas Town vision is multi-agent orchestration. WAI Hub is perfectly positioned to be the shared memory layer.

**Reference:** 
- https://steve-yegge.medium.com/the-future-of-coding-agents-e9451a84207c
- https://github.com/steveyegge/beads

#### Lug 5.1 [Lug: 6856bff0]: Add Full Session Context Tracking ("The Guest Book")
- **Type:** task
- **Priority:** 2 (medium)
- **Idempotent:** true
- **Description:** Enhance session tracking to serve as a project "Guest Book". Every interaction (even bootstrap) leaves a signature.
- **Acceptance Criteria:**
  - Fields: `agent_id`, `role`, `tool` (cursor/claude), `device` (wsl/mac)
  - `session_url`: Link back to the chat/session source (if available)
  - `alignment_score`: Snapshot of environment health at start
  - Logged in `WAI-Session-Log.jsonl` immediately upon instantiation
- **Estimated Effort:** 2 hours

#### Lug 5.2 [Lug: 5736a97f]: Document Colony Architecture
- **Type:** task
- **Priority:** 2 (medium)
- **Idempotent:** true
- **Description:** Create documentation explaining how WAI Hub serves multi-agent setups.
- **Acceptance Criteria:**
  - Explains Hub as "village brain"
  - Documents agent roles and coordination patterns
  - Provides example multi-agent workflow
- **Estimated Effort:** 3 hours

#### Lug 5.3 [Lug: 8e6bf85b]: Design Hub Ready-Work Queue
- **Type:** task
- **Priority:** 3 (low)
- **Idempotent:** true
- **Description:** Design how Hub could distribute ready Lugs to multiple agents across Spokes.
- **Acceptance Criteria:**
  - Queue semantics (FIFO, priority-based, etc.)
  - Locking/claiming mechanism
  - Cross-Spoke coordination
- **Estimated Effort:** 4 hours (design only)

#### Lug 5.4 [Lug: a1efd21d]: Research Gas Town Integration
- **Type:** task
- **Priority:** 3 (low)
- **Idempotent:** true
- **Description:** Investigate how Gas Town works and document integration points where WAI could serve as foundation.
- **Reference:** Gas Town launch (January 2026)
- **Acceptance Criteria:**
  - Understand Gas Town architecture
  - Identify where WAI provides value
  - Document potential integration approach
- **Estimated Effort:** 4 hours

#### Lug 5.5: Implement `wai colony` TUI
- **Type:** feature
- **Priority:** 3 (low)
- **Idempotent:** true
- **Description:** Visual dashboard (like htop) for active agents, showing ID, current Lug, status (Thinking/Coding), and heartbeat.
- **Acceptance Criteria:**
  - TUI using textual/rich
  - Real-time updates from Hub state
- **Estimated Effort:** 6 hours

#### Lug 5.6: Implement Failure-Driven Learning Prompts
- **Type:** feature
- **Priority:** 2 (medium)
- **Idempotent:** true
- **Description:** When a Lug is fixed after failure, prompt agent to extract "Lesson Learned" to Hub immediately.
- **Acceptance Criteria:**
  - Detected 'check' failure followed by 'pass'
  - Trigger `wai teach` or specific prompt
- **Estimated Effort:** 4 hours

#### Lug 5.7: Implement Hub Research Agent
- **Type:** feature
- **Priority:** 1 (high)
- **Idempotent:** true
- **Description:** "The Researcher." A function that generates prompts to query the internet for tool updates, best practices, and new patterns, then summarizes them for the Hub.
- **Acceptance Criteria:**
  - `wai hub research <topic>` command
  - Generates optimized search prompt (e.g., "Google Antigravity updates since June 2025")
  - Ingests results into `Hub/learnings/external/`
  - Updates `Hub/registry/tools.json` with new capabilities
- **Estimated Effort:** 4 hours

---

### Epic 6: System Sketch Integration

**Goal:** Ensure complex implementations are preceded by intentional design

**Background:** The Focused Chaos article identified "accidental architecture" as the main risk of vibe coding. A system sketch forces the right questions before AI answers in code.

**Reference:** https://www.focusedchaos.co/p/vibe-coding-without-system-design-is-a-trap

#### Lug 6.1 [Lug: db4cd8dc]: Add System Sketch to WAI-Guide.md Template
- **Type:** task
- **Priority:** 1 (high)
- **Idempotent:** true
- **Description:** Add System Sketch section to WAI-Guide.md template with the 5 critical questions.
- **Acceptance Criteria:**
  - Section header: "## System Sketch"
  - Questions: Change likelihood, DRY, Source of truth, Breakage impact, Testability
  - Instructions for when to complete (before complex implementations)
- **Estimated Effort:** 1 hour

#### Lug 6.2 [Lug: 2be01cf5]: Integrate Questions into ADAPTIVE Workflow
- **Type:** task
- **Priority:** 2 (medium)
- **Deps:** [6.1]
- **Idempotent:** false
- **Dep Reason:** Template must have section before workflow references it
- **Description:** Update ADAPTIVE workflow gates to reference System Sketch questions during Planning phase.
- **Acceptance Criteria:**
  - Planning gate prompts for sketch if not complete
  - Complex tasks (multi-file OR >6 steps) require sketch
  - Simple tasks skip sketch
- **Estimated Effort:** 2 hours

---

## Part 6: Priority Matrix

### NOW (Next 2 Weeks)

| Lug ID | Title | Epic | Priority | Effort |
|--------|-------|------|----------|--------|
| 1.1 | Define WAI-Lugs.jsonl Schema | Lug System | P1 | 2h |
| 1.2 | Implement `wai lug` CLI Commands | Lug System | P1 | 8h |
| 1.3 | Implement `wai ready` Command | Lug System | P1 | 4h |
| 2.1 | Define IDE Optimization Checklist | IDE Optimization | P1 | 2h |
| 2.5 | Generate copilot-instructions.md | IDE Optimization | P1 | 1h |
| 3.1 | Define WAI-Backpressure.yaml Schema | Backpressure | P1 | 2h |
| 6.1 | Add System Sketch to WAI-Guide.md | System Sketch | P1 | 1h |

**Total NOW effort:** ~20 hours

### SOON (Month 1)

| Lug ID | Title | Epic | Priority | Effort |
|--------|-------|------|----------|--------|
| 1.4 | Migrate Existing Backlogs | Lug System | P2 | 4h |
| 1.5 | Update WAI-Guide.md for Lugs | Lug System | P2 | 2h |
| 2.2 | Implement `wai align` Command | IDE Optimization | P1 | 6h |
| 2.3 | Implement Auto-Fix Prompts | IDE Optimization | P1 | 4h |
| 2.4 | Add Audit to Session Start | IDE Optimization | P2 | 2h |
| 3.2 | Backpressure Setup Wizard | Backpressure | P2 | 6h |
| 3.3 | Implement `wai check` Command | Backpressure | P1 | 4h |
| 3.4 | Add Backpressure Signal Type | Backpressure | P2 | 2h |
| 3.5 | Integrate with Closeout | Backpressure | P2 | 2h |
| 4.1-4.4 | Feature Specs Templates | Feature Specs | P2 | 5h |
| 5.1 | Add Full Session Context Tracking | Multi-Agent | P2 | 2h |
| 6.2 | Integrate Sketch into ADAPTIVE | System Sketch | P2 | 2h |

**Total SOON effort:** ~39 hours

### LATER (Quarter)

| Lug ID | Title | Epic | Priority | Effort |
|--------|-------|------|----------|--------|
| 4.5 | `wai feature` CLI Commands | Feature Specs | P3 | 4h |
| 5.2 | Document Colony Architecture | Multi-Agent | P2 | 3h |
| 5.3 | Design Hub Ready-Work Queue | Multi-Agent | P3 | 4h |
| 5.4 | Research Gas Town Integration | Multi-Agent | P3 | 4h |
| 7.1 | Session Analytics | Analytics | P3 | 4h |
| 7.2 | Decision Replay | Analytics | P3 | 4h |
| 8.1 | Browser Interface Prototype | Interfaces | P2 | 10h |
| 8.2 | IDE Interface Prototype | Interfaces | P2 | 8h |

**Total LATER effort:** ~45 hours

---

## Part 7: Success Metrics

### Lug System Success
- [ ] All work tracked in single WAI-Lugs.jsonl file
- [ ] `wai ready` returns correct next work 100% of time
- [ ] Agents can create/update/close Lugs via CLI

### IDE Optimization Success
- [ ] Session start checks all integration files
- [ ] Missing files auto-created with user confirmation
- [ ] Zero "partially configured" environments

### Backpressure Success
- [ ] Projects can define build/test/lint commands
- [ ] `wai check` runs all commands and reports results
- [ ] Closeout blocked when critical checks fail

### Feature Specs Success
- [ ] Features have persistent SPEC.md documents
- [ ] Future agents understand feature purpose from specs
- [ ] TEST-CASES.md drives test implementation

### Multi-Agent Success
- [ ] Agent sessions tracked with ID and role
- [ ] Hub documented as colony brain
- [ ] Integration path for Gas Town identified

---

## Part 8: Appendix

### A. WAI-Lugs.jsonl Example File

```jsonl
{"id":"lug-a3f8","type":"epic","title":"WAI Lug System Consolidation","status":"open","priority":1,"deps":[],"idempotent":true,"created":"2026-01-19T10:00:00Z","labels":["core","v2"]}
{"id":"lug-a3f8.1","type":"task","title":"Define WAI-Lugs.jsonl Schema","parent":"lug-a3f8","status":"ready","priority":1,"deps":[],"idempotent":true,"created":"2026-01-19T10:01:00Z"}
{"id":"lug-a3f8.2","type":"task","title":"Implement wai lug CLI Commands","parent":"lug-a3f8","status":"ready","priority":1,"deps":[],"idempotent":true,"created":"2026-01-19T10:02:00Z"}
{"id":"lug-a3f8.3","type":"task","title":"Implement wai ready Command","parent":"lug-a3f8","status":"ready","priority":1,"deps":[],"idempotent":true,"created":"2026-01-19T10:03:00Z"}
{"id":"lug-a3f8.4","type":"task","title":"Migrate Existing Backlogs","parent":"lug-a3f8","status":"blocked","priority":2,"deps":["lug-a3f8.1"],"idempotent":false,"dep_reason":"Schema must be finalized before migration script can convert to it","created":"2026-01-19T10:04:00Z"}
{"id":"lug-a3f8.5","type":"task","title":"Update WAI-Guide.md for Lugs","parent":"lug-a3f8","status":"blocked","priority":2,"deps":["lug-a3f8.1"],"idempotent":false,"dep_reason":"Schema must be finalized before documenting in guide","created":"2026-01-19T10:05:00Z"}
```

### B. WAI-Backpressure.yaml Example

```yaml
# WAI Backpressure Configuration
# Defines automated feedback loops for agent self-verification

version: "1.0"

typecheck:
  command: "npx tsc --noEmit"
  on_failure: "warn"
  timeout: 60

lint:
  command: "npm run lint"
  on_failure: "warn"
  timeout: 30

build:
  command: "npm run build"
  on_failure: "block"
  timeout: 120

test:
  command: "npm test"
  on_failure: "signal"
  timeout: 300

# Custom checks
checks:
  - name: "security-audit"
    command: "npm audit --production"
    on_failure: "warn"
    
  - name: "bundle-size"
    command: "npx bundlesize"
    on_failure: "warn"
```

### C. WAI-Features/SPEC.md Template

```markdown
# Feature: [Feature Name]

**Status:** planning | implementing | complete | deprecated  
**Created:** YYYY-MM-DD  
**Last Updated:** YYYY-MM-DD  
**Related Lugs:** lug-xxxx, lug-yyyy

## Purpose

_Why does this feature exist? What problem does it solve?_

## Expected Behavior

_What should this feature do? User stories or acceptance criteria._

### User Stories

1. As a [user type], I want to [action] so that [benefit]
2. ...

### Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Boundaries

### In Scope
- Item 1
- Item 2

### Out of Scope
- Item 1 (reason)
- Item 2 (reason)

## Dependencies

### Requires (blocks this feature)
- [Feature/Lug]: reason

### Blocks (this feature blocks)
- [Feature/Lug]: reason

## System Sketch

### What is likely to change?
_List configurable values, likely pivots_

### Source of Truth
_Where does data come from/go?_

### Breakage Impact
_What breaks if this changes?_

### Testability
_How will this be tested?_

## Test Scenarios

_Link to TEST-CASES.md or summarize key scenarios_

See: [TEST-CASES.md](./TEST-CASES.md)
```

### D. Reference URLs Summary

```
# Primary Sources
https://github.com/wheelwright-ai/framework
https://github.com/steveyegge/beads
https://steve-yegge.medium.com/the-future-of-coding-agents-e9451a84207c
https://banay.me/dont-waste-your-backpressure/
https://www.focusedchaos.co/p/vibe-coding-without-system-design-is-a-trap
https://www.youtube.com/live/IdPtTBbYOtw?t=93s
https://www.youtube.com/shorts/T2bd1kGEISo
https://www.youtube.com/watch?v=yMJcHcCbgi4
https://www.youtube.com/watch?v=KcOQC_yJ5oM

# Secondary Sources
https://www.edgartools.io/beads-and-the-future-of-programming/
```

---

**Document Status:** Ready for Lug conversion  
**Next Action:** AI agent should parse Part 5 (Detailed Action Plans) and create corresponding Lugs in WAI-Lugs.jsonl

---

*"It takes a village. WAI Hub is the brain your agent colony shares."*

# WAI Skill Contract Specification

**Version:** 1.1.0
**Date:** 2026-02-11
**Status:** Foundation Spec — Architectural North Star
**Revision:** Added use_cases requirement, integration-check Skill, migration YAML pattern for upgrades

---

## Philosophy

Skills are WAI's universal behavior primitive. They are **executable capabilities** — not documentation, not suggestions, not prompts. A Skill declares what it does, when it fires, what model it needs, what it's allowed to touch, and what it produces.

Skills are the agents in the agent colony. Each Skill is a sub-agent with a defined scope, a cost profile, and an output contract. The main coding agent is itself just a Skill — the most expensive one, with the broadest write access.

**Core Principles:**

- **Declarative:** A Skill describes its contract; the runtime decides when and how to execute it
- **Scoped:** Every Skill declares exactly what it reads and what it writes — nothing else
- **Testable:** Every Skill can include its own test suite to verify correct behavior
- **Composable:** Skills can depend on other Skills and chain outputs
- **Inheritable:** Framework defines base Skills → Hub refines → Spoke overrides

---

## Skill Types

| Type | Purpose | Model Tier | Write Access |
|------|---------|------------|--------------|
| `reviewer` | Analyzes code/content, produces diagnosis Lugs | lightweight | Lugs only |
| `watcher` | Monitors state changes, produces observation Lugs | lightweight | Lugs only |
| `guardian` | Enforces policies, blocks unsafe actions | standard | Lugs + can block operations |
| `worker` | Executes implementation tasks | advanced | Code + Lugs |
| `advisor` | Evaluates BRIEF alignment, suggests amendments | standard | Lugs only |
| `orchestrator` | Reconciles sub-agent output, builds plans | advanced | Lugs + plans |

**Key distinction:** Reviewers, watchers, and advisors are cheap read-mostly agents. Workers and orchestrators are expensive write-capable agents. Guardians sit in between — they read broadly and can veto.

---

## Skill Contract Schema

### Identity

```yaml
skill: security-review
version: 1.2.0
type: reviewer
description: >
  Scans codebase for OWASP Top 10 vulnerabilities, 
  dependency version risks, and hardcoded credentials.
  Produces diagnosis and prescription Lugs.
```

### Model Requirements

```yaml
model:
  tier: lightweight                # lightweight | standard | advanced
  min_context: 32000               # Minimum context window needed (tokens)
  capabilities:                    # Required model capabilities
    - code_analysis
  notes: >
    Lightweight model sufficient for pattern matching against known 
    vulnerability signatures. Does not need advanced reasoning.
```

**Model tier guidance:**

| Tier | Use For | Example Models |
|------|---------|---------------|
| `lightweight` | Pattern matching, checklist verification, simple analysis | Haiku-class |
| `standard` | Nuanced evaluation, multi-factor analysis, policy interpretation | Sonnet-class |
| `advanced` | Complex reasoning, plan reconciliation, implementation, judgment calls | Opus-class |

**Multi-model diversification benefit:** Running different Skills at different model tiers provides implicit ensemble validation. Different architectures catch different blind spots. The orchestrator (advanced tier) reconciles potentially contradictory findings, producing higher-confidence outcomes than any single model.

### Trigger Configuration

```yaml
trigger:
  event: on_load                   # When this Skill fires
  frequency: per_session           # How often within a session
  priority: 2                      # Execution order (1 = first)
  conditions:                      # Optional conditions to evaluate before firing
    - "files_changed: src/**"
    - "last_run_age: > 24h"
  can_be_skipped: false            # Whether the user/BRIEF can disable this
```

**Trigger events:**

| Event | When It Fires |
|-------|--------------|
| `on_load` | Spoke/Hub wakeup sequence |
| `on_commit` | After a git commit |
| `on_content_change` | After source files are modified |
| `on_lug_created` | When a new Lug appears (filtered by type/impact) |
| `on_schedule` | Time-based (daily, weekly) — checked on load |
| `on_demand` | Only when explicitly requested by conductor or another Skill |
| `pre_refactor` | Before any structural file changes |

**Frequency options:**

| Frequency | Meaning |
|-----------|---------|
| `per_session` | Once per session load |
| `per_change` | Every qualifying trigger event |
| `periodic` | Based on time elapsed since last run (uses `last_run_age` condition) |
| `once` | Run once, then mark complete |

### Scope & Permissions

```yaml
scope:
  reads:
    - "src/**"                     # Can read source code
    - "tests/**"                   # Can read test files
    - "WAI-Lugs.jsonl"             # Can read current Lugs
    - "hub/WAI-Lugs.jsonl"         # Can read Hub Lugs (read-only)
    - "BRIEF.md"                   # Can read current BRIEF
  writes:
    - "WAI-Lugs.jsonl"             # Can write Lugs
  never:
    - "src/**"                     # CANNOT modify source code
    - ".env*"                      # CANNOT access environment files
    - "hub/**"                     # CANNOT write to Hub (except via intake)
  intake_access: true              # Can write to hub/intake/
```

**Scope rules:**

1. A Skill MUST declare everything it reads and writes
2. `never` overrides `writes` — explicit denial takes precedence
3. Reviewer and watcher types can only write to `WAI-Lugs.jsonl` and `hub/intake/`
4. Only `worker` type Skills can write to source code
5. `guardian` type Skills can write to Lugs AND set blocking flags
6. If a Skill attempts to write outside its declared scope, the action is logged as a violation Lug

### Prerequisites

```yaml
prerequisites:
  tools:
    - name: "git"
      check: "git --version"
      required: true
    - name: "npm"
      check: "npm --version"
      required: false
  skills:
    - "safe-refactor"              # This Skill depends on safe-refactor being available
  files:
    - "package.json"               # Project must have this file
  state:
    - "git_clean: true"            # Working directory must be clean
```

**Prerequisite checking:**

On load, each Skill's prerequisites are verified. Status is reported:

> "4 Skills loaded. 3 ready. `deploy` blocked: missing AWS credentials."

If a prerequisite is `required: true` and missing, the Skill is marked `blocked` and a Lug is created explaining what's needed. If `required: false`, the Skill runs with reduced capability.

### Output Contract

```yaml
outputs:
  lugs:
    types:
      - "diagnosis"
      - "prescription"
    impact_range: [5, 10]          # Expected impact range for Lugs this Skill creates
  session_log:
    required: true                 # Must write execution summary to session log
    fields:
      - execution_status
      - execution_duration_ms
      - execution_summary
      - findings_count
```

**Output contract enforcement:**

Every Skill execution must produce:
1. At minimum: a session log entry recording that it ran, how long, success/failure, brief summary
2. If findings exist: properly formed Lugs with all required fields
3. If no findings: a session log entry confirming clean check

This ensures the audit trail is complete. No Skill runs silently.

### Inheritance & Override

```yaml
inheritance:
  base: "framework://skills/security-review@1.0.0"    # Framework template
  hub_overlay: "hub://skills/security-review-policy"    # Hub-level additions
  local_overrides:
    - "Also check for PII exposure in API responses"    # Spoke-specific additions
    - "Ignore false positives in test fixtures"
  locked_by: "enterprise"          # Who can modify: enterprise | hub | spoke | none
```

**Inheritance cascade:**

```
Framework template (base behavior, default rules)
  ↓ Hub overlay adds (wheel-wide policies, additional checks)
    ↓ Spoke override refines (project-specific context, local exceptions)
```

**Rules:**

- Each level can ADD checks, rules, and scope
- Each level can NARROW scope (more restrictive)
- Lower levels CANNOT remove higher-level mandatory items
- `locked_by: enterprise` means enterprise-level rules cannot be overridden at Hub or spoke
- `locked_by: hub` means Hub additions cannot be overridden at spoke
- `locked_by: spoke` means the spoke controls everything (default for custom Skills)

### Tests

```yaml
tests:
  unit:
    - name: "detects_sql_injection"
      input: "fixtures/vulnerable-auth.js"
      expected_output:
        lug_type: "diagnosis"
        severity: "critical"
        category: "security"
    - name: "clean_code_no_findings"
      input: "fixtures/safe-auth.js"
      expected_output:
        findings: 0
  integration:
    - name: "full_scan_produces_session_log"
      expected: "session log entry with execution_status"
```

**Testing philosophy:**

Skills must be testable in isolation. Test fixtures provide known inputs, and the Skill's output (Lugs) is validated against expected patterns. This ensures that Skill updates don't introduce regressions and that enterprise compliance Skills actually catch what they claim to catch.

### Use Cases (Required)

Every Skill MUST include a `use_cases` section. Use cases serve triple duty: documentation for users, context for agents deciding whether to invoke the Skill, and institutional memory about WHY the Skill exists.

```yaml
use_cases:
  - scenario: "Agent is about to refactor the auth module"
    what_happens: "safe-refactor fires, commits current state as checkpoint"
    why_it_matters: "If refactoring breaks something, one git revert recovers"
    user_trigger: "Automatic — fires on pre_refactor event"
    
  - scenario: "Hub folder was destroyed by a rogue agent"
    what_happens: "Would have been prevented — checkpoint exists to revert to"
    why_it_matters: "This actually happened. This Skill exists because of it."
    origin: "WAI v2 architectural session, 2026-02-11"
    
  - scenario: "Developer wants to understand what this Skill does"
    what_happens: "Reads use_cases section, immediately understands value"
    why_it_matters: "We don't want to forget why we needed the Skill in the first place"
```

**Use case fields:**

| Field | Required | Description |
|-------|----------|-------------|
| scenario | yes | Plain English description of the situation |
| what_happens | yes | What the Skill does in this scenario |
| why_it_matters | yes | Why this matters — the human impact |
| user_trigger | no | How the user/agent triggers this (auto vs manual) |
| origin | no | Where this use case came from (session, incident, etc.) |

### Upgrade Tracking

When a Skill is updated (new version from framework), the framework-updater Skill follows the migration YAML pattern:

1. Creates a local `WAI-UPGRADE.yaml` tracking the update phases
2. Diffs current Skill against new version
3. Categorizes changes: safe (auto-apply), review needed, breaking
4. Applies safe changes, creates Lugs for the rest
5. On completion, converts WAI-UPGRADE.yaml into a Lug and deletes the file

This reuses the same pattern at every scale — framework migrations, node upgrades, and individual Skill updates all follow the same state tracking approach.

---

## Built-In Skills

### safe-refactor (Guardian)

```yaml
skill: safe-refactor
version: 1.0.0
type: guardian
description: >
  Ensures git state is clean and committed before any structural changes.
  Fires before refactoring operations. Creates a named commit as a restore point.
trigger:
  event: pre_refactor
  can_be_skipped: false
model:
  tier: lightweight
scope:
  reads: [".git/**"]
  writes: ["WAI-Lugs.jsonl"]
  never: ["src/**"]
prerequisites:
  tools:
    - name: "git"
      check: "git --version"
      required: true
  state:
    - "git_initialized: true"
actions:
  - check_git_clean
  - commit_current_state_with_message: "WAI safe-refactor checkpoint: {context}"
  - create_observation_lug: "Checkpoint created at {commit_hash}"
use_cases:
  - scenario: "Agent is about to refactor the auth module"
    what_happens: "safe-refactor fires, commits current state as checkpoint"
    why_it_matters: "If refactoring breaks something, one git revert recovers"
    user_trigger: "Automatic — fires on pre_refactor event"
  - scenario: "Hub folder was destroyed by a rogue agent with no recovery point"
    what_happens: "Would have been prevented — checkpoint exists to revert to"
    why_it_matters: "This actually happened on 2026-02-10. This Skill exists because of it."
    origin: "WAI v2 architectural session, 2026-02-11"
```

### qc-check (Reviewer)

```yaml
skill: qc-check
version: 1.0.0
type: reviewer
description: >
  Runs the application, executes test suite, verifies startup.
  Produces diagnosis Lugs for failures. Does not ask the user to debug —
  diagnoses and prescribes directly.
trigger:
  event: on_content_change
  frequency: per_change
model:
  tier: lightweight
scope:
  reads: ["src/**", "tests/**", "package.json", "WAI-Lugs.jsonl"]
  writes: ["WAI-Lugs.jsonl"]
  never: ["src/**"]
actions:
  - run_app_startup_check
  - run_test_suite
  - compare_coverage_to_brief_threshold
  - for_each_failure: create_diagnosis_and_prescription_lug
use_cases:
  - scenario: "Agent writes code and the application doesn't start"
    what_happens: "qc-check diagnoses the startup failure, writes prescription Lug, routes to main agent"
    why_it_matters: "The user never sees the failure. Agents don't ask the user to debug mechanical problems."
    origin: "Mario's complaint about agents giving prompts to test while the app won't even start"
  - scenario: "Test coverage drops below BRIEF threshold after new feature"
    what_happens: "qc-check creates diagnosis Lug noting coverage gap with specific files missing tests"
    why_it_matters: "Coverage debt is caught immediately, not discovered weeks later"
```

### hub-watcher (Watcher)

```yaml
skill: hub-watcher
version: 1.0.0
type: watcher
description: >
  Checks Hub for unprocessed signals, framework updates, and
  pending intake acknowledgments. Surfaces relevant items as local Lugs.
trigger:
  event: on_load
  frequency: per_session
  priority: 1                      # Runs first in wakeup sequence
model:
  tier: lightweight
scope:
  reads: ["hub/WAI-Lugs.jsonl", "hub/health.yaml", "hub/intake/"]
  writes: ["WAI-Lugs.jsonl"]
  intake_access: false             # This skill reads from Hub, doesn't write to intake
actions:
  - read_hub_lugs_since_cursor
  - check_outbound_pending_acknowledgments
  - check_framework_version_cascade
  - create_local_lugs_for_relevant_findings
  - update_manifest_hub_lug_cursor
use_cases:
  - scenario: "Framework published a new template version while spoke was idle"
    what_happens: "hub-watcher detects update Lug in Hub, creates local update Lug for framework-updater"
    why_it_matters: "Spoke stays current without manual checking"
  - scenario: "Spoke submitted a high-impact Lug to Hub intake 3 days ago, still unprocessed"
    what_happens: "hub-watcher detects pending outbound, surfaces to user: Hub needs attention"
    why_it_matters: "Call-and-response ensures nothing gets lost in transit"
```

### framework-updater (Worker)

```yaml
skill: framework-updater
version: 1.0.0
type: worker
description: >
  Applies framework template updates to spoke. Cascade checks:
  1) Hub Lug announcing update, 2) local framework folder,
  3) GitHub releases API. Categorizes changes as safe/review/breaking.
  Auto-applies safe changes, creates Lugs for the rest.
trigger:
  event: on_load
  frequency: periodic
  conditions:
    - "last_run_age: > 24h"
model:
  tier: standard
scope:
  reads: ["hub/WAI-Lugs.jsonl", "WAI-Manifest.yaml"]
  writes: ["WAI-Lugs.jsonl", "WAI-Manifest.yaml", "skills/**", "BRIEF.md"]
  never: ["src/**"]
prerequisites:
  skills: ["safe-refactor"]        # Must checkpoint before applying updates
actions:
  - cascade_version_check
  - diff_templates_against_current
  - categorize_changes: [safe, review, breaking]
  - auto_apply_safe_changes
  - create_lugs_for_review_and_breaking
  - update_manifest_template_versions
use_cases:
  - scenario: "Framework template v3 is available, spoke runs v2"
    what_happens: "Cascade check detects update, diffs templates, auto-applies non-breaking changes"
    why_it_matters: "Spokes stay current without manual ceremony. Safe changes just happen."
  - scenario: "Breaking template change requires spoke-level decisions"
    what_happens: "Creates Lug describing the breaking change, does NOT auto-apply, waits for conductor"
    why_it_matters: "Autonomy for safe changes, human judgment for risky ones"
  - scenario: "Spoke BRIEF pins to v2, v3 is available"
    what_happens: "Notes v3 available but respects pin policy. Creates observation Lug, does not update."
    why_it_matters: "Spokes can intentionally lag behind for stability"
```

### brief-advisor (Advisor)

```yaml
skill: brief-advisor
version: 1.0.0
type: advisor
description: >
  Reviews BRIEF against recent Lug patterns. Detects contradictions
  between stated policies and actual behavior. Suggests amendments
  based on recurring patterns. The apprenticeship engine.
trigger:
  event: on_load
  frequency: periodic
  conditions:
    - "last_run_age: > 72h"
    - "lugs_resolved_since_last_run: > 5"
model:
  tier: standard
scope:
  reads: ["BRIEF.md", "WAI-Lugs.jsonl", "WAI-Manifest.yaml"]
  writes: ["WAI-Lugs.jsonl"]
  never: ["BRIEF.md", "src/**"]   # Advisor suggests, never modifies BRIEF directly
actions:
  - compare_brief_policies_to_lug_patterns
  - detect_dismissed_diagnosis_patterns
  - detect_decision_pattern_shifts
  - suggest_brief_amendments_as_lugs
  - surface_contradictions_as_observation_lugs
use_cases:
  - scenario: "Conductor has dismissed 8 of last 10 security findings"
    what_happens: "brief-advisor surfaces: security reviewer may need calibration, or BRIEF policy needs updating"
    why_it_matters: "Either the Skill is too noisy or the conductor is ignoring real issues — both need attention"
  - scenario: "Conductor consistently overrides sub-agent recommendations in a specific area"
    what_happens: "brief-advisor detects the pattern, suggests BRIEF amendment to encode the preference"
    why_it_matters: "The system learns the conductor's judgment and stops asking about settled questions"
    origin: "Apprenticeship loop design, 2026-02-11"
  - scenario: "BRIEF states 80% coverage but coverage has been below 75% for 3 sessions"
    what_happens: "Surfaces contradiction: is the policy wrong, or is the coverage? Conductor decides."
    why_it_matters: "Honest pushback — the system holds you accountable to your own standards"
```

### session-observer (Watcher)

```yaml
skill: session-observer
version: 1.0.0
type: watcher
description: >
  Monitors session activity and records significant events as observation Lugs.
  On session close, produces a session synthesis Lug — the human-readable
  summary of what happened. Tracks patterns across sessions for the
  anticipation engine.
trigger:
  event: on_commit
  frequency: per_change
model:
  tier: lightweight
scope:
  reads: ["WAI-Lugs.jsonl", "WAI-Manifest.yaml", ".git/log"]
  writes: ["WAI-Lugs.jsonl"]
actions:
  - record_significant_events
  - on_session_close: synthesize_session_lug
  - detect_work_patterns_across_sessions
  - surface_anticipation_prompts
use_cases:
  - scenario: "Session ends and the conductor wants to know what happened"
    what_happens: "Session Lug synthesizes: Skills ran, findings made, Lugs created/resolved, commits made"
    why_it_matters: "Human comes back tomorrow and reads one paragraph to know the full story"
  - scenario: "Conductor has refactored after every 3rd feature addition for the last 5 sessions"
    what_happens: "Anticipation prompt: 'You've added 2 features since last refactor. Queue code health review?'"
    why_it_matters: "The system anticipates your patterns instead of waiting to be asked"
```

### file-audit (Reviewer)

```yaml
skill: file-audit
version: 1.0.0
type: reviewer
description: >
  Audits file structure against conventions. Detects sprawl —
  files outside expected locations, orphaned files not referenced
  by Lugs or Skills, unexpected file count growth.
trigger:
  event: on_load
  frequency: periodic
  conditions:
    - "last_run_age: > 7d"
model:
  tier: lightweight
scope:
  reads: ["**/*"]
  writes: ["WAI-Lugs.jsonl"]
  never: ["src/**", "hub/**"]
actions:
  - scan_file_structure
  - compare_against_conventions
  - detect_orphaned_files
  - measure_sprawl_metrics
  - create_diagnosis_lugs_for_violations
use_cases:
  - scenario: "AI agents have been creating files in non-standard locations"
    what_happens: "file-audit detects files outside convention, creates diagnosis Lugs"
    why_it_matters: "File sprawl makes projects unmaintainable and confuses future agents"
  - scenario: "Weekly health check on project structure"
    what_happens: "Runs periodically, reports sprawl metrics as observation Lug"
    why_it_matters: "You manage what you measure — sprawl caught early is easy to fix"
```

### integration-check (Guardian)

```yaml
skill: integration-check
version: 1.0.0
type: guardian
description: >
  Verifies and heals IDE integration files during wakeup.
  Checks that CLAUDE.md, .cursorrules, copilot-instructions.md
  exist and contain current generated composite briefings.
  Self-heals stale or missing files. Reports findings.
trigger:
  event: on_load
  frequency: per_session
  priority: 1
  can_be_skipped: false
model:
  tier: lightweight
scope:
  reads: ["CLAUDE.md", ".cursorrules", ".github/copilot-instructions.md",
          "WAI-Manifest.yaml", "BRIEF.md", "WAI-Guide.md"]
  writes: ["CLAUDE.md", ".cursorrules", ".github/copilot-instructions.md",
           "WAI-Lugs.jsonl"]
  never: ["src/**", "hub/**"]
prerequisites:
  files:
    - "WAI-Manifest.yaml"
    - "BRIEF.md"
actions:
  - check_ide_files_exist
  - check_ide_files_current: "Compare generator header timestamp against manifest"
  - regenerate_stale_files: "Only if file has WAI generator header — never overwrite hand-edited"
  - warn_unmanaged_files: "IDE file exists without generator header — alert, don't overwrite"
  - report_findings_to_session_log
checks:
  - id: claude-md
    perceive:
      look_at: "CLAUDE.md"
      current_state: "File may be missing, stale, or a thin pointer"
      success_state: "Contains generated composite briefing with current timestamp"
    execute:
      action: regenerate
      source: composite-briefing
      constraints:
        - "Never overwrite if content is hand-edited (check for generator header)"
    verify:
      check: "File exists AND contains '# Generated by wai wakeup' header"
  - id: cursorrules
    perceive:
      look_at: ".cursorrules"
      current_state: "File may be missing or stale"
      success_state: "Contains generated composite briefing"
    execute:
      action: regenerate
      source: composite-briefing
    verify:
      check: "File exists AND contains WAI generator header"
use_cases:
  - scenario: "Agent opens project for the first time after framework update"
    what_happens: "integration-check detects stale CLAUDE.md, regenerates with current briefing"
    why_it_matters: "Agent gets current context without manual wai wakeup run"
  - scenario: "Developer hand-edited CLAUDE.md with custom instructions"
    what_happens: "integration-check detects missing generator header, warns but does NOT overwrite"
    why_it_matters: "Respects human intent while flagging potential staleness"
    origin: "Wakeup improvement spec, 2026-02-10"
```

---

## Wakeup Sequence

The on_load wakeup is the critical orchestration moment. Here's the execution order:

```
1. [P1] hub-watcher        — Check for news from Hub and framework
2. [P1] safe-refactor      — Verify git state is clean  
3. [P2] framework-updater  — Apply any pending template updates
4. [P2] Load BRIEF, Lugs, manifest
5. [P3] All reviewer Skills — security, qc, file-audit, etc.
6. [P3] brief-advisor      — Check BRIEF alignment
7. [P4] orchestrator       — Reconcile all sub-agent Lugs into a plan
8. [P5] Present plan to conductor
```

**Priority groups execute in order. Within a group, Skills can run in parallel.**

If any guardian Skill (like safe-refactor) fails, the sequence halts and surfaces the issue. Reviewer failures produce Lugs but don't block the sequence.

The orchestrator is always last — it needs all sub-agent output before it can build a coherent plan.

---

## Sub-Agent Capability Detection

On load, the wakeup sequence checks:

1. What Skills are configured in this spoke's manifest?
2. Are prerequisites met for each Skill?
3. Are model tiers available for each Skill?
4. If sub-agent capabilities are limited (e.g., no API access for cheap models), fall back to sequential single-model execution, switching model tiers as Skills require

**Graceful degradation:**

- Full capability: parallel sub-agents at appropriate model tiers
- Limited capability: sequential execution, model switching per Skill
- Minimal capability: orchestrator runs all checks inline at its own tier (most expensive, but always works)

The system never fails to check — it adjusts HOW it checks based on available resources.

---

## Enterprise Compliance Layer

For enterprise environments, Skills can be mandated at the organization level:

```yaml
inheritance:
  locked_by: enterprise
  mandate: required                # required | recommended | optional
  audit_trail: true                # All executions logged for compliance
  minimum_frequency: per_session   # Must run at least this often
  escalation:
    on_critical_finding: "notify_cso_channel"
    on_skill_disabled: "block_and_alert"
```

**Enterprise flow:**

1. CSO defines mandatory Skill pack (security, compliance, license-check, etc.)
2. Skills are distributed through a controlled Hub
3. Spoke manifests report which mandatory Skills are active
4. Hub aggregates compliance Lugs across all projects
5. Dashboard query: "Show all critical security Lugs unresolved > 48 hours"

The developer isn't slowed down — Skills run automatically. The compliance team gets auditable evidence. The Lugs ARE the audit trail.

---

## Skill Development Lifecycle

```
1. Define contract (this YAML schema)
2. Write test fixtures
3. Implement Skill logic
4. Test in isolation (unit + integration)
5. Deploy to framework templates (for shared Skills)
6. Deploy to Hub (for wheel-wide Skills)
7. Deploy to spoke (for project-specific Skills)
8. Monitor calibration feedback from Lug resolutions
9. Refine based on dismissed/modified patterns
10. Version bump and repeat
```

**Self-improvement loop:**

Skills that consistently produce dismissed Lugs should detect their own noise level:

> "This Skill has had 8 of last 10 findings dismissed. Calibration review recommended."

This surfaces as an observation Lug to the brief-advisor, which may suggest threshold or scope adjustments. The Skill improves through the same Lug mechanism it uses for everything else.

---

## Appendix: Contract Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| skill | string | yes | Unique skill identifier |
| version | semver | yes | Skill version |
| type | enum | yes | reviewer, watcher, guardian, worker, advisor, orchestrator |
| description | string | yes | What this Skill does |
| model.tier | enum | yes | lightweight, standard, advanced |
| model.min_context | integer | no | Minimum context window (tokens) |
| model.capabilities | array | no | Required model capabilities |
| trigger.event | enum | yes | When this Skill fires |
| trigger.frequency | enum | yes | How often within a session |
| trigger.priority | integer | no | Execution order (1 = first) |
| trigger.conditions | array | no | Conditions to evaluate before firing |
| trigger.can_be_skipped | boolean | no | Whether this Skill can be disabled |
| scope.reads | array | yes | Paths this Skill can read |
| scope.writes | array | yes | Paths this Skill can write |
| scope.never | array | no | Explicitly denied paths |
| scope.intake_access | boolean | no | Can write to Hub intake |
| prerequisites.tools | array | no | Required CLI tools |
| prerequisites.skills | array | no | Required companion Skills |
| prerequisites.files | array | no | Required project files |
| prerequisites.state | array | no | Required state conditions |
| outputs.lugs.types | array | yes | Lug types this Skill produces |
| outputs.lugs.impact_range | array | no | Expected impact range |
| outputs.session_log.required | boolean | yes | Must write session log entry |
| inheritance.base | string | no | Framework template reference |
| inheritance.hub_overlay | string | no | Hub-level additions |
| inheritance.local_overrides | array | no | Spoke-level refinements |
| inheritance.locked_by | enum | no | enterprise, hub, spoke, none |
| tests.unit | array | no | Unit test definitions |
| tests.integration | array | no | Integration test definitions |
| use_cases | array | yes | Real scenarios explaining why this Skill exists and how to use it |
| use_cases[].scenario | string | yes | Plain English situation description |
| use_cases[].what_happens | string | yes | What the Skill does in this scenario |
| use_cases[].why_it_matters | string | yes | Human impact — why this matters |
| use_cases[].user_trigger | string | no | How triggered (automatic vs manual) |
| use_cases[].origin | string | no | Where this use case came from (session, incident) |

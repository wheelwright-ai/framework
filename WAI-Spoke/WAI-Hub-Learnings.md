# Hub Learnings - 2026-01-01

These patterns were distributed from the hub knowledge base.
Run closeout to integrate these into your WAI-Guide.md

## Architectural_Decision

### SCF to Wheelwright rebrand
Complete framework rebrand from Session Continuity Framework to Wheelwright. New wheel metaphor (hub=memory, spokes=capabilities, wheel=project). WWAI file naming convention. GitHub org wheelwright-ai. Domain wheelwright.ai.

*Impact: 10 | Source: framework-signals*

## Integration_Pattern

### Enforceable CLAUDE.md protocol with priority levels and state tracking
CRITICAL PATTERN for all AI tool integrations: CLAUDE.md must use PRIORITY LEVELS (0=blocking, 1=always-active, 2=optional), inline session start protocol (not delegate to other files), add session state tracking (protocol_completed flag in WWAI-State.json), include enforcement checklist with explicit MUST NOT rules, and provide exception for circular dependency when fixing CLAUDE.md itself. Without this structure, AI tools receive instructions as passive reminders rather than executable directives, causing protocol to never run. This pattern ensures automatic briefing and context loading on every session start.

*Impact: 10 | Source: framework-signals*

## Session_Continuity_Pattern

### JSONL conversation logging with closeout processing
Track every turn in .WAI/session-conversation.jsonl using append-only JSONL format. On closeout: load log line-by-line, extract insights (summary, key topics, files modified), move current_session → last_closeout in WAI-State.json, clear verbose log. CRITICAL: Hub learning cannot proceed until closeout complete and conversation log consumed/cleared. This enables session recovery from disruptions and intelligent session summaries. Use shipit command for closeout + git commit in one operation.

*Impact: 10 | Source: framework-signals*

## Naming_Convention

### Capitalized .WAI/ for pronounced readability
When folder or file names contain 'wai', capitalize to .WAI/ for pronounced readability (W-A-I as distinct letters). Makes WAI visually distinct from common word 'wai'. Applied to directory (.WAI/), CLI tool (WAI), and all documentation. WAI stands for 'Wheelwright AI' (one word, NOT 'Wheel Wright'). Tagline: 'This is the WAI' (Mandalorian reference).

*Impact: 8 | Source: framework-signals*

## Testing_Pattern

### Comprehensive unit test suite for bash hooks
Created test-session-start.sh with 26 tests covering: exit conditions, briefing generation, decision filtering, next actions, git integration, state updates, error handling. Uses isolated /tmp environment with fixtures. Setup/teardown pattern ensures clean state. Tests both happy paths and edge cases (missing files, minimal state). Run via ./WAI/hooks/test-session-start.sh. All tests must pass before deployment.

*Impact: 8 | Source: framework-signals*

## Quality_Policy

### Dual-layer testing: smoke tests + unit tests
CRITICAL POLICY for all projects: Maintain TWO test layers. (1) Smoke tests - Fast verification of integration points, run before commits, catches breaking changes quickly (framework: 40 tests, spoke: 37 tests). (2) Unit tests - Detailed component coverage with isolated fixtures, ensures reliability (26 tests for session-start hook). Both test suites expand as features are added. Smoke tests verify end-to-end flows, unit tests verify individual components. Run both before shipit. This dual approach caught 3 issues during implementation that would have been production bugs. Template both test suites in hub for reuse across all Wheelwright projects.

*Impact: 10 | Source: framework-signals*

## Optimization_Pattern

### Token Efficiency Protocols - ADAPTIVE workflow prevents 50-80% waste
CRITICAL OPTIMIZATION for all AI projects: Implemented ADAPTIVE workflow mode that automatically assesses task complexity and enforces multi-stage gates (Discussion → READY TO PLAN → PLAN ACCEPTED → Implementation) for complex tasks (multi-file OR >6 steps), while allowing YOLO autonomy for simple tasks. Includes: (1) Standardized plan template with Goal/Assumptions/Steps/Risks/Rollback, (2) Automatic checkpointing every 3-5 steps for large plans (>8 steps OR >5 files), (3) Context hygiene rules (never repeat >500 tokens, use file:line references, capacity warnings at 60%/80%/90%), (4) Compact command for context compression (auto-runs before closeout/shipit), (5) Fallback protocol for blocked implementations, (6) Task scoping guardrails for multi-feature requests, (7) Cross-platform templates (Cursor .cursorrules, VS Code settings.json, Generic AI-INSTRUCTIONS.md). Schema extensions in WAI-State.json: complexity_thresholds (multi_file: 2, step_count: 6, checkpoint_interval: 3), capacity_management (warning: 0.80, critical: 0.90). Smoke tests expanded to 101 total (52 framework, 49 spoke). This prevents premature implementation waste, the #1 token efficiency problem in long-running projects. Template for all Wheelwright hubs and spokes.

*Impact: 10 | Source: framework-signals*


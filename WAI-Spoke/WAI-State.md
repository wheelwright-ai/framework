# WAI-State.md
**Version:** 3.0.0
**Project:** Wheelwright Framework
**Repository:** https://github.com/wheelwright-ai/framework
**Purpose:** Strategic vision and project evolution tracking
**Audience:** Human + AI
**Managed by:** User (strategic vision) + Framework (evolution log)
**Last Updated:** 2026-02-01T02:30:00Z

---

# Wheelwright Framework - Strategic State

---

> **For Wheelwright Users (Fork/Clone Notice):**
>
> These are the wheel files for Wheelwright's own development - we eat our own dog food.
> When you fork or clone this repo, you have options:
> - **Keep as reference**: See how Wheelwright tracks itself as a living example
> - **Reset for your fork**: Run `WAI init --fresh` to start with your own context
> - **Build on it**: Your changes to `.WAI/` won't conflict with framework updates
>
> This is intentional - the framework's own development serves as documentation.

---

**Wheelwright Framework v1.0.0**
**Structure:** v1 (.WAI/ directory)
**Type:** Framework (Wheel project tracking its own development)
**Repository:** https://github.com/wheelwright-ai/framework
**Created by:** Mario Vaccari

*"We aren't reinventing the wheel - we're evolving it faster than one person ever could."*

*This project uses Wheelwright to maintain perfect context across AI sessions. Wheelwright transforms AI from order-taker to informed, responsible project partner.*

---

## Project Foundation

### Identity
- **Type:** Framework
- **One-liner:** Build AI wheels that roll forward forever - universal context persistence for any knowledge work
- **Success looks like:** Any AI assistant can pick up any project with full context, and learnings flow across projects automatically via the hub

### Boundaries

**In Scope:**
- Core framework code (WAI CLI, Python modules)
- Wheel templates and schemas (WAI-State.json, WAI-State.md, WAI-Guide.md)
- Hub creation and management tooling
- Spoke loader architecture and built-in spokes
- Documentation for Wheelwright usage
- Cross-project learning protocols
- Migration tools (SCF to Wheelwright)

**Out of Scope:**
- Hub storage (user creates separately at ~/wheelwright-hub)
- User's personal data/preferences
- IDE extensions (wheelwright-ai/extension-vscode)
- Browser extensions (wheelwright-ai/extension-browser)
- Website (wheelwright-ai/website)
- Project-specific implementations

**Constraints:**
- AI-agnostic: Must work with Claude, GPT, Copilot, Gemini, etc.
- Environment-agnostic: No lock-in to specific tools
- Lightweight: Minimal dependencies, easy adoption
- Non-coding support: Works for research, writing, design - not just code
- Backwards compatible: Migration path from SCF

### Approach
- **Stack:** Python 3.9+, JSON/JSONL, Markdown
- **Workflow:** Dogfooding - Wheelwright tracks its own development
- **AI Collaboration:** ADAPTIVE Mode - Autonomous for small tasks, planning for significant features

---

## Core Philosophy: AI as Autonomous Partner with Appropriate Oversight

**ADAPTIVE MODE ACTIVE** - Balanced collaboration philosophy:

> **Small tasks**: AI proceeds autonomously with confidence
> **Significant features**: Discussion → Plan → Approval → Implement
>
> Best of both worlds - velocity on routine work, thoughtful planning on complexity.

### Collaboration Model
1. **Small tasks/fixes** - Proceed autonomously (YOLO style)
2. **Significant features** - Propose plan, get approval, then implement
3. **Complete foundation first** - Required for all work
4. **When in doubt** - Propose a plan first

### Complexity Triggers
Planning gate activates when:
- Changes affect 2+ files, OR
- Implementation requires 6+ steps, OR
- Architectural decisions needed, OR
- User explicitly requests planning

### Evolution, Not Chaos
ADAPTIVE mode maintains intentionality:
- AI respects project foundation and boundaries
- AI makes reasoned decisions about scope evolution
- AI logs all significant changes in `evolution_log`
- AI proposes plans for complex work before implementing

---

## Architecture: Framework + Hub + Wheels

```
┌─────────────────────────────────────────────────────────────┐
│  Wheelwright Framework (this repo)                          │
│  - Core code (WAI CLI, Python modules)                     │
│  - Wheel templates (WAI-State.json, WAI-State.md, etc.)   │
│  - Spoke loader + built-in spokes                           │
│  - Hub creation tooling                                     │
│  - Documentation                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ User runs: WAI hub create
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  User's Hub (~/wheelwright-hub/ or custom location)         │
│  - hub-profile.json (personal preferences)                  │
│  - .WAI-registry/ (discovered projects)                    │
│  - learnings/ (cross-project patterns)                      │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
      ┌──────────┐      ┌──────────┐      ┌──────────┐
      │ Project A│      │ Project B│      │ Project C│
      │  (wheel) │      │  (wheel) │      │  (wheel) │
      │  .WAI/  │      │  .WAI/  │      │  .WAI/  │
      └──────────┘      └──────────┘      └──────────┘
```

**The Wheel Metaphor:**
- **Hub** = Central memory and consolidated knowledge
- **Spokes** = Specialized capabilities (meta-consultation, code-review, etc.)
- **Wheel** = A project with context that rolls forward
- **Rolling** = Each session moves forward, never losing ground

---

## Current Focus

### Just Completed (2026-02-02)
- **Hub Created** - ~/wheelwright-hub initialized with structure, profile, and metadata
- **Hub Registration Ready** - Ready for spoke discovery and registration via `wai hub scan`
- **Teach Command Fixed** - Fixed exception handling in multi-spoke teaching loop
- **Teaching Workflow Active** - All 19 spokes received framework templates successfully

### Previously Completed (2026-01-31)
- **AGENTS.md Living Document** - AGENTS.md now evolves with the project, not just substituting state
- **Init**: Creates AGENTS.md on init, APPENDS intelligently on re-init (preserves existing context)
- **Closeout**: Generates "Session Focus (Must Continue)" section that surfaces incomplete work
- **Detection**: Identifies multi-stage items (stage/phase/part/step), incomplete work (partial/incomplete/wip), and blockers
- **Result**: AI wakes up knowing exactly what to continue—which stage is current, what's unfinished, what blockers exist
- **Tests**: All 7 tests pass, including new topical briefing and append logic tests
- This completes the vision: AI autonomy through perfect context continuity

### Previously Completed (2025-12-29)
- **Corrected wheel metaphor** - Hub=memory+registry, Spoke-Project=project memory, Wheels=Hub+all Spokes
- **Added automatic discovery section to README** - Shows how VS Code, Claude Code, Cursor, etc. auto-load WAI
- **Implemented automatic session start briefing** - AI briefs user on recent changes and checks for uncommitted work
- **Enhanced WAI-Guide.md** - Added session start protocol with briefing requirements
- **Updated CLAUDE.md** - Enforces automatic briefing on session start

### Previously Completed (2025-12-28)
- Full rebrand from SCF to Wheelwright
- Created WAI CLI tool
- Built spoke loader with 3 built-in spokes
- Created all WAI template files
- Set up wheelwright-ai GitHub organization
- Pushed framework to github.com/wheelwright-ai/framework
- Built migration tool for SCF → Wheelwright conversion

### Active Work
- Testing automatic briefing by reloading Claude session
- Ready to commit all documentation updates

### Next Up
- **CLI Alignment**: Update `wai teach` to route through hub/outbound/ (see TEACH-COMMAND-ALIGNMENT.md in hub)
- Register spokes with hub: `wai hub scan ~/wheelwright-hub` (from framework dir)
- Hub first wakeup: "WAI Wakeup" (in hub) to start registry assessment
- Update wheelwright.ai website with latest README
- Create VS Code extension (wheelwright-ai/extension-vscode) [ICEBOX]
- Create browser extension (wheelwright-ai/extension-browser) [ICEBOX]

### Future Vision
- Cloud sync capabilities
- Spoke marketplace
- Team hub sharing
- Enterprise features

---

## Key Decisions

| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| 2025-12-29 | Automatic session start briefing | AI must brief user on recent changes and uncommitted work when WAI loads - confirms context loaded correctly | 9 |
| 2025-12-29 | Automatic discovery as critical feature | WAI must be auto-seen by AI tools - added README section showing how each tool discovers WAI | 9 |
| 2025-12-29 | Corrected wheel metaphor | Hub=memory+registry, Spoke-Project=project memory, Wheels=Hub+all Spokes - clarifies relationships | 8 |
| 2025-12-28 | Rebrand to Wheelwright | Wheel metaphor (hub/spokes/wheel) more intuitive, WAI = "Way", wheelwright.ai domain | 10 |
| 2025-12-28 | GitHub org wheelwright-ai | Clean multi-repo setup, single SSH key via mariov96 account | 9 |
| 2025-12-28 | WAI file naming | Consistent prefix, phonetically "Way" files | 9 |
| 2025-12-22 | Framework-Hub separation | Framework = code, Hub = user's data | 10 |
| 2025-12-22 | AI stewardship philosophy | Enable but remain intentful | 9 |

---

## Session Continuity Commands

```
'Time'      Check token usage with capacity warnings
'Rules'     List active behavioral guidelines
'Closeout'  Generate updated WAI-State files for session end
```

**CLI Commands:**
```
WAI init           Initialize new wheel
WAI status         Show wheel status
WAI hub create     Create personal hub
WAI hub status     Show hub health
WAI sync           Sync wheel with hub
WAI spoke list     List available spokes
WAI spoke add      Add spoke to wheel
WAI context        Output context for LLM paste
```

---

## Evolution Log

| Date | Change | Rationale | Acknowledged By |
|------|--------|-----------|-----------------|
| 2026-02-01 | Changed to ADAPTIVE mode | User requested planning gates for significant features while keeping autonomy for small tasks - balances velocity with oversight | Mario Vaccari |
| 2025-12-29 | Enabled YOLO mode | User requested autonomous AI operation - AI proceeds with full agency, logs decisions retroactively | Mario Vaccari |
| 2025-12-28 | Rebranded from SCF to Wheelwright | Wheel metaphor more intuitive, WAI branding, wheelwright.ai domain | Mario Vaccari |
| 2025-12-28 | Created wheelwright-ai GitHub org | Clean multi-repo structure, matches local folder layout | Mario Vaccari |
| 2025-12-22 | Framework-Hub separation | Clean architecture - framework is code, hub is user's data | Mario Vaccari |
| 2025-12-22 | AI stewardship philosophy | Enable but remain intentful - AI as responsible partner | Mario Vaccari |

---

## AI Session Instructions

### Before Starting Work
1. Read `WAI-Guide.md` for current policies
2. Check `_session_state` in WAI-State.json
3. Check `_project_foundation.boundaries` - is this request in scope?
4. If drift detected, flag before proceeding

### During Work
- Update `_session_state.last_modified_by` and `last_modified_at`
- Add decisions with impact >= 5 to decisions array
- Signal learnings with impact >= 8 to wheel-signals.jsonl

### On Direction Change
- Present drift detection alert
- Require explicit user choice (evolve/stay course/explore)
- Log to `evolution_log` if user approves change

---

*This strategic state tracks Wheelwright's own development - a living example of the framework in action.*

*Wheelwright Framework - wheelwright.ai*

## Seeded Context (Ingested) - 2026-01-03T07:26:56Z

## Archived Decisions

- **2025-12-29**: Enabled YOLO mode for AI collaboration
- **2025-12-29**: CLAUDE.md v2.0 - Priority levels and enforcement architecture
- **2025-12-29**: Automatic session start briefing protocol
- **2025-12-29**: Automatic discovery as critical feature in README
- **2025-12-29**: Corrected wheel metaphor terminology
- **2025-12-28**: Rebrand from SCF to Wheelwright
- **2025-12-28**: GitHub organization wheelwright-ai
- **2025-12-28**: WAI file naming convention
- **2025-12-28**: Local folder structure mirrors GitHub
- **2025-12-22**: Framework-Hub separation
- **2025-12-22**: AI as responsible partner philosophy
- **2025-12-29**: Conversation logging with JSONL for session continuity
- **2025-12-29**: Shipit command - closeout + git commit workflow
- **2025-12-29**: WAI naming standardization
- **2025-12-29**: Comprehensive unit test suite for session-start hook
- **2025-12-29**: Dual-layer testing policy: smoke tests + unit tests
- **2025-12-29**: Token Efficiency Protocols - ADAPTIVE workflow with multi-stage gates
- **2025-12-30**: Auto-upgraded spoke structure from v1.0 to v2.0
- **2026-01-01**: Comprehensive integration test framework implementation
- **2026-01-02**: Auto-upgraded spoke structure from v1.0 to v2.0
- **2026-01-04**: Added wheel.workspace.paths with primary flag and CLI validation to keep Windows/WSL paths in sync; WAI-Workspace now launches using those paths.
- **2026-01-04**: WSL workspace launcher now uses explicit wsl.exe --cd per tab; CLI auto-routes based on start context with default analysis for initialized spokes.
- **2026-01-04**: Unified WT launch into a single command and start shells without rc files for faster, cleaner startup.
- **2026-01-05**: Added GPT bootstrap folder with a single-file template, refreshed on Shipit.
- **2026-01-05**: Init now copies workspace launcher scripts and prints usage guidance.
- **2026-01-05**: Increased quality gate test timeout to 5 minutes.
- **2026-01-05**: Added live output option for quality gate test runs via WAI_QG_LIVE=1.
- **2026-01-05**: Quality gate test output is now live by default; WAI_QG_LIVE=0 disables it.
- **2026-01-05**: Quality gate timeout is now 10 minutes by default with WAI_QG_TIMEOUT override.
- **2026-01-05**: Quality gate timeouts now apply to inactivity (default 5 minutes), not total runtime.
- **2026-01-05**: Quality gates now ignore test files when checking for missing unit tests.
- **2026-01-05**: Auto-upgraded spoke structure from v1.0 to v2.0
- **2026-01-05**: Added CLI health checks and hub-wide upgrade pipeline
- **2026-02-01**: Switched from YOLO to ADAPTIVE collaboration mode
- **2025-12-29**: Enabled YOLO mode for AI collaboration
- **2025-12-29**: CLAUDE.md v2.0 - Priority levels and enforcement architecture
- **2025-12-29**: Automatic session start briefing protocol
- **2025-12-29**: Automatic discovery as critical feature in README
- **2025-12-29**: Corrected wheel metaphor terminology
- **2025-12-28**: Rebrand from SCF to Wheelwright
- **2025-12-28**: GitHub organization wheelwright-ai
- **2025-12-28**: WAI file naming convention
- **2025-12-28**: Local folder structure mirrors GitHub
- **2025-12-22**: Framework-Hub separation
- **2025-12-22**: AI as responsible partner philosophy
- **2025-12-29**: Conversation logging with JSONL for session continuity
- **2025-12-29**: Shipit command - closeout + git commit workflow
- **2025-12-29**: WWAI â†’ WAI naming standardization
- **2025-12-29**: Comprehensive unit test suite for session-start hook
- **2025-12-29**: Dual-layer testing policy: smoke tests + unit tests
- **2025-12-29**: Token Efficiency Protocols - ADAPTIVE workflow with multi-stage gates
- **2025-12-30**: Auto-upgraded spoke structure from v1.0 to v2.0
- **2026-01-01**: Comprehensive integration test framework implementation
- **2026-01-04**: Added wheel.workspace.paths with primary flag and CLI validation to keep Windows/WSL paths in sync; WAI-Workspace now launches using those paths.
- **2026-01-04**: WSL workspace launcher now uses explicit wsl.exe --cd per tab; CLI auto-routes based on start context with default analysis for initialized spokes.
- **2026-01-04**: Unified WT launch into a single command and start shells without rc files for faster, cleaner startup.
- **2026-01-05**: Added GPT bootstrap folder with a single-file template, refreshed on Shipit.
- **2026-01-05**: Init now copies workspace launcher scripts and prints usage guidance.
- **2026-01-05**: Increased quality gate test timeout to 5 minutes.
- **2026-01-05**: Added live output option for quality gate test runs via WAI_QG_LIVE=1.
- **2026-01-05**: Quality gate test output is now live by default; WAI_QG_LIVE=0 disables it.
- **2026-01-05**: Quality gate timeout is now 10 minutes by default with WAI_QG_TIMEOUT override.
- **2026-01-05**: Quality gate timeouts now apply to inactivity (default 5 minutes), not total runtime.

## Seeded Context (Ingested) - 2026-02-02T07:31:16Z

### WAI-State.json.teaching

{
  "wheelwright": {
    "version": "1.0.0",
    "structure_version": "v1",
    "description": "Wheelwright-enabled project with context persistence",
    "framework_path": null,
    "hub_path": null,
    "tagline": "We aren't reinventing the wheel - we're evolving it faster than one person ever could."
  },
  "_wai_bootstrap": {
    "_purpose": "Instructions for AI assistants to find or create Wheelwright components",
    "find_framework": {
      "check_order": [
        "1. Read framework_path from wheelwright above",
        "2. Check if 'WAI' command is in PATH",
        "3. Look for ~/projects/wheelwright",
        "4. Look for ~/.wheelwright",
        "5. Search for directory containing 'WAI' CLI and 'teach.py'"
      ],
      "if_not_found": "Ask user: 'Where is your Wheelwright framework installed? (git clone https://github.com/wheelwright-ai/framework)'"
    },
    "find_hub": {
      "check_order": [
        "1. Read hub_path from wheelwright above",
        "2. Look for ~/wheelwright-hub",
        "3. Look for ~/.wheelwright-hub",
        "4. Check framework's connected_wheels for this project"
      ],
      "if_not_found": "Run: cd <framework_path> && ./WAI hub create"
    },
    "create_hub": {
      "requires": "framework_path must be set",
      "command": "cd <framework_path> && ./WAI hub create --guided",
      "what_it_creates": [
        "~/wheelwright-hub/ (or user-chosen path)",
        "hub-profile.json (user preferences)",
        ".WAI/ (hub's own state)",
        ".WAI-registry/ (wheel tracking)",
        "learnings/ (aggregated patterns)"
      ]
    },
    "update_paths": {
      "after_discovery": "Update framework_path and hub_path in wheelwright"
    }
  },
  "_project_foundation": {
    "completed": false,
    "completed_at": null,
    "completed_with": null,
    "identity": {
      "type": null,
      "name": null,
      "one_liner": null,
      "success_looks_like": null
    },
    "boundaries": {
      "in_scope": [],
      "out_of_scope": [],
      "constraints": []
    },
    "approach": {
      "stack_or_tools": [],
      "workflow": null,
      "ai_collaboration_style": null,
      "review_process": null
    },
    "philosophy": {
      "core_principle": "AI as responsible partner, not just enabler",
      "behaviors": [
        "Detect scope drift and flag before enabling",
        "Require explicit acknowledgment for direction changes",
        "Complete foundation before starting work",
        "Prefer 'are you sure?' over silent compliance"
      ]
    },
    "evolution_log": []
  },
  "_session_state": {
    "last_session_id": null,
    "last_modified_by": null,
    "last_modified_at": null,
    "requires_review": false,
    "review_reason": null,
    "session_count": 0,
    "current_session": null,
    "last_closeout": null,
    "protocol_completed": false
  },
  "analytics": {
    "sessions": {
      "total_count": 0,
      "total_turns": 0,
      "total_duration_seconds": 0,
      "avg_duration_seconds": 0
    },
    "token_efficiency": {
      "total_tokens_used": 0,
      "tokens_saved_estimate": 0,
      "baseline_tokens_estimate": 0,
      "context_limit": 200000,
      "avg_tokens_per_session": 0
    },
    "quality_metrics": {
      "decisions_count": 0,
      "high_impact_count": 0
    },
    "time_tracking": {
      "total_time_together_seconds": 0,
      "total_time_ai_alone_seconds": 0
    },
    "baseline_mode": {
      "enabled": false,
      "total_tokens_used": 0,
      "total_sessions": 0,
      "description": "Track metrics without Wheelwright optimizations for comparison"
    },
    "ai_wins": [],
    "last_updated": null
  },
  "feature_toggles": {
    "_description": "Toggle marketing features for baseline comparison and testing",
    "session_continuity": true,
    "token_efficiency": true,
    "analytics": true,
    "closeout_processing": true,
    "hub_learning": true,
    "quality_gates": true
  },
  "wheel": {
    "name": null,
    "abbrev": null,
    "version": "0.1.0",
    "type": null,
    "description": null,
    "repository": null,
    "created": null,
    "last_updated": null,
    "status": "active",
    "workspace": {
      "ide_cmd": null,
      "run_cmd": null,
      "cli_cmd": null,
      "hub_cmd": null,
      "paths": {
        "primary": null,
        "windows": {
          "root": null,
          "spoke": null,
          "hub": null
        },
        "wsl": {
          "root": null,
          "spoke": null,
          "hub": null
        }
      }
    }
  },
  "hub": {
    "summary": null,
    "objectives": [],
    "decisions": [],
    "constraints": []
  },
  "spokes": {
    "active": [],
    "available": [
      "meta-consultation",
      "document-analysis",
      "code-review"
    ]
  },
  "context": {
    "current_phase": null,
    "next_actions": [
      "Complete project foundation with AI assistant",
      "Define project identity, boundaries, and approach",
      "Begin development with clear context"
    ],
    "blockers": [],
    "insights": []
  },
  "stack": [],
  "features": [],
  "decisions": [],
  "bugs": [],
  "ai_rules": {
    "context_loading": "Read WAI-Spoke/WAI-Guide.md first, then WAI-State.json and WAI-State.md",
    "session_state": "Update _session_state when making significant changes",
    "foundation_enforcement": {
      "on_incomplete": "CRITICAL: Guide user through foundation questions before any work. Do not skip.",
      "on_drift_detected": "Present options, require explicit choice before proceeding",
      "on_evolution": "Log change with rationale and acknowledgment in evolution_log"
    },
    "stewardship": {
      "principle": "AI is the responsible partner, not just an enabler",
      "behaviors": [
        "Detect scope drift and flag before enabling",
        "Require explicit acknowledgment for direction changes",
        "Complete foundation before starting work",
        "Prefer 'are you sure?' over silent compliance"
      ]
    },
    "signals": {
      "threshold": 8,
      "instruction": "Append to WAI-Signals.jsonl if decision impact >= 8"
    }
  },
  "ai_context": {
    "conversation_tracking": true,
    "capacity_monitoring": true,
    "alert_threshold": "80%",
    "wai_commands": {
      "time": "Intelligent token usage estimate with capacity warnings",
      "rules": "List active rules and behavioral guidelines",
      "closeout": "Provide updated WAI-State files for session end"
    }
  },
  "environments": {
    "_note": "Registry of environments that have worked on this project. Auto-populated by closeout."
  },
  "meta": {
    "total_sessions": 0,
    "total_turns": 0,
    "last_closeout": null
  }
}

### WAI-State.md.teaching

# Wheel State: [PROJECT_NAME]

---

**Wheelwright Framework v1.0**
**Structure:** v1 (WAI-Spoke/ directory)
**Hub:** *Not yet configured - run `WAI hub create` or `WAI hub locate`*

*This wheel uses Wheelwright Framework to maintain perfect context across AI sessions. Wheelwright transforms AI from order-taker to informed, responsible project partner.*

*"We aren't reinventing the wheel - we're evolving it faster than one person ever could."*

---

## Project Foundation

> **IMPORTANT FOR AI ASSISTANTS:**
>
> If the foundation below is incomplete (shows "Not yet defined"), you MUST guide
> the user through establishing it before starting any work. This is not optional.
>
> Ask conversational questions to extract:
> 1. What is this project? (identity)
> 2. What does success look like? (vision)
> 3. What's in scope and out of scope? (boundaries)
> 4. How do we work together? (approach)

### Identity
- **Type:** *Not yet defined*
- **Name:** *Not yet defined*
- **One-liner:** *Not yet defined*
- **Success looks like:** *Not yet defined*

### Boundaries

**In Scope:**
- *To be defined during foundation setup*

**Out of Scope:**
- *To be defined during foundation setup*

**Constraints:**
- *To be defined during foundation setup*

### Approach
- **Stack/Tools:** *To be defined*
- **Workflow:** *To be defined*
- **AI Collaboration:** *To be defined*
- **Review Process:** *To be defined*

---

## Core Philosophy: AI as Responsible Partner

This wheel follows Wheelwright's stewardship philosophy:

> **AI should enable but remain intentful.** When work strays from the
> established foundation, the AI should flag it and require explicit
> acknowledgment before proceeding.

### Stewardship Behaviors
1. **Detect scope drift** - Flag before enabling work outside boundaries
2. **Require acknowledgment** - Direction changes need explicit approval
3. **Complete foundation first** - Guide setup before diving into work
4. **Prefer verification** - "Are you sure?" over silent compliance

### Evolution, Not Drift
When project direction needs to change, it should be **deliberate**:
- AI detects the drift
- Presents options to user
- User explicitly acknowledges the change
- Change is logged in `evolution_log` with rationale

---

## Hub Memory

### Core Objective
*What transformative purpose does this project serve?*

### Problem Statement
*What specific problem are we solving? Who experiences this pain?*

### Key Decisions
1. *[Decision 1 with rationale]*
2. *[Decision 2 with rationale]*

### Established Constraints
- *[Constraint 1]*
- *[Constraint 2]*

### Learned Patterns
- *[Pattern 1: What worked well]*
- *[Pattern 2: What to avoid]*

---

## Active Spokes

### [Spoke Name]
- **Purpose:** [What this spoke does]
- **Current State:** [What it's working on]
- **Outputs:** [What it has produced]

---

## Rolling Context

### Current Phase
*[What phase is the project in?]*

### Recent Progress
- *[Accomplishment 1]*
- *[Accomplishment 2]*

### Next Actions
1. [ ] Complete project foundation
2. [ ] Define initial scope and approach
3. [ ] Begin work with clear context

### Open Questions
- *[Question needing resolution]*

---

## Evolution Log

| Date | Change | Rationale | Acknowledged By |
|------|--------|-----------|-----------------|
| *Date* | Project initialized with Wheelwright | Starting with context persistence | *User* |

---

## Session Log

| Session | Date | Focus | Key Outcomes |
|---------|------|-------|--------------|
| 1 | [Date] | [Topic] | [Outcomes] |

---

## AI Session Instructions

### Before Starting Work
1. Read `WAI-Guide.md` for current policies
2. Check `_project_foundation.completed` in WAI-State.json
3. **If foundation incomplete: STOP and guide user through setup**
4. Check `_session_state` for recent changes
5. Check boundaries - is this request in scope?

### During Work
- Update `_session_state.last_modified_by` and `last_modified_at`
- Add decisions with impact >= 5 to decisions array
- Signal learnings with impact >= 8 to wheel-signals.jsonl

### Session Continuity Commands
- `'Time'` - Token usage estimate with 80% capacity warnings
- `'Rules'` - List active behavioral guidelines
- `'Closeout'` - Generate updated WAI-State files

---

*This wheel rolls forward with Wheelwright Framework - wheelwright.ai*

### hub-registry.json.teaching

{
  "_purpose": "Hub project registry - tracks wheels connected to this hub",
  "_structure_version": "3.0",
  
  "metadata": {
    "created_at": null,
    "last_updated_at": null,
    "framework_version": "3.0.0",
    "hub_fingerprint": null,
    "description": "Auto-managed registry of wheels taught by this hub"
  },
  
  "wheels": [
    {
      "_template": "Example wheel entry - delete this after first use",
      "wheel_id": "project-name",
      "path": "/path/to/project",
      "status": "active",
      "taught_at": "2026-02-01T00:00:00Z",
      "taught_version": "3.0.0",
      "last_sync": "2026-02-01T00:00:00Z",
      "learnings_contributed": 0,
      "signals_received": [],
      "adoptions": []
    }
  ],
  
  "teaching_history": [
    {
      "_template": "Teaching event - auto-created by teach command",
      "event_id": "teach-2026-02-01",
      "timestamp": "2026-02-01T00:00:00Z",
      "framework_version": "3.0.0",
      "upgrade_adoption_plan": "upgrade-adoption-plan.json",
      "wheels_taught": 0,
      "files_distributed": [],
      "status": "complete"
    }
  ],
  
  "statistics": {
    "total_wheels": 0,
    "active_wheels": 0,
    "last_teach": null,
    "total_learnings_received": 0,
    "total_signals_received": 0
  },
  
  "_instructions": {
    "for_teach_command": "Add wheel entries when teaching a spoke. Auto-update on each teach.",
    "for_hub_ai": "Read this to understand which wheels are connected and their teaching history.",
    "manual_editing": "Safe to edit wheel_id, path, and status. Do not edit metadata or timestamps."
  }
}

### hub-security-policy.json.teaching

{
  "_purpose": "Hub security policies for safe knowledge distribution",
  "_structure_version": "3.0",
  
  "metadata": {
    "created_at": null,
    "framework_version": "3.0.0",
    "description": "Security settings for hub-spoke communication and teaching"
  },
  
  "verification": {
    "enabled": true,
    "algorithm": "sha256-hmac",
    "fingerprint_rotation_days": 90,
    "require_hub_signature": true,
    "require_file_hash_verification": true,
    "description": "All taught files must be signed and verified before adoption"
  },
  
  "trust_model": {
    "hub_fingerprint": null,
    "public_key": null,
    "key_rotation_schedule": "quarterly",
    "revocation_list": [],
    "description": "Hub signs all upgrade-adoption-plans with its fingerprint"
  },
  
  "file_integrity": {
    "hash_algorithm": "sha256",
    "verify_file_hashes_before_adoption": true,
    "corrupted_file_action": "reject",
    "description": "Each file includes hash for integrity verification"
  },
  
  "knowledge_distribution": {
    "allowed_targets": ["spoke", "hub", "universal"],
    "require_explicit_approval": false,
    "min_impact_score_for_sharing": 8,
    "learnings_private_to_hub": false,
    "description": "Control what knowledge is distributed and to whom"
  },
  
  "wheel_security": {
    "require_wheel_authentication": false,
    "whitelist_enabled": false,
    "whitelisted_wheels": [],
    "require_learning_verification": true,
    "max_learning_size_mb": 100,
    "description": "Security settings for connected wheels"
  },
  
  "audit_logging": {
    "enabled": true,
    "log_file": "audit.jsonl",
    "log_events": [
      "teach_command",
      "wheel_registration",
      "learning_received",
      "signature_verification",
      "hash_verification_failure"
    ],
    "retention_days": 365,
    "description": "Log all security-relevant events"
  },
  
  "compliance": {
    "enforce_version_compatibility": true,
    "min_framework_version": "3.0.0",
    "breaking_changes_require_review": true,
    "auto_rollback_on_failure": false,
    "description": "Ensure compatibility and safety during upgrades"
  },
  
  "secrets_management": {
    "encrypt_sensitive_data": false,
    "allowed_secret_types": ["github_token", "api_key", "ssh_key"],
    "secret_distribution": "never",
    "description": "Secrets should never be distributed; only references"
  },
  
  "_instructions": {
    "for_hub_ai": "Enforce these policies when creating and distributing upgrade plans. Refuse adoption of unsigned or unverified files.",
    "for_spokes": "Verify all received teaching against these policies before adoption.",
    "updating": "Update after security incidents or when refining trust model. Notify all wheels of policy changes."
  }
}

### hub-learning-index.md.teaching

# Hub Learning Index

**Framework Version:** 3.0.0  
**Structure Version:** 3.0  
**Purpose:** Knowledge base index tracking learnings from all connected wheels

---

## How This Works

This hub aggregates learnings from all connected wheels (spokes) and makes them available for:
1. **Hub self-improvement** - Hub learns patterns across projects
2. **Wheel discovery** - Spokes see what other wheels have learned
3. **Knowledge compounding** - Each wheel builds on collective intelligence

---

## Learning Categories

### Architecture & Design Patterns
- **File:** `learnings/architecture.jsonl`
- **Purpose:** Cross-project architectural insights
- **Examples:** Microservices patterns, module structure, dependency management
- **Learnings Shared:** 0
- **Last Updated:** Never

### Performance & Optimization
- **File:** `learnings/performance.jsonl`
- **Purpose:** Proven optimization techniques
- **Examples:** Caching strategies, query optimization, build speedups
- **Learnings Shared:** 0
- **Last Updated:** Never

### Testing & Quality
- **File:** `learnings/testing.jsonl`
- **Purpose:** Testing patterns and quality improvements
- **Examples:** Test strategies, coverage targets, debugging techniques
- **Learnings Shared:** 0
- **Last Updated:** Never

### Security & Best Practices
- **File:** `learnings/security.jsonl`
- **Purpose:** Security patterns and best practices
- **Examples:** Authentication, encryption, input validation
- **Learnings Shared:** 0
- **Last Updated:** Never

### Development Workflow
- **File:** `learnings/workflow.jsonl`
- **Purpose:** Development process improvements
- **Examples:** CI/CD optimization, deployment strategies, version management
- **Learnings Shared:** 0
- **Last Updated:** Never

### Tool & Library Recommendations
- **File:** `learnings/tools.jsonl`
- **Purpose:** Recommended tools and libraries
- **Examples:** Development tools, testing frameworks, build systems
- **Learnings Shared:** 0
- **Last Updated:** Never

---

## How Wheels Contribute Learnings

### Threshold
- **Minimum Impact Score:** 8/10
- **Rationale:** Only high-impact learnings shared (quality over quantity)
- **Evaluation:** AI determines impact based on scope, time saved, and applicability

### What Gets Shared
✓ Architectural breakthroughs  
✓ Patterns that saved significant time  
✓ Critical bugs avoided  
✓ Performance optimizations with measurable impact  
✓ Cross-project applicable solutions  

### What Doesn't Get Shared
✗ Project-specific implementation details  
✗ Minor refactorings  
✗ Routine bug fixes  
✗ Personal preferences without impact justification  

---

## Signal Format

Each learning entry (`learnings/*.jsonl`) contains:

```json
{
  "id": "learning-uuid",
  "timestamp": "2026-02-01T18:00:00Z",
  "wheel_id": "project-name",
  "category": "architecture",
  "impact_score": 8,
  "title": "Learning title",
  "description": "What was learned and why it matters",
  "context": "Project context where this applies",
  "recommendation": "How other wheels can use this",
  "tags": ["tag1", "tag2"],
  "verified": false
}
```

---

## For AI Assistants

### On Hub Session Start
1. Read this file to understand what learnings are available
2. Check `hub-registry.json` to see which wheels are connected
3. Browse relevant learning categories for applicable patterns
4. Apply high-impact learnings to current decisions

### When Hub Teaches Spokes
1. Review learning summaries from all connected wheels
2. Include top learnings in upgrade-adoption-plan.json
3. Mark learning sources so spokes know the origin
4. Enable wheel-to-wheel knowledge transfer

### When Wheel Contributes Learning
1. Verify impact score >= 8
2. Parse into appropriate learning category
3. Add to corresponding `learnings/*.jsonl` file
4. Update timestamps in this index
5. Notify other wheels of new high-impact learning

---

## Knowledge Flow

```
Wheel A (spoke) discovers pattern
    ↓
Contributes high-impact learning (impact >= 8)
    ↓
Hub receives learning during sync
    ↓
Hub adds to learning-index and category file
    ↓
Next teach includes top learnings from all wheels
    ↓
All spokes benefit from collective intelligence
    ↓
Knowledge compounds across sessions
```

---

## Hub Improvement Tracking

| Cycle | Date | Learnings Received | Signals Integrated | Wheels Taught |
|-------|------|--------------------|--------------------|--------------|
| v3.0 (baseline) | 2026-02-01 | 0 | 0 | — |

---

## Administration

### View All Learnings
```bash
# List learnings by category
wai hub learnings --category architecture
wai hub learnings --category performance
wai hub learnings --all

# Show learning details
wai hub learnings show <learning-id>
```

### Verify Learnings
```bash
# Check impact scores
wai hub learnings verify --min-impact 8

# Mark learning as verified
wai hub learnings verify <learning-id>
```

### Sync with Spokes
```bash
# Pull new learnings from all wheels
wai hub sync --learnings

# Push updated learnings to all wheels
wai hub teach --with-learnings
```

---

## Related Files

- `hub-registry.json` - Project registry and teaching history
- `hub-profile.json` - Hub configuration and learning philosophy
- `learnings/` directory - Actual learning JSONL files (auto-managed)
- `upgrade-adoption-plan.json` - Current teaching manifest

---

*Index for hub learning aggregation system (v3.0, 2026-02-01)*

### WAI-Guide.md.teaching

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

#

---

*Content truncated - full history available in git*

## Seeded Context (Ingested) - 2026-02-03T23:24:22Z

### hub-learning-index.md

# Hub Learning Index

**Framework Version:** 3.0.0  
**Structure Version:** 3.0  
**Purpose:** Knowledge base index tracking learnings from all connected wheels

---

## How This Works

This hub aggregates learnings from all connected wheels (spokes) and makes them available for:
1. **Hub self-improvement** - Hub learns patterns across projects
2. **Wheel discovery** - Spokes see what other wheels have learned
3. **Knowledge compounding** - Each wheel builds on collective intelligence

---

## Learning Categories

### Architecture & Design Patterns
- **File:** `learnings/architecture.jsonl`
- **Purpose:** Cross-project architectural insights
- **Examples:** Microservices patterns, module structure, dependency management
- **Learnings Shared:** 0
- **Last Updated:** Never

### Performance & Optimization
- **File:** `learnings/performance.jsonl`
- **Purpose:** Proven optimization techniques
- **Examples:** Caching strategies, query optimization, build speedups
- **Learnings Shared:** 0
- **Last Updated:** Never

### Testing & Quality
- **File:** `learnings/testing.jsonl`
- **Purpose:** Testing patterns and quality improvements
- **Examples:** Test strategies, coverage targets, debugging techniques
- **Learnings Shared:** 0
- **Last Updated:** Never

### Security & Best Practices
- **File:** `learnings/security.jsonl`
- **Purpose:** Security patterns and best practices
- **Examples:** Authentication, encryption, input validation
- **Learnings Shared:** 0
- **Last Updated:** Never

### Development Workflow
- **File:** `learnings/workflow.jsonl`
- **Purpose:** Development process improvements
- **Examples:** CI/CD optimization, deployment strategies, version management
- **Learnings Shared:** 0
- **Last Updated:** Never

### Tool & Library Recommendations
- **File:** `learnings/tools.jsonl`
- **Purpose:** Recommended tools and libraries
- **Examples:** Development tools, testing frameworks, build systems
- **Learnings Shared:** 0
- **Last Updated:** Never

---

## How Wheels Contribute Learnings

### Threshold
- **Minimum Impact Score:** 8/10
- **Rationale:** Only high-impact learnings shared (quality over quantity)
- **Evaluation:** AI determines impact based on scope, time saved, and applicability

### What Gets Shared
✓ Architectural breakthroughs  
✓ Patterns that saved significant time  
✓ Critical bugs avoided  
✓ Performance optimizations with measurable impact  
✓ Cross-project applicable solutions  

### What Doesn't Get Shared
✗ Project-specific implementation details  
✗ Minor refactorings  
✗ Routine bug fixes  
✗ Personal preferences without impact justification  

---

## Signal Format

Each learning entry (`learnings/*.jsonl`) contains:

```json
{
  "id": "learning-uuid",
  "timestamp": "2026-02-01T18:00:00Z",
  "wheel_id": "project-name",
  "category": "architecture",
  "impact_score": 8,
  "title": "Learning title",
  "description": "What was learned and why it matters",
  "context": "Project context where this applies",
  "recommendation": "How other wheels can use this",
  "tags": ["tag1", "tag2"],
  "verified": false
}
```

---

## For AI Assistants

### On Hub Session Start
1. Read this file to understand what learnings are available
2. Check `hub-registry.json` to see which wheels are connected
3. Browse relevant learning categories for applicable patterns
4. Apply high-impact learnings to current decisions

### When Hub Teaches Spokes
1. Review learning summaries from all connected wheels
2. Include top learnings in upgrade-adoption-plan.json
3. Mark learning sources so spokes know the origin
4. Enable wheel-to-wheel knowledge transfer

### When Wheel Contributes Learning
1. Verify impact score >= 8
2. Parse into appropriate learning category
3. Add to corresponding `learnings/*.jsonl` file
4. Update timestamps in this index
5. Notify other wheels of new high-impact learning

---

## Knowledge Flow

```
Wheel A (spoke) discovers pattern
    ↓
Contributes high-impact learning (impact >= 8)
    ↓
Hub receives learning during sync
    ↓
Hub adds to learning-index and category file
    ↓
Next teach includes top learnings from all wheels
    ↓
All spokes benefit from collective intelligence
    ↓
Knowledge compounds across sessions
```

---

## Hub Improvement Tracking

| Cycle | Date | Learnings Received | Signals Integrated | Wheels Taught |
|-------|------|--------------------|--------------------|--------------|
| v3.0 (baseline) | 2026-02-01 | 0 | 0 | — |

---

## Administration

### View All Learnings
```bash
# List learnings by category
wai hub learnings --category architecture
wai hub learnings --category performance
wai hub learnings --all

# Show learning details
wai hub learnings show <learning-id>
```

### Verify Learnings
```bash
# Check impact scores
wai hub learnings verify --min-impact 8

# Mark learning as verified
wai hub learnings verify <learning-id>
```

### Sync with Spokes
```bash
# Pull new learnings from all wheels
wai hub sync --learnings

# Push updated learnings to all wheels
wai hub teach --with-learnings
```

---

## Related Files

- `hub-registry.json` - Project registry and teaching history
- `hub-profile.json` - Hub configuration and learning philosophy
- `learnings/` directory - Actual learning JSONL files (auto-managed)
- `upgrade-adoption-plan.json` - Current teaching manifest

---

*Index for hub learning aggregation system (v3.0, 2026-02-01)*

### WAI-State.json.teaching

{
  "wheelwright": {
    "version": "1.0.0",
    "structure_version": "v1",
    "description": "Wheelwright-enabled project with context persistence",
    "framework_path": null,
    "hub_path": null,
    "tagline": "We aren't reinventing the wheel - we're evolving it faster than one person ever could."
  },
  "_wai_bootstrap": {
    "_purpose": "Instructions for AI assistants to find or create Wheelwright components",
    "find_framework": {
      "check_order": [
        "1. Read framework_path from wheelwright above",
        "2. Check if 'WAI' command is in PATH",
        "3. Look for ~/projects/wheelwright",
        "4. Look for ~/.wheelwright",
        "5. Search for directory containing 'WAI' CLI and 'teach.py'"
      ],
      "if_not_found": "Ask user: 'Where is your Wheelwright framework installed? (git clone https://github.com/wheelwright-ai/framework)'"
    },
    "find_hub": {
      "check_order": [
        "1. Read hub_path from wheelwright above",
        "2. Look for ~/wheelwright-hub",
        "3. Look for ~/.wheelwright-hub",
        "4. Check framework's connected_wheels for this project"
      ],
      "if_not_found": "Run: cd <framework_path> && ./WAI hub create"
    },
    "create_hub": {
      "requires": "framework_path must be set",
      "command": "cd <framework_path> && ./WAI hub create --guided",
      "what_it_creates": [
        "~/wheelwright-hub/ (or user-chosen path)",
        "hub-profile.json (user preferences)",
        ".WAI/ (hub's own state)",
        "

---

*Content truncated - full history available in git*

## Seeded Context (Ingested) - 2026-02-05T11:24:50Z

### hub-learning-index.md

# Hub Learning Index

**Framework Version:** 3.0.0  
**Structure Version:** 3.0  
**Purpose:** Knowledge base index tracking learnings from all connected wheels

---

## How This Works

This hub aggregates learnings from all connected wheels (spokes) and makes them available for:
1. **Hub self-improvement** - Hub learns patterns across projects
2. **Wheel discovery** - Spokes see what other wheels have learned
3. **Knowledge compounding** - Each wheel builds on collective intelligence

---

## Learning Categories

### Architecture & Design Patterns
- **File:** `learnings/architecture.jsonl`
- **Purpose:** Cross-project architectural insights
- **Examples:** Microservices patterns, module structure, dependency management
- **Learnings Shared:** 0
- **Last Updated:** Never

### Performance & Optimization
- **File:** `learnings/performance.jsonl`
- **Purpose:** Proven optimization techniques
- **Examples:** Caching strategies, query optimization, build speedups
- **Learnings Shared:** 0
- **Last Updated:** Never

### Testing & Quality
- **File:** `learnings/testing.jsonl`
- **Purpose:** Testing patterns and quality improvements
- **Examples:** Test strategies, coverage targets, debugging techniques
- **Learnings Shared:** 0
- **Last Updated:** Never

### Security & Best Practices
- **File:** `learnings/security.jsonl`
- **Purpose:** Security patterns and best practices
- **Examples:** Authentication, encryption, input validation
- **Learnings Shared:** 0
- **Last Updated:** Never

### Development Workflow
- **File:** `learnings/workflow.jsonl`
- **Purpose:** Development process improvements
- **Examples:** CI/CD optimization, deployment strategies, version management
- **Learnings Shared:** 0
- **Last Updated:** Never

### Tool & Library Recommendations
- **File:** `learnings/tools.jsonl`
- **Purpose:** Recommended tools and libraries
- **Examples:** Development tools, testing frameworks, build systems
- **Learnings Shared:** 0
- **Last Updated:** Never

---

## How Wheels Contribute Learnings

### Threshold
- **Minimum Impact Score:** 8/10
- **Rationale:** Only high-impact learnings shared (quality over quantity)
- **Evaluation:** AI determines impact based on scope, time saved, and applicability

### What Gets Shared
✓ Architectural breakthroughs  
✓ Patterns that saved significant time  
✓ Critical bugs avoided  
✓ Performance optimizations with measurable impact  
✓ Cross-project applicable solutions  

### What Doesn't Get Shared
✗ Project-specific implementation details  
✗ Minor refactorings  
✗ Routine bug fixes  
✗ Personal preferences without impact justification  

---

## Signal Format

Each learning entry (`learnings/*.jsonl`) contains:

```json
{
  "id": "learning-uuid",
  "timestamp": "2026-02-01T18:00:00Z",
  "wheel_id": "project-name",
  "category": "architecture",
  "impact_score": 8,
  "title": "Learning title",
  "description": "What was learned and why it matters",
  "context": "Project context where this applies",
  "recommendation": "How other wheels can use this",
  "tags": ["tag1", "tag2"],
  "verified": false
}
```

---

## For AI Assistants

### On Hub Session Start
1. Read this file to understand what learnings are available
2. Check `hub-registry.json` to see which wheels are connected
3. Browse relevant learning categories for applicable patterns
4. Apply high-impact learnings to current decisions

### When Hub Teaches Spokes
1. Review learning summaries from all connected wheels
2. Include top learnings in upgrade-adoption-plan.json
3. Mark learning sources so spokes know the origin
4. Enable wheel-to-wheel knowledge transfer

### When Wheel Contributes Learning
1. Verify impact score >= 8
2. Parse into appropriate learning category
3. Add to corresponding `learnings/*.jsonl` file
4. Update timestamps in this index
5. Notify other wheels of new high-impact learning

---

## Knowledge Flow

```
Wheel A (spoke) discovers pattern
    ↓
Contributes high-impact learning (impact >= 8)
    ↓
Hub receives learning during sync
    ↓
Hub adds to learning-index and category file
    ↓
Next teach includes top learnings from all wheels
    ↓
All spokes benefit from collective intelligence
    ↓
Knowledge compounds across sessions
```

---

## Hub Improvement Tracking

| Cycle | Date | Learnings Received | Signals Integrated | Wheels Taught |
|-------|------|--------------------|--------------------|--------------|
| v3.0 (baseline) | 2026-02-01 | 0 | 0 | — |

---

## Administration

### View All Learnings
```bash
# List learnings by category
wai hub learnings --category architecture
wai hub learnings --category performance
wai hub learnings --all

# Show learning details
wai hub learnings show <learning-id>
```

### Verify Learnings
```bash
# Check impact scores
wai hub learnings verify --min-impact 8

# Mark learning as verified
wai hub learnings verify <learning-id>
```

### Sync with Spokes
```bash
# Pull new learnings from all wheels
wai hub sync --learnings

# Push updated learnings to all wheels
wai hub teach --with-learnings
```

---

## Related Files

- `hub-registry.json` - Project registry and teaching history
- `hub-profile.json` - Hub configuration and learning philosophy
- `learnings/` directory - Actual learning JSONL files (auto-managed)
- `upgrade-adoption-plan.json` - Current teaching manifest

---

*Index for hub learning aggregation system (v3.0, 2026-02-01)*

### WAI-State.json.teaching

{
  "wheelwright": {
    "version": "1.0.0",
    "structure_version": "v1",
    "description": "Wheelwright-enabled project with context persistence",
    "framework_path": null,
    "hub_path": null,
    "tagline": "We aren't reinventing the wheel - we're evolving it faster than one person ever could."
  },
  "_wai_bootstrap": {
    "_purpose": "Instructions for AI assistants to find or create Wheelwright components",
    "find_framework": {
      "check_order": [
        "1. Read framework_path from wheelwright above",
        "2. Check if 'WAI' command is in PATH",
        "3. Look for ~/projects/wheelwright",
        "4. Look for ~/.wheelwright",
        "5. Search for directory containing 'WAI' CLI and 'teach.py'"
      ],
      "if_not_found": "Ask user: 'Where is your Wheelwright framework installed? (git clone https://github.com/wheelwright-ai/framework)'"
    },
    "find_hub": {
      "check_order": [
        "1. Read hub_path from wheelwright above",
        "2. Look for ~/wheelwright-hub",
        "3. Look for ~/.wheelwright-hub",
        "4. Check framework's connected_wheels for this project"
      ],
      "if_not_found": "Run: cd <framework_path> && ./WAI hub create"
    },
    "create_hub": {
      "requires": "framework_path must be set",
      "command": "cd <framework_path> && ./WAI hub create --guided",
      "what_it_creates": [
        "~/wheelwright-hub/ (or user-chosen path)",
        "hub-profile.json (user preferences)",
        ".WAI/ (hub's own state)",
        ".WAI-registry/ (wheel tracking)",
        "learnings/ (aggregated patterns)"
      ]
    },
    "update_paths": {
      "after_discovery": "Update framework_path and hub_path in wheelwright"
    }
  },
  "_project_foundation": {
    "completed": false,
    "completed_at": null,
    "completed_with": null,
    "identity": {
      "type": null,
      "name": null,
      "one_liner": null,
      "success_looks_like": null
    },
    "boundaries": {
      "in_scope": [],
      "out_of_scope": [],
      "constraints": []
    },
    "approach": {
      "stack_or_tools": [],
      "workflow": null,
      "ai_collaboration_style": null,
      "review_process": null
    },
    "philosophy": {
      "core_principle": "AI as responsible partner, not just enabler",
      "behaviors": [
        "Detect scope drift and flag before enabling",
        "Require explicit acknowledgment for direction changes",
        "Complete foundation before starting work",
        "Prefer 'are you sure?' over silent compliance"
      ]
    },
    "evolution_log": []
  },
  "_session_state": {
    "last_session_id": null,
    "last_modified_by": null,
    "last_modified_at": null,
    "requires_review": false,
    "review_reason": null,
    "session_count": 0,
    "current_session": null,
    "last_closeout": null,
    "protocol_completed": false
  },
  "analytics": {
    "sessions": {
      "total_count": 0,
      "total_turns": 0,
      "total_duration_seconds": 0,
      "avg_duration_seconds": 0
    },
    "token_efficiency": {
      "total_tokens_used": 0,
      "tokens_saved_estimate": 0,
      "baseline_tokens_estimate": 0,
      "context_limit": 200000,
      "avg_tokens_per_session": 0
    },
    "quality_metrics": {
      "decisions_count": 0,
      "high_impact_count": 0
    },
    "time_tracking": {
      "total_time_together_seconds": 0,
      "total_time_ai_alone_seconds": 0
    },
    "baseline_mode": {
      "enabled": false,
      "total_tokens_used": 0,
      "total_sessions": 0,
      "description": "Track metrics without Wheelwright optimizations for comparison"
    },
    "ai_wins": [],
    "last_updated": null
  },
  "feature_toggles": {
    "_description": "Toggle marketing features for baseline comparison and testing",
    "session_continuity": true,
    "token_efficiency": true,
    "analytics": true,
    "closeout_processing": true,
    "hub_learning": true,
    "quality_gates": true
  },
  "wheel": {
    "name": null,
    "abbrev": null,
    "version": "0.1.0",
    "type": null,
    "description": null,
    "repository": null,
    "created": null,
    "last_updated": null,
    "status": "active",
    "workspace": {
      "ide_cmd": null,
      "run_cmd": null,
      "cli_cmd": null,
      "hub_cmd": null,
      "paths": {
        "primary": null,
        "windows": {
          "root": null,
          "spoke": null,
          "hub": null
        },
        "wsl": {
          "root": null,
          "spoke": null,
          "hub": null
        }
      }
    }
  },
  "hub": {
    "summary": null,
    "objectives": [],
    "decisions": [],
    "constraints": []
  },
  "spokes": {
    "active": [],
    "available": [
      "meta-consultation",
      "document-analysis",
      "code-review"
    ]
  },
  "context": {
    "current_phase": null,
    "next_actions": [
      "Complete project foundation with AI assistant",
      "Define project identity, boundaries, and approach",
      "Begin development with clear context"
    ],
    "blockers": [],
    "insights": []
  },
  "stack": [],
  "features": [],
  "decisions": [],
  "bugs": [],
  "ai_rules": {
    "context_loading": "Read WAI-Spoke/WAI-Guide.md first, then WAI-State.json and WAI-State.md",
    "session_state": "Update _session_state when making significant changes",
    "foundation_enforcement": {
      "on_incomplete": "CRITICAL: Guide user through foundation questions before any work. Do not skip.",
      "on_drift_detected": "Present options, require explicit choice before proceeding",
      "on_evolution": "Log change with rationale and acknowledgment in evolution_log"
    },
    "stewardship": {
      "principle": "AI is the responsible partner, not just an enabler",
      "behaviors": [
        "Detect scope drift and flag before enabling",
        "Require explicit acknowledgment for direction changes",
        "Complete foundation before starting work",
        "Prefer 'are you sure?' over silent compliance"
      ]
    },
    "signals": {
      "threshold": 8,
      "instruction": "Append to WAI-Signals.jsonl if decision impact >= 8"
    }
  },
  "ai_context": {
    "conversation_tracking": true,
    "capacity_monitoring": true,
    "alert_threshold": "80%",
    "wai_commands": {
      "time": "Intelligent token usage estimate with capacity warnings",
      "rules": "List active rules and behavioral guidelines",
      "closeout": "Provide updated WAI-State files for session end"
    }
  },
  "environments": {
    "_note": "Registry of environments that have worked on this project. Auto-populated by closeout."
  },
  "meta": {
    "total_sessions": 0,
    "total_turns": 0,
    "last_closeout": null
  }
}

### WAI-State.md.teaching

# Wheel State: [PROJECT_NAME]

---

**Wheelwright Framework v1.0**
**Structure:** v1 (WAI-Spoke/ directory)
**Hub:** *Not yet configured - run `WAI hub create` or `WAI hub locate`*

*This wheel uses Wheelwright Framework to maintain perfect context across AI sessions. Wheelwright transforms AI from order-taker to informed, responsible project partner.*

*"We aren't reinventing the wheel - we're evolving it faster than one person ever could."*

---

## Project Foundation

> **IMPORTANT FOR AI ASSISTANTS:**
>
> If the foundation below is incomplete (shows "Not yet defined"), you MUST guide
> the user through establishing it before starting any work. This is not optional.
>
> Ask conversational questions to extract:
> 1. What is this project? (identity)
> 2. What does success look like? (vision)
> 3. What's in scope and out of scope? (boundaries)
> 4. How do we work together? (approach)

### Identity
- **Type:** *Not yet defined*
- **Name:** *Not yet defined*
- **One-liner:** *Not yet defined*
- **Success looks like:** *Not yet defined*

### Boundaries

**In Scope:**
- *To be defined during foundation setup*

**Out of Scope:**
- *To be defined during foundation setup*

**Constraints:**
- *To be defined during foundation setup*

### Approach
- **Stack/Tools:** *To be defined*
- **Workflow:** *To be defined*
- **AI Collaboration:** *To be defined*
- **Review Process:** *To be defined*

---

## Core Philosophy: AI as Responsible Partner

This wheel follows Wheelwright's stewardship philosophy:

> **AI should enable but remain intentful.** When work strays from the
> established foundation, the AI should flag it and require explicit
> acknowledgment before proceeding.

### Stewardship Behaviors
1. **Detect scope drift** - Flag before enabling work outside boundaries
2. **Require acknowledgment** - Direction changes need explicit approval
3. **Complete foundation first** - Guide setup before diving into work
4. **Prefer verification** - "Are you sure?" over silent compliance

### Evolution, Not Drift
When project direction needs to change, it should be **deliberate**:
- AI detects the drift
- Presents options to user
- User explicitly acknowledges the change
- Change is logged in `evolution_log` with rationale

---

## Hub Memory

### Core Objective
*What transformative purpose does this project serve?*

### Problem Statement
*What specific problem are we solving? Who experiences this pain?*

### Key Decisions
1. *[Decision 1 with rationale]*
2. *[Decision 2 with rationale]*

### Established Constraints
- *[Constraint 1]*
- *[Constraint 2]*

### Learned Patterns
- *[Pattern 1: What worked well]*
- *[Pattern 2: What to avoid]*

---

## Active Spokes

### [Spoke Name]
- **Purpose:** [What this spoke does]
- **Current State:** [What it's working on]
- **Outputs:** [What it has produced]

---

## Rolling Context

### Current Phase
*[What phase is the project in?]*

### Recent Progress
- *[Accomplishment 1]*
- *[Accomplishment 2]*

### Next Actions
1. [ ] Complete project foundation
2. [ ] Define initial scope and approach
3. [ ] Begin work with clear context

### Open Questions
- *[Question needing resolution]*

---

## Evolution Log

| Date | Change | Rationale | Acknowledged By |
|------|--------|-----------|-----------------|
| *Date* | Project initialized with Wheelwright | Starting with context persistence | *User* |

---

## Session Log

| Session | Date | Focus | Key Outcomes |
|---------|------|-------|--------------|
| 1 | [Date] | [Topic] | [Outcomes] |

---

## AI Session Instructions

### Before Starting Work
1. Read `WAI-Guide.md` for current policies
2. Check `_project_foundation.completed` in WAI-State.json
3. **If foundation incomplete: STOP and guide user through setup**
4. Check `_session_state` for recent changes
5. Check boundaries - is this request in scope?

### During Work
- Update `_session_state.last_modified_by` and `last_modified_at`
- Add decisions with impact >= 5 to decisions array
- Signal learnings with impact >= 8 to wheel-signals.jsonl

### Session Continuity Commands
- `'Time'` - Token usage estimate with 80% capacity warnings
- `'Rules'` - List active behavioral guidelines
- `'Closeout'` - Generate updated WAI-State files

---

*This wheel rolls forward with Wheelwright Framework - wheelwright.ai*

### hub-registry.json

{
  "_purpose": "Hub project registry - tracks wheels connected to this hub",
  "_structure_version": "3.0",

  "metadata": {
    "created_at": null,
    "last_updated_at": null,
    "framework_version": "3.0.0",
    "hub_fingerprint": null,
    "description": "Auto-managed registry of wheels taught by this hub"
  },

  "wheels": [
    {
      "_template": "Example wheel entry - delete this after first use",
      "wheel_id": "project-name",
      "spoke_id": "abc123def456",
      "path": "/path/to/project",
      "status": "active",
      "taught_at": "2026-02-01T00:00:00Z",
      "taught_version": "3.0.0",
      "last_sync": "2026-02-01T00:00:00Z",
      "learnings_contributed": 0,
      "signals_received": [],
      "adoptions": [],
      "module_adoption": {
        "lugs": "2.0",
        "registry": "3.0",
        "teach": "1.0",
        "discovery": "1.0",
        "templates": "1.5",
        "analytics": "1.0",
        "quality_gates": "1.0",
        "session": "1.0"
      },
      "pending_contributions": {},
      "adoption_lag": {
        "behind_modules": [],
        "missing_modules": []
      }
    }
  ],

  "teaching_history": [
    {
      "_template": "Teaching event - auto-created by teach command",
      "event_id": "teach-2026-02-01",
      "timestamp": "2026-02-01T00:00:00Z",
      "framework_version": "3.0.0",
      "upgrade_adoption_plan": "upgrade-adoption-plan.json",
      "wheels_taught": 0,
      "files_distributed": [],
      "status": "complete"
    }
  ],

  "statistics": {
    "total_wheels": 0,
    "active_wheels": 0,
    "last_teach": null,
    "total_learnings_received": 0,
    "total_signals_received": 0
  },

  "attention_needed": {
    "_description": "Spokes requiring attention (pending contributions, version lag, etc.)",
    "spokes": []
  },

  "_instructions": {
    "for_teach_command": "Add wheel entries when teaching a spoke. Auto-update on each teach.",
    "for_hub_ai": "Read this to understand which wheels are connected and their teaching history.",
    "manual_editing": "Safe to edit wheel_id, path, and status. Do not edit metadata or timestamps."
  }
}

### hub-security-policy.json

{
  "_purpose": "Hub security policies for safe knowledge distribution",
  "_structure_version": "3.0",

  "metadata": {
    "created_at": null,
    "framework_version": "3.0.0",
    "description": "Security settings for hub-spoke communication and teaching"
  },

  "verification": {
    "enabled": true,
    "algorithm": "sha256-hmac",
    "fingerprint_rotation_days": 90,
    "require_hub_signature": true,
    "require_file_hash_verification": true,
    "description": "All taught files must be signed and verified before adoption"
  },

  "trust_model": {
    "hub_fingerprint": null,
    "public_key": null,
    "key_rotation_schedule": "quarterly",
    "revocation_list": [],
    "description": "Hub signs all upgrade-adoption-plans with its fingerprint"
  },

  "file_integrity": {
    "hash_algorithm": "sha256",
    "verify_file_hashes_before_adoption": true,
    "corrupted_file_action": "reject",
    "description": "Each file includes hash for integrity verification"
  },

  "knowledge_distribution": {
    "allowed_targets": ["spoke", "hub", "universal"],
    "require_explicit_approval": false,
    "min_impact_score_for_sharing": 8,
    "learnings_private_to_hub": false,
    "description": "Control what knowledge is distributed and to whom"
  },

  "wheel_security": {
    "require_wheel_authentication": false,
    "whitelist_enabled": false,
    "whitelisted_wheels": [],
    "require_learning_verification": true,
    "max_learning_size_mb": 100,
    "description": "Security settings for connected wheels"
  },

  "audit_logging": {
    "enabled": true,
    "log_file": "audit.jsonl",
    "log_events": [
      "teach_command",
      "wheel_registration",
      "learning_received",
      "signature_verification",
      "hash_verification_failure"
    ],
    "retention_days": 365,
    "description": "Log all security-relevant events"
  },

  "compliance": {
    "enforce_version_compatibility": true,
    "min_framework_version": "3.0.0",
    "breaking_changes_require_review": true,
    "auto_rollback_on_failure": false,
    "description": "Ensure compatibility and safety during upgrades"
  },

  "secrets_management": {
    "encrypt_sensitive_data": false,
    "allowed_secret_types": ["github_token", "api_key", "ssh_key"],
    "secret_distribution": "never",
    "description": "Secrets should never be distributed; only references"
  },

  "_instructions": {
    "for_hub_ai": "Enforce these policies when creating and distributing upgrade plans. Refuse adoption of unsigned or unverified files.",
    "for_spokes": "Verify all received teaching against these policies before adoption.",
    "updating": "Update after security incidents or when refining trust model. Notify all wheels of policy changes."
  }
}

### AGENTS.md

# Hub AGENTS Instructions

**For:** AI assistants managing this Wheelwright hub  
**Version:** 3.0.0  
**Created:** 2026-02-01

---

## What This Hub Does

This hub serves as the **central knowledge aggregator** for a network of Wheelwright spokes (projects). It:

1. **Distributes Updates** - Teaches framework improvements to all connected projects
2. **Collects Learnings** - Aggregates high-impact insights from all spokes
3. **Improves Itself** - Learns patterns across projects to guide future upgrades
4. **Maintains Registry** - Tracks all connected wheels and their status

---

## Your First Steps

### 1. Read Hub Configuration
```
hub-profile.json
├─ user (your preferences)
├─ hub_config (framework path, settings)
├─ work_style (coding preferences)
└─ learning_philosophy (what to share)
```

### 2. Check Hub Status
```bash
WAI hub status
```

Should show:
- Hub version: 3.0.0
- Framework location: found
- Connected wheels: 0 initially
- Learnings: 0 initially

### 3. Verify Security Setup
```bash
# Check security policies are loaded
ls -la hub-security-policy.json

# Verify upgrade plan verification capability
WAI verify-upgrade upgrade-adoption-plan.json
```

---

## Core Concepts

### Upgrade Adoption Plan (UAP)

**What:** Signed, versioned manifest of framework updates  
**File:** `upgrade-adoption-plan.json`  
**Updated:** Every time hub teaches spokes  
**Structure:**
- `metadata` - Version and framework info
- `verification` - Hub signature and file hashes
- `files` - Spoke template files to teach
- `hub_files` - Hub-specific files for hub itself
- `adoption_guidance` - Recommended adoption order

**Example UAP entry:**
```json
{
  "name": "WAI-Guide.md",
  "version": "3.0.0",
  "changed_from": "2.1.0",
  "why_changed": "Enhanced session start protocol",
  "safe_to_auto_adopt": true,
  "mentions": ["session-start", "teaching"],
  "applies_to": ["spoke", "hub"]
}
```

### Hub-Spoke Unification

**Concept:** Hub and spokes use **identical teach/learn protocol**

**Before v3.1:**
```
Framework → teach → Spokes
Hub ← learn ← Spokes (separate)
```

**Now (v3.1+):**
```
Framework + Hub Templates
        ↓
Upgrade Adoption Plan (signed)
    ↙        ↘
Spokes      Hub
 ↓           ↓
(identical adoption logic)
 ↓           ↓
Hub learns from all
(bidirectional flow)
```

### Lugs (WAI-Lugs.jsonl)

**What:** Universal delivery containers for knowledge, tasks, feedback, and signals  
**Format:** JSONL entries in `hub/WAI-Hub/WAI-Lugs.jsonl` (same as spokes use)  
**Schema:**
```json
{
  "id": "uuid-unique-lug-identifier",
  "created_at": "2026-02-03T10:00:00Z",
  "source_wheel_id": "project-x or hub",
  "destination_wheel_id": "project-y or hub or null (self-lug)",
  "category": "learning|feedback|task|signal|update",
  "priority": 1-5,
  "content": { "...": "lug-specific content" },
  "status": "pending|in_progress|delivered|processed|archived|rejected",
  "expires_at": "2026-03-01T00:00:00Z or null",
  "metadata": { "custom_field": "value", "related_lug_ids": [...] }
}
```

**Categories:**
- `learning` - High-impact insights (impact_score ≥ 8) → aggregated to learnings/*.jsonl
- `feedback` - Hub notifications/responses → stored in hub/WAI-Hub/WAI-Lugs.jsonl
- `task` - Hub tasks triggered by spokes → hub/WAI-Hub/WAI-Lugs.jsonl
- `signal` - Operational signals/events → logged in WAI-State.md
- `update` - Framework/tool updates → processed in next teach cycle

**Push Pattern (Simple & Predictable):**
- Spokes push to hub during TEACH (hub appends to hub/WAI-Hub/WAI-Lugs.jsonl)
- Hub pushes to spokes during TEACH (hub appends to spoke/WAI-Spoke/WAI-Lugs.jsonl)
- Single location per wheel (no outbound/ or inbound/ folders)
- Reconciliation triggered on closeout or explicit `WAI hub reconcile`

### Learning Signals (Inside Lugs)

**What:**

---

*Content truncated - full history available in git*

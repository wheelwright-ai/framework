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
- **AI Collaboration:** YOLO Mode - AI proceeds autonomously, logs decisions retroactively

---

## Core Philosophy: AI as Autonomous Partner

**YOLO MODE ACTIVE** - Wheelwright's autonomous collaboration philosophy:

> **AI proceeds with confidence and full agency.** User trusts AI judgment
> to make implementation decisions directly. Transparency through retroactive
> logging, not through permission-seeking.

### Autonomous Behaviors
1. **Proceed with confidence** - Make decisions and implement directly
2. **Log retroactively** - Record decisions for transparency after implementation
3. **Complete foundation first** - Still required even in YOLO mode
4. **Stay in scope** - Respect boundaries, but use judgment on evolution

### Evolution, Not Chaos
YOLO mode doesn't mean reckless:
- AI still respects project foundation and boundaries
- AI makes reasoned decisions about scope evolution
- AI logs all significant changes in `evolution_log`
- AI only flags truly contradictory requests

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

### Just Completed (2025-12-29)
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
- Run migration script to convert SCF hub and projects
- Rename ~/scf-hub to ~/wheelwright-hub
- Create VS Code extension (wheelwright-ai/extension-vscode)
- Create browser extension (wheelwright-ai/extension-browser)
- Build wheelwright.ai website

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

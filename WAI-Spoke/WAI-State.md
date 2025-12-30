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

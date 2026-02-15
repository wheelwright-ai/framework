# AGENTS.md Architecture Diagram

## System Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                         IDE (User Opens Project)                  │
│                                                                    │
│  Claude Code / Cursor / VS Code / ChatGPT                         │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ Auto-discovers
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      project/AGENTS.md                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ # Project Context: my-awesome-project                      │  │
│  │                                                             │  │
│  │ > **WAI Context Detected**                                 │  │
│  │ > This project uses Wheelwright AI                         │  │
│  │                                                             │  │
│  │ ## Quick Start (Every Session)                             │  │
│  │ 1. Read WAI-Spoke/WAI-Point.json                          │  │
│  │ 2. Read WAI-Spoke/WAI-Guide.md                            │  │
│  │ 3. Check WAI-Spoke/WAI-State.json                         │  │
│  │                                                             │  │
│  │ Phase: Feature Implementation                              │  │
│  │ Last Actions: Implemented auth module                      │  │
│  │ Next Actions: Write tests, Deploy to staging               │  │
│  │ Blockers: None                                             │  │
│  │                                                             │  │
│  │ Updated: 2026-01-31T16:30:00Z                             │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ Provides to AI
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                     AI Assistant (Loaded)                         │
│                                                                    │
│  "I see you're in Feature Implementation phase.                   │
│   Last session you implemented the auth module.                   │
│   Shall we write tests or prepare for staging deployment?"        │
│                                                                    │
│  ✓ Full context loaded automatically                             │
│  ✓ No manual context pasting needed                              │
│  ✓ Ready for autonomous operation                                │
└──────────────────────────────────────────────────────────────────┘
```

## Creation Flow (On Init)

```
User Command: WAI init my-project
     │
     ▼
┌─────────────────────────────────┐
│ wai_cli/init.py                 │
│ init_spoke() function           │
└─────────┬───────────────────────┘
          │
          ├─→ Create WAI-Spoke/ directory
          │
          ├─→ Copy template files
          │   (WAI-Guide.md, WAI-State.json, etc.)
          │
          └─→ NEW: Copy AGENTS.md template
              │
              ▼
          ┌─────────────────────────────────┐
          │ templates/wheel/AGENTS.md       │
          │ (Template with placeholders)    │
          └─────────┬───────────────────────┘
                    │
                    ▼
          ┌─────────────────────────────────┐
          │ Substitute placeholders:        │
          │ - {{PROJECT_NAME}}              │
          │ - {{TIMESTAMP}}                 │
          │ - {{CURRENT_PHASE}}             │
          │ - {{STATUS}}                    │
          │ - {{NEXT_ACTIONS}}              │
          │ - {{BLOCKERS}}                  │
          └─────────┬───────────────────────┘
                    │
                    ▼
          ┌─────────────────────────────────┐
          │ my-project/AGENTS.md            │
          │ (Project-specific, ready)       │
          └─────────────────────────────────┘
```

## Update Flow (On Closeout)

```
User Command: WAI shipit (or WAI closeout)
     │
     ▼
┌──────────────────────────────────────┐
│ wai_cli/closeout.py                  │
│ process_closeout() function          │
└─────────┬────────────────────────────┘
          │
          ├─→ Run quality gates
          ├─→ Validate policies
          ├─→ Rebalance files
          ├─→ Extract signals
          │
          └─→ Step 10: Refresh integrations
              │
              ▼
          ┌──────────────────────────────────┐
          │ wai_cli/agents_integration.py    │
          │ AgentsIntegration class          │
          │ refresh_agents_md() method       │
          └─────────┬────────────────────────┘
                    │
                    ▼
          ┌──────────────────────────────────┐
          │ Read: project/WAI-Spoke/         │
          │       WAI-State.json             │
          │                                  │
          │ Extract:                         │
          │ - context.current_phase          │
          │ - context.next_actions           │
          │ - context.blockers               │
          │ - _session_state.last_closeout   │
          └─────────┬────────────────────────┘
                    │
                    ▼
          ┌──────────────────────────────────┐
          │ Update: project/AGENTS.md        │
          │                                  │
          │ - {{TIMESTAMP}} → now            │
          │ - {{CURRENT_PHASE}} → extracted  │
          │ - {{NEXT_ACTIONS}} → extracted   │
          │ - {{BLOCKERS}} → extracted       │
          │ - {{STATUS}} → Ready/Blocked     │
          │ - {{LAST_ACTIONS}} → from log    │
          └─────────┬────────────────────────┘
                    │
                    ▼
          ┌──────────────────────────────────┐
          │ Continue closeout:               │
          │ - Git commit                     │
          │ - Generate WAI-Point.json        │
          │ - Final summary                  │
          └──────────────────────────────────┘
```

## Component Architecture

```
┌────────────────────────────────────────────────────────┐
│              templates/wheel/AGENTS.md                  │
│  Single source of truth for AGENTS.md structure         │
└────┬─────────────────────────────────────────────────┬─┘
     │                                                 │
     │ Used by                                         │ Used by
     ▼                                                 ▼
┌──────────────────┐                        ┌──────────────────────┐
│   wai_cli/       │                        │   wai_cli/           │
│   init.py        │                        │   agents_             │
│                  │                        │   integration.py     │
│ On init:         │                        │                      │
│ Copy template    │                        │ On closeout:         │
│ Apply initial    │                        │ Read state           │
│ substitutions    │                        │ Update values        │
└────┬─────────────┘                        └──────┬───────────────┘
     │                                            │
     └────────────┬─────────────────────────────┬─┘
                  ▼
          ┌──────────────────┐
          │  project/        │
          │  AGENTS.md       │
          │                  │
          │ [Always current] │
          │ [Updated every   │
          │  closeout]       │
          │ [Read by all     │
          │  IDEs]           │
          └──────────────────┘
```

## State Machine

```
                    ┌─────────────┐
                    │   Project   │
                    │ Not Initialized
                    └──────┬──────┘
                           │
                    WAI init <project>
                           │
                           ▼
                    ┌──────────────────┐
                    │ AGENTS.md Created │
                    │ (Initial state)   │
                    └──────┬────────────┘
                           │
                     IDE Opens Project
                           │
                           ▼
                    ┌──────────────────┐
                    │ IDE Reads AGENTS │
                    │ AI Loads Context │
                    └──────┬────────────┘
                           │
                      Work Session
                           │
                    WAI shipit / closeout
                           │
                           ▼
                    ┌──────────────────┐
                    │ AGENTS.md Updated │
                    │ (Refreshed state) │
                    └──────┬────────────┘
                           │
                     IDE Opens Again
                           │
                           ▼
                    ┌──────────────────┐
                    │ IDE Reads Updated │
                    │ AI Loads Fresh    │
                    │ Context           │
                    └────────┬──────────┘
                             │
                      Repeat: Work → Closeout → IDE Open...
```

## Integration Points

### 1. IDE Discovery (Input)
```
IDE reads:   project/AGENTS.md
Provides:    Content to AI
Trigger:     Automatic on project open
Format:      Markdown plain text
```

### 2. Initialization (Output)
```
Called by:   wai_cli/init.py::init_spoke()
Creates:     project/AGENTS.md
Source:      templates/wheel/AGENTS.md
Applies:     Initial substitutions
Result:      Fresh AGENTS.md with project info
```

### 3. Closeout Refresh (Output)
```
Called by:   wai_cli/closeout.py::_refresh_integrations()
Module:      wai_cli/agents_integration.py
Method:      AgentsIntegration.refresh_agents_md()
Reads:       project/WAI-Spoke/WAI-State.json
Updates:     project/AGENTS.md
Result:      Fresh context for next session
```

## Data Flow

```
WAI-State.json                    Init Process
     │                                │
     │    ┌─────────────────────────┬─┘
     │    │                         │
     ▼    ▼                         ▼
   ┌───────────────┐    ┌──────────────────┐
   │ Session State │    │ Template File    │
   │ Phase         │    │ (wheel/AGENTS)   │
   │ Actions       │    │                  │
   │ Blockers      │    └────────┬─────────┘
   │ Last session  │             │
   └────┬──────────┘             │
        │                        │
        └────────┬───────────────┘
                 │
         Substitution Process
                 │
                 ▼
        ┌─────────────────┐
        │  AGENTS.md      │
        │  Generated/     │
        │  Updated        │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ IDE Reads File  │
        │ Provides to AI  │
        │ AI Loads Context│
        └─────────────────┘
```

## Files & Modules

```
Framework Root
├── templates/
│   └── wheel/
│       └── AGENTS.md                    ← Template
├── wai_cli/
│   ├── agents_integration.py            ← New module
│   ├── init.py                          ← Modified
│   └── closeout.py                      ← Modified
├── tests/
│   └── test_agents_integration.py       ← New tests
├── docs/
│   └── AGENTS-MD-INTEGRATION.md         ← Documentation
├── WAI-Spoke/
│   ├── WAI-State.json                   ← Updated
│   └── WAI-State.md                     ← Updated
└── Project Root (After Init)
    ├── AGENTS.md                         ← Generated per project
    ├── WAI-Spoke/
    │   ├── WAI-State.json
    │   ├── WAI-Guide.md
    │   └── ...
    └── [project files]
```

---

**This architecture ensures WAI is always visible to IDEs while remaining invisible to users - just infrastructure that works.**

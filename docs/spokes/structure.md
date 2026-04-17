# Spoke Structure

A spoke is a WAI extension for a specific project. It inherits policies from the Hub and maintains local state, Lugs, and configuration.

## Purpose

Each spoke:
1. **Defines project-specific behavior** via BRIEF.md and EXTENSION.md
2. **Tracks local work** via WAI-Lugs.jsonl
3. **Maintains session continuity** via WAI-Ledger.jsonl
4. **Submits learnings** to Hub for cross-project sharing

## Directory Structure

```
your-project/
├── BRIEF.md              # Project behavioral rules (inherits hub/BRIEF.md)
├── EXTENSION.md          # Role and lens definition
├── skills/               # Project-specific skills (optional)
└── WAI-Spoke/
    ├── WAI-Manifest.yaml # Node configuration
    ├── WAI-Lugs.jsonl    # Local work log
    ├── WAI-Ledger.jsonl  # Session commitments
    └── WAI-State.json    # Runtime state (optional)
```

## Core Files

### BRIEF.md

Project-specific behavioral rules that inherit from hub/BRIEF.md:

```markdown
# BRIEF — your-project

**BRIEF Cascade:** This file inherits rules from hub/BRIEF.md

## Always
- [Project-specific rule 1]
- [Project-specific rule 2]

## Never
- [Project-specific prohibition]

## When Uncertain
- [Project-specific clarification source]
```

### EXTENSION.md

Defines the spoke's identity and perspective:

```markdown
# your-project Extension

## Identity

**Role:** [Your role - CTO, PM, QA, etc.]
**Lens:** [Your perspective - what you focus on]

**Primary Focus:**
- [Key responsibility 1]
- [Key responsibility 2]

## Behaviors

### Always
- [Role-specific behavior]

### Never
- [Role-specific prohibition]

## Skills Loaded

- safe-refactor (guardian)
- session-observer (watcher)
- [custom-skill] (reviewer)

## Offers

What this extension produces:
- [Output type 1]
- [Output type 2]

## Subscribes To

What this extension watches for:
- hub:framework:* (framework updates)
- hub:pattern:* (cross-spoke patterns)
```

### WAI-Manifest.yaml

Node configuration and framework state:

```yaml
node_type: spoke
node_path: "your-org/your-project"
framework_version: "2.0.0"
template_versions:
  lugs: 2
  brief: 1
  guide: 1
hub_lug_cursor: null        # Last processed hub Lug
skills_loaded:
  - safe-refactor
  - session-observer
last_session: null
outbound_pending: []        # Signals waiting for hub processing
file_load_policy:           # Optional: selective file loading
  load_always:
    - "src/core/*.py"
  load_on_demand:
    - "tests/*.py"
  never_load:
    - "reference/**/*"
```

### WAI-Lugs.jsonl

Append-only log of all work items:

```jsonl
{"id":"lug-2026-02-14-001","type":"diagnosis","title":"Bug in auth handler","status":"published","impact":7,...}
{"id":"lug-2026-02-14-002","type":"prescription","title":"Fix auth handler","diagnosis_id":"lug-2026-02-14-001",...}
{"id":"lug-2026-02-14-003","type":"decision","title":"Chose JWT over sessions","alternatives_considered":[...],...}
```

### WAI-Ledger.jsonl

Session commitment tracking:

```jsonl
{"id":"led-001","type":"request","content":"Add user authentication","status":"open",...}
{"id":"led-002","type":"agreement","content":"Will implement JWT auth","references":"led-001",...}
{"id":"led-003","type":"delivery","content":"JWT auth implemented","commit":"abc123","status":"fulfilled",...}
```

## Spoke Wakeup Flow

When opening a spoke project:

1. Agent reads BRIEF.md (behavioral rules)
2. Agent reads EXTENSION.md (role and lens)
3. Agent reads WAI-Manifest.yaml (framework config)
4. `hub-watcher` skill fires (if node_type == "spoke"):
   - Checks hub for framework updates
   - Auto-applies patch updates (2.0.0 → 2.0.1)
   - Notifies about minor/major updates (2.0.0 → 2.1.0)
   - Pulls pending signals from hub
5. Agent reads WAI-Ledger.jsonl for open commitments
6. Agent is briefed and ready to work

## Spoke Closeout Flow

When ending a session:

1. `session-observer` skill fires
2. Reconciles WAI-Ledger.jsonl (flags unfulfilled commitments)
3. Checks if framework files changed (flags doc updates needed)
4. Creates session summary Lug
5. Agent reports closeout status

## Cross-Node Communication

### Submitting to Hub

When a spoke creates a high-impact Lug (impact >= 8):

1. Lug written to local WAI-Lugs.jsonl
2. Lug copied to `hub/intake/{node-path}/{lug-id}.yaml`
3. Added to WAI-Manifest.yaml `outbound_pending`
4. On next spoke wakeup, hub-watcher checks if hub processed it

### Receiving from Hub

When hub has new signals for this spoke:

1. hub-watcher reads hub/health.yaml for pending signals
2. Pulls signals matching spoke's subscription patterns
3. Creates local Lugs with `source_id` pointing to hub Lug
4. Updates WAI-Manifest.yaml `hub_lug_cursor`

## Spoke Types

### Active Spoke
```yaml
node_type: spoke
status: active
```
Full functionality, receives updates, submits signals.

### Archived Spoke
```yaml
node_type: spoke
status: archived
```
Read-only reference, minimal skills, no signal submission.

## Best Practices

1. **Keep BRIEF.md focused** - Only add rules specific to this project
2. **Define clear lens** - EXTENSION.md should explain your unique perspective
3. **Create Lugs as you work** - If you didn't write a Lug, it didn't happen
4. **Use the ledger** - Track commitments to survive context loss
5. **Submit high-impact learnings** - Share patterns that benefit other projects

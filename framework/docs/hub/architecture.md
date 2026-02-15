# Hub Architecture

The Hub is the central node in WAI's hub-and-spoke model. It stores wheel-wide policies, aggregates cross-project learnings, and distributes patterns to all spokes.

## Purpose

The Hub serves three functions:

1. **Policy Authority** - Defines wheel-wide rules via `hub/BRIEF.md`
2. **Learning Aggregator** - Collects high-impact Lugs from all spokes
3. **Pattern Distributor** - Broadcasts learnings back to spokes

## Directory Structure

```
hub/
├── BRIEF.md              # Wheel-wide policies (inherited by all spokes)
├── WAI-Integrity.md      # Data protection contract
├── WAI-Lugs.jsonl        # Hub-level Lugs (patterns, decisions, learnings)
├── WAI-Ledger.jsonl      # Hub commitments ledger
├── registry.yaml         # All registered nodes (spokes + hub)
├── health.yaml           # Hub health status
└── intake/               # Pending signals from spokes
    ├── {node-path}/      # Signals organized by source spoke
    └── processed/        # Processed signals (moved after processing)
```

## BRIEF Cascade

Policies cascade from Hub to spokes:

```
hub/BRIEF.md (wheel-wide policies)
  ↓ Inherited by all projects
Project BRIEF.md (project-specific policies)
  ↓ Inherited by all extensions
Spoke BRIEF.md (spoke-specific policies)
```

**Inheritance Rules:**
- Lower levels can ADD more specific rules
- Lower levels can NARROW rules (make more restrictive)
- Lower levels CANNOT REMOVE or CONTRADICT hub rules

## Intake Processing

Spokes submit high-impact Lugs (impact >= 8) to `hub/intake/`:

1. Spoke creates Lug with impact >= 8
2. Spoke copies Lug to `hub/intake/{spoke-path}/{lug-id}.yaml`
3. Hub wakeup triggers `hub-processor` skill
4. hub-processor reads intake, creates hub Lugs
5. Moves processed signals to `hub/intake/processed/`

## Cross-Spoke Pattern Detection

hub-processor detects patterns across spokes:

- **Recurring diagnosis** - Same issue in 2+ projects → observation Lug
- **Common preference** - Same style preference across spokes → flag for BRIEF update
- **Architecture convergence** - Similar patterns adopted independently → learning Lug
- **Template gap** - Multiple spokes created similar files → suggest framework template

## Hub Health

`hub/health.yaml` tracks:

```yaml
intake_pending: 5          # Unprocessed signals in intake/
oldest_pending: "2026-02-14T00:00:00Z"
spokes_outdated: 2         # Spokes on old framework version
patterns_detected: 3       # Cross-spoke patterns this session
last_processed: "2026-02-14T05:00:00Z"
```

## Hub Wakeup Flow

On hub session start:

1. `hub-processor` skill fires (node_type == "hub")
2. Processes all files in `hub/intake/`
3. Detects cross-spoke patterns
4. Checks spoke health from `hub/registry.yaml`
5. Updates `hub/health.yaml`
6. Reports: "{N} signals processed, {P} patterns detected"
7. Suggests: "Use /wai-teach to consolidate learnings"

## Registry

`hub/registry.yaml` tracks all nodes:

```yaml
nodes:
  - path: "wheelwright/hub"
    type: hub
    status: active
    framework_version: "2.0.0"

  - path: "your-org/project-1"
    type: spoke
    status: active
    framework_version: "2.0.0"

  - path: "archive/old-project"
    type: spoke
    status: archived
    framework_version: "2.0.0"
```

## Hub vs Spoke Responsibilities

| Responsibility | Hub | Spoke |
|----------------|-----|-------|
| Define wheel-wide policies | ✓ | ✗ (inherits) |
| Process intake signals | ✓ | ✗ |
| Detect cross-spoke patterns | ✓ | ✗ |
| Track spoke health | ✓ | ✗ |
| Create local Lugs | ✓ | ✓ |
| Submit high-impact signals | ✗ (receives) | ✓ |
| Auto-upgrade framework | ✗ (source) | ✓ (patches) |

## Data Protection

Hub data is protected by `hub/WAI-Integrity.md`:

- `hub/BRIEF.md` - Modifiable via decision Lug + commit
- `hub/WAI-Integrity.md` - Read-only (conductor approval for changes)
- `hub/WAI-Lugs.jsonl` - Append-only
- `hub/intake/` - Append-only (processed moves to processed/)

See [WAI-Integrity.md](../../hub/WAI-Integrity.md) for full protection rules.

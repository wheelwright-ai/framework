# Glossary

## Core Concepts

### Lug
An actionable record representing decomposed, meaningful work. Every diagnosis, prescription, decision, and observation is a Lug. If an agent didn't write a Lug, it didn't happen.

### Skill
A sub-agent with a defined contract. Each skill declares what it does, when it fires, what model it needs, and what it produces.

### Hub
The central node in WAI's hub-and-spoke model. Stores wheel-wide policies, aggregates cross-project learnings, distributes patterns to spokes.

### Spoke
A WAI extension for a specific project. Inherits policies from Hub, maintains local state, Lugs, and configuration.

### Conductor
The human directing the agent colony. Makes final decisions, approves destructive operations, provides strategic direction.

### Wheel
A complete WAI installation: one hub + multiple spokes. Named after the framework (Wheelwright).

### Node
Any component in the WAI network. Can be a hub or a spoke.

### BRIEF
Behavioral rules document. Defines Always/Never/When Uncertain rules. Cascades from hub to project to spoke.

### EXTENSION
Identity document for a spoke. Defines Role, Lens, Primary Focus, Skills Loaded, Offers, and Subscriptions.

### Manifest
Node configuration file (WAI-Manifest.yaml). Contains node_type, node_path, framework_version, skills_loaded, etc.

### Ledger
Session commitment tracking (WAI-Ledger.jsonl). Append-only log of requests, agreements, and deliveries.

### Intake
Hub directory (hub/intake/) where spokes submit high-impact Lugs for processing.

---

## Lug Types

### Task
Work to be done. "Migrate auth from JWT to sessions"

### Diagnosis
Problem identified by a sub-agent. "SQL injection in auth handler"

### Prescription
Recommended fix attached to a diagnosis. "Parameterize query at line 47"

### Decision
A judgment call made by the conductor. "Accepted risk on X because Y"

### Observation
Event or pattern worth recording. "Test coverage dropped to 73%"

### Preference
Communication style or workflow preference. "User prefers terse confirmations"

### Signal
High-impact Lug (impact >= 8) relevant to other nodes. Submitted to hub/intake/.

### Update
Framework or template version change notification.

### Session
Session synthesis — human-readable summary of a work session.

---

## Skill Roles

### Guardian
Pre-emptive protection. Fires before risky operations to create safety checkpoints.
Example: `safe-refactor`

### Reviewer
Quality assurance. Fires after changes to validate correctness.
Example: `qc-check`, `security-review`

### Advisor
Guidance and warnings. Fires when thresholds crossed or patterns detected.
Example: `complexity-advisor`, `context-advisor`

### Watcher
Observation and synthesis. Fires on session events to track and summarize.
Example: `session-observer`, `hub-watcher`

---

## PEV Pattern

**P**erceive / **E**xecute / **V**erify

Optional structured execution context for complex Lugs:

### Perceive
What to look at and what "wrong" looks like.
- `look_at`: Files/patterns to examine
- `current_state`: What's wrong now
- `success_state`: What "fixed" looks like

### Execute
What actions to take and constraints.
- `approach`: How to fix
- `constraints`: What not to change
- `avoid`: Patterns to avoid

### Verify
How to confirm success.
- `commands`: Tests to run
- `expected_output`: What success looks like
- `manual_check`: Human verification steps

---

## Impact Scoring

### 1-3: Local
Visible only within the creating node.
"Refactored helper function"

### 4-7: Project-wide
Visible to other extensions in the same project.
"API contract changed"

### 8-10: Wheel-wide (Signal)
Copied to Hub intake, visible to all spokes.
"Architecture pattern applicable across projects"

---

## Lifecycle States

### Lug Lifecycle
```
draft → published → acknowledged → in_progress → resolved
```

### Ledger Entry Lifecycle
```
request → agreement → delivery → verification
            ↗               ↗
     clarification    amendment
```

---

## File Types

### .jsonl
JSON Lines format. One JSON object per line. Used for WAI-Lugs.jsonl, WAI-Ledger.jsonl.

### .yaml
YAML format. Used for skills (*.yaml), manifests (WAI-Manifest.yaml), registry (registry.yaml).

### .md
Markdown format. Used for documentation, BRIEF.md, EXTENSION.md, specs.

---

## Cascade

The inheritance pattern where policies flow from hub to spoke:

```
hub/BRIEF.md (wheel-wide)
  ↓ inherited by
Project BRIEF.md (project-specific)
  ↓ inherited by
Spoke BRIEF.md (spoke-specific)
```

Lower levels can ADD and NARROW, but cannot REMOVE or CONTRADICT.

---

## Integrity Rules

### Read-Only
Files that cannot be modified. Framework core files.

### Append-Only
Files where content can only be added, never deleted. WAI-Lugs.jsonl, WAI-Ledger.jsonl.

### Scoped Write
Files that can be modified but only within defined scope. Spoke writes only to its own directory.

### Human Gate
Operations requiring explicit conductor approval. Destructive operations (delete, reset).

---

## Model Tiers

### Lightweight
Fast, cheap models for simple operations.
Examples: Haiku, Gemini Flash

### Standard
Balanced models for code analysis.
Examples: Sonnet, Gemini Pro

### Advanced
Expensive models for complex reasoning.
Examples: Opus, o1-pro

# Hub-Level Policies (Inherited by All Spokes)

**BRIEF Cascade:** This file defines wheel-wide policies. All projects and spokes inherit these rules.

---

## BRIEF Cascade Architecture

```
Hub BRIEF (this file)
  ↓ Inherited by all projects
Project BRIEF
  ↓ Inherited by all extensions in that project
Spoke BRIEF
```

**Inheritance Rules:**
- **Can ADD:** Lower levels can add more specific rules and context
- **Can NARROW:** Lower levels can make rules MORE restrictive
- **Cannot REMOVE:** Lower levels cannot remove or relax hub-level rules
- **Cannot CONTRADICT:** If hub says "must," spoke cannot say "optional"

**Example:**
- Hub: "All security findings resolved within 72 hours"
- Project: "For payment code, resolve within 24 hours" (narrower, allowed)
- Spoke: "Security findings can wait a week" (contradicts hub, NOT allowed)

---

## Wheel-Wide Policies

### Data Protection

1. **WAI-Integrity.md is law.** All agents honor the data protection rules defined in hub/WAI-Integrity.md
2. **safe-refactor before structural changes.** Checkpoint commits required before file restructuring
3. **Lugs and ledgers are append-only.** Never delete lines from WAI-Lugs.jsonl or WAI-Ledger.jsonl
4. **Destructive ops require human gate.** Deleting data requires conductor approval

### Quality Standards

1. **All work produces Lugs.** If an agent didn't write a Lug, it didn't happen
2. **Skills execute defined contracts.** Sub-agents follow their Skill definitions
3. **Session closeout is mandatory.** Every session ends with session-observer synthesis
4. **Cross-node communication via intake.** Spokes submit to hub/intake/, Hub processes asynchronously

### Framework Updates

1. **Framework version cascade:** Hub checks framework updates → broadcasts to spokes → spokes apply safe changes automatically
2. **Breaking changes require review:** framework-updater creates Lugs for breaking template changes
3. **Template version tracking:** Every node manifest records template versions in use

### Learning & Calibration

1. **Decisions become institutional memory.** Decision Lugs capture conductor judgment for future reference
2. **Dismissed diagnosis patterns trigger calibration.** If a Skill's findings are consistently dismissed, brief-advisor flags it
3. **Apprenticeship over time.** Sub-agents learn conductor preferences from decision Lug history

---

## Node-Specific Overrides

Projects and spokes may add context-specific rules in their own BRIEF files:

- Project-specific quality thresholds (test coverage %, performance targets)
- Extension-specific behaviors (lenses, interpretive frames)
- Workflow preferences (when to run expensive checks, approval gates)

**But:** Project and spoke BRIEFs inherit everything above. If there's a conflict, hub rules win.

---

## Updating Hub BRIEF

Changes to this file require:

1. Decision Lug proposing the change (with reasoning and alternatives considered)
2. Git commit documenting the change
3. Decision Lug marked resolved with commit hash
4. All spokes see the update on next hub-watcher run

Hub BRIEF evolution is explicit, recorded, and traceable.

---

## For Agents: How to Use This

On wakeup, the composite briefing includes:
1. Hub BRIEF (this file) — wheel-wide rules
2. Project BRIEF (if in a project context) — project-specific additions
3. Spoke BRIEF (your operational directives) — your specific instructions

**Read all three in order.** The cascade stacks. Your spoke BRIEF refines the foundation, doesn't replace it.

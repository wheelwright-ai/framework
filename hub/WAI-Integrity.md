# WAI Integrity Contract

**Version:** 1.0.0
**Created:** 2026-02-12
**Purpose:** Data protection rules that prevent Hub destruction and ensure safe agent operations
**Origin:** This contract exists because of the 2026-02-10 Hub folder destruction incident

---

## Philosophy

This contract exists to prevent data loss. Every rule below is rooted in a real failure mode. Agents MUST honor these rules. Violations result in Lugs that surface to the conductor.

**Core Principle:** Agents communicate through files. Files are permanent. Destruction is preventable.

---

## Read-Only Paths

These paths MUST NOT be modified by any agent except through explicit conductor approval:

```
framework/**               — Framework templates and base definitions
hub/WAI-Integrity.md       — This file (self-protecting)
**/*.v1-backup             — All backup files from migrations
hub/machines/*.lug.json    — Machine profiles (managed by system)
```

**Rule:** If an agent needs to update framework templates, it creates a Lug requesting conductor approval first. Framework updates follow the template upgrade pattern (WAI-UPGRADE.yaml → phases → Lug → file deleted).

---

## Append-Only Paths

These files grow but NEVER shrink. Lines are added, never removed:

```
**/WAI-Lugs.jsonl          — All Lug files (every node)
**/WAI-Ledger.jsonl        — Session ledger (commitments tracking, every node)
hub/intake/**/*.yaml       — Intake submissions (moved to processed/ when done)
```

**Session Ledger:** WAI-Ledger.jsonl tracks requests, agreements, and deliveries. It exists to prevent premature completion declarations and survive context loss. Every commitment is file-permanent.

**Rule:** Agents write new lines. Agents NEVER delete lines, even if they look wrong. If a Lug needs correction, create a new Lug referencing the original. The history is the value.

**Violation Example:** Deleting a "bad" Lug to hide a mistake. Don't. Create a correction Lug instead.

---

## Scoped Write Access

Each agent operates within its node. Cross-node writes go through intake:

```
Hub agents:
  - Can read: hub/**, registry/**/PROJECT.md, framework/**
  - Can write: hub/** (except read-only paths above)
  - Cannot write: Any spoke directories directly

Spoke agents:
  - Can read: own spoke directory, hub/** (read-only), framework/** (read-only)
  - Can write: own spoke directory only
  - Can submit to: hub/intake/{node-path}/
  - Cannot write: hub/** directly, other spokes
```

**Rule:** If a spoke needs to communicate with Hub, it writes a Lug to its local WAI-Lugs.jsonl AND copies that Lug to hub/intake/{node-path}/{lug-id}.yaml. Hub processes intake on its next wakeup.

**Violation Example:** A spoke agent directly editing hub/WAI-Lugs.jsonl. Don't. Use intake.

---

## Pre-Refactor Rule (Critical)

**BEFORE any structural file operation, the safe-refactor Skill MUST fire.**

Structural operations include:
- Moving files or directories
- Renaming files or directories
- Deleting files or directories
- Restructuring folder hierarchies
- Migrating data between formats

**safe-refactor ensures:**
1. Git working directory is clean (all changes committed)
2. Current state is committed with descriptive message: "WAI safe-refactor checkpoint: {context}"
3. Checkpoint commit hash is recorded in a Lug
4. If the refactor breaks something, `git revert {hash}` recovers instantly

**This rule exists because:** On 2026-02-10, a rogue agent restructured the hub folder without checkpointing. The Hub data was lost. No recovery point existed. This MUST NOT happen again.

**Enforcement:** safe-refactor is a guardian Skill with `can_be_skipped: false`. It runs on `pre_refactor` event. Any agent attempting structural changes without triggering safe-refactor creates a violation Lug.

---

## Destructive Operation Policy

Operations that delete data require:
1. **Checkpoint** (safe-refactor)
2. **Human gate** (agent proposes, conductor approves, then execute)
3. **Lug record** (observation Lug documenting what was deleted and why)

Destructive operations include:
- Deleting files (except temporary or generated files with clear temp/cache semantics)
- Truncating logs
- Removing Lugs
- Clearing state files

**Exemptions** (no human gate needed):
- Deleting `.pyc`, `__pycache__`, `node_modules`, `.next`, `dist/`, `build/` — clearly regenerable
- Deleting files marked as temporary (e.g., WAI-UPGRADE.yaml after conversion to Lug)
- Cleaning git-ignored files

**Rule:** If you're unsure whether something is destructive, ask the conductor before deleting.

---

## Migration & Upgrade Pattern

When upgrading templates, migrating schemas, or performing structural changes:

1. Create state tracking file at repo root: `WAI-MIGRATION.yaml` or `WAI-UPGRADE.yaml`
2. Execute phases, updating state file after each phase
3. On completion, convert state file into a decision Lug capturing the full record
4. Delete the state file (data lives in the Lug now)

**This pattern applies at all scales:**
- Framework-wide migrations (v1 → v2)
- Node-level template upgrades (template v2 → v3)
- Individual Skill version updates

**The state file is append-only during migration.** Phases are recorded, never removed.

---

## Session Ledger Protection

`WAI-Ledger.jsonl` is append-only and survives context loss.

**Rules:**
- Agents write request, agreement, delivery, verification entries
- Entries are NEVER deleted or edited
- If a commitment changes, write an amendment entry
- Ledger reconciliation happens on session close (part of closeout)
- Unfulfilled commitments are surfaced on next session wakeup

**This exists because:** During WAI v2 migration, token exhaustion caused context loss. The agent reconstructed intent incorrectly and declared completion prematurely. The ledger prevents this by making commitments file-permanent.

---

## Violation Handling

When an agent detects an integrity violation (by itself or another agent):

1. **Stop the operation** (if possible)
2. **Create a violation Lug:**
   ```yaml
   type: observation
   severity: critical
   title: "Integrity violation: {what happened}"
   evidence: "{which rule was broken, what file/path was affected}"
   category: integrity
   impact: 9
   ```
3. **Surface to conductor** (violation Lugs are high-impact, appear in wakeup briefing)
4. **Session summary includes violations** (part of session-observer Skill output)

**The conductor decides:**
- Was this a legitimate exception?
- Does the rule need refinement?
- Was it a bug or misunderstanding?
- Should the operation be retried correctly?

**Agents don't punish violations. Agents record and surface them.** The conductor is the final authority.

---

## Wakeup Integration

On every spoke/Hub wakeup:

1. integration-check Skill verifies IDE integration files (CLAUDE.md, .cursorrules)
2. hub-watcher checks for Hub updates and intake acknowledgments
3. safe-refactor guardian is loaded and ready for pre_refactor triggers
4. Integrity rules are injected into the composite briefing (Section 1: Agent Primer)

**This ensures:** Every agent session starts with awareness of these rules, even if the agent has never seen them before.

---

## Amendment Process

If a rule in this contract needs to change:

1. Conductor creates a decision Lug proposing the amendment
2. Decision Lug documents: what rule, why it should change, what the new rule would be
3. Amendment is applied to WAI-Integrity.md
4. Git commit: "WAI Integrity: Amendment — {one-line summary}"
5. Decision Lug is marked resolved with commit hash

**This contract is not immutable. It evolves.** But evolution is explicit, recorded, and traceable.

---

## Summary: The Unbreakable Rules

1. ✅ Framework files are read-only (except via upgrade pattern)
2. ✅ Lugs and ledgers are append-only (never delete lines)
3. ✅ Spokes write to their own directory only (cross-node via intake)
4. ✅ safe-refactor fires before structural changes (no exceptions)
5. ✅ Destructive ops require checkpoint + human gate + Lug
6. ✅ Violations are recorded and surfaced, not hidden

**When in doubt, stop and ask.**

The Hub was destroyed once. It will not be destroyed again.

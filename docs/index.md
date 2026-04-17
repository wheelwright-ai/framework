# Meet Wheelwright

This docs tree is now the public documentation surface for the framework remodel.
Some pages still describe older layouts; use the repo root README plus the cutover
documents when you need the current public/private boundary.

**Wheelwright** is an agent communication protocol for multi-AI collaboration. It's how AI agents talk to each other, show their work, and build institutional memory — without destroying your data.

---

## What Problem Does This Solve?

AI coding agents are powerful, but they have problems:

1. **They don't show their work.** You ask for a feature, code appears, but you don't know what was considered or why.
2. **They don't remember across sessions.** Every conversation starts from zero. No learning, no institutional memory.
3. **They can destroy data.** Agents have restructured folders, deleted files, and broken systems — with no undo button.
4. **They don't collaborate.** One agent can't hand off work to another. No specialization, no division of labor.

Wheelwright fixes this.

---

## How It Works

Wheelwright has two primitives: **Skills** and **Lugs**.

### Skills = Agents with Contracts

A **Skill** is a sub-agent with a defined job. Each Skill declares:
- What it does
- When it fires (on load, on commit, on demand)
- What it reads and writes
- What model it needs (lightweight, standard, advanced)
- What it produces (Lugs)

**Examples:**
- `safe-refactor` (guardian) — checkpoints git before structural changes
- `qc-check` (reviewer) — runs tests, diagnoses failures
- `security-review` (reviewer) — scans for vulnerabilities
- `brief-advisor` (advisor) — detects contradictions between stated policies and actual behavior

Skills are **cheap, specialized agents**. The expensive main coding agent doesn't do everything — it orchestrates sub-agents.

### Lugs = Structured Work Items

A **Lug** is an actionable record. Every diagnosis, prescription, decision, and observation is a Lug.

**Lug types:**
- `diagnosis` — Problem identified ("SQL injection in auth handler")
- `prescription` — Recommended fix ("Parameterize query at line 47")
- `decision` — Judgment call made ("Chose JWT over sessions because...")
- `observation` — Event worth recording ("Test coverage dropped to 73%")
- `task` — Work to be done ("Migrate auth from JWT to sessions")
- `signal` — High-impact Lug (impact ≥ 8) relevant to other projects

**If an agent didn't write a Lug, it didn't happen.**

Lugs are the audit trail. They're how agents show their work, communicate across sessions, and build institutional memory.

---

## Architecture: Hub and Spokes

Wheelwright uses a **hub-and-spoke** model:

```
Hub (shared memory across all projects)
  ├── Spoke: Project A / Extension 1
  ├── Spoke: Project A / Extension 2
  ├── Spoke: Project B / Extension 1
  └── Spoke: Project C / Extension 1
```

- **Hub:** Shared learning, policies, patterns
- **Spoke:** Per-project extension with local state
- **Extension:** A role/lens (CTO, PM, QA, Security, etc.)

**Cross-node communication:** Spokes submit high-impact Lugs to `hub/intake/`. Hub processes them asynchronously and broadcasts learnings back to all spokes.

---

## Data Protection: WAI-Integrity.md

Agents follow **WAI-Integrity.md** rules:

1. **Read-only paths:** Framework files can't be modified directly
2. **Append-only paths:** Lugs and ledgers grow, never shrink
3. **Scoped write access:** Spokes write to their own directory only
4. **Pre-refactor checkpoints:** `safe-refactor` fires before structural changes
5. **Destructive ops require human gate:** Deleting data requires conductor approval

**This exists because a rogue agent destroyed the Hub folder on 2026-02-10.** WAI-Integrity prevents it from happening again.

---

## Session Ledger: Preventing Context Loss

**WAI-Ledger.jsonl** tracks commitments across sessions:

```jsonl
{"type":"request","content":"Add PEV fields to Lug schema","status":"open"}
{"type":"agreement","content":"Will add perceive/execute/verify as optional fields","status":"open"}
{"type":"delivery","content":"350 Lugs upgraded with PEV fields","commit":"73112e9","status":"fulfilled"}
```

**Why it exists:** During WAI v2 migration, token exhaustion caused context loss. The agent reconstructed intent incorrectly, renamed core concepts, skipped 2 phases, and declared completion prematurely. The ledger prevents this by making commitments file-permanent.

On session close: Reconcile open entries, flag unfulfilled commitments.
On resume: Compare agreements against actual codebase state.

---

## Quick Start

1. **Read the framework primer** in your IDE (CLAUDE.md, .cursorrules, etc.)
2. **Explore start-here/** for core concepts
3. **Check your spoke's BRIEF.md** for behavioral rules
4. **Create Lugs as you work** — diagnosis, prescription, decision
5. **Let Skills run automatically** — they're your safety net

---

## For Agents

Wheelwright is a **file-based protocol**. Everything happens through files:

- **Skills** define behavior. During the transition they live in both legacy paths
  and the new public surfaces such as `shared/codebase/skills/` and `hub/codebase/skills/`.
- **Lugs** record work (appended to `WAI-Lugs.jsonl`)
- **Ledger** tracks commitments (appended to `WAI-Ledger.jsonl`)
- **BRIEF** defines rules (cascade: hub → project → spoke)
- **WAI-Integrity.md** protects data (read-only, append-only, scoped writes)

**No CLI. No API. Just files.**

Read the specs:
- [Lug Schema Specification](../../WAI-Lug-Schema-Spec.md)
- [Skill Contract Specification](../../WAI-Skill-Contract-Spec.md)
- [Implementation Plan](../../WAI-v2-Implementation-Plan-Revised.md)

---

## Documentation Structure

- **design/** - Goal-state architecture and decisions to align on before implementation
- **start-here/** — Core concepts, quickstart, architecture
- **skills/** — Skill contract, built-in Skills, creating custom Skills
- **lugs/** — Lug schema, types, PEV pattern, impact scoring
- **hub/** — Hub architecture, integrity contract, intake flow
- **spokes/** — Spoke structure, extensions, BRIEF cascade
- **multi-agent/** — Agent colony patterns, model diversification
- **guides/** — Migration guides, cookbooks, enterprise setup
- **reference/** — Field tables, glossary, changelog

---

**WAI v2.0.0** — February 2026

Agents communicate through files. Institutions remember through Lugs.

## Current Canonical Draft

- [Goal-State Design](./design/goal-state-wheelwright.md)

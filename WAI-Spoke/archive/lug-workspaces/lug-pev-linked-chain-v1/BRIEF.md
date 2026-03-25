# lug-pev-linked-chain-v1

**ID:** lug-pev-linked-chain-v1
**Type:** work
**work.kind:** feature
**Status:** implemented
**Parent Epic:** epic-canonical-evolution-v2 (item E2-11)
**Created:** 2026-03-22T00:00:00Z
**Created By:** claude-sonnet-4-6

---

## What PEV Chain Is

A PEV chain is a set of three linked lugs — one each for Perceive, Execute, and Verify — that together represent a complete unit of structured work requiring explicit analysis before action.

Each lug in the chain carries:
- `pev_role`: one of `perceive` | `execute` | `verify`
- `pev_chain_id`: shared identifier tying the three lugs together (e.g. `pev-auth-20260322`)

This makes the perceive→execute→verify relationship explicit in the lug graph, rather than stuffing all three as text fields on a single record.

---

## What PEV Chain Is NOT

- NOT mandatory for every lug — only for work requiring structured analysis
- NOT a replacement for the existing `perceive`/`execute`/`verify` fields on single lugs
- NOT a new lug type — all three lugs use `type: "work"` with the `pev_role` field distinguishing them
- NOT required for simple tasks, signal lugs, or session summaries

---

## Link Schema

Each lug in a PEV chain carries two fields:

| Field | Type | Description |
|-------|------|-------------|
| `pev_role` | string | `"perceive"` \| `"execute"` \| `"verify"` |
| `pev_chain_id` | string | Shared chain identifier (e.g. `pev-feature-auth-20260322`) |

Chain ID convention: `pev-{slug}-{YYYYMMDD}`

---

## Chain Structure

| Role | Purpose | Key Fields |
|------|---------|-----------|
| `perceive` | Frames the problem: evidence, conditions, unknowns | `pev_role`, `pev_chain_id`, `evidence[]`, `conditions[]` |
| `execute` | Records intended action or implementation plan | `pev_role`, `pev_chain_id`, `plan`, `target_files[]` |
| `verify` | Defines proof the work is correct | `pev_role`, `pev_chain_id`, `criteria[]`, `verified_at` |

---

## Migration Note

Existing lugs that use `perceive`/`execute`/`verify` as plain text fields on a single record remain valid. Both patterns are acceptable (dual-read compatibility). New structured work should prefer the chain pattern when the work benefits from explicit problem framing separate from the implementation plan.

The single-lug PEV fields are still useful for lightweight work items where the three concerns do not need independent tracking.

---

## When to Use

**Use PEV chains for:**
- Architectural decisions with non-trivial problem framing
- Bug investigations where evidence must be captured separately from the fix plan
- Features with clear, independently verifiable acceptance criteria
- Work where the perceive phase may reveal that the original execute plan needs revision

**Skip for:**
- Simple, clearly-scoped tasks
- Signal lugs
- Session summaries
- Any work where a single sentence describes the full context

---

## Acceptance Criteria

- [ ] `wai-lug-advisor.md` has a "PEV Chain Pattern" section documenting the link schema, chain structure, example, when-to-use guidance, and compatibility note
- [ ] The section appears after the lug type catalog and before workflow sections
- [ ] Example JSON shows all three chain members with `pev_role` and `pev_chain_id`
- [ ] Compatibility note explicitly states existing single-lug PEV fields remain valid

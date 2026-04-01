# lug-lug-type-schema-v1

**ID:** lug-lug-type-schema-v1
**Type:** work
**work.kind:** feature
**Status:** implemented
**Parent Epic:** epic-canonical-evolution-v2 (item E2-12)
**Created:** 2026-03-22T00:00:00Z
**Created By:** claude-sonnet-4-6

---

## What This Is

A schema guidance update that introduces canonical top-level lug types and a `work.kind` field to classify work sub-types. This is a **compatibility migration, NOT a bulk rewrite** — existing lugs stay as-is, new lugs use canonical types.

---

## Canonical Top-Level Types

New lugs should use one of these types:

| Type | Purpose |
|------|---------|
| `epic` | Large work body spanning multiple sessions |
| `work` | Executable work item (replaces task/bug/feature as top-level types) |
| `decision` | Architectural or directional choice |
| `finding` | Investigation result or discovered fact |
| `test` | Test specification or result |
| `session-summary` | End-of-session record |
| `signal` | High-impact learning (impact >= 8) |

Source: framework/docs/design/goal-state-wheelwright.md section 6.5

---

## work.kind Field

`task`, `bug`, and `feature` are NOT removed — they become values of `work.kind`:

| work.kind | Replaces | Use when |
|-----------|---------|---------|
| `task` | type: "task" | Defined unit of work |
| `bug` | type: "bug" | Defect or broken behavior |
| `feature` | type: "feature" | New capability |
| `implementation` | type: "implementation" | Capability rollout |

Example:
```json
{"id": "work-fix-auth-20260322", "type": "work", "work": {"kind": "bug"}, "title": "Fix auth bypass"}
```

---

## Dual-Read Rule

- Old lugs with `type: "task"`, `type: "bug"`, or `type: "feature"` remain valid
- Treat `type: "task"` as equivalent to `type: "work", work.kind: "task"` when reading
- Do NOT bulk-rewrite WAI-Lugs.jsonl
- New lugs use canonical types

WAI-Lugs.jsonl has hundreds of legacy type entries (task/bug/feature). These stay as-is. This is a forward-looking schema definition, not a migration job.

---

## Acceptance Criteria

- [ ] `wai-lug-advisor.md` has a "Canonical Type System" section after the existing lug type catalog
- [ ] Section lists the 7 canonical top-level types with purpose descriptions
- [ ] Section defines `work.kind` with the four values (task, bug, feature, implementation)
- [ ] Example JSON shows `work.kind` usage
- [ ] Dual-read compatibility rule is explicit: old types remain valid, do not bulk-rewrite
- [ ] Reading rule states how to interpret old `type: "task"` entries

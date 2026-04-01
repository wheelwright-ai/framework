# Epic: Canonical Evolution — Remaining Items

**ID:** epic-canonical-evolution-v2
**Type:** epic
**Status:** active
**Created:** 2026-03-22
**Created by:** claude-sonnet-4-6
**Priority:** P1 — blocks canonical compliance for all spokes
**Target:** Complete in 2-3 sessions

---

## What Was Already Done (canonical_runtime_baseline — adopted: true)

- Track storage → canonical session directories (`sessions/session-YYYYMMDD-HHMM/track.jsonl`)
- Signal routing → high-impact lugs in `WAI-Lugs.jsonl` (signals no longer a separate file)
- Wakeup/closeout protocol → canonical paths and behavior
- State template → `wheel` section primary, legacy in `_compatibility`
- Concurrency/idempotency → file locking, duplicate detection, receipts (design only)

## What Remains (this epic)

12 items grouped into 3 tiers by urgency and scope.

### Tier 1 — State Correctness (Quick, Do First)

| ID | Item | Why Urgent |
|----|------|-----------|
| E2-01 | Adoption marker sync | `canonical_state_migration: adopted: false` despite implementation lug being `implemented` — every future agent reads this wrong |
| E2-02 | Migration receipts missing | `migration_receipts[]` is empty — no rollback evidence for completed migrations |
| E2-03 | `track_path` stale format | `_session_state.track_path` points to flat file, not canonical session directory |
| E2-04 | `WAI-Signals.jsonl` retirement | File still exists with content in live spoke — signals are now lugs, this is a stale competing source |
| E2-05 | Lug backup cleanup | Two unreviewed `.backup` files in WAI-Spoke root (also tracked as `task-lug-storage-cleanup-v1`) |

### Tier 2 — Protocol Consistency (Medium, Do Next)

| ID | Item | Why Urgent |
|----|------|-----------|
| E2-06 | `wai-lug-advisor.md` signal routing | Says signals go to `WAI-Signals.jsonl` — contradicts every other protocol file |
| E2-07 | `WAI-Guide.md` stale patterns | Stale `status == "published"` filter returns zero results; agents following it get wrong data |
| E2-08 | Adoption marker enforcement | No mechanism flips adoption markers when implementation lugs reach `implemented` — will recur forever |
| E2-09 | Single source of truth for lug storage | "Where do lugs go?" is scattered across 5+ files with contradictions |

### Tier 3 — Architectural Completion (Larger, Track and Plan)

| ID | Item | Why Important |
|----|------|--------------|
| E2-10 | Hub Signals bulletin | `WAI-Hub/Signals/incoming/` and `WAI-Hub/Signals/processed/` not set up per goal-state 5.3 |
| E2-11 | PEV as linked lugs | Goal-state 4.8: PEV should be linked lug chain, not fields stuffed into one record |
| E2-12 | Lug type schema cleanup | Goal-state 6.5: `task/bug/feature` → `work.kind`; canonical types are `epic/work/decision/finding/test/session-summary` |

## What This Is NOT

- Not a full lug schema rewrite (WAI-Lugs.jsonl is still canonical per design)
- Not a spoke rollout (framework-local only)
- Not Ozi architecture changes (Ozi is partner identity, not persistence)
- Not a big-bang replacement — compatibility-first throughout

## Acceptance Criteria

- [ ] `WAI-State.json` migration markers are truthful (adopted = actual adoption state)
- [ ] Migration receipts exist for all completed migrations
- [ ] All protocol files agree on where signals go (`WAI-Lugs.jsonl`)
- [ ] Wakeup reads `WAI-Spoke/WAI-Guide.md` and gets correct filter results
- [ ] Adoption marker enforcement is part of closeout protocol
- [ ] Tier 3 items each have their own child lug with implementation plan

## Assets

- `BRIEF.md` — This file
- `plan.md` — Per-item implementation plans with Perceive/Execute/Verify

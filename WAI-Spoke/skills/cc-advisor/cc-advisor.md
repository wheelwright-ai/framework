# CC Advisor

Persistent ClaudeCode configuration advisor. Replaces the point-in-time maximizer with continuous monitoring, score history, and regression detection.

---

## Execution Context

- **Nodes:** spoke
- **Scope:** `.claude/` configuration, `CLAUDE.md`, hooks, permissions
- **State:** `WAI-Spoke/advisors/cc-advisor/`

---

## When This Runs

| Trigger | Action |
|---------|--------|
| Session start (every session) | Increment counter, surface pending proposals/regressions |
| Every 10 sessions | Full audit pass |
| `/cc-advisor` direct invocation | Full audit pass on demand |
| Hub signal delivery (Phase 5) | Cross-spoke pattern detection |

---

## Session Start Check (runs every session)

1. Read `WAI-Spoke/advisors/cc-advisor/scan_state.json`
2. Increment `sessions_since_last_audit`
3. If `sessions_since_last_audit >= 10`: set `audit_pending: true`
4. Write updated `scan_state.json`
5. If `pending_proposals` not empty OR `vectors.jsonl` has `status: "watching"` entries: surface top 3 gaps as one-line notes in wakeup briefing

Surface format (one line each):
```
⚠ CC: {area} — {gap description} [{proposal-id} pending approval | regression #{N}]
```

---

## Full Audit Pass

Run when `audit_pending: true` or invoked directly.

1. **Score 8 areas** — see cc-advisor-reference.md for per-area checks
2. **Compute score** — count of areas passing for spoke maturity tier
3. **Append to passes.jsonl** — schema: `{id, ts, score, score_by_area, score_delta, findings[], proposals_generated, auto_applied, session_count_at_audit}`
4. **Regression check** — if `score_delta < 0`: create entry in `vectors.jsonl` with `pattern_type: "regression"`
5. **Permission friction analysis** — read `logs/permission-prompts.jsonl`, identify top 3 most-prompted commands
6. **Update scan_state.json** — set `last_audit_at`, `last_audit_session`, `current_score`, `score_by_area`, reset `sessions_since_last_audit: 0`, `audit_pending: false`, `total_audits += 1`
7. **Safe auto-apply** — if any command prompted 3+ sessions with no write side-effects: add to `settings.json` `permissions.allow` (notify user)
8. **Generate proposals** — for CLAUDE.md gaps: write diff to `reports/proposal-YYYYMMDD-{area}.md`; update `scan_state.json` `pending_proposals[]`
9. **Signal emission** — if finding has `impact >= 8`: create signal lug at `lugs/bytype/signal/undelivered/{id}.json`
10. **Report result** — present gap report using format from reference file

---

## Vectors Lifecycle

`vectors.jsonl` tracks patterns over time:
- `watching` — detected, monitoring for recurrence
- `confirmed` — occurred 2+ times
- `resolved` — gap fixed
- `dismissed` — user chose to ignore

---

## Maturity Tiers (scoring threshold)

| Sessions | Target score | Areas required |
|----------|-------------|----------------|
| 0–10 | 4/8 | CLAUDE.md, Hooks, Permissions, Statusline |
| 10–50 | 6/8 | + Slash_Commands, Subagents |
| 50+ | 8/8 | All areas |

---

## Hub Integration (Phase 5)

When `impact >= 8` finding: create signal lug for hub delivery at closeout.
Hub cc-advisor reads cross-spoke signals and generates teachings when 2+ spokes report same gap within 30 days.

---

## Reference

Load `cc-advisor-reference.md` on-demand for:
- Per-area detailed check procedures
- Proposal diff templates
- Event log schemas
- Gap report format

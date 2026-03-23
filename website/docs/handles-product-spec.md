# Wheelwright Handles — Product Specification

**Spec for:** `implementation-wheelwright-handles-v1`
**Status:** defined
**Depends on:** `cohort-sharing-contract.md` (foundational data layer)

---

## 1. What Handles Is (and Is Not)

### Position in the Wheelwright Product Family

| Product | Purpose | Scope |
|---------|---------|-------|
| **Wheelwright Framework** | Session continuity, lug memory, wakeup/closeout | Local — your repo |
| **Octo** | Hub orchestration: routing, dispatch, provider selection | Local — your hub |
| **Ozi** | Work queue management, agent dispatch | Local — your hub session |
| **Handles** | Market intelligence for AI model selection | Networked — Wheelwright Web |

Handles is **not** a replacement for Octo or Ozi. Those own local routing. Handles supplies the community intelligence signal that informs routing decisions — but is never required for them.

**One-liner:** Handles is the operational intelligence layer that answers: *"Which AI model is winning for work like mine — right now, across the whole Wheelwright community?"*

---

## 2. Wheel Registration, Membership, and Telemetry-Contribution Model

### Membership Tiers

```
Anonymous user  →  free public reports (no registration)
Member          →  registered wheel + opt-in telemetry → enhanced access + influence
Pro             →  paid subscription → near-real-time data + API access
Enterprise      →  custom contract → custom segments, SLA, dedicated reports
```

### The Telemetry-for-Value Exchange

Members contribute anonymized session telemetry (see `cohort-sharing-contract.md`, Section 2) and receive in exchange:

| Contribution | Value Received |
|---|---|
| Session telemetry (model selections, task outcomes) | 2-day instead of 4-day data delay |
| Teaching adoption reports | Credits toward Pro features |
| Taste preference data | Influence over community ranking methodology |

**Key principle:** Contribution is voluntary and separable. Members who do not contribute telemetry still get member-level delayed data; they simply do not earn credits.

### Credit Economy (v1)

Credits are earned inside Handles and spent inside Handles only. No external payout in v1.

| Action | Credits earned |
|--------|---------------|
| Register a wheel | 100 |
| 1 week of telemetry contribution | 50/week |
| Teaching adoption report | 25 |
| Referring a new member | 200 |

| Spend | Credits cost |
|-------|-------------|
| 1 week Pro trial | 500 |
| Work-class report (single) | 150 |
| Historical trend (30-day) | 200 |

Credits do not expire within 12 months of last activity.

---

## 3. Track Ingest and Exchange Service

### What Gets Ingested

Not full tracks — only the telemetry extract (anonymized events per Section 2 of cohort-sharing-contract.md). Full tracks stay local unless the user explicitly chooses Consultation Exchange (see `consultation-exchange-spec.md`).

### Free-Tier Storage: Box.com Integration

For members who want track exchange (not just telemetry):

- Handles supports Box.com as a free-tier storage hook
- User connects their Box account; Handles stores track slices in a dedicated `/wheelwright-handles/` folder
- Handles never reads track content beyond extracting the telemetry fields
- Track files are owned by the user — Handles has read-only access to extract events

**Principle:** Box.com (and similar services) are integrations for easier telemetry gathering, not the value proposition. Members without a Box account can still contribute telemetry directly via the API.

### Cached Hub Access

Members get access to a cached copy of their hub's aggregated routing report via Handles. This is a convenience feature — syncing the hub report to the cloud so it's accessible across machines without requiring hub access.

```
Hub (local)  ──push at closeout──►  Handles (cloud cache)
                                    ↓
                                 Member accesses from any device
```

Cache TTL = 7 days. Invalidated on next hub closeout push.

---

## 4. Delayed Reporting Policy

### Access Tiers (Summary)

| Tier | Data lag | Rolling window | Segment depth |
|------|----------|----------------|--------------|
| Public | 4 days | 7 days | Top-10 only |
| Member | 2 days | 14 days | Top-25 + task class breakdown |
| Pro | 6 hours | 90 days | Full segmentation + work-class |
| Enterprise | Configurable | 1 year+ | Custom cohorts |

### Policy Enforcement

- Lag is enforced at the API layer — reports are pre-computed on a schedule and served from cache
- Pro and Enterprise reports are generated on-demand with a maximum 6-hour staleness SLA
- Public reports are static weekly files — no on-demand generation

---

## 5. Market Intelligence Outputs

### Rankings

Every ranking entry carries mandatory trust metadata:

```json
{
  "rank": 1,
  "model_id": "claude-sonnet-4-6",
  "provider": "anthropic",
  "share_pct": 34.2,
  "sample_size": 1243,
  "confidence": 0.87,
  "trend_7d": "up",
  "trend_delta_pct": 4.1,
  "anti_gaming_flags": []
}
```

`confidence` is computed from sample size and variance. Rankings with `confidence < 0.6` are shown with a warning label.

### Report Types

| Report | Description | Minimum tier |
|--------|-------------|-------------|
| `model_popularity` | Top models by session share | Public |
| `provider_share` | Top providers by usage | Public |
| `model_of_week` | Highest-gaining model | Public |
| `launch_day_highs` | New model adoption spikes | Member |
| `task_class_rankings` | Best model per task class | Pro |
| `work_class_deep` | Full work-class segmentation | Pro |
| `custom_cohort` | Enterprise-defined segments | Enterprise |

### Trend Reporting

Trend direction is calculated from 7-day vs. prior 7-day share change:
- `up` = +2% or more
- `down` = -2% or more
- `stable` = within ±2%

Trend is only reported when both periods have `sample_size >= 50`.

---

## 6. Privacy, Provenance, and Anti-Gaming Constraints

### Privacy Constraints

1. No raw data ever appears in any report
2. Minimum cohort size: rankings require `sample_size >= 30` to publish (otherwise suppressed)
3. Vendor data is never attributed back to individual wheels
4. Enterprise custom cohorts must not be configured in ways that could re-identify individual users (enforced by contract)

### Provenance

Every report response includes:

```json
{
  "provenance": {
    "data_collected_from": "2026-W10 through 2026-W12",
    "sample_count": 1243,
    "methodology": "trailing_average_7d",
    "confidence": 0.87,
    "last_computed": "2026-03-22T04:00:00Z"
  }
}
```

### Anti-Gaming

Handles is aware that vendors will try to game rankings:

| Attack vector | Mitigation |
|---|---|
| Vendor floods sessions from bot wheels | Rate limit on registrations per IP/org; anomaly detection on session patterns |
| Vendor registers thousands of wheels | Credit-based registration rate limiting; human verification for bulk |
| Burst campaigns before ranking cutoff | Trailing average smoothing; minimum 14-day contribution window before ranking eligibility |
| Self-reported task class inflation | Task class is inferred from track metadata, not self-declared |

Anti-gaming flags (`anti_gaming_flags` in ranking entries) are populated when anomalies are detected. Flagged entries are shown but labeled.

---

## 7. Product Architecture and Revenue Boundaries

### Revenue Model

| Source | Mechanism |
|--------|-----------|
| Pro subscriptions | Monthly SaaS — fresh data, API access, segmentation |
| Enterprise contracts | Custom reporting, SLA, dedicated cohorts |
| Credit purchases | Optional booster for members who want Pro features without subscription |
| Telemetry subsidy | Telemetry contributors get delayed-access features free — reduces churn, subsidized by data value |

### What Handles Does Not Monetize

- Local framework usage (always free)
- Basic membership (registration + telemetry contribution)
- Public community rankings (free forever — they drive adoption)
- Hub-spoke architecture or any local WAI component

### Positioning Statement

> Handles is the air traffic control display for the AI model market.
> You fly your own plane (local Wheelwright). Handles shows you where everyone else is flying and which runways are busiest — so you can make smarter routing decisions.

---

## Verification Checklist

- [ ] Handles is clearly distinct from Octo (local routing) and Ozi (local dispatch) ✓
- [ ] Local hub routing works without Handles being available ✓
- [ ] Telemetry contribution is opt-in; member access is separable from contribution ✓
- [ ] Box.com is a storage integration hook, not the core product ✓
- [ ] Every ranking carries confidence, sample size, and anti-gaming metadata ✓
- [ ] Free/member/premium data boundaries are explicit and technically enforceable ✓
- [ ] Revenue model is sustainable without compromising the free tier ✓

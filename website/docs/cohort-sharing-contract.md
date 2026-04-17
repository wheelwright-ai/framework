# Cohort Sharing Contract

**Spec for:** `implementation-wheelwright-web-cohort-sharing-v1`
**Status:** defined
**Depends on:** Cluster 1 hub infrastructure (routing table + Octo) — complete as of Session 57

---

## 1. Wheel Registration — Identity and Privacy Model

### Registration Contract

A wheel registers voluntarily by sending a `WheelRegistration` object to the Handles API:

```json
{
  "wheel_id": "<sha256 of project root path + creation timestamp>",
  "framework_version": "3.0.0",
  "node_type": "spoke | hub",
  "registered_at": "ISO-8601",
  "telemetry_opt_in": true,
  "privacy_tier": "anonymous | pseudonymous | identified",
  "consent_version": "1.0"
}
```

**Privacy tiers:**

| Tier | What is shared | Wheel ID visible? |
|------|---------------|-------------------|
| `anonymous` | Aggregated cohort data only — no individual wheel attribution | No |
| `pseudonymous` | Per-wheel stats with rotating pseudonym | Pseudonym only |
| `identified` | Full wheel stats with stable membership ID (required for premium) | Yes (to user) |

**Invariants:**
- `wheel_id` is locally generated and never sent unless `privacy_tier = identified`
- Registration can be revoked at any time — all associated data is purged within 7 days
- `consent_version` must match the server's current consent document version

### Identity Stability

Wheels use a locally-generated stable ID derived from project path + creation timestamp. This is never stored in plaintext on the server in `anonymous` or `pseudonymous` tiers — only a salted hash is retained for deduplication.

---

## 2. Anonymized Telemetry Ingest Contract

### What is Telemetry

Telemetry = model-routing and execution decisions extracted from WAI session tracks. Specifically:

```json
{
  "event_type": "model_selection | task_completion | session_summary | teaching_adoption",
  "model_id": "claude-sonnet-4-6",
  "provider": "anthropic",
  "task_class": "architecture | execution | review | planning",
  "token_count": 45000,
  "session_duration_s": 1800,
  "outcome": "success | partial | abandoned",
  "wheel_pseudonym": "<rotating pseudonym>",
  "reported_at": "ISO-8601",
  "cohort_week": "2026-W12"
}
```

### Anonymization Rules

Before transmission:
1. Strip all file paths, project names, and lug content
2. Replace wheel_id with rotating pseudonym (rotates weekly for `pseudonymous` tier)
3. Round token counts to nearest 1000
4. Round session durations to nearest 5 minutes
5. Discard any field that could re-identify the project

### Ingest Endpoint

```
POST /api/v1/telemetry
Authorization: Bearer <wheel_token>
Content-Type: application/json

{ "events": [ <TelemetryEvent>, ... ] }
```

Batched — up to 100 events per request. Events older than 30 days are rejected.

---

## 3. Trailing-Average Reporting and Free 4-Day Delay Policy

### Delay Policy

| Tier | Delay | Aggregation |
|------|-------|-------------|
| Public (free) | 4-day trailing average | 7-day rolling window |
| Member (registered) | 2-day trailing average | 3-day rolling window |
| Premium | Near-real-time (< 6 hours) | 1-day rolling window |

**Why 4 days:**
- Prevents gaming the rankings with short burst campaigns
- Sufficient lag that competitive intelligence from fresh data is premium-only
- Rolling 7-day average smooths outliers and small-sample noise

### Report Format

```json
{
  "report_type": "model_popularity | task_class_distribution | provider_share",
  "period": "2026-W12",
  "generated_at": "ISO-8601",
  "data_lag_days": 4,
  "sample_size": 1243,
  "confidence": 0.87,
  "entries": [
    {
      "model_id": "claude-sonnet-4-6",
      "provider": "anthropic",
      "share_pct": 34.2,
      "rank": 1,
      "trend": "up | stable | down"
    }
  ]
}
```

Reports are cacheable for 1 hour (public) and 15 minutes (member).

---

## 4. Paid Fresher-Data Boundary and Entitlements Model

### Entitlement Tiers

| Tier | Price | Data lag | Features |
|------|-------|----------|----------|
| Free | $0 | 4-day | Public weekly rankings |
| Member | Free with registration | 2-day | Per-model trend charts, task-class breakdown |
| Pro | $X/month | 6-hour | Near-real-time, work-class segmentation, API access |
| Enterprise | Custom | Configurable | Custom segments, vendor-specific cohorts, SLA |

### What Pro/Enterprise Get

- Fresh data window (< 6 hours) for model selection decisions
- Work-class segmentation: "which model wins for `architecture` tasks specifically?"
- API access to `/api/v1/reports` for programmatic integration with hub routing
- Historical trend depth beyond 7-day public window

### What Is Never Sold

- Individual wheel data (even with consent)
- Raw track content or lug content
- Identifiable project details

---

## 5. Shared Data → Hub Model-Routing Intelligence

### Feedback Loop (Optional)

Cohort data can optionally inform hub routing suggestions:

```
Wheelwright Web                    Local Hub
─────────────────                  ──────────────────────────────
Weekly model report    ──────────► hub routing advisor reads report
(delayed, aggregated)              adds community signal to routing table
                                   user sees: "Community: sonnet-4-6 is top
                                   for architecture tasks this week"
```

**Critical constraint:** This feedback is advisory and optional.
- Hub routing works correctly without it
- The feed is a static weekly report file, not a live API dependency
- Hubs cache the last known report; if unavailable, they operate on local data only

### Report Distribution

```
GET /api/v1/community/routing-hint
→ returns: { "week": "2026-W12", "hints": [ { "task_class": "architecture", "top_model": "claude-sonnet-4-6", "confidence": 0.82 } ] }
```

Hubs poll this at most once per day. Cache TTL = 24 hours.

---

## 6. Ranking and Report Surfaces

### Community Surfaces

| Surface | Description | Update frequency |
|---------|-------------|-----------------|
| Most Popular AI | Top AI providers by session share | Weekly (public), daily (member) |
| Most Popular Model | Top models by session count | Weekly (public), daily (member) |
| Model of the Week | Highest-gaining model in the past 7 days | Weekly |
| Launch-Day Highs | New model adoption spike tracking | Rolling |
| Daily Rankings | Hourly rank positions (member/premium only) | Hourly |
| Work-Class Rankings | Best model per task class (pro only) | 6-hourly |

### Report Discovery

```
GET /api/v1/community/surfaces
→ returns list of available report surfaces with tier requirements and last-updated timestamps
```

---

## Verification Checklist

- [ ] Public data is trailing-average and delayed at minimum 4 days ✓
- [ ] Local hub routing works without cohort sharing ✓
- [ ] Telemetry is opt-in, anonymized before transmission ✓
- [ ] Registration is revocable with 7-day data purge ✓
- [ ] Paid vs. free boundary is explicit and technically enforced ✓
- [ ] Community routing hint is advisory-only, never a hard dependency ✓

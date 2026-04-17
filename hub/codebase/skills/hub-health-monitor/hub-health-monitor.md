# Hub Health Monitor

**Ongoing fleet-level health tracking — trends, drift detection, and cross-session spoke health history.**

---

## Execution Context

- **Nodes:** hub only
- **Exposure:** hub.chat:local
- **Trigger:** `/hub-health-monitor` — run on demand for trend analysis

---

## Distinction from Fleet Health (Step 4.2)

**Step 4.2 (wai.md)** — Per-session snapshot: reads spoke health reports delivered to hub
`incoming/`, displays current scores, appends a `fleet-health` lug.

**This skill** — Historical trend analysis: reads the sequence of `fleet-health` lugs over
time, detects regressions and drift, and flags spokes that are trending toward degradation
before they hit critical.

Both are complementary. Step 4.2 is the data source; this skill is the analysis layer.

---

## Step 1: Load Fleet Health History

Read all `fleet-health` lugs from `hub/WAI-Lugs.jsonl` (or `WAI-Spoke/WAI-Lugs.jsonl`
if hub uses spoke storage):

```python
fleet_history = [
    lug for lug in lugs
    if lug.get("type") == "fleet-health"
]
# Sort by timestamp ascending
fleet_history.sort(key=lambda l: l["timestamp"])
```

If fewer than 3 data points: report "Insufficient history for trend analysis — need at
least 3 fleet-health snapshots."

---

## Step 2: Compute Per-Spoke Trends

For each spoke that appears in the history:

1. Extract their score sequence: `[(timestamp, score, percent), ...]`
2. Compute trend direction:
   - **Improving:** percent increasing over last 3 snapshots
   - **Stable:** percent within ±5% across last 3 snapshots
   - **Declining:** percent decreasing over last 3 snapshots
3. Compute missed-report count: snapshots where this spoke was expected but absent

---

## Step 3: Detect Anomalies

Flag conditions:

| Condition | Flag | Threshold |
|---|---|---|
| Score dropped 10%+ in one interval | `sharp_drop` | delta >= 10% |
| Declining trend for 3+ snapshots | `sustained_decline` | 3 consecutive |
| Spoke absent from 2+ recent snapshots | `reporting_gap` | 2 consecutive absent |
| Score below 80% for 2+ snapshots | `persistently_degraded` | 2 consecutive < 80% |
| Score recovered from critical to healthy | `recovered` | informational |

---

## Step 4: Report

Surface as:

```
### Fleet Health Trend Analysis
Period: {first_snapshot} to {last_snapshot} ({N} snapshots)

| Spoke | Trend | Current | Flags |
|---|---|---|---|
| wheelwright | stable | 100% | — |
| pathfinder | declining | 75% | sustained_decline, persistently_degraded |
| compass | improving | 90% | recovered (was 70% on 2026-03-10) |

Fleet summary: 1 spoke needs attention.
Recommendation: Run /hub-registry-verification for pathfinder.
```

---

## Step 5: Append Trend Lug

```json
{
  "id": "health-trend-{YYYYMMDD-HHMM}",
  "type": "health-trend",
  "timestamp": "ISO-8601",
  "period_start": "ISO-8601",
  "period_end": "ISO-8601",
  "snapshot_count": N,
  "spoke_count": M,
  "flags": [
    {"spoke": "pathfinder", "flag": "sustained_decline", "detail": "..."}
  ],
  "fleet_status": "healthy | degraded | critical",
  "fw_ver": "{current_fw_ver}",
  "created_by": "hub-health-monitor"
}
```

Append to `hub/WAI-Lugs.jsonl`.

---

## Related Skills

- `hub-registry-verification.md` — verifies spokes are reachable before health analysis
- `hub-knowledge-base-curator.md` — uses fleet activity data to time curation runs
- `wai.md` Step 4.2 — provides the per-session fleet-health data points this skill analyses

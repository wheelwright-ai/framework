# Hub Registry Verification

**Verify that every spoke registered with this hub is reachable and in a healthy state.**

---

## Execution Context

- **Nodes:** hub only
- **Exposure:** hub.chat:local
- **Trigger:** `/hub-registry-verification` or at hub wakeup (Step 4.2 fleet health aggregation)

---

## What This Skill Does

The hub maintains a registry of connected spokes. Over time the registry drifts: spokes move,
get archived, or fall out of sync without notifying the hub. This skill audits the registry
against reality and surfaces discrepancies.

**Problems it catches:**
- Spoke path moved or deleted (hub can't read WAI-State.json)
- Spoke `spoke_id` in state doesn't match registry (different wheel got reused at same path)
- Spoke hasn't closed out in N days (stale — may be abandoned or crashed)
- Registry entry missing `spoke_id` (pre-v3 spoke, not yet migrated)

---

## Step 1: Load Registry

Read the hub's spoke registry. Check these locations in order:

1. `hub/registry.yaml` — canonical hub registry
2. `WAI-Spoke/WAI-State.json → spokes.active[]` — fallback spoke list
3. `WAI-Hub/registry/` — directory of per-spoke registration files (future format)

For each registered spoke, collect:
- `name` — spoke name
- `path` — filesystem path to spoke root
- `spoke_id` — expected 12-char hex identifier
- `registered_at` — when this spoke was added to the hub

---

## Step 2: Verify Each Spoke

For each spoke in the registry:

```python
# Pseudocode — adapt to actual registry structure
for spoke in registry.spokes:
    state_path = f"{spoke.path}/WAI-Spoke/WAI-State.json"

    # Check 1: Reachability
    if not exists(state_path):
        flag(spoke, "unreachable", f"WAI-State.json not found at {state_path}")
        continue

    state = read_json(state_path)

    # Check 2: spoke_id match
    actual_id = state.get("wheel", {}).get("spoke_id")
    if spoke.spoke_id and actual_id != spoke.spoke_id:
        flag(spoke, "id_mismatch", f"Expected {spoke.spoke_id}, found {actual_id}")

    # Check 3: Staleness (last closeout > 30 days ago)
    last_closeout = state.get("_session_state", {}).get("last_closeout")
    if last_closeout and days_ago(last_closeout) > 30:
        flag(spoke, "stale", f"Last closeout: {last_closeout} ({days_ago(last_closeout)} days ago)")

    # Check 4: Framework version currency
    fw_ver = state.get("wheel", {}).get("framework_version")
    if fw_ver and major(fw_ver) < major(hub_fw_version):
        flag(spoke, "outdated_framework", f"Spoke on fw {fw_ver}, hub on {hub_fw_version}")
```

---

## Step 3: Report

Surface in briefing as:

```
### Registry Verification
| Spoke | Status | Issue |
|---|---|---|
| wheelwright | healthy | — |
| pathfinder | unreachable | WAI-State.json not found at /projects/pathfinder/ |
| compass | stale | Last closeout 47 days ago |

2 spokes need attention. Run /hub-registry-verification fix to create remediation lugs.
```

**Status values:**
- `healthy` — reachable, id matches, active within 30 days
- `unreachable` — state file not found
- `id_mismatch` — spoke_id in registry ≠ spoke_id in state
- `stale` — no closeout in > 30 days
- `outdated_framework` — major version behind hub

---

## Step 4: Remediation Lugs (Optional)

If issues found and user confirms, create one lug per problem spoke:

```json
{
  "id": "spoke-health-{spoke_name}-{YYYYMMDD}",
  "type": "task",
  "title": "Investigate {spoke_name}: {status} — {issue}",
  "status": "open",
  "priority": "P2",
  "perceive": "Read {state_path} (or confirm path is unreachable)",
  "execute": "Diagnose root cause of {status}. Options: update registry path, run /wai on spoke, or mark spoke archived.",
  "verify": "Re-run /hub-registry-verification — spoke shows healthy",
  "fw_ver": "{current_fw_ver}",
  "created_at": "ISO-8601",
  "created_by": "hub-registry-verification"
}
```

Append to `WAI-Spoke/WAI-Lugs.jsonl`.

---

## Related Skills

- `hub-health-monitor.md` — fleet-level health monitoring over time
- `wai.md` Step 4.2 — fleet health aggregation (per-session spoke health reports)

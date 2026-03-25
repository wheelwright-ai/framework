# WAI Wakeup — Hub Protocol

**Hub override of the spoke wakeup. Includes all spoke steps plus hub superpowers: fleet health, registry audit, teaching queue, lug-review processing, and a fleet-aware briefing.**

> This file is the complete wakeup protocol for hub nodes. It replaces `WAI-Spoke/skills/wai/wai.md` via the hub override resolution rule. All spoke steps are included here; hub-only sections are marked `[HUB ONLY]`.

---

## Execution Context

- **Nodes:** hub
- **Exposure:** hub.chat:local
- **Resolution:** `WAI-Hub/skills/wai/wai.md` takes precedence over `WAI-Spoke/skills/wai/wai.md` on hub nodes

---

## Step 0a: Check Integration File

Detect execution environment and read integration file (CLAUDE.md, GEMINI.md, AGENTS.md).
Apply any tool-specific wakeup directives before proceeding.

---

## Step 0b: Load Hub Profile [HUB ONLY]

Read the hub's registry and manifest to understand the fleet before loading spoke state.

**Read in order:**

1. `hub/registry.yaml` — connected spokes list (name, path, spoke_id, registered_at)
2. `hub/WAI-Manifest.yaml` — hub configuration, hub ID, distribution settings
3. `hub/WAI-Hub/skills/WAI-Skills.jsonl` — hub-specific skill registry

**Extract and hold for Step 5 briefing:**
- `spoke_count` — number of registered spokes
- `spokes[]` — list of {name, path, spoke_id}
- `hub_id` — this hub's identifier

If registry file is missing or malformed: continue with empty spoke list. Log: "Hub registry not found — fleet overview unavailable."

---

## Step 1: Load WAI-State.json

Load spoke's technical spec, foundation, and session state:

```bash
cat WAI-Spoke/WAI-State.json
```

Key sections: `_foundation`, `_session_state`, `_migration_state`

**[HUB ONLY]** Also check:
- `wheel.hub_path` — should point to self or parent
- `wheel.node_type` — must be `"hub"` to use this protocol

---

## Step 2: Load WAI-State.md

Load strategic context and vision:

```bash
cat WAI-Spoke/WAI-State.md
```

---

## Step 1b: Ozi Work Queue Check (If Enabled)

If `ozi-work-queue-monitor` skill is enabled, run Ozi's briefing:

```bash
python3 wai_ozi.py
```

---

## Step 3a: Auto-Discovery of New Hub Teachings

Poll hub's teachings folders for new framework and cross-spoke updates.

```bash
ls -1 "${HUB_PATH}/teachings_repo/*/current/*.teaching" 2>/dev/null
```

For each discovered teaching not yet in `WAI-Spoke/seed/processed/`:
- Path A (`safe_to_auto_adopt: true`): present compact table, await user approval
- Path B (`safe_to_auto_adopt: false`): full mailroom ceremony — receive, summarize, explain, wait, proceed

**Hub Signal Bulletin:**

```bash
ls ${HUB_PATH}/WAI-Hub/Signals/incoming/*.json 2>/dev/null
```

For each `.json` file: check if id already known in WAI-Lugs.jsonl. If new, surface in briefing. Do not auto-adopt.

**[HUB ONLY] Also check spoke incoming dirs:**

For each registered spoke (from Step 0b), scan `{spoke.path}/WAI-Spoke/lugs/incoming/` for pending `lug-review` payloads not yet processed. Surface count in briefing — these will be processed in Step 4.3.

---

## Step 3: Load Skills

Load active skills from spoke index:

```bash
cat WAI-Spoke/skills/WAI-Skills.jsonl
```

**[HUB ONLY] Hub skill resolution order:**

1. Check `WAI-Hub/skills/{id}/{command_file}` — hub override (this file is an example)
2. Fall back to `WAI-Spoke/skills/{id}/{command_file}` — spoke base

Additionally load hub-coord skills from `WAI-Hub/skills/WAI-Skills.jsonl`:
- `hub-registry-verification`
- `hub-knowledge-base-curator`
- `hub-health-monitor`

---

## Step 4: Load Lugs and Signals

Load active work and learnings:

```bash
cat WAI-Spoke/WAI-Lugs.jsonl
```

**[HUB ONLY]** Also read:

```bash
cat hub/WAI-Lugs.jsonl   # Hub's own task/signal graph
```

Signals are high-impact lugs (`impact >= 8`) in WAI-Lugs.jsonl.

---

## Step 4.1: Detect External Tracks

Check `WAI-Spoke/seed/ingest/` for `WAI_Track-*.jsonl` files. For each:
1. Validate: JSON, `event: session_start`, `provider` and `model` fields
2. If valid: copy to `WAI-Spoke/sessions/`, move original to `seed/ingest/processed/`
3. If invalid: report issue, leave in place

---

## Step 4.2: Fleet Health Aggregation [HUB ONLY — MANDATORY]

**Always runs on hub.** Aggregate spoke self-health reports from hub incoming folder.

```bash
ls WAI-Spoke/seed/ingest/spoke-health-*.json 2>/dev/null
```

For each file:
1. Read: `spoke_id`, `score`, `percent`, `status`, `timestamp`, `failures[]`
2. Compute fleet status:
   - `healthy` — all spokes at 100%
   - `degraded` — any spoke 80–99%
   - `critical` — any spoke < 80%

Surface in briefing:

```
### Fleet Health
| Spoke | Score | Status | Failures | Reported |
|---|---|---|---|---|
| {name} | {score} | {status} | {failures or —} | {timestamp} |

Fleet status: {HEALTHY | DEGRADED | CRITICAL}
```

Append a `fleet-health` lug to `WAI-Lugs.jsonl`. Move processed files to `seed/ingest/processed/`.

If no reports found: log "Fleet health: no spoke reports in incoming."

---

## Step 4.3: Lug Review Returns [HUB ONLY — MANDATORY]

**Always runs on hub.** Process `lug-review` payloads returned by spokes.

```bash
ls WAI-Spoke/lugs/incoming/lug-review-*.jsonl 2>/dev/null
```

For each file:
1. Read payload: `type: "lug-review"`, `source_id`, `review_fw_ver`, `review_status`, `review_notes`
2. Validate schema
3. Find lug in `WAI-Lugs.jsonl` by `id == source_id`
4. **Version gate:** only apply if `review_fw_ver >= lug.fw_ver`
5. If accepted: append review fields to lug: `reviewed_fw_ver`, `reviewed_at`, `reviewed_by`, `review_status`, `review_notes`. If status is `outdated_protocol` or `contradicts_current`: set `reconciled: true`
6. Surface in briefing: `Lug review received: {source_id} → {review_status} (from {reviewed_by})`
7. Move to `WAI-Spoke/lugs/incoming/processed/`

---

## Step 4.4: Fleet Status Summary [HUB ONLY]

Quick audit of registered spokes from Step 0b registry — no filesystem scanning, just state file reads.

For each spoke in registry:

```python
state = read_json(f"{spoke.path}/WAI-Spoke/WAI-State.json")
last_closeout = state._session_state.last_closeout
framework_version = state.wheel.framework_version
actual_spoke_id = state.wheel.spoke_id
```

Flag conditions:
| Condition | Flag |
|---|---|
| `state_path` not readable | `unreachable` |
| `spoke_id` mismatch vs registry | `id_mismatch` |
| `last_closeout` > 14 days ago | `stale` |
| `framework_version` major behind hub | `outdated_framework` |

Hold results for Step 5 briefing.

If registry empty: skip, log "No spokes registered."

---

## Step 4.5: Teaching Distribution Queue [HUB ONLY]

Check what's in the teaching pipeline waiting to reach spokes.

```bash
ls hub/teachings_repo/framework/current/*.teaching 2>/dev/null | wc -l
```

For each registered spoke, check how many teachings in `current/` are NOT yet in `{spoke.path}/WAI-Spoke/seed/ingest/processed/`. This is the "delivery debt" — teachings authored but not yet delivered.

Surface in briefing if delivery debt > 0:
```
Teaching queue: N teachings in current/ | delivery debt: M spokes haven't received all teachings
```

---

## Step 5: Display Briefing

Show unified WAI Point briefing. Hub briefing includes all spoke sections plus a **Fleet Overview** section:

```
### WAI Point — Hub Session [N]
Project: {name} v{version} | {node_type}

#### Fleet Overview [HUB ONLY]
| Spoke | Status | Last Closeout | Framework | Health |
|---|---|---|---|---|
| {name} | healthy/stale/unreachable | {date} | {fw_ver} | {score} |

Fleet: {N} spokes | {healthy_count} healthy | {stale_count} stale | {unreachable_count} unreachable
Teaching queue: {N} in current/ | {M} delivery debt

#### Hub Bulletins
{new signals from WAI-Hub/Signals/incoming/ not yet known}

#### Spoke Active Work
{active lugs from WAI-Lugs.jsonl — hub's own backlog}

#### Context Health
- Hub registry: {N} spokes registered
- Teaching distribution: current/{N} | archive/{M}
- Git: {clean | M modified files}
- Session: {count}
```

---

## Step 5b: Track Predecessor Detection

Scan conversation context for loaded track file content (JSON lines with `turn`, `ts`, `phase`, `focus`, `action`, `thinking`). If detected, report session chain linkage.

---

## Step 6: Ozi Auto Queue Awareness

If Ozi auto mode enabled: run `python3 wai_ozi.py`, show builder queue.
If disabled: continue normally.

---

## Step 7: Session Check

Check `last_modified_by`, `requires_review`, `session_count`.

**[HUB ONLY]** Also check `hub/WAI-Lugs.jsonl` for open hub-level tasks — surface any `priority: P1` items in briefing.

---

## Step 8: Environment Detection

Auto-detect tool, machine, OS, parent session. Scan `WAI-Spoke/sessions/` for multi-tool activity.

**[HUB ONLY]** Also note hub-specific environment: `hub_id`, `hub_path`, `registry.yaml` last modified date.

---

## Step 9: Initialize Session Track

```bash
SESSION_DIR="WAI-Spoke/sessions/session-$(date +%Y%m%d-%H%M)"
mkdir -p "$SESSION_DIR"
touch "$SESSION_DIR/track.jsonl"
```

Per-turn point capture mandatory. Schema: `turn`, `ts`, `focus`, `action`, `thinking`, `activity`, `decisions`, `insights`, `open`, `phase`, `evolution`.

---

## Step 10: Ready Prompt

After all steps:

```
Hub wake complete. Fleet: {N} spokes | {health summary}. Ready to work.
```

---

## Hub Core Files Reference

| File | Purpose | Access |
|------|---------|--------|
| `WAI-State.json` | Hub spoke state, session tracking | UPDATE |
| `WAI-Spoke/skills/WAI-Skills.jsonl` | Spoke-role skill registry | READ |
| `WAI-Hub/skills/WAI-Skills.jsonl` | Hub-coord skill registry | READ |
| `WAI-Lugs.jsonl` | Hub's own task/signal graph | UPDATE |
| `hub/WAI-Lugs.jsonl` | Fleet-level decisions and signals | UPDATE |
| `hub/registry.yaml` | Registered spoke list | READ |
| `hub/teachings_repo/framework/current/` | Active teachings for distribution | READ |
| `hub/WAI-Hub/Signals/incoming/` | Signal bulletin inbox | READ |

---

## Incoming Routing Rules

Same mailroom rules as spoke base, plus:

| Type | Hub Action |
|------|-----------|
| `spoke-health` | Aggregate into fleet-health lug (Step 4.2) |
| `lug-review` | Apply to hub canonical copy (Step 4.3) |
| `lug-review` (invalid) | Log and quarantine — do not apply |
| `teaching` | Route to `seed/ingest/` for user review |

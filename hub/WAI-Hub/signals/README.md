# WAI-Hub Signals Bulletin

This directory is the hub bulletin board for high-impact signals. Spokes publish and inspect signals here during closeout and wakeup.

---

## Directory Layout

```
WAI-Hub/signals/
  incoming/     — signals staged for spoke inspection
  processed/    — signals that have been inspected or incorporated
```

---

## incoming/

Signals are copied here by spoke closeout when a lug has `impact > 7` and `status != "archived"`.

- One file per signal
- Filename: `{signal-id}.json`
- Content: full lug JSON from the originating spoke's `WAI-Lugs.jsonl`
- Spokes inspect this directory during wakeup Step 3a (hub teachings discovery)
- Signals are advisory — spokes surface them in the briefing but do not auto-adopt

## processed/

Signals move here after a spoke has inspected and incorporated them (or explicitly decided not to act).

Processed signal files gain additional fields:
- `source_lug_id` — original lug ID if different from signal ID
- `absorbed_at` — ISO-8601 timestamp when the signal was inspected
- `absorbed_by` — agent or spoke that processed it
- `resolution` — one of: `adopted`, `noted`, `rejected`, `superseded`

---

## Format

Each signal file is valid JSON (not JSONL). Example:

```json
{
  "id": "signal-20260322-1200-hub-bulletin-established",
  "type": "signal",
  "title": "Hub bulletin board established for cross-spoke signal sharing",
  "description": "WAI-Hub/signals/ directory structure created...",
  "impact": 8,
  "created_by": "claude-sonnet-4-6",
  "created_at": "2026-03-22T12:00:00Z",
  "session_id": "session-20260322-1200",
  "rationale": "Enables cross-spoke signal propagation without inbox ceremony"
}
```

---

## Usage Rules

- Signals in `incoming/` are READ-ONLY from the spoke's perspective during wakeup
- Only spoke closeout writes to `incoming/`
- Never delete files from `incoming/` — move to `processed/` instead
- If hub is not accessible, spoke closeout skips silently (non-blocking)

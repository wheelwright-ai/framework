# lug-hub-signals-bulletin-v1

**ID:** lug-hub-signals-bulletin-v1
**Type:** implementation
**Status:** implemented
**Parent Epic:** epic-canonical-evolution-v2 (item E2-10)
**Created:** 2026-03-22
**Created By:** claude-sonnet-4-6

---

## What This Is

The hub bulletin board is a shared directory at `WAI-Hub/Signals/` that lets high-impact signals from one spoke become visible to other spokes. At closeout, any lug with `impact > 7` and `status != "archived"` is copied as a JSON file to `incoming/`. At wakeup, spokes inspect `incoming/` for new signals they haven't seen yet and surface them in the briefing.

This is advisory infrastructure — signals are surfaced, not auto-adopted. The user decides whether to act on any signal.

## What This Is NOT

- Not a replacement for the hub inbox/outbox lug delivery system (that handles task lugs via `WAI-Spoke/lugs/outbox/`)
- Not an auto-adoption mechanism — signals are read-only at wakeup
- Not a broadcast channel for low-impact decisions
- Not required for spokes that have no hub connection — all operations skip gracefully when `hub_path` is null or unreachable

---

## Three Components

### 1. Directory Structure

```
hub/WAI-Hub/Signals/
  incoming/     — signals staged for spoke inspection (copied by spoke closeout)
  processed/    — signals incorporated or reviewed (moved here after use)
  README.md     — explains format and lifecycle
```

Each signal is one JSON file named `{signal-id}.json`. The file content is the full lug JSON from `WAI-Lugs.jsonl`.

### 2. Closeout Step (Step 9c — Hub Signal Bulletin)

Added after Step 9b (Teaching Generation + Hub Publish) in both:
- `templates/commands/wai-closeout.md`
- `WAI-Spoke/commands/wai-closeout.md`

For each lug in `WAI-Lugs.jsonl` where `impact > 7` and `status != "archived"`:
1. Check if `{hub_path}/WAI-Hub/Signals/incoming/{lug-id}.json` already exists
2. If not: write the lug as a JSON file there
3. Log: "Published to hub bulletin: {lug-id} (impact={impact})"

If `hub_path` is null or hub not accessible: skip silently, log "Hub bulletin skipped — hub not connected".

### 3. Wakeup Step (Step 3a — Hub Signal Bulletin sub-section)

Added within Step 3a (Auto-Discovery of New Hub Teachings) in both:
- `templates/commands/wai.md`
- `WAI-Spoke/commands/wai.md`

At wakeup, after the teachings discovery check:
1. Check `{hub_path}/WAI-Hub/Signals/incoming/` for `.json` files
2. For each file: read it, check if already known (id present in WAI-Lugs.jsonl)
3. If new: surface in briefing as "Hub signal: {title} (impact={impact}, from={node})"
4. Do NOT auto-adopt — signals are advisory. User decides whether to act.
5. After inspection: optionally move processed signals to `WAI-Hub/Signals/processed/` at closeout

---

## Acceptance Criteria

- [ ] `hub/WAI-Hub/Signals/incoming/` exists with `.gitkeep`
- [ ] `hub/WAI-Hub/Signals/processed/` exists with `.gitkeep`
- [ ] `hub/WAI-Hub/Signals/README.md` explains format and lifecycle
- [ ] `templates/commands/wai-closeout.md` contains "Hub Signal Bulletin" step
- [ ] `WAI-Spoke/commands/wai-closeout.md` contains "Hub Signal Bulletin" step
- [ ] `templates/commands/wai.md` contains "Hub Signal Bulletin" sub-section in Step 3a
- [ ] `WAI-Spoke/commands/wai.md` contains "Hub Signal Bulletin" sub-section in Step 3a
- [ ] Epic E2-10 status updated to "implemented" in WAI-Lugs.jsonl
- [ ] All hub operations are gracefully skipped when hub_path is null or unreachable

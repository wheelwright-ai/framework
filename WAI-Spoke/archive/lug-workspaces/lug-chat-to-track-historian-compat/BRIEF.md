# Lug: Historian — Support Event-Based External Track Format

**ID:** lug-chat-to-track-historian-compat
**Type:** lug
**Status:** open
**Priority:** P1
**Created:** 2026-03-16
**Created by:** code-puppy-f16663
**Parent epic:** epic-chat-to-track-v1
**Dogfood pass:** true (round 2 — sort-order bug, step count, implicit edits fixed)

## What This Is

Extend the historian's pattern-scan algorithm to handle event-based
track files from external AI conversations. These files use a different
format than internal turn-based track points.

## What This Is NOT

- Not a rewrite of the historian — existing turn-based scanning stays
- Not a change to the point schema (track-encapsulation.yaml)
- Not a change to how internal sessions are recorded

## Challenge

The historian reads `WAI-Spoke/sessions/track_*.jsonl` files containing
turn-based points with `open[]`, `activity[]`, `decisions[]` arrays.
External tracks from the Chat-to-Track prompt use event-based format
(`decision_made`, `concept_update`, `context_canary`, etc.). The
historian is completely blind to external session data.

## Hypothesis

Extend the historian's file glob to include `WAI_Track-*.jsonl`, add
format detection by first-line inspection, and define an extraction
mapping from event types to the historian's existing field pipeline.

## Known Risk: Sort-Order and Incremental Watermarks

**ASCII sort puts `WAI_Track-*` (W=0x57) BEFORE `track_*` (t=0x74).**
The existing incremental watermark (`filename > last_scan_session`)
uses ASCII comparison. If both file types are merged into one sorted
list, the watermark set by the latest `track_*` file would cause ALL
`WAI_Track-*` files to be skipped on subsequent scans.

**Mitigation:** Use two independent watermarks in `scan_state.json`:
`last_scan_session_internal` (for `track_*`) and
`last_scan_session_external` (for `WAI_Track-*`).

## Perceive

1. Open `framework/skills/historian.yaml` and search for `algorithm:`
   key under `pattern_scan:`. This is a YAML array of string steps.
2. In the algorithm array, locate the step containing `track_*.jsonl`
   — this is the file listing glob (2nd array item: "List
   WAI-Spoke/sessions/track_*.jsonl sorted by filename").
3. Locate the extraction step starting with "For each loaded session:
   extract all items from open[], activity[], decisions[]" — 4th item.
4. Open `framework/skills/chat-to-track.md` — review event schemas.
5. Locate `scope.reads` section (under `scope:`). Note the existing
   `track_*.jsonl` entry.
6. Locate `never_modifies` section. Note the existing entry.
7. Locate algorithm step 1 (starts with "Read WAI-Spoke/advisors/
   historian/scan_state.json") — the watermark READ step.
8. Locate the final algorithm step (starts with "Write scan_state.json")
   — the watermark WRITE step.

## Execute

**Algorithm step replacements (in-place, no net new steps):**

1. Replace algorithm step 1 (the scan_state read step). Current:
   `"Read WAI-Spoke/advisors/historian/scan_state.json (if exists) to get last_scan_session"`
   New:
   `"Read WAI-Spoke/advisors/historian/scan_state.json (if exists) to get last_scan_session_internal and last_scan_session_external. Backward compat: if only last_scan_session exists (old format), treat it as last_scan_session_internal and start last_scan_session_external from null."`

2. Replace algorithm step 2 (the file listing glob). Current:
   `"List WAI-Spoke/sessions/track_*.jsonl sorted by filename"`
   New:
   `"List WAI-Spoke/sessions/track_*.jsonl AND WAI-Spoke/sessions/WAI_Track-*.jsonl. Sort each glob independently by filename. Process as two separate streams — do NOT merge into a single sorted sequence (ASCII sort puts uppercase WAI_Track before lowercase track_, which breaks incremental watermarking)."`

3. Replace algorithm step 3 (the watermark filter step). Current text
   references `last_scan_session`. New:
   `"Load sessions using two independent watermarks: (a) For track_*.jsonl files: load where filename > last_scan_session_internal. (b) For WAI_Track-*.jsonl files: load where filename > last_scan_session_external."`

4. Replace the final algorithm step (the scan_state write step). Current:
   `"Write scan_state.json: { last_scan_session: newest session filename just processed }"`
   New:
   `"Write scan_state.json: { last_scan_session_internal: newest track_* filename just processed, last_scan_session_external: newest WAI_Track-* filename just processed }"`

**Algorithm step insertions (net +2 steps):**

5. After step 3 (watermark filter), insert a new format detection step:
   `"Format detection: For each loaded file, read the first line. If it contains '"event":"session_start"', mark as event-based format. Otherwise, treat as turn-based format (existing behavior). Use the filename (without path and extension) as the session_id for event-based files."`

6. After the existing extraction step ("For each loaded session:
   extract all items from open[], activity[], decisions[]"), insert:
   `"Event-based extraction: For files marked as event-based format, extract items using this mapping: (a) Lines with '"event":"decision_made"' — extract the 'decision' field text, record with field=decisions. (b) Lines with '"event":"concept_update"' — extract 'concept' + ': ' + 'action' as text, record with field=activity. (c) Lines with '"event":"concept_fossil"' — extract 'concept' + ' ' + 'status' as text, record with field=open. (d) Lines with '"event":"turn_marker"' — extract 'focus' field text, record with field=activity. (e) Lines with '"event":"context_canary"' — extract 'warning' field text, record with field=open. (f) Lines with '"event":"architecture_signal"' — extract 'description' field text, record with field=activity. Skip session_start, session_end, artifact_reference, and asset_created events (no historian-relevant text). After extraction, proceed to the same normalization and similarity pipeline as turn-based items."`

**Scope and metadata updates:**

7. Update `scope.reads` (search for `reads:` under `scope:`). Add a
   new entry after the existing `track_*.jsonl` line:
   `"WAI-Spoke/sessions/WAI_Track-*.jsonl (event-based external tracks)"`

8. Update `never_modifies` (search for `never_modifies:`). Add a new
   entry after the existing `sessions/track_*.jsonl` line:
   `"sessions/WAI_Track-*.jsonl — external tracks are immutable records"`

9. Add a YAML comment block above the `algorithm:` key:
   ```yaml
   # Dual-format support (added by epic-chat-to-track-v1):
   # - Turn-based: track_*.jsonl with {open[], activity[], decisions[]} per point
   # - Event-based: WAI_Track-*.jsonl from external AI chats (Chat-to-Track)
   #   Format detected by first line containing "event":"session_start"
   #   Event types mapped to historian fields — see extraction step
   #   Two independent watermarks used (ASCII sort order issue — see step 3)
   ```

## Verify

1. `grep "WAI_Track" framework/skills/historian.yaml` — returns the
   extended glob step, the scope.reads entry, and the never_modifies entry.
2. `grep "session_start" framework/skills/historian.yaml` — returns the
   format detection step.
3. `grep "track_\*" framework/skills/historian.yaml` — still returns
   the original glob (turn-based files not removed).
4. `grep -B2 "algorithm:" framework/skills/historian.yaml` — shows
   the dual-format comment.
5. Count the algorithm array steps — should be original count + 2
   (format detection + event-based extraction). Steps 1, 2, 3, and
   the final step are replaced in-place (not added).
6. `grep "last_scan_session_external" framework/skills/historian.yaml`
   — returns hits in: the read step (step 1), the watermark step
   (step 3), and the write step (final step).
7. `grep "last_scan_session_internal" framework/skills/historian.yaml`
   — same three hits plus the backward compat note.
8. `grep "Backward compat" framework/skills/historian.yaml` — confirms
   migration logic for old scan_state.json format.

## Context for Cold Reader

The Chat-to-Track system captures event-based telemetry from external
AI conversations. Once absorbed by wakeup (see sibling lug
`lug-chat-to-track-wakeup-ingest`), these files land in
`WAI-Spoke/sessions/` as `WAI_Track-*.jsonl`. This lug makes the
historian aware of them.

The event types and their fields are defined in
`framework/skills/chat-to-track.md`.

The mapping from events to historian fields:

| Event Type | Field Extracted | Maps To |
|-----------|----------------|---------|
| `decision_made` | `decision` | `decisions[]` pipeline |
| `concept_update` | `concept` + `action` | `activity[]` pipeline |
| `concept_fossil` | `concept` + `status` | `open[]` pipeline |
| `turn_marker` | `focus` | `activity[]` pipeline |
| `context_canary` | `warning` | `open[]` pipeline |
| `architecture_signal` | `description` | `activity[]` pipeline |

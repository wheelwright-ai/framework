# Epic: Chat-to-Track — External Session Capture Pipeline

**ID:** epic-chat-to-track-v1
**Type:** epic
**Status:** open
**Created:** 2026-03-16
**Source:** Framework session with code-puppy-f16663 + ChatGPT collaboration
**Priority:** P1 (base P1, High velocity + Medium cost + Aligned fit)

## What This Is

A complete pipeline for capturing value from external AI conversations
(ChatGPT, Gemini, etc.) and bringing it back into the WAI ecosystem as
structured track data the historian can process.

Three components:

1. **Chat-to-Track prompt** — A portable prompt pasted into any AI chat
   that records event-based telemetry. Auto-detects start-of-chat vs
   mid-conversation. "Closeout chat" triggers export. Includes a
   context_canary that warns before quality degrades.

2. **`/wai-chat-to-track` command** — Copies the prompt to clipboard
   with user directions for the full workflow.

3. **Ingest pipeline** — Wakeup absorbs `WAI_Track-*.jsonl` files from
   `seed/ingest/`, validates them, moves to `sessions/`, and the
   historian scans them for patterns.

## What This Is NOT

- Not a replacement for internal track-encapsulation (that's automatic
  via wakeup/closeout and remains turn-based)
- Not a conversation summarizer — events are compact JSONL telemetry,
  not prose
- Not a modification to the point schema — external tracks use a
  different event-based format
- Not the track→path rename (that's `epic-path-evolution-v1`)

## Origin Story

This epic emerged from a real use case: Mario had a valuable conversation
in ChatGPT about creating a new repo. That context was locked in ChatGPT
with no way to bring it into the WAI-managed project. The prompt went
through several iterations:

1. "WAI Extract" — post-hoc markdown synthesis (too heavy, wrong format)
2. "WAI Stenographer" — turn-per-turn recording (DRY violation with extract)
3. "Flight Data Recorder" — event-based telemetry (great concept, off-brand)
4. "Chat-to-Track" — merged single prompt, auto-mode detection, "closeout chat"

Key insight: a single smart prompt handles both live recording AND
retroactive extraction by detecting whether a conversation is already
in progress.

## Decisions Made

- **DECISION-001:** Single merged prompt, not two separate live/extract files.
  Rationale: 111 lines of duplicated event schemas was a DRY violation.
  The prompt auto-detects mode from context.

- **DECISION-002:** Event-based format, not turn-based.
  Rationale: External chats can't control cadence. Events fire only when
  meaningful signals appear (decisions, concept changes, architecture).
  More efficient and higher signal-to-noise.

- **DECISION-003:** "closeout chat" as the trigger phrase.
  Rationale: Aligns with `/wai-closeout` convention used throughout WAI.
  Familiar language, consistent mental model.

- **DECISION-004:** context_canary event recommends closeout.
  Rationale: Starting with the prompt (not bolting on at the end) means
  the AI can monitor its own context health and recommend export before
  quality degrades.

- **DECISION-005:** Track naming `WAI_Track-YYYYMMDD-HHMM-Provider-Model.jsonl`.
  Rationale: Encodes provider and model in the filename for cross-tool
  identification. Distinguishable from internal `track_*.jsonl` files.

- **DECISION-006:** `decision_made` event type added to original schema.
  Rationale: Historian specifically scans `decisions[]` for `reopened_decision`
  pattern detection. External tracks without decisions would be invisible to
  the most valuable historian pattern.

## Fit Report

**Existing lug overlap:**
- `epic-path-evolution-v1`: Challenge overlap — both address session data
  portability, but different mechanisms. Path evolution renames track→path
  and builds a WAI Path markdown synthesizer. Chat-to-Track builds an
  event-based capture pipeline for external chats. Complementary.
- `epic-track-historian-taste-v1`: Dependency — Chat-to-Track extends the
  historian with a new input format. Historian must handle event-based
  tracks.

**Existing functionality overlap:**
- Wakeup Step 6b: Partial coverage — already ingests `.track.jsonl` from
  `seed/ingest/`. Needs extension for `WAI_Track-*.jsonl` naming and
  validation of event-based format.
- `track-encapsulation.yaml` → `deferred_mode`: References external capture
  but doesn't implement it. Chat-to-Track IS the implementation.

**Signal/decision conflicts:** None.

**Terminology notes:**
- "track" (not "path") — `epic-path-evolution-v1` proposed renaming but
  never executed. We use "track" to match what's implemented.
- "closeout chat" — new term, but intentionally mirrors `/wai-closeout`.

**Fit classification:** extends

## Scoring

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Velocity lift | **High** | Unlocks cross-tool session continuity — core to Wheelwright's value proposition |
| Implementation cost | **Medium** | Prompt done, command done. Remaining: wakeup ingest + historian compat (2 files, multi-step) |
| System fit | **Aligned** | Directly extends session tracking and historian — core features |
| Generality | **All spokes** | Every spoke benefits from importing external conversations |

## Assets in This Lug

- `BRIEF.md` — This file
- `plan.md` — Task decomposition and execution plan

## Related Lugs

- `epic-path-evolution-v1` — Track→Path rename (complementary)
- `epic-track-historian-taste-v1` — Historian system (dependency)
- `epic-sessions-flat-storage-v1` — Session file storage (dependency)

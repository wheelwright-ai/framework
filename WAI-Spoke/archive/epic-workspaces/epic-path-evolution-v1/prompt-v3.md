# WAI Path Generator — Session Export Prompt

You are generating a WAI Path export for the Wheelwright AI framework.
A WAI Path is a self-contained session synthesis document that captures
all decisions, innovations, patterns, and generated assets from a
conversation session. It is the synthesized layer above raw path data.

## What a Path Is

A **path** is a sequence of **points** (waipoints) captured during a session.
Each point records what happened, what the agent was thinking, what decisions
were made, and what remains open. The path is the journey; points are the
footprints along it.

This export synthesizes raw points into a portable, self-contained document
that any spoke can ingest.

## Point Schema (What You're Synthesizing From)

Each point in a session captures:

| Field | Purpose |
|-------|---------|
| `turn` | Turn number in session |
| `ts` | ISO 8601 timestamp |
| `focus` | What this turn was about |
| `action` | What was done |
| `thinking` | Agent's internal reasoning |
| `activity` | List of concrete actions taken |
| `decisions` | Decisions made this turn |
| `insights` | Observations worth preserving |
| `open` | Unresolved questions |
| `phase` | orientation, exploration, planning, execution, review, recovery |
| `evolution` | How focus shifted from previous turn |
| `trigger` | Why this point was captured: `periodic`, `decision`, `milestone`, `manual` |

When generating this export, you are compressing the full richness of points
into a structured synthesis. Don't lose the thinking and insights — they're
the most valuable part.

## Export Structure

1. **Header** — Session metadata (date, conductor, source, status)
2. **Path Metadata** — YAML block: session_id, model, conductor, point_count, phases, capture_cadence
3. **Session Summary** — What was discussed, 2-3 sentences. Capture the evolution arc — how the session's focus shifted across points.
4. **Decisions Made** — Each with Context, Decision, Rationale, Impact, and what it Supersedes (if applicable)
5. **Innovations** — New patterns or approaches that emerged
6. **Lugs in Transit** — Lugs identified during session that need extraction into a spoke's lug system. These ride inside the path file as transport medium — they were never in a spoke yet.
7. **Embedded Assets** — All generated artifacts (prompts, schemas, configs, code). The path file IS the payload — embed everything, reference nothing.
8. **Open Questions** — Unresolved items for future sessions
9. **Connections** — Links to other spokes, Lugs, or prior sessions

## Path Metadata Block

Place immediately after the header:

```yaml
path_metadata:
  session_id: "session-YYYYMMDD-HHMM"
  model: "model used"
  conductor: "human participant"
  point_count: N
  phases: [orientation, planning, execution, ...]
  capture_cadence: "every 3 turns + on-decision"
  duration_estimate: "approximate session length"
```

This makes the path self-describing and portable without external state files.

## Formatting Rules

- Each Decision gets a unique ID: DECISION-NNN
- Decisions that supersede earlier thinking explicitly state what they replace
- Assets are embedded inline, never referenced externally
- The export is the payload — it must be self-contained
- Newest content is HEAD; if versioning prior decisions, nest history

## Lug Extraction Convention

Lugs discovered during a session ride inside the path file as **lugs in transit**.
The path file is the transport medium — lugs were never in a spoke.

When a receiving spoke processes this path:
- Each lug gets its own folder: `lugs/{lug-id}/`
- Folder contains `BRIEF.md` (metadata, summary, what it IS and IS NOT) plus any assets
- A registry entry is appended to `WAI-Lugs.jsonl` with a `folder` field pointing to the lug folder
- The path file is never modified after generation — it's an immutable record
- The extracted lug becomes HEAD (the folder at top level is always current)
- Any prior lug with the same ID is superseded (not merged alongside)
- Version history nests under `lugs/{lug-id}/versions/` for audit

For each lug in transit, provide enough context that extraction is mechanical:
- `id`, `type`, `title`, `status`, `description`
- `source_path`: this WAI Path file
- `extracted_from_session`: session ID

## Granularity Guidance

This export targets the **synthesized** level:
- **Raw** = all points as-is (the path.jsonl file itself — not this document)
- **Synthesized** = decisions + insights deduplicated, narrative arc preserved (THIS)
- **Compressed** = single-paragraph session summary (for hub aggregation)

Preserve the *why* behind decisions (from thinking and insights), not just the *what*.

## Versioning

When a WAI Path contains updates to previously exported decisions:
- The new version becomes HEAD in this document
- Reference the prior export date and decision ID being superseded
- The receiving spoke should update its HEAD lug folder accordingly
- Both versions exist, but newest is HEAD and older versions are history

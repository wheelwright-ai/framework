# Lug: Path Evolution — Track Rename, Folder Lugs, WAI Path Generator

**ID:** epic-path-evolution-v1
**Type:** epic
**Status:** open
**Created:** 2026-03-13
**Source:** WAI Path Export 2026-03-12 (claude.ai session) + framework session 12

## What This Is

A coordinated set of changes that evolve three interconnected framework concepts:

1. **Track → Path rename** — "path" is the object composed of points (waipoints). Rename across all framework files.
2. **Folder-based lugs** — Each lug becomes an atomic folder with a BRIEF.md and assets. WAI-Lugs.jsonl becomes a registry/index; content lives in folders.
3. **WAI Path Generator prompt** — A skill for synthesizing session points into portable WAI Path exports.

## What This Is NOT

- Not a rewrite of the session capture mechanism (point schema stays the same)
- Not removing WAI-Lugs.jsonl (it stays as registry/index)
- Not changing the hub-spoke architecture

## Decisions Driving This

From WAI Path Export 2026-03-12:
- DECISION-001: `/compact` is stackable (waipoints along a path)
- DECISION-002: Lug transit extraction — copy out, never modify source
- DECISION-003: Newest lug is HEAD, history nests underneath
- DECISION-004: WAI Path must embed generated assets

From framework session 12:
- "Path" is better than "track" — active, directional, connects to WAI Point
- Lugs as folders = atomic, portable, self-describing
- Point schema gains `trigger` field

## Assets in This Lug

- `plan.md` — Step-by-step execution plan (for Haiku agent)
- `prompt-v3.md` — Updated WAI Path Generator prompt (folder-based lugs)

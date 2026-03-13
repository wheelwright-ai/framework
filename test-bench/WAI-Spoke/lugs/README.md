# Lugs Directory Structure

## Purpose

This directory contains Wheelwright lugs for cross-spoke communication:

- **inbox/** - Incoming lugs from other wheels (hub, other spokes)
- **outbox/** - Outgoing lugs to be picked up by other wheels
- **{session-id}.jsonl** - Active session lugs

## Processing

- Inbox files are auto-processed on wakeup via `/wai-learn`
- Outbox files are distributed via automatic closeout delivery
- Session lugs are archived to `../lugs-closed.jsonl` on closeout

## File Format

All lugs use JSONL (JSON Lines) format:
- One lug per line
- Each line is valid JSON
- Minified keys for storage efficiency

## Do Not

- Do NOT manually edit these files
- Do NOT delete inbox files (auto-archived after processing)
- Do NOT move files between directories

See WAI-Guide.md for full protocol documentation.

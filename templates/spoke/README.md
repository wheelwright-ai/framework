# WAI-Spoke Directory

For humans: This folder contains session state, signals, configuration
For AI: Load files in order: WAI-State.json → WAI-State.md → invoke skills

## WAI-State.json
Machine-readable project state. Updated by closeout. Read by AI.
Contains: foundation, sessions, analytics, wheel metadata, hub location

## WAI-State.md
Strategic vision and decision log. Human + AI readable.
Contains: foundation, focus, decisions with rationale, evolution log

## WAI-Skills.jsonl
Skill registry - 16 skills, authoritative behavioral system
Reference only. Skill files are the source of truth.

## WAI-Lugs.jsonl
Task graph and work log - append-only
Created by user and closeout. Read by recovery commands.

## WAI-Session-Log.jsonl
Conversation transcript - append-only
Cleared at closeout. Used for session continuity.

## WAI-Signals.jsonl
High-impact decisions log (impact >= 8)
Created by signal_advisor. Pushed to hub via (deprecated - auto-discovery on wakeup).

## WAI-File-Index.json
Index of files modified. Read by AI orientation.

## Files You Can Edit
- WAI-State.md (add notes, decisions)
- WAI-Lugs.jsonl (create tasks)

## Files That Self-Update
- WAI-State.json (closeout)
- WAI-Session-Log.jsonl (appended/cleared)
- WAI-Signals.jsonl (signal_advisor)
- WAI-File-Index.json (closeout)

## Key Insight
All behavioral rules live in skill files, not .jsonl files.

AI loads context: Read JSON/md files → Invoke skills → Apply rules
Result: No duplication, no redundant guides, humans see state here

Last Updated: 2026-02-08

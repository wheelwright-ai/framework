# CC Advisor — ClaudeCode Configuration Advisor

Persistent advisor that monitors Claude Code configuration health across sessions.

## What It Does
- Scans .claude/settings.json, CLAUDE.md, and hooks for configuration gaps
- Tracks health score over time via passes.jsonl
- Suggests improvements when score drops or new features appear
- Reports to hub for fleet-wide config health tracking

## Data Sources
See scan_state.json → data_sources for what this advisor reads.

## Rubric
Absorbed from wai-claude-maximizer.md. Four categories:
- Hook Coverage (weight 3): all 5 lifecycle hooks present
- Permission Hygiene (weight 2): deny list, no wildcards, clean settings.local
- CLAUDE.md Completeness (weight 2): anti-patterns, rules, workflow, hooks
- WAI Integration (weight 3): wakeup, closeout, track, lug schema

## How to Run
The advisor runs automatically at wakeup when its threshold is met, or on-demand via `/wai-claude-maximizer`.

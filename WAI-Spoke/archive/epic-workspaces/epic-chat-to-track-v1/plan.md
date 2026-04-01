# Chat-to-Track — Execution Plan

## Status Overview

| Task | Status | Lug ID |
|------|--------|--------|
| T1 Prompt | ✅ done | — (delivered as `framework/skills/chat-to-track.md`) |
| T2 Command | ✅ done | — (delivered as `templates/commands/wai-chat-to-track.md`) |
| T3 Wakeup ingest | ✅ done | `lug-chat-to-track-wakeup-ingest` |
| T4 Historian compat | ✅ done | `lug-chat-to-track-historian-compat` |
| T5 Propagation | ✅ done | `lug-chat-to-track-propagation` |

## Execution Order

```
T3 (wakeup ingest) ─┐
                     ├─→ T5 (propagation) — after both are stable
T4 (historian compat)┘
```

T3 and T4 are independent. T5 blocked by both.

## Lug Locations

Each lug has a self-contained BRIEF.md with full Perceive/Execute/Verify:

- `WAI-Spoke/lugs/lug-chat-to-track-wakeup-ingest/BRIEF.md`
- `WAI-Spoke/lugs/lug-chat-to-track-historian-compat/BRIEF.md`
- `WAI-Spoke/lugs/lug-chat-to-track-propagation/BRIEF.md`

## Dogfood History

All three lugs passed round 2 dogfooding (naive agent test via
planning-agent). Key bugs caught and fixed:

- **Wakeup:** `WAI-Spoke/commands/wai.md` is divergent — added
  diff-before-copy guard
- **Historian:** ASCII sort-order breaks watermarks — added dual
  watermark design, explicit step 1/12 replacements, backward compat
- **Propagation:** Skill propagates via hub symlink (no teaching
  needed), reduced to 1 teaching, fixed verify format

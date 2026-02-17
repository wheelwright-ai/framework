# WAI Learn

**Push high-impact signals to hub for cross-project learning.**

---

## Execution Context

- **Nodes:** spoke, hub, framework (with paths)
- **Exposure:** spoke.chat:local, spoke.chat:external
- **Paths Required:** spoke_path, hub_path
- **Paths Source:** `lug-wai-paths.jsonl` or `WAI-State.json`

---

## When to Use

- After session with significant decisions (impact >= 8)
- Before closeout when high-impact lugs exist
- When user says "learn", "share signals", "push to hub"
- When `learn.ready` event fires (unsynced high-impact lugs detected)

## Prerequisites

- WAI-Spoke/WAI-Lugs.jsonl exists with lugs
- Hub path known (from lug-wai-paths or WAI-State.json)
- Hub accessible (directory exists, writable)

## Follow-ons

- `/wai-closeout` — Save session state after sharing
- `/wai-teach` — If hub aggregates patterns worth distributing

## Use Cases

**Use Case 1: End of Productive Session**
- Situation: Made significant architectural decisions, created valuable patterns
- Action: Run learn to share insights with hub
- Result: Other spokes can benefit from learnings

**Use Case 2: Before Context Fills**
- Situation: Context at 70%, valuable work done
- Action: Run learn before closeout to ensure signals reach hub
- Result: Knowledge persisted even if session ends abruptly

**Use Case 3: Cross-Project Pattern**
- Situation: Solved problem that applies to multiple projects
- Action: Run learn to push signal to hub
- Result: Hub can distribute pattern to relevant spokes

---

## Learn Procedure

### 1. Find Signals (Lugs with Impact >= 8)

Read from `WAI-Spoke/WAI-Lugs.jsonl`:
```
signals = lugs where impact >= 8 AND hub_synced != true
```

No separate wheel-signals.jsonl needed - signals ARE lugs.

### 2. Get Paths

Check in order:
1. `WAI-Spoke/seed/ingest/lug-wai-paths.jsonl` (from last teach)
2. `WAI-Spoke/WAI-State.json` → `wheelwright.hub_path`
3. Ask user if not found

### 3. Present Signals for Review

Show what will be shared with enough detail to verify correctness:

```markdown
**Signals Ready to Share** (X lugs, impact >= 8)

| Lug ID | What Was Captured | Value to Hub |
|--------|-------------------|--------------|
| `lug:sig-xxx` | [2-3 sentence summary confirming the insight was recorded correctly] | [Why other spokes benefit] |
| `lug:sig-yyy` | [2-3 sentence summary] | [Cross-project value] |

**Before sharing, any additions or context to include?**
> [User can add notes, clarify intent, or ask agent to elaborate on any signal]

Proceed with share? (yes/no)
```

### 4. Collect Feedback

If user provides input:
- Add their notes to the signal's `user_context` field
- If they ask questions, answer and update signal summary
- If they want to exclude a signal, mark it `hub_synced: "skipped"`

### 5. Push to Hub

For each confirmed signal:
1. Copy lug to `[hub_path]/intake/signals/[spoke_id]/`
2. Mark original lug: `hub_synced: true`, `synced_at: [timestamp]`
3. Log the push

### 6. Report Results

```markdown
**Learn Complete**

Pushed to hub:
- `lug:sig-xxx` → hub/intake/signals/
- `lug:sig-yyy` → hub/intake/signals/

Skipped: [count if any]

Hub will aggregate on next wakeup.
```

---

## No Signals Case

```markdown
**No Pending Signals**

No high-impact lugs ready to share (impact >= 8, not yet synced).

Signals are created automatically when:
- Architectural decisions are made
- Reusable patterns emerge
- Cross-project insights occur

Continue working - use `/wai-closeout` when ready to save state.
```

---

## Path Resolution

| Source | Field | Priority |
|--------|-------|----------|
| lug-wai-paths.jsonl | hub_path, framework_path | 1 (most recent teach) |
| WAI-State.json | wheelwright.hub_path | 2 (configured) |
| User input | Ask directly | 3 (fallback) |

If running from hub or framework with paths provided, learn can push signals for any spoke.

---

## Related Commands

- `/wai-closeout` — Save state (signals extracted here)
- `/wai-teach` — Distribute from hub to spokes (opposite direction)
- `/wai-status` — Check if signals pending

---

*Learn = Push insights up. Teach = Push patterns down.*

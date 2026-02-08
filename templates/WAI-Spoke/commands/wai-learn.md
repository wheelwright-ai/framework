# WAI Learn

Push this session's signals to hub.

## Instructions

1. Check for pending signals in `WAI-Spoke/wheel-signals.jsonl`

2. If signals exist with `has_high_impact_learnings: true`:
   - Summarize what will be shared
   - Confirm with user before pushing

3. Check hub location from `WAI-Spoke/WAI-State.json` -> `wheelwright.hub_path`

4. If confirmed and hub accessible:
   - Append signals to hub's learning intake
   - Mark signals as synced in wheel-signals.jsonl
   - Update kb-sync.json

5. If WAI CLI available, suggest: `WAI sync --learn`

Output format:
```
**Signals Ready to Share**

High-impact learnings from this wheel:
- [Signal 1]: [brief description]
- [Signal 2]: [brief description]

Push to hub? (yes/no)
```

Or if no signals:
```
**No Pending Signals**
No high-impact learnings to share yet.
Continue working - signals are captured automatically for decisions with impact >= 8.
```

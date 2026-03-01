# WAI Teach

Pull new learnings from hub into this spoke.

## Instructions

1. Check hub location from `WAI-Spoke/WAI-State.json` -> `wheelwright.hub_path`

2. If hub path exists, check for new knowledge:
   - Read hub's knowledge base version
   - Compare with spoke's `kb-sync.json`

3. If new learnings available:
   - List what's new (patterns, policies, etc.)
   - Ask user to confirm import
   - Update WAI-Guide.md with new "Hub Learnings" section
   - Update kb-sync.json with new version

4. If WAI CLI available, suggest: `WAI sync --teach`

Output format:
```
**Hub Teachings Available**

New since last sync:
- [Pattern/Learning 1]
- [Pattern/Learning 2]

Import these learnings? (yes/no)
```

Or if nothing new:
```
**Hub Sync Current**
No new teachings since last sync ([date]).
```

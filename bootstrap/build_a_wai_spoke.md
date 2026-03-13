# Build a WAI Spoke

Set up Wheelwright AI session continuity for this project.

## What You Need

A project directory with a git repository.

## Steps

1. Create the spoke directory:
```
mkdir -p WAI-Spoke/seed/ingest
mkdir -p WAI-Spoke/lugs/inbox
mkdir -p WAI-Spoke/lugs/outbox
```

2. Create `WAI-Spoke/WAI-State.json` with this minimum structure:
```json
{
  "wheel": {
    "version": "1.0.0",
    "node_type": "spoke",
    "name": "YOUR_PROJECT_NAME",
    "status": "active"
  },
  "_session_state": {
    "session_count": 0,
    "last_modified_by": null,
    "last_modified_at": null
  },
  "wheelwright": {
    "structure_version": "v2"
  }
}
```

3. Create `WAI-Spoke/WAI-Lugs.jsonl` — empty file, one lug per line will accumulate.

4. If you have a captured chat track (from `capture_a_chat.md`), place it in `WAI-Spoke/seed/ingest/`.

5. Add to your project's `CLAUDE.md` (or equivalent agent instructions):
```
On session start, read WAI-Spoke/WAI-State.json for project context.
After each turn, append a point to the active session track (WAI-Spoke/session-YYYYMMDD-HHMM/track.jsonl).
On session end, run closeout to preserve state.
```

6. Commit: `git add WAI-Spoke/ && git commit -m "Initialize WAI spoke"`

## What Happens Next

On the next session, the agent reads WAI-State.json and picks up context. If there's a track file in `seed/ingest/`, it processes it into a session folder as the first historical record.

For the full framework (hub connection, teaching distribution, advisor skills):
https://github.com/wheelwright-ai/framework

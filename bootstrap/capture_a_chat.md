# Capture This Chat

Turn this conversation into a session track that Wheelwright AI can use.

## What To Do

Review our conversation from the beginning. For each turn where something meaningful happened, create a point. Skip turns that were only greetings or simple acknowledgments.

Output a single file called `track.jsonl` with one JSON object per line. Each point:

```json
{"turn":1,"ts":"2026-03-07T15:00:00Z","focus":"topic of this turn","action":"what happened","thinking":"why decisions were made, what was considered","activity":["concrete actions taken"],"decisions":["choices made"],"insights":["new understanding"],"open":["unresolved questions"],"phase":"orientation","evolution":null}
```

Phase values: `orientation`, `exploration`, `planning`, `execution`, `review`, `recovery`

The `evolution` field shows how focus shifted from the previous turn. Null on the first point. Example: `"planning -> execution: user approved the approach"`

## After You Generate It

**If this project already has a WAI spoke:**
Save as `WAI-Spoke/seed/ingest/captured-chat.track.jsonl`

On next wakeup, the agent will process it into a session folder.

**If this project does not have a WAI spoke yet:**
See `build_a_wai_spoke.md` in this same folder, or visit:
https://github.com/wheelwright-ai/framework

Give your agent both files — this track and the spoke setup instructions. It will create the spoke and ingest the track as the foundation session.

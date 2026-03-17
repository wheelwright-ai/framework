# WAI Chat-to-Track

Paste this into any AI conversation to capture structured telemetry
that the Wheelwright AI historian can process.

**Works in two modes automatically:**

- Pasted at the **start** of a new chat → records events live as you go
- Pasted in the **middle or end** of an existing chat → reconstructs events retroactively

Say **"closeout chat"** when done to get your complete track file.

---

## Your Role

You have a secondary role in this conversation: **session track recorder**.

Your primary job is unchanged — answer questions, write code, design
systems, whatever is asked. But in the background you are recording
**lightweight telemetry events** about this conversation.

**If this conversation has already been going** before you received
these instructions, first reconstruct events for everything discussed
so far, then continue recording live from this point forward.

You must operate with **minimal token usage** for recording. Do NOT
produce large summaries. Only produce **compact JSONL event capsules**.

---

## Output Format

After each substantive response, append a small code block containing
one or more JSON lines. Each line is one telemetry event.

```jsonl
{"event":"turn_marker","ts":"2026-03-16T20:00:00Z","turn":3,"focus":"auth system design"}
{"event":"decision_made","ts":"2026-03-16T20:00:00Z","decision":"JWT over session tokens","rationale":"API clients need stateless auth","impact":7,"supersedes":null}
```

If nothing meaningful happened beyond the turn itself, emit only the
`turn_marker`. Don't pad with empty events.

---

## Session File Naming

The track file follows this pattern:

```
WAI_Track-YYYYMMDD-HHMM-Provider-Model.jsonl
```

Example: `WAI_Track-20260316-1304-ChatGPT-gpt4o.jsonl`

---

## Event Types

| Event | When to Emit |
|-------|-------------|
| `session_start` | Once, as your first output |
| `session_end` | Once, on closeout |
| `turn_marker` | Every substantive turn |
| `decision_made` | A choice is made that shapes future work |
| `concept_update` | A concept appears, evolves, or stabilizes |
| `concept_fossil` | A concept is superseded, abandoned, or left competing |
| `architecture_signal` | Structural patterns emerge |
| `artifact_reference` | An existing external artifact is referenced |
| `asset_created` | A new artifact is generated in this session |
| `context_canary` | Conversation health degrades |

---

## Event Schemas

### session_start

Emit once as your very first output.

```jsonl
{"event":"session_start","ts":"2026-03-16T13:04:00Z","session_id":"export-20260316-1304","provider":"ChatGPT","model":"gpt-4o"}
```

| Field | Required | Description |
|-------|----------|-------------|
| event | yes | `"session_start"` |
| ts | yes | ISO-8601 UTC |
| session_id | yes | `"export-YYYYMMDD-HHMM"` |
| provider | yes | ChatGPT, Claude, Gemini, etc. |
| model | yes | Specific model name |

### session_end

Emit once on closeout.

```jsonl
{"event":"session_end","ts":"2026-03-16T15:30:00Z","turn_count":24,"concepts_tracked":7,"decisions_made":3,"assets_created":2}
```

| Field | Required | Description |
|-------|----------|-------------|
| event | yes | `"session_end"` |
| ts | yes | ISO-8601 UTC |
| turn_count | yes | Total substantive turns |
| concepts_tracked | yes | Concept events emitted |
| decisions_made | yes | Decision events emitted |
| assets_created | yes | Asset events emitted |

### turn_marker

Emit once per substantive turn. Lightweight navigation spine.

```jsonl
{"event":"turn_marker","ts":"2026-03-16T13:12:00Z","turn":3,"focus":"auth system design"}
```

| Field | Required | Description |
|-------|----------|-------------|
| event | yes | `"turn_marker"` |
| ts | yes | ISO-8601 UTC |
| turn | yes | Sequential turn number |
| focus | yes | One phrase — what this turn was about |

### decision_made

Emit when a choice is made that shapes future work.

```jsonl
{"event":"decision_made","ts":"2026-03-16T13:20:00Z","decision":"JWT over session-based auth","rationale":"API clients need stateless tokens","impact":7,"supersedes":null}
```

| Field | Required | Description |
|-------|----------|-------------|
| event | yes | `"decision_made"` |
| ts | yes | ISO-8601 UTC |
| decision | yes | What was decided |
| rationale | yes | Why — the reasoning |
| impact | no | 1–10 (10 = fundamental direction change) |
| supersedes | no | Prior decision this replaces, null if none |

### concept_update

Emit when a concept appears, evolves, or stabilizes.

```jsonl
{"event":"concept_update","ts":"2026-03-16T13:15:00Z","concept":"Context Radar","action":"introduced","phase":"exploration"}
```

| Field | Required | Description |
|-------|----------|-------------|
| event | yes | `"concept_update"` |
| ts | yes | ISO-8601 UTC |
| concept | yes | Concept name |
| action | yes | `introduced`, `evolved`, `superseded` |
| phase | yes | `exploration`, `convergence`, `crystallization` |

### concept_fossil

Emit when a concept is superseded, abandoned, or left competing.

```jsonl
{"event":"concept_fossil","ts":"2026-03-16T14:00:00Z","concept":"Polling Architecture","status":"superseded","replaced_by":"WebSocket Push","phase":"convergence"}
```

| Field | Required | Description |
|-------|----------|-------------|
| event | yes | `"concept_fossil"` |
| ts | yes | ISO-8601 UTC |
| concept | yes | Concept name |
| status | yes | `superseded`, `unrevisited`, `competing` |
| replaced_by | no | What replaced it (if superseded) |
| phase | yes | Phase when fossilized |

### architecture_signal

Emit when structural patterns appear.

```jsonl
{"event":"architecture_signal","ts":"2026-03-16T13:45:00Z","structure":"pipeline","description":"ingest → normalize → scan → surface"}
```

| Field | Required | Description |
|-------|----------|-------------|
| event | yes | `"architecture_signal"` |
| ts | yes | ISO-8601 UTC |
| structure | yes | `loop`, `pipeline`, `layer`, `ecosystem`, `triad` |
| description | yes | Brief description |

### artifact_reference

Emit when the conversation references an existing external artifact.

```jsonl
{"event":"artifact_reference","ts":"2026-03-16T13:50:00Z","artifact_id":"historian.yaml","path":"framework/skills/historian.yaml","summary":"pattern-scan algorithm for session tracks"}
```

| Field | Required | Description |
|-------|----------|-------------|
| event | yes | `"artifact_reference"` |
| ts | yes | ISO-8601 UTC |
| artifact_id | yes | Short identifier |
| path | no | File path or URL if known |
| summary | yes | One-line description |

### asset_created

Emit when a new artifact is generated. Never embed the full asset —
record a reference only.

```jsonl
{"event":"asset_created","ts":"2026-03-16T14:10:00Z","asset_type":"schema","asset_id":"auth-rbac-v1","path":"assets/auth-rbac-v1.yaml","summary":"RBAC schema with tenant scoping"}
```

| Field | Required | Description |
|-------|----------|-------------|
| event | yes | `"asset_created"` |
| ts | yes | ISO-8601 UTC |
| asset_type | yes | `code`, `schema`, `prompt`, `plan`, `diagram`, `config` |
| asset_id | yes | Short identifier |
| path | yes | Reference path (e.g. `assets/name.ext`) |
| summary | yes | One-line description |

### context_canary

Emit when conversation health degrades. Trigger when context usage is
estimated above 70% OR earlier concepts can't be recalled reliably.

**When the canary fires, recommend the user says "closeout chat" to
preserve the track before quality degrades further.**

```jsonl
{"event":"context_canary","ts":"2026-03-16T15:00:00Z","context_usage_estimate":"~75%","warning":"Earlier auth decisions may need re-verification — recommend closeout"}
```

| Field | Required | Description |
|-------|----------|-------------|
| event | yes | `"context_canary"` |
| ts | yes | ISO-8601 UTC |
| context_usage_estimate | yes | Rough percentage |
| warning | yes | What's at risk |

---

## Concept Phases

These describe **idea maturity**, not session workflow:

| Phase | Signal |
|-------|--------|
| `exploration` | Many candidate ideas, unstable naming |
| `convergence` | Ideas repeated, definitions stabilizing |
| `crystallization` | Architecture forming, decisions locking in |

---

## Recording Rules

- Record events **only when meaningful signals appear**
- If nothing happened beyond the turn, emit only `turn_marker`
- Avoid redundant events — don't repeat a concept_update if nothing changed
- 5–12 fields per event maximum
- The conversation comes first; recording is secondary

---

## Retroactive Reconstruction

If pasted into an existing conversation, reconstruct events for
everything discussed before this prompt was introduced:

1. Emit a `session_start` event
2. Walk through the prior exchanges chronologically
3. Emit `turn_marker` for each substantive exchange
4. Emit `decision_made`, `concept_update`, `concept_fossil`,
   `architecture_signal`, `artifact_reference`, `asset_created`
   for anything that matches the event schemas above
5. Reconstruct timestamps as best estimates
6. **Only extract what actually happened** — do not invent decisions
   or concepts that weren't discussed
7. After reconstruction, continue recording live from this point

---

## Closeout

When the user says **"closeout chat"**:

1. Emit a `session_end` event
2. Output the **complete track file** — all events from the entire
   conversation in a single JSONL code block
3. Suggest the filename following the naming convention

```jsonl
{"event":"session_start","ts":"...","session_id":"...","provider":"...","model":"..."}
{"event":"turn_marker","ts":"...","turn":1,"focus":"..."}
{"event":"concept_update","ts":"...","concept":"...","action":"introduced","phase":"exploration"}
...
{"event":"session_end","ts":"...","turn_count":...,"concepts_tracked":...,"decisions_made":...,"assets_created":...}
```

---

## Self-Improvement

Future systems may refine event schemas. Treat this as an evolving
telemetry standard.

Now acknowledge track recording is active, emit your `session_start`
event, and — if we've already been talking — reconstruct events for
everything above before continuing.

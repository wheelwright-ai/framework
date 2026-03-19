# Track Format Specification (v3.0)

**Format:** Pure JSONL (JSON Lines)
**Canonical Write Target:** `WAI-Spoke/sessions/session-YYYYMMDD-HHMM/track.jsonl`
**Legacy Compatibility:** `track_YYYYMMDD-HHMM.jsonl` (read-only during migration)
**Encoding:** UTF-8

---

## 1. Overview

A Track is a sequential record of "points" (turns) captured during an AI-human session. Unlike raw chat logs, Tracks focus on **state, reasoning, and delta**.

**Canonical Storage:** Tracks are stored in session directories at `WAI-Spoke/sessions/session-YYYYMMDD-HHMM/track.jsonl` where each session gets its own directory. This enables session-scoped artifacts, metadata, and clean organization.

**Migration Note:** Flat files like `track_session-YYYYMMDD-HHMM.jsonl` in `WAI-Spoke/sessions/` are legacy format for compatibility reading only. New track generation should target the canonical session directory structure.

---

## 2. Event Types

### `session_start` (First Line)
The first line of every Track MUST be a `session_start` event.

```json
{
  "event": "session_start",
  "ts": "ISO-8601",
  "session_id": "session-20260317-0815",
  "provider": "anthropic",
  "model": "claude-3-5-sonnet-20241022",
  "machine": "macbook-pro",
  "framework_version": "3.0.0"
}
```

### `point` (Turn Telemetry)
Each subsequent line is a `point` event.

```json
{
  "event": "point",
  "turn": 1,
  "ts": "ISO-8601",
  "phase": "execution",
  "focus": "Refactoring auth module",
  "action": "Updated auth.ts with JWT validation",
  "thinking": "Reasoning proportional to complexity. 3-8 sentences.",
  "activity": ["Read src/auth.ts lines 1-100", "Executed npm test"],
  "decisions": ["Use JWT over session cookies"],
  "insights": ["Token validation is the primary bottleneck"],
  "fossils": [{"concept": "Session cookies", "replaced_by": "JWT", "reason": "Scalability"}],
  "open": [{"text": "Rotate signing keys?", "type": "deferred"}],
  "files_in": [{"name": "req.json", "type": "json"}],
  "files_out": [{"name": "auth.ts", "type": "ts", "path": "src/auth.ts"}],
  "context_health": {"usage_estimate": 0.45},
  "recovered": false
}
```

### `session_end` (Optional Final Line)
Used when a session is closed explicitly.

```json
{
  "event": "session_end",
  "ts": "ISO-8601",
  "reason": "closeout",
  "summary_id": "ss-4f1e687a"
}
```

---

## 3. Data Integrity

1. **No Mixed Formats:** Do not include Markdown commentary or YAML frontmatter.
2. **Atomic Writes:** Each turn must be appended immediately.
3. **Fidelity:** Capture enough data to reconstruct the agent's mental model without the chat history.
4. **Canonical Storage:** Always write to `WAI-Spoke/sessions/session-YYYYMMDD-HHMM/track.jsonl`. Create the session directory if needed.
5. **Legacy Compatibility:** Tools may read from flat `track_*.jsonl` files during migration but should not write new ones.

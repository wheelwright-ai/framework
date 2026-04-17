# Track Chain Protocol - Design Document

**Version:** 1.0  
**Created:** 2026-03-18  
**Status:** Implementation Ready

---

## Problem Statement

**Current limitation:** Track encapsulation assumes sessions happen in a persistent WAI-Spoke directory with automatic per-turn writing. This breaks down when:

1. User loads a track file into a new environment (different tool, no WAI-Spoke/)
2. Conversation continues across multiple tools/sessions
3. User wants to generate a track for the current session that links to the predecessor

**What's missing:**
- Track detection when loaded as context
- Predecessor linking in track schema
- Ability to generate track for non-WAI-Spoke sessions
- Conversation chain reconstruction

---

## Solution: Track Chain Protocol

Enable portable session continuity across tools/environments by:

1. **Detecting** track files loaded as context
2. **Linking** successor tracks to predecessors
3. **Generating** track files on-demand for any session
4. **Reconstructing** full conversation history from chains

---

## Schema Extensions

### 1. Session Metadata (First Point)

Add to the **first point** of each track file:

```jsonl
{
  "session_id": "session-20260318-0300",
  "session_metadata": {
    "started_at": "2026-03-18T03:00:00Z",
    "environment": "chatgpt-web",
    "model": "gpt-4",
    "has_predecessor": true,
    "predecessor": {
      "session_id": "session-20260317-2100",
      "source_file": "WAI_Track-20260317-2100-Claude-claude-opus-4-6.jsonl",
      "last_turn": 20,
      "last_timestamp": "2026-03-17T21:45:00Z",
      "detected_from": "context"
    }
  },
  "turn": 1,
  "ts": "2026-03-18T03:00:15Z",
  ...
}
```

**Key decisions:**
- `turn` **restarts at 1** for each session (not cumulative)
- `session_metadata` only appears on turn 1
- Predecessor info captured from context detection

### 2. Turn Numbering Strategy

**Per-session numbering (RECOMMENDED):**
- Session A: turns 1-20
- Session B: turns 1-5 (links to A)
- Session C: turns 1-8 (links to B)

**Rationale:**
- Each track file is self-contained
- Turn numbers are unambiguous within a session
- Chain reconstruction: sum of all session turns
- Matches existing track-encapsulation behavior

### 3. Track Detection Signature

When scanning context for track files, look for:

```jsonl
{"turn":1,"ts":"2026-03-17T21:00:00Z","phase":"orientation","focus":"...
{"turn":2,"ts":"2026-03-17T21:05:00Z","phase":"exploration","focus":"...
```

**Detection criteria:**
- JSON lines format
- Contains required fields: `turn`, `ts`, `phase`, `focus`, `action`, `thinking`
- Sequential turn numbers starting at 1
- Valid ISO-8601 timestamps

---

## Protocol Implementation

### A. Track Detection (Wakeup Step 5b)

**When:** Session start, after loading WAI-State.json

**Process:**
1. Scan conversation context for track file content
2. If detected:
   - Extract session_id (from first point)
   - Extract last turn number
   - Extract last timestamp
   - Extract source file name (if available)
3. Store detection result in memory for session use

**Report to user:**
```
### Track Predecessor Detected
- Session: session-20260317-2100
- Turns: 20
- Last activity: 2026-03-17T21:45:00Z
- Source: WAI_Track-20260317-2100-Claude-claude-opus-4-6.jsonl

New session will link to this predecessor.
```

### B. Track Generation Command

**New command:** `/wai-track-generate` or "Generate track for this conversation"

**Behavior:**
1. Check if predecessor was detected
2. Generate track points for THIS session only (not duplicating loaded content)
3. First point includes session_metadata with predecessor link
4. Output as downloadable file or code block

**Output format:**
```
Track file generated: WAI_Track-20260318-0300-Claude-claude-sonnet-4-5.jsonl

Contains:
- 5 turns (this session only)
- Links to predecessor: WAI_Track-20260317-2100-Claude-claude-opus-4-6.jsonl
- Total conversation spans 2 sessions (25 turns)

[Download link or code block with file content]
```

### C. Conversation Reconstruction

When loading a track with predecessors, agent reports chain:

```
### Conversation Chain Detected

This track is part of a 3-session chain:

Session A (WAI_Track-20260317-1800-Claude-claude-sonnet-4-5.jsonl)
├─ Turns: 1-20
├─ Started: 2026-03-17T18:00:00Z
└─ Environment: claude-code

Session B (WAI_Track-20260317-2100-Claude-claude-opus-4-6.jsonl) ← PREDECESSOR
├─ Turns: 1-5
├─ Started: 2026-03-17T21:00:00Z
├─ Environment: cursor
└─ Links to: Session A

Session C (WAI_Track-20260318-0300-Claude-claude-sonnet-4-5.jsonl) ← CURRENT
├─ Turns: 1-8 (in progress)
├─ Started: 2026-03-18T03:00:00Z
└─ Links to: Session B

Total conversation: 33 turns across 3 sessions
```

---

## File Changes Required

### 1. Update `framework/skills/track-encapsulation.yaml`

Add sections:
- `session_metadata` field in point_schema
- Track detection protocol
- Predecessor linking rules
- Track generation command reference

### 2. Create `templates/commands/wai-track-generate.md`

New command file for on-demand track generation.

### 3. Update `WAI-Spoke/commands/wai.md`

Add Step 5b: Track Predecessor Detection

### 4. Create teaching file

`track-chain-protocol-v1.md.teaching` for distribution to spokes.

---

## Usage Examples

### Example 1: Cross-Tool Continuation

```
# Session A - Claude Code with WAI-Spoke
User: "Let's build a feature"
[20 turns of work, automatic track writing]
→ Produces: WAI_Track-20260317-2100-Claude-claude-opus-4-6.jsonl

# Session B - ChatGPT Web (no WAI-Spoke)
User: [Loads WAI_Track-20260317-2100-Claude-claude-opus-4-6.jsonl]
User: "Continue building the feature"
[5 more turns of work]
User: "Generate track for this conversation"
Agent: [Outputs WAI_Track-20260318-0300-Claude-claude-sonnet-4-5.jsonl with predecessor link]

# Session C - Cursor with WAI-Spoke
User: [Loads WAI_Track-20260318-0300-Claude-claude-sonnet-4-5.jsonl]
Agent: "Detected predecessor chain (2 prior sessions, 25 turns total)"
[Work continues with automatic track writing]
```

### Example 2: Audit Trail

```
User wants to review how a decision evolved across multiple sessions:

1. Load WAI_Track-C.jsonl (current)
2. Agent reports: "Links to B → A (3 sessions, 33 turns)"
3. Load all three tracks to reconstruct full conversation
4. Search across all tracks for decision keywords
```

---

## Testing Strategy

1. **Detection Test:** Load a valid track file, verify detection and predecessor extraction
2. **Generation Test:** Run conversation, generate track, verify schema compliance
3. **Chain Test:** Load track with 2+ predecessors, verify chain reconstruction
4. **Edge Cases:**
   - Empty track file
   - Malformed track content
   - Missing predecessor file
   - Circular references (A→B→A)

---

## Migration Path

**Backward compatibility:** ✅ Full

- Existing tracks without `session_metadata`: work as-is
- New tracks with predecessors: optional enhancement
- Detection is opportunistic: if no track loaded, behavior unchanged

**No breaking changes to existing track files.**

---

## Open Questions

1. **File naming:** Should generated tracks use session_id or allow custom names?
2. **Chain depth:** Should we warn if chain exceeds N sessions (e.g., >10)?
3. **Predecessor verification:** Should we validate predecessor files exist and are loadable?
4. **Partial chains:** What if only middle session (B) is loaded, not A?

**Recommended answers:**
1. Use session_id for consistency (WAI_Track-{YYYYMMDD}-{HHMM}-{Provider}-{Model}.jsonl)
2. No hard limit, but report chain depth to user
3. No - predecessor may not be accessible (different machine/cloud)
4. Report what we know: "Links to A (not loaded), full chain may be deeper"

---

## Implementation Checklist

- [ ] Update track-encapsulation.yaml with session_metadata schema
- [ ] Create wai-track-generate.md command
- [ ] Add detection logic to wai.md Step 5b
- [ ] Test with loaded track file
- [ ] Create teaching file
- [ ] Update README with Track Chain Protocol section
- [ ] Create epic lug for tracking

---

**Status:** Ready for implementation
